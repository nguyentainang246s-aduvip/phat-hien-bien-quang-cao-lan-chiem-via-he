"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Object Tracking Demo
TASK: 21 - Trực quan hóa thuật toán ByteTrack trên Video Camera CCTV
==============================================================================
"""

import os
import sys
import time
import cv2

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from camera import VideoReader
from tracking import ObjectTracker
from utils import FPSTracker, draw_fps_badge, draw_detection


def run_tracking_demo(video_path: str = None, model_path: str = "models/best.pt"):
    print("=" * 70)
    print("DEMO BÁM VẾT BIỂN HIỆU THỜI GIAN THỰC (BYTETRACK OBJECT TRACKING - TASK 21)")
    print("=" * 70)

    # 1. Tìm video kiểm thử
    if video_path is None or not os.path.exists(video_path):
        video_dir = "data/videos"
        files = [f for f in os.listdir(video_dir) if f.lower().endswith(('.mp4', '.avi', '.mov'))] if os.path.exists(video_dir) else []
        video_path = os.path.join(video_dir, files[0]) if files else "data/videos/sample_cctv.mp4"

    if not os.path.exists(model_path):
        model_path = "yolov8n.pt"

    # 2. Khởi tạo Tracker & VideoReader
    tracker = ObjectTracker(model_path=model_path, conf_threshold=0.20)
    reader = VideoReader(video_path)
    fps_tracker = FPSTracker(alpha=0.15)

    window_name = "TASK 21: ByteTrack Multi-Object Tracking (Nhan 'q' de dung)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, min(reader.width, 960), min(reader.height, 720))

    print(f"[+] Nguồn video CCTV : {video_path} ({reader.width}x{reader.height}, {reader.fps:.1f} FPS)")
    print(f"[+] Thuật toán       : ByteTrack (Ultralytics Tracking Engine)")
    print("-" * 70)
    print(">> ĐANG CHẠY BÁM VẾT... Mỗi biển hiệu sẽ được cấp 1 mã định danh: ID: #1, ID: #2,...")

    unique_track_ids = set()
    frame_count = 0

    try:
        while True:
            ret, frame = reader.read()
            if not ret:
                reader.reset()
                tracker.reset()
                continue

            frame_count += 1

            # A. CHẠY BÁM VẾT BYTETRACK TRÊN KHUNG HÌNH GỐC
            t0 = time.perf_counter()
            tracked_objects = tracker.track(frame)
            infer_time = (time.perf_counter() - t0) * 1000

            # B. VẼ TỪNG VẬT THỂ KÈM MÃ TRACK_ID
            for obj in tracked_objects:
                track_id = obj["track_id"]
                box = obj["box"]
                conf = obj["conf"]
                if track_id > 0:
                    unique_track_ids.add(track_id)

                label = f"Conf: {conf*100:.0f}%"
                draw_detection(frame, box, label, is_violation=False, track_id=track_id)

            # C. VẼ HUD THÔNG SỐ
            fps_val = fps_tracker.update()
            draw_fps_badge(frame, fps_val, reader.fps)

            hud_text = f"Dang theo doi: {len(tracked_objects)} bien | Tong IDs: {len(unique_track_ids)}"
            cv2.putText(frame, hud_text, (20, reader.height - 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break

    finally:
        reader.release()
        cv2.destroyAllWindows()
        print("-" * 70)
        print("TỔNG KẾT PHIÊN TRACKING:")
        print(f"  • Tổng số frames đã xử lý        : {frame_count}")
        print(f"  • Tốc độ bám vết trung bình (FPS): {fps_tracker.smoothed_fps:.1f} FPS")
        print(f"  • Tổng số vật thể định danh duy nhất: {len(unique_track_ids)} (IDs: {sorted(list(unique_track_ids))})")
        print("[OK] Đã hoàn thành thử nghiệm ByteTrack.")
        print("=" * 70)


if __name__ == "__main__":
    vid = sys.argv[1] if len(sys.argv) > 1 else None
    run_tracking_demo(vid)
