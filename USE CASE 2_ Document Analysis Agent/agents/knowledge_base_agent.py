import os
import json
import logging
from datetime import datetime
import chromadb
from chromadb.config import Settings
from agents.base import MCPMessage, Agent
from utils.embeddings import embed_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeBaseAgent(Agent):
    def __init__(self, name, extraction_agent=None, structuring_agent=None,
                 text_interpreter=None, table_interpreter=None, image_interpreter=None,
                 chroma_client=None):
        super().__init__(name)
        self.extraction_agent = extraction_agent
        self.structuring_agent = structuring_agent
        self.text_interpreter = text_interpreter
        self.table_interpreter = table_interpreter
        self.image_interpreter = image_interpreter
        self.embedding_dir = os.path.join("storage", "processed_docs")
        os.makedirs(self.embedding_dir, exist_ok=True)
        
        if chroma_client is None:
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="storage/chroma_persist"
            ))
        else:
            self.client = chroma_client

        self.collection_name = "document_chunks"
        self.collection = self.client.get_or_create_collection(name=self.collection_name)



    async def route(self, message: MCPMessage):
        logger.info(f"Routing command: {message.command}")
        if message.command == "store_document":
            return await self.handle_store_document(message.payload)
        else:
            return {"error": "Unknown command"}

    async def handle_store_document(self, payload):
        doc_id = payload.get("doc_id")
        filename = payload.get("filename")
        metadata = payload.get("metadata", {})

        if not os.path.exists(filename):
            logger.error(f"File not found: {filename}")
            return {"status": "error", "message": f"File not found: {filename}"}

        logger.info(f"Starting extraction for document: {doc_id}")

        # === Step 1: Extraction ===
        extraction_msg = MCPMessage(
            sender=self.name,
            receiver=self.extraction_agent.name,
            command="extract_document",
            payload={"filename": filename, "doc_id": doc_id}
        )
        extracted_result = await self.send(self.extraction_agent, extraction_msg)
        if extracted_result.get("status") != "success":
            err_msg = extracted_result.get("message", "Extraction failed without message")
            logger.error(f"Extraction failed for {doc_id}: {err_msg}")
            return {"status": "error", "message": f"Extraction failed: {err_msg}"}

        raw_text = extracted_result.get("extracted", {}).get("text_text", "")
        image_text = extracted_result.get("extracted", {}).get("image_text", "")
        raw_tables = extracted_result.get("extracted", {}).get("tables", [])

        logger.info(f"Extraction complete for document: {doc_id}, proceeding to structuring")

        # === Step 2: Structuring ===
        structuring_msg = MCPMessage(
            sender=self.name,
            receiver=self.structuring_agent.name,
            command="structure_document",
            payload={
                "doc_id": doc_id,
                "text_text": raw_text,
                "image_text": image_text,
                "tables": raw_tables
        }
)
        structured_result = await self.send(self.structuring_agent, structuring_msg)
        if structured_result.get("status") != "success":
            err_msg = structured_result.get("message", "Structuring failed without message")
            logger.error(f"Structuring failed for {doc_id}: {err_msg}")
            return {"status": "error", "message": f"Structuring failed: {err_msg}"}

        structured_data = structured_result.get("structured", {})

        logger.info(f"Structuring complete for document: {doc_id}, starting interpretation")

        # === Step 3a: Text Interpretation ===
        text_msg = MCPMessage(
            sender=self.name,
            receiver=self.text_interpreter.name,
            command="interpret_text",
            payload={
                "doc_id": doc_id,
                "sections": structured_data.get("sections", {})
            }
        )
        text_result = await self.send(self.text_interpreter, text_msg)
        if text_result.get("status") != "success":
            err_msg = text_result.get("message", "Text interpretation failed without message")
            logger.error(f"Text interpretation failed for {doc_id}: {err_msg}")
            return {"status": "error", "message": f"Text interpretation failed: {err_msg}"}
        text_insights = text_result.get("text_insights", {})

        # === Step 3b: Table Interpretation ===
        table_msg = MCPMessage(
            sender=self.name,
            receiver=self.table_interpreter.name,
            command="interpret_tables",
            payload={
                "doc_id": doc_id,
                "tables": structured_data.get("tables", [])
            }
        )
        table_result = await self.send(self.table_interpreter, table_msg)
        if table_result.get("status") != "success":
            err_msg = table_result.get("message", "Table interpretation failed without message")
            logger.error(f"Table interpretation failed for {doc_id}: {err_msg}")
            return {"status": "error", "message": f"Table interpretation failed: {err_msg}"}
        table_insights = table_result.get("table_insights", [])

        # === Step 3c: Image Interpretation ===
        image_msg = MCPMessage(
            sender=self.name,
            receiver=self.image_interpreter.name,
            command="interpret_image",
            payload={
                "doc_id": doc_id,
                "text_sections": structured_data.get("sections", {})
            }
        )

        image_result = await self.send(self.image_interpreter, image_msg)
        if image_result.get("status") != "success":
            err_msg = image_result.get("message", "Image interpretation failed without message")
            logger.error(f"Image interpretation failed for {doc_id}: {err_msg}")
            return {"status": "error", "message": f"Image interpretation failed: {err_msg}"}
        image_insights = image_result.get("image_insights", {})

        logger.info(f"Interpretation complete for document: {doc_id}, saving output and embedding")

        # === Step 4: Save to JSON ===
        full_output = {
            "doc_id": doc_id,
            "metadata": metadata,
            "structured_data": structured_data,
            "interpretations": {
                "text": text_insights,
                "tables": table_insights,
                "images": image_insights
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        embedding_path = os.path.join(self.embedding_dir, f"{doc_id}.json")
        with open(embedding_path, "w") as f:
            json.dump(full_output, f, indent=2)

        # === Step 5: Embed into ChromaDB ===
        chunks = []

        for section, summary in text_insights.items():
            if isinstance(summary, str) and summary.strip():
                chunks.append(summary)

        for table in table_insights:
            summary = table.get("summary")
            if isinstance(summary, str) and summary.strip():
                chunks.append(summary)

        for caption in image_insights:
            if isinstance(caption, str) and caption.strip():
                chunks.append(caption)

        chunks_count = 0
        if chunks:
            try:
                embeddings = embed_text(chunks)
                if len(embeddings) != len(chunks):
                    logger.warning(f"Embedding count {len(embeddings)} does not match chunks {len(chunks)}")

                for i, chunk in enumerate(chunks):
                    embedding = embeddings[i] if i < len(embeddings) else None
                    if embedding is None:
                        logger.warning(f"No embedding for chunk index {i}")
                        continue
                    self.collection.add(
                        documents=[chunk],
                        metadatas=[{
                            "doc_id": doc_id,
                            "modality": self._infer_modality(chunk),
                            "chunk_index": i
                        }],
                        ids=[f"{doc_id}_chunk_{i}"],
                        embeddings=[embedding]
                    )
                chunks_count = len(chunks)
            except Exception as e:
                logger.error(f"Error during embedding or storing chunks for {doc_id}: {e}")

        logger.info(f"Document {doc_id} stored successfully with {chunks_count} chunks indexed")

        return {
            "status": "success",
            "message": f"Document stored and embedded: {doc_id}",
            "chunks_indexed": chunks_count
        }

    def _infer_modality(self, chunk_text):
        text = chunk_text.lower()
        if any(word in text for word in ["income", "revenue", "profit", "loss", "margin"]):
            return "financial_text"
        elif any(word in text for word in ["table", "column", "row", "figure"]):
            return "table"
        elif any(word in text for word in ["image", "diagram", "chart", "caption"]):
            return "image"
        else:
            return "text"
