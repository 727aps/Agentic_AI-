from agents.base import MCPMessage, Agent
from typing import List
import re

class DocumentStructuringAgent(Agent):
    def __init__(self, name):
        super().__init__(name)

    async def route(self, message: MCPMessage):
        if message.command == "structure_document":
            return await self.handle_structure(message.payload)
        return {"status": "error", "message": f"Unknown command: {message.command}"}

    async def handle_structure(self, payload):
        doc_id = payload.get("doc_id")
        raw_text = payload.get("text_text", "")
        image_text = payload.get("image_text", "")
        tables = payload.get("tables", [])

        sections = {}

        # === Split raw text into sections ===
        text_sections = self._split_into_sections(raw_text)
        for i, (title, content) in enumerate(text_sections.items()):
            sections[f"Text Section {i + 1}: {title}"] = content.strip()

        # === Split OCR text into sections ===
        image_sections = self._split_into_sections(image_text)
        for i, (title, content) in enumerate(image_sections.items()):
            sections[f"OCR Section {i + 1}: {title}"] = content.strip()

        # === Handle tables ===
        for idx, table in enumerate(tables):
            formatted_table = self._format_table_to_text(table)
            sections[f"Table {idx + 1}"] = formatted_table
            print(f"Formatted Table {idx + 1}:\n{formatted_table}\n")

        print("Extracted Text:", raw_text[:300])
        print("OCR Text:", image_text[:300])
        print("First Table:", tables[0] if tables else "No tables")

        structured = {
            "doc_id": doc_id,
            "sections": sections
        }

        return {
            "status": "success",
            "message": f"Document structured: {doc_id}",
            "structured": structured
        }

    def _split_into_sections(self, text: str) -> dict:

        if not text.strip():
            return {}

        pattern = r"(?:\n|\r|^)([A-Z][A-Za-z0-9 ,\-:]{3,60})(?:\n|\r)"
        parts = re.split(pattern, text)
        sections = {}

        i = 1
        while i < len(parts):
            title = parts[i].strip()
            content = parts[i + 1].strip() if i + 1 < len(parts) else ""
            sections[title] = content
            i += 2

        if not sections:
            sections["Full Text"] = text

        return sections

    def _format_table_to_text(self, data: List[List[str]]) -> str:
        if not data:
            return ""

        col_widths = []
        num_cols = max(len(row) for row in data)

        for col_idx in range(num_cols):
            max_len = max((len(str(row[col_idx])) if col_idx < len(row) else 0) for row in data)
            col_widths.append(max_len)

        lines = []
        for row_idx, row in enumerate(data):
            formatted_cells = []
            for col_idx in range(num_cols):
                cell = row[col_idx] if col_idx < len(row) else ""
                formatted_cells.append(str(cell).ljust(col_widths[col_idx]))
            line = " | ".join(formatted_cells)
            lines.append(line)

            if row_idx == 0:
                separator = " | ".join("-" * w for w in col_widths)
                lines.append(separator)

        return "\n".join(lines)
