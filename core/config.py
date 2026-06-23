from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .models import CompareThresholds


def _bool_env(name: str, default: bool) -> bool:
    return os.getenv(name, "1" if default else "0").strip().lower() not in {"0", "false", "no", "off"}


@dataclass(slots=True)
class EnterpriseConfig:
    thresholds: CompareThresholds = field(default_factory=CompareThresholds)
    strict_privacy: bool = True
    allow_network: bool = False
    model_root: Path = Path("models")
    embedding_model_path: str = ""
    reranker_model_path: str = ""
    enable_semantic_matching: bool = True
    enable_reranker: bool = True
    semantic_batch_size: int = 32
    reranker_batch_size: int = 16
    max_excel_rows: int = 1_000_000
    max_pdf_pages: int = 500
    max_upload_mb: int = 2048
    fuzzy_top_k: int = 8
    semantic_top_k: int = 5
    max_fuzzy_candidates: int = 250_000
    report_constant_memory: bool = True
    random_state: int = 42
    max_concurrent_jobs: int = 2
    job_retention_hours: int = 24
    runtime_root: Path = Path("runtime/jobs")

    @classmethod
    def from_env(cls) -> "EnterpriseConfig":
        return cls(
            strict_privacy=_bool_env("HSMT_STRICT_PRIVACY", True),
            allow_network=_bool_env("HSMT_ALLOW_NETWORK", False),
            model_root=Path(os.getenv("HSMT_MODEL_ROOT", "models")),
            embedding_model_path=os.getenv("HSMT_EMBEDDING_MODEL", ""),
            reranker_model_path=os.getenv("HSMT_RERANKER_MODEL", ""),
            enable_semantic_matching=_bool_env("HSMT_ENABLE_EMBEDDINGS", True),
            enable_reranker=_bool_env("HSMT_ENABLE_RERANKER", True),
            semantic_batch_size=int(os.getenv("HSMT_EMBED_BATCH", "32")),
            reranker_batch_size=int(os.getenv("HSMT_RERANK_BATCH", "16")),
            max_excel_rows=int(os.getenv("HSMT_MAX_EXCEL_ROWS", "1000000")),
            max_pdf_pages=int(os.getenv("HSMT_MAX_PDF_PAGES", "500")),
            max_upload_mb=int(os.getenv("HSMT_MAX_UPLOAD_MB", "2048")),
            fuzzy_top_k=int(os.getenv("HSMT_FUZZY_TOP_K", "8")),
            semantic_top_k=int(os.getenv("HSMT_SEMANTIC_TOP_K", "5")),
            max_concurrent_jobs=int(os.getenv("HSMT_MAX_CONCURRENT_JOBS", "2")),
            job_retention_hours=int(os.getenv("HSMT_JOB_RETENTION_HOURS", "24")),
            runtime_root=Path(os.getenv("HSMT_RUNTIME_ROOT", "runtime/jobs")),
        )
