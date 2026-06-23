from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import combinations
from statistics import median
from typing import Any, Callable, Iterable, Optional

from rapidfuzz import fuzz

from .config import EnterpriseConfig
from .matcher import match_items
from .models import ItemRecord, MatchKind, Severity, WorkbookData
from .number_parser import parse_number
from .peer_models import PeerComparisonResult, PeerComparisonSummary, PeerFieldComparison, PeerItemGroup
from .text_normalizer import normalize_code, normalize_name, normalize_unit

_RANK = {
    Severity.OK: 0,
    Severity.INFO: 1,
    Severity.REVIEW: 2,
    Severity.WARNING: 3,
    Severity.CRITICAL: 4,
}


def _worst(left: Severity, right: Severity) -> Severity:
    return left if _RANK[left] >= _RANK[right] else right


def _text_similarity(left: Any, right: Any) -> float:
    a, b = normalize_name(str(left or "")), normalize_name(str(right or ""))
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return (0.55 * fuzz.WRatio(a, b) + 0.45 * fuzz.token_set_ratio(a, b)) / 100.0


def _mode_text(values: Iterable[str]) -> str:
    cleaned = [str(value or "").strip() for value in values if str(value or "").strip()]
    if not cleaned:
        return ""
    counts = Counter(normalize_name(value) for value in cleaned)
    key = max(counts, key=lambda item: (counts[item], len(item)))
    return max((value for value in cleaned if normalize_name(value) == key), key=len)


def _representative(items: list[ItemRecord]) -> ItemRecord:
    """Chọn nhãn hiển thị theo medoid, không chọn hồ sơ chuẩn nghiệp vụ."""
    if len(items) == 1:
        return items[0]
    best, best_score = items[0], -1.0
    for candidate in items:
        similarities = [
            _text_similarity(candidate.item_name, other.item_name)
            for other in items if other is not candidate
        ]
        average = sum(similarities) / len(similarities) if similarities else 1.0
        completeness = sum(bool(str(value or "").strip()) for value in (
            candidate.item_code, candidate.item_name, candidate.unit,
            candidate.material, candidate.brand, candidate.origin,
        )) / 6.0
        score = 0.85 * average + 0.15 * completeness
        if score > best_score:
            best, best_score = candidate, score
    return best


@dataclass(slots=True)
class _Edge:
    left: tuple[int, int]
    right: tuple[int, int]
    score: float
    kind: MatchKind
    reason: str
    reciprocal: bool


class _UnionFind:
    def __init__(self, nodes: Iterable[tuple[int, int]]) -> None:
        self.parent = {node: node for node in nodes}
        self.rank = {node: 0 for node in nodes}
        self.bidders = {node: {node[0]} for node in nodes}

    def find(self, node: tuple[int, int]) -> tuple[int, int]:
        parent = self.parent[node]
        if parent != node:
            self.parent[node] = self.find(parent)
        return self.parent[node]

    def union_if_compatible(self, left: tuple[int, int], right: tuple[int, int]) -> bool:
        a, b = self.find(left), self.find(right)
        if a == b:
            return True
        # Một nhóm không được có hai dòng của cùng một nhà thầu.
        if self.bidders[a] & self.bidders[b]:
            return False
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        self.bidders[a] |= self.bidders[b]
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1
        return True


def _pair_edges(
    left_idx: int,
    left: WorkbookData,
    right_idx: int,
    right: WorkbookData,
    config: EnterpriseConfig,
) -> list[_Edge]:
    left_items = [item for item in left.items if item.is_comparable]
    right_items = [item for item in right.items if item.is_comparable]
    forward = match_items(left_items, right_items, config)
    reverse = match_items(right_items, left_items, config)

    forward_map = {
        (m.reference_index, m.candidate_index): m
        for m in forward
        if m.reference_index is not None and m.candidate_index is not None
    }
    reverse_map = {
        (m.candidate_index, m.reference_index): m
        for m in reverse
        if m.reference_index is not None and m.candidate_index is not None
    }

    edges: list[_Edge] = []
    for pair in set(forward_map) | set(reverse_map):
        fm, rm = forward_map.get(pair), reverse_map.get(pair)
        reciprocal = fm is not None and rm is not None
        if reciprocal:
            score = (fm.score + rm.score) / 2.0
        else:
            score = max(fm.score if fm else 0.0, rm.score if rm else 0.0) - 0.035
        chosen = fm if fm and (not rm or fm.score >= rm.score) else rm
        if chosen is None:
            continue
        # Khớp một chiều yếu không được dùng để nối nhóm.
        if not reciprocal and score < max(0.72, config.thresholds.name_reject_score + 0.08):
            continue
        edges.append(_Edge(
            left=(left_idx, int(pair[0])),
            right=(right_idx, int(pair[1])),
            score=max(0.0, min(1.0, score)),
            kind=chosen.kind,
            reason=chosen.reason,
            reciprocal=reciprocal,
        ))
    return edges


