from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np


@dataclass(slots=True)
class OCRCandidate:
    text: str
    confidence: float
    engine: str
    variant: str = ""


@dataclass(slots=True)
class OCRCell:
    page: int
    row: int
    col: int
    bbox: tuple[int, int, int, int]
    text: str = ""
    confidence: float = 0.0
    engine: str = ""
    candidates: list[OCRCandidate] = field(default_factory=list)
    field: str = ""
    numeric_value: Optional[float] = None
    status: str = "empty"
    review_reason: str = ""
    image_path: str = ""


@dataclass(slots=True)
class OCRTable:
    page: int
    bbox: tuple[int, int, int, int]
    x_lines: list[int]
    y_lines: list[int]
    cells: list[OCRCell] = field(default_factory=list)
    header_rows: int = 1
    column_fields: dict[int, str] = field(default_factory=dict)
    structure_confidence: float = 0.0
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class OCRPage:
    page: int
    image: np.ndarray
    rotation: int
    source: str
    tables: list[OCRTable] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class OCRDocument:
    source_path: Path
    pages: list[OCRPage]
    rows: list[dict]
    warnings: list[str] = field(default_factory=list)
    audit: dict = field(default_factory=dict)
