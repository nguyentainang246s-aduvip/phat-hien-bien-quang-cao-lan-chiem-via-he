# =============================================================================
# CODE CHẠY TRÊN GOOGLE COLAB ĐỂ HUẤN LUYỆN YOLOV8N - VERSION 13 (BẢN FINAL)
# =============================================================================
# Copy toàn bộ đoạn mã này vào 1 ô code trên Google Colab (chọn GPU T4) và bấm Chạy:

# 1. Cài đặt thư viện (trên Google Colab bỏ dấu thăng để chạy lệnh terminal: !pip install ultralytics roboflow)
# !pip install ultralytics roboflow

# 2. Tải Dataset Version 13 từ Roboflow (2,674 ảnh)
import os
from roboflow import Roboflow

# Bảo mật API Key qua biến môi trường (hoặc điền API Key dự án)
api_key = os.environ.get("ROBOFLOW_API_KEY")
if not api_key:
    raise ValueError("Vui lòng thiết lập biến môi trường ROBOFLOW_API_KEY trước khi chạy.")
rf = Roboflow(api_key=api_key)
project = rf.workspace("tai-nang-nguyen-duc").project("sidewalk-signboard-detection-1")
version = project.version(13)
dataset = version.download("yolov8")

# 3. Huấn luyện mô hình YOLOv8n với cấu hình chuẩn của ĐATN
from ultralytics import YOLO

# Khởi tạo mô hình pretrained COCO
model = YOLO("yolov8n.pt")

# Huấn luyện ở độ phân giải 1280x1280, batch=8, EarlyStopping patience=20
results = model.train(
    data=f"{dataset.location}/data.yaml",
    epochs=100,
    patience=20,
    batch=8,
    imgsz=1280,
    optimizer="AdamW",
    lr0=0.002,
    momentum=0.937,
    mosaic=1.0,
    erasing=0.4,
    name="train_v13",
    save=True,
    plots=True
)

# 4. Đánh giá kiểm thử độc lập trên tập Test
metrics_test = model.val(
    data=f"{dataset.location}/data.yaml",
    split="test",
    imgsz=1280,
    plots=True,
    name="test_v13"
)

# 5. Xuất mô hình sang định dạng ONNX
model.export(format="onnx", imgsz=1280, dynamic=True, simplify=True)

# 6. Nén kết quả và tải về máy
# !zip -r training_results_v13.zip runs/detect/train_v13 runs/detect/test_v13
from google.colab import files
# files.download("training_results_v13.zip")
# files.download("runs/detect/train_v13/weights/best.pt")
# files.download("runs/detect/train_v13/weights/best.onnx")
