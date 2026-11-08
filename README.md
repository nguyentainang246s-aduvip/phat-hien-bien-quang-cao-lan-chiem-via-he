# Hệ Thống Giám Sát Biển Hiệu / Biển Quảng Cáo Lấn Chiếm Vỉa Hè Qua CCTV Cố Định

> **Đồ án Tốt nghiệp Kỹ sư / Cử nhân Công nghệ Thông tin - Computer Vision & Edge AI**  
> **Mã sinh viên / Mã đề tài:** DATN20224083  
> **Phiên bản hệ thống:** Version 2.0 (Edge-Ready Architecture & Zero-Retraining Enhancements)  
> **Căn cứ pháp lý tham chiếu:** Nghị định 168/2024/NĐ-CP Điều 12 (Xử phạt vi phạm hành vi đặt, treo biển hiệu, biển quảng cáo lấn chiếm lòng đường, hè phố)

---

## 1. Giới thiệu & Kiến trúc Hệ thống

Hệ thống được thiết kế để tự động giám sát, phát hiện dấu hiệu nghi vấn lấn chiếm vỉa hè và lập hồ sơ hỗ trợ Cán bộ Đội Quản lý Trật tự Đô thị thẩm định phạt nguội thông qua hệ thống camera an ninh CCTV cố định.

```mermaid
flowchart TD
    A["Camera CCTV / Video RTSP"] --> B["StreamReader\n(Zero-Latency Frame Buffer)"]
    B --> C["Tầng 1: YOLO Detector (v13_clean)\nPhát hiện Bounding Box Biển hiệu"]
    C --> D["Tầng 2: Multi-Object Tracking\n(ByteTrack + Coasting + Static Stitching)"]
    D --> E["Tầng 3: Motion Filter\nLoại trừ Xe cộ & Người bưng bê biển (v > 35px/s)"]
    E --> F["Tầng 4: Spatial Reasoning (Hybrid Checker)\n① 3-Point Ground Contact + ② Overlap Ratio ≥ 30%"]
    F --> G["Tầng 5: Temporal Verification Streak\nĐứng yên liên tục ≥ 3.0s | Conf TB ≥ 40%"]
    G --> H["Lập Hồ Sơ Bằng Chứng Vi Phạm\n(Tự động làm mờ mặt + Watermark thời gian)"]
    H --> I[("SQLite Database\n(surveillance.db)")]
    I --> J["Web Dashboard Phạt Nguội\n(Cán bộ Đô thị Duyệt / Bác bỏ Hồ sơ)"]
```

### 5 Tầng Phân Tách Trách Nhiệm Chặt Chẽ:
1. **Tầng AI Detection (YOLOv8n - v13_clean):** Nhận diện vị trí không gian của các vật thể biển hiệu (`signboard`). Mô hình **không tự ý kết luận vi phạm**, chỉ cung cấp hộp giới hạn chính xác ($mAP_{50} = 88.2\%$).
2. **Tầng Tracking Chống Chớp Tắt (Anti-Flicker Tracking):** Cấp phát `Track ID`, sử dụng **Visual Coasting** (đệm hiển thị khi bị che khuất ngắn) và **Spatial Static Stitching** (hàn gắn lại ID cũ cho biển tĩnh khi xuất hiện lại).
3. **Tầng Lọc Chuyển Động (Motion Filtering):** Đo đạc vận tốc tức thời và độ dời tâm trong cửa sổ trượt 1.0 giây để loại trừ triệt để xe buýt/xe tải dán quảng cáo và người bưng bê biển (`[BỎ QUA] DI CHUYỂN`).
4. **Tầng Hình Học Không Gian (Spatial Reasoning):** 
   - **Quy tắc tiếp đất 3 điểm (3-Point Ground Contact):** Chân đế phải cắm trên mặt vỉa hè (loại bỏ biển treo tầng 2 hoặc biển trong nhà).
   - **Tỷ lệ diện tích đè (Overlap Ratio):** $\frac{\text{Area}(\text{Box} \cap \text{ROI})}{\text{Area}(\text{Box})} \ge 30\%$.
5. **Tầng Xác Thực Thời Gian & Thẩm Định Người - Máy (Temporal & Human-in-the-Loop):**
   - Đòi hỏi hành vi lấn chiếm tĩnh liên tục $\ge 3.0$ giây thực.
   - Hồ sơ được lưu ở trạng thái **`PENDING` (Chờ duyệt)** để Cán bộ Trật tự Đô thị xem xét bằng chứng và ra quyết định xử phạt hành chính (`APPROVED` hoặc `REJECTED`).

---

## 2. Các Kỹ Thuật Nâng Cao Mới Tích Hợp (Zero-Retraining Pipeline)

Toàn bộ các giải pháp tối ưu được can thiệp trực tiếp vào tầng logic bám vết và xử lý thời gian thực, **tăng ngay 5 – 10% F1-Score thực nghiệm mà không cần tốn công gán nhãn hay train lại mô hình**:

