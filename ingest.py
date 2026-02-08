import fitz
from pathlib import Path
from typing import List, Dict

PDF_PATH = Path("data/product_catalog_01.pdf")


def extract_text_by_page(pdf_path: Path) -> List[Dict]:
    doc = fitz.open(pdf_path)
    pages = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text()
        if text.strip():
            pages.append({
                "page": page_number,
                "text": text
            })
    return pages


def chunk_text(pages: List[Dict], chunk_size: int = 600, overlap: int = 100):
    chunks = []
    chunk_id = 0

    for page in pages:
        words = page["text"].split()
        start = 0

        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            chunks.append({
                "chunk_id": chunk_id,
                "page": page["page"],
                "text": chunk_text
            })

            chunk_id += 1
            start += chunk_size - overlap

    return chunks


if __name__ == "__main__":
    pages = extract_text_by_page(PDF_PATH)
    chunks = chunk_text(pages)

    print(f"Pages: {len(pages)}")
    print(f"Chunks: {len(chunks)}")
    print(chunks[0]["text"][:500])
