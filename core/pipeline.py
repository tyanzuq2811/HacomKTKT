from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from .config import EnterpriseConfig
from .excel_reader import file_sha256, load_workbook_items
from .models import DocumentRole, WorkbookData
from .peer_comparison import compare_workbooks_as_peers
from .peer_models import PeerComparisonResult
from .peer_reporter import export_peer_comparison_report


def compare_bidder_files(
    bidder_files: Iterable[tuple[str, str | Path]],
    output_path: str | Path | None = None,
    config: Optional[EnterpriseConfig] = None,
    bidder_sheets: Optional[dict[str, list[str]]] = None,
) -> PeerComparisonResult:
    """So sánh ngang hàng từ 2 HSDT trở lên.

    Mỗi cặp nhà thầu được ghép theo cả hai chiều. Các kết quả được hợp nhất
    thành nhóm hạng mục one-to-one, sau đó mọi giá trị được so sánh cùng lúc.
    Thứ tự file đầu vào không tạo ra nhà thầu chuẩn.
    """
    config = config or EnterpriseConfig.from_env()
    pairs = [(name.strip(), Path(path)) for name, path in bidder_files]
    if len(pairs) < 2:
        raise ValueError("Cần ít nhất 2 HSDT để so sánh ngang hàng")
    if len({name for name, _ in pairs}) != len(pairs):
        raise ValueError("Tên nhà thầu phải khác nhau")

    workbooks: list[WorkbookData] = [
        load_workbook_items(
            path,
            DocumentRole.HSDT,
            bidder=name,
            selected_sheets=(bidder_sheets or {}).get(name),
            max_rows=config.max_excel_rows,
        )
        for name, path in pairs
    ]
    result = compare_workbooks_as_peers(workbooks, config)
    result.audit = _peer_audit(workbooks, config)
    if output_path:
        export_peer_comparison_report(result, output_path)
    return result


def _peer_audit(workbooks: list[WorkbookData], config: EnterpriseConfig) -> dict:
    return {
        "mode": "HSDT_PEER_TO_PEER_NO_BASELINE",
        "comparison_principle": "Mọi nhà thầu ngang hàng; thứ tự tải file không ảnh hưởng phép tính",
        "privacy": "STRICT_LOCAL" if config.strict_privacy else "LOCAL",
        "network_allowed": config.allow_network,
        "embedding_model": config.embedding_model_path or "disabled/not installed",
        "reranker_model": config.reranker_model_path or "disabled/not installed",
        "bidder_sha256": {
            workbook.bidder: file_sha256(workbook.path) if workbook.path.exists() else ""
            for workbook in workbooks
        },
        "sheet_mappings": {workbook.bidder: workbook.sheet_info for workbook in workbooks},
        "thresholds": {
            name: getattr(config.thresholds, name)
            for name in config.thresholds.__dataclass_fields__
        },
        "spread_formula": "(max - min) / mean(abs(values))",
    }
