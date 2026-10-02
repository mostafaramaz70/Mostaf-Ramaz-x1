"""
PDF text extraction helper.
Tries pypdf if installed; otherwise returns structured placeholder.
"""

from typing import Dict, Any
from pathlib import Path


def extract_pdf_text(file_path: str) -> Dict[str, Any]:
    path = Path(file_path)
    if not path.exists():
        return {
            "status": "FILE_NOT_FOUND",
            "file_path": file_path,
            "text": "",
            "pages": 0,
        }

    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages = []
        for i, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            pages.append({"page": i + 1, "text": txt})

        full = "\n\n".join(p["text"] for p in pages).strip()
        return {
            "status": "OK",
            "file_path": file_path,
            "text": full,
            "pages": len(pages),
            "engine": "pypdf",
        }
    except Exception as e:
        return {
            "status": "PARSER_UNAVAILABLE_OR_FAILED",
            "file_path": file_path,
            "text": (
                f"[PDF_EXTRACTION_PENDING]\nFile: {file_path}\n"
                f"Install pypdf for real extraction. Error: {e}"
            ),
            "pages": 0,
            "engine": "placeholder",
            "error": str(e),
        }
