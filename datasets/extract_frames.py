"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Dataset Engineering & Data Preparation
TASK: 11 - Trích xuất ảnh (Frame Extraction) định kỳ từ Video để gán nhãn
==============================================================================
"""

import os
import sys
import cv2

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def extract_frames_from_video(video_path: str, output_dir: str = "datasets/raw_images", interval_sec: float = 1.0):
    """
    Trích xuất các khung hình từ video theo chu kỳ thời gian định trước.
    
    Args:
        video_path (str): Đường dẫn tới video nguồn (.mp4, .avi, ...)
        output_dir (str): Thư mục lưu các bức ảnh được trích xuất
        interval_sec (float): Chu kỳ lấy mẫu tính bằng giây (vd: 1.0s lấy 1 ảnh)
        
    Returns:
        int: Số lượng ảnh đã trích xuất thành công
    """
    if not os.path.exists(video_path):
        print(f"[LỖI] Không tìm thấy file video: {video_path}")
        return 0
        
    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[LỖI] OpenCV không thể mở video: {video_path}")
        return 0
        
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    # Tính số lượng frame cần nhảy cóc giữa 2 lần chụp ảnh
    # Ví dụ: Video 30 FPS, interval = 1.0s -> step = 30 frame (mỗi 30 frame lấy 1 ảnh)
    frame_step = max(1, int(fps * interval_sec))
    
    print("=" * 65)
    print("BẮT ĐẦU TRÍCH XUẤT FRAME PHỤC VỤ TẠO DATASET (TASK 11)")
    print("=" * 65)
    print(f"[+] Video nguồn      : {video_path}")
    print(f"[+] FPS video        : {fps:.2f} FPS")
    print(f"[+] Tổng số frames   : {total_frames} frames")
    print(f"[+] Chu kỳ lấy mẫu   : {interval_sec} giây / 1 ảnh (nhảy cóc {frame_step} frames)")
    print(f"[+] Thư mục lưu ảnh  : {output_dir}")
    print("-" * 65)
    
    current_frame = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Chỉ lưu frame khi nó rơi vào đúng nhịp chu kỳ (chia hết cho frame_step)
        if current_frame % frame_step == 0:
            saved_count += 1
            # Tên file đánh số thứ tự chuẩn 4 chữ số: image_0001.jpg, image_0002.jpg,...
            image_filename = f"{video_name}_frame_{saved_count:04d}.jpg"
            save_path = os.path.join(output_dir, image_filename)
            
            # Lưu ảnh ra đĩa ở chất lượng cao nhất (JPEG quality = 95)
            cv2.imwrite(save_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            print(f"  -> Đã trích xuất #{saved_count:03d} (tại giây thứ {current_frame/fps:5.1f}s): {image_filename}")
            
        current_frame += 1
        
    cap.release()
    print("=" * 65)
    print(f"[HOÀN THÀNH] Đã trích xuất thành công: {saved_count} ảnh chất lượng cao!")
    print(f">> Các ảnh đã sẵn sàng trong thư mục: '{output_dir}'")
    print(">> Bạn có thể nén zip thư mục này và tải lên Roboflow để bắt đầu gán nhãn.")
    print("=" * 65)
    return saved_count


def run():
    video_dir = "data/videos"
    video_path = "data/videos/sample_cctv.mp4"
    
    if os.path.exists(video_dir):
        files = [f for f in os.listdir(video_dir) if f.lower().endswith(('.mp4', '.avi', '.mov'))]
        if files:
            video_path = os.path.join(video_dir, files[0])
            
    # Mặc định lấy mỗi 1 giây 1 bức ảnh (interval_sec=1.0)
    extract_frames_from_video(video_path=video_path, output_dir="datasets/raw_images", interval_sec=1.0)


if __name__ == "__main__":
    run()
