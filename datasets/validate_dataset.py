"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Dataset Verification & Deep Integrity Audit (Chuẩn Ultralytics YOLO)
TASK: 14 - Kiểm tra tính toàn vẹn cấu trúc data.yaml, nhãn và rò rỉ dữ liệu
==============================================================================
"""

import os
import sys
import re
from pathlib import Path
from collections import defaultdict
import yaml

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def validate_yolo_dataset(dataset_dir_str: str = None) -> bool:
    """
    Kiểm tra chuyên sâu tính toàn vẹn của tập dữ liệu YOLO:
    1. Cấu hình data.yaml và đường dẫn tương thích.
    2. Ánh xạ 1:1 giữa images và labels (Mirror rule).
    3. Cú pháp định dạng nhãn Bounding Box (5 cột, class_id, tọa độ chuẩn hóa).
    4. Tỷ lệ mẫu âm tính (Background samples).
    5. Phát hiện rò rỉ dữ liệu (Data Leakage) giữa Train - Valid - Test.
    """
    if dataset_dir_str is None:
        # Ưu tiên kiểm tra tập v13_clean nếu có, ngược lại kiểm tra v13
        if os.path.exists("datasets/v13_clean"):
            dataset_dir_str = "datasets/v13_clean"
        else:
            dataset_dir_str = "datasets/v13"

    dataset_dir = Path(dataset_dir_str)
    
    print("=" * 70)
    print("KIỂM TRA CHUYÊN SÂU TẬP DỮ LIỆU YOLO (TASK 14 AUDIT)")
    print("=" * 70)
    print(f"[*] Thư mục khảo sát: {dataset_dir.resolve()}")
    
    if not dataset_dir.exists():
        print(f"[LỖI] Không tìm thấy thư mục: '{dataset_dir}'")
        return False
        
    yaml_path = dataset_dir / "data.yaml"
    if not yaml_path.exists():
        print(f"[LỖI] Không tìm thấy file cấu hình: '{yaml_path}'")
        return False
        
    # 1. Đọc và kiểm tra nội dung file data.yaml
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data_cfg = yaml.safe_load(f)
    except Exception as e:
        print(f"[LỖI] Không thể đọc file data.yaml: {e}")
        return False
        
    print(f"[+] Đã đọc cấu hình: {yaml_path.name}")
    print(f"    - Số lượng class (nc) : {data_cfg.get('nc', 'Chưa định nghĩa')}")
    print(f"    - Danh sách class     : {data_cfg.get('names', [])}")
    print("-" * 70)
    
    # 2. Quét từng split: train, valid, test
    splits = ["train", "valid", "test"]
    stats = {}
    base_name_to_splits = defaultdict(lambda: defaultdict(list))
    has_critical_error = False
    
    for split in splits:
        split_path = dataset_dir / split
        img_dir = split_path / "images"
        lbl_dir = split_path / "labels"
        
        if not img_dir.exists():
            img_dir = split_path
            lbl_dir = split_path
            
        imgs = {p.stem: p for p in img_dir.glob("*.*") if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]}
        lbls = {p.stem: p for p in lbl_dir.glob("*.txt") if p.name != "labels.txt"}
        
        missing_lbl = set(imgs.keys()) - set(lbls.keys())
        orphan_lbl = set(lbls.keys()) - set(imgs.keys())
        
        empty_lbls = 0
        total_boxes = 0
        corrupt_lines = 0
        out_of_bounds = 0
        invalid_classes = 0
        
        for stem, img_p in imgs.items():
            # Gom nhóm ảnh gốc để kiểm tra rò rỉ
            base = re.sub(r'(\.rf\.[a-f0-9]+|_rf_[a-f0-9]+)$', '', stem, flags=re.IGNORECASE)
            base_name_to_splits[base.lower()][split].append(stem)
            
            lbl_p = lbls.get(stem)
            if not lbl_p or not lbl_p.exists():
                continue
                
            try:
                with open(lbl_p, "r", encoding="utf-8") as f:
                    lines = [l.strip() for l in f if l.strip()]
            except Exception:
                corrupt_lines += 1
                continue
                
            if not lines:
                empty_lbls += 1
                continue
                
            for line in lines:
                parts = line.split()
                if len(parts) != 5:
                    corrupt_lines += 1
                    continue
                try:
                    cls_id = int(parts[0])
                    coords = [float(x) for x in parts[1:]]
                except ValueError:
                    corrupt_lines += 1
                    continue
                    
                if cls_id != 0:
                    invalid_classes += 1
                for c in coords:
                    if c < -0.001 or c > 1.001:
                        out_of_bounds += 1
                total_boxes += 1
                
        stats[split] = {
            "images": len(imgs),
            "labels": len(lbls),
            "missing_lbl": len(missing_lbl),
            "orphan_lbl": len(orphan_lbl),
            "empty": empty_lbls,
            "boxes": total_boxes,
            "corrupt": corrupt_lines,
            "out_of_bounds": out_of_bounds,
            "invalid_classes": invalid_classes
        }
        
    # In bảng thống kê
    print(f"{'Split':<8} | {'Images':<8} | {'Labels':<8} | {'Empty (BG)':<10} | {'Boxes':<8} | {'Lỗi cú pháp':<10}")
    print("-" * 70)
    total_imgs = sum(s["images"] for s in stats.values())
    total_boxes = sum(s["boxes"] for s in stats.values())
    total_empty = sum(s["empty"] for s in stats.values())
    
    for split, s in stats.items():
        pct = (s['images'] / total_imgs * 100) if total_imgs > 0 else 0
        err_total = s['corrupt'] + s['out_of_bounds'] + s['invalid_classes'] + s['missing_lbl'] + s['orphan_lbl']
        err_str = "HỢP LỆ" if err_total == 0 else f"{err_total} LỖI"
        if err_total > 0:
            has_critical_error = True
        print(f"{split:<8} | {s['images']:<8} | {s['labels']:<8} | {s['empty']:<10} | {s['boxes']:<8} | {err_str:<10}")
        
    print("-" * 70)
    print(f"[TỔNG CỘNG] {total_imgs} ảnh | {total_boxes} hộp BBox | {total_empty} ảnh nền âm tính ({total_empty/total_imgs*100:.1f}%)")

    # 3. Kiểm tra rò rỉ dữ liệu (Data Leakage)
    print("\n" + "=" * 70)
    print("KIỂM TRA TÍNH ĐỘC LẬP GIỮA CÁC TẬP (DATA LEAKAGE CHECK)")
    print("=" * 70)
    leaked_bases = {}
    for base, sp_dict in base_name_to_splits.items():
        if len(sp_dict) > 1:
            leaked_bases[base] = {k: len(v) for k, v in sp_dict.items()}
            
    print(f"[*] Tổng số ảnh nguồn gốc độc lập: {len(base_name_to_splits)}")
    if leaked_bases:
        print(f"[CẢNH BÁO RÒ RỈ] Phát hiện {len(leaked_bases)} ảnh gốc xuất hiện ở nhiều split!")
        for b, dist in list(leaked_bases.items())[:5]:
            print(f"  - {b}: {dist}")
        has_critical_error = True
    else:
        print("[✓] TUYỆT VỜI: 0% rò rỉ dữ liệu! Toàn bộ ảnh gốc và biến thể nằm độc lập hoàn toàn.")
        
    print("=" * 70)
    if not has_critical_error and total_imgs > 0 and stats.get("train", {}).get("images", 0) > 0:
        print(">> KẾT LUẬN: TẬP DỮ LIỆU ĐẠT CHUẨN KHOA HỌC 100%!")
        print(">> SẴN SÀNG HUẤN LUYỆN YOLOV8 TRÊN GOOGLE COLAB HOẶC MÁY CHỦ.")
        print("=" * 70)
        return True
    else:
        print("[CẢNH BÁO] Tập dữ liệu còn tồn tại lỗi cú pháp hoặc rò rỉ dữ liệu cần xử lý.")
        print("=" * 70)
        return False


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else None
    success = validate_yolo_dataset(folder)
    sys.exit(0 if success else 1)
