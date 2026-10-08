"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Production Pipeline - Version 1.0
TASK: 22 - PIPELINE GIÁM SÁT THỜI GIAN THỰC HOÀN CHỈNH
Tích hợp: Camera -> ROI Vỉa hè -> AI YOLO -> ByteTrack -> Bộ lọc 15 frames & Cooldown
==============================================================================
"""

import os
import sys
import time
import cv2

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from camera import VideoReader
from roi import ROIManager
from tracking import ObjectTracker, TemporalVerifier, TrackState
from violation import ViolationChecker
from evidence import EvidenceSaver
from database import ViolationDatabase
from utils import FPSTracker, draw_fps_badge, draw_detection




def run_temporal_pipeline(video_path: str = None, model_path: str = "models/best.pt", config_path: str = None):
    print("=" * 75)
    print("HỆ THỐNG GIÁM SÁT LẤN CHIẾM VỈA HÈ THỜI GIAN THỰC (PHIÊN BẢN 1.0 - TASK 22)")
    print("TÍCH HỢP BYTETRACK OBJECT TRACKING & BỘ LỌC XÁC NHẬN N-FRAMES CHỐNG BÁO GIẢ")
    print("=" * 75)

    # 1. KẾT NỐI NGUỒN DỮ LIỆU
    if video_path is None or not os.path.exists(video_path):
        video_dir = "data/videos"
        files = [f for f in os.listdir(video_dir) if f.lower().endswith(('.mp4', '.avi', '.mov'))] if os.path.exists(video_dir) else []
        video_path = os.path.join(video_dir, files[0]) if files else "data/videos/sample_cctv.mp4"

    is_image = video_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))

    # 2. TỰ ĐỘNG CHỌN CẤU HÌNH VÙNG VỈA HÈ (ROI)
    if config_path is None:
        if os.path.exists("configs/roi_moi.json"):
            config_path = "configs/roi_moi.json"
        elif "Duck-ai-image" in video_path and os.path.exists("configs/roi_duck_image.json"):
            config_path = "configs/roi_duck_image.json"
        else:
            config_path = "configs/roi_camera1.json"

    roi_manager = ROIManager(config_path)
    total_pts = sum(len(p) for p in roi_manager.polygons)
    print(f"[+] File cấu hình ROI   : {config_path}")
    print(f"[+] Vùng vỉa hè camera  : {roi_manager.camera_id} ({len(roi_manager.polygons)} vùng vỉa hè, tổng {total_pts} đỉnh)")

    # 3. NẠP MÔ HÌNH AI & BỘ BÁM VẾT BYTETRACK
    if not os.path.exists(model_path):
        model_path = "yolov8n.pt"

    tracker = ObjectTracker(model_path=model_path, conf_threshold=0.20)

    # 4. NẠP BỘ PHÁN QUYẾT HÌNH HỌC, BỘ LỌC THỜI GIAN & HỆ THỐNG LƯU BẰNG CHỨNG
    checker = ViolationChecker(threshold=0.30)
    # Xác nhận sau 15 frames liên tiếp (~0.5 - 1s); Cooldown 60s cho mỗi ID
    verifier = TemporalVerifier(confirm_frames=15, cooldown_seconds=60.0, max_missing_frames=30)
    evidence_saver = EvidenceSaver(base_dir="evidence")
    db = ViolationDatabase(db_path="data/surveillance.db")

    print(f"[+] Ngưỡng xác nhận     : {verifier.confirm_frames} frames liên tiếp (Lọc 100% người bê biển đi ngang)")
    print(f"[+] Cooldown cảnh báo   : {verifier.cooldown_seconds:.0f}s / mỗi biển hiệu (Chống spam alert)")
    print(f"[+] Thư mục bằng chứng  : {evidence_saver.base_dir}/ (Tự động chụp toàn cảnh & cận cảnh)")
    print(f"[+] Cơ sở dữ liệu SQLite: {db.db_path} (Lưu trữ lịch sử & phục vụ Dashboard)")



    # 5. XỬ LÝ ẢNH TĨNH
    if is_image:
        print(f"[+] Nguồn ảnh tĩnh      : {video_path}")
        print("-" * 75)
        print(">> ĐANG PHÂN TÍCH... Nhấn phím bất kỳ hoặc 'q' để đóng.")

        frame = cv2.imread(video_path)
        if frame is None:
            print(f"[LỖI] Không thể đọc ảnh: {video_path}")
            return False

        h, w = frame.shape[:2]
        window_name = "CCTV Sidewalk Surveillance - Version 1.0"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, min(w, 960), min(h, 720))

        # AI Detect trên ảnh sạch
        tracked_objs = tracker.track(frame)
        roi_manager.draw_overlay(frame, alpha=0.25)

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
                lbl = f"VI PHAM VH#{sw_idx}: {sp['overlap_pct']}%"
                status = TrackState.CONFIRMED
                ev_res = evidence_saver.save_evidence(frame, box, track_id=track_id, camera_id=roi_manager.camera_id, overlap_pct=sp['overlap_pct'])
                rec_id = db.insert_violation(
                    camera_id=roi_manager.camera_id,
                    track_id=track_id,
                    timestamp=ev_res["timestamp"],
                    confidence=conf,
                    overlap_pct=sp["overlap_pct"],
                    full_image_path=ev_res["full_path"],
                    crop_image_path=ev_res.get("crop_path", "")
                )
                print(f"  📸 [BẰNG CHỨNG #{confirmed_count}] Đã lưu ảnh: {ev_res['full_path']} | Ghi DB #{rec_id}")
            else:
                lbl = f"HOP LE: {sp['overlap_pct']}%"
                status = TrackState.NORMAL


            draw_detection(frame, box, lbl, is_violation=is_viol, track_id=track_id, status=status)


        hud_text = f"Tong bien: {len(tracked_objs)} | Vi pham: {confirmed_count}"
        hud_color = (0, 0, 255) if confirmed_count > 0 else (0, 255, 0)
        cv2.putText(frame, hud_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, hud_color, 2, cv2.LINE_AA)

        cv2.imshow(window_name, frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return True

    # 6. XỬ LÝ VIDEO CAMERA CCTV THỜI GIAN THỰC
    reader = VideoReader(video_path)
    fps_tracker = FPSTracker(alpha=0.15)
    window_name = "CCTV Sidewalk Surveillance - Version 1.0 (ByteTrack + Temporal Verifier)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, min(reader.width, 960), min(reader.height, 720))

    print(f"[+] Nguồn video CCTV    : {video_path} ({reader.width}x{reader.height}, {reader.fps:.1f} FPS)")
    print("-" * 75)
    print(">> ĐANG GIÁM SÁT LIÊN TỤC 24/7... Nhấn phím 'q' hoặc 'ESC' để dừng.")

    frame_count = 0
    total_confirmed_events = 0

    try:
        while True:
            ret, frame = reader.read()
            if not ret:
                reader.reset()
                tracker.reset()
                verifier.reset()
                continue

            frame_count += 1

            # BƯỚC A: BÁM VẾT BYTETRACK TRÊN KHUNG HÌNH GỐC NGUYÊN BẢN
            tracked_objects = tracker.track(frame)

            # BƯỚC B: VẼ LỚP PHỦ VỈA HÈ BÁN TRONG SUỐT (ROI OVERLAY)
            roi_manager.draw_overlay(frame, alpha=0.25)

            # BƯỚC C: CHẠY BỘ LỌC THỜI GIAN VÀ XÁC NHẬN VI PHẠM (TEMPORAL VERIFIER)
            verified_objects = verifier.process_frame(tracked_objects, checker, roi_manager.polygons)

            current_frame_confirmed = 0
            current_frame_suspected = 0

            # BƯỚC D: VẼ TỪNG VẬT THỂ THEO 3 TRẠNG THÁI MÀU SẮC
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

                    # KÍCH HOẠT SỰ KIỆN CẢNH BÁO MỚI (LƯU BẰNG CHỨNG & GHI CSDL)
                    if is_new_alert:
                        total_confirmed_events += 1
                        ev_res = evidence_saver.save_evidence(frame, box, track_id=track_id, camera_id=roi_manager.camera_id, overlap_pct=sp['overlap_pct'])
                        rec_id = db.insert_violation(
                            camera_id=roi_manager.camera_id,
                            track_id=track_id,
                            timestamp=ev_res["timestamp"],
                            confidence=conf,
                            overlap_pct=sp["overlap_pct"],
                            full_image_path=ev_res["full_path"],
                            crop_image_path=ev_res.get("crop_path", "")
                        )
                        print(f"🚨 [CẢNH BÁO VI PHẠM MỚI] ID #{track_id} lấn chiếm vỉa hè #{sw_idx} "
                              f"(Đứng yên >= {v_count} frames, Đè {sp['overlap_pct']}%)!")
                        print(f"   📸 Ảnh toàn cảnh : {ev_res['full_path']}")
                        if ev_res.get('crop_path'):
                            print(f"   🔍 Ảnh cận cảnh  : {ev_res['crop_path']}")
                        print(f"   💾 Bản ghi CSDL  : #{rec_id} trong data/surveillance.db")



                elif temporal_status == TrackState.SUSPECTED:
                    current_frame_suspected += 1
                    label = f"NGHI VAN ({v_count}/{verifier.confirm_frames})"
                else:
                    label = f"HOP LE ({sp['overlap_pct']}%)"

                draw_detection(frame, box, label, track_id=track_id, status=temporal_status)

            # BƯỚC E: BẢNG THỐNG KÊ TRỰC TIẾP (HUD OVERLAY)
            fps_val = fps_tracker.update()
            draw_fps_badge(frame, fps_val, reader.fps)

            # Banner cảnh báo trên góc
            hud_text = f"Bien: {len(verified_objects)} | Nghi van: {current_frame_suspected} | VI PHAM: {current_frame_confirmed}"
            hud_color = (0, 0, 255) if current_frame_confirmed > 0 else ((0, 165, 255) if current_frame_suspected > 0 else (0, 255, 0))
            cv2.putText(frame, hud_text, (reader.width - 480, 32),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, hud_color, 2, cv2.LINE_AA)

            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break

    finally:
        reader.release()
        cv2.destroyAllWindows()
        print("-" * 75)
        print("TỔNG KẾT PHIÊN GIÁM SÁT VERSION 1.0:")
        print(f"  • Tổng số frames đã xử lý               : {frame_count}")
        print(f"  • Tốc độ xử lý trung bình (FPS)         : {fps_tracker.smoothed_fps:.1f} FPS")
        print(f"  • Tổng số sự kiện vi phạm được kích hoạt : {total_confirmed_events}")
        print("[OK] Đã giải phóng tài nguyên an toàn.")
        print("=" * 75)

    return True


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    cfg = sys.argv[2] if len(sys.argv) > 2 else None
    run_temporal_pipeline(target, config_path=cfg)
