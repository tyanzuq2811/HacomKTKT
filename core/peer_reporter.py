from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import xlsxwriter

from .models import Severity
from .peer_models import PeerComparisonResult, PeerFieldComparison, PeerItemGroup


COLORS = {
    Severity.OK: "#DCFCE7",
    Severity.INFO: "#DBEAFE",
    Severity.REVIEW: "#FEF3C7",
    Severity.WARNING: "#FFEDD5",
    Severity.CRITICAL: "#FEE2E2",
}
FONT_COLORS = {
    Severity.OK: "#166534",
    Severity.INFO: "#1D4ED8",
    Severity.REVIEW: "#92400E",
    Severity.WARNING: "#C2410C",
    Severity.CRITICAL: "#B91C1C",
}


def _formats(workbook: xlsxwriter.Workbook) -> dict[str, Any]:
    return {
        "title": workbook.add_format({"bold": True, "font_size": 17, "font_color": "#FFFFFF", "bg_color": "#16324F", "valign": "vcenter"}),
        "subtitle": workbook.add_format({"italic": True, "font_color": "#16324F", "bg_color": "#EAF2FF", "text_wrap": True, "valign": "vcenter"}),
        "section": workbook.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": "#16324F", "align": "center", "valign": "vcenter", "text_wrap": True, "border": 1}),
        "header": workbook.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": "#16324F", "align": "center", "valign": "vcenter", "text_wrap": True, "border": 1}),
        "text": workbook.add_format({"valign": "top", "border": 1, "border_color": "#E2E8F0"}),
        "wrap": workbook.add_format({"valign": "top", "text_wrap": True, "border": 1, "border_color": "#E2E8F0"}),
        "num": workbook.add_format({"num_format": "#,##0.000", "valign": "top", "border": 1, "border_color": "#E2E8F0"}),
        "money": workbook.add_format({"num_format": "#,##0.00", "valign": "top", "border": 1, "border_color": "#E2E8F0"}),
        "pct": workbook.add_format({"num_format": "0.00%", "valign": "top", "border": 1, "border_color": "#E2E8F0"}),
        "score": workbook.add_format({"num_format": "0.0", "valign": "top", "border": 1, "border_color": "#E2E8F0"}),
        "note": workbook.add_format({"text_wrap": True, "valign": "top", "bg_color": "#F8FAFC", "font_color": "#334155", "border": 1}),
    }


def _severity_format(workbook: xlsxwriter.Workbook, severity: Severity):
    return workbook.add_format({
        "bold": True,
        "bg_color": COLORS[severity],
        "font_color": FONT_COLORS[severity],
        "align": "center",
        "valign": "vcenter",
        "border": 1,
    })


def _safe_text(value: Any) -> str:
    text = "" if value is None else str(value)
    if text.startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def _write_value(ws, row: int, col: int, value: Any, fmts: dict[str, Any], kind: str = "text") -> None:
    if value is None:
        ws.write_blank(row, col, None, fmts["text"])
    elif isinstance(value, bool):
        ws.write_boolean(row, col, value, fmts["text"])
    elif isinstance(value, (int, float)):
        ws.write_number(row, col, float(value), fmts.get(kind, fmts["num"]))
    else:
        ws.write(row, col, _safe_text(value), fmts.get(kind, fmts["text"]))


def _setup_sheet(ws, title: str, subtitle: str, columns: int, fmts: dict[str, Any]) -> int:
    ws.merge_range(0, 0, 0, columns - 1, title, fmts["title"])
    ws.set_row(0, 28)
    ws.merge_range(1, 0, 1, columns - 1, subtitle, fmts["subtitle"])
    ws.set_row(1, 30)
    ws.freeze_panes(4, 0)
    return 3


def _write_headers(ws, row: int, headers: list[str], fmts: dict[str, Any]) -> None:
    for col, header in enumerate(headers):
        ws.write(row, col, header, fmts["header"])
    ws.set_row(row, 32)


