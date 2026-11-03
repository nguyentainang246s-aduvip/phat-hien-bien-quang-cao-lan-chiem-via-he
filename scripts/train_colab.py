# =============================================================================
# ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
# SCRIPT HUẤN LUYỆN YOLOV8N TRÊN GOOGLE COLAB - BẢN DUY NHẤT 1 CELL (ALL-IN-ONE)
# =============================================================================
# HƯỚNG DẪN:
#   1. Chọn GPU: Runtime -> Change runtime type -> T4 GPU.
#   2. Upload file 'v13_clean.zip' vào mục Files bên trái Colab (chờ upload xong 100%).
#   3. Dán toàn bộ mã dưới đây vào 1 ô code duy nhất và bấm Run (▶️).
# =============================================================================

# BƯỚC 1: Cài đặt Ultralytics
!pip install -q ultralytics

import os
import sys
import zipfile
import torch
from pathlib import Path
from ultralytics import YOLO
from google.colab import files

print("=" * 70)
print(f"[*] PyTorch Version : {torch.__version__}")
print(f"[*] GPU khả dụng    : {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CHƯA CÓ GPU (Cần bật T4)'}")
print("=" * 70)

# BƯỚC 2: Giải nén tập dữ liệu sạch v13_clean
extract_dir = "/content/datasets/v13_clean"
os.makedirs(extract_dir, exist_ok=True)
zip_file = "/content/v13_clean.zip"

if not os.path.exists(zip_file):
    raise FileNotFoundError(f"[LỖI] Chưa tìm thấy file {zip_file}! Vui lòng upload file zip vào Colab.")

print(f"[*] Đang giải nén tập dữ liệu sạch {zip_file}...")
with zipfile.ZipFile(zip_file, 'r') as zf:
    zf.extractall(extract_dir)

data_yaml = os.path.join(extract_dir, "data.yaml")
if os.path.exists(data_yaml):
    print(f"[✓] Giải nén thành công! File cấu hình dữ liệu: {data_yaml}")
else:
    raise FileNotFoundError("Giải nén thất bại: Không tìm thấy data.yaml")

# BƯỚC 3: Khởi tạo và Huấn luyện mô hình YOLOv8n chuẩn ĐATN
print("\n" + "=" * 70)
print("[*] Bắt đầu huấn luyện YOLOv8n ở imgsz=1280, batch=8, EarlyStopping patience=20...")
print("=" * 70)

model = YOLO("yolov8n.pt")

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
    close_mosaic=10,
    erasing=0.4,
    seed=0,
    deterministic=True,
    amp=True,
    project="runs/detect",
    name="train_v13_clean",
    save=True,
    plots=True
)

print(f"\n[✓] Huấn luyện hoàn tất! Trọng số tốt nhất lưu tại: runs/detect/train_v13_clean/weights/best.pt")

# BƯỚC 4: Đánh giá độc lập trên tập Test (267 ảnh chưa từng thấy)
print("\n" + "=" * 70)
print("[*] Đang đánh giá độc lập trên tập Test (267 ảnh, cách ly 100%)...")
print("=" * 70)

best_model = YOLO("runs/detect/train_v13_clean/weights/best.pt")
metrics_test = best_model.val(
    data=data_yaml,
    split="test",
    imgsz=1280,
    plots=True,
    project="runs/detect",
    name="test_v13_clean"
)

print("\n" + "=" * 70)
print("SỐ LIỆU ĐÁNH GIÁ KIỂM THỬ TRUNG THỰC (TẬP TEST ĐỘC LẬP - ĐƯA VÀO LUẬN VĂN):")
print(f"  • Precision (Độ chính xác)     : {metrics_test.results_dict.get('metrics/precision(B)', 0):.4f}")
print(f"  • Recall (Độ bao phủ)          : {metrics_test.results_dict.get('metrics/recall(B)', 0):.4f}")
print(f"  • mAP@50                       : {metrics_test.results_dict.get('metrics/mAP50(B)', 0):.4f}")
print(f"  • mAP@50-95                    : {metrics_test.results_dict.get('metrics/mAP50-95(B)', 0):.4f}")
print("=" * 70)

# BƯỚC 5: Xuất mô hình sang định dạng ONNX
print("\n[*] Đang xuất mô hình sang ONNX phục vụ chạy CPU...")
best_model.export(format="onnx", imgsz=1280, dynamic=True, simplify=True)

# BƯỚC 6: Đóng gói artifacts và tải về máy
print("\n[*] Đang đóng gói toàn bộ artifacts (biểu đồ, log, weights)...")
!zip -q -r /content/results_v13_clean.zip runs/detect/train_v13_clean runs/detect/test_v13_clean

print("\n[✓] Đang gửi lệnh tải file về máy tính qua trình duyệt:")
print("    1. best.pt (Trọng số PyTorch)")
print("    2. best.onnx (Trọng số ONNX chạy CPU)")
print("    3. results_v13_clean.zip (Toàn bộ biểu đồ mAP, confusion matrix, kết quả)")
files.download("runs/detect/train_v13_clean/weights/best.pt")
files.download("runs/detect/train_v13_clean/weights/best.onnx")
files.download("/content/results_v13_clean.zip")
