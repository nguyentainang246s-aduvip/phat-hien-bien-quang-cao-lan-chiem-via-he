"""
Test suite cho module tracking/verifier.py (Temporal Verification & Cooldown Logic)
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath("."))

from tracking import TemporalVerifier, TrackState
from violation import ViolationChecker


def test_temporal_verifier():
    print("=" * 65)
    print("KIỂM THỬ BỘ LỌC THỜI GIAN VÀ COOLDOWN (TASK 22 - TEMPORAL VERIFIER)")
    print("=" * 65)

    checker = ViolationChecker(threshold=0.30)
    # Cấu hình: Xác nhận sau 5 frames để test nhanh; Cooldown 10 giây
    verifier = TemporalVerifier(confirm_frames=5, cooldown_seconds=10.0, max_missing_frames=5)

    # Đa giác vỉa hè giả lập
    test_poly = [[[100, 100], [500, 100], [500, 500], [100, 500]]]
    # Box vi phạm (rơi vào giữa vỉa hè)
    box_violating = (200, 200, 300, 400)

    print("\n1. Kiểm tra đối tượng đứng yên lấn chiếm vỉa hè (ID #1):")
    alert_triggered_count = 0

    for frame_idx in range(1, 8):
        tracked_objs = [{
            "track_id": 1,
            "box": box_violating,
            "conf": 0.85,
            "class_id": 0,
            "class_name": "signboard"
        }]

        results = verifier.process_frame(tracked_objs, checker, test_poly)
        res = results[0]

        status = res["temporal_status"]
        count = res["violation_frames"]
        is_alert = res["is_new_alert"]
        if is_alert:
            alert_triggered_count += 1

        print(f"  Frame #{frame_idx}: Count = {count} | Status = {status} | New Alert = {is_alert}")

        if frame_idx < 5:
            assert status == TrackState.SUSPECTED, f"Frame {frame_idx} phải là SUSPECTED!"
            assert not is_alert, "Chưa đủ 5 frames không được phép phát cảnh báo!"
        elif frame_idx == 5:
            assert status == TrackState.CONFIRMED, "Frame 5 phải nâng cấp thành CONFIRMED!"
            assert is_alert, "Frame 5 vừa đạt ngưỡng phải kích hoạt New Alert = True!"
        elif frame_idx > 5:
            assert status == TrackState.CONFIRMED, "Vẫn tiếp tục là CONFIRMED!"
            assert not is_alert, "Frame sau đó phải Cooldown, không được spam Alert!"

    assert alert_triggered_count == 1, "Cơ chế Cooldown thất bại, cảnh báo bị lặp lại!"
    print("  => [PASS] Đã xác nhận vi phạm đúng sau 5 frames liên tiếp và Cooldown thành công!")

    # 2. Kiểm tra đối tượng thoáng qua (Người bê biển đi qua trong 2 frames rồi rời đi)
    print("\n2. Kiểm tra đối tượng thoáng qua / Người bê biển đi ngang (ID #2):")
    transient_obj = [{
        "track_id": 2,
        "box": box_violating,
        "conf": 0.80,
        "class_id": 0,
        "class_name": "signboard"
    }]

    # Xuất hiện 2 frames vi phạm
    res_f1 = verifier.process_frame(transient_obj, checker, test_poly)[0]
    res_f2 = verifier.process_frame(transient_obj, checker, test_poly)[0]

    # Frame 3: Đối tượng rời khỏi vỉa hè (box nằm ngoài vỉa hè)
    box_legal = (600, 600, 700, 700)
    legal_obj = [{
        "track_id": 2,
        "box": box_legal,
        "conf": 0.80,
        "class_id": 0,
        "class_name": "signboard"
    }]
    res_f3 = verifier.process_frame(legal_obj, checker, test_poly)[0]

    print(f"  Frame #1 (Trên vỉa hè): Status = {res_f1['temporal_status']} (Count: {res_f1['violation_frames']})")
    print(f"  Frame #2 (Trên vỉa hè): Status = {res_f2['temporal_status']} (Count: {res_f2['violation_frames']})")
    print(f"  Frame #3 (Đã rời đi)  : Status = {res_f3['temporal_status']} (Count: {res_f3['violation_frames']})")

    assert res_f1["temporal_status"] == TrackState.SUSPECTED
    assert res_f2["temporal_status"] == TrackState.SUSPECTED
    assert res_f3["temporal_status"] == TrackState.SUSPECTED  # Giảm dần, không bị phạt!
    assert not res_f1["is_new_alert"] and not res_f2["is_new_alert"] and not res_f3["is_new_alert"]

    print("  => [PASS] Loại bỏ 100% cảnh báo giả cho đối tượng thoáng qua!")

    # 3. Kiểm tra cơ chế Reset khi đối tượng không vi phạm quá tolerance_frames (Issue 05)
    print("\n3. Kiểm tra cơ chế Reset dung sai khi đối tượng không vi phạm (Tolerance Reset):")
    # Frame 4 & 5 tiếp tục không vi phạm -> non_viol_streak > 2 -> count phải reset về 0 và status về NORMAL
    res_f4 = verifier.process_frame(legal_obj, checker, test_poly)[0]
    res_f5 = verifier.process_frame(legal_obj, checker, test_poly)[0]
    print(f"  Frame #4 (Không vi phạm lần 2): Count = {res_f4['violation_frames']} | Status = {res_f4['temporal_status']}")
    print(f"  Frame #5 (Không vi phạm lần 3): Count = {res_f5['violation_frames']} | Status = {res_f5['temporal_status']}")
    assert res_f5["violation_frames"] == 0 and res_f5["temporal_status"] == TrackState.NORMAL
    print("  => [PASS] Đã reset hoàn toàn bộ đếm về 0 khi không vi phạm quá thời gian dung sai!")

    # 4. Kiểm tra đối tượng bị che khuất (Occlusion Decay - Issue 06)
    print("\n4. Kiểm tra xử lý khi đối tượng bị che khuất / mất dấu (Occlusion Decay):")
    # Cho đối tượng ID #3 vi phạm 4 frames (gần đạt confirm 5)
    obj3 = [{"track_id": 3, "box": box_violating, "conf": 0.85, "class_id": 0, "class_name": "signboard"}]
    for _ in range(4):
        verifier.process_frame(obj3, checker, test_poly)
    assert verifier.track_records[3]["count"] == 4

    # Sau đó đối tượng biến mất khỏi detection trong 4 frames (do xe tải che khuất)
    for _ in range(4):
        verifier.process_frame([], checker, test_poly)
    
    # 5. Kiểm tra đối tượng di động mang biển (Người đi bộ bê biển đi ngang - ISSUE 07)
    print("\n5. Kiểm tra đối tượng di chuyển liên tục (Người đi bộ mang biển đi ngang):")
    # Biển di chuyển mỗi frame 20px theo trục X (sau 5 frames dời 80px > max_displacement_pixels=50)
    for f in range(6):
        moving_box = (150 + f * 20, 200, 250 + f * 20, 400)
        obj_moving = [{"track_id": 4, "box": moving_box, "conf": 0.85, "class_id": 0, "class_name": "signboard"}]
        res_moving = verifier.process_frame(obj_moving, checker, test_poly)[0]
    
    print(f"  ID #4 sau 6 frames di chuyển: Status = {res_moving['temporal_status']} | New Alert = {res_moving['is_new_alert']}")
    assert res_moving["temporal_status"] == TrackState.SUSPECTED, "Đối tượng di chuyển không được nâng cấp lên CONFIRMED!"
    assert not res_moving["is_new_alert"], "Đối tượng di chuyển không được phát cảnh báo!"
    print("  => [PASS] Loại bỏ thành công đối tượng di động mang biển lướt qua vỉa hè!")

    # 6. Kiểm tra khử trùng lặp không gian khi nhảy ID (Spatial Deduplication - ISSUE 08)
    print("\n6. Kiểm tra khử trùng lặp không gian khi ByteTrack đổi ID (Spatial Deduplication):")
    verifier.reset()
    # ID #5 đứng yên tại (200, 200, 300, 400), confirm sau 5 frames -> Alert = True
    obj5 = [{"track_id": 5, "box": box_violating, "conf": 0.85, "class_id": 0, "class_name": "signboard"}]
    for _ in range(5):
        res5 = verifier.process_frame(obj5, checker, test_poly)[0]
    assert res5["is_new_alert"], "ID #5 phải phát cảnh báo đầu tiên!"

    # Sau đó mất dấu và sinh ra ID mới #6 tại cùng vị trí (202, 201, 302, 401)
    obj6 = [{"track_id": 6, "box": (202, 201, 302, 401), "conf": 0.85, "class_id": 0, "class_name": "signboard"}]
    for _ in range(5):
        res6 = verifier.process_frame(obj6, checker, test_poly)[0]
    print(f"  ID #6 (ID mới tại vị trí cũ trong cooldown): Status = {res6['temporal_status']} | New Alert = {res6['is_new_alert']}")
    assert res6["temporal_status"] == TrackState.CONFIRMED
    assert not res6["is_new_alert"], "ID mới cùng vị trí trong thời gian Cooldown không được phát cảnh báo trùng!"
    print("  => [PASS] Khử trùng lặp cảnh báo theo vị trí không gian thành công 100%!")

    print("\n" + "=" * 65)
    print("[THÀNH CÔNG] 100% UNIT TEST BỘ LỌC THỜI GIAN (TASK 22) ĐẠT CHUẨN TUYỆT ĐỐI!")
    print("=" * 65)
    return True


if __name__ == "__main__":
    success = test_temporal_verifier()
    sys.exit(0 if success else 1)
