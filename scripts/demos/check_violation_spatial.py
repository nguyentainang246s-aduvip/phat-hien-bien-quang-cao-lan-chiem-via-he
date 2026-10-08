import os
import sys
# Tự động trỏ về thư mục gốc của đồ án
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Computer Vision & Spatial Geometry
TASK: 07 - Đọc JSON & Thuật toán kiểm tra Điểm nằm trong Vỉa hè (Point-in-Polygon)
==============================================================================
"""

import os
import sys
import json
import cv2
import numpy as np
import shapely.geometry as sg

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

CONFIG_FILE = "configs/roi_camera1.json"
current_mouse_pos = None


def load_roi_polygon(config_path=CONFIG_FILE):
    """Đọc file cấu hình JSON và trả về danh sách các đỉnh của đa giác."""
    if not os.path.exists(config_path):
        print(f"[LỖI] Không tìm thấy file cấu hình: {config_path}")
        return None
        
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    points = data.get("polygon_points", [])
    print(f"[OK] Đã nạp vùng vỉa hè của {data.get('camera_id')}: {len(points)} đỉnh.")
    return points


def mouse_hover_callback(event, x, y, flags, param):
    """Bắt tọa độ chuột khi người dùng di chuột trên màn hình để kiểm tra thời gian thực."""
    global current_mouse_pos
    if event == cv2.EVENT_MOUSEMOVE or event == cv2.EVENT_LBUTTONDOWN:
        current_mouse_pos = (x, y)


def is_point_in_sidewalk(point, polygon_pts):
    """
    DÒNG CỐT LÕI 1: Kiểm tra 1 điểm (x, y) có nằm trong đa giác vỉa hè hay không.
    Sử dụng thuật toán kinh điển cv2.pointPolygonTest.
    
    Returns:
        bool: True nếu điểm nằm TRONG hoặc TRÊN mép vỉa hè, False nếu nằm NGOÀI.
    """
    pts_array = np.array(polygon_pts, dtype=np.int32)
    # measureDist=False: Chỉ kiểm tra vị trí tương đối (>0: Trong, =0: Trên cạnh, <0: Ngoài)
    res = cv2.pointPolygonTest(pts_array, point, measureDist=False)
    return res >= 0


def calculate_overlap_ratio(box, polygon_pts):
    """
    DÒNG CỐT LÕI 2: Tính tỷ lệ % diện tích Bounding Box lấn vào vùng vỉa hè (Shapely).
    
    Args:
        box: Tọa độ (x1, y1, x2, y2)
        polygon_pts: Danh sách các đỉnh của vỉa hè
        
    Returns:
        float: Tỷ lệ giao nhau (từ 0.0 đến 1.0 tương đương 0% đến 100%)
    """
    x1, y1, x2, y2 = box
    box_poly = sg.box(x1, y1, x2, y2)
    sidewalk_poly = sg.Polygon(polygon_pts)
    
    if not sidewalk_poly.is_valid:
        sidewalk_poly = sidewalk_poly.buffer(0)
        
    # Tính phần diện tích giao nhau
    intersection = sidewalk_poly.intersection(box_poly)
    if box_poly.area <= 0:
        return 0.0
        
    overlap_ratio = intersection.area / box_poly.area
    return overlap_ratio


def run_spatial_demo():
    points = load_roi_polygon()
    if not points or len(points) < 3:
        print("[LỖI] Cần tối thiểu 3 đỉnh để tạo thành vùng vỉa hè.")
        return False

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

    window_name = "TASK 07 - Point-in-Polygon & Spatial Logic (Di chuot de test)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, min(width, 720), min(height, 720))
    cv2.setMouseCallback(window_name, mouse_hover_callback)

    pts_arr = np.array(points, np.int32).reshape((-1, 1, 2))

    print("=" * 65)
    print("BẮT ĐẦU DEMO TASK 07: THUẬT TOÁN HÌNH HỌC KHÔNG GIAN")
    print("=" * 65)
    print("HƯỚNG DẪN:")
    print(" - Hãy DI CHUỘT vào trong và ra ngoài vùng vỉa hè để xem kết quả kiểm tra.")
    print(" - Nhấn phím 'q' hoặc ESC để thoát.")
    print("-" * 65)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # 1. Vẽ lớp phủ vỉa hè bán trong suốt (Màu xanh lơ)
            overlay = frame.copy()
            cv2.fillPoly(overlay, [pts_arr], (255, 200, 0))
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            cv2.polylines(frame, [pts_arr], isClosed=True, color=(0, 255, 255), thickness=2)
            cv2.putText(frame, "VUNG VIA HE (ROI)", (points[0][0], points[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # 2. Kiểm tra vị trí con trỏ chuột theo thời gian thực (Point-in-Polygon)
            if current_mouse_pos:
                mx, my = current_mouse_pos
                in_sidewalk = is_point_in_sidewalk((mx, my), points)
                
                status_color = (0, 0, 255) if in_sidewalk else (0, 255, 0)
                status_text = "VI PHAM (Nam tren via he)" if in_sidewalk else "HOP LE (Ngoai via he)"
                
                # Vẽ vòng tròn tại vị trí con trỏ chuột
                cv2.circle(frame, (mx, my), 8, status_color, -1)
                cv2.circle(frame, (mx, my), 9, (255, 255, 255), 2)
                cv2.putText(frame, f"{status_text} | Pos: ({mx},{my})", (mx + 15, my),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 2, cv2.LINE_AA)

            # 3. Mô phỏng 1 Bounding Box biển hiệu để tính tỷ lệ lấn chiếm % (Shapely)
            sim_box = (int(width * 0.15), int(height * 0.58), int(width * 0.45), int(height * 0.72))
            ratio = calculate_overlap_ratio(sim_box, points)
            box_color = (0, 0, 255) if ratio >= 0.3 else (0, 255, 0)
            
            cv2.rectangle(frame, (sim_box[0], sim_box[1]), (sim_box[2], sim_box[3]), box_color, 2)
            cv2.putText(frame, f"Bien quang cao | Lan chiem: {ratio*100:.1f}%", 
                        (sim_box[0], sim_box[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)

            cv2.imshow(window_name, frame)
            key = cv2.waitKey(delay_ms) & 0xFF
            if key == ord('q') or key == 27:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[OK] Đã hoàn thành demo Task 07 an toàn.")

    return True


if __name__ == "__main__":
    run_spatial_demo()
