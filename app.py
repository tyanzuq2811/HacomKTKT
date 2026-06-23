from __future__ import annotations

import json
import re
import shutil
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from security import configure_offline_environment, deny_external_network

configure_offline_environment()

from core.config import EnterpriseConfig
from core.models import CompareThresholds, Severity
from core.pipeline import compare_bidder_files

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
DEFAULT_CONFIG = EnterpriseConfig.from_env()
JOBS_ROOT = (
    (BASE_DIR / DEFAULT_CONFIG.runtime_root).resolve()
    if not DEFAULT_CONFIG.runtime_root.is_absolute()
    else DEFAULT_CONFIG.runtime_root.resolve()
)
JOBS_ROOT.mkdir(parents=True, exist_ok=True)
_EXECUTOR = ThreadPoolExecutor(
    max_workers=max(1, DEFAULT_CONFIG.max_concurrent_jobs),
    thread_name_prefix="peer-compare-job",
)
_LOCK = threading.Lock()
_SAFE_FILENAME = re.compile(r"[^0-9A-Za-zÀ-ỹ._ -]+")

app = FastAPI(
    title="HSDT Peer Comparison — Standalone",
    version="7.2.0",
    description=(
        "So sánh ngang hàng 2, 3 hoặc nhiều hồ sơ dự thầu. "
        "Không lấy nhà thầu nào làm chuẩn; dữ liệu xử lý nội bộ."
    ),
)


def _job_dir(job_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{32}", job_id):
        raise HTTPException(400, "job_id không hợp lệ")
    return JOBS_ROOT / job_id


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    temporary.replace(path)


def _read_status(job_id: str) -> dict[str, Any]:
    path = _job_dir(job_id) / "status.json"
    if not path.exists():
        raise HTTPException(404, "Không tìm thấy tác vụ")
    return json.loads(path.read_text(encoding="utf-8"))


def _update(job_id: str, **changes: Any) -> None:
    with _LOCK:
        path = _job_dir(job_id) / "status.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        data.update(changes)
        data["updated_at"] = time.time()
        _atomic_json(path, data)


def _sanitize(name: str, fallback: str) -> str:
    clean = _SAFE_FILENAME.sub("_", Path(name or fallback).name).strip(" .")
    return clean[:180] or fallback


async def _save_upload(upload: UploadFile, target: Path, limit_bytes: int) -> None:
    size = 0
    with target.open("wb") as stream:
        while chunk := await upload.read(1024 * 1024):
            size += len(chunk)
            if size > limit_bytes:
                stream.close()
                target.unlink(missing_ok=True)
                raise HTTPException(
                    413,
                    f"File vượt giới hạn {limit_bytes // (1024 * 1024)} MB",
                )
            stream.write(chunk)
    await upload.close()
    if target.suffix.lower() != ".xlsx":
        target.unlink(missing_ok=True)
        raise HTTPException(400, "Giai đoạn hiện tại chỉ nhận file .xlsx")


def _build_config(payload: dict[str, Any]) -> EnterpriseConfig:
    config = EnterpriseConfig.from_env()
    config.thresholds = CompareThresholds(
        price_warn_pct=float(payload.get("price_warn_pct", 0.10)),
        price_critical_pct=float(payload.get("price_critical_pct", 0.25)),
        price_warn_abs=float(payload.get("price_warn_abs", 100_000)),
        price_critical_abs=float(payload.get("price_critical_abs", 1_000_000)),
        quantity_warn_pct=float(payload.get("quantity_warn_pct", 0.05)),
        quantity_critical_pct=float(payload.get("quantity_critical_pct", 0.15)),
        name_review_score=float(payload.get("name_review_score", 0.78)),
        name_reject_score=float(payload.get("name_reject_score", 0.58)),
    )
    return config


def _preview(result) -> dict[str, Any]:
    summary = result.summary
    groups = []
    for group in result.groups:
        if group.severity is Severity.OK:
            continue
        groups.append({
            "severity": group.severity.value,
            "score": round(group.anomaly_score, 1),
            "sheet": group.display_sheet,
            "stt": group.display_stt,
            "name": group.display_name,
            "present": list(group.members),
            "price_spread_pct": (
                group.field("Đơn giá tổng hợp").spread_pct
                if group.field("Đơn giá tổng hợp") else None
            ),
            "quantity_spread_pct": (
                group.field("Khối lượng").spread_pct
                if group.field("Khối lượng") else None
            ),
            "reasons": list(dict.fromkeys(group.reasons))[:5],
        })
        if len(groups) >= 200:
            break
    return {
        "summary": {
            "comparison_mode": "peer-to-peer-no-baseline",
            "bidder_names": summary.bidder_names,
            "bidder_count": summary.bidder_count,
            "total_groups": summary.total_groups,
            "complete_groups": summary.complete_groups,
            "partial_groups": summary.partial_groups,
            "groups_ok": summary.groups_ok,
            "groups_info": summary.groups_info,
            "groups_review": summary.groups_review,
            "groups_warning": summary.groups_warning,
            "groups_critical": summary.groups_critical,
            "flagged_fields": summary.flagged_fields,
            "bidder_totals": summary.bidder_totals,
        },
        "groups": groups,
    }


def _run_job(job_id: str, request: dict[str, Any]) -> None:
    folder = _job_dir(job_id)
    try:
        _update(job_id, state="running", progress=10, message="Đang đọc và chuẩn hóa các file Excel")
        config = _build_config(request)
        output = folder / "Bao_cao_so_sanh_ngang_hang.xlsx"
        pairs = [(entry["name"], folder / entry["file"]) for entry in request["bidders"]]
        with deny_external_network(config.strict_privacy and not config.allow_network):
            _update(job_id, progress=35, message="Đang ghép mọi cặp nhà thầu theo hai chiều")
            result = compare_bidder_files(pairs, output_path=output, config=config)
        _update(job_id, progress=85, message="Đang tạo file tổng hợp chênh lệch")
        _atomic_json(folder / "result.json", _preview(result))
        _update(
            job_id,
            state="done",
            progress=100,
            message="Đã hoàn tất so sánh ngang hàng",
            report=output.name,
        )
    except Exception as exc:  # pragma: no cover - đường lỗi vận hành
        _update(
            job_id,
            state="failed",
            progress=100,
            message=str(exc),
            error=type(exc).__name__,
        )


def _new_job() -> tuple[str, Path]:
    job_id = uuid.uuid4().hex
    folder = JOBS_ROOT / job_id
    folder.mkdir(parents=True, exist_ok=False)
    _atomic_json(folder / "status.json", {
        "job_id": job_id,
        "mode": "peer-to-peer-no-baseline",
        "state": "queued",
        "progress": 0,
        "message": "Đã tiếp nhận",
        "created_at": time.time(),
        "updated_at": time.time(),
    })
    return job_id, folder


def _cleanup_expired() -> None:
    cutoff = time.time() - DEFAULT_CONFIG.job_retention_hours * 3600
    for folder in JOBS_ROOT.iterdir():
        try:
            if folder.is_dir() and folder.stat().st_mtime < cutoff:
                shutil.rmtree(folder, ignore_errors=True)
        except OSError:
            continue


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": "7.2.0",
        "privacy": "local-only",
        "deployment": "standalone-no-docker",
        "comparison": "peer-to-peer-no-baseline",
    }


