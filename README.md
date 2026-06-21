# HSMT Enterprise AI v7.0

Hệ thống **xử lý hoàn toàn nội bộ** dành cho doanh nghiệp:

1. OCR PDF/ảnh scan dạng bảng thành Excel có kiểm chứng.
2. So sánh một HSMT với nhiều HSDT.
3. So sánh trực tiếp nhiều HSDT của các nhà thầu khi không có HSMT chuẩn.
4. Phát hiện bất thường về đơn giá, khối lượng, tên hạng mục, đơn vị tính, dữ liệu thiếu và phép tính.
5. Xuất báo cáo Excel có ma trận giá, danh sách cần kiểm tra và nhật ký SHA-256.

> Điểm bất thường là tín hiệu hỗ trợ chuyên viên rà soát, không phải kết luận gian lận hoặc quyết định lựa chọn nhà thầu.

## Nâng cấp chính so với v6.1

### OCR grid-first cho bảng chữ nhỏ

```text
PDF/ảnh
  → lấy ảnh nhúng gốc hoặc render cục bộ
  → thử hướng trang và chấm điểm bằng hình học + OCR header
  → phát hiện đường ngang/dọc OpenCV
  → cắt từng ô
  → bỏ viền + phóng ảnh ô
  → PP-OCRv5 recognition-only theo batch
  → chạy nhiều biến thể/Tesseract chỉ cho ô không chắc chắn
  → kiểm tra ô trống, định dạng số, KL × ĐG = Thành tiền
  → Excel + danh sách ô cần xác nhận
```

Cách này tránh đưa cả trang 19 cột vào một VLM rồi yêu cầu mô hình đoán toàn bộ bảng. PP-TableMagic và PaddleOCR-VL được giữ làm fallback local cho bảng không có lưới hoặc vùng phức tạp.

### So sánh file lớn

- Đọc `.xlsx` bằng `openpyxl` ở chế độ `read_only`, không nạp cả workbook vào RAM.
- Tự dò header một hoặc nhiều tầng, bỏ title/banner và dòng đánh số cột.
- Match theo thứ tự: mã hiệu → tên chuẩn hóa → TF-IDF ký tự + nearest-neighbor → RapidFuzz → BGE-M3 local cho các cặp khó.
- Không so sánh toàn bộ N×M; chỉ chấm điểm các ứng viên gần nhất.
- Báo cáo dùng XlsxWriter `constant_memory` và tự chia sheet khi gần giới hạn dòng Excel.
- Chế độ HSDT-vs-HSDT xây danh mục hợp nhất rồi rematch toàn bộ nhà thầu.

### Phát hiện bất thường có thể giải thích

- Lệch giá/khối lượng so với HSMT.
- Trung vị và MAD giữa các HSDT; tính Robust Z-score.
- IsolationForest đa biến chỉ đóng vai trò tín hiệu bổ sung.
- Khớp tên thấp, mã trùng nhưng tên khác, đơn vị tính khác.
- Thiếu hạng mục, hạng mục ngoài danh mục.
- Dữ liệu trống không bao giờ được đánh dấu `OK`.
- Giá trị `0` được giữ nguyên, không bị thay bằng giá trị tự tính.

## Cấu trúc

```text
core/
  excel_reader.py       đọc workbook theo luồng, tự dò schema
  matcher.py            matching lai, one-to-one, local embedding
  comparison.py         sai lệch và cờ nghiệp vụ
  anomaly.py            median/MAD/Robust-Z/IsolationForest
  reporter.py           báo cáo Excel constant-memory
  pipeline.py           HSMT-vs-HSDT và HSDT-vs-HSDT
ocr/
  pdf_io.py             ảnh nhúng, render, hướng trang
  grid.py               lưới, ROI, cell crop, preprocess
  engines.py            PP-OCRv5 batch + ensemble local
  schema.py             nhận dạng cột/header nhiều tầng
  verify.py             parse số, ô bắt buộc, phép tính
  exporter.py           Excel OCR + sheet ô cần kiểm
  pipeline.py           điều phối OCR
security/
  runtime.py            offline env, egress guard, temp cleanup
app.py                  giao diện Streamlit
cli.py                  chạy dòng lệnh/batch
```

