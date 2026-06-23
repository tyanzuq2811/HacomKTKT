# Chuẩn bị model AI theo quy trình offline

## 1. Nguyên tắc

Máy production không tải model từ Internet. Thực hiện trên một máy staging được kiểm soát:

1. Tải model từ trang chính thức.
2. Xác minh license và phiên bản.
3. Quét mã độc.
4. Tính SHA-256 cho toàn bộ snapshot.
5. Chép snapshot vào thư mục model nội bộ.
6. Production đặt các biến offline và chặn egress.
7. Chạy `python scripts/validate_models.py`.

## 2. Model matching khuyến nghị

### Cấu hình cân bằng

```text
D:/HSMT_MODELS/Qwen3-Embedding-0.6B/
D:/HSMT_MODELS/Qwen3-Reranker-0.6B/
```

`.env`:

```env
HSMT_EMBEDDING_MODEL=D:/HSMT_MODELS/Qwen3-Embedding-0.6B
HSMT_RERANKER_MODEL=D:/HSMT_MODELS/Qwen3-Reranker-0.6B
HSMT_ENABLE_EMBEDDINGS=1
HSMT_ENABLE_RERANKER=1
```

Pipeline dùng instruction riêng cho bài toán ghép dòng BOQ và chỉ chạy model trên các cặp top-K khó.

### Cấu hình chính xác cao hơn

Có thể thay bằng bản 4B nếu máy có GPU đủ mạnh. Không nên bật bản 8B trước khi benchmark độ chính xác, độ trễ và VRAM trên dữ liệu thật.

### Fallback

```text
BAAI/bge-m3
BAAI/bge-reranker-v2-m3
```

## 3. Cài thư viện model

```powershell
pip install -r requirements-models.txt
```

Production dùng `local_files_only=True`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`.

## 4. Model OCR

OCR không bắt buộc cho chức năng so sánh Excel. Khi dùng OCR, chuẩn bị model cục bộ:

```env
HSMT_PADDLE_REC_MODEL_DIR=D:/HSMT_MODELS/latin_PP-OCRv5_mobile_rec
HSMT_PADDLE_OCR_YAML=D:/HSMT_MODELS/config/ocr_v5_local.yaml
HSMT_TABLEMAGIC_YAML=D:/HSMT_MODELS/config/tablemagic_v2_local.yaml
HSMT_PPSTRUCTURE_YAML=D:/HSMT_MODELS/config/ppstructure_v3_local.yaml
HSMT_PADDLE_VL_YAML=D:/HSMT_MODELS/config/paddleocr_vl_1_6_local.yaml
```

Trong YAML, mọi `model_dir` phải trỏ đến thư mục local. Không để rỗng vì thư viện có thể cố tải trọng số.

## 5. Kiểm tra model

```powershell
python scripts/validate_models.py
```

Script in số file và tree SHA-256 để doanh nghiệp lưu vào biên bản triển khai.
