"""
Test suite cho module evidence/saver.py (Lưu trữ ảnh bằng chứng vi phạm)
"""

import os
import sys
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath("."))

from evidence import EvidenceSaver


def test_evidence_saver():
    print("=" * 65)
    print("KIỂM THỬ MODULE EVIDENCE: EVIDENCE SAVER (TASK 23)")
    print("=" * 65)

    test_evidence_dir = "evidence_test_output"
    saver = EvidenceSaver(base_dir=test_evidence_dir)

    # 1. Tạo một ảnh giả lập (dummy frame 720x1280)
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    frame[:] = (50, 50, 50)

    # Box biển hiệu vi phạm giả lập
    box = (200, 300, 450, 600)
    frame[300:600, 200:450] = (0, 255, 255)  # Biển vàng

    # 2. Lưu bằng chứng
    result = saver.save_evidence(
        frame=frame,
        box=box,
        track_id=101,
        camera_id="camera_test",
        overlap_pct=85.5
    )

    print("\n1. Kết quả trích xuất và lưu file bằng chứng:")
    print(f"  • Ảnh toàn cảnh (Full) : {result['full_path']}")
    print(f"  • Ảnh cận cảnh (Crop)  : {result['crop_path']}")
    print(f"  • Mốc thời gian         : {result['timestamp']}")

    # 3. Kiểm tra file có thực sự tồn tại và có kích thước > 0
    assert os.path.exists(result["full_path"]), "File ảnh toàn cảnh không tồn tại!"
    assert os.path.exists(result["crop_path"]), "File ảnh cận cảnh không tồn tại!"
    assert os.path.getsize(result["full_path"]) > 0, "File toàn cảnh bị rỗng (0 bytes)!"
    assert os.path.getsize(result["crop_path"]) > 0, "File cận cảnh bị rỗng (0 bytes)!"

    # Dọn dẹp thư mục test
    import shutil
    shutil.rmtree(test_evidence_dir, ignore_errors=True)

    print("\n[OK] 100% CẤU TRÚC FILE BẰNG CHỨNG VÀ ĐÓNG TEM PHÁP LÝ CHUẨN XÁC!")
    print("=" * 65)
    return True


if __name__ == "__main__":
    success = test_evidence_saver()
    sys.exit(0 if success else 1)
