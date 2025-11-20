# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
import os


class Settings(BaseSettings):

    # -----------------------------
    #   CHROMA SETTINGS
    # -----------------------------
    CHROMA_HOST: str = Field(default="localhost")
    CHROMA_PORT: int = Field(default=8001)

    # -----------------------------
    #   MODEL API SETTINGS
    # -----------------------------
    RAG_COLLECTION: str = Field(default="nvidia_earnings_calls")

    # -----------------------------
    #   EMBEDDINGS
    # -----------------------------
    EMBEDDING_MODEL: str = Field(default="BAAI/bge-base-en-v1.5")
    K: int = Field(default=10)
    
    # -----------------------------
    #   PATHS FOR LOCAL DATA
    # -----------------------------
    DATA_DIR: str = Field(default="./ingest/data")
    CHUNKS_FILENAME: str = Field(default="nvidia_chunks.jsonl")

    @property
    def CHUNKS_FILE(self) -> str:
        return os.path.join(self.DATA_DIR, self.CHUNKS_FILENAME)

settings = Settings()
