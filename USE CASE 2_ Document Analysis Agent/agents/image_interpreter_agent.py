import os
import logging
import asyncio
import requests
import time
from typing import Dict, Any, List
from dotenv import load_dotenv
from transformers import AutoTokenizer
from langchain_huggingface import HuggingFaceEmbeddings
from agents.base import MCPMessage, Agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

MAX_TOKENS = 1024
CHUNK_SIZE = 512

class ImageInterpreterAgent(Agent):
    def __init__(self, name, chroma_client):
        super().__init__(name)
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.chroma_client = chroma_client
        self.chroma_collection = self.chroma_client.get_or_create_collection("image_insights")


        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not set in environment variables.")

        self.groq_model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        self.groq_url = os.getenv("GROQ_URL", "https://api.groq.com/openai/v1/chat/completions")

    async def route(self, message: MCPMessage):
        if message.command == "interpret_image":
            doc_id = message.payload.get("doc_id")
            text_sections = message.payload.get("text_sections")
            return await self.interpret_image(doc_id, text_sections)
        else:
            logger.warning(f"Unknown command received by {self.name}: {message.command}")
            return {"status": "error", "message": f"Unknown command: {message.command}"}

    def chunk_text(self, text: str) -> List[str]:
        tokens = self.tokenizer.encode(text)
        chunks = []
        for i in range(0, len(tokens), MAX_TOKENS):
            chunk_tokens = tokens[i:i+MAX_TOKENS]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
        return chunks

    def build_prompt(self, title: str, text: str) -> str:
        return (
            f"You are an AI assistant helping interpret text extracted from an image. "
            f"Here is the OCR output for the section '{title}':\n\n"
            f"{text}\n\n"
            f"Please summarize what this section is about and highlight any useful insights."
        )

    def call_groq_api(self, prompt: str, retries=3, delay=2) -> str:
        for attempt in range(retries):
            try:
                response = requests.post(
                    self.groq_url,
                    json={
                        "model": self.groq_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 512,
                        "stream": False,
                    },
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=10,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"Groq API call failed (attempt {attempt+1}): {response.status_code}")
            except Exception as e:
                logger.error(f"Groq API exception (attempt {attempt+1}): {e}")

            time.sleep(delay)

        raise Exception("Groq API failed after retries")

    async def interpret_image(self, doc_id: str, text_sections: Dict[str, str]) -> Dict[str, Any]:
        image_insights = {}

        for title, text in text_sections.items():
            logger.info(f"Processing section: {title}")
            chunks = self.chunk_text(text)
            interpretations = []

            for i, chunk in enumerate(chunks):
                prompt = self.build_prompt(title, chunk)
                try:

                    loop = asyncio.get_running_loop()
                    summary = await loop.run_in_executor(None, self.call_groq_api, prompt)
                    interpretations.append(summary)

                    try:
                        embedding = self.embeddings.embed_documents([summary])[0]
                    except Exception as e:
                        logger.error(f"Embedding failed for chunk {i} of '{title}': {e}")
                        embedding = [0.0] * 384 

                    unique_id = f"{doc_id}_{title.replace(' ', '_')}_{i}"
                    self.collection.add(
                    documents=[summary],
                    embeddings=[embedding],
                    ids=[f"{doc_id}_image_{i}"],
                    metadatas=[{
                        "doc_id": doc_id,                  
                        "modality": "image",
                        "caption_index": i
                    }]
                )
                except Exception as e:
                    logger.error(f"Error interpreting chunk {i} of '{title}': {e}")
                    interpretations.append("Failed to interpret this chunk.")

            full_summary = "\n\n".join(interpretations)
            image_insights[title] = full_summary
            print(f"\nSection: {title}\nInterpretation:\n{full_summary}\n")

        return {
            "status": "success",
            "message": f"OCR sections interpreted for document {doc_id}",
            "image_insights": image_insights
        }