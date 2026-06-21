from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Optional


class DocumentRole(str, Enum):
    HSMT = "HSMT"
    HSDT = "HSDT"


class MatchKind(str, Enum):
    EXACT_CODE = "exact_code"
    EXACT_NAME = "exact_name"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    MISSING = "missing"
    EXTRA = "extra"
    GROUP = "group"


class Severity(str, Enum):
    OK = "OK"
    INFO = "THÔNG TIN"
    REVIEW = "CẦN KIỂM TRA"
    WARNING = "CẢNH BÁO"
    CRITICAL = "BẤT THƯỜNG"


@dataclass(slots=True)
class CompareThresholds:
    price_warn_pct: float = 0.10
    price_critical_pct: float = 0.20
    quantity_warn_pct: float = 0.05
    quantity_critical_pct: float = 0.15
    name_review_score: float = 0.78
    name_reject_score: float = 0.55
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
    item_code: str = ""
    item_name: str = ""
    unit: str = ""
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    material: str = ""
    brand: str = ""
    origin: str = ""
    note: str = ""
    parent_group: str = ""
    is_group: bool = False
    raw: dict[str, Any] = field(default_factory=dict)
    normalized_code: str = ""
    normalized_name: str = ""
    normalized_unit: str = ""
    data_quality_flags: list[str] = field(default_factory=list)

    @property
    def display_key(self) -> str:
        return self.item_code.strip() or self.item_name.strip() or f"{self.sheet}!{self.row_number}"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["role"] = self.role.value
        return d


@dataclass(slots=True)
class WorkbookData:
    path: Path
    role: DocumentRole
    bidder: str
    items: list[ItemRecord]
    warnings: list[str] = field(default_factory=list)
    sheet_info: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class MatchResult:
    reference_index: Optional[int]
    candidate_index: Optional[int]
    kind: MatchKind
    score: float
    code_score: float = 0.0
    lexical_score: float = 0.0
    semantic_score: float = 0.0
    unit_score: float = 0.0
    reason: str = ""


@dataclass(slots=True)
class ComparedItem:
    canonical_id: str
    bidder: str
    reference: Optional[ItemRecord]
    candidate: Optional[ItemRecord]
    match: MatchResult
    quantity_delta: Optional[float] = None
    quantity_delta_pct: Optional[float] = None
    price_delta: Optional[float] = None
    price_delta_pct: Optional[float] = None
    amount_delta: Optional[float] = None
    consensus_price: Optional[float] = None
    consensus_mad: Optional[float] = None
    robust_z: Optional[float] = None
    anomaly_score: float = 0.0
    severity: Severity = Severity.OK
    flags: list[str] = field(default_factory=list)

    def to_flat_dict(self) -> dict[str, Any]:
        r, c = self.reference, self.candidate
        return {
            "Mã chuẩn": self.canonical_id,
            "Nhà thầu": self.bidder,
            "Sheet HSMT/chuẩn": r.sheet if r else "",
            "Dòng HSMT/chuẩn": r.row_number if r else None,
            "Mã HSMT/chuẩn": r.item_code if r else "",
            "Tên HSMT/chuẩn": r.item_name if r else "",
            "ĐVT HSMT/chuẩn": r.unit if r else "",
            "KL HSMT/chuẩn": r.quantity if r else None,
            "Đơn giá HSMT/chuẩn": r.unit_price if r else None,
            "Thành tiền HSMT/chuẩn": r.amount if r else None,
            "Sheet HSDT": c.sheet if c else "",
            "Dòng HSDT": c.row_number if c else None,
            "Mã HSDT": c.item_code if c else "",
            "Tên HSDT": c.item_name if c else "",
            "ĐVT HSDT": c.unit if c else "",
            "KL HSDT": c.quantity if c else None,
            "Đơn giá HSDT": c.unit_price if c else None,
            "Thành tiền HSDT": c.amount if c else None,
            "Vật tư/Quy cách": c.material if c else "",
            "Thương hiệu": c.brand if c else "",
            "Xuất xứ": c.origin if c else "",
            "Kiểu khớp": self.match.kind.value,
            "Điểm khớp": self.match.score,
            "Điểm từ vựng": self.match.lexical_score,
            "Điểm ngữ nghĩa": self.match.semantic_score,
            "Lệch KL": self.quantity_delta,
            "Lệch KL (%)": self.quantity_delta_pct,
            "Lệch đơn giá": self.price_delta,
            "Lệch đơn giá (%)": self.price_delta_pct,
            "Lệch thành tiền": self.amount_delta,
            "Trung vị giá các HSDT": self.consensus_price,
            "Robust Z": self.robust_z,
            "Điểm bất thường": self.anomaly_score,
            "Mức độ": self.severity.value,
            "Cờ đánh giá": " | ".join(self.flags),
        }


@dataclass(slots=True)
class ComparisonSummary:
    reference_name: str
    bidder_count: int
    total_reference_items: int
    total_rows: int
    exact_matches: int
    fuzzy_matches: int
    missing_items: int
    extra_items: int
    warning_rows: int
    critical_rows: int
    total_reference_amount: float
    bidder_totals: dict[str, float]
    generated_at: str


@dataclass(slots=True)
class ComparisonResult:
    rows: list[ComparedItem]
    summary: ComparisonSummary
    warnings: list[str] = field(default_factory=list)
    audit: dict[str, Any] = field(default_factory=dict)

    def iter_flat(self) -> Iterable[dict[str, Any]]:
        for row in self.rows:
            yield row.to_flat_dict()
