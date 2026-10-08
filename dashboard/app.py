"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Web Dashboard Giám Sát & Quản Lý Phạt Nguội (Streamlit)
TASK: 25 & 26 - GIAO DIỆN GIÁM SÁT TRỰC QUAN (VERSION 1.4)
==============================================================================
"""

import os
import sys
import time
import datetime
import cv2
import numpy as np
import pandas as pd
import streamlit as st

# Thêm thư mục gốc vào đường dẫn import
sys.path.insert(0, os.path.abspath("."))

from camera import VideoReader
from roi import ROIManager
from tracking import ObjectTracker, TemporalVerifier, TrackState
from violation import ViolationChecker
from evidence import EvidenceSaver
from database import ViolationDatabase
from utils import FPSTracker, draw_fps_badge, draw_detection


# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Hệ Thống Giám Sát Lấn Chiếm Vỉa Hè CCTV",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tùy biến CSS giao diện hiện đại
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #757575;
        margin-bottom: 25px;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #334155;
        text-align: center;
    }
    .badge-confirmed {
        background-color: #ef4444;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-suspected {
        background-color: #f59e0b;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_database():
    return ViolationDatabase(db_path="data/surveillance.db")


db = get_database()

# Sidebar: Điều hướng chính
st.sidebar.image("https://img.icons8.com/color/96/cctv.png", width=70)
st.sidebar.title("CCTV Surveillance")
st.sidebar.markdown("**Đồ Án Tốt Nghiệp 2026**")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "CHỨC NĂNG CHÍNH",
    ["📊 Tổng Quan Hệ Thống", "📹 Giám Sát Trực Tiếp", "🔍 Tra Cứu Vi Phạm & Bằng Chứng", "⚙️ Quản Lý Vùng Vỉa Hè (ROI)"]
)

st.sidebar.markdown("---")
# Quick stats trên sidebar
stats = db.get_statistics()
st.sidebar.metric("Tổng số vụ vi phạm", stats["total_violations"])
st.sidebar.metric("Vi phạm hôm nay", stats["today_violations"])


# ==============================================================================
# TRANG 1: TỔNG QUAN HỆ THỐNG
# ==============================================================================
if menu == "📊 Tổng Quan Hệ Thống":
    st.markdown('<div class="main-header">🚨 HỆ THỐNG GIÁM SÁT BIỂN HIỆU LẤN CHIẾM VỈA HÈ</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Phát hiện, định danh theo thời gian và quản lý xử phạt thông qua camera an ninh CCTV cố định</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📹 Điểm Giám Sát Có Dữ Liệu", len(stats["violations_by_camera"]))
    with col2:
        st.metric("🚨 Tổng Số Vụ Vi Phạm", stats["total_violations"])
    with col3:
        st.metric("📅 Vi Phạm Trong Ngày", stats["today_violations"])
    with col4:
        st.metric("⚡ Thuật Toán AI & Tracking", "YOLOv8 + ByteTrack")

    st.markdown("---")
    st.subheader("📈 Phân Bố Vi Phạm Theo Từng Vị Trí Camera")
    
    if stats["violations_by_camera"]:
        df_cam = pd.DataFrame(list(stats["violations_by_camera"].items()), columns=["Camera ID", "Số Vụ Vi Phạm"])
        st.bar_chart(df_cam.set_index("Camera ID"))
    else:
        st.info("Chưa có bản ghi vi phạm nào trong cơ sở dữ liệu. Hãy chạy tính năng Giám Sát Trực Tiếp để thu thập dữ liệu.")

    st.markdown("---")
    st.subheader("🕒 Các Vụ Vi Phạm Gần Nhất")
    recent_violations = db.get_violations(limit=5)
    if recent_violations:
        df_recent = pd.DataFrame(recent_violations)
        st.dataframe(df_recent[["id", "camera_id", "track_id", "timestamp", "overlap_pct", "full_image_path"]], use_container_width=True)
    else:
        st.write("Chưa có vi phạm nào gần đây.")


# ==============================================================================
# TRANG 2: GIÁM SÁT TRỰC TIẾP
# ==============================================================================
elif menu == "📹 Giám Sát Trực Tiếp":
    st.markdown('<div class="main-header">📹 GIÁM SÁT CAMERA THỜI GIAN THỰC</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Luồng phân tích hình ảnh AI trực tiếp kèm cảnh báo thời gian thực</div>', unsafe_allow_html=True)

    col_ctrl, col_view = st.columns([1, 3])

    with col_ctrl:
        st.subheader("⚙️ Cấu Hình Luồng")
        # Chọn nguồn
        video_dir = "data/videos"
        v_files = [f for f in os.listdir(video_dir) if f.lower().endswith(('.mp4', '.avi', '.mov'))] if os.path.exists(video_dir) else []
        img_dir = "data/images"
        i_files = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))] if os.path.exists(img_dir) else []

        source_options = [f"Video: {f}" for f in v_files] + [f"Ảnh: {f}" for f in i_files]
        selected_src = st.selectbox("Nguồn dữ liệu CCTV", source_options) if source_options else None

        # Chọn cấu hình ROI
        config_files = [f for f in os.listdir("configs") if f.endswith(".json")] if os.path.exists("configs") else []
        selected_cfg = st.selectbox("Cấu hình Vỉa hè (ROI)", config_files) if config_files else None

        # Tùy chỉnh tham số
        st.markdown("---")
        st.markdown("**Tham số thuật toán:**")
        conf_thresh = st.slider("Ngưỡng tin cậy AI (Confidence)", 0.1, 0.9, 0.20, 0.05)
        overlap_thresh = st.slider("Ngưỡng lấn chiếm diện tích (%)", 10, 80, 30, 5)
        confirm_n_frames = st.slider("Số frames xác nhận (N-frames)", 3, 30, 15, 1)

        btn_start = st.button("▶️ Khởi Động Giám Sát", use_container_width=True, type="primary")
        btn_stop = st.button("⏹️ Dừng Giám Sát", use_container_width=True)

    with col_view:
        frame_placeholder = st.empty()
        metrics_placeholder = st.empty()
        log_placeholder = st.empty()

        if btn_start and selected_src and selected_cfg:
            # Xác định đường dẫn nguồn
            if selected_src.startswith("Video: "):
                media_path = os.path.join("data/videos", selected_src.replace("Video: ", ""))
                is_img = False
            else:
                media_path = os.path.join("data/images", selected_src.replace("Ảnh: ", ""))
                is_img = True

            cfg_path = os.path.join("configs", selected_cfg)

            # Nạp các module
            roi_mgr = ROIManager(cfg_path)
            tracker = ObjectTracker(model_path="models/best.pt" if os.path.exists("models/best.pt") else "yolov8n.pt", conf_threshold=conf_thresh)
            checker = ViolationChecker(threshold=overlap_thresh / 100.0)
            verifier = TemporalVerifier(confirm_frames=confirm_n_frames, cooldown_seconds=60.0)
            ev_saver = EvidenceSaver(base_dir="evidence")

            if is_img:
                frame = cv2.imread(media_path)
                if frame is not None:
                    tracked = tracker.track(frame)
                    roi_mgr.draw_overlay(frame, alpha=0.25)
                    confirmed_cnt = 0

                    for obj in tracked:
                        sp = checker.check_multi(obj["box"], roi_mgr.polygons)
                        is_viol = sp["is_violation"]
                        if is_viol:
                            confirmed_cnt += 1
                            sw_idx = sp.get("sidewalk_index", 1)
                            lbl = f"VI PHAM VH#{sw_idx} ({sp['overlap_pct']}%)"
                            st_val = TrackState.CONFIRMED
                            ev_res = ev_saver.save_evidence(frame, obj["box"], obj["track_id"], camera_id=roi_mgr.camera_id, overlap_pct=sp["overlap_pct"])
                            db.insert_violation(roi_mgr.camera_id, obj["track_id"], ev_res["timestamp"], obj["conf"], sp["overlap_pct"], ev_res["full_path"], ev_res["crop_path"])
                        else:
                            lbl = f"HOP LE ({sp['overlap_pct']}%)"
                            st_val = TrackState.NORMAL

                        draw_detection(frame, obj["box"], lbl, is_violation=is_viol, track_id=obj["track_id"], status=st_val)

                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_placeholder.image(frame_rgb, caption=f"Ảnh: {selected_src} | Phát hiện: {len(tracked)} biển | Vi phạm: {confirmed_cnt}", use_container_width=True)
            else:
                reader = VideoReader(media_path)
                fps_track = FPSTracker(alpha=0.15)
                f_count = 0

                while not btn_stop:
                    ret, frame = reader.read()
                    if not ret:
                        reader.reset()
                        tracker.reset()
                        verifier.reset()
                        continue

                    f_count += 1
                    tracked = tracker.track(frame)
                    roi_mgr.draw_overlay(frame, alpha=0.25)
                    verified = verifier.process_frame(tracked, checker, roi_mgr.polygons)

                    conf_cnt = 0
                    susp_cnt = 0

                    for it in verified:
                        st_val = it["temporal_status"]
                        sp = it["spatial_res"]
                        if st_val == TrackState.CONFIRMED:
                            conf_cnt += 1
                            lbl = f"VI PHAM ({sp['overlap_pct']}%)"
                            if it["is_new_alert"]:
                                ev_res = ev_saver.save_evidence(frame, it["box"], it["track_id"], camera_id=roi_mgr.camera_id, overlap_pct=sp["overlap_pct"])
                                db.insert_violation(roi_mgr.camera_id, it["track_id"], ev_res["timestamp"], it["conf"], sp["overlap_pct"], ev_res["full_path"], ev_res["crop_path"])
                                log_placeholder.warning(f"🚨 [CẢNH BÁO VI PHẠM] ID #{it['track_id']} lấn chiếm vỉa hè ({sp['overlap_pct']}%) lúc {ev_res['timestamp']}!")
                        elif st_val == TrackState.SUSPECTED:
                            susp_cnt += 1
                            lbl = f"NGHI VAN {it['violation_frames']}/{confirm_n_frames}"
                        else:
                            lbl = f"HOP LE ({sp['overlap_pct']}%)"

                        draw_detection(frame, it["box"], lbl, track_id=it["track_id"], status=st_val)

                    cur_fps = fps_track.update()
                    draw_fps_badge(frame, cur_fps, reader.fps)

                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_placeholder.image(frame_rgb, use_container_width=True)

                    metrics_placeholder.markdown(f"**FPS:** `{cur_fps:.1f}` | **Tổng biển:** `{len(verified)}` | **Nghi vấn:** `{susp_cnt}` | **XÁC NHẬN VI PHẠM:** `{conf_cnt}`")
                    time.sleep(0.01)

                reader.release()


# ==============================================================================
# TRANG 3: TRA CỨU VI PHẠM & BẰNG CHỨNG
# ==============================================================================
elif menu == "🔍 Tra Cứu Vi Phạm & Bằng Chứng":
    st.markdown('<div class="main-header">🔍 KHO LƯU TRỮ BẰNG CHỨNG & LỊCH SỬ PHẠT NGUỘI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Truy vấn chi tiết từng vụ việc, hình ảnh đóng dấu tem pháp lý và xuất báo cáo</div>', unsafe_allow_html=True)

    # Bộ lọc
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        cams = list(stats["violations_by_camera"].keys())
        cam_filter = st.selectbox("Lọc theo Camera", ["Tất cả"] + cams)
        cam_param = None if cam_filter == "Tất cả" else cam_filter

    with col_f2:
        date_filter = st.date_input("Lọc theo ngày", value=datetime.date.today())
        date_param = str(date_filter)

    with col_f3:
        records_limit = st.selectbox("Số lượng bản ghi", [10, 25, 50, 100], index=1)

    # Truy vấn dữ liệu từ SQLite theo đúng bộ lọc người dùng chọn
    records = db.get_violations(camera_id=cam_param, date_str=date_param, limit=records_limit)

    if records:
        st.markdown(f"**Tìm thấy `{len(records)}` vụ vi phạm được ghi nhận:**")
    else:
        st.info(f"Không tìm thấy vụ vi phạm nào phù hợp với bộ lọc (Camera: {filter_camera}, Ngày: {filter_date}).")

    if records:
        # Nút xuất CSV
        df_export = pd.DataFrame(records)
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Xuất Báo Cáo Vi Phạm (CSV)",
            data=csv_data,
            file_name=f"bao_cao_vi_pham_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

        st.markdown("---")
        # Hiển thị từng card vụ việc
        for rec in records:
            with st.expander(f"🚨 Vụ #{rec['id']} | Cam: {rec['camera_id']} | ID Biển: #{rec['track_id']} | Thời gian: {rec['timestamp']} | Lấn chiếm: {rec['overlap_pct']}%"):
                c1, c2 = st.columns([2, 1])

                with c1:
                    st.markdown("**Ảnh Toàn Cảnh (Full Frame - Tem Pháp Lý):**")
                    if os.path.exists(rec["full_image_path"]):
                        st.image(rec["full_image_path"], use_container_width=True)
                    else:
                        st.warning(f"Không tìm thấy file: {rec['full_image_path']}")

                with c2:
                    st.markdown("**Ảnh Cận Cảnh (Cropped):**")
                    if rec["crop_image_path"] and os.path.exists(rec["crop_image_path"]):
                        st.image(rec["crop_image_path"], width=220)
                    else:
                        st.info("Chưa có ảnh crop.")

                    st.markdown(f"""
                    - **Mã vụ việc:** `#{rec['id']}`
                    - **Camera:** `{rec['camera_id']}`
                    - **Biển số ID:** `#{rec['track_id']}`
                    - **Thời gian:** `{rec['timestamp']}`
                    - **Độ tin cậy AI:** `{rec['confidence']*100:.0f}%`
                    - **Mức độ lấn chiếm:** `{rec['overlap_pct']}%`
                    - **Hành vi:** `Lấn chiếm vỉa hè`
                    """)
    else:
        st.info("Không có dữ liệu vi phạm phù hợp với bộ lọc.")


# ==============================================================================
# TRANG 4: QUẢN LÝ VÙNG VỈA HÈ (ROI)
# ==============================================================================
elif menu == "⚙️ Quản Lý Vùng Vỉa Hè (ROI)":
    st.markdown('<div class="main-header">⚙️ QUẢN LÝ VÙNG QUAN TÂM VỈA HÈ (ROI)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Danh sách cấu hình đa giác vỉa hè cho từng camera an ninh</div>', unsafe_allow_html=True)

    cfg_dir = "configs"
    if os.path.exists(cfg_dir):
        files = [f for f in os.listdir(cfg_dir) if f.endswith(".json")]
        st.write(f"Hiện có **{len(files)}** file cấu hình vỉa hè:")

        for f in files:
            path = os.path.join(cfg_dir, f)
            mgr = ROIManager(path)
            with st.expander(f"📁 {f} ({mgr.camera_id} - {len(mgr.polygons)} vùng vỉa hè)"):
                st.write(f"**Số vùng vỉa hè:** {len(mgr.polygons)}")
                for idx, p in enumerate(mgr.polygons, 1):
                    st.write(f"- Vỉa hè #{idx}: `{p}`")

    st.markdown("---")
    st.subheader("💡 Cách Vẽ Thêm Vỉa Hè Mới:")
    st.code(r".\.venv\Scripts\python.exe roi_drawer.py <đường_dẫn_ảnh_hoặc_video> configs/roi_ten_moi.json", language="powershell")
    st.markdown("""
    1. Click chuột trái để chấm các đỉnh vỉa hè.
    2. Nhấn phím **`n`** nếu muốn vẽ thêm vỉa hè bên kia đường (Multi-ROI).
    3. Nhấn phím **`s`** để lưu cấu hình JSON.
    """)
