# app/service_rag.py
from app.config import settings
from app.utils import get_chroma_client
from app.utils import  embed


_retriever = None

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


class Retriever:
    """
    Production-ready Retriever using Chroma Server + SentenceTransformer embeddings.
    """

    def __init__(self):
        print("🔌 Initializing Retriever...")

        # Chroma client
        self.client = get_chroma_client()

        # Load existing collection (error if missing)
        self.collection_name = settings.RAG_COLLECTION

        try:
            self.collection = self.client.get_collection(self.collection_name)
        except Exception:
            raise RuntimeError(
                f"❌ Chroma collection '{self.collection_name}' not found. "
                f"Run the Chroma DB Init script before starting the server."
            )

        print(f"📚 Retriever loaded collection: {self.collection_name}")

    # -----------------------------------------------------
    # Vector Search RAG
    # -----------------------------------------------------
    def get_context(self, query: str) -> str:
        print(f"🔎 Querying Chroma for: {query}")

        try:
            # Local embedding (Chroma HTTP cannot embed)
            query_emb = embed([query])

            results = self.collection.query(
                query_embeddings=query_emb,
                n_results=settings.K
            )

        except Exception as e:
            print("❌ ChromaDB query failed:", e)
            return ""

        # Safety check
        if (
            not results
            or not results.get("documents")
            or not results["documents"][0]
        ):
            print("⚠️ No documents found.")
            return ""

        docs = results["documents"][0]
        metas = results["metadatas"][0]

        # Format retrieved chunks
        formatted = []
        for i, doc in enumerate(docs):
            meta = metas[i]
            speaker = meta.get("speaker", "Unknown")
            year = meta.get("year", "?")
            quarter = meta.get("quarter", "?")

            formatted.append(
                f"[Chunk {i+1}] Speaker: {speaker} — {year} {quarter}\n{doc}"
            )

        print(f"📄 Retrieved {len(docs)} documents.")
        return "\n\n".join(formatted)
