from __future__ import annotations

import hashlib
import re
from pathlib import Path
from itertools import chain
from typing import Any, Iterable, Optional

from openpyxl import load_workbook

from .models import DocumentRole, ItemRecord, WorkbookData
from .number_parser import math_error, parse_number, safe_amount
from .text_normalizer import normalize_code, normalize_name, normalize_text, normalize_unit


# Weighted signals. The detector scores flattened multi-row headers.
COLUMN_PATTERNS: dict[str, list[tuple[str, int]]] = {
    "item_code": [
        ("ma hieu", 10), ("mã hiệu", 10), ("ma cong tac", 9),
        ("mã công tác", 9), ("ky hieu", 7), ("code", 6),
    ],
    "item_name": [
        ("ten hang muc", 12), ("tên hạng mục", 12), ("noi dung cong viec", 11),
        ("nội dung công việc", 11), ("dien giai", 10), ("diễn giải", 10),
        ("mo ta", 8), ("mô tả", 8), ("ten vat tu", 8), ("tên vật tư", 8),
    ],
    "unit": [("don vi tinh", 12), ("đơn vị tính", 12), ("dvt", 10), ("đvt", 10), ("don vi", 7)],
    "quantity": [
        ("khoi luong nha thau", 14), ("khối lượng nhà thầu", 14),
        ("khoi luong moi thau", 13), ("khối lượng mời thầu", 13),
        ("khoi luong", 10), ("khối lượng", 10), ("so luong", 8), ("số lượng", 8),
    ],
    "unit_price": [
        ("don gia du thau", 14), ("đơn giá dự thầu", 14),
        ("don gia nha thau", 14), ("đơn giá nhà thầu", 14),
        ("don gia tong hop", 12), ("đơn giá tổng hợp", 12),
        ("don gia", 10), ("đơn giá", 10), ("price", 7),
    ],
    "amount": [
        ("thanh tien sau thue", 15), ("thành tiền sau thuế", 15),
        ("thanh tien truoc thue", 14), ("thành tiền trước thuế", 14),
        ("thanh tien", 11), ("thành tiền", 11), ("gia tri", 8), ("giá trị", 8),
    ],
    "material": [
        ("ma hieu quy cach", 13), ("mã hiệu quy cách", 13),
        ("quy cach", 10), ("quy cách", 10), ("vat tu", 9), ("vật tư", 9),
        ("vat lieu", 8), ("vật liệu", 8),
    ],
    "brand": [("thuong hieu", 12), ("thương hiệu", 12), ("nhan hieu", 10), ("hãng", 8)],
    "origin": [("xuat xu", 12), ("xuất xứ", 12), ("nuoc san xuat", 9), ("country", 7)],
    "note": [("ghi chu", 10), ("ghi chú", 10), ("remark", 7)],
}

ROLE_BONUS = {
    DocumentRole.HSDT: {
        "quantity": ["nha thau", "dự thầu", "du thau", "chào"],
        "unit_price": ["nha thau", "dự thầu", "du thau", "chào"],
        "amount": ["nha thau", "dự thầu", "du thau", "chào"],
    },
    DocumentRole.HSMT: {
        "quantity": ["moi thau", "mời thầu", "hsmt"],
        "unit_price": ["moi thau", "mời thầu", "hsmt", "du toan", "dự toán"],
        "amount": ["moi thau", "mời thầu", "hsmt", "du toan", "dự toán"],
    },
}

SKIP_SHEETS = {"tong hop", "tổng hợp", "dieu khoan", "điều khoản", "bia", "bìa", "muc luc", "mục lục", "chart"}


