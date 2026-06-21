# Kiến trúc v7

## 1. Performance path

- Excel input: streaming rows.
- Candidate generation: sparse char TF-IDF nearest neighbors.
- Semantic embedding: chỉ chạy trên top-K ứng viên khó.
- OCR input: bỏ qua ô trắng trước inference.
- OCR recognition: recognition-only batch, không chạy detector cho từng ô.
- Second pass: chỉ ô dưới ngưỡng confidence.
- Excel output: constant-memory, sequential rows.

## 2. Safety path

- Dữ liệu thiếu → `CẦN KIỂM TRA`, không phải `OK`.
- Số 0 được phân biệt với `None`.
- Mỗi hạng mục chỉ ghép với tối đa một hạng mục đối diện.
- Mã trùng nhiều dòng không được tự ghi đè.
- Giá bất thường dùng cả chênh HSMT và consensus giữa nhà thầu.
- OCR cell lưu engine, confidence, bbox, ứng viên và lý do review.

## 3. Model strategy

- Hình học quyết định cấu trúc bảng có lưới.
- PP-OCRv5 đọc nội dung từng cell.
- PP-TableMagic/PP-StructureV3 xử lý bảng không lưới/tài liệu hỗn hợp.
- PaddleOCR-VL-1.6 chỉ làm fallback vùng khó.
- BGE-M3 local chỉ hỗ trợ matching tên; kết quả cuối vẫn có score và lý do giải thích.
