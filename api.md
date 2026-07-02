# Lộ trình Triển khai Thực tế & Tích hợp LLM cho PriceAdvisor

**Bối cảnh:** PriceAdvisor là module mở rộng (Phase 2), cắm nối trực tiếp vào Lớp Xử lý (Python Engine) và Lớp API (FastAPI) của kiến trúc Phase 1. Mục tiêu là xây dựng một luồng RAG (Retrieval-Augmented Generation) để LLM tư vấn giá tham khảo nội bộ. Tài liệu này cung cấp lộ trình từ lúc xây dựng nền tảng đến khi đưa vào vận hành thực tế (Production).

---

## 1. Luồng công việc Kỹ thuật (Technical Workflow)

Khi hệ thống đi vào hoạt động, đây là luồng xử lý tự động chạy ngầm ngay sau **Bước 3 (ComparisonEngine)** của Phase 1:

1. **Kích hoạt (Async):** `ComparisonEngine` phát hiện hạng mục thiếu giá (cấp 1-4) và đẩy yêu cầu vào `BackgroundTasks` của FastAPI.
2. **Truy vấn (Retrieval):** Tìm kiếm vector các hạng mục tương đồng nhất trong Kho giá nội bộ (`pgvector`). Toàn bộ chạy Local.
3. **Ẩn danh (Egress Guard):** Xóa tên dự án, nhà thầu, mã nội bộ. Chỉ đóng gói mô tả vật tư và lịch sử giá thành Prompt.
4. **Suy luận (LLM Inference):** Gọi LLM (qua API ngoài hoặc Local) để đọc hiểu dữ liệu và sinh ra cấu trúc JSON (Khoảng giá + Lý do).
5. **Kiểm duyệt (Validator):** Hệ thống lọc kết quả ảo tưởng, đối chiếu đơn vị tính, biên độ sai số.
6. **Lưu trữ & Hiển thị:** Ghi vào các trường `suggested_*` của bảng `BOQItem` trên PostgreSQL và hiển thị cột "Giá gợi ý" trên React/Vite UI để người dùng Chấp nhận/Từ chối.

---

## 2. Lộ trình Triển khai Thực tế (Implementation Roadmap)

Thay vì đập đi xây lại, lộ trình được chia thành 4 giai đoạn cuốn chiếu để giảm rủi ro và tối ưu chi phí đầu tư hạ tầng.

### Giai đoạn 1: Xây dựng nền tảng Dữ liệu (Data Foundation)
*LLM chỉ thông minh khi dữ liệu RAG sạch. Đây là bước quan trọng nhất.*
* **Nhiệm vụ:** Gom toàn bộ dữ liệu gói thầu cũ, catalogue, dự toán lịch sử.
* **Hành động:** * Viết script ETL (Extract, Transform, Load) để làm sạch, chuẩn hóa chuỗi định dạng (ví dụ: quy hết `m2`, `mét vuông` về `m²`).
  * Sử dụng một mô hình Embedding nhẹ (như `bge-m3` chạy local) để chuyển đổi text thành vector.
  * Lưu trữ vào PostgreSQL qua extension **`pgvector`** để tận dụng DB sẵn có của Phase 1.

### Giai đoạn 2: Prototype & Đánh giá (Sử dụng API Thương mại)
*Mục tiêu là kiểm chứng tính khả thi (PoC) nhanh nhất với chi phí rẻ nhất.*
* **Nhiệm vụ:** Tích hợp LLM, tinh chỉnh Prompt và luồng Egress Guard.
* **Hành động:**
  * Mở kết nối có kiểm soát (Gateway) để gọi API các mô hình thương mại (OpenAI, Claude, Gemini).
  * Đánh giá chất lượng của phần "Lý do" (Reasoning) do AI sinh ra.
  * Tinh chỉnh System Prompt để ép AI luôn trả về đúng định dạng JSON mà hệ thống yêu cầu.

### Giai đoạn 3: Chuyển đổi Production (Self-host Local LLM)
*Mục tiêu là ngắt hoàn toàn kết nối Internet, đảm bảo bảo mật 100% hồ sơ thầu doanh nghiệp.*
* **Nhiệm vụ:** Đưa mô hình AI về chạy trực tiếp trên server LAN của công ty.
* **Hành động:**
  * Triển khai mô hình Open-weight (ví dụ: Qwen2.5, Llama 3) lên server có GPU nội bộ.
  * Sử dụng các engine inference như **vLLM** hoặc **Ollama**. Các công cụ này cung cấp API nội bộ giả lập chuẩn OpenAI (OpenAI-compatible endpoints).
  * **Chuyển đổi liền mạch:** Kỹ sư chỉ cần đổi `base_url` trong mã nguồn FastAPI từ `https://api.openai.com...` thành `http://[IP-Server-Nội-Bộ]:8000/v1` mà **không cần sửa bất kỳ logic code nào**.

### Giai đoạn 4: Vòng lặp học hỏi (Human-in-the-loop)
* **Nhiệm vụ:** Đưa lên Web UI cho chuyên viên sử dụng và thu thập dữ liệu nhãn.
* **Hành động:** Chuyên viên MEP thao tác Accept/Reject trên UI. Các kết quả Accept được tự động dán nhãn là dữ liệu chất lượng cao, định kỳ nạp ngược lại vào Kho giá (Vector DB) để hệ thống ngày càng thông minh.

