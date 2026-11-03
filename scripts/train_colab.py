# =============================================================================
# ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
# SCRIPT HUẤN LUYỆN YOLOV8N TRÊN GOOGLE COLAB VỚI DATASET SẠCH (V13_CLEAN)
# =============================================================================
# HOÀN TOÀN KHÔNG CẦN ROBOFLOW - KHÔNG CẦN API KEY
# 
# HƯỚNG DẪN 3 BƯỚC:
#   Bước 1: Mở Google Colab (chọn Runtime -> Change runtime type -> T4 GPU).
#   Bước 2: Kéo file 'v13_clean.zip' từ máy tính thả vào biểu tượng Thư mục (Files) bên trái Colab.
#   Bước 3: Copy toàn bộ mã bên dưới dán vào 1 ô code và bấm Run (phím Play).
# =============================================================================

# 1. Cài đặt thư viện Ultralytics mới nhất
!pip install -q ultralytics

# 2. Giải nén tập dữ liệu sạch v13_clean
import os
import sys
import zipfile
from pathlib import Path

extract_dir = "/content/datasets/v13_clean"
os.makedirs(extract_dir, exist_ok=True)

print("[*] Đang giải nén tập dữ liệu v13_clean.zip...")
with zipfile.ZipFile('/content/v13_clean.zip', 'r') as zf:
    zf.extractall(extract_dir)

data_yaml = os.path.join(extract_dir, "data.yaml")
if os.path.exists(data_yaml):
    print(f"[✓] Giải nén thành công! File cấu hình dữ liệu: {data_yaml}")
else:
    raise FileNotFoundError(f"Không tìm thấy {data_yaml} sau khi giải nén!")

# 3. Khởi tạo và Huấn luyện mô hình YOLOv8n chuẩn cấu hình ĐATN
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

print("[*] Bắt đầu huấn luyện YOLOv8n ở imgsz=1280, batch=8, EarlyStopping patience=20...")
results = model.train(
    data=data_yaml,
    epochs=100,
    patience=20,
    batch=8,
    imgsz=1280,
    optimizer="AdamW",
    lr0=0.002,
    momentum=0.937,
    mosaic=1.0,
    erasing=0.4,
    name="train_v13_clean",
    save=True,
    plots=True
)

# 4. Đánh giá kiểm định độc lập trên tập Test (267 ảnh chưa từng thấy)
print("\n[*] Đang đánh giá trên tập Test độc lập...")
metrics_test = model.val(
    data=data_yaml,
    split="test",
    imgsz=1280,
    plots=True,
    name="test_v13_clean"
)

# 5. Xuất mô hình sang định dạng ONNX phục vụ chạy thực tế trên CPU
print("\n[*] Đang xuất mô hình sang ONNX...")
model.export(format="onnx", imgsz=1280, dynamic=True, simplify=True)

# 6. Tự động tải 2 file trọng số tốt nhất về máy tính của bạn
from google.colab import files
print("\n[✓] Huấn luyện hoàn tất! Trình duyệt sẽ tự động tải 2 file weights về:")
print("    - best.pt   (dùng cho kiểm thử PyTorch)")
print("    - best.onnx (dùng cho suy luận tối ưu CPU)")
files.download("runs/detect/train_v13_clean/weights/best.pt")
files.download("runs/detect/train_v13_clean/weights/best.onnx")

# (Tùy chọn) Tải toàn bộ báo cáo biểu đồ mAP và confusion matrix
# !zip -r training_results.zip runs/detect/train_v13_clean runs/detect/test_v13_clean
# files.download("training_results.zip")
