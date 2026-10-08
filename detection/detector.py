"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Computer Vision & Object Detection Wrapper
TASK: 10 - Xây dựng Module detection/detector.py chuẩn hóa đầu ra AI

LƯU Ý KIẾN TRÚC (ISSUE 14): Module này dùng cho test/demo ĐỘC LẬP
(test_detector.py, demo_yolo.py, sweep_threshold.py).
Pipeline chính (main.py) sử dụng ObjectTracker (tracking/tracker.py) thay thế
— ObjectTracker tích hợp cả Detection + ByteTrack trong một bước.
Conf mặc định ở đây (0.35) KHÁC với pipeline chính (0.20) vì mục đích khác nhau.
==============================================================================
"""

import os
from ultralytics import YOLO

class YOLODetector:
    """
    Lớp đóng gói (Wrapper) cho mô hình YOLOv8.
    Chuẩn hóa dữ liệu đầu ra từ PyTorch Tensor sang kiểu dữ liệu Python cơ bản.
    """
    def __init__(self, model_path: str = "models/best.pt", conf_threshold: float = 0.35, imgsz: int = 1280):
        """
        Khởi tạo Detector.
        
        Args:
            model_path: Đường dẫn tới trọng số .pt (vd: 'models/best.pt')
            conf_threshold: Ngưỡng độ tin cậy tối thiểu (mặc định 0.35 = 35%)
            imgsz: Kích thước cạnh ảnh đưa vào YOLO (mặc định 1280)
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.imgsz = imgsz
        
        if not os.path.exists(model_path) and not model_path.endswith("yolov8n.pt"):
            raise FileNotFoundError(f"Không tìm thấy file trọng số mô hình: {model_path}")
            
        print(f"[AI DETECTOR] Đang nạp mô hình: {model_path} (Conf: {conf_threshold}, Imgsz: {imgsz})")
        self.model = YOLO(model_path)
        self.class_names = self.model.names

    def detect(self, frame, imgsz: int = None) -> list:
        """
        Dự đoán các vật thể có trong khung hình.
        
        Args:
            frame: Ảnh ma trận BGR từ camera
            imgsz: Tùy chọn kích thước ảnh suy luận (nếu None sẽ dùng self.imgsz)
            
        Returns:
            list: Danh sách các dictionary chứa thông tin từng vật thể:
                  [
                      {
                          "box": (x1, y1, x2, y2),
                          "conf": float (độ tin cậy 0..1),
                          "class_id": int,
                          "class_name": str
                      },
                      ...
                  ]
        """
        infer_imgsz = imgsz if imgsz is not None else self.imgsz
        results = self.model.predict(frame, conf=self.conf_threshold, imgsz=infer_imgsz, verbose=False)
        detections = []
        
        if len(results) == 0 or results[0].boxes is None:
            return detections
            
        boxes = results[0].boxes
        for box in boxes:
            # Chuyển đổi tọa độ từ Tensor sang số nguyên chuẩn (x1, y1, x2, y2)
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            conf = float(box.conf[0].cpu().numpy())
            cls_id = int(box.cls[0].cpu().numpy())
            cls_name = self.class_names.get(cls_id, f"class_{cls_id}")
            
            detections.append({
                "box": (int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])),
                "conf": round(conf, 2),
                "class_id": cls_id,
                "class_name": cls_name
            })
            
        return detections
