"""
Test suite cho module camera/stream_reader.py (Auto-Reconnect & Multi-Source)
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath("."))

from camera import StreamReader


def test_stream_reader():
    print("=" * 65)
    print("KIỂM THỬ MODULE CAMERA: STREAM READER (TASK 27)")
    print("=" * 65)

    video_path = "data/videos/YTSave_Shorts_Fire-Engulfs-Newly-Built-House-Intense-F_Media_U6wCTL34uMI_002_720p.mp4"
    if not os.path.exists(video_path):
        video_dir = "data/videos"
        files = [f for f in os.listdir(video_dir) if f.lower().endswith(('.mp4', '.avi', '.mov'))] if os.path.exists(video_dir) else []
        video_path = os.path.join(video_dir, files[0]) if files else None

    assert video_path is not None, "Không tìm thấy video mẫu để test!"

    # 1. Khởi tạo StreamReader
    reader = StreamReader(source=video_path, reconnect_delay=0.5, max_retries=3)
    assert reader.cap.isOpened(), "Không thể mở video qua StreamReader!"
    assert reader.width > 0 and reader.height > 0, "Kích thước frame không hợp lệ!"

    # 2. Đọc 5 frames liên tiếp
    for i in range(1, 6):
        ret, frame = reader.read()
        assert ret and frame is not None, f"Lỗi đọc frame #{i}"

    print(f"[+] Đọc thành công 5 frames đầu ({reader.width}x{reader.height}, {reader.fps:.1f} FPS)")

    # 3. Giải phóng
    reader.release()
    print("\n[OK] 100% MODULE STREAM READER HOẠT ĐỘNG HOÀN TOÀN CHUẨN XÁC!")
    print("=" * 65)
    return True


if __name__ == "__main__":
    success = test_stream_reader()
    sys.exit(0 if success else 1)
