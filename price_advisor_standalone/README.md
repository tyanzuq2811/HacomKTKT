# PriceAdvisor Standalone

## Module này làm gì?

PriceAdvisor là hệ thống **gợi ý khoảng đơn giá vật tư MEP** dựa trên dữ liệu lịch sử chào thầu. Nó hoạt động theo cơ chế **RAG (Retrieval-Augmented Generation)**:

1. Bạn có **kho giá lịch sử** (từ các file Excel chào giá của nhà thầu).
2. Khi cần gợi ý giá cho một hạng mục, hệ thống **tìm các hạng mục tương tự** trong kho.
3. **Python tính toán** Min/Max/Median/Q1/Q3 từ dữ liệu tìm được.
4. **LLM chỉ viết lập luận** (reasoning) dựa trên các con số Python đã tính sẵn.
5. Kết quả luôn bị **ép nằm trong biên dữ liệu thật** — LLM không thể bịa giá.

**Không cần Fine-tuning model local.** Qwen2.5-14B-Instruct đã được huấn luyện sẵn khả năng tuân thủ chỉ thị và xử lý tiếng Việt. Hệ thống sử dụng **One-Shot Prompting** (đưa 1 ví dụ mẫu trong prompt) để LLM hiểu format đầu ra. Toàn bộ phép tính (Min, Max, Median) do Python đảm nhiệm — LLM chỉ cần viết 1-2 câu giải thích bằng tiếng Việt.

---

## Kiến trúc tổng quan

```
┌─────────────────────────────────────────────────────────────┐
│  HACOM_DATA (Excel chào giá)                                │
│  4 nhà thầu × 8 hệ thống MEP = 8.662 dòng giá             │
└──────────────┬──────────────────────────────────────────────┘
               │ extract-hacom
               ▼
┌──────────────────────────────────────────────────────────────┐
│  CSV chuẩn (hacom_price_refs.csv)                            │
│  Mỗi dòng: mô tả, đơn vị, giá, nhà thầu, thương hiệu...   │
└──────────────┬───────────────────────────────────────────────┘
               │ ingest / ingest-hacom
               ▼
┌──────────────────────────────────────────────────────────────┐
│  ChromaDB (Vector Database)                                  │
│  Embedding bge-m3 → tìm kiếm ngữ nghĩa tiếng Việt          │
└──────────────┬───────────────────────────────────────────────┘
               │ suggest (khi user hỏi giá)
               ▼
┌──────────────────────────────────────────────────────────────┐
│  RAG Pipeline                                                │
│  1. Tìm top-5 hạng mục tương tự trong ChromaDB              │
│  2. Python tính Min/Max/Median/Q1/Q3                         │
│  3. Dựng prompt One-Shot + đút số liệu đã tính              │
│  4. LLM viết reasoning (Ollama local hoặc Gemini API)        │
│  5. Ép kết quả vào biên Min/Max ± 5%                         │
└──────────────────────────────────────────────────────────────┘
```

---

## Cài đặt

### Trên Windows (máy dev)

```powershell
cd price_advisor_standalone
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### Trên Linux Server (production)

```bash
cd price_advisor_standalone
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

> **Hoàn toàn chạy được trên Linux.** Toàn bộ code là Python thuần, không phụ thuộc Windows. ChromaDB, sentence-transformers, openpyxl, httpx đều cross-platform. Ollama cũng có bản Linux native.

### Cài Ollama (Local LLM Server)

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:14b-instruct

# Windows — tải installer từ https://ollama.com/download
ollama pull qwen2.5:14b-instruct
```

Ollama tự chạy API server tại `http://localhost:11434`. **Không cần cấu hình gì thêm.**

### Cấu hình `.env`

```env
# === Backend LLM ===
# "ollama" = local, không cần internet (MẶC ĐỊNH)
# "gemini" = API Google, cần internet + API key
# "deterministic" = offline, không gọi LLM, chỉ dùng Python tính (để test luồng)
PRICE_ADVISOR_LLM_BACKEND=ollama

# Phải bật cờ này nếu dùng Gemini (bảo vệ chống gọi API ngoài nhầm)
PRICE_ADVISOR_ALLOW_EXTERNAL_API=0

# === Ollama ===
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b-instruct
OLLAMA_TIMEOUT_SECONDS=120

# === Gemini (chỉ cần khi BACKEND=gemini) ===
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash

# === RAG / Embedding ===
PRICE_ADVISOR_DB_DIR=./runtime/chroma
PRICE_ADVISOR_COLLECTION=price_refs
PRICE_ADVISOR_EMBEDDING_MODEL=BAAI/bge-m3
PRICE_ADVISOR_EMBEDDING_DEVICE=cpu
PRICE_ADVISOR_TOP_K=5

# === Guardrails ===
PRICE_ADVISOR_MAX_RANGE_EXPANSION=0.05
PRICE_ADVISOR_MIN_REFERENCES=1
```

