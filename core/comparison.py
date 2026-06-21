from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from .config import EnterpriseConfig
from .models import (
    ComparedItem, ComparisonResult, ComparisonSummary, ItemRecord,
    MatchKind, MatchResult, Severity, WorkbookData,
)
from .number_parser import math_error, percent_delta
from .text_normalizer import canonical_id


def _worst(a: Severity, b: Severity) -> Severity:
    rank = {Severity.OK: 0, Severity.INFO: 1, Severity.REVIEW: 2, Severity.WARNING: 3, Severity.CRITICAL: 4}
    return a if rank[a] >= rank[b] else b


def _safe_delta(a: Optional[float], b: Optional[float]) -> Optional[float]:
    return b - a if a is not None and b is not None else None


def build_bidder_rows(
    reference_items: list[ItemRecord],
    bidder_items: list[ItemRecord],
    bidder_name: str,
    matches: list[MatchResult],
    config: EnterpriseConfig,
) -> list[ComparedItem]:
    refs = [x for x in reference_items if not x.is_group]
    cands = [x for x in bidder_items if not x.is_group]
    t = config.thresholds
    output: list[ComparedItem] = []

    for m in matches:
        ref = refs[m.reference_index] if m.reference_index is not None else None
        cand = cands[m.candidate_index] if m.candidate_index is not None else None
        anchor = ref or cand
        assert anchor is not None
        cid = canonical_id(anchor.sheet, anchor.item_code, anchor.item_name, anchor.row_number)
        flags: list[str] = []
        severity = Severity.OK
        score = 0.0

        if m.kind is MatchKind.MISSING:
            flags.append("Thiếu hạng mục trong hồ sơ nhà thầu")
            severity = Severity.CRITICAL
            score += 45
        elif m.kind is MatchKind.EXTRA:
            flags.append("Hạng mục ngoài danh mục chuẩn/HSMT")
            severity = Severity.WARNING
            score += 30
        elif m.kind is MatchKind.EXACT_CODE and m.lexical_score < t.name_review_score:
            # A matching code must not hide a substantially different description.
            flags.append(f"Trùng mã nhưng tên hạng mục khác đáng kể ({m.lexical_score:.1%})")
            severity = _worst(
                severity,
                Severity.CRITICAL if m.lexical_score < t.name_reject_score else Severity.WARNING,
            )
            score += 32 if m.lexical_score < t.name_reject_score else 20
        elif m.score < t.name_review_score:
            flags.append(f"Tên hạng mục khớp thấp ({m.score:.1%})")
            severity = _worst(severity, Severity.REVIEW)
            score += min(30, (t.name_review_score - m.score) * 100)

        q_delta = _safe_delta(ref.quantity if ref else None, cand.quantity if cand else None)
        q_pct = percent_delta(ref.quantity if ref else None, cand.quantity if cand else None)
        p_delta = _safe_delta(ref.unit_price if ref else None, cand.unit_price if cand else None)
        p_pct = percent_delta(ref.unit_price if ref else None, cand.unit_price if cand else None)
        a_delta = _safe_delta(ref.amount if ref else None, cand.amount if cand else None)

        if ref and cand:
            if ref.sheet.casefold() != cand.sheet.casefold():
                flags.append(f"Khớp khác sheet/hệ thống: {ref.sheet} ↔ {cand.sheet}")
                severity = _worst(severity, Severity.REVIEW)
                score += 8

            if ref.normalized_unit and cand.normalized_unit and ref.normalized_unit != cand.normalized_unit:
                flags.append(f"Khác đơn vị tính: {ref.unit} ↔ {cand.unit}")
                severity = _worst(severity, Severity.WARNING)
                score += 18

            if q_pct is None and (ref.quantity is None or cand.quantity is None):
                flags.append("Thiếu dữ liệu khối lượng")
                severity = _worst(severity, Severity.REVIEW)
                score += 14
            elif q_pct is not None:
                if abs(q_pct) >= t.quantity_critical_pct:
                    flags.append(f"Khối lượng lệch {q_pct:+.1%}")
                    severity = _worst(severity, Severity.CRITICAL)
                    score += 28
                elif abs(q_pct) >= t.quantity_warn_pct:
                    flags.append(f"Khối lượng lệch {q_pct:+.1%}")
                    severity = _worst(severity, Severity.WARNING)
                    score += 15

            if p_pct is None and (ref.unit_price is None or cand.unit_price is None):
                flags.append("Thiếu dữ liệu đơn giá")
                severity = _worst(severity, Severity.REVIEW)
                score += 18
            elif p_pct is not None:
                if abs(p_pct) >= t.price_critical_pct:
                    flags.append(f"Đơn giá lệch {p_pct:+.1%}")
                    severity = _worst(severity, Severity.CRITICAL)
                    score += 35
                elif abs(p_pct) >= t.price_warn_pct:
                    flags.append(f"Đơn giá lệch {p_pct:+.1%}")
                    severity = _worst(severity, Severity.WARNING)
                    score += 20

        for item, label in ((ref, "HSMT/chuẩn"), (cand, "HSDT")):
            if item:
                if item.data_quality_flags:
                    flags.extend(f"{label}: {x}" for x in item.data_quality_flags)
                    severity = _worst(severity, Severity.REVIEW)
                    score += min(20, len(item.data_quality_flags) * 6)
                err = math_error(item.quantity, item.unit_price, item.amount, t.math_tolerance_pct)
                if err is not None:
                    flags.append(f"{label}: sai KL×ĐG, lệch {err:,.0f}")
                    severity = _worst(severity, Severity.CRITICAL)
                    score += 30

        output.append(ComparedItem(
            canonical_id=cid,
            bidder=bidder_name,
            reference=ref,
            candidate=cand,
            match=m,
            quantity_delta=q_delta,
            quantity_delta_pct=q_pct,
            price_delta=p_delta,
            price_delta_pct=p_pct,
            amount_delta=a_delta,
            anomaly_score=min(100.0, score),
            severity=severity,
            flags=list(dict.fromkeys(flags)),
        ))
    return output


