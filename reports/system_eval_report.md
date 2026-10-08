# BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG TOÀN HỆ THỐNG (SYSTEM-LEVEL METRICS)

> **Phương pháp:** Chạy toàn bộ pipeline (AI Detection + ByteTrack + Spatial Rule Engine + Temporal Verifier) trên bộ dữ liệu video camera giám sát thực địa (720 frames, 3 video CCTV tại Hà Nội) với vùng vỉa hè (ROI) được vẽ và hiệu chuẩn thực tế.
> 
> **Phân biệt với Model-level Metrics:** mAP/Precision/Recall từ Ultralytics chỉ đo khả năng **phát hiện vật thể "biển hiệu"** trong ảnh tĩnh. Các chỉ số dưới đây đo khả năng **phán quyết đúng "LẤN CHIẾM VỈA HÈ" theo chuỗi thời gian** — bao gồm cả logic hình học chân đế tiếp đất, tỷ lệ đè vỉa hè, và bộ lọc thời gian loại bỏ người đi bộ/rung lắc.

### Cấu hình thực nghiệm

| Thông số | Giá trị |
| :--- | :--- |
| **Nguồn dữ liệu đánh giá** | 3 video CCTV thực tế (`video test.mp4`, `videotesst2.mp4`, `video test3.mp4`) |
| **Tổng số frames kiểm thử** | 720 frames (30.0 giây) |
| **Tổng số biển hiệu theo dõi** | 16 lượt đối tượng (Track IDs) |
| **Ngưỡng overlap (Threshold)** | 30% |
| **Ngưỡng confidence AI** | 20% |
| **Thời gian xác nhận liên tục** | 15 frames / 3.0 giây |
| **Model** | `models/best.onnx` (ONNX Runtime CPU AVX2) |

---

## KẾT QUẢ ĐÁNH GIÁ CHẤT LƯỢNG TOÀN HỆ THỐNG

| Chỉ số Đánh giá | Giá trị Thực Nghiệm | Ý nghĩa thực nghiệm |
| :--- | :---: | :--- |
| **True Positives (TP)** | `11` | Số vụ vi phạm thực tế ngoài đời được hệ thống phát hiện chính xác |
| **False Positives (FP)** | `0` | Số vụ báo động giả (không có người đi bộ hay xe cộ nào bị bắt nhầm) |
| **False Negatives (FN)** | `1` | Số vụ vi phạm bị bỏ sót (do ở xa hoặc bị người đi qua che khuất) |
| **True Negatives (TN)** | `3` | Số biển hiệu hợp lệ ngoài mép vỉa hè được hệ thống phán quyết đúng |
| **System Precision** | **100.00%** | Tỷ lệ cảnh báo của hệ thống là vi phạm thật |
| **System Recall** | **91.67%** | Tỷ lệ vi phạm ngoài thực tế được hệ thống ghi nhận |
| **System F1-Score** | **95.65%** | Điểm cân bằng điều hòa tối ưu sau toàn bộ chuỗi lọc |
| **False Alarm Rate (FA/h)** | **0.0 cảnh báo/giờ** | Không phát sinh cảnh báo rác, giảm tải tối đa cho cán bộ |
| **Tốc độ xử lý bình quân** | **30.4 – 39.3 FPS** | Xử lý Real-time trực tiếp trên CPU, không đòi hỏi GPU đắt tiền |

*(Báo cáo chi tiết từng track ID và ảnh crop bằng chứng: xem tại `reports/BAO_CAO_THUC_NGHIEM_VIDEO_THAT.md`)*
