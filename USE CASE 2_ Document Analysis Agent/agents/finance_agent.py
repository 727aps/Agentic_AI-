import os
import logging
import asyncio
import requests
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
import time
from chromadb.config import Settings
from agents.base import Agent, MCPMessage

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinanceAgent(Agent):
    def __init__(self, name: str, chroma_client):
        super().__init__(name)

        self.client = chroma_client
        self.collection_name = "document_chunks"
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise RuntimeError("GROQ_API_KEY not found in environment variables.")

        self.groq_url = os.getenv("GROQ_URL", "https://api.groq.com/openai/v1/chat/completions")
        self.groq_model = os.getenv("GROQ_MODEL", "llama3-8b-8192")

        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        self.load_chain()

    def load_chain(self):
        self.prompt_template = PromptTemplate.from_template(
            "You are a financial report generation assistant.\n"
            "Given the following financial document context, generate a structured summary report including:\n"
            "- Key statistics\n"
            "- Financial highlights\n"
            "- Important numbers and dates\n"
            "- Any anomalies or trends\n\n"
            "Context:\n{context}\n\nReport:"
        )

    async def route(self, message: MCPMessage):
        if message.command == "generate_report":
            doc_id = message.payload.get("doc_id")
            if not doc_id:
                return {"status": "error", "message": "Missing 'doc_id' in payload."}

            try:
                results = self.collection.query(
                    query_texts=["financial report"],  # dummy query to activate search
                    n_results=5,
                    where={"doc_id": doc_id}
                )
                docs = [doc for doc in results['documents'][0] if doc]

                if not docs:
                    return {"status": "error", "message": f"No document chunks found for doc_id: {doc_id}"}

                context = "\n\n".join(docs)
                prompt = self.prompt_template.format(context=context)

                # Call Groq API to generate report
                report = await self._call_groq_llm_async(prompt)

                return {"status": "success", "report": report}

            except Exception as e:
                logger.error(f"Error generating report for doc_id {doc_id}: {e}")
                return {"status": "error", "message": "Failed to generate report."}

        elif message.command == "refresh_index":
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            self.load_chain()
            return {"status": "success", "message": "Vectorstore reloaded"}

        return {"status": "error", "message": f"FinanceAgent cannot handle command: {message.command}"}

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
