from __future__ import annotations

import argparse
from pathlib import Path

from security import configure_offline_environment, deny_external_network

configure_offline_environment()

from core.config import EnterpriseConfig
from core.pipeline import compare_bidder_files, compare_tender_files
from ocr.config import OCRConfig
from ocr.pipeline import run_ocr


def _pairs(values: list[str]) -> list[tuple[str, str]]:
    result = []
    for item in values:
        if "=" not in item:
            raise argparse.ArgumentTypeError("HSDT phải có dạng TênNhàThầu=duong_dan.xlsx")
        name, path = item.split("=", 1)
        result.append((name.strip(), path.strip()))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="HSMT Enterprise AI — xử lý hoàn toàn nội bộ")
    sub = parser.add_subparsers(dest="command", required=True)

    p1 = sub.add_parser("compare", help="So sánh HSMT với một hoặc nhiều HSDT")
    p1.add_argument("--hsmt", required=True)
    p1.add_argument("--hsdt", action="append", required=True, help="Tên=path.xlsx; lặp lại nhiều lần")
    p1.add_argument("--output", required=True)

    p2 = sub.add_parser("compare-bidders", help="So sánh nhiều HSDT với nhau")
    p2.add_argument("--hsdt", action="append", required=True, help="Tên=path.xlsx; lặp lại nhiều lần")
    p2.add_argument("--output", required=True)

    p3 = sub.add_parser("ocr", help="OCR PDF/ảnh scan sang Excel kiểm chứng")
    p3.add_argument("--input", required=True)
    p3.add_argument("--output", required=True)

    args = parser.parse_args()
    with deny_external_network(True):
        if args.command == "compare":
            compare_tender_files(args.hsmt, _pairs(args.hsdt), args.output, EnterpriseConfig.from_env())
        elif args.command == "compare-bidders":
            compare_bidder_files(_pairs(args.hsdt), args.output, EnterpriseConfig.from_env())
        else:
            run_ocr(args.input, args.output, OCRConfig.from_env())
    print(f"Đã tạo: {args.output}")


if __name__ == "__main__":
    main()
