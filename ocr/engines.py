from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Protocol

import cv2
import numpy as np

from .config import OCRConfig
from .grid import make_variants
from .models import OCRCandidate


class TextEngine(Protocol):
    name: str
    def recognize(self, image: np.ndarray, numeric: bool = False) -> OCRCandidate: ...


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _clean_numeric(text: str) -> str:
    text = str(text or "").strip()
    text = text.replace("O", "0").replace("o", "0").replace("I", "1").replace("l", "1")
    text = text.replace("S", "5").replace("B", "8")
    return re.sub(r"[^0-9.,()\-+]", "", text)


class PaddleOCRv5Engine:
    name = "PP-OCRv5-local"

    def __init__(self, config: OCRConfig):
        self.model = None
        if not config.paddle_ocr_yaml or not Path(config.paddle_ocr_yaml).exists():
            return
        try:
            from paddleocr import PaddleOCR
            self.model = PaddleOCR(paddlex_config=config.paddle_ocr_yaml, device=config.device)
        except Exception:
            self.model = None

    @property
    def available(self) -> bool:
        return self.model is not None

    def recognize(self, image: np.ndarray, numeric: bool = False) -> OCRCandidate:
        if not self.model:
            return OCRCandidate("", 0.0, self.name)
        try:
            output = list(self.model.predict(input=image))
            texts, scores = [], []
            for res in output:
                data = getattr(res, "json", None)
                if callable(data):
                    data = data()
                if not isinstance(data, dict):
                    data = getattr(res, "res", None) or getattr(res, "_res", None) or {}
                # PaddleOCR 3.x nested result convention.
                root = data.get("res", data) if isinstance(data, dict) else {}
                t = root.get("rec_texts", []) or root.get("texts", [])
                s = root.get("rec_scores", []) or root.get("scores", [])
                texts.extend(map(str, t))
                scores.extend(float(x) for x in s)
            text = " ".join(texts)
            text = _clean_numeric(text) if numeric else _clean_text(text)
            conf = float(np.mean(scores)) if scores else 0.0
            return OCRCandidate(text, conf, self.name)
        except Exception:
            return OCRCandidate("", 0.0, self.name)


class TesseractEngine:
    name = "Tesseract-local"

    def __init__(self, config: OCRConfig):
        self.available = False
        try:
            import pytesseract
            if config.tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd
            _ = pytesseract.get_tesseract_version()
            self.pytesseract = pytesseract
            self.available = True
        except Exception:
            self.pytesseract = None

    def recognize(self, image: np.ndarray, numeric: bool = False) -> OCRCandidate:
        if not self.available:
            return OCRCandidate("", 0.0, self.name)
        config = "--oem 1 --psm 7"
        if numeric:
            config += " -c tessedit_char_whitelist=0123456789.,()-+"
        try:
            data = self.pytesseract.image_to_data(image, lang="vie+eng", config=config, output_type=self.pytesseract.Output.DICT)
        except Exception:
            try:
                data = self.pytesseract.image_to_data(image, lang="eng", config=config, output_type=self.pytesseract.Output.DICT)
            except Exception:
                return OCRCandidate("", 0.0, self.name)
        texts, confs = [], []
        for text, conf in zip(data.get("text", []), data.get("conf", [])):
            text = str(text).strip()
            try:
                c = float(conf)
            except Exception:
                c = -1
            if text and c >= 0:
                texts.append(text); confs.append(c / 100.0)
        text = " ".join(texts)
        text = _clean_numeric(text) if numeric else _clean_text(text)
        return OCRCandidate(text, float(np.mean(confs)) if confs else 0.0, self.name)


class OCRCellEnsemble:
    def __init__(self, config: OCRConfig):
        self.config = config
        paddle = PaddleOCRv5Engine(config)
        tesseract = TesseractEngine(config)
        self.engines: list[TextEngine] = []
        if paddle.available:
            self.engines.append(paddle)
        if tesseract.available:
            self.engines.append(tesseract)

    @property
    def available(self) -> bool:
        return bool(self.engines)

    def recognize(self, cell_image: np.ndarray, numeric: bool = False) -> tuple[OCRCandidate, list[OCRCandidate]]:
        candidates: list[OCRCandidate] = []
        for variant_name, variant in make_variants(cell_image, self.config.upscale_factor):
            for engine in self.engines:
                result = engine.recognize(variant, numeric=numeric)
                result.variant = variant_name
                if result.text:
                    candidates.append(result)
        if not candidates:
            return OCRCandidate("", 0.0, "none"), []

        # Consensus is based on exact normalized strings; confidence receives agreement bonus.
        normalize = _clean_numeric if numeric else lambda s: _clean_text(s).lower()
        groups: dict[str, list[OCRCandidate]] = {}
        for c in candidates:
            groups.setdefault(normalize(c.text), []).append(c)
        ranked = []
        for key, group in groups.items():
            base = max(group, key=lambda x: x.confidence)
            agreement = len({(x.engine, x.variant) for x in group})
            score = min(0.999, base.confidence + min(0.18, 0.04 * (agreement - 1)))
            ranked.append((agreement, score, len(key), OCRCandidate(base.text, score, base.engine, base.variant)))
        ranked.sort(reverse=True, key=lambda x: (x[0], x[1], x[2]))
        return ranked[0][3], candidates


