# Báo cáo kiểm chứng HSMT Enterprise AI v7

Ngày kiểm chứng: 2026-06-21

## 1. Kiểm thử mã nguồn

- `python -m pytest -q`: **8/8 bài kiểm thử đạt**.
- `python -m compileall -q .`: **không có lỗi cú pháp**.
- Tổng mã Python: khoảng **3.450+ dòng** (không tính cache và thư viện ngoài).

## 2. Kiểm thử đối chiếu Excel mẫu

Lệnh:

```bash
python cli.py compare \
  --hsmt data/HSMT_GoiM01.xlsx \
  --hsdt "MinhPhat=data/NT_MinhPhat_HSDT.xlsx" \
  --output HSMT_Enterprise_AI_v7_validation_report.xlsx
```

Kết quả:

- Hạng mục chuẩn: 22.
- Dòng đối chiếu: 22.
- Khớp chính xác: 22.
- Thiếu hạng mục: 0.
- Hạng mục ngoài danh mục: 0.
- Dòng cảnh báo: 2.
- Dòng bất thường nghiêm trọng: 2.
- Báo cáo có 6 sheet: Tổng quan, Đối chiếu chi tiết, Bất thường, Ma trận giá, Thiếu và ngoài danh mục, Nhật ký & bảo mật.

## 3. Kiểm tra cấu trúc PDF scan do người dùng cung cấp

Tệp: `20260616045331942.pdf`

Pipeline lấy ảnh scan nhúng gốc rồi phát hiện lưới bằng hình học OpenCV, chưa gọi OCR model:

| Trang | Kích thước ảnh | Nguồn | Biên bảng | Đường dọc | Đường ngang | Confidence cấu trúc |
|---|---:|---|---|---:|---:|---:|
| 1 | 2340×1654 | embedded-image | (235,130,1852,1320) | 20 | 82 | 1.0000 |
| 2 | 2340×1654 | embedded-image | (241,122,1855,1377) | 20 | 93 | 1.0000 |

Như vậy cấu trúc 19 cột của hai trang đã được nhận diện bằng đường kẻ thay vì yêu cầu VLM đoán toàn bộ bảng.

## 4. Phạm vi chưa kiểm chứng trong môi trường này

- Chưa chạy nhận dạng ký tự hoàn chỉnh trên PDF thật vì bộ trọng số PaddleOCR cục bộ chưa được đặt trong thư mục `models/`.
- Không tải model tự động nhằm giữ đúng chế độ bảo mật, không phát sinh kết nối mạng ngoài.
- Độ chính xác OCR cuối cùng phải được benchmark trên tập ground truth của doanh nghiệp trước khi đưa vào quy trình phê duyệt.

## 5. Điều kiện chấp nhận production đề xuất

- Numeric Cell Exact Match của các cột giá/khối lượng đạt ngưỡng doanh nghiệp quy định.
- Không có lỗi âm thầm: ô không chắc chắn phải xuất hiện trong sheet kiểm tra.
- Chạy model hoàn toàn cục bộ, kiểm tra SHA-256 trước khi khởi động.
- Có kiểm thử tải với các workbook lớn và giới hạn tài nguyên phù hợp máy chủ triển khai.