---

## Các luồng chạy (Workflows)

### Luồng 1: Trích xuất dữ liệu giá từ Excel → CSV

**Mục đích:** Đọc các file Excel chào giá của nhà thầu (format HACOM Mall V2), trích ra từng dòng hạng mục kèm đơn giá, thương hiệu, xuất xứ... rồi lưu thành file CSV chuẩn.

**Khi nào chạy:** Chỉ cần chạy **1 lần** khi có bộ dữ liệu mới. Hoặc chạy lại khi có thêm file Excel mới.

```bash
python -m price_advisor extract-hacom \
    --data-dir ../HACOM_DATA \
    --output runtime/hacom_price_refs.csv
```

**Bên trong xảy ra gì:**
1. Tìm các file `.xlsx` trong `HACOM_DATA/5. Tong hop chao gia 11.12.2025/`.
2. Bỏ qua file tổng hợp (bắt đầu bằng `0.`) để tránh trùng lặp.
3. Với mỗi file, tự nhận diện layout bảng qua header (STT, Diễn giải, Đơn vị, KL Nhà thầu chào, Thành tiền BOQ...).
4. Trích từng dòng chi tiết: mô tả, đơn vị, đơn giá tổng hợp, vật liệu, mã hiệu, thương hiệu, xuất xứ, 5 thành phần giá.
5. Parse ngày từ tên file (ví dụ `2025.12.08` → `observed_at=2025-12-08`).
6. Log cảnh báo nếu phát hiện giá bất thường (≤ 500 VND hoặc ≥ 5 tỷ VND).
7. Ghi ra CSV với encoding UTF-8 BOM (mở được bằng Excel không bị lỗi font).

**Kết quả:** File `runtime/hacom_price_refs.csv` chứa ~8.662 dòng giá từ 4 nhà thầu.

---

### Luồng 2: Nạp dữ liệu vào ChromaDB (Vector Database)

**Mục đích:** Chuyển dữ liệu CSV thành vector embeddings và lưu vào ChromaDB để có thể tìm kiếm ngữ nghĩa (semantic search) bằng tiếng Việt.

**Khi nào chạy:** Sau khi có file CSV từ Luồng 1. Chỉ cần chạy **1 lần** (dữ liệu persist trên ổ cứng).

**Cách 1 — Nạp từ CSV đã trích (2 bước tách rời):**
```bash
python -m price_advisor ingest --csv runtime/hacom_price_refs.csv
```

**Cách 2 — Trích + nạp 1 lệnh (tắt gọn):**
```bash
python -m price_advisor ingest-hacom --data-dir ../HACOM_DATA
```

**Bên trong xảy ra gì:**
1. Đọc CSV (hoặc đọc Excel trực tiếp nếu dùng `ingest-hacom`).
2. Với mỗi dòng, tạo chuỗi tìm kiếm: `"mô tả chuẩn hóa | unit:đơn_vị"`.
3. Dùng model embedding `bge-m3` (chạy local trên CPU/GPU) để chuyển chuỗi thành vector 1024 chiều.
4. Lưu vector + metadata vào ChromaDB tại `runtime/chroma/`.

**Lần đầu chạy:** Model `bge-m3` sẽ tự tải về (~2GB), mất ~1-2 phút. Các lần sau nhanh hơn vì đã cache.

**Kết quả:** Thư mục `runtime/chroma/` chứa database vector, sẵn sàng cho tìm kiếm.

---

### Luồng 3: Gợi ý giá cho 1 hạng mục

**Mục đích:** Nhập mô tả hạng mục + đơn vị → nhận về khoảng giá gợi ý + lý do.

**Khi nào chạy:** Mỗi khi cần gợi ý giá. Yêu cầu đã chạy Luồng 2 trước.

