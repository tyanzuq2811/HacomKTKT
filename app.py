from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import streamlit as st

from security import configure_offline_environment, deny_external_network, secure_workspace

configure_offline_environment()

from core.config import EnterpriseConfig
from core.models import CompareThresholds
from core.pipeline import compare_bidder_files, compare_tender_files
from ocr.config import OCRConfig
from ocr.pipeline import run_ocr

st.set_page_config(page_title="HSMT Enterprise AI", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
.stApp {background:#f5f7fb}
[data-testid="stSidebar"] {background:#12233f}
[data-testid="stSidebar"] * {color:#eef4ff!important}
.hero {padding:20px 24px;border-radius:16px;background:linear-gradient(120deg,#102a43,#245d8f);color:white;margin-bottom:16px}
.hero h1 {margin:0;font-size:27px}.hero p{margin:8px 0 0;color:#dbeafe}
.card {background:white;border:1px solid #dbe3ec;border-radius:12px;padding:14px}
</style>
<div class="hero"><h1>🛡️ HSMT Enterprise AI</h1><p>OCR bảng scan · So sánh HSMT/HSDT · Phát hiện bất thường giá và tên hạng mục · Xử lý cục bộ</p></div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.subheader("Ngưỡng đánh giá")
    price_warn = st.slider("Cảnh báo đơn giá", 1, 50, 10) / 100
    price_critical = st.slider("Bất thường đơn giá", 2, 100, 20) / 100
    qty_warn = st.slider("Cảnh báo khối lượng", 1, 30, 5) / 100
    qty_critical = st.slider("Bất thường khối lượng", 2, 60, 15) / 100
    name_review = st.slider("Tên cần kiểm tra", 40, 95, 78) / 100
    semantic = st.checkbox("Bật BGE-M3 local khi đã cài", value=True)
    st.divider()
    st.success("🔒 Strict local: không gửi hồ sơ ra Internet")
    st.caption("Các model phải được cài trong máy chủ nội bộ trước khi chạy.")


def make_config() -> EnterpriseConfig:
    cfg = EnterpriseConfig.from_env()
    cfg.thresholds = CompareThresholds(
        price_warn_pct=price_warn,
        price_critical_pct=price_critical,
        quantity_warn_pct=qty_warn,
        quantity_critical_pct=qty_critical,
        name_review_score=name_review,
        name_reject_score=max(0.35, name_review - 0.22),
    )
    cfg.enable_semantic_matching = semantic
    return cfg


def save_upload(upload, path: Path) -> Path:
    path.write_bytes(upload.getvalue())
    return path


def result_preview(result):
    s = result.summary
    cols = st.columns(6)
    cols[0].metric("Hạng mục chuẩn", f"{s.total_reference_items:,}")
    cols[1].metric("Dòng đối chiếu", f"{s.total_rows:,}")
    cols[2].metric("Khớp chính xác", f"{s.exact_matches:,}")
    cols[3].metric("Khớp tương đối", f"{s.fuzzy_matches:,}")
    cols[4].metric("Cảnh báo", f"{s.warning_rows:,}")
    cols[5].metric("Bất thường", f"{s.critical_rows:,}")
    df = pd.DataFrame(result.iter_flat())
    if not df.empty:
        severities = ["Tất cả"] + sorted(df["Mức độ"].dropna().unique().tolist())
        c1, c2 = st.columns([1, 3])
        severity = c1.selectbox("Lọc mức độ", severities)
        query = c2.text_input("Tìm mã hiệu/tên hạng mục")
        shown = df
        if severity != "Tất cả":
            shown = shown[shown["Mức độ"] == severity]
        if query:
            mask = shown.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
            shown = shown[mask]
        st.dataframe(shown, use_container_width=True, height=520)


t1, t2, t3 = st.tabs(["HSMT ↔ nhiều HSDT", "So sánh các HSDT", "OCR PDF/ảnh → Excel"])

with t1:
    hsmt = st.file_uploader("HSMT (.xlsx)", type=["xlsx"], key="hsmt")
    bids = st.file_uploader("Các HSDT (.xlsx) — chọn nhiều file", type=["xlsx"], accept_multiple_files=True, key="bids")
    names = []
    if bids:
        st.markdown("**Tên nhà thầu**")
        for i, upload in enumerate(bids):
            names.append(st.text_input(upload.name, value=Path(upload.name).stem, key=f"bid_name_{i}"))
    if st.button("Chạy đối chiếu HSMT/HSDT", type="primary", disabled=not hsmt or not bids):
        with st.spinner("Đang đọc file theo luồng, lập chỉ mục tên và tính bất thường..."):
            with secure_workspace() as work, deny_external_network(True):
                hsmt_path = save_upload(hsmt, work / "HSMT.xlsx")
                pairs = []
                for i, upload in enumerate(bids):
                    path = save_upload(upload, work / f"HSDT_{i:03d}.xlsx")
                    pairs.append((names[i], path))
                out = work / "Bao_cao_HSMT_HSDT.xlsx"
                result = compare_tender_files(hsmt_path, pairs, out, make_config())
                st.session_state["t1_result"] = result
                st.session_state["t1_file"] = out.read_bytes()
    if "t1_result" in st.session_state:
        result_preview(st.session_state["t1_result"])
        st.download_button("Tải báo cáo Excel", st.session_state["t1_file"], "Bao_cao_HSMT_HSDT.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with t2:
    bids2 = st.file_uploader("Tải ít nhất 2 HSDT (.xlsx)", type=["xlsx"], accept_multiple_files=True, key="bids2")
    names2 = []
    if bids2:
        for i, upload in enumerate(bids2):
            names2.append(st.text_input(upload.name, value=Path(upload.name).stem, key=f"bid2_name_{i}"))
    if st.button("So sánh giữa các nhà thầu", type="primary", disabled=not bids2 or len(bids2) < 2):
        with st.spinner("Đang xây danh mục hợp nhất và ma trận giá..."):
            with secure_workspace() as work, deny_external_network(True):
                pairs = []
                for i, upload in enumerate(bids2):
                    path = save_upload(upload, work / f"BID_{i:03d}.xlsx")
                    pairs.append((names2[i], path))
                out = work / "Bao_cao_so_sanh_HSDT.xlsx"
                result = compare_bidder_files(pairs, out, make_config())
                st.session_state["t2_result"] = result
                st.session_state["t2_file"] = out.read_bytes()
    if "t2_result" in st.session_state:
        result_preview(st.session_state["t2_result"])
        st.download_button("Tải báo cáo Excel", st.session_state["t2_file"], "Bao_cao_so_sanh_HSDT.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with t3:
    scan = st.file_uploader("PDF scan hoặc ảnh", type=["pdf", "png", "jpg", "jpeg", "tif", "tiff"], key="scan")
    c1, c2, c3 = st.columns(3)
    device = c1.selectbox("Thiết bị", ["gpu:0", "cpu"])
    dpi = c2.selectbox("DPI render", [200, 300, 400], index=1)
    upscale = c3.selectbox("Phóng ô nhỏ", [2.0, 3.0, 4.0], index=1)
    if st.button("Chạy OCR bảo mật", type="primary", disabled=not scan):
        with st.spinner("Đang xoay trang, dò lưới, cắt ô và OCR theo batch..."):
            try:
                with secure_workspace() as work, deny_external_network(True):
                    src = save_upload(scan, work / f"scan{Path(scan.name).suffix.lower()}")
                    out = work / "Ket_qua_OCR.xlsx"
                    cfg = OCRConfig.from_env()
                    cfg.device = device; cfg.render_dpi = dpi; cfg.upscale_factor = upscale
                    doc = run_ocr(src, out, cfg)
                    st.session_state["ocr_doc"] = doc
                    st.session_state["ocr_file"] = out.read_bytes()
            except Exception as exc:
                st.error(str(exc))
    if "ocr_doc" in st.session_state:
        doc = st.session_state["ocr_doc"]
        cols = st.columns(4)
        cols[0].metric("Trang", len(doc.pages))
        cols[1].metric("Dòng OCR", len(doc.rows))
        review_count = sum(bool(r.get("ocr_flags")) for r in doc.rows)
        cols[2].metric("Dòng cần kiểm", review_count)
        cols[3].metric("Chế độ", "Local-only")
        st.dataframe(pd.DataFrame(doc.rows), use_container_width=True, height=480)
        st.download_button("Tải Excel OCR", st.session_state["ocr_file"], "Ket_qua_OCR.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
