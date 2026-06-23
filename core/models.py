from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class DocumentRole(str, Enum):
    HSMT = "HSMT"
    HSDT = "HSDT"


class RowType(str, Enum):
    GROUP = "group"
    DETAIL = "detail"
    COMPONENT = "component"
    SUMMARY = "summary"


class MatchKind(str, Enum):
    EXACT_STRUCTURE = "exact_structure"
    EXACT_CODE = "exact_code"
    EXACT_NAME = "exact_name"
    ROW_NEAR = "row_near"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    RERANKED = "reranked"
    MISSING = "missing"
    EXTRA = "extra"


class Severity(str, Enum):
    OK = "OK"
    INFO = "THÔNG TIN"
    REVIEW = "CẦN KIỂM TRA"
    WARNING = "CẢNH BÁO"
    CRITICAL = "BẤT THƯỜNG"


@dataclass(slots=True)
class CompareThresholds:
    price_warn_pct: float = 0.10
    price_critical_pct: float = 0.25
    price_warn_abs: float = 100_000.0
    price_critical_abs: float = 1_000_000.0
    quantity_warn_pct: float = 0.05
    quantity_critical_pct: float = 0.15
    component_warn_pct: float = 0.10
    component_critical_pct: float = 0.25
    technical_warn_pct: float = 0.05
    name_review_score: float = 0.78
    name_reject_score: float = 0.58
    material_review_score: float = 0.72
    math_tolerance_pct: float = 0.005
    robust_z_warn: float = 2.5
    robust_z_critical: float = 3.5
    min_bidders_for_consensus: int = 3


@dataclass(slots=True)
class ItemRecord:
    source_id: str
    role: DocumentRole
    bidder: str
    workbook: str
    sheet: str
    row_number: int
    stt: str = ""
    item_code: str = ""
    item_name: str = ""
    unit: str = ""
    reference_quantity: Optional[float] = None
    bid_quantity: Optional[float] = None
    price_main: Optional[float] = None
    price_aux: Optional[float] = None
    price_labor: Optional[float] = None
    price_management: Optional[float] = None
    price_profit: Optional[float] = None
    unit_price_total: Optional[float] = None
    reference_amount: Optional[float] = None
    bid_amount: Optional[float] = None
    material: str = ""
    brand: str = ""
    origin: str = ""
    note: str = ""
    technical_specs: dict[str, Any] = field(default_factory=dict)
    section_path: tuple[str, ...] = field(default_factory=tuple)
    section_codes: tuple[str, ...] = field(default_factory=tuple)
    row_type: RowType = RowType.DETAIL
    raw: dict[str, Any] = field(default_factory=dict)
    normalized_stt: str = ""
    normalized_code: str = ""
    normalized_name: str = ""
    normalized_unit: str = ""
    normalized_path: str = ""
    structural_key: str = ""
    data_quality_flags: list[str] = field(default_factory=list)

    @property
    def is_group(self) -> bool:
        return self.row_type is RowType.GROUP

    @property
    def is_comparable(self) -> bool:
        return self.row_type in {RowType.DETAIL, RowType.COMPONENT}

    @property
    def quantity(self) -> Optional[float]:
        if self.role is DocumentRole.HSDT:
            return self.bid_quantity if self.bid_quantity is not None else self.reference_quantity
        return self.reference_quantity if self.reference_quantity is not None else self.bid_quantity

    @property
    def amount(self) -> Optional[float]:
        if self.role is DocumentRole.HSDT:
            return self.bid_amount if self.bid_amount is not None else self.reference_amount
        return self.reference_amount if self.reference_amount is not None else self.bid_amount

    @property
    def price_components(self) -> dict[str, Optional[float]]:
        return {
            "VL chính": self.price_main,
            "VL phụ": self.price_aux,
            "NC&M": self.price_labor,
            "CF quản lý": self.price_management,
            "Lợi nhuận": self.price_profit,
        }

    @property
    def display_key(self) -> str:
        return self.stt.strip() or self.item_code.strip() or self.item_name.strip() or f"{self.sheet}!{self.row_number}"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["role"] = self.role.value
        data["row_type"] = self.row_type.value
        return data


@dataclass(slots=True)
class WorkbookData:
    path: Path
    role: DocumentRole
    bidder: str
    items: list[ItemRecord]
    warnings: list[str] = field(default_factory=list)
    sheet_info: list[dict[str, Any]] = field(default_factory=list)
    totals: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class MatchResult:
    reference_index: Optional[int]
    candidate_index: Optional[int]
    kind: MatchKind
    score: float
    structure_score: float = 0.0
    code_score: float = 0.0
    lexical_score: float = 0.0
    semantic_score: float = 0.0
    reranker_score: float = 0.0
    unit_score: float = 0.0
    row_distance: Optional[int] = None
    reason: str = ""
