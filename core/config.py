from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .models import CompareThresholds


@dataclass(slots=True)
class EnterpriseConfig:
    thresholds: CompareThresholds = field(default_factory=CompareThresholds)
    strict_privacy: bool = True
    allow_network: bool = False
    model_root: Path = Path("models")
    embedding_model_path: str = ""
    enable_semantic_matching: bool = True
    semantic_batch_size: int = 64
    max_excel_rows: int = 1_000_000
    max_pdf_pages: int = 500
    max_upload_mb: int = 2048
    fuzzy_top_k: int = 8
    report_constant_memory: bool = True
    random_state: int = 42

    @classmethod
    def from_env(cls) -> "EnterpriseConfig":
        strict = os.getenv("HSMT_STRICT_PRIVACY", "1") != "0"
        allow_network = os.getenv("HSMT_ALLOW_NETWORK", "0") == "1"
        model_root = Path(os.getenv("HSMT_MODEL_ROOT", "models"))
        embedding = os.getenv("HSMT_EMBEDDING_MODEL", "")
        return cls(
            strict_privacy=strict,
            allow_network=allow_network,
            model_root=model_root,
            embedding_model_path=embedding,
            enable_semantic_matching=os.getenv("HSMT_ENABLE_EMBEDDINGS", "1") != "0",
            semantic_batch_size=int(os.getenv("HSMT_EMBED_BATCH", "64")),
            max_pdf_pages=int(os.getenv("HSMT_MAX_PDF_PAGES", "500")),
            max_upload_mb=int(os.getenv("HSMT_MAX_UPLOAD_MB", "2048")),
        )
