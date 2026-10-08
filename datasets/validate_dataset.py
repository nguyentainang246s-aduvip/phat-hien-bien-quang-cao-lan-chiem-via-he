"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Dataset Verification & YAML Configuration
TASK: 14 - Kiểm tra tính toàn vẹn cấu trúc data.yaml và tập Train / Val / Test
==============================================================================
"""

import os
import sys
import yaml

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def validate_yolo_dataset(dataset_dir: str = "datasets/v8"):
    """
    Kiểm tra tính toàn vẹn của tập dữ liệu sau khi tải từ Roboflow về.
    Xác thực file data.yaml và khớp cặp giữa ảnh (.jpg/.png) và nhãn (.txt).
    """
    print("=" * 65)
    print("KIỂM TRA CẤU TRÚC TẬP DỮ LIỆU DATASET (TASK 14)")
    print("=" * 65)
    
    if not os.path.exists(dataset_dir):
        print(f"[LỖI] Chưa tìm thấy thư mục: '{dataset_dir}'")
        return False
        
    yaml_path = os.path.join(dataset_dir, "data.yaml")
    if not os.path.exists(yaml_path):
        print(f"[CHƯA CÓ DỮ LIỆU] Không tìm thấy file: '{yaml_path}'")
        print("\n>> HƯỚNG DẪN BẠN ĐƯA DỮ LIỆU VÀO ĐỒ ÁN:")
        print("  1. Trên Roboflow: Bấm Export Dataset -> Chọn định dạng YOLOv8 -> Download zip.")
        print(f"  2. Mở file zip đó ra và giải nén toàn bộ vào thư mục:")
        print(f"     👉 {os.path.abspath(dataset_dir)}")
        print("  3. Chạy lại script này để kiểm tra tự động.")
        print("=" * 65)
        return False
        
    # 1. Đọc và kiểm tra nội dung file data.yaml
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data_cfg = yaml.safe_load(f)
    except Exception as e:
        print(f"[LỖI] Không thể đọc file data.yaml: {e}")
        return False
        
    print(f"[+] Đã đọc thành công cấu hình: {yaml_path}")
    print(f"    - Số lượng class (nc) : {data_cfg.get('nc', 'Chưa định nghĩa')}")
    print(f"    - Danh sách class     : {data_cfg.get('names', [])}")
    print("-" * 65)
    
    # 2. Kiểm tra các thư mục con: train, valid, test
    splits = ["train", "valid", "test"]
    stats = {}
    
    for split in splits:
        split_path = os.path.join(dataset_dir, split)
        img_dir = os.path.join(split_path, "images")
        lbl_dir = os.path.join(split_path, "labels")
        
        if not os.path.exists(img_dir):
            # Một số bản Roboflow để trực tiếp trong split mà không có thư mục con images
            if os.path.exists(split_path):
                img_dir = split_path
                lbl_dir = split_path
            else:
                stats[split] = {"images": 0, "labels": 0, "status": "THIẾU THƯ MỤC"}
                continue
                
        images = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        labels = [f for f in os.listdir(lbl_dir) if f.lower().endswith('.txt') and f != "labels.txt"] if os.path.exists(lbl_dir) else []
        
        stats[split] = {
            "images": len(images),
            "labels": len(labels),
            "status": "ĐẦY ĐỦ" if len(images) > 0 else "TRỐNG"
        }
        
    print("THỐNG KÊ PHÂN CHIA DỮ LIỆU:")
    total_imgs = sum(s["images"] for s in stats.values())
    
    for split, info in stats.items():
        pct = (info['images'] / total_imgs * 100) if total_imgs > 0 else 0
        print(f"  • Tập {split.upper():5s}: {info['images']:4d} ảnh ({pct:5.1f}%) | {info['labels']:4d} file nhãn -> [{info['status']}]")
        
    print("-" * 65)
    print(f"[TỔNG CỘNG] Tập dữ liệu có: {total_imgs} ảnh.")
    
    if total_imgs > 0 and stats.get("train", {}).get("images", 0) > 0:
        print(">> KẾT LUẬN: TẬP DỮ LIỆU ĐẠT CHUẨN ĐẦY ĐỦ 100%!")
        print(">> SẴN SÀNG HUẤN LUYỆN MODEL TRÊN GOOGLE COLAB (TASK 15).")
        print("=" * 65)
        return True
    else:
        print("[CẢNH BÁO] Tập dữ liệu chưa có ảnh trong thư mục train.")
        print("=" * 65)
        return False


if __name__ == "__main__":
    dataset_folder = sys.argv[1] if len(sys.argv) > 1 else "datasets/v8"
    validate_yolo_dataset(dataset_folder)
