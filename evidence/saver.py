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
    def __init__(self, base_dir: str = "evidence", blur_faces: bool = False):
        """
        Args:
            base_dir: Thư mục gốc lưu trữ bằng chứng (mặc định 'evidence')
            blur_faces: Bật/tắt tự động làm mờ khuôn mặt người đi đường (Privacy Protection)
        """
        self.base_dir = base_dir
        self.blur_faces = blur_faces
        self._face_cascade = None
        if self.blur_faces:
            try:
                cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                if os.path.exists(cascade_path):
                    self._face_cascade = cv2.CascadeClassifier(cascade_path)
            except Exception:
                pass
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

        h, w = frame.shape[:2]
        x1, y1, x2, y2 = [int(v) for v in box]
        x1_clamped, y1_clamped = max(0, x1), max(0, y1)
        x2_clamped, y2_clamped = min(w, x2), min(h, y2)

        # 1. Cắt ảnh cận cảnh (Cropped Target Sign) từ frame sạch trước khi vẽ đè
        cropped_img = frame[y1_clamped:y2_clamped, x1_clamped:x2_clamped].copy()
        crop_filename = f"crop_id{track_id}_{time_str}.jpg"
        crop_path = os.path.join(crop_dir, crop_filename)
        if cropped_img.size > 0:
            cv2.imwrite(crop_path, cropped_img)
        else:
            crop_path = ""

        # 2. Xử lý ảnh toàn cảnh (Full Frame with Target Highlight & Watermark Stamp)
        stamped_frame = frame.copy()

        # Làm mờ khuôn mặt người đi đường nếu bật privacy_blur_faces
        if self._face_cascade is not None:
            try:
                gray = cv2.cvtColor(stamped_frame, cv2.COLOR_BGR2GRAY)
                faces = self._face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=4, minSize=(30, 30))
                for (fx, fy, fw_box, fh_box) in faces:
                    is_inside_sign = (fx >= x1_clamped and fx + fw_box <= x2_clamped and fy >= y1_clamped and fy + fh_box <= y2_clamped)
                    if not is_inside_sign:
                        f_roi = stamped_frame[fy:fy+fh_box, fx:fx+fw_box]
                        if f_roi.size > 0:
                            k_w = max(15, (fw_box // 2) * 2 + 1)
                            k_h = max(15, (fh_box // 2) * 2 + 1)
                            stamped_frame[fy:fy+fh_box, fx:fx+fw_box] = cv2.GaussianBlur(f_roi, (k_w, k_h), 20)
            except Exception:
                pass

        # Vẽ khung đỏ đánh dấu đối tượng vi phạm trên ảnh bằng chứng toàn cảnh
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.rectangle(stamped_frame, (x1_clamped, y1_clamped), (x2_clamped, y2_clamped), (0, 0, 255), 2)
        box_label = f"VI PHAM ID:#{track_id} ({overlap_pct:.1f}%)"
        (bw, bh), _ = cv2.getTextSize(box_label, font, 0.55, 2)
        lbl_top = max(0, y1_clamped - bh - 8)
        cv2.rectangle(stamped_frame, (x1_clamped, lbl_top), (x1_clamped + bw + 10, y1_clamped), (0, 0, 255), -1)
        cv2.putText(stamped_frame, box_label, (x1_clamped + 5, max(15, y1_clamped - 4)), font, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

        # Đóng dấu tem pháp lý (Legal Stamp) ở góc dưới khung hình
        stamp_text = f"BANG CHUNG CCTV | Cam: {camera_id} | ID: #{track_id} | Lan chiem: {overlap_pct:.1f}% | {iso_timestamp}"
        (tw, th), _ = cv2.getTextSize(stamp_text, font, 0.55, 1)
        cv2.rectangle(stamped_frame, (10, h - th - 20), (20 + tw, h - 5), (0, 0, 0), -1)
        cv2.putText(stamped_frame, stamp_text, (15, h - 10), font, 0.55, (0, 255, 255), 1, cv2.LINE_AA)

        full_filename = f"violation_id{track_id}_{time_str}.jpg"
        full_path = os.path.join(full_dir, full_filename)
        cv2.imwrite(full_path, stamped_frame)

        return {
            "full_path": full_path.replace("\\", "/"),
            "crop_path": crop_path.replace("\\", "/"),
            "timestamp": iso_timestamp,
            "camera_id": camera_id,
            "track_id": track_id,
            "overlap_pct": overlap_pct
        }
