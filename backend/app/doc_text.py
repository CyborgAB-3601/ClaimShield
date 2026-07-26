from pathlib import Path

from pypdf import PdfReader

from app.sarvam_client import digitise


def extract_paginated_text(file_path: str) -> str:
    """Get digitised text for a document upload, with real page numbers where possible.

    Sarvam Digitise caps PDFs at 10 pages, but real policy wordings and claim forms can run
    well beyond that. Born-digital PDFs are read directly with pypdf instead, which also
    yields exact page numbers (better than anything Digitise's markdown output would give
    us). Only non-PDF uploads (a photographed page, say) go through Digitise.
    """
    if Path(file_path).suffix.lower() != ".pdf":
        return digitise(file_path)

    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        pages.append(f"[PAGE {i}]\n{page.extract_text()}")
    return "\n\n".join(pages)
