"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Roboflow Dataset Downloader (Hỗ trợ Dataset Version 12 Mới Nhất)
==============================================================================
"""

import os
import sys
import argparse
from roboflow import Roboflow

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

DEFAULT_API_KEY = os.environ.get("ROBOFLOW_API_KEY")

def download_signboard_dataset(version_num: int = 12, api_key: str = None, location: str = None, overwrite: bool = False):
    key = api_key or os.environ.get("ROBOFLOW_API_KEY") or DEFAULT_API_KEY
    if not key:
        print("[LỖI BẢO MẬT] Chưa có API key Roboflow!")
        print("Vui lòng truyền --api-key hoặc thiết lập biến môi trường ROBOFLOW_API_KEY")
        sys.exit(1)

    target_dir = os.path.abspath(location or f"datasets/v{version_num}")
    
    # Nếu thư mục đích đã tồn tại nhưng chưa có data.yaml, bắt buộc bật overwrite để Roboflow thực sự tải
    yaml_check = os.path.join(target_dir, "data.yaml")
    force_overwrite = overwrite or (not os.path.exists(yaml_check))

    rf = Roboflow(api_key=key)
    project = rf.workspace("tai-nang-nguyen-duc").project("sidewalk-signboard-detection-1")
    version = project.version(version_num)

    print(f"[*] Đang kết nối Roboflow: Project '{project.name}' (Version {version_num})")
    print(f"[*] Thư mục đích: {target_dir}")
    print(f"[*] Bắt đầu tải và giải nén (overwrite={force_overwrite})...")
    
    dataset = version.download("yolov8", location=target_dir, overwrite=force_overwrite)
    print(f"[OK] Tải và giải nén dữ liệu thành công! Thư mục dataset: {dataset.location}")
    return dataset

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tải tập dữ liệu từ Roboflow")
    parser.add_argument("--version", type=int, default=12, help="Phiên bản dataset (mặc định: 12)")
    parser.add_argument("--api-key", type=str, default=DEFAULT_API_KEY, help="Roboflow API Key")
    parser.add_argument("--location", type=str, default=None, help="Thư mục lưu trữ")
    parser.add_argument("--overwrite", action="store_true", help="Ghi đè dữ liệu nếu đã tồn tại")
    args = parser.parse_args()

    download_signboard_dataset(version_num=args.version, api_key=args.api_key, location=args.location, overwrite=args.overwrite)