def _format_flag_rows(ws, first_row: int, last_row: int, last_col: int) -> None:
    if last_row < first_row:
        return
    for severity in Severity:
        if severity is Severity.OK:
            continue
        ws.conditional_format(first_row, 0, last_row, 0, {
            "type": "text",
            "criteria": "containing",
            "value": severity.value,
            "format": None,
        })
    # Row-level fills use formulas and are intentionally light to preserve readability.
    rules = [
        (Severity.CRITICAL, "#FEE2E2", "#B91C1C"),
        (Severity.WARNING, "#FFEDD5", "#C2410C"),
        (Severity.REVIEW, "#FEF3C7", "#92400E"),
        (Severity.INFO, "#DBEAFE", "#1D4ED8"),
    ]
    for severity, fill, font in rules:
        fmt = ws.book.add_format({"bg_color": fill, "font_color": font}) if hasattr(ws, "book") else None
        if fmt:
            ws.conditional_format(first_row, 0, last_row, last_col, {
                "type": "formula",
                "criteria": f'=$A{first_row + 1}="{severity.value}"',
                "format": fmt,
            })


def _values_text(entry: PeerFieldComparison, bidders: list[str]) -> str:
    chunks = []
    for bidder in bidders:
        value = entry.values.get(bidder)
        if value in (None, ""):
            rendered = "[không có]"
        elif isinstance(value, (int, float)):
            rendered = f"{value:,.3f}"
        else:
            rendered = str(value)
        chunks.append(f"{bidder}: {rendered}")
    return " | ".join(chunks)


def _write_guide(workbook, fmts, result: PeerComparisonResult) -> None:
    ws = workbook.add_worksheet("Hướng dẫn đọc")
    ws.merge_range("A1:C1", "CÁCH ĐỌC BÁO CÁO SO SÁNH NGANG HÀNG", fmts["title"])
    rows = [
        ("Không có nhà thầu chuẩn", "Tất cả hồ sơ ngang hàng", "File tải lên trước hay sau không làm thay đổi nguyên tắc tính toán."),
        ("Chênh lệch %", "Công thức đối xứng", "(Cao nhất − thấp nhất) chia cho trung bình trị tuyệt đối của tất cả giá trị đang có."),
        ("Trung vị", "Chỉ để mô tả", "Trung vị không phải giá chuẩn và không được dùng để kết luận hồ sơ nào đúng."),
        ("Tên và thông số", "So sánh nội dung", "Hệ thống kiểm tra tên, mã, đơn vị, vật tư, thương hiệu, xuất xứ và các thông số động."),
        ("Lý do", "Có thể kiểm tra lại", "Mỗi dòng nêu thông số nào khác, chênh bao nhiêu %, bên nào thấp/cao hoặc bên nào thiếu dữ liệu."),
        ("Kết luận", "Con người quyết định", "Cảnh báo chỉ hỗ trợ rà soát; không tự kết luận gian lận hoặc lựa chọn nhà thầu."),
    ]
    _write_headers(ws, 2, ["Nguyên tắc", "Ý nghĩa", "Giải thích dễ hiểu"], fmts)
    for row_idx, row in enumerate(rows, start=3):
        for col, value in enumerate(row):
            ws.write(row_idx, col, value, fmts["wrap"])
    ws.set_column("A:A", 28)
    ws.set_column("B:B", 28)
    ws.set_column("C:C", 78)


