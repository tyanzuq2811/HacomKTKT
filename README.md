# HSDT Peer Comparison v7.2

## Công cụ so sánh ngang hàng giữa 2, 3 hoặc nhiều nhà thầu

Hệ thống đặt tất cả hồ sơ dự thầu cạnh nhau và **không chọn nhà thầu nào làm chuẩn**.

Ví dụ có ba nhà thầu A, B và C:

```text
Nhà thầu A ─┐
Nhà thầu B ─┼─> Ghép các hạng mục tương ứng
Nhà thầu C ─┘            ↓
                  Đặt mọi giá trị cạnh nhau
                            ↓
                  Đánh dấu điểm khác biệt
                            ↓
                    Xuất báo cáo Excel
```

Thứ tự tải file không làm thay đổi nguyên tắc tính toán.

---

## 1. Hệ thống kiểm tra những gì?

Với mỗi hạng mục, hệ thống so sánh:

- Tên hạng mục và mã hiệu.
- Đơn vị tính.
- Khối lượng.
- Đơn giá tổng hợp.
- Thành tiền.
- Vật liệu chính, vật liệu phụ, nhân công và máy.
- Chi phí quản lý và lợi nhuận.
- Vật tư hoặc quy cách.
- Thương hiệu và xuất xứ.
- Các cột thông số kỹ thuật khác được phát hiện trong file.
- Hạng mục chỉ xuất hiện ở một hoặc một số hồ sơ.
- Lỗi dữ liệu như ô trống, mã trùng, số liệu không hợp lệ hoặc sai phép tính.

---

## 2. Cách tính chênh lệch không thiên vị

### Khi có hai nhà thầu

```text
Chênh lệch % = |A - B| / ((|A| + |B|) / 2)
```

Ví dụ:

```text
Nhà thầu A: 100 triệu
Nhà thầu B: 120 triệu

Chênh tuyệt đối = 20 triệu
Chênh lệch % = 20 / 110 = 18,18%
```

Đổi A và B cho nhau vẫn ra 18,18%.

### Khi có từ ba nhà thầu trở lên

```text
Chênh lệch % = (giá trị cao nhất - giá trị thấp nhất)
                / trung bình trị tuyệt đối của tất cả giá trị đang có
```

Trung vị, thấp nhất và cao nhất chỉ dùng để mô tả mặt bằng chung. Chúng **không phải giá chuẩn**.

---

## 3. Cách hệ thống ghép hạng mục

Hệ thống không lấy file đầu tiên làm danh mục chuẩn. Thay vào đó:

1. So sánh từng cặp nhà thầu.
2. Chạy ghép theo cả hai chiều A→B và B→A.
3. Ưu tiên mã, cấu trúc, STT và tên trùng nhau.
4. Dùng TF-IDF và RapidFuzz cho cách viết hơi khác.
5. Có thể dùng embedding và reranker cục bộ cho trường hợp khó.
6. Hợp nhất các kết quả thành một nhóm hạng mục chung.
7. Không cho một nhóm chứa hai dòng của cùng một nhà thầu.

Cách này giúp giảm thiên lệch do thứ tự file.

---

## 4. Báo cáo Excel đầu ra

Báo cáo gồm:

1. **Hướng dẫn đọc** – giải thích bằng ngôn ngữ đơn giản.
2. **Tổng quan** – số nhà thầu, số nhóm, số cảnh báo.
3. **Tổng hợp hạng mục** – mỗi hạng mục một dòng, có giá trị của tất cả nhà thầu.
4. **Chi tiết chênh lệch** – từng thông số, phần trăm và lý do.
5. **Ma trận đơn giá** – đặt giá các nhà thầu cạnh nhau.
6. **Ma trận khối lượng** – đặt khối lượng các nhà thầu cạnh nhau.
7. **Khác danh mục** – hạng mục không xuất hiện đầy đủ ở mọi hồ sơ.
8. **Chất lượng dữ liệu** – lỗi từ file gốc.
9. **Nhật ký và bảo mật** – hash file, model và ngưỡng đã dùng.

Mỗi cảnh báo ghi rõ:

```text
Thông số nào khác
Giá trị của từng nhà thầu
Chênh lệch tuyệt đối
Chênh lệch phần trăm
Nhà thầu thấp nhất và cao nhất
Lý do bị đánh dấu
```

---

## 5. Mức đánh dấu

| Mức | Ý nghĩa |
|---|---|
| THÔNG TIN | Có khác biệt nhỏ, vẫn ghi lại để theo dõi |
| CẦN KIỂM TRA | Thiếu dữ liệu hoặc cách ghi chưa đủ chắc chắn |
| CẢNH BÁO | Chênh lệch vượt ngưỡng cảnh báo |
| BẤT THƯỜNG | Chênh lệch lớn hoặc hạng mục chỉ có ở một hồ sơ |

Mức đánh dấu là tín hiệu hỗ trợ. Hệ thống không tự kết luận gian lận và không tự chọn nhà thầu.

---

## 6. Chạy trên Windows, chưa cần Docker

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app:app --host 127.0.0.1 --port 8000
```

Mở trình duyệt:

```text
http://127.0.0.1:8000
```

### Chạy bằng dòng lệnh

```powershell
python cli.py compare-bidders `
  --hsdt "Nhà thầu A=D:\DuLieu\A.xlsx" `
  --hsdt "Nhà thầu B=D:\DuLieu\B.xlsx" `
  --hsdt "Nhà thầu C=D:\DuLieu\C.xlsx" `
  --output "D:\KetQua\Bao_cao_so_sanh.xlsx"
```

---

## 7. Model cục bộ

Mặc định hệ thống vẫn chạy bằng mã, cấu trúc, TF-IDF và RapidFuzz.

Khi doanh nghiệp đặt model vào máy chủ nội bộ, có thể bật thêm:

```env
HSMT_EMBEDDING_MODEL=D:/HSMT_MODELS/Qwen3-Embedding-0.6B
HSMT_RERANKER_MODEL=D:/HSMT_MODELS/Qwen3-Reranker-0.6B
HSMT_ENABLE_EMBEDDINGS=1
HSMT_ENABLE_RERANKER=1
HSMT_ALLOW_NETWORK=0
HSMT_STRICT_PRIVACY=1
```

Model chỉ được nạp từ đường dẫn cục bộ. Production không tự tải model từ Internet.

---

## 8. Bảo mật

- File được xử lý trong máy hoặc máy chủ nội bộ.
- Có thể chặn kết nối Internet trong lúc xử lý.
- Model được lưu trong hạ tầng doanh nghiệp.
- File tạm có thời hạn lưu và có thể xóa sau khi tải báo cáo.
- SHA-256 của từng hồ sơ được ghi vào nhật ký.
- Nội dung bắt đầu bằng ký tự công thức Excel được escape khi xuất báo cáo.
