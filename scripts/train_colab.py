# =============================================================================
# CODE CHẠY TRÊN GOOGLE COLAB ĐỂ HUẤN LUYỆN YOLOV8N - VERSION 8
# =============================================================================
# Copy toàn bộ đoạn mã này vào 1 ô code trên Google Colab (chọn GPU T4) và bấm Chạy:

# 1. Cài đặt thư viện (trên Google Colab bỏ dấu thăng để chạy lệnh terminal: !pip install ultralytics roboflow)
# !pip install ultralytics roboflow

# 2. Tải Dataset Version 8 từ Roboflow
from roboflow import Roboflow
rf = Roboflow(api_key="mm2WOhL7NRUJjs5pn3h1")
project = rf.workspace("tai-nang-nguyen-duc").project("sidewalk-signboard-detection-1")
version = project.version(8)
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
    name="train_v8",
    save=True,
    plots=True
)

# 4. Đánh giá kiểm thử độc lập trên tập Test
metrics_test = model.val(
    data=f"{dataset.location}/data.yaml",
    split="test",
    imgsz=1280,
    plots=True,
    name="test_v8"
)

# 5. Nén kết quả và tải về máy (trên Google Colab: !zip -r training_results_v8.zip ...)
# !zip -r training_results_v8.zip runs/detect/train_v8 runs/detect/test_v8
from google.colab import files
files.download("training_results_v8.zip")
files.download("runs/detect/train_v8/weights/best.pt")
