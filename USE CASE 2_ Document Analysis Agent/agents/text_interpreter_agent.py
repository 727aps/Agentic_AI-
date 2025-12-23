import os
import logging
from typing import Dict, Any, List
import asyncio
import requests
from dotenv import load_dotenv
from transformers import AutoTokenizer
from langchain_huggingface import HuggingFaceEmbeddings
from agents.base import MCPMessage, Agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


MAX_TOKENS = 1024
CHUNK_SIZE = 512

class TextInterpreterAgent(Agent):
    def __init__(self, name, chroma_client):
        super().__init__(name)
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")  # Can adjust
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        self.chroma_client = chroma_client
        self.chroma_collection = self.chroma_client.get_or_create_collection("text_insights")

        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not set in environment variables.")
        self.groq_model = "llama3-8b-8192"  # or "llama3-70b-8192"
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

    async def route(self, message: MCPMessage):
        logger.info(f"[{self.name}] Routing command: {message.command}")
        
        if message.command == "interpret_text":
            return await self.handle_interpret_text(message.payload)
        else:
            logger.warning(f"[{self.name}] Unknown command received: {message.command}")
            return {
                "status": "error",
                "message": f"Unknown command: {message.command}"
            }

    async def handle_interpret_text(self, payload: Dict[str, Any]):
        doc_id = payload.get("doc_id")
        sections = payload.get("sections", {})

        if not sections:
            logger.info(f"No text sections found in document {doc_id}")
            return {
                "status": "success",
                "message": f"No text sections to interpret in document {doc_id}",
                "text_insights": {}
            }

        text_insights = {}
        for section_title, section_text in sections.items():
            summary = await self._summarize_with_chunking(section_title, section_text)

            try:
                embedding = self.embeddings.embed_query(summary)
                unique_id = f"{doc_id}_{section_title.replace(' ', '_')}"
                self.chroma_collection.add(
                documents=[summary],
                embeddings=[embedding],
                ids=[unique_id],
                metadatas=[{
                    "doc_id": doc_id,                  
                    "section_title": section_title, 
                    "modality": "text"                 
                }]
)
            except Exception as e:
                logger.error(f"Failed to store in ChromaDB for section '{section_title}': {e}")

            text_insights[section_title] = summary
            print(f"\n=== Section: {section_title} ===\n{summary}\n")

        return {
            "status": "success",
            "message": f"Text interpreted for document {doc_id}",
            "text_insights": text_insights
        }

    async def _summarize_with_chunking(self, section_title: str, section_text: str) -> str:
        tokens = self.tokenizer.encode(section_text)
        if len(tokens) <= MAX_TOKENS:
            prompt = self._build_prompt(section_title, section_text)
            return await self._run_llm(prompt)

        chunks = self._split_tokens_into_chunks(tokens, CHUNK_SIZE)
        chunk_summaries = []

        for idx, chunk in enumerate(chunks):
            chunk_text = self.tokenizer.decode(chunk)
            chunk_prompt = (
                f"You are an intelligent assistant. This is chunk {idx + 1} of section '{section_title}'.\n\n"
                f"{chunk_text}\n\n"
                f"Summarize this chunk clearly."
            )
            try:
                chunk_summary = await self._run_llm(chunk_prompt)
            except Exception as e:
                logger.error(f"LLM failed on chunk {idx + 1} of section '{section_title}': {e}")
                chunk_summary = "Summary failed."

            chunk_summaries.append(chunk_summary)

        final_prompt = (
            f"The following are summaries of chunks from section '{section_title}':\n\n"
            + "\n\n".join(chunk_summaries) +
            "\n\nProvide an overall summary of the section based on these."
        )
        try:
            return await self._run_llm(final_prompt)
        except Exception as e:
            logger.error(f"Final summary failed for section '{section_title}': {e}")
            return "Final summary failed."

    def _split_tokens_into_chunks(self, tokens: List[int], chunk_size: int) -> List[List[int]]:
        return [tokens[i:i + chunk_size] for i in range(0, len(tokens), chunk_size)]

    def _build_prompt(self, section_title: str, section_text: str) -> str:
        return (
            f"You are an intelligent assistant. Please analyze and summarize the following "
            f"section titled '{section_title}':\n\n"
            f"{section_text}\n\n"
            f"Provide a concise summary highlighting the key points, insights, or any important data."
        )

    async def _run_llm(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.groq_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 512,
            "stream": False
        }
        try:
            async with asyncio.Semaphore(1):
                loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(self.groq_url, headers=headers, json=payload, timeout=10)
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"GROQ API failed: {e}")
            return "LLM request failed."

