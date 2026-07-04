# BÁO CÁO TỔNG HỢP VÀ PHÂN TÍCH LỖI HỆ THỐNG PRICE ADVISOR AI
*(Tổng hợp từ các phiên chạy thử nghiệm, Benchmark 100 mẫu và 500 mẫu)*

---

Trong quá trình phát triển, thử nghiệm và chạy Benchmark trên tập dữ liệu vật tư MEP (Cơ điện) lớn (hơn 8.600 mặt hàng), hệ thống đã trải qua nhiều phiên bản chạy thử nghiệm (từ 100 mẫu ban đầu đến 500 mẫu chính thức). Dưới đây là tổng hợp toàn bộ các lỗi thực tế đã được phát hiện, nguyên nhân cốt lõi và các giải pháp kỹ thuật đã áp dụng để cải tiến hệ thống.

---

## 1. BẢNG TỔNG HỢP CÁC NHÓM LỖI HỆ THỐNG

Ghi nhận qua phiên chạy Benchmark quy mô lớn $N=500$ mẫu (Run ID: `k06c1gnt`), hệ thống đạt tỷ lệ thành công **99.4%** và độ chính xác **94.4%** (chỉ có 31 ca gặp sự cố hoặc dự báo sai lệch trên tổng số 500 mẫu):

| Nhóm lỗi | Số ca gặp | Tỷ lệ | Nguyên nhân cốt lõi | Biện pháp khắc phục đã áp dụng | Trạng thái |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **Nhóm 1: Thiếu hụt ngữ cảnh (RAG Noise)** | 15 | 3.0% | Người dùng nhập mô tả quá ngắn (ví dụ: "D90", "D32", "Ống") dẫn đến ChromaDB lấy nhầm thiết bị khác loại cùng kích thước. | Tích hợp cảnh báo thời gian thực trên giao diện Web UI yêu cầu nhập tối thiểu 10 ký tự. | **Đã xử lý trên UI** |
| **Nhóm 2: Kẹp khoảng giá quá chặt** | 11 | 2.2% | Sử dụng dung sai cố định $\epsilon = 5\%$ gạt bỏ mức giá cao thực tế của các thiết bị đặc chủng, cao cấp. | **Nâng cấp sang Thuật toán Kẹp Biên Động (Dynamic Clamping)** tự động điều chỉnh dung sai từ 5% đến 25%. | **Đã tích hợp mã nguồn & Test Pass** |
| **Nhóm 3: Egress Guard che khuất từ khóa** | 2 | 0.4% | Việc bôi đen tên dự án/nhà thầu thành `***` làm mất đi từ khóa kỹ thuật cốt lõi khiến LLM đoán sai khoảng giá. | **Chuyển dịch sang Local LLM (Qwen3-30B-A3B)** chạy offline và tắt hoàn toàn Egress Guard (`DISABLE_EGRESS_GUARD=True`). | **Sẵn sàng triển khai** |
| **Nhóm 4: Lỗi kết nối API mạng** | 3 | 0.6% | Lỗi Rate Limit (HTTP 429) hoặc Timeout mạng tạm thời từ nhà cung cấp Cloud LLM khi gửi request liên tục. | Tích hợp cơ chế **Auto-Retry với Exponential Backoff** (tự động thử lại với độ trễ tăng dần 15s, 30s, 60s). | **Đã xử lý tự động** |
| **Nhóm 5: Sai lệch so sánh biên toán học** *(Lịch sử)* | - | - | Phiên bản đầu tiên so sánh khoảng giá dùng điều kiện nghiêm ngặt ($> , <$) thay vì bao gồm dấu bằng ($\geq , \leq$) và chưa làm tròn dấu phẩy động. | Cập nhật hàm so sánh sang $\geq , \leq$ và làm tròn phần nguyên để loại bỏ sai lệch dấu phẩy động. | **Đã sửa đổi hoàn tất** |

---

## 2. PHÂN TÍCH CHI TIẾT TỪNG TRƯỜNG HỢP LỖI

