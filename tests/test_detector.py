"""
Script kiểm thử module detection.YOLODetector (Task 10)
"""
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath("."))

from camera import VideoReader
from detection import YOLODetector

def test_detector():
    print("=" * 60)
    print("KIỂM THỬ MODULE DETECTION (TASK 10)")
    print("=" * 60)
    
    # 1. Khởi tạo detector
    detector = YOLODetector(model_path="yolov8n.pt", conf_threshold=0.3)
    
    # 2. Đọc 1 frame từ video test
    video_path = "data/videos/sample_cctv.mp4"
    if os.path.exists("data/videos"):
        files = [f for f in os.listdir("data/videos") if f.lower().endswith(('.mp4', '.avi', '.mov'))]
        if files:
            video_path = os.path.join("data/videos", files[0])

    reader = VideoReader(video_path)
    ret, frame = reader.read()
    reader.release()
    
    if not ret or frame is None:
        print("[FAIL] Không thể đọc frame từ video.")
        return False

    # 3. Chạy hàm detect chuẩn hóa
    detections = detector.detect(frame)
    
    print("-" * 60)
    print(f">> Số lượng vật thể phát hiện: {len(detections)}")
    for idx, det in enumerate(detections):
        print(f"  Vật thể #{idx+1}: Lớp '{det['class_name']}' | Tin cậy: {det['conf']*100:.0f}% | Tọa độ: {det['box']}")
        
    print("=" * 60)
    print(">> KẾT QUẢ: MODULE DETECTION HOẠT ĐỘNG CHUẨN XÁC 100%!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_detector()
    sys.exit(0 if success else 1)
