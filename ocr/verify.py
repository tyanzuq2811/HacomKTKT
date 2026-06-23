from __future__ import annotations

from collections import defaultdict
from typing import Any

from core.number_parser import math_error, parse_number, safe_amount

from .config import OCRConfig
from .models import OCRCell, OCRTable


REQUIRED_FIELDS = {"item_name", "quantity", "unit_price", "amount"}


def assemble_rows(table: OCRTable, config: OCRConfig) -> list[dict[str, Any]]:
    grouped: dict[int, list[OCRCell]] = defaultdict(list)
    for cell in table.cells:
        if cell.row >= table.header_rows:
            grouped[cell.row].append(cell)
    rows: list[dict[str, Any]] = []
    for row_idx in sorted(grouped):
        cells = sorted(grouped[row_idx], key=lambda c: c.col)
        record: dict[str, Any] = {
            "page": table.page,
            "table_row": row_idx,
            "ocr_confidence": 1.0,
            "ocr_status": "OK",
            "ocr_flags": [],
            "raw_columns": {},
        }
        for cell in cells:
            field = table.column_fields.get(cell.col, f"col_{cell.col+1}")
            cell.field = field
            record["raw_columns"][field] = cell.text
            if field in {"quantity", "unit_price", "amount"}:
                cell.numeric_value = parse_number(cell.text)
                record[field] = cell.numeric_value
            else:
                record[field] = cell.text
            record["ocr_confidence"] = min(record["ocr_confidence"], cell.confidence if cell.text else 0.0)
            if cell.review_reason:
                record["ocr_flags"].append(f"{field}: {cell.review_reason}")

        name = str(record.get("item_name", "") or "").strip()
        any_value = any(str(v or "").strip() for k, v in record.items() if k not in {"raw_columns", "ocr_flags"})
        if not any_value:
            continue

        # A short text-only row is treated as a group header, not a financial item.
        record["is_group"] = bool(name and record.get("quantity") is None and record.get("unit_price") is None and record.get("amount") is None)
        if not record["is_group"]:
            for field in REQUIRED_FIELDS:
                value = record.get(field)
                missing = value is None or (isinstance(value, str) and not value.strip())
                if missing:
                    record["ocr_flags"].append(f"Thiếu trường bắt buộc: {field}")
            q, p, a = record.get("quantity"), record.get("unit_price"), record.get("amount")
            err = math_error(q, p, a, config.math_tolerance_pct)
            if err is not None:
                record["ocr_flags"].append(f"Sai KL×ĐG=TT, lệch {err:,.0f}")
            record["computed_amount"] = safe_amount(q, p, None)

        if record["ocr_flags"]:
            record["ocr_status"] = "CẦN KIỂM TRA"
        rows.append(record)
    return rows


def update_cell_status(cell: OCRCell, config: OCRConfig, numeric: bool) -> None:
    if not cell.text:
        cell.status = "empty"
        cell.review_reason = "Ô trống/không đọc được"
        return
    threshold = config.min_numeric_confidence if numeric else config.min_text_confidence
    if cell.confidence < threshold:
        cell.status = "low_confidence"
        cell.review_reason = f"Độ tin cậy thấp {cell.confidence:.1%}"
    else:
        cell.status = "ok"
    if numeric and parse_number(cell.text) is None:
        cell.status = "invalid_number"
        cell.review_reason = f"Không chuẩn hóa được số: {cell.text}"
