"""
services/semantic_search.py — Semantic search over tasks using sentence embeddings.

Primary path  : sentence-transformers + chromadb (persistent vector store).
Fallback path : keyword / TF-IDF search when heavy dependencies are absent.
"""

import os
import json
import math
import re
from config import active_config as cfg

# ---------------------------------------------------------------------------
# Try to import optional heavy dependencies
# ---------------------------------------------------------------------------
try:
    from sentence_transformers import SentenceTransformer
    _ST_AVAILABLE = True
except ImportError:
    _ST_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    _CHROMA_AVAILABLE = True
except ImportError:
    _CHROMA_AVAILABLE = False


# ---------------------------------------------------------------------------
# Lazy singletons
# ---------------------------------------------------------------------------

_model = None
_chroma_client = None
_collection_cache = {}


def _get_model():
    global _model
    if _model is None and _ST_AVAILABLE:
        _model = SentenceTransformer(cfg.EMBEDDING_MODEL)
    return _model


def _get_collection(user_id: int):
    """Return (or create) the per-user Chroma collection."""
    global _chroma_client, _collection_cache
    if not _CHROMA_AVAILABLE:
        return None
    if _chroma_client is None:
        os.makedirs(cfg.VECTOR_STORE_DIR, exist_ok=True)
        _chroma_client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=cfg.VECTOR_STORE_DIR,
                anonymized_telemetry=False,
            )
        )
    name = f"user_{user_id}_tasks"
    if name not in _collection_cache:
        _collection_cache[name] = _chroma_client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection_cache[name]


# ---------------------------------------------------------------------------
# Index a task
# ---------------------------------------------------------------------------

def index_task(task: dict):
    """Embed and store a task in the vector store."""
    model = _get_model()
    collection = _get_collection(task["user_id"])
    if model is None or collection is None:
        return  # Graceful no-op

    text = _task_to_text(task)
    embedding = model.encode(text).tolist()
    doc_id = str(task["id"])

    collection.upsert(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{
            "task_id": task["id"],
            "title": task.get("title", ""),
            "subject": task.get("subject", ""),
            "status": task.get("status", ""),
            "priority": task.get("priority", ""),
        }],
    )


def remove_task_from_index(task_id: int, user_id: int):
    collection = _get_collection(user_id)
    if collection is None:
        return
    try:
        collection.delete(ids=[str(task_id)])
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def semantic_search(query: str, user_id: int, top_k: int = 10) -> list[dict]:
    """
    Return a ranked list of {'task_id', 'score', 'title', 'subject'} dicts.
    Falls back to keyword search when embeddings are unavailable.
    """
    if _ST_AVAILABLE and _CHROMA_AVAILABLE:
        return _vector_search(query, user_id, top_k)
    return _keyword_search(query, user_id, top_k)


def _vector_search(query: str, user_id: int, top_k: int) -> list[dict]:
    model = _get_model()
    collection = _get_collection(user_id)
    if model is None or collection is None:
        return _keyword_search(query, user_id, top_k)

    q_embedding = model.encode(query).tolist()
    try:
        results = collection.query(
            query_embeddings=[q_embedding],
            n_results=min(top_k, collection.count() or 1),
            include=["metadatas", "distances"],
        )
    except Exception:
        return _keyword_search(query, user_id, top_k)

    output = []
    for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
        output.append({
            "task_id": meta["task_id"],
            "title":   meta["title"],
            "subject": meta["subject"],
            "status":  meta["status"],
            "score":   round(1 - dist, 4),  # cosine distance → similarity
        })
    return output


def _keyword_search(query: str, user_id: int, top_k: int) -> list[dict]:
    """Simple TF-IDF-style keyword fallback over in-memory tasks."""
    from models.task import get_tasks
    tasks = get_tasks(user_id)
    tokens = set(re.findall(r"\w+", query.lower()))
    scored = []
    for t in tasks:
        text = _task_to_text(t).lower()
        hits = sum(1 for tok in tokens if tok in text)
        if hits > 0:
            scored.append((hits, t))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "task_id": t["id"],
            "title":   t["title"],
            "subject": t.get("subject", ""),
            "status":  t["status"],
            "score":   round(hits / (len(tokens) or 1), 4),
        }
        for hits, t in scored[:top_k]
    ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _task_to_text(task: dict) -> str:
    """Concatenate task fields into a single searchable string."""
    parts = [
        task.get("title", ""),
        task.get("description", ""),
        task.get("subject", ""),
        task.get("tags", ""),
        task.get("priority", ""),
    ]
    return " ".join(p for p in parts if p)


def reindex_all_tasks(user_id: int):
    """Rebuild the entire vector index for a user's tasks."""
    from models.task import get_tasks
    tasks = get_tasks(user_id)
    for task in tasks:
        index_task(task)