def file_sha256(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def list_sheets(path: str | Path) -> list[dict[str, Any]]:
    wb = load_workbook(path, read_only=True, data_only=True)
    result = []
    try:
        for ws in wb.worksheets:
            result.append({"name": ws.title, "rows": ws.max_row or 0, "cols": ws.max_column or 0})
    finally:
        wb.close()
    return result


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _flatten_header(rows: list[list[Any]], column_count: int) -> list[str]:
    inherited = [""] * column_count
    parts: list[list[str]] = [[] for _ in range(column_count)]
    for row in rows:
        current = ""
        for c in range(column_count):
            text = _as_text(row[c] if c < len(row) else "")
            if text:
                current = text
                inherited[c] = text
            elif current:
                # This safely approximates horizontally merged cells in read_only mode.
                inherited[c] = current
            if inherited[c]:
                norm = normalize_text(inherited[c])
                if norm and norm not in parts[c]:
                    parts[c].append(norm)
    return [" ".join(p) for p in parts]


def _header_signal_score(texts: Iterable[str]) -> int:
    joined = " | ".join(normalize_text(x) for x in texts if x)
    score = 0
    recognized = set()
    for field, patterns in COLUMN_PATTERNS.items():
        field_score = max((pts for phrase, pts in patterns if normalize_text(phrase) in joined), default=0)
        if field_score:
            score += field_score
            recognized.add(field)
    score += len(recognized) * 3
    return score


def detect_header(buffer: list[list[Any]], max_header_depth: int = 3) -> tuple[int, int, list[str]]:
    """Return zero-based start, end and flattened header names."""
    if not buffer:
        raise ValueError("Sheet không có dữ liệu")
    max_cols = max(len(r) for r in buffer)
    best: tuple[int, int, int, list[str]] | None = None
    scan_limit = min(len(buffer), 60)
    for start in range(scan_limit):
        # A document title/merged banner usually has only one populated cell and
        # must not be treated as the first level of a table header.
        if sum(bool(_as_text(v)) for v in buffer[start]) < 2:
            continue
        for depth in range(1, max_header_depth + 1):
            end = start + depth
            if end > scan_limit:
                break
            flat = _flatten_header(buffer[start:end], max_cols)
            score = _header_signal_score(flat)
            # Prefer shallower headers when scores tie.
            candidate = (score, -depth, -start, flat)
            if best is None or candidate[:3] > best[:3]:
                best = (score, -depth, -start, flat)
    if best is None or best[0] < 18:
        raise ValueError("Không tự nhận diện được hàng tiêu đề. Hãy chọn sheet/định dạng đúng.")
    depth = -best[1]
    start = -best[2]
    return start, start + depth - 1, best[3]


def map_columns(flat_headers: list[str], role: DocumentRole) -> dict[int, str]:
    candidates: list[tuple[int, int, str]] = []
    for col, text in enumerate(flat_headers):
        plain = normalize_text(text)
        if not plain:
            continue
        for field, patterns in COLUMN_PATTERNS.items():
            score = 0
            for phrase, pts in patterns:
                if normalize_text(phrase) in plain:
                    score = max(score, pts)
            if score and any(normalize_text(x) in plain for x in ROLE_BONUS.get(role, {}).get(field, [])):
                score += 4
            if score:
                candidates.append((score, col, field))

    candidates.sort(key=lambda x: (-x[0], x[1], x[2]))
    used_cols: set[int] = set()
    used_fields: set[str] = set()
    mapping: dict[int, str] = {}
    for score, col, field in candidates:
        if col in used_cols or field in used_fields:
            continue
        mapping[col] = field
        used_cols.add(col)
        used_fields.add(field)
    return mapping


def _numbering_row(row: list[Any]) -> bool:
    values = [_as_text(v) for v in row if _as_text(v)]
    if len(values) < 3:
        return False
    numeric = sum(bool(re.fullmatch(r"\d+", v) or re.match(r"^\d+\s*=", v)) for v in values)
    return numeric / len(values) >= 0.6


def _row_is_empty(row: list[Any]) -> bool:
    return not any(_as_text(v) for v in row)


def _looks_group(name: str, quantity: Optional[float], unit_price: Optional[float], amount: Optional[float], unit: str) -> bool:
    if not name:
        return False
    if quantity is not None or unit_price is not None or amount is not None or unit:
        return False
    short = name.strip()
    return len(short) < 180


def _iter_sheet_rows(ws) -> Iterable[tuple[int, list[Any]]]:
    for row_num, row in enumerate(ws.iter_rows(values_only=True), start=1):
        yield row_num, list(row)


def load_workbook_items(
    path: str | Path,
    role: DocumentRole,
    bidder: str = "",
    selected_sheets: Optional[list[str]] = None,
    max_rows: int = 1_000_000,
) -> WorkbookData:
    path = Path(path)
    if path.suffix.lower() != ".xlsx":
        raise ValueError("Bản Enterprise chỉ nhận .xlsx. Hãy mở file .xls và Save As .xlsx trước khi chạy.")
    workbook_hash = file_sha256(path)
    source_id = workbook_hash[:16]
    wb = load_workbook(path, read_only=True, data_only=True, keep_links=False)
    items: list[ItemRecord] = []
    warnings: list[str] = []
    infos: list[dict[str, Any]] = []

    try:
        for ws in wb.worksheets:
            norm_sheet = normalize_name(ws.title)
            if selected_sheets is not None and ws.title not in selected_sheets:
                continue
            if selected_sheets is None and any(normalize_name(k) in norm_sheet for k in SKIP_SHEETS):
                continue

            row_iter = _iter_sheet_rows(ws)
            buffer: list[tuple[int, list[Any]]] = []
            for _ in range(80):
                try:
                    buffer.append(next(row_iter))
                except StopIteration:
                    break
            if not buffer:
                continue

            values_only = [r for _, r in buffer]
            try:
                header_start, header_end, flat_headers = detect_header(values_only)
                mapping = map_columns(flat_headers, role)
            except ValueError as exc:
                warnings.append(f"Sheet '{ws.title}': {exc}")
                continue

            if "item_name" not in mapping.values():
                warnings.append(f"Sheet '{ws.title}': không xác định được cột tên hạng mục.")
                continue

            infos.append({
                "sheet": ws.title,
                "header_start": buffer[header_start][0],
                "header_end": buffer[header_end][0],
                "mapped_columns": {flat_headers[c]: field for c, field in mapping.items()},
            })

            current_group = ""
            empty_streak = 0
            processed = 0
            for row_num, row in chain(buffer, row_iter):
                if row_num <= buffer[header_end][0]:
                    continue
                if _numbering_row(row):
                    continue
                if _row_is_empty(row):
                    empty_streak += 1
                    if empty_streak > 200:
                        break
                    continue
                empty_streak = 0
                processed += 1
                if processed > max_rows:
                    warnings.append(f"Sheet '{ws.title}' vượt giới hạn {max_rows:,} dòng và đã dừng đọc.")
                    break

                data: dict[str, Any] = {}
                for col, field in mapping.items():
                    data[field] = row[col] if col < len(row) else None

                name = _as_text(data.get("item_name"))
                code = _as_text(data.get("item_code"))
                unit = _as_text(data.get("unit"))
                quantity = parse_number(data.get("quantity"))
                unit_price = parse_number(data.get("unit_price"))
                raw_amount = parse_number(data.get("amount"))
                amount = safe_amount(quantity, unit_price, raw_amount)
                if not name and not code:
                    continue

                is_group = _looks_group(name, quantity, unit_price, raw_amount, unit)
                if is_group:
                    current_group = name

                quality_flags: list[str] = []
                if not is_group:
                    if quantity is None:
                        quality_flags.append("Thiếu khối lượng")
                    if unit_price is None:
                        quality_flags.append("Thiếu đơn giá")
                    if raw_amount is None and amount is None:
                        quality_flags.append("Thiếu thành tiền")
                    err = math_error(quantity, unit_price, raw_amount)
                    if err is not None:
                        quality_flags.append(f"Sai phép tính KL×ĐG, lệch {err:,.0f}")

                items.append(ItemRecord(
                    source_id=source_id,
                    role=role,
                    bidder=bidder or ("HSMT" if role is DocumentRole.HSMT else path.stem),
                    workbook=path.name,
                    sheet=ws.title,
                    row_number=row_num,
                    item_code=code,
                    item_name=name,
                    unit=unit,
                    quantity=quantity,
                    unit_price=unit_price,
                    amount=amount,
                    material=_as_text(data.get("material")),
                    brand=_as_text(data.get("brand")),
                    origin=_as_text(data.get("origin")),
                    note=_as_text(data.get("note")),
                    parent_group="" if is_group else current_group,
                    is_group=is_group,
                    raw={k: _as_text(v) for k, v in data.items()},
                    normalized_code=normalize_code(code),
                    normalized_name=normalize_name(f"{current_group} {name}" if current_group and not is_group else name),
                    normalized_unit=normalize_unit(unit),
                    data_quality_flags=quality_flags,
                ))
    finally:
        wb.close()

    # Duplicate codes inside the same sheet are never silently collapsed.
    duplicate_codes: dict[tuple[str, str], list[ItemRecord]] = {}
    for item in items:
        if item.is_group or not item.normalized_code:
            continue
        duplicate_codes.setdefault((item.sheet.casefold(), item.normalized_code), []).append(item)
    for (_, code), duplicated in duplicate_codes.items():
        if len(duplicated) <= 1:
            continue
        rows = ", ".join(str(x.row_number) for x in duplicated[:20])
        flag = f"Mã hiệu trùng trong cùng sheet ({code}), các dòng: {rows}"
        for item in duplicated:
            item.data_quality_flags.append(flag)
        warnings.append(f"Sheet '{duplicated[0].sheet}': {flag}")

    if not items:
        warnings.append("Không đọc được hạng mục dữ liệu nào từ workbook.")
    return WorkbookData(path=path, role=role, bidder=bidder or path.stem, items=items, warnings=warnings, sheet_info=infos)
