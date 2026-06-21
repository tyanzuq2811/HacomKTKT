from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable, Optional

import cv2
import numpy as np

from core.excel_reader import file_sha256

from .config import OCRConfig
from .engines import FastCellRecognizer, PaddleTableFallback
from .exporter import export_ocr_document
from .grid import build_table, crop_cell, detect_grid
from .models import OCRDocument, OCRPage, OCRTable
from .pdf_io import load_pages, rotate_image
from .schema import infer_columns, infer_header_rows, is_numeric_field
from .verify import assemble_rows, update_cell_status


def _ink_ratio(image: np.ndarray) -> float:
    if image.size == 0:
        return 0.0
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return float(np.count_nonzero(bw) / max(bw.size, 1))


def _recognize_header(table: OCRTable, image: np.ndarray, recognizer: FastCellRecognizer, config: OCRConfig) -> float:
    header_cells = [c for c in table.cells if c.row < table.header_rows]
    crops = [crop_cell(image, c) for c in header_cells]
    outputs = recognizer.recognize_many(crops, [False] * len(crops))
    confidences = []
    for cell, (best, candidates) in zip(header_cells, outputs):
        cell.text = best.text
        cell.confidence = best.confidence
        cell.engine = best.engine
        cell.candidates = candidates
        update_cell_status(cell, config, numeric=False)
        if best.text:
            confidences.append(best.confidence)
    infer_columns(table)
    recognized_fields = len(set(table.column_fields.values()))
    return table.structure_confidence + recognized_fields * 0.25 + (float(np.mean(confidences)) if confidences else 0.0)


def _candidate_table(page_number: int, image: np.ndarray, recognizer: FastCellRecognizer, config: OCRConfig, debug_dir: str) -> tuple[OCRTable | None, float]:
    detection = detect_grid(image, config)
    if detection is None:
        return None, -1.0
    table = build_table(page_number, image, detection, config, debug_dir=debug_dir)
    table.header_rows = infer_header_rows(table)
    score = _recognize_header(table, image, recognizer, config)
    return table, score


def _select_orientation_and_table(page: OCRPage, recognizer: FastCellRecognizer, config: OCRConfig) -> OCRTable | None:
    # Geometry can distinguish portrait/landscape but not always 0 vs 180. Compare both
    # using recognized header fields, so upside-down scans are corrected without cloud APIs.
    attempts = [(page.image, 0), (rotate_image(page.image, 180), 180)]
    best_table = None
    best_image = page.image
    best_extra_rotation = 0
    best_score = -1.0
    for image, extra in attempts:
        debug_dir = ""
        if config.debug_dir:
            debug_dir = str(Path(config.debug_dir) / f"page_{page.page:03d}_rot_{extra}")
        table, score = _candidate_table(page.page, image, recognizer, config, debug_dir)
        if table is not None and score > best_score:
            best_table, best_image, best_extra_rotation, best_score = table, image, extra, score
    if best_table is not None:
        page.image = best_image
        page.rotation = (page.rotation + best_extra_rotation) % 360
    return best_table


def _recognize_data_cells(page: OCRPage, table: OCRTable, recognizer: FastCellRecognizer, config: OCRConfig) -> None:
    cells = [c for c in table.cells if c.row >= table.header_rows]
    work_cells = []
    crops = []
    numeric_flags = []
    for cell in cells:
        crop = crop_cell(page.image, cell)
        # Blank cells dominate BOQ documents; skipping them is the main speed gain.
        if _ink_ratio(crop) < 0.006:
            cell.text = ""
            cell.confidence = 1.0
            cell.engine = "blank-detector"
            cell.status = "empty"
            continue
        field = table.column_fields.get(cell.col, f"col_{cell.col+1}")
        cell.field = field
        work_cells.append(cell)
        crops.append(crop)
        numeric_flags.append(is_numeric_field(field))

    outputs = recognizer.recognize_many(crops, numeric_flags)
    for cell, numeric, (best, candidates) in zip(work_cells, numeric_flags, outputs):
        cell.text = best.text
        cell.confidence = best.confidence
        cell.engine = best.engine
        cell.candidates = candidates
        update_cell_status(cell, config, numeric=numeric)


def _process_page(page: OCRPage, recognizer: FastCellRecognizer, table_fallback: PaddleTableFallback, config: OCRConfig) -> list[dict]:
    table = _select_orientation_and_table(page, recognizer, config)
    if table is None:
        page.warnings.append("Không phát hiện được lưới bảng bằng OpenCV.")
        if table_fallback.available:
            results = table_fallback.predict(page.image)
            page.warnings.append(f"PP-TableMagic trả {len(results)} kết quả; cần cấu hình bộ chuyển đổi custom nếu bảng không có lưới.")
        return []

    if len(table.column_fields) < 3:
        table.warnings.append("Nhận diện tiêu đề yếu: xác định dưới 3 trường chuẩn.")
    _recognize_data_cells(page, table, recognizer, config)
    page.tables.append(table)
    return assemble_rows(table, config)


def run_ocr(
    input_path: str | Path,
    output_path: str | Path | None = None,
    config: Optional[OCRConfig] = None,
) -> OCRDocument:
    config = config or OCRConfig.from_env()
    input_path = Path(input_path)
    if input_path.stat().st_size > 2 * 1024**3:
        raise ValueError("Tệp vượt giới hạn an toàn 2 GB.")

    pages = load_pages(input_path, config)
    recognizer = FastCellRecognizer(config)
    if not recognizer.available:
        raise RuntimeError(
            "Không có OCR engine local. Hãy cấu hình HSMT_PADDLE_REC_MODEL_DIR "
            "(khuyến nghị PP-OCRv5 local) hoặc cài Tesseract trên máy nội bộ."
        )
    fallback = PaddleTableFallback(config)
    all_rows: list[dict] = []
    warnings = config.validate_local_models()
    for page in pages:
        all_rows.extend(_process_page(page, recognizer, fallback, config))
        warnings.extend(f"Trang {page.page}: {w}" for w in page.warnings)
        for table in page.tables:
            warnings.extend(f"Trang {page.page}: {w}" for w in table.warnings)

    audit = {
        "privacy_mode": "STRICT_LOCAL" if config.strict_privacy else "LOCAL",
        "network_calls": 0,
        "source_sha256": file_sha256(input_path),
        "device": config.device,
        "render_dpi": config.render_dpi,
        "upscale_factor": config.upscale_factor,
        "ocr_fast_path": "PP-OCRv5 recognition-only batched" if config.paddle_rec_model_dir else "Tesseract local fallback",
        "table_method": "OpenCV grid-first + optional PP-TableMagic local fallback",
        "pages": len(pages),
    }
    doc = OCRDocument(input_path, pages, all_rows, warnings=warnings, audit=audit)
    if output_path:
        export_ocr_document(doc, output_path)
    return doc


def run_ocr_batch(files: Iterable[str | Path], output_dir: str | Path, config: Optional[OCRConfig] = None) -> list[OCRDocument]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    documents = []
    for path in files:
        path = Path(path)
        out = output_dir / f"{path.stem}_OCR.xlsx"
        documents.append(run_ocr(path, out, config=config))
    return documents
