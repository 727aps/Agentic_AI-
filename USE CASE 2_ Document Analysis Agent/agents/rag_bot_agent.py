import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import time
import asyncio
import requests
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
import chromadb
from chromadb.config import Settings

from agents.base import MCPMessage, Agent

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGBotAgent(Agent):
    def __init__(self, name: str, chroma_persist_dir: str = "storage/chroma", chroma_client=None):
        super().__init__(name)

        if chroma_client is not None:
            self.client = chroma_client
        else:
            Path(chroma_persist_dir).mkdir(parents=True, exist_ok=True)
            self.client = chromadb.Client(Settings(
                persist_directory=chroma_persist_dir,
                anonymized_telemetry=False
            ))

        self.collection_name = "document_chunks"
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise RuntimeError("GROQ_API_KEY not found in environment.")

        self.groq_url = os.getenv("GROQ_URL", "https://api.groq.com/openai/v1/chat/completions")
        self.groq_model = os.getenv("GROQ_MODEL", "llama3-8b-8192")

        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        self.prompt_template = PromptTemplate.from_template(
            "You are an intelligent assistant.\n"
            "Given the following context, answer the question concisely and accurately.\n"
            "If the answer is not in the context, say 'I don't know.'\n\n"
            "Context:\n{context}\n\nQuestion: {input}\nAnswer:"
        )

    async def route(self, message: MCPMessage):
        if message.command == "query":
            query = message.payload.get("query", "")
            doc_id = message.payload.get("doc_id", None)  # Get doc_id to filter retrieval
            
            if not query:
                return {"status": "error", "message": "Empty query"}

            if not self.collection:
                return {"status": "error", "message": "Knowledge base is empty or not loaded"}

            try:
                if doc_id:
                    results = self.collection.query(
                        query_texts=[query],
                        n_results=3,
                        where={"doc_id": doc_id}
                    )
                    docs = [doc for doc in results['documents'][0] if doc]
                else:
                    results = self.collection.query(
                        query_texts=[query],
                        n_results=3,
                    )
                    docs = [doc for doc in results['documents'][0] if doc]

                if not docs:
                    return {"status": "success", "answer": "I don't know."}

                context = "\n\n".join(docs)
                prompt = self.prompt_template.format(context=context, input=query)

                answer = await self._call_groq_llm_async(prompt)

                return {"status": "success", "answer": answer}

            except Exception as e:
                logger.error(f"Failed to process query: {e}")
                return {"status": "error", "message": "Failed to process query."}

        elif message.command == "refresh_index":
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            return {"status": "success", "message": "Vectorstore reloaded"}

        return {"status": "error", "message": f"RAGBotAgent cannot handle command: {message.command}"}

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
            "max_tokens": 512,
        }

        for attempt in range(3):
            try:
                response = requests.post(self.groq_url, headers=headers, json=data, timeout=10)
                if response.status_code == 200:
                    res_json = response.json()
                    return res_json['choices'][0]['message']['content']
                else:
                    logger.warning(f"Groq API call failed with status {response.status_code}: {response.text}")
            except requests.RequestException as e:
                logger.error(f"Request exception on attempt {attempt + 1}: {e}")

            time.sleep(2)

        raise RuntimeError("Groq API call failed after 3 attempts.")
