# Hướng dẫn Xây dựng PriceAdvisor — Model Local (14B) + Gemini 3.5 Flash

## Mục tiêu

Xây dựng module **PriceAdvisor** hoàn chỉnh, TÁCH RỜI khỏi Phase 1, gồm:
- **Model Local**: Qwen2.5-14B-Instruct chạy qua Ollama.
- **API Thương mại (Test RAG)**: Gemini 3.5 Flash (rẻ, nhanh, lý tưởng để test retrieval RAG).
- **Kho giá RAG**: Vector DB dùng ChromaDB (nhẹ, không cần PostgreSQL+pgvector).
- **Embedding Local**: `bge-m3` chạy qua sentence-transformers.
- **Structured Outputs**: Sử dụng tính năng Schema Response của API để ép 100% định dạng JSON.

---

## 1. Ý tưởng cốt lõi (Kiến trúc & Tối ưu)

### 1.1 Chi phí & Tốc độ test RAG với Gemini 3.5 Flash
Giai đoạn 2 cần chạy thử liên tục hàng trăm dòng vật tư MEP để xem Kho dữ liệu RAG lấy giá có chuẩn không.
- **Chi phí**: API siêu rẻ của dòng Flash giúp bạn test toàn bộ file MasterBOQ mà không lo tốn kém.
- **Độ trễ (Latency)**: Phản hồi cực nhanh, giúp Web UI hiển thị kết quả gần như tức thì.

### 1.2 Không Fine-Tuning — Few-Shot Prompting
gemini-3.5-flash đã có khả năng tuân thủ chỉ thị rất sắc bén. Thay vì Fine-tuning, chúng ta sử dụng **One-Shot / Few-Shot Prompting**.

**Ví dụ Prompt:**
```text
Input: Cáp đồng 4x25. Lịch sử: [98k, 104k, 110k]. Cực trị DB: Min=98000, Max=110000.
Output JSON: {"price_low": 99000, "price_high": 108000, "reasoning": "Giá dao động từ 98k-110k trong 3 dự án gần nhất. Chọn mốc an toàn loại trừ đột biến."}

[Dữ liệu thực tế cần đánh giá]
Input: {desc}. Lịch sử: {history}. Cực trị DB: Min={min_price}, Max={max_price}.
```

### 1.3 Ép khuôn JSON cực nhàn với Native Structured Outputs
Với thư viện `google-genai`, ta có thể ép Gemini trả về đúng cấu trúc JSON thông qua tham số `response_schema` (Pydantic Schema). KHÔNG bao giờ lo lỗi thiếu ngoặc `}` làm crash FastAPI.

### 1.4 Code Python tính toán cực trị (Không để LLM làm toán)
LLM sinh ra chuỗi (text), rất dở làm toán. Do đó, mã Python sẽ bóc tách giá Min/Max từ RAG (ChromaDB) và đút sẵn vào Prompt. Nhiệm vụ của LLM chỉ là **ráp nối và đưa ra lập luận (reasoning)**.

---

## 2. Chuẩn bị Hạ tầng

### 2.1 Yêu cầu phần cứng

| Thành phần | Tối thiểu (chạy Flash) | Khuyến nghị (chạy Local 14B) |
|---|---|---|
| RAM | 16 GB | 32 GB |
| GPU (cho Local) | Không bắt buộc | RTX 3090/4090 24GB (hoặc Mac M2/M3 Max) |

### 2.2 Cài đặt Dependencies
```powershell
pip install chromadb sentence-transformers google-genai httpx pydantic
```

