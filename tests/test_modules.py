"""
Script kiểm thử tích hợp tất cả các module chuẩn hóa của Task 08
"""
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Đảm bảo đường dẫn gốc của đồ án nằm trong sys.path
sys.path.insert(0, os.path.abspath("."))

def test_all_modules():
    print("=" * 60)
    print("KIỂM TRA TÍCH HỢP TOÀN BỘ MODULE (TASK 08)")
    print("=" * 60)
    
    # 1. Test Module Camera
    try:
        from camera import VideoReader
        print("[OK] Import Module 'camera.VideoReader' thành công.")
    except Exception as e:
        print(f"[FAIL] Lỗi module camera: {e}")
        return False
        
    # 2. Test Module ROI
    try:
        from roi import ROIManager
        roi = ROIManager("configs/roi_camera1.json")
        print(f"[OK] Import Module 'roi.ROIManager' thành công (Camera: {roi.camera_id}).")
    except Exception as e:
        print(f"[FAIL] Lỗi module roi: {e}")
        return False
        
    # 3. Test Module Violation
    try:
        from violation import ViolationChecker
        checker = ViolationChecker(threshold=0.3)
        # Test 1 phép tính giao nhau mẫu
        res = checker.check_multi((100, 760, 400, 900), roi.polygons)
        print(f"[OK] Import Module 'violation.ViolationChecker' thành công (Test overlap: {res['overlap_pct']}%).")
    except Exception as e:
        print(f"[FAIL] Lỗi module violation: {e}")
        return False
        
    # 4. Test Module Utils
    try:
        from utils import FPSTracker, draw_fps_badge, draw_detection
        fps_tracker = FPSTracker()
        print("[OK] Import Module 'utils' (FPSTracker, Visualizer) thành công.")
    except Exception as e:
        print(f"[FAIL] Lỗi module utils: {e}")
        return False

    print("=" * 60)
    print(">> KẾT QUẢ: TOÀN BỘ 4 MODULE ĐÃ KẾT NỐI ĐỒNG BỘ 100%!")
    print(">> HỆ THỐNG SẴN SÀNG ĐÓN NHẬN MÔ HÌNH AI YOLO Ở TASK 09.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_all_modules()
    sys.exit(0 if success else 1)
