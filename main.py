"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Unified Surveillance Platform (Version 2.0)
TASK: 28 - ĐIỂM VÀO ĐIỀU HÀNH HỆ THỐNG TRUNG TÂM (UNIFIED ENTRY POINT - main.py)
==============================================================================
Hỗ trợ 3 chế độ hoạt động chính:
  1. --mode monitor   : Chạy pipeline giám sát thời gian thực (CCTV RTSP / Video / Webcam)
  2. --mode dashboard : Khởi chạy Web Dashboard trực quan quản lý vi phạm & phạt nguội
  3. --mode roi       : Mở công cụ tương tác vẽ & hiệu chỉnh vỉa hè đa vùng (Multi-ROI)
==============================================================================
"""

import os
import sys
import argparse
import time
import cv2

try:
    import yaml as _yaml
    def _load_settings(path: str = "configs/settings.yaml") -> dict:
        """Nạp cấu hình từ settings.yaml. Trả về dict rỗng nếu file không tồn tại."""
        if not os.path.exists(path):
            return {}
        with open(path, encoding="utf-8") as f:
            return _yaml.safe_load(f) or {}
except ImportError:
    def _load_settings(path: str = "configs/settings.yaml") -> dict:
        print("[WARN] PyYAML chưa cài. Cài bằng: pip install pyyaml")
        return {}

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Import các module cốt lõi trong hệ thống
from camera import StreamReader
from roi import ROIManager
from tracking import ObjectTracker, TemporalVerifier, TrackState
from violation import ViolationChecker
from evidence import EvidenceSaver
from database import ViolationDatabase
from utils import FPSTracker, draw_fps_badge, draw_detection


BANNER = r"""
==============================================================================
   ____ ____ _______     __  ____  _     _                 _ _                 
  / ___/ ___|_   _\ \   / / / ___|(_) __| | _____      ____| | | __ ___  _ __   
 | |  | |     | |  \ \ / /  \___ \| |/ _` |/ _ \ \ /\ / / _` | |/ // _ \| '_ \  
 | |__| |___  | |   \ V /    ___) | | (_| |  __/\ V  V / (_| |   <| (_) | | | | 
  \____\____| |_|    \_/    |____/|_|\__,_|\___| \_/\_/ \__,_|_|\_\\___/|_| |_| 
                                                                               
   HỆ THỐNG GIÁM SÁT & XỬ LÝ BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CAMERA CCTV
   Phiên bản: 2.0 (Hệ thống điều hành thống nhất - Unified Architecture)
==============================================================================
"""


def run_monitor_mode(args):
    """
    Chế độ 1: Pipeline giám sát thông minh 24/7.
    Tích hợp:
      - StreamReader: Auto-reconnect cho RTSP & looping video
      - ROIManager: Đa giác vỉa hè đa vùng
      - ObjectTracker: ByteTrack gán track_id ổn định
      - TemporalVerifier: Bộ lọc xác nhận 15 frames & Cooldown 60s
      - EvidenceSaver: Đóng dấu mộc tư pháp & lưu ảnh bằng chứng
      - ViolationDatabase: SQLite ghi nhận lịch sử vi phạm
    """
    print(BANNER)
    print(">> ĐANG KHỞI ĐỘNG CHẾ ĐỘ GIÁM SÁT THỜI GIAN THỰC (MONITOR MODE)...")
    print("-" * 78)

    # 1. Khởi tạo nguồn Camera / Video
    source = args.source
    if source is None:
        video_dir = "data/videos"
        files = [f for f in os.listdir(video_dir) if f.lower().endswith(('.mp4', '.avi', '.mov'))] if os.path.exists(video_dir) else []
        if files:
            source = os.path.join(video_dir, files[0])
        else:
            print("[LỖI] Không tìm thấy video nào trong thư mục data/videos/!")
            return False

    is_stream = isinstance(source, str) and source.lower().startswith(("rtsp://", "http://", "https://"))
    is_webcam = (isinstance(source, int) or (isinstance(source, str) and source.isdigit()))
    if not is_stream and not is_webcam and not os.path.exists(str(source)):
        print(f"[LỖI] Tệp tin nguồn không tồn tại: {source}")
        return False

    is_image = isinstance(source, str) and source.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))

    # 2. Quản lý cấu hình ROI vỉa hè
    # FIX: Không tự động chọn roi_moi.json cho mọi nguồn (lỗi cũ báo cáo bởi reviewer).
    # Thứ tự ưu tiên: --config arg > khớp tên file > roi_camera1.json mặc định.
    config_path = args.config
    if config_path is None:
        source_name = os.path.basename(str(source)).lower()
        # Thử tìm file roi khớp theo tên source
        candidate = os.path.join("configs", f"roi_{source_name.rsplit('.', 1)[0]}.json")
        if os.path.exists(candidate):
            config_path = candidate
        elif os.path.exists("configs/roi_camera1.json"):
            config_path = "configs/roi_camera1.json"
        else:
            # Fallback cuối cùng: lấy file roi đầu tiên tìm thấy trong configs/
            roi_files = sorted(f for f in os.listdir("configs") if f.startswith("roi_") and f.endswith(".json"))
            config_path = os.path.join("configs", roi_files[0]) if roi_files else "configs/roi_camera1.json"

    roi_manager = ROIManager(config_path)
    total_pts = sum(len(p) for p in roi_manager.polygons)

    # 3. Nạp cấu hình tham số tập trung (settings.yaml)
    cfg = _load_settings()
    cfg_temporal = cfg.get("temporal", {})
    cfg_detector = cfg.get("detector", {})
    cfg_perf = cfg.get("performance", {})

    is_edge_mode = getattr(args, "edge", False)

    model_path = args.model
    if getattr(args, "onnx", False) or is_edge_mode or (model_path == "models/best.pt" and cfg_perf.get("use_onnx", False)):
        if os.path.exists("models/best.onnx"):
            model_path = "models/best.onnx"
        elif os.path.exists(cfg_detector.get("onnx_path", "")):
            model_path = cfg_detector["onnx_path"]

    imgsz = args.imgsz if getattr(args, "imgsz", None) is not None else cfg_detector.get("imgsz", 640)
    
    if is_edge_mode:
        frame_skip = args.skip_frames if getattr(args, "skip_frames", None) is not None else 2
    else:
        frame_skip = args.skip_frames if getattr(args, "skip_frames", None) is not None else cfg_perf.get("frame_skip", 2)

    # Đồng bộ nhịp phát Real-time FPS (Khóa nhịp thời gian thực tránh tua nhanh trên Edge)
    sync_playback = True
    if getattr(args, "no_sync", False):
        sync_playback = False
    elif getattr(args, "sync_fps", False) or is_edge_mode:
        sync_playback = True
    elif "sync_playback" in cfg_perf:
        sync_playback = bool(cfg_perf["sync_playback"])
    
    if is_stream:
        sync_playback = False

    target_fps = args.target_fps if getattr(args, "target_fps", None) is not None else float(cfg_perf.get("target_fps", 24.0))
    engine_name = "ONNX Runtime (CPU AVX2)" if str(model_path).endswith(".onnx") else "PyTorch"
    sync_str = f"Realtime {target_fps:.0f} FPS (1.0x)" if sync_playback else "Unlocked (Max Compute)"

    print(f"[*] Nguồn cấp dữ liệu : {source}")
    print(f"[*] Cấu hình Vỉa hè   : {config_path} ({len(roi_manager.polygons)} vùng vỉa hè, {total_pts} đỉnh)")
    print(f"[*] Model AI Detector : {model_path} (Imgsz: {imgsz})")
    print(f"[*] Cấu hình Edge AI  : Engine: {engine_name} | Frame Skip: {frame_skip} | Playback: {sync_str}")
    print(f"[*] Ngưỡng tin cậy AI : {args.conf * 100:.0f}%")
    print(f"[*] Ngưỡng đè vỉa hè  : {args.overlap * 100:.0f}%")
    print(f"[*] Bộ lọc thời gian  : Xác nhận sau {args.confirm_frames} frames | Cooldown {args.cooldown}s")
    print("-" * 78)

    tracker = ObjectTracker(model_path=model_path, conf_threshold=args.conf, imgsz=imgsz)
    checker = ViolationChecker(threshold=args.overlap)
    verifier = TemporalVerifier(
        confirm_frames=args.confirm_frames,
        confirm_seconds=cfg_temporal.get("confirm_seconds", 0.5),
        cooldown_seconds=args.cooldown,
        max_missing_frames=cfg_temporal.get("max_missing_frames", 30),
        tolerance_frames=cfg_temporal.get("tolerance_frames", 2),
    )
    evidence_saver = EvidenceSaver(base_dir=args.evidence_dir)
    db = ViolationDatabase(db_path=args.db)

    # 4. XỬ LÝ ẢNH TĨNH
    if is_image:
        print(">> Đang xử lý ảnh tĩnh...")
        frame = cv2.imread(source)
        if frame is None:
            print(f"[LỖI] Không thể đọc tệp ảnh: {source}")
            return False

        # ISSUE 01 FIX: Validate & auto-scale ROI theo resolution thực tế
        fh, fw = frame.shape[:2]
        roi_manager.validate_resolution(fw, fh)

        # AI Detect trên ảnh sạch nguyên bản
        tracked_objs = tracker.track(frame)

        # Lưu bản sạch trước khi vẽ overlay (dùng cho evidence)
        clean_frame = frame.copy()
        roi_manager.draw_overlay(frame, alpha=0.25)

        # ISSUE 10 FIX: Ảnh tĩnh dùng nhãn SUSPECTED thay vì CONFIRMED
        confirmed_count = 0
        for obj in tracked_objs:
            box = obj["box"]
            track_id = obj["track_id"]
            conf = obj["conf"]
            sp = checker.check_multi(box, roi_manager.polygons)
            is_viol = sp["is_violation"]

            if is_viol:
                confirmed_count += 1
                sw_idx = sp.get("sidewalk_index", 1)
                lbl = f"NGHI VAN VH#{sw_idx}: {sp['overlap_pct']}% (Anh tinh)"
                status = TrackState.SUSPECTED
                ev_res = evidence_saver.save_evidence(clean_frame, box, track_id=track_id, camera_id=roi_manager.camera_id, overlap_pct=sp['overlap_pct'])
                rec_id = db.insert_violation(
                    camera_id=roi_manager.camera_id,
                    track_id=track_id,
                    timestamp=ev_res["timestamp"],
                    confidence=conf,
                    overlap_pct=sp["overlap_pct"],
                    full_image_path=ev_res["full_path"],
                    crop_image_path=ev_res.get("crop_path", ""),
                    bbox=box,
                    sidewalk_index=sw_idx
                )
                print(f"  📸 [BẰNG CHỨNG #{confirmed_count}] Đã ghi nhận vi phạm ID #{track_id} -> DB record #{rec_id}")
            else:
                lbl = f"HOP LE: {sp['overlap_pct']}%"
                status = TrackState.NORMAL

            draw_detection(frame, box, lbl, is_violation=is_viol, track_id=track_id, status=status)

        hud_text = f"Tong bien: {len(tracked_objs)} | Vi pham: {confirmed_count}"
        cv2.putText(frame, hud_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255) if confirmed_count > 0 else (0, 255, 0), 2)

        if not args.headless:
            window_name = "CCTV Sidewalk Surveillance 2.0"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            h, w = frame.shape[:2]
            cv2.resizeWindow(window_name, min(w, 1024), min(h, 768))
            cv2.imshow(window_name, frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return True

    # 5. XỬ LÝ LUỒNG VIDEO / RTSP / WEBCAM LIÊN TỤC
    reader = StreamReader(source=source)
    # Truyền FPS nguồn để TemporalVerifier tính giây chính xác
    verifier.source_fps = reader.fps if hasattr(reader, 'fps') and reader.fps > 0 else None
    fps_tracker = FPSTracker(alpha=0.15)
    window_name = "CCTV Sidewalk Surveillance 2.0 (ByteTrack + Temporal Verifier)"

    if not args.headless:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, min(reader.width, 1024), min(reader.height, 768))

    print(">> ĐANG GIÁM SÁT TRỰC TUYẾN 24/7. Nhấn 'q' hoặc 'ESC' để dừng.")
    frame_count = 0
    total_confirmed_events = 0
    roi_validated = False

    last_verified_render = []
    last_confirmed_count = 0
    last_suspected_count = 0
    last_object_count = 0

    target_frame_interval = 1.0 / target_fps if target_fps > 0 else 0.04167

    try:
        while True:
            loop_start_time = time.perf_counter()
            ret, frame = reader.read()
            if not ret or frame is None:
                # StreamReader đã tự động retry hoặc tua lại video, nếu vẫn None thì tạm nghỉ
                time.sleep(0.01)
                continue

            fps_val = fps_tracker.update()

            # ISSUE 01 FIX: Validate & auto-scale ROI trên frame đầu tiên
            if not roi_validated:
                fh, fw = frame.shape[:2]
                roi_manager.validate_resolution(fw, fh)
                roi_validated = True

            # Khi video file tua lại đầu: reset tracker & verifier để tránh duplicate violations
            if hasattr(reader, 'looped') and reader.looped:
                reader.looped = False
                tracker.reset()
                verifier.reset()
                last_verified_render.clear()
                last_confirmed_count = 0
                last_suspected_count = 0
                last_object_count = 0
                print("[INFO] Video đã tua lại đầu — đã reset Tracker & Verifier.")

            frame_count += 1
            is_infer_frame = (frame_skip <= 0) or (frame_count % (frame_skip + 1) == 1)

            if is_infer_frame:
                # BƯỚC 1: AI BÁM VẾT BYTETRACK TRÊN KHUNG HÌNH SẠCH NGUYÊN BẢN
                tracked_objects = tracker.track(frame)

                # BƯỚC 1.5: Tạo bản sạch cho evidence trước khi vẽ overlay
                clean_frame = frame.copy()

                # BƯỚC 2: VẼ VÙNG VỈA HÈ LÊN FRAME HIỂN THỊ
                roi_manager.draw_overlay(frame, alpha=0.25)

                # BƯỚC 3: BỘ LỌC XÁC MINH THỜI GIAN
                verified_objects = verifier.process_frame(tracked_objects, checker, roi_manager.polygons)

                current_frame_confirmed = 0
                current_frame_suspected = 0
                last_verified_render = []

                # BƯỚC 4: VẼ KẾT QUẢ VÀ LƯU BẰNG CHỨNG
                for item in verified_objects:
                    box = item["box"]
                    track_id = item["track_id"]
                    conf = item["conf"]
                    sp = item["spatial_res"]
                    temporal_status = item["temporal_status"]
                    v_count = item["violation_frames"]
                    is_new_alert = item["is_new_alert"]

                    if temporal_status == TrackState.CONFIRMED:
                        current_frame_confirmed += 1
                        sw_idx = sp.get("sidewalk_index", 1)
                        label = f"VI PHAM VH#{sw_idx} ({sp['overlap_pct']}%)"

                        # Khi phát hiện vi phạm thực sự lần đầu (sau 15 frames)
                        if is_new_alert:
                            # ISSUE 09 FIX: Kiểm tra trùng lặp trước khi ghi DB (chống ghi trùng khi restart)
                            if db.is_duplicate_violation(roi_manager.camera_id, box, time_window_minutes=5):
                                print(f"[DEDUP] Bỏ qua vi phạm trùng lặp ID #{track_id} (đã có bản ghi tương tự trong 5 phút gần đây)")
                            else:
                                total_confirmed_events += 1
                                ev_res = evidence_saver.save_evidence(
                                    clean_frame, box, track_id=track_id, camera_id=roi_manager.camera_id, overlap_pct=sp['overlap_pct']
                                )
                                rec_id = db.insert_violation(
                                    camera_id=roi_manager.camera_id,
                                    track_id=track_id,
                                    timestamp=ev_res["timestamp"],
                                    confidence=conf,
                                    overlap_pct=sp["overlap_pct"],
                                    full_image_path=ev_res["full_path"],
                                    crop_image_path=ev_res.get("crop_path", ""),
                                    bbox=box,
                                    sidewalk_index=sw_idx
                                )
                                print(f"🚨 [CẢNH BÁO VI PHẠM MỚI] ID #{track_id} lấn chiếm vỉa hè #{sw_idx} ({sp['overlap_pct']}%)")
                                print(f"   📸 Ảnh bằng chứng: {ev_res['full_path']} | DB Record #{rec_id}")

                    elif temporal_status == TrackState.SUSPECTED:
                        current_frame_suspected += 1
                        label = f"NGHI VAN ({v_count}/{verifier.confirm_frames})"
                    else:
                        label = f"HOP LE ({sp['overlap_pct']}%)"

                    draw_detection(frame, box, label, track_id=track_id, status=temporal_status)
                    last_verified_render.append((box, label, track_id, temporal_status))

                last_confirmed_count = current_frame_confirmed
                last_suspected_count = current_frame_suspected
                last_object_count = len(verified_objects)

            else:
                # FRAME BỎ QUA INFER (Tối ưu CPU): Tái sử dụng kết quả frame trước để render mượt
                roi_manager.draw_overlay(frame, alpha=0.25)
                for (box, label, track_id, temporal_status) in last_verified_render:
                    draw_detection(frame, box, label, track_id=track_id, status=temporal_status)
                current_frame_confirmed = last_confirmed_count
                current_frame_suspected = last_suspected_count

            # BƯỚC 5: HUD OVERLAY THÔNG SỐ VÀ FPS
            draw_fps_badge(frame, fps_val, reader.fps)

            # Banner cảnh báo trên góc
            obj_cnt = len(verified_objects) if is_infer_frame else last_object_count
            hud_text = f"Bien: {obj_cnt} | Nghi van: {current_frame_suspected} | VI PHAM: {current_frame_confirmed}"
            hud_color = (0, 0, 255) if current_frame_confirmed > 0 else ((0, 165, 255) if current_frame_suspected > 0 else (0, 255, 0))
            cv2.putText(frame, hud_text, (max(10, reader.width - 480), 32),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, hud_color, 2, cv2.LINE_AA)

            if args.max_frames and frame_count >= args.max_frames:
                print(f"[INFO] Đã đạt giới hạn {args.max_frames} frames chỉ định. Dừng giám sát.")
                break

            # Đồng bộ nhịp thời gian thực chuẩn cho Thiết bị biên (Edge Sleep & Power Saving)
            proc_elapsed = time.perf_counter() - loop_start_time
            remaining_sleep = target_frame_interval - proc_elapsed

            if not args.headless:
                cv2.imshow(window_name, frame)
                if sync_playback and remaining_sleep > 0.001:
                    wait_ms = max(1, int(remaining_sleep * 1000))
                else:
                    wait_ms = 1
                key = cv2.waitKey(wait_ms) & 0xFF
                if key == ord('q') or key == 27:
                    break
            else:
                if sync_playback and remaining_sleep > 0.001:
                    time.sleep(remaining_sleep)

    finally:
        reader.release()
        if not args.headless:
            cv2.destroyAllWindows()
        print("-" * 78)
        print("TỔNG KẾT PHIÊN GIÁM SÁT:")
        print(f"  • Tổng số khung hình đã xử lý            : {frame_count}")
        print(f"  • Tốc độ xử lý trung bình                : {fps_tracker.smoothed_fps:.1f} FPS")
        print(f"  • Tổng số sự kiện vi phạm được ghi nhận  : {total_confirmed_events}")
        print("[OK] Đã giải phóng tài nguyên an toàn.")
        print("=" * 78)

    return True


def run_dashboard_mode(args):
    """
    Chế độ 2: Khởi chạy Web Dashboard.
    """
    print(BANNER)
    print(">> ĐANG KHỞI ĐỘNG WEB DASHBOARD TRỰC QUAN...")
    from dashboard.web_app import run_dashboard
    run_dashboard(port=args.port)


def run_roi_mode(args):
    """
    Chế độ 3: Khởi chạy công cụ vẽ & cấu hình vỉa hè đa vùng (Multi-ROI).
    """
    print(BANNER)
    print(">> ĐANG KHỞI ĐỘNG CÔNG CỤ VẼ VÙNG VỈA HÈ (MULTI-ROI DRAWER)...")
    source = args.source
    if source is None:
        video_dir = "data/videos"
        files = [f for f in os.listdir(video_dir) if f.lower().endswith(('.mp4', '.avi', '.mov'))] if os.path.exists(video_dir) else []
        source = os.path.join(video_dir, files[0]) if files else "data/videos/sample_cctv.mp4"

    cfg = args.config if args.config else "configs/roi_camera1.json"
    from roi_drawer import run_roi_tool
    run_roi_tool(source, cfg)


def run_benchmark_mode(args):
    """
    Chế độ 4: Thực nghiệm & Đo đạc chỉ số (Benchmark & Latency Breakdown).
    Tự động xuất báo cáo Markdown chuẩn cho Chương 7 Luận văn.
    """
    print(BANNER)
    from evaluation import SystemBenchmark
    bench = SystemBenchmark(
        source=args.source,
        config_path=args.config,
        model_path=args.model,
        num_frames=args.max_frames if args.max_frames else 50
    )
    res = bench.run_benchmark(verbose=True)
    report_file = args.report if hasattr(args, 'report') and args.report else "reports/benchmark_report.md"
    bench.export_markdown_report(res, output_file=report_file)


def main():
    parser = argparse.ArgumentParser(
        description="CCTV Sidewalk Signboard Surveillance System (Version 2.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  # 1. Giám sát từ video mẫu hoặc camera RTSP:
  python main.py --mode monitor --source data/videos/sample_cctv.mp4 --config configs/roi_moi.json
  python main.py --mode monitor --source rtsp://admin:pass@192.168.1.10:554/stream1

  # 2. Khởi chạy Web Dashboard xem lịch sử & bằng chứng vi phạm:
  python main.py --mode dashboard --port 8501

  # 3. Vẽ cấu hình vỉa hè mới cho camera:
  python main.py --mode roi --source data/videos/sample_cctv.mp4 --config configs/roi_cam1.json
        """
    )

    parser.add_argument("--mode", choices=["monitor", "dashboard", "roi", "benchmark"], default="monitor",
                        help="Chế độ hoạt động của hệ thống (mặc định: monitor)")
    parser.add_argument("--source", type=str, default=None,
                        help="Nguồn camera: Đường dẫn video, URL RTSP, số webcam (0, 1) hoặc ảnh tĩnh")
    parser.add_argument("--config", type=str, default=None,
                        help="Đường dẫn tệp cấu hình tọa độ vỉa hè JSON (Mặc định tự động chọn)")
    parser.add_argument("--model", type=str, default="models/best.pt",
                        help="Đường dẫn trọng số mô hình YOLO (mặc định: models/best.pt)")
    parser.add_argument("--conf", type=float, default=0.20,
                        help="Ngưỡng tin cậy phát hiện biển hiệu (mặc định: 0.20)")
    parser.add_argument("--overlap", type=float, default=0.30,
                        help="Ngưỡng diện tích đè vỉa hè để kết luận vi phạm (mặc định: 0.30 = 30%%)")
    parser.add_argument("--confirm-frames", type=int, default=15,
                        help="Số frames liên tiếp vi phạm để xác nhận (mặc định: 15)")
    parser.add_argument("--cooldown", type=float, default=60.0,
                        help="Thời gian cooldown cảnh báo lại cùng 1 vật thể (giây, mặc định: 60)")
    parser.add_argument("--max-frames", type=int, default=None,
                        help="Giới hạn số frames chạy (dùng cho đo đạc hiệu năng benchmark hoặc test)")
    parser.add_argument("--report", type=str, default="reports/benchmark_report.md",
                        help="Đường dẫn file xuất báo cáo Markdown khi chạy benchmark")
    parser.add_argument("--evidence-dir", type=str, default="evidence",
                        help="Thư mục lưu trữ hình ảnh bằng chứng (mặc định: evidence)")
    parser.add_argument("--db", type=str, default="data/surveillance.db",
                        help="Đường dẫn tệp cơ sở dữ liệu SQLite (mặc định: data/surveillance.db)")
    parser.add_argument("--port", type=int, default=8501,
                        help="Cổng mở Web Dashboard (mặc định: 8501)")
    parser.add_argument("--edge", action="store_true",
                        help="Kích hoạt hồ sơ tối ưu toàn diện cho Thiết bị biên (Edge Profile: ONNX + 640px + Skip 2 + Sync 24FPS)")
    parser.add_argument("--onnx", action="store_true",
                        help="Kích hoạt ONNX Runtime Engine CPU (tự động dùng models/best.onnx)")
    parser.add_argument("--imgsz", type=int, default=None,
                        help="Kích thước cạnh ảnh chuẩn khi suy luận (mặc định: 640)")
    parser.add_argument("--skip-frames", type=int, default=None,
                        help="Số frames bỏ qua giữa các lần infer (mặc định: 2, gợi ý: 1 hoặc 2)")
    parser.add_argument("--sync-fps", action="store_true",
                        help="Khóa nhịp FPS thời gian thực chuẩn 1.0x (tiết kiệm CPU, mặc định bật cho video)")
    parser.add_argument("--no-sync", action="store_true",
                        help="Tắt khóa nhịp FPS để chạy hết công suất phần cứng (Benchmark mode)")
    parser.add_argument("--target-fps", type=float, default=None,
                        help="Tốc độ FPS mục tiêu cho thiết bị biên (mặc định: 24.0)")
    parser.add_argument("--headless", action="store_true",
                        help="Chạy ở chế độ không mở cửa sổ giao diện OpenCV (cho server)")

    args = parser.parse_args()

    if args.mode == "monitor":
        run_monitor_mode(args)
    elif args.mode == "dashboard":
        run_dashboard_mode(args)
    elif args.mode == "roi":
        run_roi_mode(args)
    elif args.mode == "benchmark":
        run_benchmark_mode(args)


if __name__ == "__main__":
    main()