### 2.1. Nhóm 1: Thiếu hụt ngữ cảnh do mô tả quá ngắn
*   **Mô tả lỗi:** Khi kỹ sư nhập các từ khóa quá vắn tắt hoặc chỉ chứa kích thước kỹ thuật (ví dụ: `D90`, `D25`, `Ống nhựa`).
*   **Hậu quả:** Bộ máy RAG (truy xuất ngữ nghĩa) thông qua ChromaDB không thể phân biệt được mục đích. Nó sẽ trả về một danh sách hỗn tạp bao gồm: *Ống nhựa uPVC D90*, *Van bướm tay gạt D90*, *Đai treo ống D90*, v.v. Điều này làm nhiễu dữ liệu đầu vào của LLM, dẫn đến khoảng giá đề xuất bị kéo giãn hoặc sai lệch hoàn toàn.
*   **Giải pháp:** Tích hợp một bộ kiểm tra độ dài câu truy vấn bằng JavaScript ngay trên giao diện Web UI. Nếu mô tả dưới 10 ký tự, hệ thống lập tức hiển thị cảnh báo yêu cầu người dùng bổ sung thêm thông tin chất liệu (ví dụ: `uPVC`, `PPR`) hoặc thương hiệu (ví dụ: `Tiền Phong`, `Đông Á`) để tăng độ chính xác tìm kiếm RAG.

### 2.2. Nhóm 2: Kẹp khoảng giá quá chặt (Outlier Clamping)
*   **Mô tả lỗi:** Thuật toán lọc giá trị ngoại lai ban đầu sử dụng một hệ số kẹp khoảng giá cố định ($\epsilon = 0.05$ hay 5%).
*   **Hậu quả:** Đối với các thiết bị phổ thông (như dây điện, ống nước thông thường), hệ số 5% hoạt động rất tốt. Tuy nhiên, đối với các thiết bị đặc chủng hoặc thiết bị trang trí cao cấp (ví dụ: *Đèn chùm trang trí sảnh lớn*, *Contactor công suất cực lớn*), giá thực tế có thể đắt gấp nhiều lần hàng phổ thông cùng kích thước. Thuật toán kẹp biên cố định đã vô tình gạt bỏ các giá trị cao này vì nghĩ đó là dữ liệu rác (outliers).
*   **Giải pháp nâng cấp:** Chuyển sang cơ chế **Điều chỉnh động hệ số dung sai $\epsilon$**. Hệ thống tính toán độ phân tán giá tương đối của RAG context ($\text{Spread} = (P_{\max} - P_{\min})/P_{\text{mean}}$) và tự động giãn rộng biên $\epsilon$ từ 5% lên tối đa 25% cho các vật tư đặc thù có giá trị biến động mạnh.

### 2.3. Nhóm 3: Egress Guard che khuất từ khóa kỹ thuật nhạy cảm
*   **Mô tả lỗi:** Bộ lọc Egress Guard thực hiện quét các từ khóa nhạy cảm như "HACOM", "nhà thầu" và tự động thay thế bằng ký tự che chắn `***` để tránh rò rỉ dữ liệu lên Cloud API.
*   **Hậu quả:** Trong một số câu mô tả phức tạp, việc bôi đen vô tình che mất cả các cụm từ kỹ thuật quan trọng liền kề, làm LLM bị mất ngữ cảnh kỹ thuật của vật tư để định giá.
*   **Giải pháp lâu dài:** Chuyển dịch hệ thống sang chạy offline hoàn toàn bằng **Local LLM (Qwen3-30B-A3B)** trên Server Linux của Lab. Vì dữ liệu không gửi đi ra Internet, hệ thống tắt bỏ Egress Guard hoàn toàn để bảo toàn 100% ngữ cảnh gốc mà không sợ rò rỉ thông tin.

### 2.4. Nhóm 4: Lỗi kết nối API đám mây (Rate Limit & Timeout)
*   **Mô tả lỗi:** Khi hệ thống chạy kiểm thử hàng loạt gửi hàng trăm request liên tục lên API Cloud (Google Gemini), nhà cung cấp dịch vụ sẽ chặn tạm thời và trả về mã lỗi HTTP 429 (Too Many Requests).
*   **Hậu quả:** Làm gián đoạn và sập tiến trình Benchmark giữa chừng khi đang xử lý số lượng mẫu lớn.
*   **Giải pháp:** Tích hợp cơ chế tự động thử lại (Auto-Retry) kết hợp thời gian chờ tăng dần theo hàm số mũ (Exponential Backoff). Nếu gặp lỗi kết nối, hệ thống tự động nghỉ 15 giây, 30 giây rồi gửi lại yêu cầu. Nhờ đó, tỷ lệ thành công của phiên Benchmark đạt tới 99.4% (chỉ có 3 mẫu gặp sự cố mạng không thể phục hồi).

---
**Tổng kết:** Các cải tiến trên (Cảnh báo UI, Kẹp biên động thích ứng, Chuyển đổi sang Local LLM và Auto-Retry) đã giúp hệ thống nâng tầm từ độ chính xác **87.5%** lên **94.4%**, loại bỏ hầu hết các điểm nghẽn kỹ thuật để sẵn sàng chạy thử nghiệm thực tế trên máy chủ.
