from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Optional

from .models import ItemRecord, Severity


@dataclass(slots=True)
class PeerFieldComparison:
    """Kết quả của một thông số trong một nhóm hạng mục ngang hàng.

    Không có giá trị chuẩn. ``min/median/max`` chỉ giúp mô tả mức phân tán.
    """

    field: str
    field_group: str
    values: dict[str, Any]
    present_bidders: list[str] = field(default_factory=list)
    missing_bidders: list[str] = field(default_factory=list)
    min_value: Optional[float] = None
    min_bidders: list[str] = field(default_factory=list)
    median_value: Optional[float] = None
    mean_abs_value: Optional[float] = None
    max_value: Optional[float] = None
    max_bidders: list[str] = field(default_factory=list)
    spread_abs: Optional[float] = None
    spread_pct: Optional[float] = None
    lowest_similarity: Optional[float] = None
    lowest_similarity_pair: tuple[str, str] | None = None
    distinct_values: list[str] = field(default_factory=list)
    bidder_deviation_pct: dict[str, Optional[float]] = field(default_factory=dict)
    severity: Severity = Severity.OK
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


@dataclass(slots=True)
class PeerItemGroup:
    """Một hạng mục chung được ghép từ 2 hoặc nhiều hồ sơ dự thầu."""

    group_id: str
    members: dict[str, ItemRecord]
    display_sheet: str = ""
    display_stt: str = ""
    display_code: str = ""
    display_name: str = ""
    display_unit: str = ""
    group_confidence: float = 0.0
    match_explanation: str = ""
    field_comparisons: list[PeerFieldComparison] = field(default_factory=list)
    severity: Severity = Severity.OK
    anomaly_score: float = 0.0
    reasons: list[str] = field(default_factory=list)

    @property
    def presence_count(self) -> int:
        return len(self.members)

    def field(self, name: str) -> PeerFieldComparison | None:
        return next((entry for entry in self.field_comparisons if entry.field == name), None)

    def to_summary_dict(self, bidders: Iterable[str]) -> dict[str, Any]:
        names = list(bidders)
        price = self.field("Đơn giá tổng hợp")
        quantity = self.field("Khối lượng")
        amount = self.field("Thành tiền")
        row: dict[str, Any] = {
            "Mức độ": self.severity.value,
            "Điểm bất thường": self.anomaly_score,
            "Mã nhóm": self.group_id,
            "Sheet/Hệ thống": self.display_sheet,
            "STT gợi ý": self.display_stt,
            "Mã hiệu gợi ý": self.display_code,
            "Tên hạng mục gợi ý": self.display_name,
            "ĐVT gợi ý": self.display_unit,
            "Số nhà thầu có hạng mục": self.presence_count,
            "Tổng số nhà thầu": len(names),
            "Độ tin cậy ghép": self.group_confidence,
            "Chênh đơn giá (%)": price.spread_pct if price else None,
            "Chênh khối lượng (%)": quantity.spread_pct if quantity else None,
            "Chênh thành tiền (%)": amount.spread_pct if amount else None,
            "Số thông số khác biệt": sum(
                1 for entry in self.field_comparisons if entry.severity is not Severity.OK
            ),
            "Lý do": " | ".join(dict.fromkeys(self.reasons)),
        }
        for bidder in names:
            item = self.members.get(bidder)
            row[f"{bidder} - Có hạng mục"] = "Có" if item else "Không"
            row[f"{bidder} - Tên"] = item.item_name if item else ""
            row[f"{bidder} - ĐVT"] = item.unit if item else ""
            row[f"{bidder} - Khối lượng"] = item.quantity if item else None
            row[f"{bidder} - Đơn giá"] = item.unit_price_total if item else None
            row[f"{bidder} - Thành tiền"] = item.amount if item else None
            row[f"{bidder} - Vật tư/Quy cách"] = item.material if item else ""
            row[f"{bidder} - Thương hiệu"] = item.brand if item else ""
            row[f"{bidder} - Xuất xứ"] = item.origin if item else ""
        return row


@dataclass(slots=True)
class PeerComparisonSummary:
    bidder_names: list[str]
    bidder_count: int
    total_groups: int
    complete_groups: int
    partial_groups: int
    groups_ok: int
    groups_info: int
    groups_review: int
    groups_warning: int
    groups_critical: int
    flagged_fields: int
    bidder_totals: dict[str, float]
    generated_at: str


@dataclass(slots=True)
class PeerComparisonResult:
    groups: list[PeerItemGroup]
    summary: PeerComparisonSummary
    warnings: list[str] = field(default_factory=list)
    audit: dict[str, Any] = field(default_factory=dict)

    def iter_flagged_fields(self) -> Iterable[tuple[PeerItemGroup, PeerFieldComparison]]:
        for group in self.groups:
            for entry in group.field_comparisons:
                if entry.severity is not Severity.OK:
                    yield group, entry