## Cài nhanh phần so sánh Excel

Yêu cầu Python 3.10 hoặc 3.11.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Phần so sánh Excel hoạt động ngay, không cần GPU.

## Cài OCR production

1. Cài PaddlePaddle phù hợp CUDA trên server nội bộ.
2. Cài:

```powershell
pip install -r requirements-ocr-gpu.txt
```

3. Chuẩn bị model trên một máy staging được kiểm soát, quét mã độc và kiểm tra checksum, sau đó chép vào thư mục model nội bộ.
4. Sửa `.env` theo `.env.example` để tất cả đường dẫn đều trỏ đến file/thư mục local.
5. Production đặt:

```env
HSMT_STRICT_PRIVACY=1
HSMT_ALLOW_NETWORK=0
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
```

Khuyến nghị model:

- `latin_PP-OCRv5_mobile_rec`: nhận dạng từng ô theo batch, hỗ trợ tiếng Việt/Latin.
- `PP-TableMagic` / `TableRecognitionPipelineV2`: fallback cấu trúc bảng.
- `PP-StructureV3`: tài liệu hỗn hợp.
- `PaddleOCR-VL-1.6`: fallback cho vùng phức tạp, không dùng làm đường mặc định cho bảng lưới chữ nhỏ.
- `BAAI/bge-m3`: matching tên đa ngôn ngữ, tải về máy và dùng `local_files_only=True`.

Tài liệu chính thức:

- https://www.paddleocr.ai/latest/en/version3.x/pipeline_usage/PaddleOCR-VL.html
- https://paddlepaddle.github.io/PaddleOCR/main/en/version3.x/pipeline_usage/table_recognition_v2.html
- https://paddlepaddle.github.io/PaddleOCR/main/en/version3.x/pipeline_usage/PP-StructureV3.html
- https://paddlepaddle.github.io/PaddleOCR/main/en/version3.x/module_usage/text_recognition.html
- https://huggingface.co/BAAI/bge-m3

## Chạy CLI

### HSMT với nhiều HSDT

```powershell
python cli.py compare `
  --hsmt HSMT.xlsx `
  --hsdt "Nhà thầu A=A.xlsx" `
  --hsdt "Nhà thầu B=B.xlsx" `
  --output Bao_cao.xlsx
```

### So sánh các HSDT

```powershell
python cli.py compare-bidders `
  --hsdt "Nhà thầu A=A.xlsx" `
  --hsdt "Nhà thầu B=B.xlsx" `
  --hsdt "Nhà thầu C=C.xlsx" `
  --output So_sanh_HSDT.xlsx
```

### OCR

```powershell
python cli.py ocr --input scan.pdf --output scan_OCR.xlsx
```

## Báo cáo Excel

Báo cáo so sánh gồm:

- `Tổng quan`
- `Đối chiếu chi tiết`
- `Bất thường`
- `Ma trận giá`
- `Thiếu và ngoài danh mục`
- `Nhật ký & bảo mật`

Báo cáo OCR gồm:

- `Dữ liệu OCR`
- `Ô cần kiểm tra`
- `Nhật ký OCR`

## Bảo mật

- Không có API cloud trong mã nguồn.
- Model chỉ được nạp từ đường dẫn local trong strict mode.
- `deny_external_network()` chặn kết nối ra ngoài ở cấp tiến trình, vẫn cho loopback.
- Docker production dùng mạng nội bộ không có egress, chỉ bind UI vào `127.0.0.1`, filesystem chỉ đọc, tmpfs và bỏ toàn bộ Linux capabilities.
- Tệp upload được xử lý trong thư mục tạm quyền hạn chế và xóa khi kết thúc.
- Báo cáo ghi SHA-256 của từng nguồn để truy vết.
- Chuỗi bắt đầu bằng `=`, `+`, `-`, `@` được escape khi ghi Excel để giảm nguy cơ formula injection.

## Kiểm thử

```powershell
python -m pytest -q
```

Bộ test hiện kiểm tra parser số Việt Nam/quốc tế, giá trị 0, dữ liệu thiếu, matching one-to-one, outlier đa nhà thầu, dò lưới và egress guard.
