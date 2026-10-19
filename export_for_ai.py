"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Script xuất toàn bộ mã nguồn, cấu hình và báo cáo thành 1 file text duy nhất
để gửi cho AI Reviewer đọc trực tiếp mà không bị lỗi giải mã file nhị phân/zip.
==============================================================================
"""

import os
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Các đuôi file văn bản/code cần đọc
TEXT_EXTENSIONS = {
    ".py", ".md", ".yaml", ".yml", ".json", ".txt", ".csv", ".log"
}

# Các thư mục hoặc thành phần không cần đưa vào để tránh rác và phình kích thước
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "env",
    "node_modules",
    "video_eval_crops",
    "figures",
    "runs",
    "scratch",
    ".pytest_cache",
    "labels",  # Bỏ qua 900+ file nhãn tọa độ YOLO để giữ file tinh gọn, chỉ giữ code & data.yaml
}

OUTPUT_FILE = "FULL_PROJECT_REVIEW.txt"


def export_project():
    root_dir = Path(".")
    exported_count = 0
    total_lines = 0

    print(f"[*] Đang quét và xuất dự án ra file: {OUTPUT_FILE}...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        # Header tổng quan
        out.write("=" * 80 + "\n")
        out.write("ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV\n")
        out.write("TỔNG HỢP TOÀN BỘ MÃ NGUỒN, CẤU HÌNH VÀ BÁO CÁO PHỤC VỤ AI REVIEW\n")
        out.write("=" * 80 + "\n\n")

        for file_path in sorted(root_dir.rglob("*")):
            # Bỏ qua thư mục nằm trong danh sách loại trừ
            if any(part in EXCLUDE_DIRS for part in file_path.parts):
                continue

            if file_path.is_file() and file_path.suffix.lower() in TEXT_EXTENSIONS:
                if file_path.name in {OUTPUT_FILE, "FULL_PROJECT_REVIEW.txt"}:
                    continue

                rel_path = file_path.relative_to(root_dir)
                out.write(f"\n{'='*80}\n")
                out.write(f"FILE: {rel_path}\n")
                out.write(f"{'='*80}\n\n")
                try:
                    content = file_path.read_text(encoding="utf-8", errors="replace")
                    out.write(content + "\n")
                    exported_count += 1
                    total_lines += content.count("\n") + 1
                except Exception as e:
                    out.write(f"[Lỗi đọc file: {e}]\n")

    file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print("=" * 80)
    print(f"[OK] Đã xuất thành công toàn bộ dự án ra file: {OUTPUT_FILE}")
    print(f"[INFO] Tổng số file đã gộp: {exported_count} files")
    print(f"[INFO] Tổng số dòng: {total_lines:,} lines")
    print(f"[INFO] Kích thước file: {file_size_mb:.2f} MB")
    print("=" * 80)


if __name__ == "__main__":
    export_project()
