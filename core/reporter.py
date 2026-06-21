from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import xlsxwriter

from .models import ComparisonResult, Severity

EXCEL_MAX_ROWS = 1_048_576


def _safe_excel_text(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    if value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def _write_value(ws, row: int, col: int, value: Any, fmt=None):
    value = _safe_excel_text(value)
    if value is None:
        ws.write_blank(row, col, None, fmt)
    elif isinstance(value, bool):
        ws.write_boolean(row, col, value, fmt)
    elif isinstance(value, (int, float)):
        ws.write_number(row, col, value, fmt)
    else:
        ws.write(row, col, value, fmt)


def export_comparison_report(result: ComparisonResult, output_path: str | Path) -> str:
    output_path = str(output_path)
    wb = xlsxwriter.Workbook(output_path, {"constant_memory": True, "strings_to_formulas": False, "strings_to_urls": False})
    wb.set_properties({
        "title": "Báo cáo đối chiếu hồ sơ thầu",
        "subject": "Phân tích HSMT/HSDT và bất thường giá",
        "author": "HSMT Enterprise AI — local-only",
        "comments": "Dữ liệu được xử lý cục bộ; kết quả cần chuyên viên xác nhận.",
    })

    formats = _formats(wb)
    _write_summary(wb, result, formats)
    flat_rows = list(result.iter_flat())
    _write_rows_chunked(wb, "Đối chiếu chi tiết", flat_rows, formats)
    anomalies = [r for r in flat_rows if r["Mức độ"] in {Severity.WARNING.value, Severity.CRITICAL.value, Severity.REVIEW.value}]
    _write_rows_chunked(wb, "Bất thường", anomalies, formats)
    _write_price_matrix(wb, result, formats)
    _write_unmatched(wb, flat_rows, formats)
    _write_audit(wb, result, formats)
    wb.close()
    return output_path


def _formats(wb):
    return {
        "title": wb.add_format({"bold": True, "font_size": 18, "font_color": "#FFFFFF", "bg_color": "#17365D", "align": "center", "valign": "vcenter"}),
        "section": wb.add_format({"bold": True, "font_size": 12, "font_color": "#FFFFFF", "bg_color": "#2F75B5"}),
        "header": wb.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": "#1F4E78", "border": 1, "align": "center", "valign": "vcenter", "text_wrap": True}),
        "text": wb.add_format({"border": 1, "valign": "top", "text_wrap": True}),
        "num": wb.add_format({"border": 1, "num_format": "#,##0.00;[Red]-#,##0.00", "valign": "top"}),
        "money": wb.add_format({"border": 1, "num_format": "#,##0;[Red]-#,##0", "valign": "top"}),
        "pct": wb.add_format({"border": 1, "num_format": "0.00%;[Red]-0.00%", "valign": "top"}),
        "score": wb.add_format({"border": 1, "num_format": "0.0", "valign": "top"}),
        "label": wb.add_format({"bold": True, "bg_color": "#D9EAF7", "border": 1}),
        "value": wb.add_format({"border": 1}),
        "ok": wb.add_format({"bg_color": "#E2F0D9", "font_color": "#375623", "border": 1}),
        "review": wb.add_format({"bg_color": "#FFF2CC", "font_color": "#7F6000", "border": 1}),
        "warning": wb.add_format({"bg_color": "#FCE4D6", "font_color": "#C65911", "border": 1}),
        "critical": wb.add_format({"bg_color": "#F4CCCC", "font_color": "#9C0006", "bold": True, "border": 1}),
        "mono": wb.add_format({"font_name": "Consolas", "font_size": 9, "text_wrap": True, "valign": "top"}),
    }


def _write_summary(wb, result: ComparisonResult, f):
    ws = wb.add_worksheet("Tổng quan")
    ws.set_tab_color("#2F75B5")
    ws.set_column("A:A", 30)
    ws.set_column("B:B", 24)
    ws.set_column("D:D", 28)
    ws.set_column("E:E", 24)
    ws.merge_range("A1:E2", "BÁO CÁO ĐỐI CHIẾU & PHÁT HIỆN BẤT THƯỜNG", f["title"])
    ws.set_row(0, 26)
    s = result.summary
    metrics = [
        ("Nguồn chuẩn", s.reference_name),
        ("Số nhà thầu", s.bidder_count),
        ("Hạng mục chuẩn", s.total_reference_items),
        ("Dòng đối chiếu", s.total_rows),
        ("Khớp chính xác", s.exact_matches),
        ("Khớp tương đối/ngữ nghĩa", s.fuzzy_matches),
        ("Thiếu hạng mục", s.missing_items),
        ("Hạng mục ngoài danh mục", s.extra_items),
        ("Dòng cảnh báo", s.warning_rows),
        ("Dòng bất thường", s.critical_rows),
        ("Tổng giá chuẩn", s.total_reference_amount),
        ("Thời điểm tạo", s.generated_at),
    ]
    row = 3
    for label, value in metrics:
        _write_value(ws, row, 0, label, f["label"])
        _write_value(ws, row, 1, value, f["money"] if "giá" in label.lower() else f["value"])
        row += 1

    row = 3
    _write_value(ws, row, 3, "Tổng giá theo nhà thầu", f["section"])
    _write_value(ws, row, 4, "Giá trị", f["section"])
    row += 1
    for bidder, total in sorted(s.bidder_totals.items()):
        _write_value(ws, row, 3, bidder, f["text"])
        _write_value(ws, row, 4, total, f["money"])
        row += 1

    if result.warnings:
        row = max(row + 2, 18)
        ws.merge_range(row, 0, row, 4, "CẢNH BÁO ĐỌC DỮ LIỆU", f["section"])
        row += 1
        for warning in result.warnings[:200]:
            ws.merge_range(row, 0, row, 4, _safe_excel_text(warning), f["review"])
            row += 1
    ws.freeze_panes(3, 0)


def _column_format(header: str, f):
    h = header.lower()
    if "(%)" in h or header in {"Điểm khớp", "Điểm từ vựng", "Điểm ngữ nghĩa"}:
        return f["pct"]
    if any(k in h for k in ["đơn giá", "thành tiền", "trung vị giá", "lệch thành tiền"]):
        return f["money"]
    if any(k in h for k in ["kl ", "lệch kl"]):
        return f["num"]
    if header in {"Robust Z", "Điểm bất thường"}:
        return f["score"]
    return f["text"]


def _width_for(header: str) -> int:
    h = header.lower()
    if "tên " in h or "cờ đánh giá" in h or "vật tư" in h:
        return 42
    if "sheet" in h or "kiểu khớp" in h or "mức độ" in h:
        return 18
    if "mã" in h or "nhà thầu" in h:
        return 22
    return 15


def _write_rows_chunked(wb, base_name: str, rows: list[dict[str, Any]], f):
    if not rows:
        ws = wb.add_worksheet(base_name[:31])
        ws.write(0, 0, "Không có dữ liệu", f["header"])
        return
    headers = list(rows[0].keys())
    capacity = EXCEL_MAX_ROWS - 2
    for part, start in enumerate(range(0, len(rows), capacity), start=1):
        chunk = rows[start:start + capacity]
        name = base_name if part == 1 else f"{base_name[:26]}_{part}"
        ws = wb.add_worksheet(name[:31])
        if base_name == "Bất thường":
            ws.set_tab_color("#C00000")
        ws.freeze_panes(1, 0)
        ws.autofilter(0, 0, len(chunk), len(headers) - 1)
        ws.set_row(0, 34)
        for col, header in enumerate(headers):
            _write_value(ws, 0, col, header, f["header"])
            ws.set_column(col, col, _width_for(header))
        for r_idx, record in enumerate(chunk, start=1):
            severity = record.get("Mức độ", "")
            for c_idx, header in enumerate(headers):
                fmt = _column_format(header, f)
                if header == "Mức độ":
                    fmt = {
                        Severity.OK.value: f["ok"],
                        Severity.REVIEW.value: f["review"],
                        Severity.WARNING.value: f["warning"],
                        Severity.CRITICAL.value: f["critical"],
                    }.get(severity, f["text"])
                _write_value(ws, r_idx, c_idx, record.get(header), fmt)
        # Highlight the entire anomaly score scale and critical deviations.
        if "Điểm bất thường" in headers:
            c = headers.index("Điểm bất thường")
            ws.conditional_format(1, c, len(chunk), c, {"type": "3_color_scale", "min_color": "#63BE7B", "mid_color": "#FFEB84", "max_color": "#F8696B"})


def _write_price_matrix(wb, result: ComparisonResult, f):
    ws = wb.add_worksheet("Ma trận giá")
    ws.set_tab_color("#70AD47")
    bidders = sorted(result.summary.bidder_totals)
    grouped: dict[str, dict[str, Any]] = defaultdict(dict)
    meta: dict[str, tuple[str, str, str]] = {}
    for row in result.rows:
        item = row.reference or row.candidate
        if not item:
            continue
        meta[row.canonical_id] = (item.item_code, item.item_name, item.unit)
        grouped[row.canonical_id][row.bidder] = row.candidate.unit_price if row.candidate else None
    headers = ["Mã chuẩn", "Mã hiệu", "Tên hạng mục", "ĐVT"] + bidders + ["Min", "Trung vị", "Max", "Biên độ %"]
    for c, h in enumerate(headers):
        _write_value(ws, 0, c, h, f["header"])
        ws.set_column(c, c, 42 if h == "Tên hạng mục" else 18)
    ws.freeze_panes(1, 4)
    for r, cid in enumerate(sorted(grouped), start=1):
        code, name, unit = meta[cid]
        prices = [grouped[cid].get(b) for b in bidders]
        valid = [p for p in prices if p is not None]
        median = sorted(valid)[len(valid)//2] if valid else None
        min_v, max_v = (min(valid), max(valid)) if valid else (None, None)
        spread = ((max_v - min_v) / abs(median)) if valid and median not in {None, 0} else None
        values = [cid, code, name, unit] + prices + [min_v, median, max_v, spread]
        for c, value in enumerate(values):
            fmt = f["pct"] if headers[c] == "Biên độ %" else (f["money"] if c >= 4 else f["text"])
            _write_value(ws, r, c, value, fmt)
    if grouped:
        ws.autofilter(0, 0, len(grouped), len(headers)-1)


def _write_unmatched(wb, rows: list[dict[str, Any]], f):
    unmatched = [r for r in rows if r["Kiểu khớp"] in {"missing", "extra"}]
    _write_rows_chunked(wb, "Thiếu và ngoài danh mục", unmatched, f)


def _write_audit(wb, result: ComparisonResult, f):
    ws = wb.add_worksheet("Nhật ký & bảo mật")
    ws.set_column("A:A", 34)
    ws.set_column("B:B", 100)
    ws.write(0, 0, "Thuộc tính", f["header"])
    ws.write(0, 1, "Giá trị", f["header"])
    entries = {
        "Chế độ xử lý": result.audit.get("mode"),
        "Mức bảo mật": result.audit.get("privacy"),
        "Cho phép mạng": result.audit.get("network_allowed"),
        "Mô hình embedding": result.audit.get("embedding_model"),
        "SHA-256 nguồn chuẩn": result.audit.get("reference_sha256"),
        "SHA-256 các HSDT": json.dumps(result.audit.get("bidder_sha256", {}), ensure_ascii=False, indent=2),
        "Ngưỡng đánh giá": json.dumps(result.audit.get("thresholds", {}), ensure_ascii=False, indent=2),
        "Lưu ý pháp lý": "Điểm bất thường là tín hiệu hỗ trợ rà soát, không phải kết luận gian lận hay quyết định lựa chọn nhà thầu.",
    }
    for r, (key, value) in enumerate(entries.items(), start=1):
        _write_value(ws, r, 0, key, f["label"])
        _write_value(ws, r, 1, value, f["mono"])
