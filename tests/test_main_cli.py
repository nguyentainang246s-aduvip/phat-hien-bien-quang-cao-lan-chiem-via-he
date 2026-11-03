"""
Unit test for Unified System Entry Point (main.py) using standard library unittest.
"""
import os
import sys
import subprocess
import unittest

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class TestMainCLI(unittest.TestCase):
    def test_main_help(self):
        res = subprocess.run(
            [sys.executable, "main.py", "--help"],
            capture_output=True, text=True, encoding="utf-8"
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("CCTV Sidewalk Signboard Surveillance System", res.stdout)
        self.assertIn("--mode", res.stdout)
        self.assertIn("monitor", res.stdout)
        self.assertIn("dashboard", res.stdout)
        self.assertIn("roi", res.stdout)

    def test_main_monitor_image_headless(self):
        img_path = "data/images/Duck-ai-image-2026-09-14-09-20 (1).jpeg"
        if not os.path.exists(img_path):
            self.skipTest(f"Image not found: {img_path}")

        res = subprocess.run(
            [sys.executable, "main.py", "--mode", "monitor", "--source", img_path, "--config", "configs/roi_moi.json", "--headless"],
            capture_output=True, text=True, encoding="utf-8"
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("BẰNG CHỨNG", res.stdout)
        self.assertIn("DB record", res.stdout)

    def test_main_monitor_video_max_frames(self):
        res = subprocess.run(
            [sys.executable, "main.py", "--mode", "monitor", "--max-frames", "10", "--headless"],
            capture_output=True, text=True, encoding="utf-8"
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("TỔNG KẾT PHIÊN GIÁM SÁT", res.stdout)
        self.assertIn("Tổng số khung hình đã xử lý", res.stdout)

    def test_main_invalid_source(self):
        res = subprocess.run(
            [sys.executable, "main.py", "--mode", "monitor", "--source", "non_existent_file.mp4", "--headless"],
            capture_output=True, text=True, encoding="utf-8"
        )
        self.assertIn("không tồn tại", res.stdout)
        self.assertEqual(res.returncode, 1)

    def test_main_live_stream_missing_roi(self):
        res = subprocess.run(
            [sys.executable, "main.py", "--mode", "monitor", "--source", "rtsp://camera_no_roi:554/stream", "--headless"],
            capture_output=True, text=True, encoding="utf-8"
        )
        self.assertEqual(res.returncode, 1)
        self.assertIn("LỖI CẤU HÌNH", res.stdout)
        self.assertIn("chưa được chỉ định cấu hình ROI", res.stdout)
        self.assertNotIn("Traceback", res.stderr)
        self.assertNotIn("NameError", res.stderr)

    def test_main_live_stream_masked_password(self):
        res = subprocess.run(
            [sys.executable, "main.py", "--mode", "monitor", "--source", "rtsp://admin:super_secret_pwd@192.168.1.50/live", "--headless"],
            capture_output=True, text=True, encoding="utf-8"
        )
        self.assertEqual(res.returncode, 1)
        self.assertNotIn("super_secret_pwd", res.stdout)
        self.assertIn("rtsp://admin:***@192.168.1.50/live", res.stdout)


if __name__ == "__main__":
    unittest.main()