### 2.3 Ollama & Gemini API Key
- **Gemini**: Tạo key tại [Google AI Studio](https://aistudio.google.com/apikey).
- **Ollama**: Cài đặt và tải model 14B:
```powershell
ollama pull qwen2.5:14b-instruct
```

Trong file `.env`:
```env
PRICE_ADVISOR_LLM_BACKEND=gemini
GEMINI_API_KEY=your_api_key_here
OLLAMA_MODEL=qwen2.5:14b-instruct
```

---

    ## 3. Triển khai Code

### 3.1 Pydantic Schema cho Structured Output (`price_advisor/schemas.py`)
```python
from pydantic import BaseModel, Field

class PriceSuggestion(BaseModel):
    price_low: int = Field(description="Mức giá đề xuất thấp nhất")
    price_high: int = Field(description="Mức giá đề xuất cao nhất")
    reasoning: str = Field(description="Lý do ngắn gọn bằng tiếng Việt")
```

### 3.2 Khởi tạo LLM Client (`price_advisor/llm_client.py`)
```python
import os
import json
import httpx
from google import genai
from google.genai import types
from .schemas import PriceSuggestion

SYSTEM_PROMPT = """Bạn là chuyên gia tư vấn giá vật tư MEP. Dựa vào dữ liệu lịch sử và cực trị được cung cấp, hãy đề xuất khoảng giá hợp lý và giải thích ngắn gọn. Không tự sáng tác số."""

class GeminiClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        
    def ask_price(self, prompt: str) -> dict:
        response = self.client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PriceSuggestion,
                temperature=0.2,
                system_instruction=SYSTEM_PROMPT
            ),
        )
        return json.loads(response.text)

class OllamaClient:
    def __init__(self, model: str = "qwen2.5:14b-instruct"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"
        
    def ask_price(self, prompt: str) -> dict:
        # VLLM hoặc Ollama hỗ trợ schema json format tùy phiên bản, ở đây fallback sang prompt-based JSON.
        full_prompt = f"{SYSTEM_PROMPT}\n\nQuy tắc: Output bắt buộc phải là JSON với các key: price_low, price_high, reasoning.\n\n{prompt}"
        resp = httpx.post(self.url, json={
            "model": self.model,
            "prompt": full_prompt,
            "format": "json",
            "stream": False
        }, timeout=120)
        return json.loads(resp.json()["response"])
```

### 3.3 Điều phối (Advisor) và Python tính toán (`price_advisor/advisor.py`)
```python
from .llm_client import GeminiClient, OllamaClient
import os

class PriceAdvisor:
    def __init__(self):
        backend = os.getenv("PRICE_ADVISOR_LLM_BACKEND", "gemini")
        if backend == "gemini":
            self.llm = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
        else:
            self.llm = OllamaClient(model=os.getenv("OLLAMA_MODEL", "qwen2.5:14b-instruct"))
            
    def suggest_price(self, description: str, unit: str, refs: list[dict]) -> dict:
        # 1. PYTHON LÀM TOÁN: Tính min/max
        prices = [r["price"] for r in refs if "price" in r]
        if not prices:
            return {"error": "Không có dữ liệu lịch sử"}
            
        min_price = min(prices)
        max_price = max(prices)
        
        # 2. Xây dựng Prompt (Few-shot)
        history_str = ", ".join([f"{int(r['price'])}k" for r in refs])
        
        prompt = f"""
Ví dụ:
Input: Cáp đồng 4x25. Lịch sử: [98k, 104k, 110k]. Cực trị DB: Min=98000, Max=110000.
Output JSON: {{"price_low": 99000, "price_high": 108000, "reasoning": "Giá dao động từ 98k-110k trong 3 dự án gần nhất. Chọn mốc an toàn loại trừ đột biến."}}

---
Thực tế cần đánh giá:
Input: {description}. Lịch sử: [{history_str}]. Cực trị DB: Min={min_price}, Max={max_price}.
"""
        # 3. LLM Sinh dữ liệu (Reasoning)
        return self.llm.ask_price(prompt)
```

---

## 4. Tóm tắt Luồng Tối ưu

1. **RAG Vector Search**: Tìm bằng ChromaDB + `bge-m3`.
2. **Tiền xử lý (Python)**: Code Python trích xuất `prices`, tìm Min/Max.
3. **One-Shot Prompting**: Nối Min/Max và dữ liệu lịch sử vào Template đã có sẵn Ví dụ.
4. **Structured Generation**: API Gemini áp dụng Pydantic Schema `PriceSuggestion` lên Output.
5. **JSON chuẩn 100%**: Trả kết quả về FastAPI không bao giờ bị lỗi format.

Với lộ trình này, bạn có thể **test ngay lập tức hàng nghìn dòng dữ liệu** bằng Gemini 3.5 Flash để tinh chỉnh CSDL RAG (ChromaDB) mà không tốn công cấu hình GPU cho Qwen2.5-14B. Khi dữ liệu chuẩn, prompt chuẩn, bạn chỉ việc gạt switch sang Local LLM.
