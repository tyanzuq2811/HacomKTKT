from pathlib import Path

from core.config import EnterpriseConfig
from core.models import DocumentRole, ItemRecord, RowType, Severity, WorkbookData
from core.peer_comparison import compare_workbooks_as_peers
from core.peer_reporter import export_peer_comparison_report


def _item(bidder: str, price: float, quantity: float = 2.0) -> ItemRecord:
    return ItemRecord(
        source_id=f"{bidder}-1",
        role=DocumentRole.HSDT,
        bidder=bidder,
        workbook=f"{bidder}.xlsx",
        sheet="Điện",
        row_number=10,
        stt="1",
        item_code="CB-01",
        item_name="Tủ điện tổng MSB",
        unit="Tủ",
        bid_quantity=quantity,
        unit_price_total=price,
        bid_amount=price * quantity,
        material="Thiết bị đóng cắt Schneider",
        brand="Schneider",
        origin="Pháp",
        row_type=RowType.DETAIL,
        normalized_stt="1",
        normalized_code="cb01",
        normalized_name="tu dien tong msb",
        normalized_unit="tu",
        normalized_path="dien",
        structural_key="dien::1::cb01",
    )


def _workbook(name: str, price: float) -> WorkbookData:
    return WorkbookData(
        path=Path(f"{name}.xlsx"),
        role=DocumentRole.HSDT,
        bidder=name,
        items=[_item(name, price)],
    )


def test_peer_spread_is_symmetric_and_has_no_baseline(tmp_path):
    config = EnterpriseConfig()
    config.enable_semantic_matching = False
    config.enable_reranker = False
    forward = compare_workbooks_as_peers([
        _workbook("A", 100.0), _workbook("B", 120.0), _workbook("C", 80.0)
    ], config)
    reverse = compare_workbooks_as_peers([
        _workbook("C", 80.0), _workbook("A", 100.0), _workbook("B", 120.0)
    ], config)

    assert forward.summary.total_groups == 1
    assert reverse.summary.total_groups == 1
    price_forward = forward.groups[0].field("Đơn giá tổng hợp")
    price_reverse = reverse.groups[0].field("Đơn giá tổng hợp")
    assert price_forward is not None and price_reverse is not None
    assert round(price_forward.spread_pct or 0, 6) == 0.4
    assert round(price_reverse.spread_pct or 0, 6) == 0.4
    assert set(forward.groups[0].members) == {"A", "B", "C"}

    output = tmp_path / "peer.xlsx"
    export_peer_comparison_report(forward, output)
    assert output.exists() and output.stat().st_size > 10_000


def test_missing_item_is_described_without_reference_bidder():
    config = EnterpriseConfig()
    config.enable_semantic_matching = False
    config.enable_reranker = False
    a = _workbook("A", 100.0)
    b = WorkbookData(path=Path("B.xlsx"), role=DocumentRole.HSDT, bidder="B", items=[])
    result = compare_workbooks_as_peers([a, b], config)
    assert result.summary.partial_groups == 1
    assert result.groups[0].severity is Severity.CRITICAL
    reason = " | ".join(result.groups[0].reasons)
    assert "chỉ xuất hiện ở A" in reason
    assert "baseline" not in reason.lower()
