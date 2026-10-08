# Hệ Thống Giám Sát Biển Hiệu / Biển Quảng Cáo Lấn Chiếm Vỉa Hè Qua CCTV Cố Định

> **Đồ án Tốt nghiệp Kỹ sư / Cử nhân Công nghệ Thông tin - Computer Vision & AI**  
> **Mã đồ án:** DATN20224083  
> **Kiến trúc hệ thống:** 3 Tầng độc lập (Object Detection $\to$ Multi-Object Tracking $\to$ Spatial & Temporal Verification)

---

## 1. Giới thiệu & Kiến trúc Hệ thống

Hệ thống được thiết kế để giải quyết bài toán tự động phát hiện, định danh và lập hồ sơ xử lý hành vi đặt biển hiệu, biển quảng cáo lấn chiếm không gian vỉa hè dành cho người đi bộ thông qua camera an ninh CCTV cố định.

```mermaid
flowchart LR
    A[CCTV / Video RTSP] --> B[StreamReader\nZero-Latency Buffer]
    B --> C[Tầng 1: YOLOv8n\nPhát hiện Bounding Box Biển hiệu]
    C --> D[Tầng 2: ByteTrack\nĐịnh danh Track ID liên tục]
    D --> E[Tầng 3: Spatial Checker\nChân cắm + Overlap Ratio]
    E --> F[Tầng 3: Temporal Verifier\nXác minh thời gian + Cooldown]
    F --> G[Evidence Saver & SQLite DB\nLưu ảnh sạch & Hồ sơ vi phạm]
    G --> H[Web Dashboard\nTheo dõi & Thống kê vi phạm]
```

### Phân tách trách nhiệm kiến trúc (Làm rõ ngữ nghĩa Class Name)
- **Tầng AI (Detection):** Model YOLOv8n được huấn luyện để phát hiện đối tượng vật thể biển hiệu/biển quảng cáo (`signboard`). Model **KHÔNG** làm nhiệm vụ kết luận vi phạm hay không, mà chỉ cung cấp bounding box và tọa độ vật thể với độ chính xác cao ($mAP_{50} = 82.5\%$).
- **Tầng Hình học (Spatial Decision):** Sử dụng thư viện hình học giải tích Shapely để tính toán tỷ lệ giao cắt:
  $$\text{Overlap Ratio} = \frac{\text{Area}(\text{Bounding Box} \cap \text{ROI})}{\text{Area}(\text{Bounding Box})}$$
  Kết hợp với điều kiện điểm tiếp xúc mặt đất (Ground Contact Point - đáy tâm bounding box) nằm trọn trong vùng vỉa hè.
- **Tầng Thời gian (Temporal Verification):** Bộ lọc chuỗi thời gian yêu cầu hành vi lấn chiếm duy trì liên tục $\ge 15$ frames kèm cơ chế dung sai ($K=2$ frames) và cơ chế suy giảm khi che khuất (Occlusion Decay). Điều này triệt tiêu hoàn toàn báo động giả do người cầm biển đi ngang hoặc xe cộ che khuất tạm thời.

---

## 2. Cấu trúc Thư mục Dự án

```
DATN20224083/
├── camera/             # Module đọc luồng video/RTSP tự động kết nối lại & flush buffer
├── configs/            # File cấu hình đa giác vỉa hè (Multi-ROI)
├── dashboard/          # Web dashboard trực quan xem hồ sơ vi phạm (Streamlit & HTTP Server)
├── data/
│   ├── images/         # Ảnh tĩnh kiểm thử
│   ├── videos/         # Video CCTV kiểm thử
│   └── surveillance.db # Cơ sở dữ liệu SQLite lưu vết vi phạm
├── database/           # SQLite Database Manager với schema migration tự động
├── datasets/           # Dữ liệu huấn luyện Roboflow (train / valid / test)
├── detection/          # Wrapper chuẩn hóa đầu ra mô hình YOLOv8
├── evaluation/         # Bộ đo benchmark hiệu năng, sweep threshold và system metrics
├── evidence/           # Module trích xuất và đóng dấu ảnh bằng chứng vi phạm
├── models/             # Trọng số mô hình đã huấn luyện (best.pt)
├── reports/            # Biểu đồ training, báo cáo sweep threshold, benchmark
├── roi/                # Quản lý vùng vỉa hè (Multi-ROI, auto-scale resolution)
├── scripts/            # Script tiện ích, kiểm tra môi trường & bản demo thực nghiệm
│   ├── check_env.py    # Kiểm tra cấu hình môi trường thực thi (Task 01)
│   ├── create_sample_video.py # Sinh video giả lập CCTV phục vụ test
│   ├── detect_only.py  # Nhận diện biển hiệu thuần YOLO không qua ROI
│   ├── train_colab.py  # Script huấn luyện YOLOv8n trên Google Colab GPU T4
│   └── demos/          # Mã nguồn các bài thực nghiệm theo roadmap (Task 02 – Task 21)
├── tests/              # Bộ unit test tự động cho toàn bộ các module
├── tracking/           # ByteTrack tracker và Temporal Verifier
├── utils/              # Bộ đếm FPS và vẽ đồ họa trực quan
├── test_on_image.py    # Công cụ kiểm thử trực quan trên ảnh tĩnh kèm kiểm tra 3 điểm chân đế
├── roi_drawer.py       # Công cụ giao diện đồ họa vẽ vùng vỉa hè bằng chuột
├── requirements.txt    # Danh mục thư viện phụ thuộc
└── main.py             # Điểm khởi chạy thống nhất của toàn hệ thống (Unified Entry Point)
```