def _write_overview(workbook, fmts, result: PeerComparisonResult) -> None:
    ws = workbook.add_worksheet("Tổng quan")
    ws.merge_range("A1:H1", "BÁO CÁO SO SÁNH NGANG HÀNG GIỮA CÁC NHÀ THẦU", fmts["title"])
    ws.merge_range("A2:H2", "Không lấy nhà thầu nào làm chuẩn — mọi hồ sơ được đặt cạnh nhau để tìm chênh lệch.", fmts["subtitle"])
    ws.write_row("A4", ["THÔNG TIN", "KẾT QUẢ"], fmts["header"])
    ws.write_row("D4", ["MỨC ĐÁNH DẤU", "SỐ HẠNG MỤC"], fmts["header"])
    s = result.summary
    information = [
        ("Số nhà thầu", s.bidder_count),
        ("Danh sách", "; ".join(s.bidder_names)),
        ("Tổng nhóm hạng mục", s.total_groups),
        ("Có ở đủ nhà thầu", s.complete_groups),
        ("Thiếu ở ít nhất một nhà thầu", s.partial_groups),
        ("Thông số bị đánh dấu", s.flagged_fields),
        ("Nguyên tắc", "So sánh ngang hàng, không baseline"),
        ("Bảo mật", result.audit.get("privacy", "LOCAL")),
    ]
    levels = [
        (Severity.INFO, s.groups_info),
        (Severity.REVIEW, s.groups_review),
        (Severity.WARNING, s.groups_warning),
        (Severity.CRITICAL, s.groups_critical),
    ]
    sev_formats = {severity: _severity_format(workbook, severity) for severity in Severity}
    # Ghi tuần tự theo hàng để tương thích constant_memory.
    for offset in range(max(len(information), len(levels))):
        row = 4 + offset
        if offset < len(information):
            label, value = information[offset]
            ws.write(row, 0, label, fmts["text"])
            _write_value(ws, row, 1, value, fmts, "wrap")
        if offset < len(levels):
            severity, value = levels[offset]
            ws.write(row, 3, severity.value, sev_formats[severity])
            ws.write_number(row, 4, value, fmts["num"])
    ws.merge_range("A14:H14", "CÔNG THỨC KHÔNG THIÊN VỊ", fmts["header"])
    ws.merge_range("A15:H16", "Chênh lệch % = (giá trị cao nhất − giá trị thấp nhất) / trung bình trị tuyệt đối của các giá trị đang có. Công thức không chọn một nhà thầu làm mẫu số. Dữ liệu thiếu được báo riêng, không ép thành 0.", fmts["subtitle"])
    ws.set_column("A:A", 32)
    ws.set_column("B:B", 42)
    ws.set_column("C:C", 3)
    ws.set_column("D:D", 22)
    ws.set_column("E:E", 18)
    ws.set_column("F:H", 12)
    chart = workbook.add_chart({"type": "column"})
    chart.add_series({
        "name": "Số hạng mục",
        "categories": "='Tổng quan'!$D$5:$D$8",
        "values": "='Tổng quan'!$E$5:$E$8",
        "fill": {"color": "#1F6D8C"},
    })
    chart.set_title({"name": "Phân bố mức đánh dấu"})
    chart.set_legend({"none": True})
    chart.set_size({"width": 610, "height": 310})
    ws.insert_chart("D10", chart)


def _write_group_summary(workbook, fmts, result: PeerComparisonResult) -> None:
    bidders = result.summary.bidder_names
    fixed = [
        "Mức độ", "Điểm bất thường", "Mã nhóm", "Sheet/Hệ thống", "STT", "Mã hiệu",
        "Tên hạng mục", "ĐVT", "Số nhà thầu có hạng mục", "Độ tin cậy ghép",
        "Chênh đơn giá (%)", "Chênh khối lượng (%)", "Chênh thành tiền (%)",
        "Số thông số khác biệt", "Lý do",
    ]
    bidder_headers: list[str] = []
    for bidder in bidders:
        bidder_headers.extend([
            f"{bidder} - Có", f"{bidder} - Tên", f"{bidder} - ĐVT",
            f"{bidder} - Khối lượng", f"{bidder} - Đơn giá", f"{bidder} - Thành tiền",
            f"{bidder} - Vật tư/Quy cách", f"{bidder} - Thương hiệu", f"{bidder} - Xuất xứ",
        ])
    headers = fixed + bidder_headers
    ws = workbook.add_worksheet("Tổng hợp hạng mục")
    header_row = _setup_sheet(
        ws,
        "TỔNG HỢP THEO HẠNG MỤC — MỖI HẠNG MỤC MỘT DÒNG",
        "Các hồ sơ được đặt ngang hàng. Cột tên gợi ý chỉ là nhãn dễ đọc của nhóm, không phải nhà thầu chuẩn.",
        len(headers), fmts,
    )
    _write_headers(ws, header_row, headers, fmts)
    severity_formats = {severity: _severity_format(workbook, severity) for severity in Severity}
    for row_idx, group in enumerate(result.groups, start=header_row + 1):
        price = group.field("Đơn giá tổng hợp")
        quantity = group.field("Khối lượng")
        amount = group.field("Thành tiền")
        values: list[Any] = [
            group.severity.value, group.anomaly_score, group.group_id,
            group.display_sheet, group.display_stt, group.display_code,
            group.display_name, group.display_unit, group.presence_count,
            group.group_confidence, price.spread_pct if price else None,
            quantity.spread_pct if quantity else None, amount.spread_pct if amount else None,
            sum(entry.severity is not Severity.OK for entry in group.field_comparisons),
            " | ".join(dict.fromkeys(group.reasons)),
        ]
        for bidder in bidders:
            item = group.members.get(bidder)
            values.extend([
                "Có" if item else "Không", item.item_name if item else "", item.unit if item else "",
                item.quantity if item else None, item.unit_price_total if item else None,
                item.amount if item else None, item.material if item else "",
                item.brand if item else "", item.origin if item else "",
            ])
        for col, value in enumerate(values):
            if col == 0:
                ws.write(row_idx, col, value, severity_formats[group.severity])
            elif col in {1}:
                _write_value(ws, row_idx, col, value, fmts, "score")
            elif col in {9, 10, 11, 12}:
                _write_value(ws, row_idx, col, value, fmts, "pct")
            elif col == 14 or (col >= 15 and (col - 15) % 9 in {1, 6, 7, 8}):
                _write_value(ws, row_idx, col, value, fmts, "wrap")
            elif col >= 15 and (col - 15) % 9 in {3, 4, 5}:
                _write_value(ws, row_idx, col, value, fmts, "money")
            else:
                _write_value(ws, row_idx, col, value, fmts)
    ws.set_column(0, 0, 15)
    ws.set_column(1, 1, 15)
    ws.set_column(2, 2, 30)
    ws.set_column(3, 5, 16)
    ws.set_column(6, 6, 42)
    ws.set_column(7, 13, 16)
    ws.set_column(14, 14, 70)
    ws.autofilter(header_row, 0, max(header_row, header_row + len(result.groups)), len(headers) - 1)
    for start in range(15, len(headers), 9):
        ws.set_column(start, start, 11)
        ws.set_column(start + 1, start + 1, 38)
        ws.set_column(start + 2, start + 5, 16)
        ws.set_column(start + 6, start + 8, 28)


