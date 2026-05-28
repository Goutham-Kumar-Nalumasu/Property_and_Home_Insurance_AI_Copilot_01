import json
from pathlib import Path
from typing import Dict, List
from pypdf import PdfReader
#from PyPDF2 import PdfReader
import sys
sys.path.append('/home/ubuntu/homeshield-insurance-copilot_02/app')
from config import settings


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(f"\n\n[Page {page_number}]\n{text}")

    return "\n".join/pages if False else "\n".join(pages)


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    clean_text = " ".join(text.split())
    chunks = []

    start = 0
    while start < len(clean_text):
        end = start + chunk_size
        chunk = clean_text[start:end]
        chunks.append(chunk)

        if end >= len(clean_text):
            break

        start = end - overlap

    return chunks


def infer_policy_type(file_name: str) -> str:
    upper_name = file_name.upper()

    if "STANDARD" in upper_name:
        return "Standard"
    if "COMPREHENSIVE" in upper_name:
        return "Comprehensive"
    if "LANDLORD" in upper_name:
        return "Landlord Plus"
    if "GLOSSARY" in upper_name:
        return "Glossary"
    if "PERILS" in upper_name or "EXCLUSIONS" in upper_name:
        return "Perils and Exclusions"

    return "Unknown"


def build_chunks() -> List[Dict]:
    settings.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = list(settings.RAW_DATA_DIR.glob("*.pdf"))
    all_chunks = []

    chunk_id = 0

    for pdf_file in pdf_files:
        text = extract_pdf_text(pdf_file)
        chunks = chunk_text(
            text=text,
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP,
        )

        for chunk in chunks:
            all_chunks.append(
                {
                    "chunk_id": chunk_id,
                    "document": pdf_file.name,
                    "policy_type": infer_policy_type(pdf_file.name),
                    "text": chunk,
                }
            )
            chunk_id += 1

    with open(settings.CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)

    return all_chunks


if __name__ == "__main__":
    chunks = build_chunks()
    print(f"Created {len(chunks)} chunks at {settings.CHUNKS_FILE}")