def _build_groups(workbooks: list[WorkbookData], config: EnterpriseConfig) -> list[PeerItemGroup]:
    comparable = [[item for item in workbook.items if item.is_comparable] for workbook in workbooks]
    nodes = [(bi, ii) for bi, items in enumerate(comparable) for ii in range(len(items))]
    union = _UnionFind(nodes)
    edges: list[_Edge] = []
    for left_idx, right_idx in combinations(range(len(workbooks)), 2):
        edges.extend(_pair_edges(left_idx, workbooks[left_idx], right_idx, workbooks[right_idx], config))

    for edge in sorted(edges, key=lambda item: (not item.reciprocal, -item.score)):
        union.union_if_compatible(edge.left, edge.right)

    grouped_nodes: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for node in nodes:
        grouped_nodes[union.find(node)].append(node)

    edge_lookup: dict[frozenset[tuple[int, int]], _Edge] = {
        frozenset((edge.left, edge.right)): edge for edge in edges
    }
    groups: list[PeerItemGroup] = []
    for order, members_nodes in enumerate(grouped_nodes.values(), start=1):
        members = {
            workbooks[bi].bidder: comparable[bi][ii]
            for bi, ii in members_nodes
        }
        items = list(members.values())
        rep = _representative(items)
        in_group_edges = [
            edge_lookup[frozenset((a, b))]
            for a, b in combinations(members_nodes, 2)
            if frozenset((a, b)) in edge_lookup
        ]
        confidence = (
            sum(edge.score for edge in in_group_edges) / len(in_group_edges)
            if in_group_edges else (1.0 if len(items) == 1 else 0.0)
        )
        explanations = sorted({edge.reason for edge in in_group_edges if edge.reason})
        group_id = (
            f"G{order:06d}::{normalize_name(rep.sheet)}::"
            f"{normalize_code(rep.item_code) or normalize_name(rep.item_name)}"
        )
        groups.append(PeerItemGroup(
            group_id=group_id,
            members=members,
            display_sheet=_mode_text(item.sheet for item in items),
            display_stt=_mode_text(item.stt for item in items),
            display_code=_mode_text(item.item_code for item in items),
            display_name=_mode_text(item.item_name for item in items),
            display_unit=_mode_text(item.unit for item in items),
            group_confidence=confidence,
            match_explanation="; ".join(explanations),
        ))
    groups.sort(key=lambda group: (
        normalize_name(group.display_sheet),
        min(item.row_number for item in group.members.values()),
        normalize_name(group.display_name),
    ))
    return groups


