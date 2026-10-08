"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Object Tracking & Multi-Object Association
TASK: 21 - Xây dựng Module tracking/tracker.py tích hợp ByteTrack
==============================================================================
"""

import os
import cv2
import numpy as np
from ultralytics import YOLO


class ObjectTracker:
    """
    Bộ bám vết vật thể (Multi-Object Tracker) tích hợp thuật toán ByteTrack.
    Nhiệm vụ: Gán và duy trì một mã định danh duy nhất (track_id: 1, 2, 3...)
    cho từng biển hiệu xuyên suốt các khung hình video theo thời gian.
    """
    def __init__(self, model_path: str = "models/best.pt", conf_threshold: float = 0.20, tracker_type: str = "bytetrack.yaml"):
        """
        Khởi tạo ObjectTracker.
        
        Args:
            model_path: Đường dẫn file trọng số YOLO (vd: 'models/best.pt' hoặc 'yolov8n.pt')
            conf_threshold: Ngưỡng độ tin cậy tối thiểu (mặc định 0.20 = 20%)
            tracker_type: File cấu hình tracker ('bytetrack.yaml' hoặc 'botsort.yaml')
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.tracker_type = tracker_type
        
        if not os.path.exists(model_path) and not model_path.endswith("yolov8n.pt"):
            raise FileNotFoundError(f"Không tìm thấy file trọng số mô hình: {model_path}")
            
        print(f"[OBJECT TRACKER] Nạp mô hình: {model_path} | Thuật toán: {tracker_type} (Conf: {conf_threshold})")
        self.model = YOLO(model_path)
        self.class_names = self.model.names

    def track(self, frame) -> list:
        """
        Thực hiện phát hiện và bám vết đối tượng trong khung hình.
        
        Args:
            frame: Ảnh ma trận BGR nguyên bản từ camera (Raw Frame)
            
        Returns:
            list: Danh sách các đối tượng được bám vết:
                  [
                      {
                          "track_id": int (Mã định danh duy nhất: 1, 2, 3...; -1 nếu chưa khớp),
                          "box": (x1, y1, x2, y2),
                          "conf": float (0.0 -> 1.0),
                          "class_id": int,
                          "class_name": str
                      },
                      ...
                  ]
        """
        # persist=True: Bắt buộc để ByteTrack nhớ trạng thái Kalman Filter giữa các frames liên tiếp
        results = self.model.track(
            source=frame,
            persist=True,
            tracker=self.tracker_type,
            conf=self.conf_threshold,
            verbose=False
        )

        tracked_objects = []
        if len(results) == 0 or results[0].boxes is None:
            return tracked_objects

        boxes = results[0].boxes
        for box in boxes:
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            conf = float(box.conf[0].cpu().numpy())
            cls_id = int(box.cls[0].cpu().numpy())
            cls_name = self.class_names.get(cls_id, f"class_{cls_id}")

            # Lấy track_id do ByteTrack sinh ra
            if box.id is not None:
                track_id = int(box.id[0].cpu().numpy())
            else:
                track_id = -1  # Vật thể mới xuất hiện chưa đủ độ tin cậy để gán ID

            tracked_objects.append({
                "track_id": track_id,
                "box": (int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])),
                "conf": round(conf, 2),
                "class_id": cls_id,
                "class_name": cls_name
            })

        return tracked_objects

    def reset(self):
        """Reset bộ nhớ trạng thái tracker (khi chuyển luồng camera hoặc tua lại video)"""
        # Khởi tạo lại tracker state trong model
        if hasattr(self.model, 'predictor') and self.model.predictor is not None:
            self.model.predictor.trackers = None
