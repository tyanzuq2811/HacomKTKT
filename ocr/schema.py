from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from core.excel_reader import COLUMN_PATTERNS
from core.text_normalizer import normalize_text

from .models import OCRCell, OCRTable


FIELD_PRIORITY = [
    "item_code", "item_name", "unit", "quantity", "unit_price", "amount",
    "material", "brand", "origin", "note",
]

FIELD_LABELS = {
    "item_code": "Mã hiệu",
    "item_name": "Tên hạng mục",
    "unit": "ĐVT",
    "quantity": "Khối lượng",
    "unit_price": "Đơn giá",
    "amount": "Thành tiền",
    "material": "Vật tư/Quy cách",
    "brand": "Thương hiệu",
    "origin": "Xuất xứ",
    "note": "Ghi chú",
}


def infer_header_rows(table: OCRTable) -> int:
    row_heights = [table.y_lines[i+1] - table.y_lines[i] for i in range(len(table.y_lines)-1)]
    if len(row_heights) <= 2:
        return 1
    median = sorted(row_heights)[len(row_heights)//2]
    header = 1
    # Multi-level table headers are usually taller than data rows.
    for i, h in enumerate(row_heights[:5]):
        if i == 0 or h >= median * 1.15:
            header = i + 1
        else:
            break
    return max(1, min(header, 4))


def infer_columns(table: OCRTable) -> dict[int, str]:
    by_col: dict[int, list[str]] = defaultdict(list)
    for cell in table.cells:
        if cell.row < table.header_rows and cell.text:
            by_col[cell.col].append(cell.text)

    candidates: list[tuple[int, int, str]] = []
    for col in range(max((c.col for c in table.cells), default=-1) + 1):
        header = normalize_text(" ".join(by_col.get(col, [])))
        for field, patterns in COLUMN_PATTERNS.items():
            score = max((pts for phrase, pts in patterns if normalize_text(phrase) in header), default=0)
            if score:
                candidates.append((score, col, field))

    candidates.sort(key=lambda x: (-x[0], x[1]))
    mapping: dict[int, str] = {}
    used_fields: set[str] = set()
    for score, col, field in candidates:
        if col not in mapping and field not in used_fields:
            mapping[col] = field
            used_fields.add(field)

    n_cols = max((c.col for c in table.cells), default=-1) + 1
    # Conservative positional recovery for dense Vietnamese BOQ tables.
    # Only fills fields not recognized from headers; recognized columns always win.
    numeric_candidates = list(range(max(0, n_cols - 9), n_cols))
    if "item_name" not in used_fields and n_cols >= 6:
        # Name/description is usually the widest early-middle column.
        widths = [table.x_lines[i+1] - table.x_lines[i] for i in range(n_cols)]
        early = range(0, min(n_cols, max(6, n_cols // 2 + 1)))
        col = max(early, key=lambda i: widths[i])
        if col not in mapping:
            mapping[col] = "item_name"; used_fields.add("item_name")
    if "unit" not in used_fields and n_cols >= 5:
        widths = [table.x_lines[i+1] - table.x_lines[i] for i in range(n_cols)]
        possible = [i for i in range(n_cols) if i not in mapping]
        if possible:
            col = min(possible, key=lambda i: widths[i])
            mapping[col] = "unit"; used_fields.add("unit")
    # Prefer right-side financial columns in order quantity -> unit price -> amount.
    free_right = [c for c in numeric_candidates if c not in mapping]
    for field, position in (("amount", -1), ("unit_price", -2), ("quantity", -3)):
        if field not in used_fields and len(free_right) >= abs(position):
            col = free_right[position]
            mapping[col] = field; used_fields.add(field)

    table.column_fields = mapping
    return mapping


def is_numeric_field(field: str) -> bool:
    return field in {"quantity", "unit_price", "amount", "stt"}
