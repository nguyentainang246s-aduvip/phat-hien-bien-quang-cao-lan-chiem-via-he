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
| **Ngưỡng confidence AI** | 25% (đồng bộ theo `configs/settings.yaml`) |
| **Thời gian xác nhận liên tục** | `confirm_seconds` = 3.0 giây |
| **Model** | `models/best.onnx` (ONNX Runtime CPU AVX2) |

---

## KẾT QUẢ ĐÁNH GIÁ CHẤT LƯỢNG TOÀN HỆ THỐNG

| Chỉ số Đánh giá | Giá trị Thực Nghiệm | Ý nghĩa thực nghiệm & Khoảng tin cậy |
| :--- | :---: | :--- |
| **True Positives (TP)** | `11` | Số vụ vi phạm thực tế ngoài đời được hệ thống phát hiện chính xác (Version B) |
| **False Positives (FP)** | `0` | Số vụ báo động giả (không có người đi bộ hay xe cộ nào bị bắt nhầm) |
| **False Negatives (FN)** | `3` | Track #4 (conf TB 35.9% < 40%), Track #8 (clip 10s kết thúc tại 2.63s quan sát < 3.0s), Track #13 (ở xa, conf chập chờn); giữ SUSPECTED |
| **True Negatives (TN)** | `2` | Số biển hiệu hợp lệ ngoài mép vỉa hè / gắn tường được phán quyết đúng |
| **System Precision** | **100.00%** | Tỷ lệ cảnh báo của hệ thống là vi phạm thật (Wilson 95% CI: 74.1%–100%) |
| **System Recall (Version B)** | **78.57%** | 11/14 vi phạm thực tế ngoài đời (Wilson 95% CI: 52.4%–92.4%) |
| **System Recall (Version A - ROI cũ)** | **71.43%** | 10/14 vi phạm thực tế (Wilson 95% CI: 45.4%–88.3%; Standee #3 đè 66.0% nhưng chân đế ngoài ROI, xếp NORMAL là FN) |
| **System F1-Score** | **88.00%** | Điểm cân bằng điều hòa tối ưu sau toàn bộ chuỗi lọc (Version B) |
| **Cảnh báo sai trong mẫu** | **0 cảnh báo sai / 30s** | Không phát sinh cảnh báo rác trên 30s mẫu thử nghiệm |
| **Tốc độ xử lý bình quân** | **31.3 – 39.2 FPS** | Pipeline Throughput trên CPU Intel Core (ổn định: 38.1 – 43.8 FPS; tần suất suy luận ~10.4–13.1 Hz; latency p50 63.7 ms, mean 62.6 ms; loại trừ frame khởi động) |

*(Báo cáo chi tiết từng track ID và ảnh crop bằng chứng: xem tại `reports/BAO_CAO_THUC_NGHIEM_VIDEO_THAT.md`)*
