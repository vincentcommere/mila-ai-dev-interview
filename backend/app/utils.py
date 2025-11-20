# app/utils.py

import numpy as np
from functools import lru_cache

from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions

from chromadb import HttpClient

from app.config import settings


_chroma_client = None

def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT
        )
    return _chroma_client


@lru_cache(maxsize=1) #model est chargé UNE seule fois
def get_embedder():
    print("🚀 Loading embedding model:", settings.EMBEDDING_MODEL)
    return SentenceTransformer(settings.EMBEDDING_MODEL)

# @lru_cache(maxsize=1)  # modèle chargé UNE seule fois
# def get_embedder():
#     print("🚀 Loading embedding model:", settings.EMBEDDING_MODEL)
#     return embedding_functions.SentenceTransformerEmbeddingFunction(
#         model_name=settings.EMBEDDING_MODEL
#     )


def embed(texts):
    model = get_embedder()
    vecs = model.encode(texts, convert_to_numpy=True)

    # 🔥 normalisation → meilleure qualité cosine
    vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)

    return vecs.tolist()


def test_retriever():
    print("\n🔍 Testing Chroma Retriever...")

    client = get_chroma_client()
    col = client.get_collection(settings.RAG_COLLECTION, embedding_function=get_embedder(),)

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
