"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
TASK: 16 - Đánh giá và Chạy thử nghiệm mô hình đã huấn luyện (models/best.pt)
==============================================================================
"""

import os
import sys
import cv2

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from camera import VideoReader
from detection import YOLODetector
from utils import FPSTracker, draw_fps_badge, draw_detection

def run_custom_model_demo():
    print("=" * 65)
    print("BẮT ĐẦU TASK 16: KIỂM THỬ MÔ HÌNH CUSTOM TRAINED (models/best.pt)")
    print("=" * 65)
    
    model_path = "models/best.pt"
    if not os.path.exists(model_path):
        print(f"[LỖI] Không tìm thấy file: {model_path}")
        return False
        
    # Khởi tạo detector với bộ não do bạn tự đào tạo
    detector = YOLODetector(model_path=model_path, conf_threshold=0.25)
    
    # Nguồn video kiểm thử
    video_path = "data/videos/sample_cctv.mp4"
    if os.path.exists("data/videos"):
        files = [f for f in os.listdir("data/videos") if f.lower().endswith(('.mp4', '.avi', '.mov'))]
        if files:
            video_path = os.path.join("data/videos", files[0])

    reader = VideoReader(video_path)
    fps_tracker = FPSTracker(alpha=0.15)
    
    window_name = "TASK 16 - Custom Signboard Model (Nhan 'q' de thoat)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, min(reader.width, 720), min(reader.height, 720))

    print(f"[+] Mô hình đã nạp : {model_path}")
    print(f"[+] Lớp nhận diện  : {detector.class_names}")
    print(f"[+] Nguồn video    : {video_path}")
    print("-" * 65)
    print("Đang quét và phát hiện biển hiệu thời gian thực... Nhấn 'q' để dừng.")

    try:
        while True:
            ret, frame = reader.read()
            if not ret:
                reader.reset()
                continue
                
            # Đưa frame qua mô hình AI tự huấn luyện
            detections = detector.detect(frame)
            
            # Vẽ từng biển hiệu phát hiện được lên frame
            for det in detections:
                box = det["box"]
                conf = det["conf"]
                label_text = f"Bien Quang Cao ({conf*100:.0f}%)"
                draw_detection(frame, box, label_text, is_violation=True)
                
            current_fps = fps_tracker.update()
            draw_fps_badge(frame, current_fps, reader.fps)
            
            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
                
    finally:
        reader.release()
        cv2.destroyAllWindows()
        print("[OK] Đã hoàn thành Task 16 an toàn.")

    return True

if __name__ == "__main__":
    run_custom_model_demo()
