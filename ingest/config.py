# app/config.py
from pydantic_settings import BaseSettings
# from pydantic_settings import SettingsConfigDict
from pydantic import Field
from pydantic import SecretStr
import os

class Settings(BaseSettings):
    # -----------------------------
    #   APP SETTINGS
    # -----------------------------
    # APP_NAME: str = Field(default="Nvidia Earnings Call Assistant API")
    # APP_VERSION: str = Field(default="1.0.0")
    # ENV: str = Field(default="development")

    # -----------------------------
    #   CHROMA SETTINGS
    # -----------------------------
    CHROMA_HOST: str = Field(default="localhost")
    CHROMA_PORT: int = Field(default=8001)
    # CHROMA_PERSIST_DIR: str = Field(default="chroma_db")

    # -----------------------------
    #   MODEL API SETTINGS
    # -----------------------------
    # API_URL: str = Field(..., description="URL du provider LLM")
    # API_KEY: SecretStr = Field(..., description="API key (sécurisée)")
    # MODEL: str = Field(..., description="Nom du modèle LLM")
    # PROVIDER: str = Field(default="fireworks-ai")
    RAG_COLLECTION: str = Field(default="nvidia_earnings_calls")

    # -----------------------------
    #   EMBEDDINGS
    # -----------------------------
    EMBEDDING_MODEL: str = Field(default="BAAI/bge-large-en-v1.5")
    K: int = Field(default=10)
    # -----------------------------
    #   PATHS FOR LOCAL DATA
    # -----------------------------
    DATA_DIR: str = Field(default="data")
    CHUNKS_FILENAME: str = Field(default="nvidia_chunks.jsonl")

    @property
    def CHUNKS_FILE(self) -> str:
        return os.path.join(self.DATA_DIR, self.CHUNKS_FILENAME)

    # -----------------------------
    #   LOADING CONFIG
    # -----------------------------
    # model_config = SettingsConfigDict(
    #     env_file=".env",
    #     env_file_encoding="utf-8",
    #     case_sensitive=False,
    #     extra="forbid",   # interdit les inconnues (comportement normal)
    # )


settings = Settings()
