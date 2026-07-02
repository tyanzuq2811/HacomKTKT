from __future__ import annotations

import json
from typing import Protocol

import httpx

from .config import PriceAdvisorConfig
from .schemas import PriceSuggestion

import re as _re
import time as _time

SYSTEM_PROMPT = (
    "Bạn là chuyên gia tư vấn giá vật tư MEP. "
    "Chỉ dùng dữ liệu lịch sử, min/max/median được cung cấp. "
    "Không tự sáng tác số ngoài biên dữ liệu. "
    "Trả về JSON đúng schema: price_low, price_high, unit, confidence, reasoning, source_ids."
)

_MAX_RETRIES = 3
_RETRY_CODES = ("429", "500", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "INTERNAL")


def _json_from_text(text: str) -> dict:
    """Trích xuất cục JSON đầu tiên từ phản hồi LLM — xử lý:
      - markdown ```json ... ```
      - double JSON nối nhau
      - text rác trước/sau JSON
    """
    cleaned = text.strip()
    # Bỏ markdown fenced block
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    # Trích xuất cục JSON đầu tiên bằng regex
    match = _re.search(r"\{", cleaned)
    if match:
        start = match.start()
        depth = 0
        for i, ch in enumerate(cleaned[start:], start=start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(cleaned[start : i + 1])
    # Fallback: thử parse nguyên cục
    return json.loads(cleaned)


def _retry_on_transient(func, *args, **kwargs):
    """Auto-retry với exponential backoff cho lỗi tạm thời (429/500/503)."""
    for attempt in range(_MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            err_msg = str(exc)
            is_transient = any(code in err_msg for code in _RETRY_CODES)
            if is_transient and attempt < _MAX_RETRIES - 1:
                wait = (attempt + 1) * 15  # 15s, 30s
                print(f"[LLM_CLIENT] Lỗi tạm thời ({err_msg[:80]}...). Thử lại sau {wait}s (lần {attempt+2}/{_MAX_RETRIES})")
                _time.sleep(wait)
            else:
                raise


class LLMClient(Protocol):
    backend_name: str

    def ask_price(self, prompt: str) -> PriceSuggestion:
        ...


class OllamaClient:
    backend_name = "ollama"

    def __init__(self, config: PriceAdvisorConfig):
        self.model = config.ollama_model
        self.url = f"{config.ollama_base_url}/api/generate"
        self.timeout = config.ollama_timeout_seconds

    def ask_price(self, prompt: str) -> PriceSuggestion:
        full_prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            "Output bắt buộc là JSON thuần, không markdown.\n\n"
            f"{prompt}"
        )
        response = httpx.post(
            self.url,
            json={
                "model": self.model,
                "prompt": full_prompt,
                "format": "json",
                "stream": False,
                "options": {"temperature": 0.2},
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        return PriceSuggestion.model_validate(_json_from_text(payload["response"]))


class GeminiClient:
    backend_name = "gemini"

    def __init__(self, config: PriceAdvisorConfig):
        if not config.allow_external_api:
            raise ValueError("Gemini backend requires PRICE_ADVISOR_ALLOW_EXTERNAL_API=1")
        if not config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required for Gemini backend")
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise RuntimeError("Install google-genai to use Gemini backend") from exc
        self._types = types
        self.client = genai.Client(api_key=config.gemini_api_key)
        self.model = config.gemini_model
        print(f"[LLM_CLIENT] Khởi tạo thành công kết nối Gemini API (Model: {self.model})")

    def _call_api(self, prompt: str):
        """Gọi Gemini API (được wrap bởi retry)."""
        return self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self._types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PriceSuggestion,
                temperature=0.2,
                system_instruction=SYSTEM_PROMPT,
            ),
        )

    def ask_price(self, prompt: str) -> PriceSuggestion:
        print("[LLM_CLIENT] Bắt đầu gửi request tới Gemini API...")
        response = _retry_on_transient(self._call_api, prompt)
        print("[LLM_CLIENT] Đã nhận kết quả từ Gemini API thành công!")
        return PriceSuggestion.model_validate(_json_from_text(response.text))


class DeterministicClient:
    """Small offline client for tests and smoke runs."""

    backend_name = "deterministic"

    def ask_price(self, prompt: str) -> PriceSuggestion:
        import re

        min_match = re.search(r"Min=(\d+(?:\.\d+)?)", prompt)
        max_match = re.search(r"Max=(\d+(?:\.\d+)?)", prompt)
        unit_match = re.search(r"Đơn vị=([^.\n]+)", prompt)
        low = int(float(min_match.group(1))) if min_match else 1
        high = int(float(max_match.group(1))) if max_match else low
        spread = max(high - low, 0)
        return PriceSuggestion(
            price_low=int(round(low + spread * 0.10)),
            price_high=int(round(high - spread * 0.10)) if spread else high,
            unit=(unit_match.group(1).strip() if unit_match else ""),
            confidence=0.65,
            reasoning="Khoảng giá được chọn từ dữ liệu lịch sử gần nhất; không gọi LLM ngoài.",
            source_ids=[],
        )


def build_llm_client(config: PriceAdvisorConfig) -> LLMClient:
    backend = config.llm_backend.lower()
    if backend == "gemini":
        return GeminiClient(config)
    if backend == "deterministic":
        return DeterministicClient()
    if backend == "ollama":
        return OllamaClient(config)
    raise ValueError(f"Unsupported PRICE_ADVISOR_LLM_BACKEND={config.llm_backend!r}")