def _numeric_comparison(
    field: str,
    field_group: str,
    members: dict[str, ItemRecord],
    bidders: list[str],
    getter: Callable[[ItemRecord], Any],
    warn_pct: float,
    critical_pct: float,
    warn_abs: float = 0.0,
    critical_abs: float = 0.0,
) -> PeerFieldComparison | None:
    values: dict[str, Optional[float]] = {}
    for bidder in bidders:
        item = members.get(bidder)
        raw = getter(item) if item else None
        value = raw if isinstance(raw, (int, float)) and not isinstance(raw, bool) else parse_number(raw)
        values[bidder] = float(value) if value is not None and math.isfinite(float(value)) else None

    valid_pairs = [(bidder, value) for bidder, value in values.items() if value is not None]
    if not valid_pairs:
        return None
    valid = [value for _, value in valid_pairs]
    missing = [bidder for bidder, value in values.items() if value is None]
    result = PeerFieldComparison(
        field=field,
        field_group=field_group,
        values=values,
        present_bidders=[bidder for bidder, _ in valid_pairs],
        missing_bidders=missing,
    )
    result.min_value = min(valid)
    result.max_value = max(valid)
    result.median_value = median(valid)
    result.mean_abs_value = sum(abs(value) for value in valid) / len(valid)
    result.min_bidders = [bidder for bidder, value in valid_pairs if value == result.min_value]
    result.max_bidders = [bidder for bidder, value in valid_pairs if value == result.max_value]
    result.spread_abs = result.max_value - result.min_value
    if result.mean_abs_value > 1e-12:
        result.spread_pct = abs(result.spread_abs) / result.mean_abs_value
    elif result.spread_abs == 0:
        result.spread_pct = 0.0
    for bidder, value in values.items():
        result.bidder_deviation_pct[bidder] = (
            None if value is None or result.mean_abs_value <= 1e-12
            else (value - result.median_value) / result.mean_abs_value
        )

    reasons: list[str] = []
    if missing:
        result.severity = Severity.REVIEW
        reasons.append("Thiếu giá trị ở: " + ", ".join(missing))
    if len(valid) >= 2 and result.spread_abs > 0:
        pct = result.spread_pct
        critical = pct is not None and pct >= critical_pct and result.spread_abs >= critical_abs
        warning = pct is not None and pct >= warn_pct and result.spread_abs >= warn_abs
        result.severity = _worst(
            result.severity,
            Severity.CRITICAL if critical else Severity.WARNING if warning else Severity.INFO,
        )
        pct_text = f"{pct:.2%}" if pct is not None else "không xác định"
        reasons.append(
            f"{field} chênh {pct_text}: thấp nhất {', '.join(result.min_bidders)} = "
            f"{result.min_value:,.3f}; cao nhất {', '.join(result.max_bidders)} = "
            f"{result.max_value:,.3f}; chênh tuyệt đối = {result.spread_abs:,.3f}."
        )
    result.reason = "; ".join(reasons)
    return result


def _text_comparison(
    field: str,
    field_group: str,
    members: dict[str, ItemRecord],
    bidders: list[str],
    getter: Callable[[ItemRecord], Any],
    review_score: float,
    warning_score: float,
) -> PeerFieldComparison | None:
    values = {
        bidder: str(getter(members[bidder]) or "").strip() if bidder in members else ""
        for bidder in bidders
    }
    nonempty = [(bidder, value) for bidder, value in values.items() if value]
    if not nonempty:
        return None
    missing = [bidder for bidder, value in values.items() if not value]
    result = PeerFieldComparison(
        field=field,
        field_group=field_group,
        values=values,
        present_bidders=[bidder for bidder, _ in nonempty],
        missing_bidders=missing,
    )
    normalizer = normalize_code if field == "Mã hiệu" else (
        normalize_unit if field == "Đơn vị tính" else normalize_name
    )
    unique: dict[str, str] = {}
    for _, value in nonempty:
        unique.setdefault(normalizer(value), value)
    result.distinct_values = list(unique.values())

    lowest = 1.0
    lowest_pair: tuple[str, str] | None = None
    for (bidder_a, value_a), (bidder_b, value_b) in combinations(nonempty, 2):
        if field == "Mã hiệu":
            a, b = normalize_code(value_a), normalize_code(value_b)
            score = 1.0 if a and a == b else fuzz.ratio(a, b) / 100.0
        elif field == "Đơn vị tính":
            a, b = normalize_unit(value_a), normalize_unit(value_b)
            score = 1.0 if a and a == b else fuzz.ratio(a, b) / 100.0
        else:
            score = _text_similarity(value_a, value_b)
        if score < lowest:
            lowest, lowest_pair = score, (bidder_a, bidder_b)
    result.lowest_similarity = lowest if len(nonempty) >= 2 else None
    result.lowest_similarity_pair = lowest_pair

    reasons: list[str] = []
    if missing:
        result.severity = Severity.REVIEW
        reasons.append("Không có thông tin ở: " + ", ".join(missing))
    if len(result.distinct_values) > 1 and result.lowest_similarity is not None:
        if result.lowest_similarity < warning_score:
            result.severity = _worst(result.severity, Severity.WARNING)
        elif result.lowest_similarity < review_score:
            result.severity = _worst(result.severity, Severity.REVIEW)
        else:
            result.severity = _worst(result.severity, Severity.INFO)
        pair = " và ".join(result.lowest_similarity_pair or ())
        reasons.append(
            f"{field} có cách ghi khác nhau; độ giống nhau thấp nhất "
            f"{result.lowest_similarity:.1%}" + (f" giữa {pair}." if pair else ".")
        )
    result.reason = "; ".join(reasons)
    return result


