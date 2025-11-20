# app/services_llm.py
import json
import requests
from app.config import settings


_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = HuggingFaceLLM()
    return _llm


class BaseRequest:
    """
    Basic JSON POST request handler with HuggingFace Router error management.
    """

    def __init__(self):
        # secret safely stored in .env
        self.api_key = settings.API_KEY.get_secret_value()

    def build_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def post(self, url: str, payload: dict):
        try:
            res = requests.post(url, json=payload, headers=self.build_headers())
        except Exception as e:
            return {"error": f"Network error: {e}"}

        # HTTP errors
        if res.status_code >= 400:
            return {"error": f"HTTP {res.status_code}", "details": res.text}

        try:
            data = res.json()
        except Exception:
            return {"error": "Invalid JSON response", "raw": res.text}

        # HF Router error block
        if "error" in data:
            return {"error": "HF API Error", "details": data["error"]}

        return data


class HuggingFaceLLM(BaseRequest):

    def __init__(self):
        super().__init__()   
        self.model_name = f"{settings.MODEL}:{settings.PROVIDER}"
        self.API_URL = settings.API_URL

    def load_prompt(self, file_path) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"❌ PROMPT LOADING ERROR: {e}")
            return "You are an assistant. Answer the user's question."

    # --------------------------
    # Build standard payload
    # --------------------------
    def build_payload(self, query: str):
        prompt = self.load_prompt(settings.PROMPT_FILE)

        prompt = prompt.replace("{{question}}", query)

        return {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": prompt},  # FIX 3: Use system role
                {"role": "user", "content": query},
            ],
            "max_tokens": 500,
            "temperature": 0.2,
        }

    # --------------------------
    # Build RAG payload
    # --------------------------
    def build_rag_payload(self, query: str, context: str):
        prompt = self.load_prompt(settings.RAG_PROMPT_FILE)
        
        prompt = prompt.replace("{{context}}", context)
        prompt = prompt.replace("{{question}}", query)

        return {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": query},
            ],
            "max_tokens": 600,
            "temperature": 0.1,
        }

    # --------------------------
    # Ask normal question
    # --------------------------
    def ask(self, query: str):
        payload = self.build_payload(query)
        data = self.post(self.API_URL, payload)

        if not data or "error" in data:
            return f"❌ LLM Error: {json.dumps(data, indent=2)}"

        return data["choices"][0]["message"]["content"]

    # --------------------------
    # RAG Query
    # --------------------------
    def ask_rag(self, query: str, context: str):
        payload = self.build_rag_payload(query, context)
        data = self.post(self.API_URL, payload)

        if not data or "error" in data:
            return f"❌ RAG Error: {json.dumps(data, indent=2)}"

        return data["choices"][0]["message"]["content"]
