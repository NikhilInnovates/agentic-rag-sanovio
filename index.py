import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from ingest import extract_text_by_page, chunk_text, PDF_PATH

INDEX_PATH = "index_store/faiss.index"
META_PATH = "index_store/metadata.pkl"


def build_index():
    pages = extract_text_by_page(PDF_PATH)
    chunks = chunk_text(pages)

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = model.encode([c["text"] for c in chunks], show_progress_bar=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print("Index built successfully")


if __name__ == "__main__":
    build_index()
