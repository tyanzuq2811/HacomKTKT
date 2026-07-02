import os
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .advisor import PriceAdvisor
from .config import PriceAdvisorConfig
from .schemas import AdvisorError, PriceSuggestion

app = FastAPI(title="Price Advisor Test UI")

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"
WEB_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


class SuggestRequest(BaseModel):
    description: str
    unit: str
    backend: str = "ollama"
    top_k: int = 5


# W&B Globals
wandb_run = None
wandb_table = None

@app.on_event("startup")
def startup_event():
    global wandb_run, wandb_table
    try:
        import wandb
        # Chỉ bật W&B nếu môi trường cho phép hoặc đang đăng nhập
        if wandb.api.api_key:
            wandb_run = wandb.init(project="price-advisor-web-live", name=f"server-{int(time.time())}")
            wandb_table = wandb.Table(columns=["Description", "Unit", "Backend", "Latency (s)", "Price Low", "Price High", "Confidence", "Reasoning"])
            print("\n[W&B] Đã kích hoạt theo dõi LIVE trên Weights & Biases!")
    except Exception as e:
        print(f"\n[W&B] Không khởi tạo được W&B: {e}")

@app.on_event("shutdown")
def shutdown_event():
    global wandb_run, wandb_table
    if wandb_run and wandb_table:
        print("\n[W&B] Đang đồng bộ bảng dữ liệu cuối cùng lên Server...")
        wandb_run.log({"live_queries_table": wandb_table})
        wandb_run.finish()


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    index_path = WEB_DIR / "index.html"
    if not index_path.exists():
        return "<h1>Missing web/index.html</h1>"
    return index_path.read_text(encoding="utf-8")


@app.post("/api/suggest")
async def suggest_price(req: SuggestRequest) -> Any:
    global wandb_run, wandb_table
    start_time = time.time()
    
    config = PriceAdvisorConfig.from_env()
    config.llm_backend = req.backend
    if req.backend == "gemini":
        config.allow_external_api = True

    print(f"\n[SERVER] Nhận truy vấn mới: '{req.description}' - Backend: {req.backend}")

    try:
        advisor = PriceAdvisor(config)
        result = advisor.suggest_price(
            description=req.description,
            unit=req.unit,
            top_k=req.top_k,
        )
        latency = time.time() - start_time
        
        if isinstance(result, AdvisorError):
            return {"status": "error", "error": result.model_dump()}

        # Ghi log thời gian thực lên W&B
        if wandb_run and wandb_table is not None:
            wandb_run.log({
                "live_latency_sec": latency,
                "live_confidence_pct": result.confidence * 100
            })
            wandb_table.add_data(
                req.description, req.unit, req.backend, round(latency, 2),
                result.price_low, result.price_high, round(result.confidence, 2), result.reasoning
            )

        refs = advisor.store.search(req.description, req.unit, req.top_k)
        refs_dump = [
            {
                "ref_id": r.ref_id,
                "description": r.description,
                "unit": r.unit,
                "price": r.price,
                "source": r.source,
                "metadata": r.metadata,
            }
            for r in refs
        ]
        
        return {
            "status": "success",
            "suggestion": result.model_dump(),
            "references": refs_dump
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
