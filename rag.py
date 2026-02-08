from dotenv import load_dotenv
load_dotenv()
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import requests
import json
from agent import classify_query, retrieval_k
from prompts import SYSTEM_PROMPT
from dotenv import load_dotenv
load_dotenv()

INDEX_PATH = "index_store/faiss.index"
META_PATH = "index_store/metadata.pkl"

OLLAMA_API_URL = "http://localhost:11434/api/chat"


def load_index():
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata


def retrieve(query: str):
    index, metadata = load_index()
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    q_type = classify_query(query)
    k = retrieval_k(q_type)

    q_emb = model.encode([query])
    distances, indices = index.search(np.array(q_emb), k)

    retrieved = [metadata[i] for i in indices[0]]
    return retrieved, q_type


def generate_answer(query: str, retrieved_chunks):
    context = "\n\n".join(
        [f"(Page {c['page']}) {c['text']}" for c in retrieved_chunks]
    )

    # Enhanced prompt to force English response
    enhanced_prompt = f"""You MUST respond ONLY in English. Do NOT respond in German.

Context (German product information):
{context}

Question: {query}

Instructions:
- Answer ONLY in English
- Reference German product IDs and names as they appear
- Quote relevant German text if needed, but explain it in English
- If information is not in the context, say "I don't know"

Answer in English:"""

    response = requests.post(OLLAMA_API_URL, json={
        "model": "llama3.2",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT + "\n\nCRITICAL: You MUST respond in English language only. Never respond in German."},
            {"role": "user", "content": enhanced_prompt}
        ],
        "stream": False
    })

    result = response.json()
    return result['message']['content']