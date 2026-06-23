from __future__ import annotations

import argparse

from security import configure_offline_environment, deny_external_network

configure_offline_environment()

from core.config import EnterpriseConfig
from core.pipeline import compare_bidder_files
from ocr.config import OCRConfig
from ocr.pipeline import run_ocr


def _pairs(values: list[str]) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for item in values:
        if "=" not in item:
            raise argparse.ArgumentTypeError(
                "HSDT phải có dạng TênNhàThầu=duong_dan.xlsx"
            )
        name, path = item.split("=", 1)
        result.append((name.strip(), path.strip()))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="So sánh ngang hàng nhiều HSDT và OCR cục bộ"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    compare = sub.add_parser(
        "compare-bidders",
        help="So sánh 2, 3 hoặc nhiều HSDT; không có nhà thầu chuẩn",
    )
    compare.add_argument(
        "--hsdt",
        action="append",
        required=True,
        help="Tên=path.xlsx; lặp lại cho từng nhà thầu",
    )
    compare.add_argument("--output", required=True)

    ocr = sub.add_parser("ocr", help="OCR PDF/ảnh scan sang Excel kiểm chứng")
    ocr.add_argument("--input", required=True)
    ocr.add_argument("--output", required=True)

    args = parser.parse_args()
    with deny_external_network(True):
        if args.command == "compare-bidders":
            pairs = _pairs(args.hsdt)
            if len(pairs) < 2:
                parser.error("Cần ít nhất hai tham số --hsdt")
            compare_bidder_files(
                pairs,
                output_path=args.output,
                config=EnterpriseConfig.from_env(),
            )
        else:
            run_ocr(args.input, args.output, OCRConfig.from_env())
    print(f"Đã tạo: {args.output}")


if __name__ == "__main__":
    main()
