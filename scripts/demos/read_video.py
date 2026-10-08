import os
import sys
# Tự động trỏ về thư mục gốc của đồ án
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Computer Vision & Fixed Camera Surveillance
TASK: 02 - Đọc và hiển thị luồng Video cơ bản bằng OpenCV (cv2.VideoCapture)
==============================================================================
"""

# Thư viện hệ thống dùng để kiểm tra tệp tin và nhận tham số dòng lệnh
import os
import sys

# Thư viện Thị giác máy tính OpenCV (Open Source Computer Vision Library)
import cv2

# Cấu hình UTF-8 cho console Windows để in tiếng Việt có dấu không bị lỗi font/crash
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def play_video(video_path: str, display: bool = True, max_frames: int = None) -> bool:
    """
    Hàm đọc và phát video từ đường dẫn cho trước.
    
    Tham số (Arguments):
        video_path (str): Đường dẫn đến tệp video (.mp4, .avi, ...).
        display (bool): True nếu muốn mở cửa sổ đồ họa hiển thị video, 
                        False nếu chạy ngầm (dùng cho test tự động).
        max_frames (int, optional): Giới hạn số frame tối đa cần đọc (dùng để test nhanh).
        
    Trả về (Returns):
        bool: True nếu đọc video thành công không có lỗi, False nếu có sự cố.
    """
    print("=" * 60)
    print("BẮT ĐẦU ĐỌC VIDEO VỚI OPENCV (TASK 02)")
    print("=" * 60)
    
    # -------------------------------------------------------------------------
    # BƯỚC 1: KIỂM TRA SỰ TỒN TẠI CỦA FILE VIDEO
    # -------------------------------------------------------------------------
    # Trước khi nạp vào OpenCV, luôn kiểm tra xem file có thực sự tồn tại trên ổ cứng không.
    # Tránh trường hợp người dùng gõ sai tên file hoặc sai đường dẫn.
    if not os.path.exists(video_path):
        print(f"[LỖI] File video không tồn tại: '{video_path}'")
        print("Vui lòng kiểm tra lại đường dẫn tệp tin.")
        return False
        
    # -------------------------------------------------------------------------
    # BƯỚC 2: KHỞI TẠO ĐỐI TƯỢNG BẮT HÌNH (cv2.VideoCapture)
    # -------------------------------------------------------------------------
    # cv2.VideoCapture đóng vai trò như một "đầu đọc đĩa/máy phát" kết nối tới video.
    cap = cv2.VideoCapture(video_path)
    
    # -------------------------------------------------------------------------
    # BƯỚC 3: KIỂM TRA ĐẦU ĐỌC CÓ MỞ THÀNH CÔNG KHÔNG
    # -------------------------------------------------------------------------
    # cap.isOpened() trả về True nếu OpenCV giải mã và kết nối được với file video.
    # Nếu file hỏng, thiếu codec (bộ giải mã MP4) hoặc file rỗng -> isOpened() trả về False.
    if not cap.isOpened():
        print(f"[LỖI] OpenCV không thể giải mã video: '{video_path}'")
        print("Nguyên nhân: File bị hỏng, thiếu codec phần cứng hoặc định dạng không hỗ trợ.")
        return False
        
    # -------------------------------------------------------------------------
    # BƯỚC 4: ĐỌC VÀ TRÍCH XUẤT CÁC THÔNG SỐ KỸ THUẬT (METADATA)
    # -------------------------------------------------------------------------
    # Hàm cap.get() đọc các thông tin phần cứng/thuộc tính của video:
    # - CAP_PROP_FRAME_WIDTH : Chiều rộng khung hình (đơn vị: pixels).
    # - CAP_PROP_FRAME_HEIGHT: Chiều cao khung hình (đơn vị: pixels).
    # - CAP_PROP_FPS         : Tốc độ ghi hình (Frames Per Second - số khung hình/giây).
    # - CAP_PROP_FRAME_COUNT : Tổng số khung hình (bức ảnh tĩnh) cấu thành nên video.
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"[+] Đường dẫn video : {video_path}")
    print(f"[+] Độ phân giải    : {width} x {height} (Pixels)")
    print(f"[+] FPS gốc         : {fps:.2f} frames/giây")
    print(f"[+] Tổng số frames  : {total_frames} frames")
    if fps > 0:
        duration_sec = total_frames / fps
        print(f"[+] Thời lượng video: {duration_sec:.1f} giây")
    print("-" * 60)
    print("Đang phát video... Nhấn phím 'q' hoặc 'ESC' trên cửa sổ video để dừng.")
    
    # Tính khoảng thời gian nghỉ giữa 2 frame (tính bằng mili-giây).
    # Ví dụ: 30 FPS -> Mỗi frame cách nhau: 1000ms / 30 = ~33 mili-giây.
    # Điều này giúp video phát tự nhiên, đúng với tốc độ thời gian thực ngoài đời.
    delay_ms = int(1000 / fps) if (fps and fps > 0) else 33
    
    # Biến đếm số lượng frame đã đọc thực tế
    frame_count = 0
    
    # Tên định danh của cửa sổ hiển thị.
    # LƯU Ý SỐNG CÒN: Tên cửa sổ PHẢI CỐ ĐỊNH và khởi tạo NGOÀI vòng lặp.
    # Nếu tên cửa sổ thay đổi theo frame, OpenCV sẽ mở hàng trăm cửa sổ mới.
    window_title = "CCTV Video Reader - Nhan 'q' de thoat"
    if display:
        # cv2.WINDOW_NORMAL cho phép người dùng dùng chuột kéo to/nhỏ cửa sổ
        cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
        # Giới hạn kích thước hiển thị ban đầu (tối đa 720x720) để tránh tràn màn hình máy tính
        cv2.resizeWindow(window_title, min(width, 720), min(height, 720))
    
    # -------------------------------------------------------------------------
    # BƯỚC 5: VÒNG LẶP ĐỌC VÀ HIỂN THỊ TỪNG KHUNG HÌNH (FRAME)
    # -------------------------------------------------------------------------
    try:
        while True:
            # cap.read() rút 1 bức ảnh tiếp theo từ luồng video.
            # Trả về 2 giá trị:
            # - ret (boolean): True nếu đọc thành công, False nếu hết video hoặc lỗi đọc.
            # - frame (ndarray): Ma trận điểm ảnh đa chiều kích thước (Height, Width, 3).
            ret, frame = cap.read()
            
            # Nếu ret == False nghĩa là video đã phát tới khung hình cuối cùng
            if not ret:
                print(f"[KẾT THÚC] Đã đọc xong toàn bộ video ({frame_count} frames).")
                break
                
            frame_count += 1
            
            # -----------------------------------------------------------------
            # BƯỚC 6: HIỂN THỊ ẢNH VÀ XỬ LÝ PHÍM ĐIỀU KHIỂN
            # -----------------------------------------------------------------
            if display:
                # Vẽ bức ảnh 'frame' hiện tại lên cửa sổ có tên 'window_title'
                cv2.imshow(window_title, frame)
                
                # cv2.waitKey(delay_ms): Tạm dừng chương trình trong delay_ms mili-giây.
                # Mục đích:
                # 1. Cho phép Windows vẽ bức ảnh lên màn hình.
                # 2. Lắng nghe xem người dùng có gõ phím nào trên bàn phím không.
                # & 0xFF: Phép toán lấy 8-bit cuối để nhận diện mã ASCII chính xác.
                key = cv2.waitKey(delay_ms) & 0xFF
                
                # ord('q'): Mã số ASCII của chữ cái 'q'.
                # 27: Mã số ASCII của phím ESC (Escape).
                # Nếu người dùng nhấn 'q' hoặc 'ESC' -> Dừng vòng lặp ngay lập tức.
                if key == ord('q') or key == 27:
                    print(f"[THÔNG BÁO] Người dùng nhấn phím dừng tại frame {frame_count}.")
                    break
                    
            # Giới hạn số frame phục vụ cho kiểm thử tự động
            if max_frames and frame_count >= max_frames:
                print(f"[THÔNG BÁO] Đã đạt giới hạn test {max_frames} frames.")
                break
                
    except Exception as e:
        # Bắt các lỗi ngoại lệ phát sinh trong quá trình đọc
        print(f"[LỖI NGOẠI LỆ] Xảy ra sự cố khi xử lý video: {e}")
        return False
        
    finally:
        # ---------------------------------------------------------------------
        # BƯỚC 7: GIẢI PHÓNG TÀI NGUYÊN BỘ NHỚ (CỰC KỲ QUAN TRỌNG)
        # ---------------------------------------------------------------------
        # Khối 'finally:' luôn luôn chạy dù chương trình thoát bình thường hay bị lỗi.
        # - cap.release(): Ngắt kết nối tệp tin / camera, giải phóng RAM.
        # - cv2.destroyAllWindows(): Đóng toàn bộ cửa sổ đồ họa của OpenCV.
        cap.release()
        if display:
            cv2.destroyAllWindows()
        print(f"[OK] Đã giải phóng bộ nhớ camera và đóng cửa sổ an toàn.")
        print("=" * 60)
        
    return True


def find_default_video() -> str:
    """
    Hàm phụ trợ: Tự động quét thư mục data/videos/ để tìm file video hợp lệ.
    Giúp người dùng không phải gõ tên file thủ công khi chạy lệnh.
    """
    video_dir = "data/videos"
    if os.path.exists(video_dir):
        # Lọc các file có đuôi mở rộng là video phổ biến
        files = [f for f in os.listdir(video_dir) if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]
        if files:
            return os.path.join(video_dir, files[0])
            
    # Nếu không tìm thấy file nào trong thư mục, trả về đường dẫn mẫu mặc định
    return os.path.join(video_dir, "sample_cctv.mp4")


# Điểm khởi chạy chương trình (Main Entry Point)
if __name__ == "__main__":
    # Nếu người dùng truyền đường dẫn từ dòng lệnh: python read_video.py "duong_dan.mp4"
    # -> Sử dụng sys.argv[1].
    # Nếu không truyền gì -> Tự động tìm video trong thư mục data/videos/.
    target_video = sys.argv[1] if len(sys.argv) > 1 else find_default_video()
    
    # Thực thi hàm phát video
    success = play_video(target_video)
    
    # Thoát với mã code chuẩn: 0 là thành công, 1 là thất bại
    sys.exit(0 if success else 1)
