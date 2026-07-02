from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from .advisor import PriceAdvisor
from .config import PriceAdvisorConfig
from .hacom_excel import export_references_csv, extract_hacom_references
from .rag_store import ChromaPriceStore, load_references_from_csv
from .schemas import AdvisorError, PriceSuggestion


def _setup_logging() -> None:
    # Force UTF-8 on Windows console (cp1252 would crash on Vietnamese text)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )


def _run_benchmark(config: PriceAdvisorConfig, csv_path: str, n: int, seed: int, wandb_project: str | None = None) -> None:
    """Benchmark: pick N random items from CSV, run suggest on each, report stats."""
    refs = load_references_from_csv(csv_path)
    if not refs:
        print(json.dumps({"error": "CSV rỗng hoặc không đọc được"}, ensure_ascii=False))
        return

    random.seed(seed)
    samples = random.sample(refs, min(n, len(refs)))
    advisor = PriceAdvisor(config)

    results: list[dict] = []
    total_latency = 0.0
    success_count = 0
    error_count = 0

    print(f"Benchmark: {len(samples)} items | backend={config.llm_backend}", file=sys.stderr)
    print("-" * 70, file=sys.stderr)

    for index, ref in enumerate(samples, start=1):
        t0 = time.perf_counter()
        while True:
            try:
                result = advisor.suggest_price(ref.description, ref.unit)
                break
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "Quota exceeded" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    print(f"  [Rate Limit 429] Nghỉ 30 giây rồi thử lại...", file=sys.stderr)
                    time.sleep(30)
                else:
                    from .schemas import AdvisorError
                    result = AdvisorError(error=err_msg, description=ref.description, unit=ref.unit)
                    break
        elapsed = time.perf_counter() - t0
        total_latency += elapsed

        entry: dict = {
            "index": index,
            "description": ref.description[:80],
            "unit": ref.unit,
            "actual_price": int(round(ref.price)),
            "latency_seconds": round(elapsed, 3),
        }

        if isinstance(result, PriceSuggestion):
            success_count += 1
            actual_rounded = int(round(ref.price))
            in_range = result.price_low <= actual_rounded <= result.price_high
            entry.update({
                "status": "ok",
                "price_low": result.price_low,
                "price_high": result.price_high,
                "confidence": result.confidence,
                "actual_in_range": in_range,
                "reasoning": result.reasoning[:120],
                "warnings": result.warnings,
            })
            marker = "✅" if in_range else "⚠️"
            print(
                f"  [{index}/{len(samples)}] {marker} {ref.description[:50]} | "
                f"{result.price_low:,}-{result.price_high:,} vs actual {int(ref.price):,} | "
                f"{elapsed:.2f}s",
                file=sys.stderr,
            )
        else:
            error_count += 1
            entry.update({"status": "error", "error": result.error})
            print(
                f"  [{index}/{len(samples)}] ❌ {ref.description[:50]} | {result.error} | {elapsed:.2f}s",
                file=sys.stderr,
            )

        results.append(entry)
        
        # Ngăn chặn lỗi Rate Limit 429 (Quá tải API) của Google Gemini Free Tier
        if config.llm_backend == "gemini":
            time.sleep(4)

    # Aggregate stats
    avg_latency = total_latency / len(samples) if samples else 0
    in_range_count = sum(1 for r in results if r.get("actual_in_range") is True)
    accuracy_pct = (in_range_count / success_count * 100) if success_count else 0

    summary = {
        "backend": config.llm_backend,
        "model": config.ollama_model if config.llm_backend == "ollama" else config.gemini_model,
        "total_items": len(samples),
        "success": success_count,
        "errors": error_count,
        "actual_in_range": in_range_count,
        "accuracy_pct": round(accuracy_pct, 1),
        "total_latency_seconds": round(total_latency, 3),
        "avg_latency_seconds": round(avg_latency, 3),
        "items": results,
    }

    if wandb_project:
        try:
            import wandb
            wandb.init(
                project=wandb_project,
                config={
                    "backend": summary["backend"],
                    "model": summary["model"],
                    "n_samples": n,
                    "seed": seed,
                },
                name=f"{summary['backend']}-{int(time.time())}"
            )
            # Tạo bảng trực quan trên wandb
            columns = ["Mô tả", "Đơn vị", "Giá thực tế", "Gợi ý thấp", "Gợi ý cao", "Đúng khoảng?", "Latency (s)", "Lập luận"]
            table = wandb.Table(columns=columns)
            
            for r in results:
                table.add_data(
                    r.get("description", ""),
                    r.get("unit", ""),
                    r.get("actual_price", 0),
                    r.get("price_low", 0),
                    r.get("price_high", 0),
                    r.get("actual_in_range", False),
                    r.get("latency_seconds", 0),
                    r.get("reasoning", r.get("error", ""))
                )
            
            # Gửi lên wandb
            wandb.log({
                "accuracy_pct": summary["accuracy_pct"],
                "avg_latency": summary["avg_latency_seconds"],
                "success_count": summary["success"],
                "error_count": summary["errors"],
                "benchmark_results": table
            })
            wandb.finish()
            print(f"\n[WANDB] Đã đồng bộ báo cáo trực quan lên dự án: {wandb_project}", file=sys.stderr)
        except ImportError:
            print("\n[WANDB] Lỗi: Chưa cài đặt wandb. Chạy 'pip install wandb' để dùng tính năng này.", file=sys.stderr)
        except Exception as e:
            print(f"\n[WANDB] Lỗi khi đồng bộ: {e}", file=sys.stderr)

    print("\n" + "=" * 70, file=sys.stderr)
    print(
        f"  Backend: {summary['backend']} ({summary['model']})\n"
        f"  Items: {summary['total_items']} | Success: {summary['success']} | Errors: {summary['errors']}\n"
        f"  Actual price in suggested range: {in_range_count}/{success_count} ({accuracy_pct:.1f}%)\n"
        f"  Avg latency: {avg_latency:.3f}s | Total: {total_latency:.1f}s",
        file=sys.stderr,
    )
    print("=" * 70, file=sys.stderr)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> None:
    load_dotenv(Path(".env"), override=False)
    _setup_logging()
    parser = argparse.ArgumentParser(description="Standalone PriceAdvisor RAG + LLM")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="Nạp CSV giá lịch sử vào ChromaDB")
    ingest.add_argument("--csv", required=True)

    extract_hacom = sub.add_parser("extract-hacom", help="Trích dữ liệu giá từ folder HACOM_DATA ra CSV chuẩn RAG")
    extract_hacom.add_argument("--data-dir", required=True)
    extract_hacom.add_argument("--output", required=True)

    ingest_hacom = sub.add_parser("ingest-hacom", help="Trích và nạp dữ liệu giá từ folder HACOM_DATA vào ChromaDB")
    ingest_hacom.add_argument("--data-dir", required=True)

    suggest = sub.add_parser("suggest", help="Gợi ý khoảng đơn giá")
    suggest.add_argument("--desc", required=True)
    suggest.add_argument("--unit", required=True)
    suggest.add_argument("--qty", type=float)
    suggest.add_argument("--top-k", type=int)

    bench = sub.add_parser("benchmark", help="Benchmark: chạy suggest cho N dòng ngẫu nhiên từ CSV, đo latency + accuracy")
    bench.add_argument("--csv", required=True, help="CSV nguồn (ví dụ runtime/hacom_price_refs.csv)")
    bench.add_argument("-n", type=int, default=20, help="Số dòng test (mặc định 20)")
    bench.add_argument("--seed", type=int, default=42, help="Random seed để tái tạo kết quả")
    bench.add_argument("--wandb", dest="wandb_project", type=str, help="Tên dự án wandb để xuất biểu đồ (VD: price-advisor-eval)")

    serve = sub.add_parser("serve", help="Khởi động Web UI test trên FastAPI")
    serve.add_argument("--host", default="127.0.0.1", help="Host address (mặc định 127.0.0.1)")
    serve.add_argument("--port", type=int, default=8000, help="Port (mặc định 8000)")

    args = parser.parse_args()
    config = PriceAdvisorConfig.from_env()

    if args.command == "ingest":
        store = ChromaPriceStore(config)
        refs = load_references_from_csv(args.csv)
        count = store.add_references(refs)
        print(json.dumps({"ingested": count, "db_dir": str(config.db_dir)}, ensure_ascii=False, indent=2))
        return

    if args.command == "extract-hacom":
        refs = extract_hacom_references(args.data_dir)
        count = export_references_csv(refs, args.output)
        print(json.dumps({"extracted": count, "output": args.output}, ensure_ascii=False, indent=2))
        return

    if args.command == "ingest-hacom":
        refs = extract_hacom_references(args.data_dir)
        store = ChromaPriceStore(config)
        count = store.add_references(refs)
        print(json.dumps({"ingested": count, "db_dir": str(config.db_dir)}, ensure_ascii=False, indent=2))
        return

    if args.command == "benchmark":
        _run_benchmark(config, args.csv, args.n, args.seed, args.wandb_project)
        return

    if args.command == "serve":
        import uvicorn
        print(f"Starting server at http://{args.host}:{args.port}")
        uvicorn.run("price_advisor.server:app", host=args.host, port=args.port)
        return

    advisor = PriceAdvisor(config)
    result = advisor.suggest_price(args.desc, args.unit, quantity=args.qty, top_k=args.top_k)
    if isinstance(result, AdvisorError):
        print(result.model_dump_json(indent=2))
    else:
        print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