```bash
python -m price_advisor suggest \
    --desc "Cáp đồng XLPE/PVC 4x25mm2" \
    --unit m \
    --top-k 5
```

**Bên trong xảy ra gì:**
1. **Tìm kiếm (Retrieval):** Dùng embedding để tìm top-5 hạng mục tương tự nhất trong ChromaDB, lọc theo đơn vị (m, cái, bộ...).
2. **Python tính toán:** Từ 5 kết quả, Python tính `Min=98000, Max=110000, Median=104000, Q1=101250, Q3=107000`.
3. **Dựng prompt One-Shot:**
   ```
   Ví dụ:
   Input: Cáp đồng 4x25. Đơn vị=m. Lịch sử=[98000, 104000, 110000]. Min=98000. Max=110000.
   Output JSON: {"price_low": 99000, "price_high": 108000, ...}

   ---
   Dữ liệu thực tế cần đánh giá:
   Input: Cáp đồng XLPE/PVC 4x25mm2. Đơn vị=m. Lịch sử=[98500, 104000, 110000]. Min=98500. Max=110000.
   ```
4. **LLM sinh JSON:** Ollama (local) hoặc Gemini (API) trả về `{price_low, price_high, reasoning}`.
5. **Ép biên (Clamp):** Nếu LLM trả giá ngoài khoảng `[Min×0.95, Max×1.05]`, hệ thống tự ép về biên và ghi warning.
6. **Trả kết quả JSON** với đầy đủ: giá thấp, giá cao, đơn vị, confidence, reasoning, source_ids, warnings.

**Output mẫu:**
```json
{
  "price_low": 99000,
  "price_high": 108000,
  "unit": "m",
  "confidence": 0.78,
  "reasoning": "Giá dao động trong vùng 98k-110k/m từ 3 nguồn gần nhất; chọn khoảng an toàn.",
  "source_ids": ["HACOM-367cdd64dfd2", "HACOM-50dcbfe60851"],
  "backend": "ollama",
  "warnings": []
}
```

---

### Luồng 4: Benchmark — So sánh backend

**Mục đích:** Chạy gợi ý giá cho N dòng ngẫu nhiên từ CSV, đo tốc độ (latency) và độ chính xác (accuracy) của từng backend LLM.

**Khi nào chạy:** Khi muốn so sánh Ollama vs Gemini, hoặc đánh giá chất lượng RAG.

```bash
# Test với backend hiện tại (trong .env), 20 dòng ngẫu nhiên
python -m price_advisor benchmark \
    --csv runtime/hacom_price_refs.csv \
    -n 20 \
    --seed 42
```

**Bên trong xảy ra gì:**
1. Đọc CSV, chọn ngẫu nhiên N dòng (seed cố định → tái tạo được kết quả).
2. Với mỗi dòng, chạy `suggest_price()` và đo thời gian.
3. So sánh: giá thật của dòng đó có nằm trong khoảng `[price_low, price_high]` mà LLM gợi ý không?
4. In progress realtime ra stderr (✅/⚠️/❌ cho từng dòng).
5. Cuối cùng xuất JSON tổng hợp ra stdout.

**Quy trình so sánh Ollama vs Gemini:**

```bash
# Bước 1: Chạy với Ollama (sửa .env: PRICE_ADVISOR_LLM_BACKEND=ollama)
python -m price_advisor benchmark --csv runtime/hacom_price_refs.csv -n 20 > benchmark_ollama.json

# Bước 2: Chạy với Gemini (sửa .env: PRICE_ADVISOR_LLM_BACKEND=gemini, ALLOW_EXTERNAL_API=1)
python -m price_advisor benchmark --csv runtime/hacom_price_refs.csv -n 20 > benchmark_gemini.json

# Bước 3: So sánh 2 file JSON → xem accuracy_pct và avg_latency_seconds
```

**Output mẫu (tóm tắt):**
```
Backend: ollama (qwen2.5:14b-instruct)
Items: 20 | Success: 20 | Errors: 0
Actual price in suggested range: 17/20 (85.0%)
Avg latency: 4.231s | Total: 84.6s
```

---

### Luồng 5 (bonus): Test offline không cần LLM

**Mục đích:** Chạy toàn bộ pipeline mà KHÔNG cần Ollama hay Gemini. Dùng backend `deterministic` — Python tự tính `price_low = Min + 10%`, `price_high = Max - 10%`.

