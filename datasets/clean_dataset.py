"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Dataset Engineering & Quality Assurance
TASK: 12 - Kiểm tra chất lượng ảnh, lọc ảnh nhòe mờ & Chuẩn hóa Dataset
==============================================================================
"""

import os
import sys
import cv2
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def calculate_blur_score(image: np.ndarray) -> float:
    """
    DÒNG CỐT LÕI 1: Đo độ sắc nét của ảnh bằng phương sai toán tử Laplace (Laplacian Variance).
    
    Nguyên lý:
        Toán tử Laplace tìm các cạnh (edges) sắc nét trong ảnh.
        - Ảnh sắc nét: Nhiều cạnh rõ ràng -> Phương sai biến thiên lớn (score cao > 100).
        - Ảnh mờ/nhòe do rung camera: Ít cạnh, pixel bị nhòe đều -> Phương sai rất thấp (score < 50).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()
    return variance


def check_brightness(image: np.ndarray) -> float:
    """Đo độ sáng trung bình của ảnh (0 = tối đen, 255 = trắng xóa)."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return float(np.mean(gray))


def audit_and_clean_dataset(input_dir: str = "datasets/raw_images", blur_threshold: float = 40.0):
    """
    Quét toàn bộ ảnh trong thư mục raw, kiểm tra tính hợp lệ và lọc các ảnh kém chất lượng.
    """
    print("=" * 65)
    print("BẮT ĐẦU KIỂM TRA CHẤT LƯỢNG DATASET (TASK 12)")
    print("=" * 65)
    
    if not os.path.exists(input_dir):
        print(f"[LỖI] Thư mục không tồn tại: {input_dir}")
        return
        
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    total_images = len(image_files)
    
    if total_images == 0:
        print(f"[THÔNG BÁO] Chưa có ảnh nào trong: {input_dir}")
        return
        
    print(f"[+] Tổng số ảnh cần kiểm tra: {total_images} ảnh")
    print(f"[+] Ngưỡng lọc ảnh mờ       : Laplacian Score >= {blur_threshold}")
    print("-" * 65)
    
    valid_count = 0
    blurry_count = 0
    corrupt_count = 0
    
    for idx, fname in enumerate(image_files, 1):
        img_path = os.path.join(input_dir, fname)
        
        # 1. Kiểm tra ảnh có đọc được không
        img = cv2.imread(img_path)
        if img is None:
            print(f"  [HỎNG] #{idx:03d} File hỏng hoặc không thể đọc: {fname}")
            corrupt_count += 1
            continue
            
        h, w, c = img.shape
        blur_score = calculate_blur_score(img)
        brightness = check_brightness(img)
        
        # 2. Đánh giá độ sắc nét
        if blur_score < blur_threshold:
            status = "NHÒE/MỜ (Cần loại bỏ)"
            blurry_count += 1
        else:
            status = "ĐẠT CHUẨN"
            valid_count += 1
            
        print(f"  #{idx:03d} {fname[:35]}... | Size: {w}x{h} | Blur: {blur_score:6.1f} | Sáng: {brightness:5.1f} -> [{status}]")
        
    print("=" * 65)
    print(f"[KẾT QUẢ ĐÁNH GIÁ CHẤT LƯỢNG DATASET]")
    print(f"  ✓ Ảnh đạt chuẩn đưa vào gán nhãn : {valid_count} / {total_images} ({valid_count/total_images*100:.1f}%)")
    print(f"  ✗ Ảnh bị mờ/rung camera          : {blurry_count}")
    print(f"  ✗ File lỗi hỏng                  : {corrupt_count}")
    print("=" * 65)


if __name__ == "__main__":
    audit_and_clean_dataset()