def summarize(rows: list[ComparedItem], reference: WorkbookData, bidders: list[WorkbookData]) -> ComparisonSummary:
    bidder_totals: dict[str, float] = defaultdict(float)
    for row in rows:
        if row.candidate and row.candidate.amount is not None:
            bidder_totals[row.bidder] += row.candidate.amount
    refs = [x for x in reference.items if not x.is_group]
    return ComparisonSummary(
        reference_name=reference.bidder or reference.path.stem,
        bidder_count=len(bidders),
        total_reference_items=len(refs),
        total_rows=len(rows),
        exact_matches=sum(r.match.kind in {MatchKind.EXACT_CODE, MatchKind.EXACT_NAME} for r in rows),
        fuzzy_matches=sum(r.match.kind in {MatchKind.FUZZY, MatchKind.SEMANTIC} for r in rows),
        missing_items=sum(r.match.kind is MatchKind.MISSING for r in rows),
        extra_items=sum(r.match.kind is MatchKind.EXTRA for r in rows),
        warning_rows=sum(r.severity is Severity.WARNING for r in rows),
        critical_rows=sum(r.severity is Severity.CRITICAL for r in rows),
        total_reference_amount=sum(x.amount or 0.0 for x in refs),
        bidder_totals=dict(bidder_totals),
        generated_at=datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    )


def make_result(rows: list[ComparedItem], reference: WorkbookData, bidders: list[WorkbookData], audit: dict) -> ComparisonResult:
    warnings = list(reference.warnings)
    for b in bidders:
        warnings.extend(f"{b.bidder}: {w}" for w in b.warnings)
    return ComparisonResult(rows=rows, summary=summarize(rows, reference, bidders), warnings=warnings, audit=audit)