**Khi nào chạy:** Khi muốn test luồng code, verify dữ liệu RAG mà không muốn chờ LLM.

```bash
# Sửa .env: PRICE_ADVISOR_LLM_BACKEND=deterministic
python -m price_advisor suggest --desc "Ống thép mạ kẽm D50" --unit m
python -m price_advisor benchmark --csv runtime/hacom_price_refs.csv -n 50
```

---

## Tại sao KHÔNG cần Fine-tune model local?

| Câu hỏi | Trả lời |
|----------|---------|
| **LLM có cần biết giá vật tư không?** | **Không.** Python đã tính sẵn Min/Max/Median và đút vào prompt. LLM chỉ chọn khoảng trong biên đó. |
| **LLM có cần biết domain MEP không?** | **Rất ít.** Prompt đã có sẵn ví dụ mẫu (One-Shot). LLM chỉ cần "bắt chước" format. |
| **Nếu LLM trả giá sai thì sao?** | **Bị chặn.** Hàm `clamp_price_range()` ép kết quả vào biên dữ liệu RAG ± 5%. LLM không thể hallucinate giá. |
| **Qwen2.5-14B đã đủ tốt chưa?** | **Đủ.** Model này đã được Alibaba huấn luyện instruction-following + tiếng Việt. Với task đơn giản (chọn khoảng giá từ dữ liệu cho sẵn), 14B là thừa sức. |
| **Khi nào mới cần Fine-tune?** | Chỉ khi bạn muốn LLM tự viết reasoning chuyên sâu hơn (ví dụ: so sánh giá theo vùng miền, phân tích xu hướng giá theo thời gian). Giai đoạn hiện tại chưa cần. |

---

## Triển khai trên Linux Server

### Yêu cầu hệ thống

| Thành phần | Chạy Gemini API | Chạy Ollama Local (14B) |
|---|---|---|
| **CPU** | 4 cores | 8+ cores |
| **RAM** | 8 GB | 32 GB |
| **GPU** | Không cần | NVIDIA 16GB+ VRAM (khuyến nghị) hoặc CPU-only (chậm hơn ~5x) |
| **Ổ cứng** | 5 GB (embedding model) | 15 GB (embedding + LLM weights) |
| **Internet** | Cần (gọi API Google) | Không cần |

### Bước triển khai

```bash
# 1. Clone code
git clone <repo> && cd HacomKTKT/price_advisor_standalone

# 2. Setup Python
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Cấu hình
cp .env.example .env
nano .env   # sửa backend, API key nếu cần

# 4. Cài Ollama (nếu dùng local LLM)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:14b-instruct

# 5. Copy dữ liệu Excel lên server
scp -r HACOM_DATA/ user@server:~/HacomKTKT/

# 6. Trích xuất + nạp dữ liệu (chạy 1 lần)
python -m price_advisor ingest-hacom --data-dir ../HACOM_DATA

# 7. Test
python -m price_advisor suggest --desc "Cáp đồng XLPE/PVC 4x25mm2" --unit m

# 8. Benchmark
python -m price_advisor benchmark --csv runtime/hacom_price_refs.csv -n 20
```

### Chạy Ollama trên server không có GPU

```bash
# Ollama tự fallback sang CPU nếu không có GPU NVIDIA
# Tốc độ chậm hơn (~10-15s/query thay vì ~3-5s) nhưng vẫn hoạt động
ollama pull qwen2.5:14b-instruct

# Hoặc dùng model nhỏ hơn nếu RAM hạn chế
ollama pull qwen2.5:7b-instruct   # ~5GB RAM, nhanh hơn
```

### Gợi ý chiến lược triển khai

```
┌────────────────────────────────────────────────────────┐
│  Giai đoạn 1: Test RAG (ngay bây giờ)                  │
│  → Dùng Gemini 3.5 Flash (rẻ, nhanh, test hàng nghìn  │
│    dòng BOQ để tinh chỉnh dữ liệu RAG + prompt)       │
├────────────────────────────────────────────────────────┤
│  Giai đoạn 2: Production nội bộ                        │
│  → Đổi sang Ollama + Qwen2.5-14B trên server Linux    │
│  → Không cần internet, bảo mật tuyệt đối              │
│  → Chỉ cần đổi 1 dòng trong .env                      │
├────────────────────────────────────────────────────────┤
│  Giai đoạn 3: Tối ưu (tùy chọn)                       │
│  → Nếu cần nhanh hơn: dùng vLLM thay Ollama           │
│  → Nếu cần chính xác hơn: thêm dữ liệu RAG           │
│  → Fine-tune chỉ khi muốn reasoning chuyên sâu hơn    │
└────────────────────────────────────────────────────────┘
```

