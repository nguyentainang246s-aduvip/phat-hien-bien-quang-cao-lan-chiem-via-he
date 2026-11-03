# =============================================================================
# ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
# SCRIPT HUẤN LUYỆN YOLOV8N TRÊN GOOGLE COLAB - PHIÊN BẢN SẠCH 100% (V13_CLEAN)
# =============================================================================
# Hướng dẫn chạy trên Google Colab (chọn Runtime -> Change runtime type -> T4 GPU):
# Copy toàn bộ file này dán vào 1 ô code trên Colab và bấm Run.

import os
import re
import shutil
import random
from pathlib import Path
from collections import defaultdict

# -----------------------------------------------------------------------------
# 1. CÀI ĐẶT THƯ VIỆN CẦN THIẾT
# -----------------------------------------------------------------------------
# !pip install ultralytics roboflow

# -----------------------------------------------------------------------------
# 2. TẢI DATASET V13 TỪ ROBOFLOW HOẶC GOOGLE DRIVE
# -----------------------------------------------------------------------------
from roboflow import Roboflow

api_key = os.environ.get("ROBOFLOW_API_KEY")
if not api_key:
    # Bạn có thể điền trực tiếp API Key Roboflow của bạn vào đây nếu chưa đặt biến môi trường:
    api_key = "YOUR_ROBOFLOW_API_KEY"

rf = Roboflow(api_key=api_key)
project = rf.workspace("tai-nang-nguyen-duc").project("sidewalk-signboard-detection-1")
version = project.version(13)
raw_dataset = version.download("yolov8", location="/content/datasets/v13_raw")

# -----------------------------------------------------------------------------
# 3. TỰ ĐỘNG CHUẨN HÓA & TRIỆT TIÊU 100% RÒ RỈ DỮ LIỆU (GROUP-BASED STRATIFIED SPLIT)
# -----------------------------------------------------------------------------
def polygon_to_bbox(coords):
    xs = coords[0::2]
    ys = coords[1::2]
    x_min, x_max = max(0.0, min(xs)), min(1.0, max(xs))
    y_min, y_max = max(0.0, min(ys)), min(1.0, max(ys))
    w = max(0.0, x_max - x_min)
    h = max(0.0, y_max - y_min)
    cx = x_min + w / 2.0
    cy = y_min + h / 2.0
    return cx, cy, w, h

def get_group_key(stem):
    base = re.sub(r'(\.rf\.[a-f0-9]+|_rf_[a-f0-9]+)$', '', stem, flags=re.I)
    cctv_m = re.match(r'^(cctv_[a-zA-Z0-9_]+?_angle|cctv_[a-zA-Z0-9_]+|Bon-goc-[a-zA-Z0-9_\-]+|Canh-CCTV-[a-zA-Z0-9_\-]+|Man-hinh-CCTV-[a-zA-Z0-9_\-]+)', base, re.I)
    if cctv_m:
        raw = re.sub(r'(_angle.*|_camera.*|\d+)$', '', cctv_m.group(1).lower())
        return 'cctv_group:' + raw
    gemini_m = re.match(r'^(Gemini_Generated_Image_[a-zA-Z0-9]+)', base, re.I)
    if gemini_m:
        return 'gemini_group:' + gemini_m.group(1).lower()
    chatgpt_m = re.match(r'^(ChatGPT-Image-[a-zA-Z0-9_\-]+|Duck-ai-image-[a-zA-Z0-9_\-]+)', base, re.I)
    if chatgpt_m:
        raw = re.sub(r'_\d+$', '', chatgpt_m.group(1).lower())
        return 'ai_group:' + raw
    return 'base_group:' + base.lower()

src_dir = Path("/content/datasets/v13_raw")
dst_dir = Path("/content/datasets/v13_clean")

print("[*] Đang tiến hành làm sạch dataset và triệt tiêu rò rỉ dữ liệu...")
all_pairs = []
for sp in ["train", "valid", "test"]:
    img_p = src_dir / sp / "images"
    lbl_p = src_dir / sp / "labels"
    if not img_p.exists():
        continue
    for img in img_p.glob("*.*"):
        if img.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            lbl = lbl_p / f"{img.stem}.txt"
            has_b = lbl.exists() and lbl.stat().st_size > 0 and bool(lbl.read_text(encoding="utf-8").strip())
            all_pairs.append((img, lbl, has_b))

