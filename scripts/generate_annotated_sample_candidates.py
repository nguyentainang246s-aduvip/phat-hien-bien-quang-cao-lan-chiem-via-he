"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Tác vụ: Sinh tập hợp các mẫu ảnh gán nhãn chuẩn YOLO (5 cột: class_id cx cy w h)
Mục tiêu: Cung cấp bộ sưu tập đa dạng các góc quay, bối cảnh, ánh sáng
để người dùng dễ dàng lựa chọn mẫu ưng ý nhất chèn vào báo cáo.
Lưu vào: reports/figures/annotated_samples/
==============================================================================
"""

import os
import sys
from pathlib import Path
import cv2
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
TRAIN_IMG_DIR = ROOT_DIR / "datasets/v13_clean/train/images"
TRAIN_LBL_DIR = ROOT_DIR / "datasets/v13_clean/train/labels"
OUT_DIR = ROOT_DIR / "reports/figures/annotated_samples"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CANDIDATES = [
    {
        "id": "sample_01_cctv_thanh_xuan",
        "file": "cctv_thanh_xuan_angle_4_medium_right_reverse_jpg.rf.1c186adbad29a5e3c302f2d99bdd0955.jpg",
        "title": "Mẫu 01: CCTV Góc nghiêng 45 độ hè phố kinh doanh (Thanh Xuân)",
        "context": "Hành lang vỉa hè thương mại ban ngày, biển hộp đèn & standee chân sắt"
    },
    {
        "id": "sample_02_cctv_night_street",
        "file": "cctv_night_angle_4_medium_right_reverse_jpg.rf.2dfe571ada226825be79047e6d6f2f83.jpg",
        "title": "Mẫu 02: CCTV Ban đêm chiếu sáng phức tạp (Night Surveillance)",
        "context": "Các biển hộp đèn phát sáng rực rỡ trên hành lang đi bộ ban đêm"
    },
    {
        "id": "sample_03_commercial_sidewalk_101",
        "file": "101_png.rf.50a11d82a151f751dc094528ba406abe.jpg",
        "title": "Mẫu 03: Tuyến phố thương mại sầm uất (Phố Huế - Hàng Bài)",
        "context": "Dãy biển hiệu và pano dựng sát mép vỉa hè người đi bộ"
    },
    {
        "id": "sample_04_urban_street_106",
        "file": "106_png.rf.7f47929620b3ec6d578bc12a522a3e14.jpg",
        "title": "Mẫu 04: Đô thị hiện đại với biển dựng dọc lề bo hè",
        "context": "Biển chữ A và hộp đèn dựng riêng lẻ, góc nhìn rõ nét"
    },
    {
        "id": "sample_05_street_signs_113",
        "file": "113_png.rf.6612d0ad08da44fe38c11e42fc00455d.jpg",
        "title": "Mẫu 05: Dãy biển quảng cáo trước ki-ốt kinh doanh",
        "context": "Nhiều biển hộp đứng liên tiếp chiếm lối đi bộ của người dân"
    },
    {
        "id": "sample_06_cctv_street_angle_1",
        "file": "cctv_street_angle_1_jpg.rf.00b8135f5509e28beaca40296f930dd3.jpg",
        "title": "Mẫu 06: CCTV Góc rộng quan sát hè phố và biển bạt lớn",
        "context": "Pano khung sắt lớn chắn ngang tầm nhìn vỉa hè giao lộ"
    },
    {
        "id": "sample_07_cctv_pho_standee",
        "file": "cctv_pho_angle_1_jpg.rf.4194253a9c4b02c4820635a3314c6fbb.jpg",
        "title": "Mẫu 07: CCTV Cự ly gần biển Standee chân sắt chữ A",
        "context": "Biển Standee đặt chính giữa lòng vỉa hè trước cửa hàng"
    },
    {
        "id": "sample_08_cctv_street_day_10",
        "file": "10_png.rf.170eb94693d7ddcfcaf7d1a6bc39c3c7.jpg",
        "title": "Mẫu 08: Khung cảnh vỉa hè ban ngày với cụm biển quảng cáo",
        "context": "Quan sát rõ mặt biển và chân đế tiếp đất trên vỉa hè"
    }
]


def generate_all():
    rendered_tiles = []
    
    print("=" * 70)
    print("BẮT ĐẦU SINH BỘ SƯU TẬP 8 MẪU ẢNH GÁN NHÃN CHUẨN YOLO")
    print("=" * 70)

    for item in CANDIDATES:
        img_p = TRAIN_IMG_DIR / item["file"]
        lbl_p = TRAIN_LBL_DIR / (img_p.stem + ".txt")

        if not img_p.exists() or not lbl_p.exists():
            print(f"[!] Bỏ qua do thiếu file: {item['file']}")
            continue

        img = cv2.imread(str(img_p))
        if img is None:
            continue
        h, w = img.shape[:2]

        lines = [l.strip() for l in lbl_p.read_text(encoding="utf-8").splitlines() if l.strip()]

        # Vẽ bounding box lên ảnh
        annotated = img.copy()
        for idx, line in enumerate(lines):
            parts = line.split()
            cls_id = int(parts[0])
            cx, cy, bw, bh = [float(x) for x in parts[1:]]

            x1 = int((cx - bw / 2.0) * w)
            y1 = int((cy - bh / 2.0) * h)
            x2 = int((cx + bw / 2.0) * w)
            y2 = int((cy + bh / 2.0) * h)

            # Khung chữ nhật xanh lá neon chuẩn
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 3)

            # Nhãn badge
            badge_text = f"bien-quang-cao [{cx:.2f}, {cy:.2f}]"
            font_scale = 0.55 if w > 1000 else 0.45
            (tw, th), _ = cv2.getTextSize(badge_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)
            cv2.rectangle(annotated, (x1, max(0, y1 - 24)), (x1 + tw + 10, max(0, y1)), (0, 180, 0), -1)
            cv2.putText(annotated, badge_text, (x1 + 5, max(17, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), 2)

        # Thanh tiêu đề trên (Header Banner) chuẩn phong cách Bách Khoa
        banner_h = 65
        banner = np.zeros((banner_h, w, 3), dtype=np.uint8)
        cv2.rectangle(banner, (0, 0), (w, banner_h), (30, 58, 138), -1)  # Navy Blue #1E3A8A
        cv2.putText(banner, f"{item['title']} - CHUẨN YOLO 5 CỘT", (15, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(banner, f"Bối cảnh: {item['context']} | Số BBox: {len(lines)} | Cú pháp: 0 cx cy w h", (15, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (165, 243, 252), 1)

        final_img = np.vstack([banner, annotated])
        out_file = OUT_DIR / f"{item['id']}.jpg"
        cv2.imwrite(str(out_file), final_img)
        print(f"[✓] Đã tạo thành công: {out_file.name} (Độ phân giải: {w}x{h+banner_h})")

        # Thu nhỏ để ghép vào Catalog tổng hợp
        tile = cv2.resize(final_img, (640, 380))
        rendered_tiles.append(tile)

    # Tạo bảng tổng hợp Catalog 8 ảnh
    if len(rendered_tiles) == 8:
        row1 = np.hstack(rendered_tiles[0:2])
        row2 = np.hstack(rendered_tiles[2:4])
        row3 = np.hstack(rendered_tiles[4:6])
        row4 = np.hstack(rendered_tiles[6:8])
        catalog = np.vstack([row1, row2, row3, row4])

        catalog_path = OUT_DIR / "catalog_all_8_samples.jpg"
        cv2.imwrite(str(catalog_path), catalog)
        print(f"[✓] Đã tạo bảng Catalog tổng hợp 8 ảnh: {catalog_path.name} ({catalog.shape[1]}x{catalog.shape[0]})")
        
        # Sao chép mẫu 01 (CCTV Thanh Xuân rất đẹp và chuẩn) làm mẫu mặc định cho roboflow_sample_annotated.jpg
        best_default = OUT_DIR / "sample_01_cctv_thanh_xuan.jpg"
        target_default = ROOT_DIR / "reports/figures/roboflow_sample_annotated.jpg"
        if best_default.exists():
            import shutil
            shutil.copyfile(str(best_default), str(target_default))
            print(f"[✓] Đã cập nhật mẫu 01 làm ảnh mặc định tại: {target_default.name}")


if __name__ == "__main__":
    generate_all()

