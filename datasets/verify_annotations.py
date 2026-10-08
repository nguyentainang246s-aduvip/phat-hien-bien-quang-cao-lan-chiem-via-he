"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Dataset Annotation & Verification
TASK: 13 - Kiểm tra và Hiển thị trực quan nhãn gán định dạng chuẩn YOLO (.txt)
==============================================================================
"""

import os
import sys
import cv2

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def yolo_to_pixel_coords(box_normalized, img_width: int, img_height: int):
    """
    DÒNG CỐT LÕI 1: Chuyển tọa độ chuẩn hóa YOLO (0..1) sang tọa độ Pixel thực tế (x1, y1, x2, y2).
    
    YOLO format: (x_center, y_center, width, height) dạng tỷ lệ 0.0 -> 1.0
    OpenCV pixel: (x1, y1, x2, y2) tính từ góc trên-trái.
    """
    x_c, y_c, w, h = box_normalized
    
    # Chuyển tỷ lệ sang pixel
    box_w = w * img_width
    box_h = h * img_height
    box_x_center = x_c * img_width
    box_y_center = y_c * img_height
    
    # Tính tọa độ 2 góc đối diện
    x1 = int(box_x_center - (box_w / 2))
    y1 = int(box_y_center - (box_h / 2))
    x2 = int(box_x_center + (box_w / 2))
    y2 = int(box_y_center + (box_h / 2))
    
    # Đảm bảo không vượt quá biên của bức ảnh
    x1 = max(0, min(x1, img_width - 1))
    y1 = max(0, min(y1, img_height - 1))
    x2 = max(0, min(x2, img_width - 1))
    y2 = max(0, min(y2, img_height - 1))
    
    return x1, y1, x2, y2


def verify_yolo_labels(image_path: str, label_path: str, class_names=None):
    """
    Đọc 1 cặp ảnh + nhãn txt và vẽ các bounding box do con người gán nhãn lên ảnh.
    """
    if class_names is None:
        class_names = {0: "bien_hieu"}
        
    if not os.path.exists(image_path):
        print(f"[LỖI] Không tìm thấy file ảnh: {image_path}")
        return None
        
    img = cv2.imread(image_path)
    if img is None:
        print(f"[LỖI] Không thể đọc ảnh: {image_path}")
        return None
        
    h, w, _ = img.shape
    
    if not os.path.exists(label_path):
        print(f"[THÔNG BÁO] Đây là ảnh nền âm bản (Negative sample - không có biển hiệu).")
        return img
        
    with open(label_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    print(f"[+] Đang kiểm tra: {os.path.basename(image_path)} | Số nhãn gán: {len(lines)}")
    
    for idx, line in enumerate(lines, 1):
        parts = line.strip().split()
        if len(parts) != 5:
            continue
            
        cls_id = int(parts[0])
        coords = [float(p) for p in parts[1:]]
        x1, y1, x2, y2 = yolo_to_pixel_coords(coords, w, h)
        
        cls_name = class_names.get(cls_id, f"class_{cls_id}")
        
        # Vẽ Bounding Box màu cam nổi bật cho nhãn thủ công
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 140, 255), 2)
        
        # Vẽ nhãn tên
        label_text = f"#{idx} {cls_name}"
        cv2.putText(img, label_text, (x1, max(15, y1 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 255), 2, cv2.LINE_AA)
                    
    return img


def create_sample_annotation_for_demo():
    """Tạo thử 1 file nhãn mẫu .txt cho bức ảnh đầu tiên để demo kiểm thử."""
    img_dir = "datasets/raw_images"
    if not os.path.exists(img_dir):
        return None, None
        
    files = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.png'))]
    if not files:
        return None, None
        
    first_img = os.path.join(img_dir, files[0])
    label_file = os.path.splitext(first_img)[0] + ".txt"
    
    # Tạo nhãn mẫu chuẩn định dạng YOLO:
    # class_id=0 (bien_hieu), x_center=0.45, y_center=0.65, width=0.25, height=0.18
    sample_yolo_label = "0 0.450000 0.650000 0.250000 0.180000\n"
    with open(label_file, "w", encoding="utf-8") as f:
        f.write(sample_yolo_label)
        
    return first_img, label_file


if __name__ == "__main__":
    print("=" * 65)
    print("CÔNG CỤ KIỂM TRA NHÃN CHUẨN YOLO (TASK 13)")
    print("=" * 65)
    img_p, lbl_p = create_sample_annotation_for_demo()
    if img_p and lbl_p:
        vis_img = verify_yolo_labels(img_p, lbl_p, {0: "bien_hieu"})
        print(f"[OK] File nhãn mẫu chuẩn YOLO đã được tạo tại: {lbl_p}")
        print(f"     Nội dung nhãn: {open(lbl_p).read().strip()}")
        print("=" * 65)