groups = defaultdict(list)
for item in all_pairs:
    groups[get_group_key(item[0].stem)].append(item)

group_keys = sorted(groups.keys())
random.seed(42)
random.shuffle(group_keys)

tot = len(all_pairs)
target_v = int(tot * 0.10)
target_t = int(tot * 0.10)
sp_data = {'train': [], 'valid': [], 'test': []}
assigned = {'train': 0, 'valid': 0, 'test': 0}

for k in group_keys:
    items = groups[k]
    cnt = len(items)
    if assigned['valid'] + cnt <= target_v:
        sp_data['valid'].extend(items)
        assigned['valid'] += cnt
    elif assigned['test'] + cnt <= target_t:
        sp_data['test'].extend(items)
        assigned['test'] += cnt
    else:
        sp_data['train'].extend(items)
        assigned['train'] += cnt

for sp in ["train", "valid", "test"]:
    o_img = dst_dir / sp / "images"
    o_lbl = dst_dir / sp / "labels"
    o_img.mkdir(parents=True, exist_ok=True)
    o_lbl.mkdir(parents=True, exist_ok=True)
    for img_p, lbl_p, has_b in sp_data[sp]:
        shutil.copy2(img_p, o_img / img_p.name)
        dst_lbl = o_lbl / f"{img_p.stem}.txt"
        if not lbl_p.exists() or not has_b:
            dst_lbl.write_text("", encoding="utf-8")
            continue
        lines = []
        with open(lbl_p, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                cls_id = int(parts[0])
                coords = [float(x) for x in parts[1:]]
                if len(parts) == 5:
                    cx, cy, w, h = coords
                elif len(parts) >= 7 and len(parts) % 2 == 1:
                    cx, cy, w, h = polygon_to_bbox(coords)
                else:
                    continue
                lines.append(f"{cls_id} {max(0.0, min(1.0, cx)):.6f} {max(0.0, min(1.0, cy)):.6f} {max(0.001, min(1.0, w)):.6f} {max(0.001, min(1.0, h)):.6f}\n")
        dst_lbl.write_text("".join(lines), encoding="utf-8")

yaml_clean = dst_dir / "data.yaml"
yaml_clean.write_text("""train: train/images
val: valid/images
test: test/images
nc: 1
names:
  0: bien-quang-cao
""", encoding="utf-8")

print(f"[✓] Đã tạo tập dữ liệu sạch tại: {dst_dir}")
print(f"    Train: {len(sp_data['train'])}, Valid: {len(sp_data['valid'])}, Test: {len(sp_data['test'])}")

# -----------------------------------------------------------------------------
# 4. HUẤN LUYỆN YOLOV8N VỚI CẤU HÌNH ĐATN CHUẨN
# -----------------------------------------------------------------------------
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

results = model.train(
    data=str(yaml_clean),
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

# -----------------------------------------------------------------------------
# 5. ĐÁNH GIÁ KIỂM ĐỊNH ĐỘC LẬP TRÊN TẬP TEST (100% UNSEEN)
# -----------------------------------------------------------------------------
metrics_test = model.val(
    data=str(yaml_clean),
    split="test",
    imgsz=1280,
    plots=True,
    name="test_v13_clean"
)

# -----------------------------------------------------------------------------
# 6. XUẤT MÔ HÌNH SANG ĐỊNH DẠNG ONNX
# -----------------------------------------------------------------------------
model.export(format="onnx", imgsz=1280, dynamic=True, simplify=True)

# -----------------------------------------------------------------------------
# 7. NÉN KẾT QUẢ VÀ TẢI VỀ MÁY
# -----------------------------------------------------------------------------
# !zip -r training_results_v13_clean.zip runs/detect/train_v13_clean runs/detect/test_v13_clean
from google.colab import files
# files.download("training_results_v13_clean.zip")
# files.download("runs/detect/train_v13_clean/weights/best.pt")
# files.download("runs/detect/train_v13_clean/weights/best.onnx")
