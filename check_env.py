"""
Script kiểm tra môi trường chạy cho Đồ án Tốt nghiệp
Hệ thống: Phát hiện biển quảng cáo/biển hiệu lấn chiếm vỉa hè qua CCTV cố định
Module: System Environment Verification
"""
import sys

# Cấu hình UTF-8 cho console trên Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def verify_environment():
    print("=" * 60)
    print("  KIỂM TRA MÔI TRƯỜNG THỰC THI (TASK 01)")
    print("=" * 60)
    
    # 1. Kiểm tra Python Interpreter
    python_path = sys.executable
    python_ver = sys.version.split()[0]
    print(f"[+] Trình thông dịch Python: {python_path}")
    print(f"[+] Phiên bản Python       : {python_ver}")
    
    # Đảm bảo đang chạy trong môi trường ảo (.venv)
    is_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if is_venv:
        print("[OK] Môi trường ảo (venv)   : ĐÃ KÍCH HOẠT CHÍNH XÁC")
    else:
        print("[CẢNH BÁO] Chưa kích hoạt venv! Đang dùng Python toàn cục.")

    all_passed = True

    # 2. Kiểm tra OpenCV
    try:
        import cv2
        print(f"[OK] OpenCV Version        : {cv2.__version__}")
    except ImportError as e:
        print(f"[FAIL] Lỗi OpenCV          : {e}")
        all_passed = False

    # 3. Kiểm tra NumPy
    try:
        import numpy as np
        print(f"[OK] NumPy Version         : {np.__version__}")
    except ImportError as e:
        print(f"[FAIL] Lỗi NumPy           : {e}")
        all_passed = False

    print("=" * 60)
    if all_passed and is_venv:
        print(">> KẾT QUẢ: TẤT CẢ TIÊU CHÍ ĐỀU ĐẠT CHUẨN!")
        print(">> HỆ THỐNG SẴN SÀNG CHO TASK 02.")
    elif all_passed and not is_venv:
        print(">> LƯU Ý: Thư viện đã cài nhưng cần kích hoạt .venv trước khi chạy.")
    else:
        print(">> KẾT QUẢ: MÔI TRƯỜNG CHƯA ĐẠT. VUI LÒNG KIỂM TRA CÁC MỤC [FAIL].")
    print("=" * 60)
    
    return all_passed and is_venv

if __name__ == "__main__":
    success = verify_environment()
    sys.exit(0 if success else 1)
