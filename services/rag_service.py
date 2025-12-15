import hashlib
import requests
import logging
from config import OLLAMA_URL

logger = logging.getLogger(__name__)

base_url = OLLAMA_URL.replace("/api/generate", "").replace("/api/chat", "").rstrip("/")
EMBED_ENDPOINT = f"{base_url}/api/embeddings"

embedding_cache = {}

# ==========================================
def get_embedding(text):
    if not text:
        return []
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    if text_hash in embedding_cache:
        return embedding_cache[text_hash]

    try:
        r = requests.post(EMBED_ENDPOINT, json={
            "model": "nomic-embed-text",
            "prompt": text
        })
        vector = r.json().get('embedding')
        if vector:
            embedding_cache[text_hash] = vector
            return vector
    except Exception as e:
        logger.error(f"Embedding Error: {e}")
    return []


def cosine_similarity(v1, v2):
    if not v1 or not v2:
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = sum(a * a for a in v1) ** 0.5
    mag2 = sum(b * b for b in v2) ** 0.5
    return dot / (mag1 * mag2) if mag1 * mag2 > 0 else 0


def retrieve_relevant_context(session, query, top_k=3):
    chunks = session.get('raw_text_chunks', [])
    embeddings = session.get('embeddings', [])
    if not chunks or not embeddings:
        return ""

    q_vec = get_embedding(query)
    if not q_vec:
        return ""

    scores = sorted([(cosine_similarity(q_vec, emb), chunk) for emb, chunk in zip(embeddings, chunks)],
                    key=lambda x: x[0], reverse=True)
    return "\n---\n".join([s[1] for s in scores[:top_k]])
