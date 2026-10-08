import os
import sys
from roboflow import Roboflow

def download_signboard_dataset():
    api_key = os.environ.get("ROBOFLOW_API_KEY")
    if not api_key:
        print("[LỖI BẢO MẬT] Chưa thiết lập biến môi trường ROBOFLOW_API_KEY!")
        print("Vui lòng thiết lập trước khi chạy:")
        print("  Windows PowerShell: $env:ROBOFLOW_API_KEY=\"<your_api_key>\"")
        print("  Linux/macOS:        export ROBOFLOW_API_KEY=\"<your_api_key>\"")
        sys.exit(1)

    rf = Roboflow(api_key=api_key)
    project = rf.workspace("tai-nang-nguyen-duc").project("sidewalk-signboard-detection-1")
    version = project.version(8)
    
    target_dir = os.path.abspath("datasets/v8")
    print(f"Đang tải dataset Roboflow v8 về thư mục: {target_dir}...")
    dataset = version.download("yolov8", location=target_dir)
    print("Tải dữ liệu hoàn tất! Thư mục dataset:", dataset.location)

if __name__ == "__main__":
    download_signboard_dataset()
