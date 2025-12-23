import json
import os
import uuid
import asyncio
import gradio as gr
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from agents.base import MCPMessage
from agents.router_agent import RouterAgent
from agents.knowledge_base_agent import KnowledgeBaseAgent
from agents.rag_bot_agent import RAGBotAgent
from agents.finance_agent import FinanceAgent
from agents.document_extraction_agent import DocumentExtractionAgent
from agents.document_structuring_agent import DocumentStructuringAgent
from agents.text_interpreter_agent import TextInterpreterAgent
from agents.table_interpreter_agent import TableInterpreterAgent
from agents.image_interpreter_agent import ImageInterpreterAgent

load_dotenv()

persist_dir = os.getenv("CHROMA_PERSIST_DIRECTORY", "storage/chroma")
chroma_client = chromadb.Client(Settings(persist_directory=persist_dir))

extractor = DocumentExtractionAgent("DocumentExtractionAgent")
structurer = DocumentStructuringAgent("DocumentStructuringAgent")
text_interpreter = TextInterpreterAgent("TextInterpreterAgent", chroma_client)
table_interpreter = TableInterpreterAgent("TableInterpreterAgent", chroma_client)
image_interpreter = ImageInterpreterAgent("ImageInterpreterAgent", chroma_client)

knowledge = KnowledgeBaseAgent(
    name="KnowledgeBaseAgent",
    extraction_agent=extractor,
    structuring_agent=structurer,
    text_interpreter=text_interpreter,
    table_interpreter=table_interpreter,
    image_interpreter=image_interpreter,
    chroma_client=chroma_client
)

finance_agent = FinanceAgent("FinanceAgent", chroma_client)
rag_bot_agent = RAGBotAgent("RAGBotAgent", chroma_client=chroma_client)
router = RouterAgent("RouterAgent", knowledge, rag_bot_agent, finance_agent)

doc_id_holder = {"doc_id": None}


async def upload_document(file, title, date):
    if file is None:
        return "Please upload a PDF file."
    
    doc_path = file.name
    doc_id = str(uuid.uuid4())
    doc_id_holder["doc_id"] = doc_id

    msg = MCPMessage(
        sender="User",
        receiver="RouterAgent",
        command="upload_document",
        payload={
            "doc_id": doc_id,
            "filename": doc_path,
            "metadata": {
                "title": title,
                "date": date,
                "type": "pdf"
            }
        }
    )
    response = await router.handle(msg)
    return json.dumps(response, indent=2)


async def ask_query(query):
    doc_id = doc_id_holder.get("doc_id")
    if not doc_id:
        return "No document uploaded yet."
    
    msg = MCPMessage(
        sender="User",
        receiver="RouterAgent",
        command="user_query",
        payload={"query": query, "doc_id": doc_id}
    )
    response = await router.handle(msg)
    return json.dumps(response, indent=2)


async def generate_report():
    doc_id = doc_id_holder.get("doc_id")
    if not doc_id:
        return "No document uploaded yet."
    
    msg = MCPMessage(
        sender="User",
        receiver="RouterAgent",
        command="generate_report",
        payload={"query": "generate a financial summary report", "doc_id": doc_id}
    )
    response = await router.handle(msg)
    return json.dumps(response, indent=2)


with gr.Blocks(title="Document Analysis AI") as demo:
    gr.Markdown("# 📄 Document Analysis & Q&A System")

    with gr.Tab("1. Upload Document"):
        file_input = gr.File(label="Upload PDF")
        title_input = gr.Textbox(label="Document Title")
        date_input = gr.Textbox(label="Document Date (YYYY-MM-DD)")
        upload_button = gr.Button("Upload")
        upload_output = gr.Textbox(label="Upload Status / Response", lines=10)

    with gr.Tab("2. Ask a Question"):
        question_input = gr.Textbox(label="Enter your query")
        ask_button = gr.Button("Submit Query")
        query_output = gr.Textbox(label="Query Response", lines=10)

    with gr.Tab("3. Generate Report"):
        report_button = gr.Button("Generate Financial Report")
        report_output = gr.Textbox(label="Report Output", lines=10)

    upload_button.click(upload_document, inputs=[file_input, title_input, date_input], outputs=upload_output)
    ask_button.click(ask_query, inputs=[question_input], outputs=query_output)
    report_button.click(generate_report, outputs=report_output)

def start_gradio():
    import nest_asyncio
    nest_asyncio.apply()
    demo.launch()

if __name__ == "__main__":
    start_gradio()