def _technical_comparisons(
    members: dict[str, ItemRecord], bidders: list[str]
) -> list[PeerFieldComparison]:
    labels: dict[str, str] = {}
    specs: dict[str, dict[str, Any]] = {}
    for bidder, item in members.items():
        current: dict[str, Any] = {}
        for label, value in item.technical_specs.items():
            key = normalize_name(label)
            if key:
                labels.setdefault(key, label)
                current[key] = value
        specs[bidder] = current

    output: list[PeerFieldComparison] = []
    for key, label in sorted(labels.items()):
        raw_values = {bidder: specs.get(bidder, {}).get(key) for bidder in bidders}
        present = [value for value in raw_values.values() if value not in (None, "")]
        numeric = present and all(parse_number(value) is not None for value in present)
        getter = lambda item, k=key: next(
            (value for name, value in item.technical_specs.items() if normalize_name(name) == k),
            None,
        )
        if numeric:
            entry = _numeric_comparison(
                f"Thông số: {label}", "Thông số kỹ thuật", members, bidders,
                getter, 0.05, 0.15,
            )
        else:
            entry = _text_comparison(
                f"Thông số: {label}", "Thông số kỹ thuật", members, bidders,
                getter, 0.90, 0.65,
            )
        if entry:
            output.append(entry)
    return output


def _apply(group: PeerItemGroup, entry: PeerFieldComparison | None, weight: float) -> None:
    if entry is None:
        return
    group.field_comparisons.append(entry)
    if entry.severity is Severity.OK:
        return
    group.severity = _worst(group.severity, entry.severity)
    if entry.reason:
        group.reasons.append(entry.reason)
    multiplier = {
        Severity.INFO: 0.10,
        Severity.REVIEW: 0.45,
        Severity.WARNING: 0.75,
        Severity.CRITICAL: 1.0,
    }[entry.severity]
    group.anomaly_score = min(100.0, group.anomaly_score + weight * multiplier)


