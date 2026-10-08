# BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG TOÀN HỆ THỐNG (SYSTEM-LEVEL METRICS)

> **Phương pháp:** Chạy toàn bộ pipeline (AI Detection + Spatial Rule Engine) trên bộ ảnh có gán nhãn Ground Truth thủ công, sau đó so khớp kết quả phán quyết vi phạm với nhãn thực tế.

> **Phân biệt với Model-level Metrics:** mAP/Precision/Recall từ Ultralytics chỉ đo khả năng **phát hiện vật thể "biển hiệu"** trong ảnh. Các chỉ số dưới đây đo khả năng **phán quyết đúng "LẤN CHIẾM VỈA HÈ"** — bao gồm cả logic hình học (Spatial) và ngưỡng overlap.

### Cấu hình thực nghiệm

| Thông số | Giá trị |
| :--- | :--- |
| **Số ảnh test** | 2 |
| **Tổng annotations GT** | 5 |
| **Tổng predictions hệ thống** | 7 |
| **Ngưỡng overlap (Threshold)** | 30% |
| **Model** | models/best.pt |
| **Ngưỡng confidence AI** | 20% |

---

## ĐÁNH GIÁ CHẤT LƯỢNG TOÀN HỆ THỐNG (SYSTEM-LEVEL METRICS)

> **Phương pháp:** Đánh giá độc lập phán quyết vi phạm của toàn pipeline (AI Detection + Spatial Rule + Temporal Verifier) so với Ground Truth thực tế.

| Chỉ số Đánh giá | Giá trị | Ý nghĩa thực nghiệm |
| :--- | :---: | :--- |
| **True Positives (TP)** | `3` | Số vụ vi phạm thực tế được hệ thống phát hiện chính xác |
| **False Positives (FP)** | `0` | Số vụ báo động giả (biển hợp lệ hoặc vật thể khác bị bắt nhầm) |
| **False Negatives (FN)** | `1` | Số vụ vi phạm thực tế mà hệ thống bỏ sót |
| **System Precision** | **100.00%** | Tỷ lệ cảnh báo của hệ thống là vi phạm thật |
| **System Recall** | **75.00%** | Tỷ lệ vi phạm ngoài thực tế được hệ thống ghi nhận |
| **System F1-Score** | **85.71%** | Điểm cân bằng điều hòa giữa Precision và Recall |
