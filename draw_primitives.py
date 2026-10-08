"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
TASK: 04 - Vẽ Bounding Box, Nhãn Vi Phạm và Điểm Chân Biển Hiệu (Primitives)
==============================================================================
"""

import os
import sys
import time
import cv2

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def draw_bounding_box(frame, box, label, is_violation=True):
    """
    Vẽ khung chữ nhật (Bounding Box) có nhãn dán chuyên nghiệp trên nóc.
    
    Args:
        frame: Bức ảnh cần vẽ
        box: Tọa độ (x1, y1, x2, y2)
        label: Chữ hiển thị (vd: 'VI PHAM: 94%')
        is_violation: True -> Màu đỏ, False -> Màu xanh lá
    """
    x1, y1, x2, y2 = box
    
    # Màu sắc: Đỏ cảnh báo (BGR: 0, 0, 255) hoặc Xanh lá an toàn (BGR: 0, 255, 0)
    color = (0, 0, 255) if is_violation else (0, 255, 0)
    
    # 1. DÒNG CỐT LÕI 1: Vẽ khung chữ nhật bọc quanh vật thể
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    
    # 2. DÒNG CỐT LÕI 2: Đo kích thước chữ và vẽ thẻ nhãn (Header Tag)
    (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    tag_top = max(0, y1 - th - 8)
    # Tô đặc miếng nền cho nhãn
    cv2.rectangle(frame, (x1, tag_top), (x1 + tw + 10, y1), color, -1)
    # Viết chữ trắng lên miếng nền đó
    cv2.putText(frame, label, (x1 + 5, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    
    # 3. DÒNG CỐT LÕI 3: Vẽ điểm chân đế tiếp xúc mặt đất (Điểm chính giữa đáy)
    base_x = int((x1 + x2) / 2)
    base_y = y2
    cv2.circle(frame, (base_x, base_y), 5, (0, 255, 255), -1)  # Chấm tròn vàng
    cv2.circle(frame, (base_x, base_y), 5, (0, 0, 0), 1)        # Viền đen cho rõ


def run_demo():
    # Tự động tìm video trong thư mục data/videos/
    video_path = "data/videos/sample_cctv.mp4"
    if os.path.exists("data/videos"):
        files = [f for f in os.listdir("data/videos") if f.lower().endswith(('.mp4', '.avi', '.mov'))]
        if files:
            video_path = os.path.join("data/videos", files[0])
            
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[LỖI] Không thể mở video: {video_path}")
        return False
        
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    delay_ms = int(1000 / fps)
    
    window_name = "CCTV Drawing Primitives - Nhan 'q' de thoat"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, min(width, 720), min(height, 720))
    
    print("=" * 60)
    print("BẮT ĐẦU CHẠY DEMO TASK 04: VẼ BOUNDING BOX & NHÃN VI PHẠM")
    print("=" * 60)
    print("Đang phát... Nhấn 'q' hoặc 'ESC' để dừng.")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Mô phỏng: Sau này YOLO sẽ tự sinh ra các tọa độ này
            # Hộp 1: Mô phỏng biển hiệu VI PHẠM (Màu đỏ)
            violation_box = (int(width * 0.2), int(height * 0.4), int(width * 0.5), int(height * 0.6))
            draw_bounding_box(frame, violation_box, "VI PHAM: BIEN LAN CHIEM (94%)", is_violation=True)
            
            # Hộp 2: Mô phỏng biển hiệu HỢP LỆ (Màu xanh lá)
            valid_box = (int(width * 0.6), int(height * 0.7), int(width * 0.85), int(height * 0.88))
            draw_bounding_box(frame, valid_box, "HOP LE (89%)", is_violation=False)
            
            cv2.imshow(window_name, frame)
            key = cv2.waitKey(delay_ms) & 0xFF
            if key == ord('q') or key == 27:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[OK] Đã hoàn thành demo Task 04 an toàn.")
        
    return True


if __name__ == "__main__":
    run_demo()
