# ingest_chroma.py

import json
import numpy as np
from functools import lru_cache

from chromadb import HttpClient
from sentence_transformers import SentenceTransformer
# from chromadb.utils import embedding_functions


from config import settings   # ✔ ton vrai fichier config.py dans app/

# ------------------------------------------
# 🔌 CHROMA CLIENT
# ------------------------------------------

_chroma_client = None

def get_chroma_client():
    """Create or return a global Chroma HTTP client."""
    global _chroma_client
    if _chroma_client is None:
        print(f"🔗 Connecting to Chroma at {settings.CHROMA_HOST}:{settings.CHROMA_PORT}")
        _chroma_client = HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT
        )
    return _chroma_client


# ------------------------------------------
# 🧠 EMBEDDING MODEL
# ------------------------------------------

@lru_cache(maxsize=1)
def get_embedder():
    print(f"🚀 Loading embedding model: {settings.EMBEDDING_MODEL}")
    return SentenceTransformer(settings.EMBEDDING_MODEL)


def embed(texts):
    """Compute normalized embeddings."""
    model = get_embedder()
    vecs = model.encode(texts, convert_to_numpy=True)

    # normalize vectors for better cosine similarity results
    vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)

    return vecs.tolist()


# ------------------------------------------
# 📥 INGESTION
# ------------------------------------------

def load_into_chroma(chunks_file):
    print("\n=====================================")
    print("📥 STARTING CHROMA INGESTION")
    print("=====================================\n")

    print(f"📄 Chunks file: {chunks_file}")
    print(f"🎯 Target collection: {settings.RAG_COLLECTION}")

    client = get_chroma_client()

    # Try to create or load the collection
    try:
        col = client.get_or_create_collection(
            name=settings.RAG_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
        print("✅ Collection ready.")
    except Exception as e:
        print("❌ Could not create/get collection:", e)
        return

    ids, docs, metas = [], [], []

    # Load chunks
    try:
        with open(chunks_file, "r") as f:
            for line in f:
                item = json.loads(line)
                ids.append(item["id"])
                docs.append(item["text"])
                metas.append(item.get("metadata", {}))

        print(f"📦 Loaded {len(ids)} chunks from file.")
    except Exception as e:
        print("❌ Error reading chunks file:", e)
        return

    # Compute embeddings
    try:
        embeddings = embed(docs)
        print("🧠 Embeddings computed.")
    except Exception as e:
        print("❌ Embedding computation failed:", e)
        return

    # Insert into Chroma
    try:
        col.add(
            ids=ids,
            documents=docs,
            metadatas=metas,
            embeddings=embeddings,
        )
        print(f"🔥 Successfully inserted {len(ids)} vectors into Chroma.")
    except Exception as e:
        print("❌ Failed to insert vectors:", e)
        return

    print("\n🏁 INGESTION COMPLETED\n")

# ------------------------------------------
# 📥 TEST INGESTION
# ------------------------------------------

def test_retriever():
    print("\n🔍 Testing Chroma Retriever...")

    client = get_chroma_client()
    col = client.get_collection(settings.RAG_COLLECTION)

    query = "What did Jensen Huang say about data center growth?"

    # 🔥 MUST embed here → HTTP Chroma can NOT embed
    query_emb = embed([query])

    results = col.query(
        query_embeddings=query_emb,
        n_results=5
    )

    print("\n🔎 Top 5 results:")
    docs = results["documents"][0]
    metas = results["metadatas"][0]

    for i in range(len(docs)):
        print(f"\n--- Result #{i+1} ---")
        print("Speaker:", metas[i].get("speaker"))
        print("Chunk:", docs[i][:600])


# ------------------------------------------
# ▶️ ENTRY POINT
# ------------------------------------------

if __name__ == "__main__":
    load_into_chroma(settings.CHUNKS_FILE)
    test_retriever()

