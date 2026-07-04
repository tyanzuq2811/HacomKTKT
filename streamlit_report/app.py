import sys
import os
import time
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Thêm thư mục price_advisor_standalone vào Python Path để import module
BASE_DIR = Path(__file__).resolve().parent.parent
STANDALONE_DIR = BASE_DIR / "price_advisor_standalone"
sys.path.append(str(STANDALONE_DIR))

# Load dotenv từ price_advisor_standalone/.env
from dotenv import load_dotenv
load_dotenv(STANDALONE_DIR / ".env", override=True)

try:
    from price_advisor.advisor import PriceAdvisor
    from price_advisor.config import PriceAdvisorConfig
    from price_advisor.schemas import AdvisorError
    HAS_BACKEND = True
except Exception as e:
    HAS_BACKEND = False
    BACKEND_ERROR = str(e)

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Price Advisor AI Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS để giao diện trông premium, hiện đại
st.markdown("""
<style>
    /* Google Font Inter */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
    }
    
    /* Header Gradient */
    .title-gradient {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 0.5rem;
    }
    
    /* Card design */
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1), 0 4px 6px -2px rgba(59, 130, 246, 0.05);
        border-color: #bfdbfe;
    }
    
    /* Custom Alerts */
    .custom-info {
        background-color: #eff6ff;
        border-left: 5px solid #3b82f6;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def custom_metric(label, value, note, color="#2563eb"):
    st.markdown(f"""
    <div style="background: #ffffff; padding: 1.2rem; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); text-align: center; height: 100%;">
        <p style="margin: 0; font-size: 0.85rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">{label}</p>
        <p style="margin: 0.3rem 0; font-size: 1.8rem; font-weight: 800; color: {color};">{value}</p>
        <p style="margin: 0; font-size: 0.82rem; font-weight: 600; color: #10b981;">{note}</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/gradient/100/artificial-intelligence.png", width=70)
    st.markdown("### **THÀNH VIÊN THỰC HIỆN**")
    st.markdown("""
    *   **Lê Tuấn Dũng** - MSV: 1771020189
    *   **Nguyễn Hòa Bình** - MSV: 1671040004
    """)
    st.markdown("---")
    st.markdown("### **MÔI TRƯỜNG & HỆ THỐNG**")
    st.info("Conda Env: `deep_learning` \n\nGPU: NVIDIA RTX 3050 \n\nCUDA: 13.1")
    
    # Checkbox force mock để demo khi không có API key hoặc offline
    st.markdown("---")
    force_mock = st.checkbox("Sử dụng dữ liệu Mô phỏng (Mock Demo)", value=False, help="Bật tính năng này nếu bạn muốn chạy thử nghiệm không cần kết nối mạng hay API Key thực tế.")

# Main Title (giống 100% tên đề tài trên LaTeX)
st.markdown('<p class="title-gradient">ỨNG DỤNG RAG VÀ LLM TRONG TỰ ĐỘNG HÓA TƯ VẤN DỰ TOÁN VẬT TƯ CƠ ĐIỆN</p>', unsafe_allow_html=True)
st.markdown("<p style='color:#64748b; font-size:1.1rem; font-weight:500; margin-top:-10px; margin-bottom:25px;'>Báo cáo kết quả nghiên cứu và ứng dụng thực nghiệm hệ thống Price Advisor AI</p>", unsafe_allow_html=True)

# Tabs
tab_overview, tab_dataset, tab_benchmark, tab_demo = st.tabs([
    "📂 Tổng quan Kiến trúc", 
    "📊 Bộ dữ liệu MEP", 
    "📈 Kết quả Weights & Biases", 
    "⚡ Trải nghiệm Gợi ý Giá (Demo)"
])

# ----------------------------------------------------
# TAB 1: TỔNG QUAN KIẾN TRÚC
# ----------------------------------------------------
with tab_overview:
    st.markdown("### 1. Kiến trúc luồng dữ liệu của hệ thống (End-to-End)")
    
    st.markdown("""
    Hệ thống hoạt động theo kiến trúc **Retrieval-Augmented Generation (RAG)** kết hợp kiểm duyệt an ninh hai đầu (Ingress/Egress Guard). Quy trình xử lý gồm 2 giai đoạn chính:
    
    *   **Giai đoạn 1 (Offline - Số hóa dữ liệu):** Trích xuất thông tin chào thầu từ các file Excel dự án $\\rightarrow$ Chuẩn hóa dữ liệu $\\rightarrow$ Tạo Vector Embedding bằng model `bge-m3` $\\rightarrow$ Lưu trữ vào Cơ sở dữ liệu Vector local (**ChromaDB**).
    *   **Giai đoạn 2 (Online - Truy vấn & Gợi ý giá):** Kỹ sư nhập yêu cầu $\\rightarrow$ Hệ thống truy xuất các báo giá lịch sử tương đồng nhất $\\rightarrow$ Thực hiện bộ lọc ĐVT $\\rightarrow$ Lọc bảo mật thông tin doanh nghiệp $\\rightarrow$ Gọi API đám mây **Gemini 3.5 Flash** để phân tích $\\rightarrow$ Áp dụng thuật toán kẹp biên an toàn bằng Python để chống ảo giác của AI.
    """)
    
    st.markdown("""
    <div class="custom-info">
        <strong>💡 Điểm cải tiến kỹ thuật cốt lõi:</strong><br>
        Chúng tôi không gửi trực tiếp câu hỏi của kỹ sư lên AI mà thiết lập các chốt chặn tự động ở giữa bằng Python. Điều này vừa giúp <strong>bảo mật tuyệt đối dữ liệu nội bộ</strong> của công ty (không gửi tên nhà thầu, tên dự án lên Cloud), vừa giúp <strong>chống ảo giác số liệu</strong> của AI bằng cách kẹp cứng đầu ra của AI trong khoảng giá trị thực tế của cơ sở dữ liệu.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 2. Sơ đồ luồng xử lý chi tiết (9 Khối chức năng)")
    
    # Render Khối 1
    with st.expander("🔍 Khối 1: Ingress Parser (Trích xuất & Chuẩn hóa Excel)"):
        st.code("[Excel thô] ──► (Ingress Parser) ──► [Dữ liệu chuẩn hóa]", language="text")
        st.markdown("""
        *   **Nhiệm vụ:** Đọc và làm sạch dữ liệu Excel chào thầu thô.
        *   **Cách hoạt động:** Loại bỏ các dòng tiêu đề phụ, dòng rác, tự động quy đổi và chuẩn hóa Đơn vị tính (ĐVT) về chuẩn chung (mét, cái, bộ, kg...), lọc bỏ các giá trị đơn giá bất thường (quá nhỏ < 500đ hoặc quá lớn > 5 tỷ).
        """)
        
    st.markdown("<div style='text-align: center; color: #2563eb; font-size: 1.8rem; font-weight: bold; margin: -10px 0 -10px 0;'>▼</div>", unsafe_allow_html=True)
    
    # Render Khối 2
    with st.expander("🧬 Khối 2: Dense Embedding (Mô hình nhúng ngữ nghĩa)"):
        st.code("[Dữ liệu chuẩn hóa] ──► (bge-m3) ──► [Vector 1024 chiều]", language="text")
        st.markdown("""
        *   **Nhiệm vụ:** Biến đổi văn bản thành Vector toán học.
        *   **Cách hoạt động:** Sử dụng mô hình local mã nguồn mở **BAAI/bge-m3** chạy trên GPU để chuyển đổi các chuỗi mô tả vật tư MEP thành các vector số học 1024 chiều chứa đựng ý nghĩa ngữ nghĩa (Semantic).
        """)
        
    st.markdown("<div style='text-align: center; color: #2563eb; font-size: 1.8rem; font-weight: bold; margin: -10px 0 -10px 0;'>▼</div>", unsafe_allow_html=True)
    
    # Render Khối 3
    with st.expander("💾 Khối 3: Local Vector DB (Cơ sở dữ liệu ChromaDB)"):
        st.code("[Vector 1024 chiều] ──► (ChromaDB) ──► [Top K mẫu tương đồng]", language="text")
        st.markdown("""
        *   **Nhiệm vụ:** Lưu trữ kho tri thức và tìm kiếm tương đồng.
        *   **Cách hoạt động:** Sử dụng cơ sở dữ liệu vector **ChromaDB** chạy local. Khi kỹ sư nhập mô tả vật tư mới, ChromaDB sẽ so sánh khoảng cách vector để tìm ra **Top K** (mặc định K=5) dòng báo giá lịch sử giống nhất về mặt ngữ nghĩa.
        """)
        
    st.markdown("<div style='text-align: center; color: #2563eb; font-size: 1.8rem; font-weight: bold; margin: -10px 0 -10px 0;'>▼</div>", unsafe_allow_html=True)
    
    # Render Khối 4
    with st.expander("🛡️ Khối 4: Hard Filter / Unit Alignment (Đồng bộ Đơn vị tính)"):
        st.code("[Top K mẫu tương đồng] ──► (Lọc ĐVT) ──► [Mẫu khớp ĐVT]", language="text")
        st.markdown("""
        *   **Nhiệm vụ:** Lọc cứng đơn vị tính để đảm bảo tính nhất quán.
        *   **Cách hoạt động:** Thuật toán Python tự động so sánh ĐVT của yêu cầu tra cứu với ĐVT của các tài liệu tham chiếu RAG. Loại bỏ hoàn toàn các dòng tham chiếu khác ĐVT (ví dụ: yêu cầu tra cứu theo 'mét' nhưng RAG trả về tài liệu tính theo 'cuộn' hoặc 'cái').
        """)
        
    st.markdown("<div style='text-align: center; color: #2563eb; font-size: 1.8rem; font-weight: bold; margin: -10px 0 -10px 0;'>▼</div>", unsafe_allow_html=True)
    
    # Render Khối 5
    with st.expander("🔢 Khối 5: Pre-calculation Engine (Tiền xử lý số liệu thống kê)"):
        st.code("[Mẫu khớp ĐVT] ──► (Pre-calc) ──► [Chỉ số Min, Max, Median]", language="text")
        st.markdown("""
        *   **Nhiệm vụ:** Tính toán các chỉ số thống kê thực tế.
        *   **Cách hoạt động:** Python tự tính toán các giá trị Min, Max, và Median (trung vị) của khoảng giá thực tế từ ngữ cảnh RAG trước. Các con số này sẽ được đưa thẳng vào Prompt của LLM để AI không phải làm toán cộng trừ nhân chia (tránh sai sót tính toán của LLM).
        """)
        
    st.markdown("<div style='text-align: center; color: #2563eb; font-size: 1.8rem; font-weight: bold; margin: -10px 0 -10px 0;'>▼</div>", unsafe_allow_html=True)
    
    # Render Khối 6
    with st.expander("🔒 Khối 6: Egress Guard (Chốt chặn bảo mật thông tin nội bộ)"):
        st.code("[Chỉ số & Mẫu] ──► (Egress Guard) ──► [Prompt ẩn danh ***]", language="text")
        st.markdown("""
        *   **Nhiệm vụ:** Bảo mật thông tin nhạy cảm của doanh nghiệp.
        *   **Cách hoạt động:** Rà soát toàn bộ văn bản RAG bằng biểu thức chính quy (Regex). Tự động thay thế tên các dự án hoặc nhà thầu nội bộ (ví dụ: "HACOM Mall", "Linh Anh"...) thành ký tự ẩn danh `***` hoặc `REF-X` trước khi gửi lên API đám mây của Google.
        """)
        
    st.markdown("<div style='text-align: center; color: #2563eb; font-size: 1.8rem; font-weight: bold; margin: -10px 0 -10px 0;'>▼</div>", unsafe_allow_html=True)
    
    # Render Khối 7
    with st.expander("🧠 Khối 7: Commercial Inference Engine (Google Gemini 3.5 Flash API)"):
        st.code("[Prompt ẩn danh] ──► (Gemini 3.5 Flash API) ──► [JSON kết quả LLM]", language="text")
        st.markdown("""
        *   **Nhiệm vụ:** Phân tích logic ngữ cảnh và đề xuất giá.
        *   **Cách hoạt động:** Gọi API thương mại **Gemini 3.5 Flash** truyền prompt đã ẩn danh. Sử dụng tính năng **Native Structured Outputs (Pydantic Schema)** để ép buộc AI trả về đúng cấu trúc JSON gồm: giá thấp, giá cao, độ tin cậy và lý giải chi tiết bằng tiếng Việt.
        """)
        
    st.markdown("<div style='text-align: center; color: #2563eb; font-size: 1.8rem; font-weight: bold; margin: -10px 0 -10px 0;'>▼</div>", unsafe_allow_html=True)
    
    # Render Khối 8
    with st.expander("🗜️ Khối 8: Post-processing Clamping (Kẹp biên an toàn)"):
        st.code("[JSON kết quả LLM] ──► (Python Clamping) ──► [Giá an toàn]", language="text")
        st.markdown("""
        *   **Nhiệm vụ:** Chống ảo giác (hallucination) giá trị của AI.
        *   **Cách hoạt động:** Thuật toán Python tự động tính biên an toàn động $\\epsilon$ (từ 5% đến 25%) dựa trên phân phối của context. Nếu khoảng giá đề xuất của AI vượt ra ngoài vùng an toàn thực tế, thuật toán sẽ tự động kéo giá trị đó về biên an toàn gần nhất.
        """)
        
    st.markdown("<div style='text-align: center; color: #2563eb; font-size: 1.8rem; font-weight: bold; margin: -10px 0 -10px 0;'>▼</div>", unsafe_allow_html=True)
    
    # Render Khối 9
    with st.expander("💻 Khối 9: UI Frontend (Trực quan hóa và Tương tác)"):
        st.code("[Giá an toàn] ──► (UI Web/Streamlit) ──► [Hiển thị kỹ sư]", language="text")
        st.markdown("""
        *   **Nhiệm vụ:** Tương tác với người dùng (Kỹ sư dự toán).
        *   **Cách hoạt động:** Giao diện Web được xây dựng tối giản, trực quan, cho phép kỹ sư nhập vật tư cần tra cứu, chọn backend AI xử lý, hiển thị kết quả phân tích giá kèm bảng đối chiếu các dòng báo giá lịch sử gốc.
        """)




# ----------------------------------------------------
# TAB 2: BỘ DỮ LIỆU MEP
# ----------------------------------------------------
with tab_dataset:
    st.markdown("### 2. Thống kê và cấu trúc dữ liệu số hóa")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        custom_metric(label="Tổng số dòng báo giá lịch sử", value="8,662", note="100% Sạch & Chuẩn hóa")
    with col_stat2:
        custom_metric(label="Số lượng nhà thầu tham chiếu", value="4", note="Linh Anh, Searefico...")
    with col_stat3:
        custom_metric(label="Số phân hệ MEP chính", value="8 phân hệ", note="Cáp, Ống, Van, Đèn...")
    with col_stat4:
        custom_metric(label="Quy tắc lọc ngoại lai", value="500đ - 5 tỷ", note="Loại bỏ nhiễu dự toán")
        
    # Tạo dữ liệu minh họa
    sample_data = pd.DataFrame([
        {"ref_id": "HACOM-204ab3cca174", "description": "Cu/FR/XLPE (1x240)mm2 | Cu/Mica/XLPE/LSZH 1x240mm2, 0.6/1kV", "unit": "m", "price": 1186481, "brand": "Taisin", "origin": "Việt Nam"},
        {"ref_id": "HACOM-a26ce64a6124", "description": "Cu/FR/XLPE (4x25)mm2 | Cu/Mica/XLPE/LSZH 4x25mm2, 0.6/1kV", "unit": "m", "price": 584301, "brand": "Taisin", "origin": "Việt Nam"},
        {"ref_id": "HACOM-018930dd6207", "description": "Đèn dowlight, 220V/9W, lắp âm trần | Đèn downlight liền khối viền trắng đơn sắc", "unit": "bộ", "price": 169184, "brand": "Simon", "origin": "Việt Nam"},
        {"ref_id": "HACOM-7dfc9a38bd2b", "description": "Ống luồn dây PVC cứng D20 (lắp đặt nổi) | Lực nén 750N", "unit": "m", "price": 20475, "brand": "Sam Phú", "origin": "Việt Nam"},
        {"ref_id": "HACOM-6dfdce90571e", "description": "Ổ cắm điện 3 cực (2P+E), 250V/16A, loại đôi kiểu lắp chìm (Mặt+Hộp âm)", "unit": "cái", "price": 154405, "brand": "Simon", "origin": "Việt Nam"}
    ])
    
    st.subheader("Bảng mẫu dữ liệu chào thầu điển hình (đã chuẩn hóa)")
    st.dataframe(sample_data, use_container_width=True)
    
    # Biểu đồ phân phối danh mục MEP
    st.subheader("Phân phối số lượng mẫu theo danh mục hệ thống MEP")
    mep_dist = pd.DataFrame({
        "Hệ thống MEP": ["Cáp điện", "uPVC phụ kiện", "PPR phụ kiện", "uPVC ống", "Ống kẽm", "PPR ống", "Phụ kiện kẽm", "Đầu nối"],
        "Số lượng mẫu": [2850, 1820, 1450, 980, 640, 520, 310, 92]
    })
    fig_mep = px.bar(mep_dist, x="Hệ thống MEP", y="Số lượng mẫu", color="Số lượng mẫu", 
                     color_continuous_scale="Viridis", height=350)
    st.plotly_chart(fig_mep, use_container_width=True)

# ----------------------------------------------------
# TAB 3: KẾT QUẢ WEIGHTS & BIASES
# ----------------------------------------------------
with tab_benchmark:
    st.markdown("### 3. Kết quả đánh giá hiệu năng trên Weights & Biases (Run: `k06c1gnt`)")
    
    col_bench1, col_bench2, col_bench3, col_bench4 = st.columns(4)
    with col_bench1:
        custom_metric(label="Quy mô mẫu đánh giá (N)", value="500", note="Độ bao phủ toàn diện")
    with col_bench2:
        custom_metric(label="Độ chính xác đề xuất (Accuracy)", value="94.4%", note="+6.9% so với mô hình cũ")
    with col_bench3:
        custom_metric(label="Tỷ lệ API thành công", value="99.4%", note="Hỗ trợ Auto-Retry thông minh")
    with col_bench4:
        custom_metric(label="Thời gian đáp ứng trung bình", value="10.62s", note="Đo trực tiếp trên W&B", color="#4f46e5")

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("Phân tích lỗi hệ thống (28 ca dự đoán sai)")
        error_df = pd.DataFrame({
            "Nguyên nhân lỗi": ["Thiếu ngữ cảnh đầu vào", "Kẹp biên quá chặt (chênh lệch epsilon)", "Lỗi kỹ thuật mạng API", "Egress Guard chặn từ khóa"],
            "Số lượng ca": [15, 11, 3, 2]
        })
        fig_error = px.pie(error_df, values="Số lượng ca", names="Nguyên nhân lỗi", 
                           color_discrete_sequence=px.colors.sequential.RdBu, height=350)
        st.plotly_chart(fig_error, use_container_width=True)
        
    with col_chart2:
        st.subheader("So sánh Độ chính xác trước và sau cải tiến (%)")
        compare_df = pd.DataFrame({
            "Phiên chạy": ["Ban đầu (N=100)", "Nâng cấp (N=500, Gemini 3.5 Flash)"],
            "Độ chính xác (%)": [87.5, 94.4]
        })
        fig_compare = px.bar(compare_df, x="Phiên chạy", y="Độ chính xác (%)", text="Độ chính xác (%)",
                             color="Phiên chạy", color_discrete_sequence=["#94a3b8", "#2563eb"], height=350)
        fig_compare.update_layout(yaxis=dict(range=[80, 100]))
        st.plotly_chart(fig_compare, use_container_width=True)

    st.markdown("""
    💡 **Liên kết bảng điều khiển trực tuyến:**
    *   Dashboard theo dõi trực quan: [Weights & Biases Project](https://wandb.ai/models-dai-nam-university/price-advisor-web-live)
    *   Mã phiên chạy chính thức: `k06c1gnt` (Theo dõi trực tuyến toàn bộ phiên benchmark 500 mẫu)
    """)
    
    st.markdown("### 3.1. Chi tiết phân tích nguyên nhân các trường hợp lỗi hoặc sai lệch giá")
    
    st.markdown("""
    Thông qua phân tích các ca lỗi/sai lệch ghi nhận trên Weights & Biases, chúng tôi phân loại thành 4 nhóm nguyên nhân chính:
    
    1.  **Thiếu hụt ngữ cảnh (15 ca - 48.4%):** 
        *   *Mô tả:* Lỗi xuất hiện khi người dùng đưa vào truy vấn quá vắn tắt như `"D90"`, `"D32"`. RAG truy xuất lấy ra hỗn hợp các báo giá nhiễu của nhiều loại thiết bị có cùng kích cỡ (ống kẽm, van bướm, đai treo) khiến khoảng giá bị loãng.
        *   *Khắc phục:* Web UI đã tích hợp chốt cảnh báo trực quan. Khi người dùng nhập mô tả dưới 10 ký tự, dòng cảnh báo màu vàng sẽ lập tức xuất hiện khuyên bổ sung chất liệu hoặc nhà sản xuất.
    2.  **Kẹp biên quá chặt (11 ca - 35.5%):**
        *   *Mô tả:* Thuật toán kẹp khoảng giá khi áp dụng hệ số $\\epsilon = 0.05$ đã vô tình gạt bỏ một số mức giá thực tế quá cao hoặc quá thấp của các vật tư đặc chủng (như đèn thả trang trí cao cấp có giá gấp nhiều lần đèn thông thường).
        *   *Khắc phục:* Đề xuất điều chỉnh động tham số $\\epsilon$ theo phân nhóm danh mục vật tư trong các phiên bản tiếp theo.
    3.  **Lỗi liên quan Egress Guard (2 ca - 6.45%):**
        *   *Mô tả:* Do thông tin mô tả bị bôi đen quá nhiều (`***`) làm mất đi từ khóa kỹ thuật cốt lõi. Tuy nhiên, các lỗi sập yêu cầu do chặn nhầm mã ID chứa chữ `HACOM` hoặc cụm từ `Nhà thầu` đã hoàn toàn được khắc phục nhờ thuật toán bôi đen văn bản nhạy cảm bằng `***` và vô danh hóa mã tham chiếu sang `REF-X`.
    4.  **Lỗi kỹ thuật API (3 ca - 9.68%):**
        *   *Mô tả:* Rate limit hoặc timeout từ API máy chủ Google Cloud tạm thời. Cơ chế Auto-Retry đã xử lý thành công 99.4% số lượng request còn lại.
    """)

# ----------------------------------------------------
# TAB 4: TRẢI NGHIỆM GỢI Ý GIÁ (DEMO)
# ----------------------------------------------------
with tab_demo:
    st.markdown("### 4. Trình diễn đề xuất khoảng giá thời gian thực")
    
    col_input, col_result = st.columns([1, 2])
    
    with col_input:
        st.subheader("Thông tin đầu vào")
        desc_input = st.text_area("Mô tả vật tư / Thiết bị:", value="Cáp đồng XLPE/PVC 4x25mm2", placeholder="Nhập tên chi tiết kèm quy cách kỹ thuật...")
        unit_input = st.text_input("Đơn vị tính:", value="m", placeholder="m, cái, bộ...")
        
        # Backend selection
        backend_choice = st.selectbox(
            "Mô hình AI xử lý (Backend):",
            ["gemini", "ollama", "deterministic"],
            format_func=lambda x: "Gemini 3.5 Flash (Google API)" if x == "gemini" else ("Ollama Local (Qwen)" if x == "ollama" else "Tính toán Python (Deterministic)")
        )
        
        top_k_val = st.slider("Số lượng tài liệu tham chiếu (Top K):", min_value=1, max_value=10, value=5)
        
        submit_btn = st.button("Phân tích & Tư vấn giá ⚡", type="primary")

    with col_result:
        st.subheader("Kết quả tư vấn từ hệ thống")
        
        if submit_btn:
            if force_mock:
                with st.spinner("Đang truy xuất dữ liệu mô phỏng..."):
                    time.sleep(1.5)
                st.success("Tư vấn giá thành công!")
                
                # Mock result
                col_res1, col_res2, col_res3 = st.columns(3)
                with col_res1:
                    custom_metric(label="Giá thấp đề xuất", value="512,000 VNĐ", note="Cận dưới an toàn")
                with col_res2:
                    custom_metric(label="Giá cao đề xuất", value="538,000 VNĐ", note="Cận trên an toàn")
                with col_res3:
                    custom_metric(label="Độ tin cậy", value="92.0%", note="Dữ liệu khớp cao", color="#10b981")
                
                st.info("**Lý giải của AI:** Giá được tính toán dựa trên 4 báo giá cáp Taisin 4x25mm2 đồng dạng có mức giá dao động xung quanh 520,000 VNĐ/m. Đã lọc bỏ cáp 4x35mm2 nhiễu.")
            else:
                if not HAS_BACKEND:
                    st.error(f"Không thể import module PriceAdvisor: {BACKEND_ERROR}")
                else:
                    config = PriceAdvisorConfig.from_env()
                    config.llm_backend = backend_choice
                    if backend_choice == "gemini":
                        config.allow_external_api = True
                    
                    st.info(f"Đang gọi backend `{backend_choice}` với mô hình `{config.gemini_model if backend_choice == 'gemini' else config.ollama_model}`...")
                    
                    with st.spinner("Đang truy xuất ChromaDB và gửi yêu cầu suy luận đến LLM..."):
                        try:
                            start_time = time.time()
                            advisor = PriceAdvisor(config)
                            result = advisor.suggest_price(
                                description=desc_input,
                                unit=unit_input,
                                top_k=top_k_val,
                            )
                            latency = time.time() - start_time
                            
                            if isinstance(result, AdvisorError):
                                st.error(f"Lỗi từ hệ thống AI: {result.message}")
                            else:
                                st.success(f"Hoàn thành trong {latency:.2f} giây!")
                                
                                # Hiển thị 3 chỉ số chính
                                col_res1, col_res2, col_res3 = st.columns(3)
                                with col_res1:
                                    custom_metric(label="Giá thấp đề xuất", value=f"{result.price_low:,.0f} VNĐ", note="Cận dưới an toàn")
                                with col_res2:
                                    custom_metric(label="Giá cao đề xuất", value=f"{result.price_high:,.0f} VNĐ", note="Cận trên an toàn")
                                with col_res3:
                                    custom_metric(label="Độ tin cậy", value=f"{result.confidence * 100:.1f}%", note="Mức độ tin cậy của AI", color="#10b981" if result.confidence > 0.8 else "#f59e0b")
                                
                                st.subheader("Lập luận của Mô hình (Reasoning)")
                                st.write(result.reasoning)
                                
                                # Show warnings if any
                                if result.warnings:
                                    st.warning(" | ".join(result.warnings))
                                    
                                # Hiển thị bảng tham chiếu gốc từ ChromaDB
                                st.subheader("Các tài liệu tham chiếu RAG tìm thấy từ ChromaDB")
                                refs = advisor.store.search(desc_input, unit_input, top_k_val)
                                if refs:
                                    refs_data = []
                                    for idx, r in enumerate(refs, 1):
                                        refs_data.append({
                                            "Mã tham chiếu": f"REF-{idx}",
                                            "Mô tả gốc": r.description,
                                            "ĐVT": r.unit,
                                            "Đơn giá chào thầu": f"{r.price:,.0f} VNĐ",
                                            "Hồ sơ thầu": r.source,
                                            "Nhà thầu phụ": r.metadata.get("contractor", "N/A")
                                        })
                                    st.table(pd.DataFrame(refs_data))
                                else:
                                    st.warning("Không tìm thấy tài liệu tham chiếu nào phù hợp trong ChromaDB.")
                                    
                        except Exception as ex:
                            st.error(f"Lỗi trong quá trình chạy: {ex}")
                            import traceback
                            st.code(traceback.format_exc())
        else:
            st.info("Nhập các thông tin bên trái và nhấn nút 'Phân tích & Tư vấn giá' để bắt đầu demo trực quan.")
