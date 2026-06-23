# Báo cáo kiểm thử v7.2

## 1. Kiểm thử mã nguồn

- Biên dịch toàn bộ mã Python thành công.
- Health check FastAPI trả phiên bản `7.2.0`.
- Kiểm thử số Việt Nam và số quốc tế.
- Kiểm thử matcher one-to-one.
- Kiểm thử so sánh ngang hàng với ba nhà thầu.
- Đổi thứ tự A/B/C không làm thay đổi phần trăm chênh lệch.
- Kiểm thử hạng mục chỉ có ở một số hồ sơ.
- Kiểm thử xuất báo cáo Excel ngang hàng.
- Kiểm thử chặn kết nối mạng ngoài.

Kết quả bộ kiểm thử trọng tâm: **5/5 bài kiểm thử đạt**.

## 2. Chạy thử trên hai file Hacom Mall

Pipeline v7.2 đã chạy trực tiếp trên:

- Linh Anh.
- Văn Lang – Trí Trung.

Kết quả lần chạy hiện tại:

| Chỉ số | Kết quả |
|---|---:|
| Số nhà thầu | 2 |
| Tổng nhóm hạng mục | 4.647 |
| Nhóm có ở đủ hai hồ sơ | 4.247 |
| Nhóm chỉ có ở một hồ sơ | 400 |
| Nhóm mức Cần kiểm tra | 43 |
| Nhóm mức Cảnh báo | 759 |
| Nhóm mức Bất thường | 1.929 |
| Tổng thông số bị đánh dấu | 27.024 |

Báo cáo tạo thành công với chín sheet và không có cột “nhà thầu chuẩn”. Các số trên là kết quả sàng lọc tự động, chưa phải kết luận nghiệp vụ.

## 3. Lưu ý về độ chính xác

- Ghép fuzzy hoặc ghép bằng model là tín hiệu hỗ trợ; các nhóm có độ tin cậy thấp được đánh dấu để kiểm tra.
- Một số dòng cấu thành có thể được tổ chức khác nhau giữa hai hồ sơ nên cần xác nhận bằng file gốc.
- Chuyên viên vẫn phải kiểm tra hồ sơ nguồn trước khi kết luận về giá, khối lượng hoặc tính phù hợp kỹ thuật.