---

## 3. Hướng dẫn Cài đặt & Sử dụng

### 3.1. Cài đặt Môi trường
Yêu cầu Python 3.10 – 3.12:
```bash
# Tạo môi trường ảo
python -m venv .venv
.venv\Scripts\activate  # Trên Windows
# source .venv/bin/activate # Trên Linux/macOS

# Cài đặt thư viện
pip install -r requirements.txt
```

### 3.2. Vẽ Vùng Vỉa Hè (Sidewalk ROI)
Khởi động công cụ vẽ ROI cho camera mới hoặc video kiểm thử:
```bash
python roi_drawer.py --source data/videos/test.mp4 --output configs/roi_test.json
```
- Click chuột trái để chấm các điểm quanh vỉa hè.
- Nhấn `n` để chuyển sang vẽ vỉa hè tiếp theo (hỗ trợ nhiều vỉa hè trái/phải).
- Nhấn `s` để lưu file cấu hình JSON.
- Nhấn `q` để thoát.

### 3.3. Khởi chạy Giám sát Thời gian thực
```bash
# Giám sát video có hiển thị màn hình trực quan
python main.py --source data/videos/test.mp4 --config configs/roi_test.json --view

# Giám sát camera CCTV RTSP ở chế độ nền (Headless Mode 24/7)
python main.py --source "rtsp://admin:password@192.168.1.100:554/stream1" --config configs/roi_cam1.json --headless
```

### 3.4. Xem Bảng điều khiển Quản lý Vi phạm (Dashboard)
Hệ thống cung cấp 2 phương thức dashboard:
1. **Web Dashboard Độc lập (Zero Dependency):**
   ```bash
   python -m dashboard.web_app
   ```
   Truy cập: `http://localhost:5000`
2. **Streamlit Analytics Dashboard:**
   ```bash
   streamlit run dashboard/app.py
   ```
   Truy cập: `http://localhost:8501`

### 3.5. Chạy Đánh giá Thực nghiệm & Benchmark (Phục vụ Báo cáo ĐATN)
```bash
# Thực nghiệm quét ngưỡng diện tích (Threshold Sweep)
python evaluation/sweep_threshold.py

# Đo đạc hiệu năng FPS và độ trễ từng module (Latency Breakdown)
python evaluation/benchmark.py --num-frames 100

# Chạy toàn bộ test suite kiểm thử
python -m unittest discover tests
```

---

## 4. Kết quả Huấn luyện & Đánh giá (Metrics Summary)

- **Model Detection Layer (YOLOv8n - 3.01M params):**
  - Tập dữ liệu: 369 ảnh (336 train, 33 val), 1 class `signboard`.
  - $mAP_{50}$: **82.5%** | $mAP_{50-95}$: **59.0%**
  - Precision: **78.2%** | Recall: **79.5%**
- **System Decision Layer (Threshold 30%):**
  - Ngưỡng tối ưu F1-Score: **30% Overlap Ratio** (xem chi tiết tại `reports/threshold_sweep_report.md`).
  - Tốc độ xử lý: **> 30–45 FPS** trên GPU phổ thông, đáp ứng xử lý thời gian thực cho camera CCTV.
