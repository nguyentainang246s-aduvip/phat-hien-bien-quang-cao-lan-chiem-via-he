"""
Test suite cho module database/db.py (SQLite Database Management)
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath("."))

from database import ViolationDatabase


def test_violation_database():
    print("=" * 65)
    print("KIỂM THỬ MODULE DATABASE: SQLITE VIOLATION DB (TASK 24)")
    print("=" * 65)

    test_db_file = "data/test_surveillance.db"
    if os.path.exists(test_db_file):
        os.remove(test_db_file)

    db = ViolationDatabase(db_path=test_db_file)

    # 1. Thử chèn 2 bản ghi vi phạm
    id1 = db.insert_violation(
        camera_id="camera_01",
        track_id=1,
        timestamp="2026-09-15 10:30:00",
        confidence=0.88,
        overlap_pct=85.2,
        full_image_path="evidence/records/cam_01/2026-09-15/violation_id1.jpg",
        crop_image_path="evidence/crops/cam_01/2026-09-15/crop_id1.jpg"
    )

    id2 = db.insert_violation(
        camera_id="camera_02",
        track_id=5,
        timestamp="2026-09-15 11:15:20",
        confidence=0.92,
        overlap_pct=91.0,
        full_image_path="evidence/records/cam_02/2026-09-15/violation_id5.jpg",
        crop_image_path="evidence/crops/cam_02/2026-09-15/crop_id5.jpg"
    )

    print(f"\n1. Đã chèn 2 bản ghi vi phạm thành công (ID: {id1}, {id2})")

    # 2. Kiểm tra truy vấn
    records = db.get_violations(camera_id="camera_01")
    print(f"  • Truy vấn theo camera_01: Tìm thấy {len(records)} bản ghi.")
    assert len(records) == 1
    assert records[0]["track_id"] == 1
    assert records[0]["overlap_pct"] == 85.2

    # 3. Kiểm tra thống kê
    stats = db.get_statistics()
    print("\n2. Thống kê tổng quan CSDL:")
    print(f"  • Tổng số vụ vi phạm  : {stats['total_violations']}")
    print(f"  • Thống kê theo camera : {stats['violations_by_camera']}")
    assert stats["total_violations"] == 2
    assert stats["violations_by_camera"]["camera_01"] == 1
    assert stats["violations_by_camera"]["camera_02"] == 1

    # 4. Kiểm tra cập nhật trạng thái (Human-in-the-Loop)
    ok_conf = db.update_violation_status(id1, "confirmed", reviewed_by="Đ/c Nguyễn Văn A")
    assert ok_conf is True

    ok_dism = db.update_violation_status(id2, "dismissed", reviewed_by="Đ/c Trần Thị B", dismiss_reason="Biển có giấy phép hợp lệ")
    assert ok_dism is True

    # Kiểm tra truy vấn theo trạng thái
    pending_list = db.get_violations(status="pending")
    confirmed_list = db.get_violations(status="confirmed")
    dismissed_list = db.get_violations(status="dismissed")

    assert len(pending_list) == 0
    assert len(confirmed_list) == 1
    assert confirmed_list[0]["reviewed_by"] == "Đ/c Nguyễn Văn A"
    assert len(dismissed_list) == 1
    assert dismissed_list[0]["dismiss_reason"] == "Biển có giấy phép hợp lệ"

    # Kiểm tra thống kê theo trạng thái
    stats2 = db.get_statistics()
    assert stats2["violations_by_status"]["confirmed"] == 1
    assert stats2["violations_by_status"]["dismissed"] == 1

    # 5. Kiểm tra khử trùng lặp thông minh (Deduplication theo Incident Lifecycle)
    from datetime import datetime
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id3 = db.insert_violation(
        camera_id="camera_03",
        track_id=10,
        timestamp=now_str,
        confidence=0.85,
        overlap_pct=80.0,
        full_image_path="evidence/records/cam_03/test.jpg",
        bbox=(100, 100, 200, 200)
    )
    # Tọa độ lân cận trong dung sai margin_x, margin_y
    near_bbox = (105, 98, 202, 197)
    far_bbox = (500, 500, 600, 600)

    # 5.1. Khi trạng thái là pending: phát hiện trùng lặp
    assert db.is_duplicate_violation("camera_03", near_bbox, time_window_minutes=60) is True
    assert db.is_duplicate_violation("camera_03", far_bbox, time_window_minutes=60) is False

    # 5.2. Khi trạng thái chuyển sang confirmed: vẫn tiếp tục chặn trùng lặp
    db.update_violation_status(id3, "confirmed", reviewed_by="Đ/c Test")
    assert db.is_duplicate_violation("camera_03", near_bbox, time_window_minutes=60) is True

    # 5.3. Khi trạng thái là dismissed (có giấy phép): chặn trùng lặp trong 24 giờ
    db.update_violation_status(id3, "dismissed", reviewed_by="Đ/c Test", dismiss_reason="Được cấp phép")
    assert db.is_duplicate_violation("camera_03", near_bbox, time_window_minutes=60) is True

    # 5.4. Khi trạng thái là resolved (đã xử lý/thu dọn): cho phép phát hiện vụ việc mới
    db.update_violation_status(id3, "resolved", reviewed_by="Đ/c Test")
    assert db.is_duplicate_violation("camera_03", near_bbox, time_window_minutes=60) is False

    # 5.5. Kiểm tra hồ sơ pending tạo cách đây 2 giờ (-2 hours) vẫn chặn trùng lặp tuyệt đối (loại bỏ cửa sổ 60p)
    from datetime import timedelta
    two_hours_ago = (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    id4 = db.insert_violation(
        camera_id="camera_04",
        track_id=15,
        timestamp=two_hours_ago,
        confidence=0.90,
        overlap_pct=85.0,
        full_image_path="evidence/records/cam_04/old.jpg",
        bbox=(300, 300, 400, 400)
    )
    old_pending_near = (305, 298, 402, 397)
    # Vụ việc pending từ 2 giờ trước vẫn đang tồn tại -> is_duplicate_violation PHẢI trả về True
    assert db.is_duplicate_violation("camera_04", old_pending_near) is True
    assert db.is_duplicate_violation("camera_04", far_bbox) is False

    # Dọn dẹp file test db
    if os.path.exists(test_db_file):
        os.remove(test_db_file)

    print("\n[OK] 100% CSDL SQLITE HOẠT ĐỘNG HOÀN HẢO THEO CHUẨN ĐỒ ÁN!")
    print("=" * 65)


if __name__ == "__main__":
    success = test_violation_database()
    sys.exit(0 if success else 1)