def _evaluate_group(group: PeerItemGroup, bidders: list[str], config: EnterpriseConfig) -> None:
    thresholds = config.thresholds
    members = group.members
    missing_items = [bidder for bidder in bidders if bidder not in members]
    if missing_items:
        severity = Severity.CRITICAL if len(members) == 1 else Severity.WARNING
        reason = (
            f"Hạng mục chỉ xuất hiện ở {', '.join(members)}; không tìm thấy ở "
            f"{', '.join(missing_items)}."
        )
        _apply(group, PeerFieldComparison(
            field="Sự hiện diện hạng mục",
            field_group="Danh mục",
            values={bidder: "Có" if bidder in members else "Không" for bidder in bidders},
            present_bidders=list(members),
            missing_bidders=missing_items,
            severity=severity,
            reason=reason,
        ), 30.0)

    # Giá, khối lượng và thành tiền.
    _apply(group, _numeric_comparison(
        "Khối lượng", "Giá và số lượng", members, bidders,
        lambda item: item.quantity,
        thresholds.quantity_warn_pct, thresholds.quantity_critical_pct,
    ), 18.0)
    _apply(group, _numeric_comparison(
        "Đơn giá tổng hợp", "Giá và số lượng", members, bidders,
        lambda item: item.unit_price_total,
        thresholds.price_warn_pct, thresholds.price_critical_pct,
        thresholds.price_warn_abs, thresholds.price_critical_abs,
    ), 25.0)
    _apply(group, _numeric_comparison(
        "Thành tiền", "Giá và số lượng", members, bidders,
        lambda item: item.amount,
        thresholds.price_warn_pct, thresholds.price_critical_pct,
        thresholds.price_warn_abs, thresholds.price_critical_abs,
    ), 22.0)

    component_getters = [
        ("VL chính", lambda item: item.price_main),
        ("VL phụ", lambda item: item.price_aux),
        ("NC&M", lambda item: item.price_labor),
        ("CF quản lý", lambda item: item.price_management),
        ("Lợi nhuận", lambda item: item.price_profit),
    ]
    for label, getter in component_getters:
        _apply(group, _numeric_comparison(
            f"Thành phần giá: {label}", "Thành phần giá", members, bidders,
            getter, thresholds.component_warn_pct, thresholds.component_critical_pct,
            thresholds.price_warn_abs / 5, thresholds.price_critical_abs / 5,
        ), 8.0)

    # Tên và thông số chữ.
    for field, getter, review, warning, weight in [
        ("Mã hiệu", lambda item: item.item_code, 0.95, 0.70, 8.0),
        ("Tên hạng mục", lambda item: item.item_name, thresholds.name_review_score, thresholds.name_reject_score, 20.0),
        ("Đơn vị tính", lambda item: item.unit, 0.98, 0.80, 12.0),
        ("Vật tư/Quy cách", lambda item: item.material, 0.85, thresholds.material_review_score, 15.0),
        ("Thương hiệu", lambda item: item.brand, 0.90, 0.70, 12.0),
        ("Xuất xứ", lambda item: item.origin, 0.90, 0.70, 10.0),
    ]:
        _apply(group, _text_comparison(field, "Tên và thông số", members, bidders, getter, review, warning), weight)

    for entry in _technical_comparisons(members, bidders):
        _apply(group, entry, 8.0)

    # Chất lượng dữ liệu file gốc.
    quality_values = {
        bidder: " | ".join(item.data_quality_flags) if item else ""
        for bidder, item in ((bidder, members.get(bidder)) for bidder in bidders)
    }
    if any(quality_values.values()):
        _apply(group, PeerFieldComparison(
            field="Chất lượng dữ liệu",
            field_group="Chất lượng file",
            values=quality_values,
            present_bidders=[bidder for bidder, value in quality_values.items() if value],
            severity=Severity.REVIEW,
            reason="File nguồn có cảnh báo dữ liệu; xem sheet Chất lượng dữ liệu.",
        ), 10.0)


def compare_workbooks_as_peers(
    workbooks: list[WorkbookData], config: EnterpriseConfig
) -> PeerComparisonResult:
    if len(workbooks) < 2:
        raise ValueError("Cần ít nhất 2 hồ sơ dự thầu để so sánh ngang hàng")
    bidder_names = [workbook.bidder for workbook in workbooks]
    if len(set(bidder_names)) != len(bidder_names):
        raise ValueError("Tên nhà thầu phải khác nhau")

    groups = _build_groups(workbooks, config)
    for group in groups:
        _evaluate_group(group, bidder_names, config)

    counts = Counter(group.severity for group in groups)
    summary = PeerComparisonSummary(
        bidder_names=bidder_names,
        bidder_count=len(bidder_names),
        total_groups=len(groups),
        complete_groups=sum(group.presence_count == len(bidder_names) for group in groups),
        partial_groups=sum(group.presence_count < len(bidder_names) for group in groups),
        groups_ok=counts[Severity.OK],
        groups_info=counts[Severity.INFO],
        groups_review=counts[Severity.REVIEW],
        groups_warning=counts[Severity.WARNING],
        groups_critical=counts[Severity.CRITICAL],
        flagged_fields=sum(
            entry.severity is not Severity.OK
            for group in groups for entry in group.field_comparisons
        ),
        bidder_totals={
            workbook.bidder: sum(
                item.amount or 0.0 for item in workbook.items if item.is_comparable
            )
            for workbook in workbooks
        },
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    warnings = [warning for workbook in workbooks for warning in workbook.warnings]
    return PeerComparisonResult(groups=groups, summary=summary, warnings=warnings)
