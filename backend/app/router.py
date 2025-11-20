# app/src/router.py

from fastapi import APIRouter
from app.schema import Payload
from app.service_llm import get_llm
from app.service_rag import get_retriever


router = APIRouter()
# Singleton LLM
llm = get_llm()
# Singleton Retriever
retriever = get_retriever()


@router.get("/")
async def ask_question():
    return {"answer": "test ok !"}

@router.post("/dummy")
async def dummy_route(payload: Payload):
    return {"answer": f"You said: {payload.query}"}

@router.post("/llm")
async def llm_route(payload: Payload):
    """
    Calls the LLM synchronously (model already loaded globally).
    Returns: { "role": "assistant", "answer": "..."}
    """
    try:
        answer = llm.ask(payload.query)

        return {
            "role": "assistant",
            "answer": answer
        }

    except Exception as e:
        print("❌ LLM ERROR:", e)
        return {
            "role": "assistant",
            "answer": f"LLM error: {str(e)}"
        }

@router.post("/rag")
async def rag_route(payload: Payload):
    """
    RAG pipeline:
    1) Retrieve context
    2) Ask LLM with RAG prompt
    """

    try:
        # 1. Retrieve context from your retriever
        context = retriever.get_context(payload.query)

        # 2. Ask LLM with RAG (pass both query + context)
        answer = llm.ask_rag(payload.query, context)

        return {
            "role": "assistant",
            "context_used": context,   # optionnel
            "answer": answer
        }

    except Exception as e:
        print("❌ RAG ERROR:", e)
        return {
            "role": "assistant",
            "answer": f"RAG error: {str(e)}"
        }
