from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class OCRConfig:
    strict_privacy: bool = True
    device: str = "gpu:0"
    render_dpi: int = 300
    upscale_factor: float = 3.0
    max_pages: int = 500
    min_cell_width: int = 8
    min_cell_height: int = 6
    min_text_confidence: float = 0.72
    min_numeric_confidence: float = 0.80
    math_tolerance_pct: float = 0.005
    orientation_with_tesseract: bool = True
    use_grid_first: bool = True
    use_tablemagic_fallback: bool = True
    use_paddle_vl_fallback: bool = True
    workers: int = 1
    paddle_ocr_yaml: str = ""
    paddle_rec_model_dir: str = ""
    paddle_rec_model_name: str = "latin_PP-OCRv5_mobile_rec"
    tablemagic_yaml: str = ""
    ppstructure_yaml: str = ""
    paddle_vl_yaml: str = ""
    tesseract_cmd: str = ""
    debug_dir: str = ""

    @classmethod
    def from_env(cls) -> "OCRConfig":
        return cls(
            strict_privacy=os.getenv("HSMT_STRICT_PRIVACY", "1") != "0",
            device=os.getenv("HSMT_OCR_DEVICE", "gpu:0"),
            render_dpi=int(os.getenv("HSMT_OCR_DPI", "300")),
            upscale_factor=float(os.getenv("HSMT_OCR_UPSCALE", "3")),
            max_pages=int(os.getenv("HSMT_MAX_PDF_PAGES", "500")),
            workers=int(os.getenv("HSMT_OCR_WORKERS", "1")),
            paddle_ocr_yaml=os.getenv("HSMT_PADDLE_OCR_YAML", ""),
            paddle_rec_model_dir=os.getenv("HSMT_PADDLE_REC_MODEL_DIR", ""),
            paddle_rec_model_name=os.getenv("HSMT_PADDLE_REC_MODEL_NAME", "latin_PP-OCRv5_mobile_rec"),
            tablemagic_yaml=os.getenv("HSMT_TABLEMAGIC_YAML", ""),
            ppstructure_yaml=os.getenv("HSMT_PPSTRUCTURE_YAML", ""),
            paddle_vl_yaml=os.getenv("HSMT_PADDLE_VL_YAML", ""),
            tesseract_cmd=os.getenv("TESSERACT_CMD", ""),
            debug_dir=os.getenv("HSMT_OCR_DEBUG_DIR", ""),
        )

    def validate_local_models(self) -> list[str]:
        warnings = []
        for label, path in [
            ("PP-OCRv5 pipeline", self.paddle_ocr_yaml),
            ("PP-OCRv5 recognition", self.paddle_rec_model_dir),
            ("PP-TableMagic", self.tablemagic_yaml),
            ("PP-StructureV3", self.ppstructure_yaml),
            ("PaddleOCR-VL", self.paddle_vl_yaml),
        ]:
            if path and not Path(path).exists():
                warnings.append(f"{label}: không tìm thấy cấu hình local '{path}'")
        return warnings
