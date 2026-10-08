"""
Module hỗ trợ vẽ các thành phần đồ họa (Visualizer)
"""
import cv2
import numpy as np

def draw_fps_badge(frame, fps_value: float, video_fps: float = None):
    text = f"FPS: {fps_value:.1f}"
    if video_fps:
        text += f" | Native: {video_fps:.1f}"
        
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), _ = cv2.getTextSize(text, font, 0.6, 2)
    cv2.rectangle(frame, (10, 10), (10 + tw + 10, 10 + th + 10), (30, 30, 30), -1)
    cv2.rectangle(frame, (10, 10), (10 + tw + 10, 10 + th + 10), (0, 255, 0), 1)
    cv2.putText(frame, text, (15, 10 + th + 3), font, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

def draw_detection(frame, box, label, is_violation=False, track_id=None, status=None):
    x1, y1, x2, y2 = box
    
    # Xác định màu sắc theo 3 cấp độ: ĐỎ (Confirmed) | VÀNG CAM (Suspected) | XANH (Normal)
    if status == "CONFIRMED" or (status is None and is_violation):
        color = (0, 0, 255)       # Đỏ: Đã xác nhận vi phạm
    elif status == "SUSPECTED":
        color = (0, 165, 255)     # Vàng cam: Đang nghi vấn (chờ đủ N frames)
    else:
        color = (0, 255, 0)       # Xanh lá: Hợp lệ / Bình thường
    
    # Ghép ID vào nhãn nếu có
    display_text = f"ID:{track_id} | {label}" if (track_id is not None and track_id > 0) else label
    
    # 1. Bounding box
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    
    # 2. Tag nhãn
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), _ = cv2.getTextSize(display_text, font, 0.5, 1)
    tag_top = max(0, y1 - th - 8)
    cv2.rectangle(frame, (x1, tag_top), (x1 + tw + 10, y1), color, -1)
    cv2.putText(frame, display_text, (x1 + 5, y1 - 4), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    
    # 3. Ba điểm chân tiếp đất (Chân trái, Giữa, Chân phải)
    pt_left = (int(x1), int(y2))
    pt_center = (int((x1 + x2) / 2), int(y2))
    pt_right = (int(x2), int(y2))
    
    # Thanh ngang chân đế
    cv2.line(frame, pt_left, pt_right, (0, 255, 255), 2, cv2.LINE_AA)
    
    # Vẽ 3 chấm tròn vàng viền đen đánh dấu 3 chân tiếp xúc
    for pt in [pt_left, pt_center, pt_right]:
        cv2.circle(frame, pt, 5, (0, 255, 255), -1)
        cv2.circle(frame, pt, 5, (0, 0, 0), 1)