def _write_details(workbook, fmts, result: PeerComparisonResult) -> None:
    bidders = result.summary.bidder_names
    headers = [
        "Mức độ", "Mã nhóm", "Sheet/Hệ thống", "STT", "Tên hạng mục",
        "Nhóm thông số", "Thông số", "Chênh lệch tuyệt đối",
        "Chênh lệch (%)", "Độ giống nhau thấp nhất", "Giá trị từng nhà thầu", "Lý do",
    ]
    ws = workbook.add_worksheet("Chi tiết chênh lệch")
    header_row = _setup_sheet(
        ws,
        "CHI TIẾT TỪNG THÔNG SỐ KHÁC NHAU",
        "Mỗi dòng ghi rõ thông số nào khác, giá trị từng nhà thầu, chênh bao nhiêu phần trăm và vì sao bị đánh dấu.",
        len(headers), fmts,
    )
    _write_headers(ws, header_row, headers, fmts)
    severity_formats = {severity: _severity_format(workbook, severity) for severity in Severity}
    row_idx = header_row + 1
    for group, entry in result.iter_flagged_fields():
        row = [
            entry.severity.value, group.group_id, group.display_sheet, group.display_stt,
            group.display_name, entry.field_group, entry.field, entry.spread_abs,
            entry.spread_pct, entry.lowest_similarity, _values_text(entry, bidders), entry.reason,
        ]
        for col, value in enumerate(row):
            if col == 0:
                ws.write(row_idx, col, value, severity_formats[entry.severity])
            elif col == 7:
                _write_value(ws, row_idx, col, value, fmts, "money")
            elif col in {8, 9}:
                _write_value(ws, row_idx, col, value, fmts, "pct")
            elif col in {4, 10, 11}:
                _write_value(ws, row_idx, col, value, fmts, "wrap")
            else:
                _write_value(ws, row_idx, col, value, fmts)
        row_idx += 1
    ws.autofilter(header_row, 0, max(header_row, row_idx - 1), len(headers) - 1)
    ws.set_column("A:A", 15)
    ws.set_column("B:B", 30)
    ws.set_column("C:D", 16)
    ws.set_column("E:E", 42)
    ws.set_column("F:G", 24)
    ws.set_column("H:J", 18)
    ws.set_column("K:K", 58)
    ws.set_column("L:L", 72)


