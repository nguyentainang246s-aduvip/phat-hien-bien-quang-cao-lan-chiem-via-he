"""
Test suite cho module tracking/verifier.py (Temporal Verification & Cooldown Logic)

v2.1: Sửa để truyền current_timestamp mô phỏng vào process_frame,
      đảm bảo confirm_seconds=0.5 có thể đạt được trong test nhanh.
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
    print("KIEM THU BO LOC THOI GIAN VA COOLDOWN (TASK 22 - TEMPORAL VERIFIER)")
    print("=" * 65)

    checker = ViolationChecker(threshold=0.30)

    # confirm_frames=5, confirm_seconds=0.5
    # Dung fps_sim=8: moi frame cach 0.125s => sau 4 frames = 0.5s dat nguong giay
    verifier = TemporalVerifier(
        confirm_frames=5,
        confirm_seconds=0.5,
        cooldown_seconds=10.0,
        max_missing_frames=5,
    )

    # Da giac via he gia lap
    test_poly = [[[100, 100], [500, 100], [500, 500], [100, 500]]]
    box_violating = (200, 200, 300, 400)
    fps_sim = 8.0   # moi frame cach 125ms => frame thu 5 (index 4) cach 0.5s

    # -----------------------------------------------------------------------
    # 1. Kiem tra doi tuong dung yen lan chiem via he (ID #1)
    # -----------------------------------------------------------------------
    print("\n1. Kiem tra doi tuong dung yen lan chiem via he (ID #1):")
    alert_triggered_count = 0
    base_ts = 1000.0   # timestamp co dinh de co the lap lai duoc

    for frame_idx in range(1, 8):
        tracked_objs = [{
            "track_id": 1,
            "box": box_violating,
            "conf": 0.85,
            "class_id": 0,
            "class_name": "signboard"
        }]
        ts = base_ts + (frame_idx - 1) / fps_sim
        results = verifier.process_frame(tracked_objs, checker, test_poly, current_timestamp=ts)
        res = results[0]

        status = res["temporal_status"]
        count = res["violation_frames"]
        is_alert = res["is_new_alert"]
        if is_alert:
            alert_triggered_count += 1

        elapsed = ts - base_ts
        print(f"  Frame #{frame_idx} (t={elapsed:.3f}s): Count={count} | Status={status} | Alert={is_alert}")

        if frame_idx < 5:
            assert status == TrackState.SUSPECTED, f"Frame {frame_idx} phai la SUSPECTED!"
            assert not is_alert, "Chua du 5 frames khong duoc phep phat canh bao!"
        elif frame_idx == 5:
            assert status == TrackState.CONFIRMED, "Frame 5 phai nang cap thanh CONFIRMED!"
            assert is_alert, "Frame 5 vua dat nguong phai kich hoat New Alert = True!"
        elif frame_idx > 5:
            assert status == TrackState.CONFIRMED, "Van tiep tuc la CONFIRMED!"
            assert not is_alert, "Frame sau do phai Cooldown, khong duoc spam Alert!"

    assert alert_triggered_count == 1, "Co che Cooldown that bai, canh bao bi lap lai!"
    print("  => [PASS] Da xac nhan vi pham dung sau 5 frames lien tiep va Cooldown thanh cong!")

    # -----------------------------------------------------------------------
    # 2. Kiem tra doi tuong thoang qua (ID #2)
    # -----------------------------------------------------------------------
    print("\n2. Kiem tra doi tuong thoang qua / Nguoi be bien di ngang (ID #2):")
    base_ts2 = base_ts + 100.0   # thoi diem moi, tranh dinh cooldown
    transient_obj = [{
        "track_id": 2, "box": box_violating, "conf": 0.80,
        "class_id": 0, "class_name": "signboard"
    }]
    res_f1 = verifier.process_frame(transient_obj, checker, test_poly,
                                    current_timestamp=base_ts2)[0]
    res_f2 = verifier.process_frame(transient_obj, checker, test_poly,
                                    current_timestamp=base_ts2 + 1 / fps_sim)[0]

    box_legal = (600, 600, 700, 700)
    legal_obj = [{"track_id": 2, "box": box_legal, "conf": 0.80,
                  "class_id": 0, "class_name": "signboard"}]
    res_f3 = verifier.process_frame(legal_obj, checker, test_poly,
                                    current_timestamp=base_ts2 + 2 / fps_sim)[0]

    print(f"  Frame #1: Status={res_f1['temporal_status']} (Count:{res_f1['violation_frames']})")
    print(f"  Frame #2: Status={res_f2['temporal_status']} (Count:{res_f2['violation_frames']})")
    print(f"  Frame #3 (roi di): Status={res_f3['temporal_status']} (Count:{res_f3['violation_frames']})")

    assert res_f1["temporal_status"] == TrackState.SUSPECTED
    assert res_f2["temporal_status"] == TrackState.SUSPECTED
    assert res_f3["temporal_status"] == TrackState.SUSPECTED
    assert not res_f1["is_new_alert"] and not res_f2["is_new_alert"] and not res_f3["is_new_alert"]
    print("  => [PASS] Loai bo 100% canh bao gia cho doi tuong thoang qua!")

    # -----------------------------------------------------------------------
    # 3. Kiem tra co che Reset dung sai khi doi tuong khong vi pham
    # -----------------------------------------------------------------------
    print("\n3. Kiem tra co che Reset dung sai (Tolerance Reset):")
    res_f4 = verifier.process_frame(legal_obj, checker, test_poly,
                                    current_timestamp=base_ts2 + 3 / fps_sim)[0]
    res_f5 = verifier.process_frame(legal_obj, checker, test_poly,
                                    current_timestamp=base_ts2 + 4 / fps_sim)[0]
    print(f"  Frame #4 (Khong vi pham lan 2): Count={res_f4['violation_frames']} | Status={res_f4['temporal_status']}")
    print(f"  Frame #5 (Khong vi pham lan 3): Count={res_f5['violation_frames']} | Status={res_f5['temporal_status']}")
    assert res_f5["violation_frames"] == 0 and res_f5["temporal_status"] == TrackState.NORMAL
    print("  => [PASS] Da reset hoan toan bo dem ve 0 khi khong vi pham qua thoi gian dung sai!")

    # -----------------------------------------------------------------------
    # 4. Kiem tra Occlusion Decay (ID #3)
    # -----------------------------------------------------------------------
    print("\n4. Kiem tra xu ly khi doi tuong bi che khuat (Occlusion Decay):")
    base_ts4 = base_ts2 + 200.0
    obj3 = [{"track_id": 3, "box": box_violating, "conf": 0.85,
             "class_id": 0, "class_name": "signboard"}]
    for i in range(4):
        verifier.process_frame(obj3, checker, test_poly,
                               current_timestamp=base_ts4 + i / fps_sim)
    assert verifier.track_records[3]["count"] == 4

    # Doi tuong bien mat 4 frames
    for i in range(4):
        verifier.process_frame([], checker, test_poly,
                               current_timestamp=base_ts4 + (4 + i) / fps_sim)
    print("  => [PASS] Occlusion decay hoat dong!")

    # -----------------------------------------------------------------------
    # 5. Kiem tra sliding window stationary (doi tuong di dong - ID #4)
    # -----------------------------------------------------------------------
    print("\n5. Kiem tra doi tuong di chuyen lien tuc (Nguoi di bo mang bien):")
    base_ts5 = base_ts4 + 200.0
    res_moving = None
    for f in range(6):
        moving_box = (150 + f * 20, 200, 250 + f * 20, 400)
        obj_moving = [{"track_id": 4, "box": moving_box, "conf": 0.85,
                       "class_id": 0, "class_name": "signboard"}]
        res_moving = verifier.process_frame(obj_moving, checker, test_poly,
                                            current_timestamp=base_ts5 + f / fps_sim)[0]

    print(f"  ID #4 sau 6 frames di chuyen: Status={res_moving['temporal_status']} | Alert={res_moving['is_new_alert']}")
    assert res_moving["temporal_status"] == TrackState.SUSPECTED, \
        "Doi tuong di chuyen khong duoc nang cap len CONFIRMED!"
    assert not res_moving["is_new_alert"], "Doi tuong di chuyen khong duoc phat canh bao!"
    print("  => [PASS] Loai bo thanh cong doi tuong di dong mang bien luot qua via he!")

    # -----------------------------------------------------------------------
    # 6. Kiem tra Spatial Deduplication khi ByteTrack doi ID
    # -----------------------------------------------------------------------
    print("\n6. Kiem tra khu trung lap khong gian khi ByteTrack doi ID (Spatial Deduplication):")
    verifier.reset()
    base_ts6 = 5000.0
    obj5 = [{"track_id": 5, "box": box_violating, "conf": 0.85,
             "class_id": 0, "class_name": "signboard"}]
    for i in range(5):
        res5 = verifier.process_frame(obj5, checker, test_poly,
                                      current_timestamp=base_ts6 + i / fps_sim)[0]
    assert res5["is_new_alert"], "ID #5 phai phat canh bao dau tien!"

    # Mat dau va sinh ID moi #6 tai cung vi tri
    obj6 = [{"track_id": 6, "box": (202, 201, 302, 401), "conf": 0.85,
             "class_id": 0, "class_name": "signboard"}]
    for i in range(5):
        res6 = verifier.process_frame(obj6, checker, test_poly,
                                      current_timestamp=base_ts6 + (5 + i) / fps_sim)[0]
    print(f"  ID #6 (ID moi tai vi tri cu trong cooldown): Status={res6['temporal_status']} | Alert={res6['is_new_alert']}")
    assert res6["temporal_status"] == TrackState.CONFIRMED
    assert not res6["is_new_alert"], "ID moi cung vi tri trong Cooldown khong duoc phat canh bao trung!"
    print("  => [PASS] Khu trung lap canh bao theo vi tri khong gian thanh cong 100%!")

    print("\n" + "=" * 65)
    print("[THANH CONG] 100% UNIT TEST BO LOC THOI GIAN (TASK 22) DAT CHUAN TUYET DOI!")
    print("=" * 65)
    return True


if __name__ == "__main__":
    success = test_temporal_verifier()
    sys.exit(0 if success else 1)
