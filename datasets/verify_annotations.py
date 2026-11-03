"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Dataset Annotation & Verification Tool (Hỗ trợ cả BBox & Polygon)
TASK: 13 - Kiểm tra và Hiển thị trực quan nhãn gán định dạng chuẩn YOLO
==============================================================================
"""

import os
import sys
import argparse
from pathlib import Path
import cv2
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def yolo_to_pixel_coords(box_normalized, img_width: int, img_height: int):
    """Chuyển tọa độ chuẩn hóa YOLO (cx, cy, w, h) sang Pixel (x1, y1, x2, y2)."""
    x_c, y_c, w, h = box_normalized
    box_w = w * img_width
    box_h = h * img_height
    box_x_center = x_c * img_width
    box_y_center = y_c * img_height
    
    x1 = int(box_x_center - (box_w / 2))
    y1 = int(box_y_center - (box_h / 2))
    x2 = int(box_x_center + (box_w / 2))
    y2 = int(box_y_center + (box_h / 2))
    
    x1 = max(0, min(x1, img_width - 1))
    y1 = max(0, min(y1, img_height - 1))
    x2 = max(0, min(x2, img_width - 1))
    y2 = max(0, min(y2, img_height - 1))
    return x1, y1, x2, y2


def verify_yolo_labels(image_path: str, label_path: str, class_names=None, output_path: str = None):
    """
    Đọc cặp ảnh + nhãn txt và vẽ các đối tượng (BBox hoặc Polygon) lên ảnh.
    """
    if class_names is None:
        class_names = {0: "bien_quang_cao"}
        
    if not os.path.exists(image_path):
        print(f"[LỖI] Không tìm thấy file ảnh: {image_path}")
        return None
        
    img = cv2.imread(image_path)
    if img is None:
        print(f"[LỖI] Không thể đọc ảnh: {image_path}")
        return None
        
    h, w, _ = img.shape
    
    if not os.path.exists(label_path):
        print(f"[THÔNG BÁO] Không có nhãn -> Đây là ảnh nền âm tính (Negative sample).")
        return img
        
    with open(label_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        
    print(f"[+] Kiểm tra ảnh: {os.path.basename(image_path)} | Số đối tượng: {len(lines)}")
    
    for idx, line in enumerate(lines, 1):
        parts = line.split()
        if not parts:
            continue
        try:
            cls_id = int(parts[0])
            coords = [float(p) for p in parts[1:]]
        except ValueError:
            continue
            
        cls_name = class_names.get(cls_id, f"class_{cls_id}")
        
        if len(parts) == 5:
            # Chuẩn Bounding Box: class cx cy w h
            x1, y1, x2, y2 = yolo_to_pixel_coords(coords, w, h)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 140, 255), 2)
            cv2.putText(img, f"#{idx} {cls_name}", (x1, max(15, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 255), 2, cv2.LINE_AA)
        elif len(parts) >= 7 and len(parts) % 2 == 1:
            # Chuẩn Polygon: class x1 y1 x2 y2 ...
            pts = []
            for i in range(0, len(coords), 2):
                pts.append([int(coords[i] * w), int(coords[i+1] * h)])
            pts = np.array(pts, np.int32).reshape((-1, 1, 2))
            cv2.polylines(img, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            if len(pts) > 0:
                lx, ly = pts[0][0]
                cv2.putText(img, f"#{idx} [poly] {cls_name}", (lx, max(15, ly - 6)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
                
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, img)
        print(f"[OK] Đã lưu ảnh minh họa trực quan tại: {output_path}")
        
    return img


def inspect_sample_from_dataset(dataset_dir: str = "datasets/v13_clean"):
    """Lấy mẫu ngẫu nhiên 1 ảnh có nhãn từ dataset để kiểm tra."""
    img_dir = Path(dataset_dir) / "train" / "images"
    lbl_dir = Path(dataset_dir) / "train" / "labels"
    if not img_dir.exists():
        print(f"[LỖI] Chưa tìm thấy thư mục {img_dir}")
        return None
        
    for img_p in img_dir.glob("*.jpg"):
        lbl_p = lbl_dir / f"{img_p.stem}.txt"
        if lbl_p.exists() and lbl_p.stat().st_size > 0:
            out_p = "scratch/verified_sample.jpg"
            verify_yolo_labels(str(img_p), str(lbl_p), output_path=out_p)
            return out_p
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kiểm tra và trực quan hóa nhãn YOLO")
    parser.add_argument("--image", type=str, default=None, help="Đường dẫn file ảnh")
    parser.add_argument("--label", type=str, default=None, help="Đường dẫn file nhãn .txt")
    parser.add_argument("--dataset", type=str, default="datasets/v13_clean", help="Thư mục dataset")
    args = parser.parse_args()
    
    print("=" * 65)
    print("CÔNG CỤ KIỂM TRA & TRỰC QUAN HÓA NHÃN YOLO (TASK 13)")
    print("=" * 65)
    
    if args.image and args.label:
        verify_yolo_labels(args.image, args.label, output_path="scratch/verified_custom.jpg")
    else:
        inspect_sample_from_dataset(args.dataset)
