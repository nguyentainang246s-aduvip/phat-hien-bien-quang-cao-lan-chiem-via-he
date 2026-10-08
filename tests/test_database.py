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

    # Dọn dẹp file test db
    if os.path.exists(test_db_file):
        os.remove(test_db_file)

    print("\n[OK] 100% CSDL SQLITE HOẠT ĐỘNG HOÀN HẢO THEO CHUẨN ĐỒ ÁN!")
    print("=" * 65)
    return True


if __name__ == "__main__":
    success = test_violation_database()
    sys.exit(0 if success else 1)
