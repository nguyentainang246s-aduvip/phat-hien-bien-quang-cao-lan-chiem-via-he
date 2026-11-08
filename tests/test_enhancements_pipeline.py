"""
==============================================================================
Test suite kiểm thử chuyên sâu Bộ 3 Cải tiến:
  (1) Hysteresis Thresholding (Ngưỡng trễ kép kích hoạt & duy trì ByteTrack)
  (2) Motion Filter (Bộ lọc vận tốc & loại trừ đối tượng di chuyển)
  (3) Spatial Adaptive Thresholding (Ngưỡng tự thích ứng không gian theo ROI)
==============================================================================
"""

import os
import sys
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath("."))

from tracking.motion_filter import MotionFilter
from tracking.verifier import TemporalVerifier, TrackState
from tracking.tracker import ObjectTracker
from violation.checker import ViolationChecker


def test_motion_filter_stationary():
    """Kiểm tra đối tượng đứng yên hoàn toàn."""
    mf = MotionFilter(
        max_displacement_pixels=40.0,
        max_velocity_pixels_per_sec=35.0,
        window_seconds=1.0,
        min_stationary_seconds=0.5
    )

    box = (100, 100, 200, 300)
    # Cập nhật vị trí qua 5 mốc thời gian cách nhau 0.1s (tổng 0.5s)
    res = None
    for i in range(6):
        t = i * 0.1
        res = mf.update(track_id=1, box=box, timestamp=t)

    assert not res["is_moving"], "Vật thể đứng yên không được coi là moving!"
    assert res["is_stationary"], "Vật thể đứng yên sau 0.5s phải được coi là stationary!"
    assert res["velocity_px_s"] == 0.0, f"Vận tốc phải bằng 0, nhận được: {res['velocity_px_s']}"
    assert res["status"] == "STATIONARY"


def test_motion_filter_moving_vehicle():
    """Kiểm tra xe buýt/người bê biển di chuyển với vận tốc cao."""
    mf = MotionFilter(
        max_displacement_pixels=40.0,
        max_velocity_pixels_per_sec=35.0,
        window_seconds=1.0,
        min_stationary_seconds=1.0
    )

    # Mỗi 0.1s di chuyển 20 pixels => Vận tốc = 200 px/s
    res = None
    for i in range(5):
        t = i * 0.1
        box = (100 + i * 20, 100, 200 + i * 20, 300)
        res = mf.update(track_id=2, box=box, timestamp=t)

    assert res["is_moving"], "Vật thể di chuyển 200px/s bắt buộc phải is_moving=True!"
    assert not res["is_stationary"], "Vật thể di chuyển không được là stationary!"
    assert res["velocity_px_s"] > 35.0, f"Vận tốc ước lượng {res['velocity_px_s']} phải lớn hơn 35 px/s!"
    assert res["status"] == "MOVING"


def test_spatial_adaptive_logic():
    """Kiểm tra logic phân định ngưỡng trong ROI vỉa hè vs ngoài ROI."""
    polygons = [
        [[100, 100], [500, 100], [500, 500], [100, 500]]  # Vùng vỉa hè
    ]

    # Hộp 1: Chân đế (300, 400) nằm TRONG vỉa hè
    box_inside = (250, 200, 350, 400)
    is_in_1 = ObjectTracker.is_box_in_roi(box_inside, polygons)
    assert is_in_1, "Hộp nằm trong vùng vỉa hè phải trả về True!"

    # Hộp 2: Chân đế (800, 800) nằm NGOÀI vỉa hè (lòng đường hoặc trên cao)
    box_outside = (750, 600, 850, 800)
    is_in_2 = ObjectTracker.is_box_in_roi(box_outside, polygons)
    assert not is_in_2, "Hộp ngoài vỉa hè phải trả về False!"


def test_combined_temporal_moving_rejection():
    """Kiểm tra TemporalVerifier kết hợp MotionFilter loại trừ vật thể di chuyển (TrackState.MOVING)."""
    checker = ViolationChecker(threshold=0.30)
    test_poly = [[[100, 100], [500, 100], [500, 500], [100, 500]]]

    verifier = TemporalVerifier(
        confirm_frames=5,
        confirm_seconds=0.5,
        min_stationary_seconds=0.4,
        max_velocity_pixels_per_sec=30.0,
        max_displacement_pixels=30.0,
    )

    # Giả lập đối tượng di chuyển liên tục qua vùng vỉa hè
    # Di chuyển 15px mỗi frame (150 px/s ở 10 FPS)
    for frame_idx in range(1, 8):
        t = (frame_idx - 1) * 0.1
        box = (150 + frame_idx * 15, 200, 250 + frame_idx * 15, 400)
        tracked_objs = [{
            "track_id": 99,
            "box": box,
            "conf": 0.88,
            "class_id": 0,
            "class_name": "signboard"
        }]
        res = verifier.process_frame(tracked_objs, checker, test_poly, current_timestamp=t)[0]

        # Ở frame >= 2 khi có ít nhất 2 mốc thời gian:
        if frame_idx >= 2:
            assert res["is_moving"], f"Frame {frame_idx} phải được đánh dấu is_moving=True!"
            assert "DI CHUYEN" in res["suspect_reason"], f"Lý do nghi vấn phải là DI CHUYEN, thực tế: {res['suspect_reason']}"
            assert res["temporal_status"] != TrackState.CONFIRMED, "Vật thể di chuyển không được là CONFIRMED!"
            assert not res["is_new_alert"], "Vật thể di chuyển tuyệt đối không được phát cảnh báo vi phạm!"

    print("[PASS] Đã xác thực thành công: Vật thể di chuyển bị phân loại MOVING và bị loại trừ khỏi cảnh báo vi phạm!")


def test_combined_stationary_confirmation():
    """Kiểm tra đối tượng đứng yên tĩnh trên vỉa hè được xác nhận CONFIRMED."""
    checker = ViolationChecker(threshold=0.30)
    test_poly = [[[100, 100], [500, 100], [500, 500], [100, 500]]]

    verifier = TemporalVerifier(
        confirm_frames=5,
        confirm_seconds=0.5,
        min_stationary_seconds=0.3,
        max_velocity_pixels_per_sec=30.0,
        max_displacement_pixels=30.0,
    )

    static_box = (200, 200, 300, 400)
    res = None
    for frame_idx in range(1, 8):
        t = (frame_idx - 1) * 0.1
        tracked_objs = [{
            "track_id": 100,
            "box": static_box,
            "conf": 0.85,
            "class_id": 0,
            "class_name": "signboard"
        }]
        res = verifier.process_frame(tracked_objs, checker, test_poly, current_timestamp=t)[0]

    assert res["temporal_status"] == TrackState.CONFIRMED, f"Sau 0.7s đứng yên, biển tĩnh phải là CONFIRMED! Nhận được: {res['temporal_status']}"
    print("[PASS] Biển tĩnh đứng yên trên vỉa hè được xác nhận CONFIRMED chuẩn xác!")
