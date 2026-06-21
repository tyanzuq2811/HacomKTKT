# Chuẩn bị model theo quy trình offline

## Nguyên tắc

Máy production không tải model. Việc tải chỉ được thực hiện trên máy staging có kiểm soát, sau đó:

1. Xác minh nguồn chính thức và license.
2. Ghi SHA-256 cho mọi tệp model.
3. Quét mã độc.
4. Chép bằng kênh nội bộ vào thư mục chỉ đọc.
5. Sửa YAML PaddleX để `model_dir` trỏ tới đường dẫn local.
6. Ngắt mạng production và chạy `scripts/validate_models.py`.

## BGE-M3

Sao chép toàn bộ snapshot BGE-M3 vào thư mục nội bộ, ví dụ:

```text
D:/HSMT_MODELS/bge-m3/
```

Khai báo:

```env
HSMT_EMBEDDING_MODEL=D:/HSMT_MODELS/bge-m3
```

`core/matcher.py` luôn nạp bằng `local_files_only=True`.

## Paddle OCR

Chuẩn bị các model/config local:

```env
HSMT_PADDLE_REC_MODEL_DIR=D:/HSMT_MODELS/latin_PP-OCRv5_mobile_rec
HSMT_PADDLE_OCR_YAML=D:/HSMT_MODELS/config/ocr_v5_local.yaml
HSMT_TABLEMAGIC_YAML=D:/HSMT_MODELS/config/tablemagic_v2_local.yaml
HSMT_PPSTRUCTURE_YAML=D:/HSMT_MODELS/config/ppstructure_v3_local.yaml
HSMT_PADDLE_VL_YAML=D:/HSMT_MODELS/config/paddleocr_vl_1_6_local.yaml
```

Trong từng YAML, không để `model_dir: null`; mọi module phải trỏ tới model local. Nếu để null, PaddleOCR có thể cố tải model chính thức và strict network guard sẽ chặn.
