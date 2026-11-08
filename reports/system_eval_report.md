# BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG TOÀN HỆ THỐNG (SYSTEM-LEVEL METRICS)
## Giai đoạn: Tuần 9–11 | Mô hình: YOLOv8n (v13_clean) + ByteTrack + Temporal Verifier
### Trích xuất chính thức từ `reports/system_eval_results.json` và `reports/ground_truth_events_cctv.csv` (Cập nhật ngày 03/11/2026)

---

> **Phương pháp:** Chạy toàn bộ pipeline (AI Detection + ByteTrack + Spatial Rule Engine + Temporal Verifier) trên bộ dữ liệu video camera giám sát thực địa (720 frames, 3 video CCTV tại Hà Nội) với vùng vỉa hè (ROI) được vẽ và hiệu chuẩn thực tế.
> 
> **Phân biệt với Model-level Metrics:** mAP/Precision/Recall từ Ultralytics chỉ đo khả năng **phát hiện vật thể "biển hiệu"** trong ảnh tĩnh. Các chỉ số dưới đây đo khả năng **phán quyết đúng "LẤN CHIẾM VỈA HÈ" theo chuỗi thời gian** — bao gồm cả logic hình học chân đế tiếp đất, tỷ lệ đè vỉa hè, và bộ lọc thời gian loại bỏ người đi bộ/rung lắc.

### 1. Cấu hình thực nghiệm

| Thông số | Giá trị |
| :--- | :--- |
| **Nguồn dữ liệu đánh giá** | 3 video CCTV thực tế: Camera 1 (Phố Huế / Hàng Bài), Camera 2 (Phố Bạch Mai), Camera 3 (Phố Trần Đại Nghĩa) |
| **Tổng số frames kiểm thử** | 720 frames (30.0 giây) |
| **Tổng số đối tượng theo dõi** | 18 lượt đối tượng (Track IDs) — gồm 14 vi phạm thực tế (GT) và 2 biển hiệu hợp lệ (GT) |
| **Ngưỡng diện tích đè vỉa hè (Threshold)** | 30% |
| **Ngưỡng độ tin cậy AI Detector** | 25% (đồng bộ theo `configs/settings.yaml`) |
| **Thời gian xác nhận liên tục** | `confirm_seconds = 3.0s` (kèm bộ lọc đứng yên liên tục $\ge 2.0s$) |
| **Mô hình AI** | `models/best.onnx` (ONNX Runtime 1.30.0 CPU AVX2, `frame_skip = 2`) |

---

## 2. KẾT QUẢ ĐÁNH GIÁ CHẤT LƯỢNG TOÀN HỆ THỐNG (A/B COMPARISON)

| Chỉ số Đánh giá | Phiên bản B (Chính thức - Mở rộng ROI) | Phiên bản A (Baseline ROI) | Ý nghĩa thực nghiệm & Căn cứ đối chiếu |
| :--- | :---: | :---: | :--- |
| **True Positives (TP)** | **12** | **11** | Số vụ vi phạm thực tế ngoài đời được hệ thống phát hiện chính xác |
| **False Positives (FP)** | **2** | **2** | Cảnh báo sai (Camera 3: Track #6 conf 59.6% và Track #7 conf 41.5% ngoài GT) |
| **False Negatives (FN)** | **2** | **3** | Bỏ sót (Camera 2: Track #23 và #33 ở xa, conf thấp < 40%, giữ `SUSPECTED`) |
| **True Negatives (TN)** | **2** | **2** | Số biển hiệu hợp lệ ngoài mép vỉa hè / gắn tường được phán quyết đúng |
| **System Precision** | **85.71%** | **84.62%** | Tỷ lệ cảnh báo của hệ thống là vi phạm thật: $\frac{TP}{TP + FP}$ |
| **System Recall** | **85.71%** | **78.57%** | Tỷ lệ vi phạm thật được phát hiện: $\frac{TP}{TP + FN}$ |
| **System F1-Score** | **85.71%** | **81.48%** | Điểm cân bằng điều hòa tối ưu sau toàn bộ chuỗi lọc |
| **Throughput bình quân** | **36.1 – 51.2 FPS** | **36.1 – 51.2 FPS** | Tốc độ thông lượng toàn pipeline trên CPU Intel Core i5 |

---

## 3. PHÂN BỔ CHI TIẾT THEO TỪNG CAMERA THỰC ĐỊA (PHIÊN BẢN B)

| Video / Camera thực địa | Vi phạm thực tế (GT) | Phát hiện đúng (TP) | Báo sai (FP) | Bỏ sót (FN) | Precision | Recall |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Camera 1: Phố Huế / Hàng Bài** (`video test.mp4`) | 4 vụ | 4 vụ | 0 vụ | 0 vụ | **100.0%** | **100.0%** |
| **Camera 2: Phố Bạch Mai** (`videotesst2.mp4`) | 5 vụ | 3 vụ | 0 vụ | 2 vụ | **100.0%** | **60.00%** |
| **Camera 3: Phố Trần Đại Nghĩa** (`video test3.mp4`) | 5 vụ | 5 vụ | 2 vụ | 0 vụ | **71.43%** | **100.0%** |
| **TỔNG HỢP TOÀN HỆ THỐNG (Version B)** | **14 vụ** | **12 vụ** | **2 vụ** | **2 vụ** | **85.71%** | **85.71%** |

*(Ghi chú lịch sử: Bản báo cáo ngày 14/10/2026 ghi nhận số liệu sơ bộ TP=11/FN=3/FP=0 trên bản ROI cũ; bản cập nhật này đã đồng bộ hóa 100% với file JSON đánh giá hệ thống `reports/system_eval_results.json` và bảng Ground Truth `reports/ground_truth_events_cctv.csv`).*
