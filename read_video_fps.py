"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Computer Vision & Fixed Camera Surveillance
TASK: 03 - Đo và Hiển thị FPS xử lý thực tế lên Video (Checkpoint v0.2)
==============================================================================
"""

import os
import sys
import time
import cv2

# Cấu hình UTF-8 cho console Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class FPSTracker:
    """
    Bộ đếm và tính toán FPS (Frames Per Second) xử lý thực tế.
    Áp dụng thuật toán làm mượt hàm mũ (Exponential Moving Average - EMA)
    để số FPS hiển thị ổn định, không bị giật/nhấp nháy liên tục.
    """
    def __init__(self, alpha: float = 0.1):
        """
        Khởi tạo bộ theo dõi FPS.
        
        Args:
            alpha (float): Hệ số làm mượt (0 < alpha <= 1.0).
                           Càng nhỏ thì số FPS hiển thị càng êm/ổn định.
        """
        self.alpha = alpha
        self.prev_time = None
        self.smoothed_fps = 0.0
        self.frame_count = 0

    def update(self) -> float:
        """
        Cập nhật thời gian sau khi xử lý xong 1 frame và tính toán FPS.
        
        Returns:
            float: Giá trị FPS thực tế đã được làm mượt.
        """
        curr_time = time.perf_counter()
        self.frame_count += 1
        
        # Ở frame đầu tiên chưa có mốc thời gian trước đó để so sánh
        if self.prev_time is None:
            self.prev_time = curr_time
            return 0.0
            
        # delta_t: Khoảng thời gian tính bằng giây để hoàn thành 1 frame
        delta_t = curr_time - self.prev_time
        self.prev_time = curr_time
        
        if delta_t > 0:
            instant_fps = 1.0 / delta_t
            if self.smoothed_fps == 0.0:
                self.smoothed_fps = instant_fps
            else:
                # Công thức làm mượt EMA: FPS_mới = alpha * tức_thời + (1 - alpha) * FPS_cũ
                self.smoothed_fps = self.alpha * instant_fps + (1.0 - self.alpha) * self.smoothed_fps
                
        return self.smoothed_fps


def draw_fps_badge(frame, fps_value: float, video_fps: float = None):
    """
    Vẽ khung thông tin FPS chuyên nghiệp lên góc trên cùng của khung hình.
    Có nền đen mờ phía sau để text luôn đọc được rõ ràng dù nền video sáng hay tối.
    """
    fps_text = f"Processing FPS: {fps_value:.1f}"
    if video_fps and video_fps > 0:
        fps_text += f" | Native: {video_fps:.1f}"

    # Tọa độ và kích thước badge
    x, y = 15, 15
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.65
    font_thickness = 2
    
    # Đo kích thước chuỗi text để vẽ khung nền chữ nhật vừa vặn
    (text_w, text_h), baseline = cv2.getTextSize(fps_text, font, font_scale, font_thickness)
    
    # 1. Vẽ hộp nền màu xám đen phía sau chữ
    cv2.rectangle(frame, (x - 8, y - 5), (x + text_w + 12, y + text_h + 12), (30, 30, 30), -1)
    # Vẽ viền ngoài cho hộp
    cv2.rectangle(frame, (x - 8, y - 5), (x + text_w + 12, y + text_h + 12), (0, 255, 0), 1)

    # 2. Vẽ chữ FPS màu xanh lá dạ quang (Neon Green)
    # Tọa độ text trong OpenCV được tính từ góc dưới-trái của dòng chữ
    cv2.putText(frame, fps_text, (x, y + text_h + 2), font, font_scale, (0, 255, 0), font_thickness, cv2.LINE_AA)


def play_video_with_fps(video_path: str, display: bool = True, max_frames: int = None) -> bool:
    """
    Phát video và hiển thị thông số FPS xử lý thực tế lên khung hình.
    """
    print("=" * 60)
    print("BẮT ĐẦU PHÁT VIDEO KÈM ĐO ĐẠC FPS (TASK 03)")
    print("=" * 60)
    
    if not os.path.exists(video_path):
        print(f"[LỖI] File video không tồn tại: '{video_path}'")
        return False
        
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[LỖI] OpenCV không thể mở video: '{video_path}'")
        return False
        
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    native_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"[+] Tệp tin video  : {video_path}")
    print(f"[+] Độ phân giải   : {width} x {height}")
    print(f"[+] FPS gốc camera : {native_fps:.2f} FPS")
    print(f"[+] Tổng số frames : {total_frames}")
    print("-" * 60)
    print("Đang chạy... Nhấn phím 'q' hoặc 'ESC' trên cửa sổ để dừng.")

    # Khởi tạo bộ đo FPS
    fps_tracker = FPSTracker(alpha=0.15)
    
    # Độ trễ cơ bản (1ms để OpenCV kịp vẽ giao diện mà không kìm hãm tốc độ đo)
    # Nếu muốn xem tốc độ tối đa máy tính xử lý được -> để delay = 1ms
    delay_ms = 1
    
    window_title = "CCTV Stream with FPS Overlay - Nhan 'q' de thoat"
    if display:
        cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_title, min(width, 720), min(height, 720))
        
    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"[KẾT THÚC] Đã phát hết video ({frame_count} frames).")
                break
                
            frame_count += 1
            
            # Cập nhật và tính toán FPS thực tế
            current_fps = fps_tracker.update()
            
            # Vẽ thông số FPS trực tiếp lên góc trên khung hình
            draw_fps_badge(frame, current_fps, native_fps)
            
            if display:
                cv2.imshow(window_title, frame)
                key = cv2.waitKey(delay_ms) & 0xFF
                if key == ord('q') or key == 27:
                    print(f"[THÔNG BÁO] Người dùng nhấn phím dừng tại frame {frame_count}.")
                    break
                    
            if max_frames and frame_count >= max_frames:
                print(f"[THÔNG BÁO] Đã đạt giới hạn test {max_frames} frames.")
                break
                
    except Exception as e:
        print(f"[LỖI NGOẠI LỆ] {e}")
        return False
        
    finally:
        cap.release()
        if display:
            cv2.destroyAllWindows()
        print(f"[OK] Đã giải phóng tài nguyên an toàn. FPS trung bình: {fps_tracker.smoothed_fps:.1f}")
        print("=" * 60)
        
    return True


def find_default_video() -> str:
    """Tìm video trong thư mục data/videos/"""
    video_dir = "data/videos"
    if os.path.exists(video_dir):
        files = [f for f in os.listdir(video_dir) if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]
        if files:
            return os.path.join(video_dir, files[0])
    return os.path.join(video_dir, "sample_cctv.mp4")


if __name__ == "__main__":
    target_video = sys.argv[1] if len(sys.argv) > 1 else find_default_video()
    success = play_video_with_fps(target_video)
    sys.exit(0 if success else 1)