@app.post("/api/compare-bidders", status_code=202)
async def compare_bidders_api(
    files: Annotated[list[UploadFile], File(...)],
    bidder_names: Annotated[list[str], Form(...)],
    price_warn_pct: Annotated[float, Form()] = 0.10,
    price_critical_pct: Annotated[float, Form()] = 0.25,
    quantity_warn_pct: Annotated[float, Form()] = 0.05,
    quantity_critical_pct: Annotated[float, Form()] = 0.15,
):
    _cleanup_expired()
    if len(files) < 2 or len(files) != len(bidder_names):
        raise HTTPException(400, "Cần ít nhất 2 file và tên nhà thầu tương ứng")
    clean_names = [name.strip() for name in bidder_names]
    if any(not name for name in clean_names):
        raise HTTPException(400, "Tên nhà thầu không được để trống")
    if len(set(clean_names)) != len(clean_names):
        raise HTTPException(400, "Tên nhà thầu phải khác nhau")

    job_id, folder = _new_job()
    limit = DEFAULT_CONFIG.max_upload_mb * 1024 * 1024
    entries: list[dict[str, str]] = []
    try:
        for index, (upload, name) in enumerate(zip(files, clean_names)):
            filename = _sanitize(upload.filename or "", f"bidder_{index}.xlsx")
            if not filename.lower().endswith(".xlsx"):
                filename += ".xlsx"
            target = folder / f"{index:03d}_{filename}"
            await _save_upload(upload, target, limit)
            entries.append({"name": name, "file": target.name})
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise

    request = {
        "bidders": entries,
        "price_warn_pct": price_warn_pct,
        "price_critical_pct": price_critical_pct,
        "quantity_warn_pct": quantity_warn_pct,
        "quantity_critical_pct": quantity_critical_pct,
    }
    _atomic_json(folder / "request.json", request)
    _EXECUTOR.submit(_run_job, job_id, request)
    return {"job_id": job_id, "status_url": f"/api/jobs/{job_id}"}


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str):
    return _read_status(job_id)


@app.get("/api/jobs/{job_id}/result")
def job_result(job_id: str):
    folder = _job_dir(job_id)
    status = _read_status(job_id)
    if status.get("state") != "done":
        raise HTTPException(409, "Tác vụ chưa hoàn tất")
    path = folder / "result.json"
    if not path.exists():
        raise HTTPException(404, "Không có bản xem trước")
    return JSONResponse(json.loads(path.read_text(encoding="utf-8")))


@app.get("/api/jobs/{job_id}/download")
def job_download(job_id: str):
    folder = _job_dir(job_id)
    status = _read_status(job_id)
    if status.get("state") != "done":
        raise HTTPException(409, "Tác vụ chưa hoàn tất")
    report = folder / str(status.get("report", "Bao_cao_so_sanh_ngang_hang.xlsx"))
    if not report.exists():
        raise HTTPException(404, "Không tìm thấy báo cáo")
    return FileResponse(
        report,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="Bao_cao_so_sanh_ngang_hang_cac_nha_thau.xlsx",
    )


@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: str):
    folder = _job_dir(job_id)
    if not folder.exists():
        raise HTTPException(404, "Không tìm thấy tác vụ")
    shutil.rmtree(folder, ignore_errors=True)
    return {"deleted": True}


app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
