"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Script đóng gói toàn bộ mã nguồn quan trọng, tài liệu báo cáo và cấu hình
thành file ZIP tinh gọn (loại bỏ .venv, video nặng, models nặng) để gửi cho AI review
==============================================================================
"""

import os
import sys
import zipfile

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

ZIP_NAME = "DATN_AI_Review_Package.zip"

INCLUDE_EXTENSIONS = {
    ".py", ".md", ".json", ".yaml", ".yml", ".txt", ".docx", ".log", ".csv"
}

# Các thư mục chứa code và tài liệu cần đưa vào
INCLUDE_DIRS = [
    "camera",
    "configs",
    "dashboard",
    "database",
    "detection",
    "evaluation",
    "evidence",
    "reports",
    "roi",
    "scripts",
    "tests",
    "tracking",
    "utils",
    "violation"
]

# Các file đơn lẻ ở thư mục gốc
ROOT_FILES = [
    "AI_PROJECT_OVERVIEW.md",
    "README.md",
    "ke-hoach-do-an-tot-nghiep.md",
    "main.py",
    "roi_drawer.py",
    "test_on_image.py",
    "requirements.txt",
    ".gitignore",
    "FULL_PROJECT_REVIEW.txt",
    "PROJECT_ESSENTIALS_FOR_AI.txt",
    "export_word.py",
    "HO_SO_SUA_LOI_VA_MA_NGUON_DATN_20224083.docx"
]

# Một số ảnh crop bằng chứng tiêu biểu và ma trận nhầm lẫn để AI có thể phân tích
SAMPLE_IMAGES = [
    "reports/video_eval_crops/video_test/track_1_conf95.jpg",
    "reports/video_eval_crops/video_test/track_2_conf92.jpg",
    "reports/video_eval_crops/videotesst2/track_1_conf91.jpg",
    "reports/video_eval_crops/video_test3/track_1_conf92.jpg",
    "reports/video_eval_crops/video_test3/track_3_conf92.jpg",
    "reports/figures/cm_v8_test_conf0.424_norm.png",
    "reports/figures/confusion_matrix_test_v8_normalized.png"
]

# Các file docx cũ cồng kềnh (>7MB) hoặc file duplicate cần bỏ qua để giữ 1 nguồn duy nhất
OBSOLETE_DOCX = {
    "bao_cao_tien_do_yolov8n_datn_v8.docx",
    "bao_cao_tien_do_yolov8n_datn_v8_final.docx",
    "bao_cao_tien_do_yolov8n_datn.docx",
    "bao_cao_tien_do_tuan_nay_chi_tiet_toan_dien.docx",
    "bao_cao_tuan_nay_va_de_cuong_datn.docx",
    "bao_cao_tien_do_datn_tuan_tiep_theo_va_de_cuong.docx",
    "bao_cao_tien_do_tuan_nay_full_pipeline_va_de_cuong.docx"
}

EXCLUDE_DIRS = {
    ".venv", "venv", "__pycache__", ".git", ".pytest_cache", "runs", "scratch"
}


def package_project():
    print(f"[*] Bắt đầu đóng gói dự án vào: {ZIP_NAME}...")
    file_count = 0

    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zipf:
        # 1. Thêm các file ở thư mục gốc
        for f in ROOT_FILES:
            if os.path.exists(f):
                zipf.write(f, arcname=f)
                file_count += 1
                print(f"  + Thêm file gốc: {f}")

        # 2. Thêm các thư mục code và cấu hình
        for d in INCLUDE_DIRS:
            if not os.path.exists(d):
                continue
            for root, dirs, files in os.walk(d):
                # Bỏ qua thư mục rác
                dirs[:] = [sub for sub in dirs if sub not in EXCLUDE_DIRS]

                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in INCLUDE_EXTENSIONS:
                        # Bỏ qua file docx tạm thời mở bằng Word (~$...) hoặc docx cũ >7MB
                        if file.startswith("~$") or file.lower() in OBSOLETE_DOCX:
                            continue
                        full_path = os.path.join(root, file)
                        zipf.write(full_path, arcname=full_path)
                        file_count += 1

        # 3. Thêm các ảnh crop minh chứng tiêu biểu & ma trận nhầm lẫn
        for img in SAMPLE_IMAGES:
            if os.path.exists(img):
                zipf.write(img, arcname=img)
                file_count += 1
                print(f"  + Thêm ảnh minh chứng / ma trận: {img}")

    zip_size_mb = os.path.getsize(ZIP_NAME) / (1024 * 1024)
    print("=" * 70)
    print(f"[OK] DA DONG GOI THANH CONG: {ZIP_NAME}")
    print(f"[INFO] Tong so files: {file_count} files")
    print(f"[INFO] Dung luong file ZIP: {zip_size_mb:.2f} MB")
    print("=" * 70)


if __name__ == "__main__":
    package_project()