def _write_matrix(workbook, fmts, result: PeerComparisonResult, field: str, sheet_name: str) -> None:
    bidders = result.summary.bidder_names
    headers = ["Mã nhóm", "Sheet/Hệ thống", "STT", "Tên hạng mục", "ĐVT"] + bidders + [
        "Thấp nhất", "Trung vị", "Cao nhất", "Chênh lệch (%)", "Nhà thầu thấp", "Nhà thầu cao",
    ]
    ws = workbook.add_worksheet(sheet_name)
    header_row = _setup_sheet(
        ws,
        sheet_name.upper(),
        "Các giá trị được đặt cạnh nhau. Thấp nhất/trung vị/cao nhất chỉ mô tả mặt bằng chung, không phải giá chuẩn.",
        len(headers), fmts,
    )
    _write_headers(ws, header_row, headers, fmts)
    row_idx = header_row + 1
    for group in result.groups:
        entry = group.field(field)
        if entry is None:
            continue
        values = [
            group.group_id, group.display_sheet, group.display_stt, group.display_name,
            group.display_unit,
        ] + [entry.values.get(bidder) for bidder in bidders] + [
            entry.min_value, entry.median_value, entry.max_value, entry.spread_pct,
            ", ".join(entry.min_bidders), ", ".join(entry.max_bidders),
        ]
        for col, value in enumerate(values):
            if col == 3:
                _write_value(ws, row_idx, col, value, fmts, "wrap")
            elif col >= 5 and col < 5 + len(bidders) + 3:
                _write_value(ws, row_idx, col, value, fmts, "money")
            elif col == 5 + len(bidders) + 3:
                _write_value(ws, row_idx, col, value, fmts, "pct")
            else:
                _write_value(ws, row_idx, col, value, fmts)
        row_idx += 1
    ws.autofilter(header_row, 0, max(header_row, row_idx - 1), len(headers) - 1)
    ws.set_column("A:A", 30)
    ws.set_column("B:B", 18)
    ws.set_column("C:C", 10)
    ws.set_column("D:D", 44)
    ws.set_column("E:E", 11)
    ws.set_column(5, len(headers) - 1, 18)
    if row_idx > header_row + 1:
        pct_col = 5 + len(bidders) + 3
        ws.conditional_format(header_row + 1, pct_col, row_idx - 1, pct_col, {
            "type": "3_color_scale",
            "min_color": "#DCFCE7",
            "mid_color": "#FEF3C7",
            "max_color": "#FEE2E2",
        })


def _write_missing(workbook, fmts, result: PeerComparisonResult) -> None:
    bidders = result.summary.bidder_names
    headers = ["Mức độ", "Mã nhóm", "Sheet/Hệ thống", "STT", "Mã hiệu", "Tên hạng mục", "ĐVT"] + bidders + ["Lý do"]
    ws = workbook.add_worksheet("Khác danh mục")
    header_row = _setup_sheet(
        ws,
        "HẠNG MỤC KHÔNG CÓ ĐỦ Ở TẤT CẢ NHÀ THẦU",
        "Mỗi cột nhà thầu ghi Có/Không. Không dùng khái niệm thiếu so với nhà thầu chuẩn.",
        len(headers), fmts,
    )
    _write_headers(ws, header_row, headers, fmts)
    sev_formats = {severity: _severity_format(workbook, severity) for severity in Severity}
    row_idx = header_row + 1
    for group in result.groups:
        if group.presence_count == len(bidders):
            continue
        values = [
            group.severity.value, group.group_id, group.display_sheet, group.display_stt,
            group.display_code, group.display_name, group.display_unit,
        ] + ["Có" if bidder in group.members else "Không" for bidder in bidders] + [
            next((entry.reason for entry in group.field_comparisons if entry.field == "Sự hiện diện hạng mục"), "")
        ]
        for col, value in enumerate(values):
            if col == 0:
                ws.write(row_idx, col, value, sev_formats[group.severity])
            elif col in {5, len(headers) - 1}:
                _write_value(ws, row_idx, col, value, fmts, "wrap")
            else:
                _write_value(ws, row_idx, col, value, fmts)
        row_idx += 1
    ws.autofilter(header_row, 0, max(header_row, row_idx - 1), len(headers) - 1)
    ws.set_column("A:A", 15)
    ws.set_column("B:B", 30)
    ws.set_column("C:E", 16)
    ws.set_column("F:F", 46)
    ws.set_column("G:G", 11)
    ws.set_column(7, 7 + len(bidders) - 1, 20)
    ws.set_column(len(headers) - 1, len(headers) - 1, 72)


