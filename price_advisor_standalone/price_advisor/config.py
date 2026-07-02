from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off", ""}


def _int_env(name: str, default: int, minimum: int = 1, maximum: int = 100) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(maximum, value))


def _float_env(name: str, default: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    try:
        value = float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(maximum, value))


@dataclass(slots=True)
class PriceAdvisorConfig:
    llm_backend: str = "ollama"
    allow_external_api: bool = False

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:30b-a3b"
    ollama_timeout_seconds: int = 120

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"

    db_dir: Path = Path("./runtime/chroma")
    collection_name: str = "price_refs"
    embedding_model: str = "BAAI/bge-m3"
    embedding_device: str = "cpu"
    top_k: int = 5

    max_range_expansion: float = 0.05
    min_references: int = 1

    @classmethod
    def from_env(cls) -> "PriceAdvisorConfig":
        load_dotenv(override=True)
        return cls(
            llm_backend=os.getenv("PRICE_ADVISOR_LLM_BACKEND", "ollama").strip().lower(),
            allow_external_api=_bool_env("PRICE_ADVISOR_ALLOW_EXTERNAL_API", False),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
            ollama_model=os.getenv("OLLAMA_MODEL", "qwen3:30b-a3b"),
            ollama_timeout_seconds=_int_env("OLLAMA_TIMEOUT_SECONDS", 120, 5, 600),
            gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
            db_dir=Path(os.getenv("PRICE_ADVISOR_DB_DIR", "./runtime/chroma")),
            collection_name=os.getenv("PRICE_ADVISOR_COLLECTION", "price_refs"),
            embedding_model=os.getenv("PRICE_ADVISOR_EMBEDDING_MODEL", "BAAI/bge-m3"),
            embedding_device=os.getenv("PRICE_ADVISOR_EMBEDDING_DEVICE", "cuda"),
            top_k=_int_env("PRICE_ADVISOR_TOP_K", 5, 1, 30),
            max_range_expansion=_float_env("PRICE_ADVISOR_MAX_RANGE_EXPANSION", 0.05, 0.0, 0.25),
            min_references=_int_env("PRICE_ADVISOR_MIN_REFERENCES", 1, 1, 30),
        )

