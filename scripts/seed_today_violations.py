import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import cv2
from tracking import ObjectTracker, TemporalVerifier, TrackState
from roi import ROIManager
from violation import ViolationChecker
from evidence import EvidenceSaver
from database import ViolationDatabase

db = ViolationDatabase("data/surveillance.db")
evidence_saver = EvidenceSaver(base_dir="evidence", blur_faces=True)

# 3 video CCTV kèm cấu hình ROI chuẩn
VIDEOS = [
    {
        "name": "Camera 1: Phố Hàng Bạc",
        "camera_id": "video test",
        "video_path": "data/videos/video test.mp4",
        "roi_path": "configs/roi_video_test.json"
    },
    {
        "name": "Camera 2: Phố Bạch Mai",
        "camera_id": "videotesst2",
        "video_path": "data/videos/videotesst2.mp4",
        "roi_path": "configs/roi_videotesst2.json"
    },
    {
        "name": "Camera 3: Phố Trần Đại Nghĩa",
        "camera_id": "video test3",
        "video_path": "data/videos/video test3.mp4",
        "roi_path": "configs/roi_video_test3.json"
    }
]

print("=" * 70)
print(f"KHỞI CHẠY TẠO HỒ SƠ VI PHẠM MỚI CHO NGÀY HÔM NAY ({datetime.now().strftime('%d/%m/%Y')})")
print("Sử dụng mô hình YOLOv8n v13_clean mới nhất: models/best.pt")
print("=" * 70)

total_today_inserted = 0

for v_info in VIDEOS:
    v_path = v_info["video_path"]
    cam_id = v_info["camera_id"]
    roi_path = v_info["roi_path"]
    name = v_info["name"]

    if not os.path.exists(v_path):
        print(f"[!] Không tìm thấy video: {v_path}, bỏ qua.")
        continue

    print(f"\n[*] Đang xử lý {name} ({cam_id})...")
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0

    tracker = ObjectTracker(model_path="models/best.pt", conf_threshold=0.25, imgsz=1280)
    roi_mgr = ROIManager(roi_path)
    checker = ViolationChecker(threshold=0.30)
    verifier = TemporalVerifier(confirm_frames=20, confirm_seconds=3.0, source_fps=fps)

    frame_idx = 0
    confirmed_tracks = set()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        clean_frame = frame.copy()
        
        # Chỉ chạy infer mỗi 3 frames để tối ưu tốc độ
        if frame_idx % 3 != 1:
            continue

        tracked_objects = tracker.track(frame)
        ts = frame_idx / fps
        verified_objects = verifier.process_frame(tracked_objects, checker, roi_mgr.polygons, current_timestamp=ts)

        for obj in verified_objects:
            tid = obj["track_id"]
            stat = obj["temporal_status"]
            sp = obj["spatial_res"]
            box = obj["box"]
            conf = obj["conf"]

            if stat == TrackState.CONFIRMED and obj.get("is_new_alert", False):
                if not db.is_duplicate_violation(cam_id, box):
                    ev_res = evidence_saver.save_evidence(
                        clean_frame, box, track_id=tid, camera_id=cam_id,
                        overlap_pct=sp["overlap_pct"], roi_frame=frame
                    )
                    if ev_res:
                        sw_idx = sp.get("sidewalk_index", 1)
                        rec_id = db.insert_violation(
                            camera_id=cam_id,
                            track_id=tid,
                            timestamp=ev_res["timestamp"],
                            confidence=conf,
                            overlap_pct=sp["overlap_pct"],
                            full_image_path=ev_res["full_path"],
                            crop_image_path=ev_res.get("crop_path", ""),
                            bbox=box,
                            sidewalk_index=sw_idx
                        )
                        confirmed_tracks.add(tid)
                        total_today_inserted += 1
                        print(f"   [VI PHẠM HÔM NAY #{rec_id}] Track #{tid} ({cam_id}): Overlap {sp['overlap_pct']}% | Conf {conf*100:.1f}%")

    cap.release()
    print(f"[✓] {name}: Đã ghi nhận {len(confirmed_tracks)} hồ sơ vi phạm mới.")

print("\n" + "=" * 70)
print(f"[THÀNH CÔNG] Đã ghi nhận tổng cộng {total_today_inserted} hồ sơ vi phạm cho ngày hôm nay ({datetime.now().strftime('%d/%m/%Y')})!")
print("=" * 70)

