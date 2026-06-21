from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Iterable, Optional

from .anomaly import enrich_consensus_anomalies
from .comparison import build_bidder_rows, make_result
from .config import EnterpriseConfig
from .excel_reader import file_sha256, load_workbook_items
from .matcher import match_items
from .models import ComparisonResult, DocumentRole, ItemRecord, WorkbookData
from .reporter import export_comparison_report


def compare_tender_files(
    hsmt_path: str | Path,
    bidder_files: Iterable[tuple[str, str | Path]],
    output_path: str | Path | None = None,
    config: Optional[EnterpriseConfig] = None,
    hsmt_sheets: Optional[list[str]] = None,
    bidder_sheets: Optional[dict[str, list[str]]] = None,
) -> ComparisonResult:
    config = config or EnterpriseConfig.from_env()
    reference = load_workbook_items(hsmt_path, DocumentRole.HSMT, bidder="HSMT", selected_sheets=hsmt_sheets, max_rows=config.max_excel_rows)
    bidders: list[WorkbookData] = []
    all_rows = []
    for bidder_name, path in bidder_files:
        wb = load_workbook_items(
            path, DocumentRole.HSDT, bidder=bidder_name,
            selected_sheets=(bidder_sheets or {}).get(bidder_name),
            max_rows=config.max_excel_rows,
        )
        bidders.append(wb)
        matches = match_items(reference.items, wb.items, config)
        all_rows.extend(build_bidder_rows(reference.items, wb.items, bidder_name, matches, config))

    enrich_consensus_anomalies(all_rows, config)
    audit = _audit(reference, bidders, config, mode="HSMT_vs_HSDT")
    result = make_result(all_rows, reference, bidders, audit)
    if output_path:
        export_comparison_report(result, output_path)
    return result


def compare_bidder_files(
    bidder_files: Iterable[tuple[str, str | Path]],
    output_path: str | Path | None = None,
    config: Optional[EnterpriseConfig] = None,
) -> ComparisonResult:
    """Compare multiple HSDTs without HSMT.

    A union catalogue is built locally, then every bidder is rematched to that final
    catalogue. This avoids losing items that only appear in later workbooks.
    """
    config = config or EnterpriseConfig.from_env()
    bidders = [
        load_workbook_items(path, DocumentRole.HSDT, bidder=name, max_rows=config.max_excel_rows)
        for name, path in bidder_files
    ]
    if len(bidders) < 2:
        raise ValueError("Cần ít nhất 2 HSDT để so sánh giữa các nhà thầu.")

    # Build a union reference from the first bidder and all later unmatched extras.
    union_items = [deepcopy(x) for x in bidders[0].items if not x.is_group]
    for wb in bidders[1:]:
        matches = match_items(union_items, wb.items, config)
        cands = [x for x in wb.items if not x.is_group]
        for m in matches:
            if m.reference_index is None and m.candidate_index is not None:
                extra = deepcopy(cands[m.candidate_index])
                extra.bidder = "DANH MỤC HỢP NHẤT"
                union_items.append(extra)

    reference = WorkbookData(
        path=Path("DANH_MUC_HOP_NHAT.xlsx"),
        role=DocumentRole.HSMT,
        bidder="Danh mục hợp nhất từ các HSDT",
        items=union_items,
        warnings=[],
        sheet_info=[],
    )

    all_rows = []
    for wb in bidders:
        matches = match_items(reference.items, wb.items, config)
        all_rows.extend(build_bidder_rows(reference.items, wb.items, wb.bidder, matches, config))
    enrich_consensus_anomalies(all_rows, config)
    audit = _audit(reference, bidders, config, mode="HSDT_vs_HSDT")
    result = make_result(all_rows, reference, bidders, audit)
    if output_path:
        export_comparison_report(result, output_path)
    return result


def _audit(reference: WorkbookData, bidders: list[WorkbookData], config: EnterpriseConfig, mode: str) -> dict:
    return {
        "mode": mode,
        "privacy": "STRICT_LOCAL" if config.strict_privacy else "LOCAL",
        "network_allowed": config.allow_network,
        "embedding_model": config.embedding_model_path or "disabled/not installed",
        "reference_sha256": file_sha256(reference.path) if reference.path.exists() else "synthetic-union",
        "bidder_sha256": {b.bidder: file_sha256(b.path) for b in bidders},
        "thresholds": {
            k: getattr(config.thresholds, k)
            for k in config.thresholds.__dataclass_fields__
        },
    }


# Backward-compatible single-pair entry point.
def run_comparison(hsmt_path, hsdt_path, output_path=None, ten_nha_thau="Nhà thầu", **kwargs):
    config = kwargs.pop("config", None) or EnterpriseConfig.from_env()
    if "fuzzy_threshold" in kwargs:
        config.thresholds.name_reject_score = float(kwargs["fuzzy_threshold"])
    return compare_tender_files(hsmt_path, [(ten_nha_thau, hsdt_path)], output_path=output_path, config=config)


def run_multi(hsmt_path, bidder_files, output_path=None, config=None):
    return compare_tender_files(hsmt_path, bidder_files, output_path=output_path, config=config)
