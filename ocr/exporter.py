from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import xlsxwriter

from .models import OCRDocument


def _safe_text(v: Any) -> Any:
    if isinstance(v, str) and v.startswith(("=", "+", "-", "@")):
        return "'" + v
    return v


def export_ocr_document(document: OCRDocument, output_path: str | Path) -> str:
    output_path = str(output_path)
    wb = xlsxwriter.Workbook(output_path, {"constant_memory": True, "strings_to_formulas": False, "strings_to_urls": False})
    title = wb.add_format({"bold": True, "font_size": 16, "font_color": "#FFFFFF", "bg_color": "#17365D", "align": "center"})
    header = wb.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": "#1F4E78", "border": 1, "text_wrap": True, "align": "center"})
    text = wb.add_format({"border": 1, "text_wrap": True, "valign": "top"})
    num = wb.add_format({"border": 1, "num_format": "#,##0.00;[Red]-#,##0.00"})
    money = wb.add_format({"border": 1, "num_format": "#,##0;[Red]-#,##0"})
    ok = wb.add_format({"border": 1, "bg_color": "#E2F0D9"})
    review = wb.add_format({"border": 1, "bg_color": "#FFF2CC", "font_color": "#7F6000", "text_wrap": True})
    critical = wb.add_format({"border": 1, "bg_color": "#F4CCCC", "font_color": "#9C0006", "text_wrap": True})
    mono = wb.add_format({"font_name": "Consolas", "font_size": 9, "text_wrap": True, "valign": "top"})

    ws = wb.add_worksheet("Dữ liệu OCR")
    headers = [
        "Trang", "Dòng bảng", "Mã hiệu", "Tên hạng mục", "ĐVT", "Khối lượng",
        "Đơn giá", "Thành tiền", "Thành tiền tính lại", "Vật tư/Quy cách",
        "Thương hiệu", "Xuất xứ", "Ghi chú", "Độ tin cậy OCR", "Trạng thái OCR", "Lý do kiểm tra",
    ]
    for c, h in enumerate(headers):
        ws.write(0, c, h, header)
        ws.set_column(c, c, 42 if h in {"Tên hạng mục", "Lý do kiểm tra", "Vật tư/Quy cách"} else 16)
    ws.freeze_panes(1, 0)
    ws.autofilter(0, 0, max(1, len(document.rows)), len(headers)-1)
    for r, row in enumerate(document.rows, start=1):
        values = [
            row.get("page"), row.get("table_row"), row.get("item_code", ""), row.get("item_name", ""),
            row.get("unit", ""), row.get("quantity"), row.get("unit_price"), row.get("amount"),
            row.get("computed_amount"), row.get("material", ""), row.get("brand", ""), row.get("origin", ""),
            row.get("note", ""), row.get("ocr_confidence"), row.get("ocr_status"), " | ".join(row.get("ocr_flags", [])),
        ]
        for c, value in enumerate(values):
            fmt = text
            if c == 5:
                fmt = num
            elif c in {6, 7, 8}:
                fmt = money
            elif c == 13:
                fmt = wb.add_format({"border": 1, "num_format": "0.0%"})
            elif c in {14, 15}:
                fmt = review if row.get("ocr_flags") else ok
            ws.write(r, c, _safe_text(value), fmt)

    review_ws = wb.add_worksheet("Ô cần kiểm tra")
    review_headers = ["Trang", "Hàng", "Cột", "Trường", "Nội dung OCR", "Confidence", "Engine", "Lý do", "BBox", "Ảnh ô"]
    for c, h in enumerate(review_headers):
        review_ws.write(0, c, h, header)
        review_ws.set_column(c, c, 24 if h not in {"Nội dung OCR", "Lý do"} else 48)
    rr = 1
    for page in document.pages:
        for table in page.tables:
            for cell in table.cells:
                if not cell.review_reason:
                    continue
                values = [cell.page, cell.row, cell.col, cell.field, cell.text, cell.confidence, cell.engine, cell.review_reason, str(cell.bbox), cell.image_path]
                for c, value in enumerate(values):
                    review_ws.write(rr, c, _safe_text(value), review if c in {4, 7} else text)
                rr += 1
    review_ws.freeze_panes(1, 0)

    audit = wb.add_worksheet("Nhật ký OCR")
    audit.set_column("A:A", 32); audit.set_column("B:B", 110)
    audit.write(0, 0, "Thuộc tính", header); audit.write(0, 1, "Giá trị", header)
    entries = {
        "Tệp nguồn": document.source_path.name,
        "Số trang": len(document.pages),
        "Số dòng trích xuất": len(document.rows),
        "Cảnh báo": json.dumps(document.warnings, ensure_ascii=False, indent=2),
        "Audit": json.dumps(document.audit, ensure_ascii=False, indent=2),
        "Nguyên tắc": "OCR chỉ hỗ trợ số hóa. Ô thiếu, confidence thấp hoặc sai kiểm tra toán học bắt buộc được người dùng xác nhận.",
    }
    for r, (k, v) in enumerate(entries.items(), start=1):
        audit.write(r, 0, k, text); audit.write(r, 1, _safe_text(v), mono)
    wb.close()
    return output_path
