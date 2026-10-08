import os
import sys
# Tự động trỏ về thư mục gốc của đồ án
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
TASK: 09 - Chạy thử nghiệm mô hình AI YOLOv8n trên Video (Milestone M2)
==============================================================================
"""

import os
import sys
import cv2

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Import các module đã chuẩn hóa ở Task 08
from camera import VideoReader
from utils import FPSTracker, draw_fps_badge

def run_yolo_demo():
    print("=" * 65)
    print("BẮT ĐẦU TASK 09: KHỞI TẠO VÀ CHẠY THỬ MÔ HÌNH AI YOLOV8")
    print("=" * 65)
    
    # 1. NẠP MÔ HÌNH YOLOV8 NANO
    # ultralytics sẽ tự động tải trọng số 'yolov8n.pt' (~6.2 MB) ở lần chạy đầu tiên
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[LỖI] Chưa cài đặt thư viện ultralytics! Vui lòng chờ cài đặt hoàn tất.")
        return False
        
    print("[+] Đang nạp mô hình YOLOv8n (Nano - phiên bản tối ưu nhẹ nhất)...")
    model = YOLO("yolov8n.pt")
    print("[OK] Đã nạp xong mô hình YOLOv8n thành công!")

    # 2. MỞ LUỒNG VIDEO BẰNG MODULE CAMERA
    video_path = "data/videos/sample_cctv.mp4"
    if os.path.exists("data/videos"):
        files = [f for f in os.listdir("data/videos") if f.lower().endswith(('.mp4', '.avi', '.mov'))]
        if files:
            video_path = os.path.join("data/videos", files[0])

    reader = VideoReader(video_path)
    fps_tracker = FPSTracker(alpha=0.15)
    
    window_name = "TASK 09 - YOLOv8n Object Detection (Nhan 'q' de thoat)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, min(reader.width, 720), min(reader.height, 720))

    print(f"[+] Nguồn video: {video_path} ({reader.width}x{reader.height}, {reader.fps:.1f} FPS)")
    print("-" * 65)
    print("Đang phát hiện vật thể thời gian thực bằng AI... Nhấn 'q' để dừng.")

    frame_idx = 0
    try:
        while True:
            ret, frame = reader.read()
            if not ret:
                # Tua lại đầu video để xem liên tục
                reader.reset()
                continue
                
            frame_idx += 1
            
            # 3. DÒNG CỐT LÕI: ĐƯA FRAME VÀO MÔ HÌNH AI YOLO ĐỂ DỰ ĐOÁN
            # conf=0.35: Chỉ lấy các vật thể có độ tin cậy >= 35%
            # verbose=False: Tắt in log rác ra màn hình terminal
            results = model.predict(frame, conf=0.35, verbose=False)
            
            # 4. VẼ KẾT QUẢ DETECTION LÊN FRAME
            # results[0].plot() tự động vẽ Bounding Box, nhãn class và confidence
            annotated_frame = results[0].plot()
            
            # Đo và in Processing FPS thực tế khi vừa chạy AI vừa hiển thị
            current_fps = fps_tracker.update()
            draw_fps_badge(annotated_frame, current_fps, reader.fps)
            
            cv2.imshow(window_name, annotated_frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
                
    finally:
        reader.release()
        cv2.destroyAllWindows()
        print(f"[OK] Đã hoàn thành Task 09 an toàn. Processing FPS với AI: {fps_tracker.smoothed_fps:.1f}")

    return True

if __name__ == "__main__":
    run_yolo_demo()
