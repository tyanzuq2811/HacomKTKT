from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np

from .config import OCRConfig
from .models import OCRCell, OCRTable


@dataclass(slots=True)
class GridDetection:
    bbox: tuple[int, int, int, int]
    x_lines: list[int]
    y_lines: list[int]
    confidence: float
    horizontal_mask: np.ndarray
    vertical_mask: np.ndarray


def _binarize(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    # A mild contrast enhancement preserves tiny punctuation better than aggressive denoising.
    clahe = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 12)


def _merge_positions(values: Iterable[int], tolerance: int = 4) -> list[int]:
    values = sorted(int(v) for v in values)
    if not values:
        return []
    groups = [[values[0]]]
    for v in values[1:]:
        if v - groups[-1][-1] <= tolerance:
            groups[-1].append(v)
        else:
            groups.append([v])
    return [int(round(sum(g) / len(g))) for g in groups]


def _projection_lines(mask: np.ndarray, axis: int, min_ratio: float) -> list[int]:
    # axis=0 -> x positions using vertical mask; axis=1 -> y positions using horizontal mask.
    projection = np.count_nonzero(mask, axis=axis)
    span = mask.shape[axis]
    threshold = max(3, int(span * min_ratio))
    idx = np.where(projection >= threshold)[0]
    return _merge_positions(idx.tolist(), tolerance=max(2, int(min(mask.shape) * 0.0015)))


def detect_grid(image: np.ndarray, config: OCRConfig) -> GridDetection | None:
    bw = _binarize(image)
    h, w = bw.shape
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(25, w // 45), 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(20, h // 45)))
    horizontal = cv2.morphologyEx(bw, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    vertical = cv2.morphologyEx(bw, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
    grid = cv2.bitwise_or(horizontal, vertical)
    grid = cv2.morphologyEx(grid, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

    contours, _ = cv2.findContours(grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for contour in contours:
        x, y, ww, hh = cv2.boundingRect(contour)
        area_ratio = (ww * hh) / max(w * h, 1)
        if area_ratio >= 0.12 and ww >= 0.35 * w and hh >= 0.25 * h:
            candidates.append((area_ratio, x, y, ww, hh))
    if not candidates:
        # Fallback to all detected line pixels.
        pts = cv2.findNonZero(grid)
        if pts is None:
            return None
        x, y, ww, hh = cv2.boundingRect(pts)
    else:
        _, x, y, ww, hh = max(candidates)

    # Expand slightly to retain border strokes.
    pad = max(2, int(min(w, h) * 0.003))
    x = max(0, x - pad); y = max(0, y - pad)
    ww = min(w - x, ww + 2 * pad); hh = min(h - y, hh + 2 * pad)
    h_roi = horizontal[y:y+hh, x:x+ww]
    v_roi = vertical[y:y+hh, x:x+ww]

    x_lines = _projection_lines(v_roi, axis=0, min_ratio=0.25)
    y_lines = _projection_lines(h_roi, axis=1, min_ratio=0.12)
    # Add outer boundaries when morphology missed a faint edge.
    if x_lines and x_lines[0] > 10:
        x_lines.insert(0, 0)
    if x_lines and ww - x_lines[-1] > 10:
        x_lines.append(ww - 1)
    if y_lines and y_lines[0] > 10:
        y_lines.insert(0, 0)
    if y_lines and hh - y_lines[-1] > 10:
        y_lines.append(hh - 1)

    x_lines = [p for i, p in enumerate(x_lines) if i == 0 or p - x_lines[i-1] >= config.min_cell_width]
    y_lines = [p for i, p in enumerate(y_lines) if i == 0 or p - y_lines[i-1] >= config.min_cell_height]
    if len(x_lines) < 4 or len(y_lines) < 4:
        return None

    intersections = cv2.bitwise_and(h_roi, v_roi)
    expected = len(x_lines) * len(y_lines)
    actual = len(cv2.findNonZero(intersections)) if cv2.findNonZero(intersections) is not None else 0
    # Pixel intersections are thick; normalize conservatively and mix topology score.
    topology = min(1.0, (len(x_lines) / 10.0) * (len(y_lines) / 20.0))
    density = np.count_nonzero(grid[y:y+hh, x:x+ww]) / max(ww * hh, 1)
    confidence = float(np.clip(0.65 * topology + 0.35 * min(1.0, density / 0.08), 0, 1))
    return GridDetection((x, y, ww, hh), x_lines, y_lines, confidence, h_roi, v_roi)


def remove_borders(cell: np.ndarray) -> np.ndarray:
    if cell.size == 0:
        return cell
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY) if cell.ndim == 3 else cell.copy()
    h, w = gray.shape
    margin_x = max(1, int(w * 0.025)); margin_y = max(1, int(h * 0.08))
    gray[:margin_y, :] = 255; gray[-margin_y:, :] = 255
    gray[:, :margin_x] = 255; gray[:, -margin_x:] = 255
    return gray


def make_variants(cell: np.ndarray, upscale: float) -> list[tuple[str, np.ndarray]]:
    gray = remove_borders(cell)
    if gray.size == 0:
        return []
    gray = cv2.copyMakeBorder(gray, 8, 8, 12, 12, cv2.BORDER_CONSTANT, value=255)
    interp = cv2.INTER_CUBIC if upscale > 1 else cv2.INTER_AREA
    up = cv2.resize(gray, None, fx=upscale, fy=upscale, interpolation=interp)
    clahe = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(8, 8)).apply(up)
    binary = cv2.adaptiveThreshold(clahe, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 12)
    otsu = cv2.threshold(clahe, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return [("gray", up), ("clahe", clahe), ("adaptive", binary), ("otsu", otsu)]


def build_table(page_number: int, image: np.ndarray, detection: GridDetection, config: OCRConfig, debug_dir: str = "") -> OCRTable:
    x0, y0, w, h = detection.bbox
    table = OCRTable(
        page=page_number,
        bbox=detection.bbox,
        x_lines=detection.x_lines,
        y_lines=detection.y_lines,
        structure_confidence=detection.confidence,
    )
    roi = image[y0:y0+h, x0:x0+w]
    debug_root = Path(debug_dir) if debug_dir else None
    if debug_root:
        debug_root.mkdir(parents=True, exist_ok=True)

    for r in range(len(detection.y_lines) - 1):
        y1, y2 = detection.y_lines[r], detection.y_lines[r+1]
        for c in range(len(detection.x_lines) - 1):
            x1, x2 = detection.x_lines[c], detection.x_lines[c+1]
            if x2 - x1 < config.min_cell_width or y2 - y1 < config.min_cell_height:
                continue
            pad_x = max(1, int((x2-x1)*0.025)); pad_y = max(1, int((y2-y1)*0.06))
            crop = roi[max(0,y1+pad_y):min(h,y2-pad_y), max(0,x1+pad_x):min(w,x2-pad_x)]
            cell = OCRCell(page=page_number, row=r, col=c, bbox=(x0+x1, y0+y1, x2-x1, y2-y1))
            if debug_root and crop.size:
                path = debug_root / f"p{page_number:03d}_r{r:04d}_c{c:03d}.png"
                cv2.imwrite(str(path), crop)
                cell.image_path = str(path)
            table.cells.append(cell)
    return table


def crop_cell(image: np.ndarray, cell: OCRCell) -> np.ndarray:
    x, y, w, h = cell.bbox
    return image[y:y+h, x:x+w]
