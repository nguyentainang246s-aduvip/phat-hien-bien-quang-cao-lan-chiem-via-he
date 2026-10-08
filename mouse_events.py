"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Computer Vision & Fixed Camera Surveillance
TASK: 05 - Bắt sự kiện chuột (Mouse Callback) để lấy tọa độ điểm trên Frame
==============================================================================
"""

import os
import sys
import cv2

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Danh sách toàn cục lưu trữ các điểm mà người dùng đã click: [(x1, y1), (x2, y2), ...]
clicked_points = []


def mouse_callback(event, x, y, flags, param):
    """
    Hàm Callback được OpenCV tự động kích hoạt mỗi khi có tương tác chuột.
    
    Tham số:
        event: Loại sự kiện (Click trái, click phải, di chuột...)
        x, y: Tọa độ pixel chính xác của con trỏ chuột trên bức ảnh
        flags: Các cờ trạng thái phím bổ trợ (Ctrl, Shift...)
        param: Dữ liệu tùy chọn truyền từ ngoài vào
    """
    global clicked_points
    
    # 1. SỰ KIỆN CLICK CHUỘT TRÁI (cv2.EVENT_LBUTTONDOWN): Thêm điểm mới
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_points.append((x, y))
        print(f"[CLICK TRÁI] Đã chọn điểm #{len(clicked_points)}: Tọa độ (X={x}, Y={y})")
        
    # 2. SỰ KIỆN CLICK CHUỘT PHẢI (cv2.EVENT_RBUTTONDOWN): Xóa điểm gần nhất (Undo)
    elif event == cv2.EVENT_RBUTTONDOWN:
        if clicked_points:
            removed = clicked_points.pop()
            print(f"[CLICK PHẢI] Đã xóa điểm vừa chọn: (X={removed[0]}, Y={removed[1]}). Còn lại: {len(clicked_points)} điểm.")
        else:
            print("[THÔNG BÁO] Danh sách điểm đang trống, không có gì để xóa.")


def run_mouse_demo():
    # Tìm video trong thư mục data/videos/
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

    window_name = "CCTV Mouse Event - Click chuot de chon toa do"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, min(width, 720), min(height, 720))

    # ĐĂNG KÝ HÀM CALLBACK CHO CỬA SỔ
    # Dòng này nói với OpenCV: "Khi có thao tác chuột trên cửa sổ window_name, hãy gọi hàm mouse_callback"
    cv2.setMouseCallback(window_name, mouse_callback)

    print("=" * 65)
    print("BẮT ĐẦU DEMO TASK 05: BẮT TỌA ĐỘ CHUỘT TRÊN VIDEO")
    print("=" * 65)
    print("HƯỚNG DẪN TƯƠNG TÁC:")
    print(" - Click CHUỘT TRÁI : Chọn một điểm trên màn hình (vẽ chấm đỏ)")
    print(" - Click CHUỘT PHẢI: Xóa điểm vừa chọn (Undo)")
    print(" - Phím 'c'         : Xóa toàn bộ điểm (Clear all)")
    print(" - Phím 'q' hoặc ESC: Thoát chương trình")
    print("-" * 65)

    try:
        while True:
            ret, frame = cap.read()
            # Nếu hết video thì tua lại từ đầu để người dùng tiếp tục click test
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # Vẽ các điểm đã click lên frame hiện tại
            for idx, (px, py) in enumerate(clicked_points):
                # Vẽ chấm tròn đỏ rực tâm (px, py)
                cv2.circle(frame, (px, py), 6, (0, 0, 255), -1)
                # Viền trắng bên ngoài
                cv2.circle(frame, (px, py), 6, (255, 255, 255), 2)
                # In số thứ tự và tọa độ bên cạnh điểm
                coord_text = f"P{idx+1}({px},{py})"
                cv2.putText(frame, coord_text, (px + 10, py - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)

            # Nối các điểm lại với nhau bằng đường kẻ nếu có từ 2 điểm trở lên (bước chuẩn bị cho Polygon vỉa hè)
            if len(clicked_points) >= 2:
                for i in range(len(clicked_points) - 1):
                    cv2.line(frame, clicked_points[i], clicked_points[i + 1], (0, 255, 0), 2)

            cv2.imshow(window_name, frame)
            key = cv2.waitKey(delay_ms) & 0xFF

            # Phím 'c': Xóa sạch danh sách điểm
            if key == ord('c') or key == ord('C'):
                clicked_points.clear()
                print("[THÔNG BÁO] Đã xóa toàn bộ điểm.")
            elif key == ord('q') or key == 27:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("-" * 65)
        print("TỔNG KẾT TỌA ĐỘ CÁC ĐIỂM ĐÃ CHỌN:")
        for idx, pt in enumerate(clicked_points):
            print(f"  Điểm #{idx+1}: {pt}")
        print("[OK] Đã giải phóng tài nguyên an toàn.")
        print("=" * 65)

    return True


if __name__ == "__main__":
    run_mouse_demo()
