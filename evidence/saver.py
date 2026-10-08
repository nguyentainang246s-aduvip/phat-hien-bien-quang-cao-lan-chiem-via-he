"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Evidence Management & Law Enforcement Proof
TASK: 23 - Xây dựng Module evidence/saver.py (Lưu trữ ảnh bằng chứng vi phạm)
==============================================================================
"""

import os
import time
import datetime
import cv2
import numpy as np


class EvidenceSaver:
    """
    Quản lý lưu trữ bằng chứng hình ảnh khi phát hiện vi phạm lấn chiếm vỉa hè.
    Tự động phân loại thư mục theo Camera và Ngày (YYYY-MM-DD).
    Lưu 2 cấp độ bằng chứng phục vụ phạt nguội:
      1. Ảnh Toàn Cảnh (Full Frame): Có đóng dấu thời gian, mã camera, tọa độ vỉa hè làm căn cứ pháp lý.
      2. Ảnh Cận Cảnh (Cropped Image): Phóng to riêng tấm biển hiệu để đọc rõ nội dung chữ và SĐT.
    """
    def __init__(self, base_dir: str = "evidence"):
        """
        Args:
            base_dir: Thư mục gốc lưu trữ bằng chứng (mặc định 'evidence')
        """
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_evidence(self, frame: np.ndarray, box: tuple, track_id: int, 
                      camera_id: str = "cam_01", overlap_pct: float = 0.0) -> dict:
        """
        Lưu cặp ảnh bằng chứng (toàn cảnh + cận cảnh).
        
        Args:
            frame: Khung hình camera tại thời điểm vi phạm (đã vẽ ROI và Bounding Box)
            box: Tọa độ bounding box của biển hiệu (x1, y1, x2, y2)
            track_id: Mã định danh đối tượng (ID: 1, 2, ...)
            camera_id: Mã nhận diện camera CCTV
            overlap_pct: Tỷ lệ diện tích lấn chiếm (%)
            
        Returns:
            dict: Đường dẫn lưu trữ và metadata:
                  {
                      "full_path": str,
                      "crop_path": str,
                      "timestamp": str,
                      "camera_id": str,
                      "track_id": int
                  }
        """
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M-%S-%f")  # Bao gồm microsecond để tránh trùng file
        iso_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        # 1. Tạo cấu trúc thư mục lưu trữ theo ngày và camera
        camera_clean_id = camera_id.replace(" ", "_").replace("(", "").replace(")", "")
        full_dir = os.path.join(self.base_dir, "records", camera_clean_id, date_str)
        crop_dir = os.path.join(self.base_dir, "crops", camera_clean_id, date_str)
        os.makedirs(full_dir, exist_ok=True)
        os.makedirs(crop_dir, exist_ok=True)

        # 2. Xử lý ảnh toàn cảnh (Full Frame with Watermark Stamp)
        stamped_frame = frame.copy()
        h, w = stamped_frame.shape[:2]

        # Đóng dấu tem pháp lý (Legal Stamp) ở góc dưới khung hình
        stamp_text = f"BANG CHUNG CCTV | Cam: {camera_id} | ID: #{track_id} | Lan chiem: {overlap_pct:.1f}% | {iso_timestamp}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        (tw, th), _ = cv2.getTextSize(stamp_text, font, 0.55, 1)
        cv2.rectangle(stamped_frame, (10, h - th - 20), (20 + tw, h - 5), (0, 0, 0), -1)
        cv2.putText(stamped_frame, stamp_text, (15, h - 10), font, 0.55, (0, 255, 255), 1, cv2.LINE_AA)

        full_filename = f"violation_id{track_id}_{time_str}.jpg"
        full_path = os.path.join(full_dir, full_filename)
        cv2.imwrite(full_path, stamped_frame)

        # 3. Xử lý ảnh cận cảnh (Cropped Target Sign)
        x1, y1, x2, y2 = box
        # Đảm bảo không vượt quá biên ảnh
        x1_clamped = max(0, x1)
        y1_clamped = max(0, y1)
        x2_clamped = min(w, x2)
        y2_clamped = min(h, y2)

        cropped_img = frame[y1_clamped:y2_clamped, x1_clamped:x2_clamped]
        crop_filename = f"crop_id{track_id}_{time_str}.jpg"
        crop_path = os.path.join(crop_dir, crop_filename)

        if cropped_img.size > 0:
            cv2.imwrite(crop_path, cropped_img)
        else:
            crop_path = ""

        return {
            "full_path": full_path.replace("\\", "/"),
            "crop_path": crop_path.replace("\\", "/"),
            "timestamp": iso_timestamp,
            "camera_id": camera_id,
            "track_id": track_id,
            "overlap_pct": overlap_pct
        }
