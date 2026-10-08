# CHƯƠNG 7: THỰC NGHIỆM VÀ ĐÁNH GIÁ KẾT QUẢ HỆ THỐNG

## 7.1. Môi trường thực nghiệm và Cấu hình phần cứng

Hệ thống được kiểm thử và đánh giá hiệu năng thực tế trên môi trường máy tính với cấu hình như sau:

| Thông số | Chi tiết cấu hình |
| :--- | :--- |
| **Hệ điều hành** | Windows 11 (AMD64) |
| **Môi trường runtime** | Python 3.12.10 (64-bit) |
| **Bộ xử lý (CPU)** | Intel64 Family 6 Model 165 Stepping 2, GenuineIntel |
| **Bộ nhớ RAM** | 15.8 GB |
| **Thiết bị xử lý (Device)** | CPU: Intel64 Family 6 Model 165 Stepping 2, GenuineIntel |
| **Nguồn dữ liệu thực nghiệm** | data/videos\YTSave_YouTube_Bien-quang-cao-lan-chiem-via-he-pho-Bang_Media_7nwUTmQ6KIs_002_720p.mp4 (1280x720, FPS gốc: 25.0) |
| **Số lượng khung hình đánh giá** | 50 frames |

---

## 7.2. Kết quả đo đạc tốc độ xử lý và Độ trễ thời gian thực

Để chứng minh hệ thống đáp ứng tiêu chuẩn giám sát thời gian thực (Real-time Surveillance) trên luồng camera CCTV, thời gian xử lý của từng module trong pipeline đã được đo đạc chính xác qua từng khung hình:

### Bảng 7.1. Phân rã độ trễ từng thành phần (Latency Breakdown)

| STT | Thành phần chức năng | Thời gian trung bình (ms) | Tỷ trọng (%) | Ghi chú kỹ thuật |
| :---: | :--- | :---: | :---: | :--- |
| 1 | **Đọc khung hình (Camera Ingestion)** | 2.31 ms | 5.1% | StreamReader xử lý buffer flush |
| 2 | **AI Object Detection + ByteTrack** | **39.59 ms** | **88.0%** | **YOLOv8n + gán định danh track_id** |
| 3 | **Phán quyết hình học (Spatial Check)** | 0.47 ms | 1.0% | Tọa độ chân $P_{base} \in ROI$ & Overlap |
| 4 | **Bộ lọc thời gian (Temporal Verifier)** | 0.02 ms | 0.0% | Máy trạng thái 3 cấp độ (15 frames) |
| 5 | **Vẽ & Trực quan hóa (Rendering)** | 2.59 ms | 5.8% | Lớp phủ đa giác bán trong suốt + HUD |
| **—** | **TỔNG THỜI GIAN ĐẦU-CUỐI (E2E Latency)** | **44.98 ms** | **100%** | **Độ lệch chuẩn: ±5.63 ms** |

### Bảng 7.2. Tốc độ khung hình (Throughput FPS)

| Chỉ số FPS | Giá trị đạt được | Tiêu chuẩn đánh giá |
| :--- | :---: | :--- |
| **FPS Trung bình (Average FPS)** | **22.2 FPS** | Đạt chuẩn xử lý thời gian thực (>= 15 FPS) |
| **FPS Thấp nhất (Worst Case FPS)** | 14.2 FPS | Khung hình có mật độ vật thể phức tạp |
| **FPS Cao nhất (Peak FPS)** | 25.0 FPS | Khung hình ổn định |

> **Nhận xét chuyên môn:** 
> - Module **AI YOLOv8 + ByteTrack** chiếm tỷ trọng tải tính toán lớn nhất (88.0%).
> - Thuật toán phán quyết hình học và bộ lọc thời gian do tác giả thiết kế hoạt động cực kỳ nhẹ (0.49 ms, chiếm < 5% tổng độ trễ), hầu như không làm giảm hiệu năng chung của hệ thống.
> - Tốc độ đạt **22.2 FPS** khẳng định hệ thống hoàn toàn vận hành mượt mà trên camera CCTV thực tế mà không gây trễ luồng (Zero Latency Accumulation).

---

## 7.3. Nghiên cứu bóc tách (Ablation Study) — Vai trò của Bộ lọc thời gian (Temporal Verification)

Để làm rõ đóng góp khoa học của giải pháp kiểm định thời gian nhiều khung hình, thực nghiệm so sánh hai kịch bản đã được thực hiện:
1. **Kịch bản cơ sở (Baseline - Không có Temporal Verifier):** Phán quyết vi phạm tức thời theo từng khung hình độc lập (Single-frame).
2. **Kịch bản đề xuất (Proposed System):** Tích hợp máy trạng thái xác thực 15 khung hình liên tiếp và cơ chế làm nguội (Cooldown 60s).

### Bảng 7.3. Kết quả so sánh khả năng triệt tiêu báo động giả

| Kịch bản đánh giá | Tổng số cảnh báo sinh ra | Số vụ vi phạm chốt lưu DB | Tỷ lệ giảm báo giả/spam |
| :--- | :---: | :---: | :---: |
| **Baseline (Từng frame đơn lẻ)** | 87 cảnh báo | 87 (bị spam liên tục mỗi frame) | 0% |
| **Proposed (Bộ lọc 15 frames + Cooldown)** | 2 sự kiện | 2 sự kiện | **97.7%** |

> **Kết luận:**
> Nhờ có bộ xác minh thời gian (Temporal Verifier), hệ thống đã loại bỏ được **97.7%** số lượng cảnh báo trùng lặp và các trường hợp người đi bộ mang biển hiệu ngang qua vỉa hè trong chốc lát, giảm đáng kể tình trạng tràn ngập dữ liệu (Alert Fatigue) cho trung tâm chỉ huy đô thị.