def _write_quality(workbook, fmts, result: PeerComparisonResult) -> None:
    headers = ["Nhà thầu", "File", "Sheet/Hệ thống", "Dòng", "STT", "Tên hạng mục", "Cảnh báo dữ liệu"]
    ws = workbook.add_worksheet("Chất lượng dữ liệu")
    header_row = _setup_sheet(
        ws,
        "CẢNH BÁO CHẤT LƯỢNG FILE GỐC",
        "Các lỗi file nguồn cần được xác nhận trước khi dùng kết quả so sánh để kết luận.",
        len(headers), fmts,
    )
    _write_headers(ws, header_row, headers, fmts)
    row_idx = header_row + 1
    for group in result.groups:
        for bidder, item in group.members.items():
            for flag in item.data_quality_flags:
                row = [bidder, item.workbook, item.sheet, item.row_number, item.stt, item.item_name, flag]
                for col, value in enumerate(row):
                    _write_value(ws, row_idx, col, value, fmts, "wrap" if col in {1, 5, 6} else "text")
                row_idx += 1
    ws.autofilter(header_row, 0, max(header_row, row_idx - 1), len(headers) - 1)
    ws.set_column("A:A", 22)
    ws.set_column("B:B", 52)
    ws.set_column("C:C", 18)
    ws.set_column("D:E", 10)
    ws.set_column("F:F", 44)
    ws.set_column("G:G", 72)


def _write_audit(workbook, fmts, result: PeerComparisonResult) -> None:
    ws = workbook.add_worksheet("Nhật ký và bảo mật")
    _write_headers(ws, 0, ["Thuộc tính", "Giá trị"], fmts)
    data = {
        "Chế độ": "SO SÁNH NGANG HÀNG — KHÔNG BASELINE",
        "Nguyên tắc": "Mọi nhà thầu có địa vị ngang nhau trong phép tính",
        "Công thức độ phân tán": "(max - min) / mean(abs(values))",
        "Ý nghĩa trung vị": "Chỉ mô tả mặt bằng chung; không phải giá chuẩn",
        "Mức bảo mật": result.audit.get("privacy", "LOCAL"),
        "Cho phép mạng": result.audit.get("network_allowed", False),
        "Embedding local": result.audit.get("embedding_model", "disabled/not installed"),
        "Reranker local": result.audit.get("reranker_model", "disabled/not installed"),
        "SHA-256 các hồ sơ": json.dumps(result.audit.get("bidder_sha256", {}), ensure_ascii=False, indent=2),
        "Ngưỡng đánh giá": json.dumps(result.audit.get("thresholds", {}), ensure_ascii=False, indent=2),
        "Lưu ý": "Cảnh báo là tín hiệu hỗ trợ rà soát; chuyên viên phải xem hồ sơ gốc trước khi kết luận.",
    }
    for row_idx, (key, value) in enumerate(data.items(), start=1):
        ws.write(row_idx, 0, key, fmts["text"])
        ws.write(row_idx, 1, _safe_text(value), fmts["wrap"])
    ws.set_column("A:A", 30)
    ws.set_column("B:B", 100)


def export_peer_comparison_report(result: PeerComparisonResult, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(str(output), {"constant_memory": True})
    workbook.set_properties({
        "title": "Báo cáo so sánh ngang hàng các hồ sơ dự thầu",
        "subject": "So sánh giá, khối lượng, tên và thông số giữa nhiều nhà thầu",
        "comments": "Không lấy nhà thầu nào làm chuẩn. Cảnh báo chỉ hỗ trợ rà soát.",
    })
    fmts = _formats(workbook)
    _write_guide(workbook, fmts, result)
    _write_overview(workbook, fmts, result)
    _write_group_summary(workbook, fmts, result)
    _write_details(workbook, fmts, result)
    _write_matrix(workbook, fmts, result, "Đơn giá tổng hợp", "Ma trận đơn giá")
    _write_matrix(workbook, fmts, result, "Khối lượng", "Ma trận khối lượng")
    _write_missing(workbook, fmts, result)
    _write_quality(workbook, fmts, result)
    _write_audit(workbook, fmts, result)
    workbook.close()
    return output