class PaddleTableFallback:
    """Optional local PP-TableMagic fallback; never initializes without a local YAML."""
    def __init__(self, config: OCRConfig):
        self.pipeline = None
        if not config.tablemagic_yaml or not Path(config.tablemagic_yaml).exists():
            return
        try:
            from paddleocr import TableRecognitionPipelineV2
            self.pipeline = TableRecognitionPipelineV2(paddlex_config=config.tablemagic_yaml, device=config.device)
        except Exception:
            self.pipeline = None

    @property
    def available(self) -> bool:
        return self.pipeline is not None

    def predict(self, image: np.ndarray):
        if not self.pipeline:
            return []
        try:
            return list(self.pipeline.predict(image))
        except Exception:
            return []

class PaddleBatchRecognitionEngine:
    """Recognition-only PP-OCRv5 engine for already cropped cells.

    This is the fast path: hundreds of cell crops are submitted in batches instead
    of invoking the full detection pipeline once per cell.
    """
    name = "PP-OCRv5-rec-local"

    def __init__(self, config: OCRConfig):
        self.model = None
        self.config = config
        model_dir = Path(config.paddle_rec_model_dir) if config.paddle_rec_model_dir else None
        if not model_dir or not model_dir.exists():
            return
        try:
            from paddleocr import TextRecognition
            self.model = TextRecognition(
                model_name=config.paddle_rec_model_name,
                model_dir=str(model_dir),
                device=config.device,
                enable_hpi=True,
            )
        except Exception:
            self.model = None

    @property
    def available(self) -> bool:
        return self.model is not None

    def recognize_batch(self, images: list[np.ndarray], batch_size: int = 64) -> list[OCRCandidate]:
        if not self.model or not images:
            return [OCRCandidate("", 0.0, self.name) for _ in images]
        out: list[OCRCandidate] = []
        try:
            results = list(self.model.predict(input=images, batch_size=batch_size))
            for res in results:
                data = getattr(res, "json", None)
                if callable(data):
                    data = data()
                if not isinstance(data, dict):
                    data = getattr(res, "res", None) or getattr(res, "_res", None) or {}
                root = data.get("res", data) if isinstance(data, dict) else {}
                text = root.get("rec_text", "") or root.get("text", "")
                score = root.get("rec_score", 0.0) or root.get("score", 0.0)
                out.append(OCRCandidate(_clean_text(str(text)), float(score), self.name))
        except Exception:
            return [OCRCandidate("", 0.0, self.name) for _ in images]
        if len(out) < len(images):
            out.extend(OCRCandidate("", 0.0, self.name) for _ in range(len(images)-len(out)))
        return out[:len(images)]


class FastCellRecognizer:
    """Two-stage local ensemble: batched Paddle first, Tesseract only for uncertain cells."""

    def __init__(self, config: OCRConfig):
        self.config = config
        self.batch = PaddleBatchRecognitionEngine(config)
        self.tesseract = TesseractEngine(config)
        self.slow = OCRCellEnsemble(config)

    @property
    def available(self) -> bool:
        return self.batch.available or self.slow.available

    def recognize_many(self, cell_images: list[np.ndarray], numeric_flags: list[bool]) -> list[tuple[OCRCandidate, list[OCRCandidate]]]:
        if not cell_images:
            return []
        # One high-quality grayscale crop per cell for the fast batch pass.
        primary = []
        for img in cell_images:
            variants = make_variants(img, self.config.upscale_factor)
            primary.append(variants[1][1] if len(variants) > 1 else variants[0][1] if variants else img)
        if self.batch.available:
            batch_results = self.batch.recognize_batch(primary, batch_size=64)
        elif self.tesseract.available:
            batch_results = [self.tesseract.recognize(img, numeric=flag) for img, flag in zip(primary, numeric_flags)]
        else:
            batch_results = [OCRCandidate("", 0.0, "none") for _ in primary]
        outputs: list[tuple[OCRCandidate, list[OCRCandidate]]] = []
        for img, numeric, first in zip(cell_images, numeric_flags, batch_results):
            if numeric:
                first.text = _clean_numeric(first.text)
            threshold = self.config.min_numeric_confidence if numeric else self.config.min_text_confidence
            if first.text and first.confidence >= threshold:
                outputs.append((first, [first]))
                continue
            # Expensive multi-variant ensemble runs only for uncertain cells.
            best, candidates = self.slow.recognize(img, numeric=numeric)
            if first.text:
                candidates.append(first)
                if first.confidence > best.confidence:
                    best = first
            outputs.append((best, candidates))
        return outputs
