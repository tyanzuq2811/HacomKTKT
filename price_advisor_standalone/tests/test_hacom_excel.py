from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from price_advisor.hacom_excel import extract_hacom_references_from_workbook


def test_extract_standard_hacom_quote_sheet(tmp_path: Path) -> None:
    path = tmp_path / "1. Chao gia ME Hacom Mall Linh Anh V2.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "1. HT điện"
    ws.append(["Dự án: HACOM"])
    ws.append(["Gói thầu"])
    ws.append(["Hạng mục"])
    ws.append(["KHỐI LƯỢNG MỜI THẦU", None, None, None, None, "LINH ANH"])
    ws.append([])
    ws.append([
        "STT",
        "Diễn giải",
        "Đơn vị",
        "KL\nMời thầu\nLần 2",
        "Ghi chú",
        "KL\nNhà thầu\nchào",
        "THÔNG TIN VỀ VẬT LIỆU CHÍNH",
        None,
        None,
        None,
        "ĐƠN GIÁ",
        None,
        None,
        None,
        None,
        None,
        "Thành tiền\nBOQ",
    ])
    ws.append(["", "", "", "", "", "", "Mô tả/ Quy cách", "Mã hiệu", "Thương hiệu", "Xuất xứ", "VL chính"])
    ws.append(["A", "ĐẦU MỤC CÔNG VIỆC THEO KLMT"])
    ws.append(["1.1", "Cáp đồng XLPE/PVC 4x25mm2", "m", 100, "", 100, "Cadivi 4x25", "CV-425", "Cadivi", "VN", 90_000, 1_000, 2_000, 3_000, 4_000, 100_000, 10_000_000])
    wb.save(path)

    refs = extract_hacom_references_from_workbook(path)

    assert len(refs) == 1
    assert refs[0].price == 100_000
    assert refs[0].unit == "m"
    assert refs[0].metadata["bidder"] == "Linh Anh"
    assert refs[0].metadata["brand"] == "Cadivi"

