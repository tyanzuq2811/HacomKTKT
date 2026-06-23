from __future__ import annotations

from pathlib import Path
from typing import Iterable

import cv2
import fitz
import numpy as np

from .config import OCRConfig
from .models import OCRPage


def _pixmap_to_bgr(pix: fitz.Pixmap) -> np.ndarray:
    channels = pix.n
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, channels)
    if channels == 4:
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    if channels == 3:
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    return cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)


def _dominant_embedded_image(doc: fitz.Document, page: fitz.Page) -> np.ndarray | None:
    images = page.get_images(full=True)
    best = None
    best_pixels = 0
    for image in images:
        xref = image[0]
        try:
            info = doc.extract_image(xref)
            data = np.frombuffer(info["image"], dtype=np.uint8)
            img = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if img is None:
                continue
            pixels = img.shape[0] * img.shape[1]
            if pixels > best_pixels:
                best, best_pixels = img, pixels
        except Exception:
            continue
    return best if best_pixels >= 800_000 else None


def load_pages(path: str | Path, config: OCRConfig) -> list[OCRPage]:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}:
        img = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Không đọc được ảnh: {path}")
        oriented, rotation = normalize_orientation(img, config)
        return [OCRPage(page=1, image=oriented, rotation=rotation, source="image")]
    if suffix != ".pdf":
        raise ValueError("OCR hỗ trợ PDF hoặc ảnh PNG/JPG/TIFF.")

    doc = fitz.open(path)
    pages: list[OCRPage] = []
    try:
        if len(doc) > config.max_pages:
            raise ValueError(f"PDF có {len(doc)} trang, vượt giới hạn {config.max_pages} trang.")
        for page_idx, page in enumerate(doc):
            embedded = _dominant_embedded_image(doc, page)
            if embedded is not None:
                img = embedded
                source = "embedded-image"
            else:
                zoom = config.render_dpi / 72.0
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
                img = _pixmap_to_bgr(pix)
                source = f"render-{config.render_dpi}dpi"
            oriented, rotation = normalize_orientation(img, config)
            pages.append(OCRPage(page=page_idx + 1, image=oriented, rotation=rotation, source=source))
    finally:
        doc.close()
    return pages


def rotate_image(image: np.ndarray, angle: int) -> np.ndarray:
    angle %= 360
    if angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    if angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    if angle == 270:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return image.copy()


def _line_score(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    h, w = bw.shape
    hk = cv2.getStructuringElement(cv2.MORPH_RECT, (max(20, w // 35), 1))
    vk = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(20, h // 35)))
    horizontal = cv2.morphologyEx(bw, cv2.MORPH_OPEN, hk)
    vertical = cv2.morphologyEx(bw, cv2.MORPH_OPEN, vk)
    density = (np.count_nonzero(horizontal) + np.count_nonzero(vertical)) / max(h * w, 1)
    landscape_bonus = 0.02 if w >= h else 0.0
    return float(density + landscape_bonus)


def _tesseract_osd_rotation(image: np.ndarray, config: OCRConfig) -> int | None:
    if not config.orientation_with_tesseract:
        return None
    try:
        import pytesseract
        if config.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd
        sample = image
        max_side = max(sample.shape[:2])
        if max_side > 2200:
            scale = 2200 / max_side
            sample = cv2.resize(sample, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        osd = pytesseract.image_to_osd(sample, output_type=pytesseract.Output.DICT)
        # rotate value is how much clockwise rotation Tesseract recommends.
        return int(osd.get("rotate", 0)) % 360
    except Exception:
        return None


def normalize_orientation(image: np.ndarray, config: OCRConfig) -> tuple[np.ndarray, int]:
    osd = _tesseract_osd_rotation(image, config)
    if osd in {0, 90, 180, 270}:
        oriented = rotate_image(image, osd)
        # Reject OSD result if table geometry is substantially worse.
        if _line_score(oriented) >= 0.75 * max(_line_score(rotate_image(image, a)) for a in (0, 90, 180, 270)):
            return oriented, osd

    scored = [(a, _line_score(rotate_image(image, a))) for a in (0, 90, 180, 270)]
    # Geometry cannot distinguish 0/180; deterministic preference is acceptable,
    # and the OCR ensemble can later retry 180 for a low-confidence header.
    angle = max(scored, key=lambda x: (x[1], -x[0]))[0]
    return rotate_image(image, angle), angle