---

## 3. Danh sách, Bảng giá và Benchmark các LLM API (Cập nhật 2026)

*Bảng giá tính trên 1 triệu token. Sử dụng chủ yếu cho Giai đoạn 2 (Prototype).*

### A. Phân khúc Cao cấp (Tác vụ suy luận MEP phức tạp)
*Phù hợp cho các vật tư có mô tả kỹ thuật dài, nhiều thông số chồng chéo.*

| Nhà cung cấp | Mô hình | Giá Input | Giá Output | Nhận xét thực chiến |
| :--- | :--- | :--- | :--- | :--- |
| **Anthropic** | Claude Opus 4.6 | $5.00 | $25.00 | Dẫn đầu về độ chính xác và bám sát cấu trúc JSON. Tối ưu khi sai sót gây rủi ro cao. |
| **Google** | Gemini 3.1 Pro (Preview) | $2.00 | $12.00 | Lựa chọn cân bằng nhất về hiệu năng và chi phí. Sức mạnh tương đương Opus nhưng rẻ hơn 60%. |
| **OpenAI** | GPT-5.4 | $2.50 | $15.00 | Đỉnh cao về sử dụng công cụ (Tool Use). Ổn định, hệ sinh thái hỗ trợ lập trình viên tốt nhất. |

### B. Phân khúc Tầm trung & Tiết kiệm
*Khuyên dùng cho PriceAdvisor. AI chỉ làm nhiệm vụ tổng hợp RAG, không cần mô hình quá nặng.*

| Nhà cung cấp | Mô hình | Giá Input | Giá Output | Đặc điểm nổi bật |
| :--- | :--- | :--- | :--- | :--- |
| **Anthropic** | Claude Sonnet 4.6 | $3.00 | $15.00 | Xử lý RAG xuất sắc, văn phong giải thích logic, chuyên nghiệp. |
| **OpenAI** | GPT-4.1 Mini | $0.40 | $1.60 | Rất nhanh, lý tưởng để xử lý dữ liệu JSON số lượng lớn với chi phí cực rẻ. |
| **Google** | Gemini 2.5 Flash | $0.30 | $2.50 | Tốc độ phản hồi (latency) cực thấp, rẻ hơn 10 lần so với bản Pro. |

### C. Phân khúc Siêu rẻ (Định tuyến sơ bộ)

| Nhà cung cấp | Mô hình | Giá Input | Giá Output | Ưu điểm chính |
| :--- | :--- | :--- | :--- | :--- |
| **DeepSeek** | DeepSeek V3.2 | $0.14 | $0.28 | Giá cực kỳ cạnh tranh, làm tốt các tác vụ tóm tắt hoặc so khớp cơ bản. |
| **Google** | Gemini 2.5 Flash-Lite| $0.10 | $0.40 | Lựa chọn tối giản và tiết kiệm tối đa. |
| **OpenAI** | GPT-4.1 Nano | $0.10 | $0.40 | Rẻ gấp 20 lần bản Mini, chuyên dùng cho phân loại nhị phân. |

---

## 4. Khuyến nghị Chiến lược & Lựa chọn Mô hình

Để tối ưu giữa chi phí, hiệu năng và bảo mật, chiến lược lựa chọn mô hình nên áp dụng theo từng giai đoạn:

### Đối với Giai đoạn Prototype (Dùng API Thương mại):
1. **Lúc bắt đầu tinh chỉnh:** Bắt đầu với **Claude Sonnet 4.6** hoặc **Gemini 3.1 Pro**. Năng lực lý luận mạnh của nhóm này giúp bạn dễ dàng viết Prompt và đánh giá xem định dạng JSON có trả về chuẩn không.
2. **Khi mở rộng Test nội bộ (Scale-up):** Áp dụng Kỹ thuật *Prompt Caching* và hạ cấp xuống **GPT-4.1 Mini** hoặc **Gemini 2.5 Flash**. Điều này giúp test khối lượng lớn dữ liệu (hàng nghìn dòng BOQ) với chi phí chỉ vài chục USD/tháng.

### Đối với Giai đoạn Production (Self-host Local):
Khi hệ thống đã ổn định và sẵn sàng đóng gói chạy trong mạng nội bộ, hãy cắt toàn bộ API thương mại và chuyển sang các mô hình mã nguồn mở (Open-weight). 
* **Lựa chọn hàng đầu:** **Qwen2.5-7B-Instruct** (hoặc dòng Llama 3.x 8B).
* **Lý do:** Các mô hình tham số tầm trung (7B-8B) này khi chạy trên nền tảng **vLLM** tiêu tốn rất ít tài nguyên phần cứng (chỉ cần 1 card GPU tầm trung như RTX 4090 hoặc 3090). Tuy nhỏ nhưng khả năng đọc hiểu tài liệu, lập luận tiếng Việt và xuất JSON của chúng đã tiệm cận các mô hình thương mại lớn, đáp ứng hoàn hảo bài toán RAG nội bộ của PriceAdvisor.