---

## Quy tắc an toàn

- **Mặc định**: Backend = `ollama`, không gọi API ngoài, không cần internet.
- **Gemini**: Chỉ chạy khi bật cờ `PRICE_ADVISOR_ALLOW_EXTERNAL_API=1`.
- **Egress Guard**: Khi gửi prompt ra Gemini, hệ thống tự xóa tên dự án, tên nhà thầu, mã nội bộ. Chỉ gửi mô tả hạng mục + thống kê giá ẩn danh.
- **Clamp Range**: Kết quả LLM luôn bị ép vào biên `[Min×0.95, Max×1.05]` của dữ liệu RAG. LLM không thể bịa giá ngoài dữ liệu.
- **Fallback**: Nếu ChromaDB không tìm được dữ liệu tương tự, module trả lỗi có cấu trúc (`AdvisorError`) thay vì tự bịa.

---

## Cấu trúc thư mục

```
price_advisor_standalone/
├── .env.example              # Mẫu cấu hình
├── requirements.txt          # Thư viện Python
├── sample_prices.csv         # Dữ liệu mẫu nhỏ (5 dòng)
├── README.md                 # File này
├── price_advisor/            # Source code chính
│   ├── __init__.py           # Export PriceAdvisor, PriceAdvisorConfig
│   ├── __main__.py           # Entry point: python -m price_advisor
│   ├── cli.py                # 5 lệnh: ingest, extract-hacom, ingest-hacom, suggest, benchmark
│   ├── config.py             # Đọc .env → PriceAdvisorConfig
│   ├── schemas.py            # Pydantic models: PriceReference, PriceSuggestion, AdvisorError
│   ├── normalizer.py         # Chuẩn hóa text tiếng Việt, đơn vị (m², cái, bộ...)
│   ├── hacom_excel.py        # Parser Excel format HACOM Mall V2 + parse ngày + log outlier
│   ├── rag_store.py          # ChromaDB wrapper + InMemoryStore (test) + CSV loader
│   ├── llm_client.py         # 3 backend: OllamaClient, GeminiClient, DeterministicClient
│   ├── egress_guard.py       # Ẩn danh dữ liệu trước khi gửi API ngoài
│   ├── advisor.py            # Điều phối chính: retrieval → stats → prompt → LLM → clamp
│   └── stats.py              # Tính min/max/median/Q1/Q3, ép biên kết quả LLM
├── tests/                    # Unit tests (chạy offline, không cần LLM)
│   ├── test_advisor.py       # Test pipeline end-to-end với DeterministicClient
│   └── test_hacom_excel.py   # Test parser Excel
└── runtime/                  # Dữ liệu runtime (git-ignored)
    ├── chroma/               # ChromaDB vector database
    └── hacom_price_refs.csv  # CSV đã trích từ HACOM_DATA
```

---

## Tóm tắt lệnh

| Lệnh | Ý nghĩa | Chạy bao nhiêu lần |
|-------|---------|---------------------|
| `python -m price_advisor extract-hacom --data-dir ../HACOM_DATA --output runtime/hacom_price_refs.csv` | Trích Excel → CSV | 1 lần (khi có data mới) |
| `python -m price_advisor ingest --csv runtime/hacom_price_refs.csv` | Nạp CSV → ChromaDB | 1 lần (khi có data mới) |
| `python -m price_advisor ingest-hacom --data-dir ../HACOM_DATA` | Trích Excel → ChromaDB (tắt gọn) | 1 lần (khi có data mới) |
| `python -m price_advisor suggest --desc "..." --unit m` | Gợi ý giá cho 1 hạng mục | Mỗi khi cần |
| `python -m price_advisor benchmark --csv runtime/hacom_price_refs.csv -n 20` | Đo latency + accuracy | Khi so sánh backend |
| `python -m pytest tests` | Chạy unit tests | Khi sửa code |
