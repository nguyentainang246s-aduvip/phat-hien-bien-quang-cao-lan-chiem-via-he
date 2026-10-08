"""
Test suite cho module tracking/tracker.py (ByteTrack Object Tracking)
"""

import os
import sys
import cv2
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath("."))

from tracking import ObjectTracker



def test_object_tracker():
    print("=" * 60)
    print("KIỂM THỬ MODULE TRACKING: OBJECT TRACKER (BYTETRACK)")
    print("=" * 60)

    model_path = "models/best.pt" if os.path.exists("models/best.pt") else "yolov8n.pt"
    tracker = ObjectTracker(model_path=model_path, conf_threshold=0.20)

    # Đọc ảnh test
    img_path = "data/images/Duck-ai-image-2026-09-14-09-20 (1).jpeg"
    if not os.path.exists(img_path):
        print("[LỖI] Không tìm thấy ảnh kiểm thử!")
        return False

    frame = cv2.imread(img_path)

    # Chạy tracking qua 3 frame liên tiếp (giả lập video luồng tĩnh)
    print("\n1. Kiểm tra tracking qua 3 khung hình liên tiếp:")
    for f_idx in range(1, 4):
        tracked = tracker.track(frame)
        print(f"  Frame #{f_idx}: Phát hiện & theo dõi {len(tracked)} vật thể.")
        for item in tracked[:3]:  # In 3 vật thể đầu tiên
            print(f"    • ID: #{item['track_id']} | Box: {item['box']} | Conf: {item['conf']*100:.0f}% | Class: {item['class_name']}")

    # Kiểm tra cấu trúc dữ liệu đầu ra
    assert len(tracked) > 0, "Không phát hiện được vật thể nào!"
    first_item = tracked[0]
    assert "track_id" in first_item, "Thiếu trường 'track_id'!"
    assert "box" in first_item, "Thiếu trường 'box'!"
    assert len(first_item["box"]) == 4, "Tọa độ box không đủ 4 số (x1, y1, x2, y2)!"
    assert "conf" in first_item, "Thiếu trường 'conf'!"

    print("\n[OK] 100% CẤU TRÚC DỮ LIỆU ĐẦU RA TRACKING CHUẨN XÁC!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_object_tracker()
    sys.exit(0 if success else 1)