* **Hysteresis Dual-Thresholding:** Ngưỡng kích hoạt cao ($0.22 - 0.25$) để lọc nhiễu ban đầu; ngưỡng duy trì thấp ($0.08$) để bám vết bền bỉ khi bị che khuất hoặc ánh sáng thay đổi.
* **Track Coasting & Visual Persistence:** Đệm hiển thị 16 khung hình (~2.2 giây trên Web) khi vật thể bị người/xe che khuất chớp nhoáng, chấm dứt hoàn toàn hiện tượng biển bị chớp tắt.
* **Spatial Static Stitching:** Lưu vết tọa độ biển tĩnh trong 180 frames; tự động hàn gắn lại đúng ID cũ khi biển lộ ra sau che khuất dài, không làm reset bộ đếm thời gian vi phạm.
* **Containment De-duplication:** Khử xung đột 2 bounding box lồng nhau trên cùng 1 biển ($IoS \ge 75\%$), đảm bảo mỗi biển chỉ có duy nhất 1 nhãn ổn định.
* **Memory-Aware Static Thresholding:** Giữ bám vết ổn định cho cả các biển nhỏ ở hậu cảnh xa (như Track #12) ngay cả khi độ tin cậy dao động quanh ngưỡng kích hoạt.
* **Tự động bắt cầu môi trường ảo (`.venv`):** Tự động phát hiện và chuyển tiếp môi trường thực thi trong `main.py` và `dashboard/web_app.py`, ngăn chặn lỗi thiếu thư viện `ultralytics`.

---

## 3. Cấu Trúc Thư Mục Dự Án

```
DATN20224083/
├── camera/             # Đọc luồng video/RTSP tự động kết nối lại & flush buffer
├── configs/            # Tệp cấu hình đa giác vỉa hè (Multi-ROI) & tham số hệ thống
│   ├── settings.yaml          # Tham số toàn cục: tracking, motion, temporal, evidence
│   ├── bytetrack_custom.yaml  # Cấu hình tối ưu cho ByteTrack biển hiệu tĩnh
│   ├── video_ground_truth.json# Nhãn chuẩn thực nghiệm 3 video CCTV
│   └── roi_*.json             # Tọa độ đa giác vỉa hè cho từng camera
├── dashboard/          # Web Dashboard Giám sát & Quản lý Phạt nguội
│   ├── web_app.py      # Máy chủ HTTP Web Dashboard độc lập (Zero Dependency)
│   └── app.py          # Dashboard giao diện Streamlit thay thế
├── data/
│   ├── videos/         # 6 Video CCTV thực tế kiểm thử (video test, videotesst2, ...)
│   └── surveillance.db # Cơ sở dữ liệu SQLite lưu trữ vết vi phạm
├── database/           # SQLite Database Manager với schema migration tự động
├── datasets/           # Dữ liệu huấn luyện YOLO v13_clean (2.674 ảnh, 8.097 box)
├── detection/          # Wrapper chuẩn hóa đầu ra mô hình YOLOv8
├── evaluation/         # Đánh giá F1-score, Confusion Matrix, Sweep threshold & Benchmark
├── evidence/           # Module trích xuất, làm mờ mặt (Privacy) và đóng dấu ảnh vi phạm
├── models/             # Trọng số mô hình đã huấn luyện (best.pt & best.onnx)
├── reports/            # Báo cáo tiến độ Tuần 4–8, 9–11, 12–13, biểu đồ đánh giá
├── roi/                # Quản lý đa giác vỉa hè (Multi-ROI, auto-scale resolution)
├── scripts/            # Script tiện ích xuất báo cáo DOCX, kiểm toán nhãn, benchmark
├── tests/              # Bộ 21 unit test và integration test tự động (pytest)
├── tracking/           # ObjectTracker, TemporalVerifier và MotionFilter
├── utils/              # Bộ đếm FPS, vẽ đồ họa bounding box và HUD badge
├── requirements.txt    # Danh mục thư viện phụ thuộc
└── main.py             # Điểm khởi chạy thống nhất (Unified Entry Point)
```

---

## 4. Hướng Dẫn Cài Đặt & Sử Dụng

### 4.1. Cài đặt Môi trường
Yêu cầu Python 3.10 – 3.12:
```bash
# 1. Tạo môi trường ảo
python -m venv .venv

# 2. Kích hoạt môi trường ảo
.\.venv\Scripts\activate      # Trên Windows
# source .venv/bin/activate   # Trên Linux/macOS

# 3. Cài đặt thư viện phụ thuộc
pip install -r requirements.txt
```

---

### 4.2. Khởi Chạy Web Dashboard Quản Lý Phạt Nguội (Khuyên dùng)
Khởi chạy bảng điều khiển trung tâm tại cổng 8501:
```bash
python main.py --mode dashboard --port 8501
```
* Mở trình duyệt truy cập: **`http://localhost:8501`**
* **Trình phát AI trực tiếp (Live AI Player):** Xem trực tiếp video/RTSP kèm nhận diện bounding box, bộ lọc chuyển động, HUD thống kê. Hỗ trợ tùy chỉnh tức thì:
  * **Tần suất (Frame Skip):** `Skip 0` (Mượt từng khung hình), `Skip 1` hoặc `Skip 2`.
  * **Độ nét suy luận:** `640px`, `960px` hoặc `1280px`.
  * **Độ nhạy AI:** `15% - Cao`, `25% - Chuẩn` hoặc `40% - Khắt khe`.
* **Hồ sơ Phạt nguội (Human-in-the-Loop):** Xem chi tiết ảnh phóng to vi phạm, ảnh toàn cảnh có tem pháp lý; duyệt (`APPROVED`) hoặc bác bỏ (`REJECTED`) hồ sơ vi phạm.
* **Studio Vẽ ROI Vỉa Hè Trực Tuyến:** Vẽ và chỉnh sửa đa giác vỉa hè trực tiếp trên trình duyệt Web.

---

### 4.3. Giám Sát Trực Tiếp Qua Màn Hình OpenCV
```bash
# Giám sát video mẫu (độ nét chuẩn 960px, tối ưu hiển thị)
python main.py --mode monitor --source data/videos/videotesst2.mp4 --imgsz 960

# Giám sát luồng camera giao thông RTSP 24/7 ở chế độ nền (Headless)
python main.py --mode monitor --source "rtsp://admin:pass@192.168.1.10:554/stream1" --config configs/roi_cam1.json --headless
```

---

### 4.4. Cấu Hình Tối Ưu Cho Thiết Bị Biên Yếu (Raspberry Pi 4 / Jetson Nano)
Do biển hiệu là vật thể tĩnh, thiết bị biên không cần chạy 24 FPS liên tục. Sử dụng chiến lược **Suy luận ngắt quãng (1 – 2 FPS)** kết hợp **Độ phân giải cao 960px**:

```bash
python main.py \
  --mode monitor \
  --source rtsp://admin:pass@192.168.1.10:554/stream1 \
  --imgsz 960 \
  --skip-frames 11 \
  --onnx \
  --sync-fps \
  --headless
```
* **`--imgsz 960`**: Bắt trọn các biển hiệu nhỏ và mờ ở hậu cảnh xa.
* **`--skip-frames 11`**: Quét 2 lần/giây (ở video 24 FPS), giảm tải CPU $12\times$. Mức tải CPU Raspberry Pi 4 chỉ **~30%**, máy chạy mát mẻ ($<50^\circ\text{C}$) bền bỉ 24/7.
* **`--onnx`**: Tăng tốc phần cứng bằng ONNX Runtime CPU AVX2/NEON.
* **`--headless`**: Tắt giao diện đồ họa, tiết kiệm 20% RAM và CPU.

---

## 5. Kết Quả Huấn Luyện & Đánh Giá Thực Nghiệm

### 5.1. Mô hình YOLOv8n (Bộ dữ liệu `v13_clean`)
* **Quy mô tập dữ liệu:** **2.674 ảnh** (2.417 train, 153 val, 104 test), **8.097 bounding box** được chuẩn hóa và kiểm toán sạch 100%, 201 ảnh nền (negative samples).
* **Độ chính xác trên tập Validation:**
  * $mAP_{50}$: **88.2%** | $mAP_{50-95}$: **66.1%**
  * Precision: **84.3%** | Recall: **82.9%**
* **Kích thước mô hình:** Chỉ **3.01 triệu tham số** (dung lượng 6.2 MB bản PyTorch, 11.8 MB bản ONNX FP32, ~3 MB bản INT8), cực kỳ gọn nhẹ cho thiết bị biên.

### 5.2. Đánh giá Thực nghiệm trên 6 Video CCTV Thực tế
* **Hiện tượng nhảy ID & chớp tắt:** Giảm từ 75 frames/video xuống **0 frame (Duplicate frames = 0)**.
* **Tỷ lệ F1-Score toàn hệ thống:** Đạt **91.4%** trên bộ dữ liệu kiểm thử thực tế đa dạng góc nhìn, ánh sáng ban ngày và ban đêm.

---

## 6. Chạy Kiểm Thử Tự Động (Automated Testing)

Toàn bộ hệ thống được bảo vệ bởi bộ kiểm thử tự động toàn diện:
```bash
pytest tests/
```
**Kết quả kiểm thử:** `21 passed, 1 skipped (100% PASS)` bao gồm kiểm tra bám vết, lọc chuyển động, khử trùng lặp, cơ sở dữ liệu SQLite và giao diện dòng lệnh CLI.

---

## 7. Căn Cứ Pháp Lý & Bản Quyền

* **Căn cứ pháp lý:** Tham chiếu Điều 12 Nghị định 168/2024/NĐ-CP của Chính phủ quy định xử phạt vi phạm hành chính trong lĩnh vực trật tự, an toàn giao thông đường bộ đối với hành vi sử dụng trái phép lòng đường, hè phố để đặt, treo biển hiệu, biển quảng cáo.
* **Quyền riêng tư:** Hệ thống tích hợp sẵn tính năng tự động làm mờ khuôn mặt người đi đường trên mọi ảnh chụp bằng chứng nhằm tuân thủ các quy định bảo vệ dữ liệu cá nhân.
* **Tác giả đề tài:** Nguyễn Đức Tài Năng (Mã SV: 20224083) — Đồ án Tốt nghiệp CNTT.
