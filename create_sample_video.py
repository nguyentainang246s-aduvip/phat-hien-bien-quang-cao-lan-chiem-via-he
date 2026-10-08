"""
Script tạo video mẫu mô phỏng góc nhìn CCTV vỉa hè
Phục vụ kiểm thử cho các task đầu tiên khi chưa có video thực tế
"""
import os
import sys
import cv2
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def create_sample_cctv_video(output_path="data/videos/sample_cctv.mp4", duration_sec=5, fps=25):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    width, height = 640, 360
    total_frames = duration_sec * fps
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for i in range(total_frames):
        # Tạo khung nền đường phố & vỉa hè
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Lòng đường (xám đậm)
        frame[180:, :] = (50, 50, 50)
        
        # Vạch kẻ đường
        for x in range(20, width, 80):
            frame[280:290, x:x+40] = (255, 255, 255)
            
        # Vỉa hè (xám nhạt)
        sidewalk_pts = np.array([[0, 140], [width, 140], [width, 210], [0, 210]], np.int32)
        cv2.fillPoly(frame, [sidewalk_pts], (120, 120, 120))
        
        # Bờ kè vỉa hè (ranh giới)
        cv2.line(frame, (0, 210), (width, 210), (200, 200, 200), 2)
        
        # Biển quảng cáo mô phỏng đặt trên vỉa hè
        # Tọa độ: x=240..320, y=130..195
        cv2.rectangle(frame, (240, 130), (320, 195), (0, 165, 255), -1) # Cam
        cv2.rectangle(frame, (240, 130), (320, 195), (255, 255, 255), 2)
        cv2.putText(frame, "BIEN HIEU", (245, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Thông tin camera giả lập
        cv2.putText(frame, f"CCTV 01 - CAM_VIA_HE | Frame: {i+1}/{total_frames}", (15, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        out.write(frame)
        
    out.release()
    print(f"[OK] Đã tạo video mẫu thành công: {output_path} ({total_frames} frames, {width}x{height}, {fps} FPS)")

if __name__ == "__main__":
    create_sample_cctv_video()
