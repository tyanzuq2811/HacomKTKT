from __future__ import annotations

import hashlib
import os
from pathlib import Path

from core.config import EnterpriseConfig
from ocr.config import OCRConfig


def hash_tree(root: Path) -> tuple[int, str]:
    h = hashlib.sha256(); count = 0
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        count += 1
        h.update(str(path.relative_to(root)).encode())
        with path.open("rb") as f:
            while chunk := f.read(1024 * 1024):
                h.update(chunk)
    return count, h.hexdigest()


def main():
    cfg = EnterpriseConfig.from_env(); ocr = OCRConfig.from_env()
    paths = {
        "BGE-M3": cfg.embedding_model_path,
        "PP-OCRv5 rec": ocr.paddle_rec_model_dir,
        "OCR YAML": ocr.paddle_ocr_yaml,
        "TableMagic YAML": ocr.tablemagic_yaml,
        "PP-Structure YAML": ocr.ppstructure_yaml,
        "PaddleOCR-VL YAML": ocr.paddle_vl_yaml,
    }
    failed = False
    for label, raw in paths.items():
        if not raw:
            print(f"[SKIP] {label}: chưa cấu hình")
            continue
        path = Path(raw)
        if not path.exists():
            print(f"[FAIL] {label}: {path}"); failed = True; continue
        if path.is_dir():
            count, digest = hash_tree(path)
            print(f"[OK] {label}: {count} files, tree-sha256={digest}")
        else:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            print(f"[OK] {label}: sha256={digest}")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
