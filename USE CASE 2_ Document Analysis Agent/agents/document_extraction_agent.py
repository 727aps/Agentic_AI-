import os
from agents.base import Agent, MCPMessage
import fitz 
import pytesseract
from PIL import Image
import io
import pdfplumber
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from agents.base import MCPMessage, Agent


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

def extract_ocr_text_from_images(pdf_path, lang='eng'):
    doc = fitz.open(pdf_path)
    ocr_texts = []

    for page in doc:
        images = page.get_images(full=True)
        for img in images:
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))

            # OCR the image
            ocr_text = pytesseract.image_to_string(image, lang=lang).strip()
            if ocr_text:
                ocr_texts.append(ocr_text)

    return "\n\n".join(ocr_texts).strip()

def extract_tables_from_pdf(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables()
            if page_tables:
                tables.extend(page_tables)
    return tables


class DocumentExtractionAgent(Agent):
    def __init__(self, name):
        super().__init__(name)

    async def route(self, message: MCPMessage):
        if message.command == "extract_document":
            return await self.handle_extraction(message.payload)
        return {"status": "error", "message": f"Unknown command: {message.command}"}

    async def handle_extraction(self, payload):
        filepath = payload.get("filename")
        doc_id = payload.get("doc_id")

        if not os.path.exists(filepath):
            return {"status": "error", "message": f"File not found: {filepath}"}

        try:
            extracted_text = extract_text_from_pdf(filepath)
            ocr_text = extract_ocr_text_from_images(filepath)
            extracted_tables = extract_tables_from_pdf(filepath)

            extracted = {
                "doc_id": doc_id,
                "text_text": extracted_text,       # Normal text from pages
                "image_text": ocr_text,            # OCR text from images
                "tables": extracted_tables         # Tables as lists of lists
            }

            print("Text extracted (first 500 chars):")
            print(extracted['text_text'][:500])

            print("\nOCR Text extracted (first 500 chars):")
            print(extracted['image_text'][:500])

            print("\nNumber of tables extracted:", len(extracted['tables']))
            if extracted['tables']:
                print("First table:")
                for row in extracted['tables'][0]:
                    print(row)


            return {
                "status": "success",
                "message": f"Document extracted: {doc_id}",
                "extracted": extracted
            }

        except Exception as e:
            return {"status": "error", "message": f"Extraction failed: {str(e)}"}

