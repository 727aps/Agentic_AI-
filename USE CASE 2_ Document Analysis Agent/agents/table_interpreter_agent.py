import os
import logging
import asyncio
from typing import Dict, Any
import requests
from dotenv import load_dotenv
from transformers import AutoTokenizer
from langchain_huggingface import HuggingFaceEmbeddings
from agents.base import MCPMessage, Agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

class TableInterpreterAgent(Agent):
    def __init__(self, name, chroma_client):
        super().__init__(name)
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        self.chroma_client = chroma_client
        self.chroma_collection = self.chroma_client.get_or_create_collection("table_insights")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise RuntimeError("GROQ_API_KEY not found in environment.")
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.groq_model = "llama3-8b-8192"

        self.max_tokens_per_chunk = 800

    async def route(self, message: MCPMessage):
        logger.info(f"[{self.name}] Routing command: {message.command}")

        if message.command == "interpret_tables":
            return await self.interpret_tables(message.payload)
        else:
            logger.warning(f"[{self.name}] Unknown command received: {message.command}")
            return {
                "status": "error",
                "message": f"Unknown command: {message.command}"
            }


    async def interpret_tables(self, structured_input: Dict[str, Any]) -> Dict[str, Any]:
        doc_id = structured_input.get("doc_id", "unknown_doc")
        sections = structured_input.get("sections", {})

        table_sections = {
            title: content for title, content in sections.items()
            if title.lower().startswith("table")
        }

        if not table_sections:
            logger.info(f"No table sections found in document {doc_id}")
            return {
                "status": "success",
                "message": f"No tables to interpret in document {doc_id}",
                "table_insights": {}
            }

        table_insights = {}

        for title, table_text in table_sections.items():
            chunks = self._chunk_table_text(table_text)
            interpretations = []

            for i, chunk in enumerate(chunks):
                prompt = self._build_prompt(title, chunk)
                try:
                    summary = await self._call_groq_llm_async(prompt)
                    interpretations.append(summary)

                    embedding = self.embeddings.embed_query(summary)
                    unique_id = f"{doc_id}_{title.replace(' ', '_')}_{i}"
                    self.collection.add(
                    documents=[chunk],
                    metadatas=[{
                        "doc_id": doc_id,                   
                        "modality": "table",
                        "table_index": i
                    }],
                    ids=[f"{doc_id}_chunk_{i}"],
                    embeddings=[embedding]
                )
                except Exception as e:
                    logger.error(f"Failed to interpret chunk {i} in '{title}': {e}")
                    interpretations.append("Failed to interpret chunk.")

            full_summary = "\n\n".join(interpretations)
            table_insights[title] = full_summary

            print(f"\nTable: {title}\nInterpretation:\n{full_summary}\n")
        return {
            "status": "success",
            "message": f"Tables interpreted for document {doc_id}",
            "table_insights": table_insights
        }

    def _chunk_table_text(self, table_text: str):
        lines = table_text.strip().splitlines()
        chunks = []
        current_chunk = []
        token_count = 0

        for line in lines:
            line_tokens = len(self.tokenizer.encode(line))
            if token_count + line_tokens > self.max_tokens_per_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                token_count = line_tokens
            else:
                current_chunk.append(line)
                token_count += line_tokens

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def _build_prompt(self, title: str, table_text: str) -> str:
        return (
            f"You are a financial data analyst. Interpret the following table titled '{title}':\n\n"
            f"{table_text}\n\n"
            f"Summarize the key insights, patterns, anomalies, and trends in simple terms."
        )

    async def _call_groq_llm_async(self, prompt: str) -> str:
        return await asyncio.to_thread(self._call_groq_llm_sync, prompt)

    def _call_groq_llm_sync(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.groq_api_key}"
        }
        data = {
            "model": self.groq_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 512
        }

        for attempt in range(3):
            try:
                response = requests.post(self.groq_url, headers=headers, json=data, timeout=10)
                if response.status_code == 200:
                    res_json = response.json()
                    return res_json['choices'][0]['message']['content']
                else:
                    logging.warning(f"Groq API call failed with status {response.status_code}: {response.text}")
            except requests.RequestException as e:
                logging.error(f"Request exception on attempt {attempt+1}: {e}")

            asyncio.sleep(2)

        raise RuntimeError("Groq API call failed after 3 attempts.")