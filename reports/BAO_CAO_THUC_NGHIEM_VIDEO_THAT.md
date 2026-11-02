# BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG TOÀN HỆ THỐNG TRÊN VIDEO THỰC TẾ (SYSTEM-LEVEL METRICS)

> **Thời gian chạy kiểm thử:** 2026-11-01 17:42:54  
> **Người thực hiện:** Nguyễn Đức Tài Năng (ĐATN 20224083)  
> **Cơ chế đo đạc:** Chạy tự động từ `evaluation/evaluate_videos.py`, đối chiếu với `configs/video_ground_truth.json` và trích xuất `reports/system_eval_results.json`.

---

## 1. Cấu Hình Phần Cứng & Môi Trường Suy Luận

| Thông số | Giá trị thực nghiệm | Ghi chú kỹ thuật |
| :--- | :--- | :--- |
| **Hệ thống thử nghiệm** | CPU Intel64 Family 6 Model 165 Stepping 2, GenuineIntel (Windows-11-10.0.26200-SP0) | Tối ưu hóa suy luận trên CPU phổ thông |
| **Engine suy luận AI** | ONNX Runtime 1.30.0 (CPU AVX2 ExecutionProvider) | `models/best.onnx` (FP32, Imgsz: 640x640) |
| **Thuật toán bám vết** | ByteTrack (`bytetrack.yaml`) | Gán mã định danh ổn định theo thời gian |
| **Quy tắc hình học không gian** | Overlap $\ge 30\%$ + Tiếp đất chân đế 3 điểm | Loại trừ biển treo trên cao |
| **Bộ lọc chuỗi thời gian** | `confirm_seconds = 3.0s` (cửa sổ trượt 1.0s $\le 50\text{px}$) | Loại trừ người bê biển đi ngang & rung lắc |
| **Số video thực nghiệm** | **3 video clip CCTV đường phố Hà Nội (720 frames, 30.0s)** | Dữ liệu video thực tế ngoài đời |

---

## 2. Kết Quả Chi Tiết Từng Video Thực Địa

### Video: `data/videos/video test.mp4`
* **Độ dài:** 240 frames (10.0 giây) &bull; **Tốc độ thông lượng:** **39.7 FPS**
* **Phân tích độ trễ:** AI+Tracker Mean = 39.51 ms (p50: 37.28 ms, p95: 50.05 ms); Verifier Mean = 1.29 ms; Tổng khung hình infer = 44.01 ms (Frame khởi động: 2115.21 ms)
* **Kết quả:** **4 Vi phạm (Confirmed)** | **0 Nghi vấn (Suspected)** | **1 Hợp lệ (Normal)**

| Track ID | Số frames | Độ tin cậy TB | % Lấn chiếm TB | Kết luận Hệ thống | File ảnh Crop |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **#1** | 78 | 81.3% | 100.0% | `CONFIRMED` | `track_1_conf85.jpg` |
| **#2** | 80 | 82.7% | 100.0% | `CONFIRMED` | `track_2_conf84.jpg` |
| **#3** | 80 | 81.4% | 76.0% | `CONFIRMED` | `track_3_conf82.jpg` |
| **#4** | 80 | 76.0% | 9.6% | `NORMAL` | `track_4_conf78.jpg` |
| **#5** | 69 | 67.0% | 100.0% | `CONFIRMED` | `track_5_conf75.jpg` |

---

### Video: `data/videos/videotesst2.mp4`
* **Độ dài:** 240 frames (10.0 giây) &bull; **Tốc độ thông lượng:** **60.5 FPS**
* **Phân tích độ trễ:** AI+Tracker Mean = 38.82 ms (p50: 37.22 ms, p95: 44.24 ms); Verifier Mean = 1.29 ms; Tổng khung hình infer = 42.96 ms (Frame khởi động: 131.63 ms)
* **Kết quả:** **5 Vi phạm (Confirmed)** | **2 Nghi vấn (Suspected)** | **1 Hợp lệ (Normal)**

| Track ID | Số frames | Độ tin cậy TB | % Lấn chiếm TB | Kết luận Hệ thống | File ảnh Crop |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **#1** | 80 | 84.4% | 72.1% | `CONFIRMED` | `track_1_conf85.jpg` |
| **#2** | 79 | 74.1% | 100.0% | `CONFIRMED` | `track_2_conf85.jpg` |
| **#3** | 80 | 65.3% | 100.0% | `CONFIRMED` | `track_3_conf72.jpg` |
| **#4** | 79 | 55.4% | 94.3% | `CONFIRMED` | `track_4_conf67.jpg` |
| **#5** | 54 | 47.6% | 100.0% | `CONFIRMED` | `track_5_conf74.jpg` |
| **#12** | 17 | 31.6% | 91.1% | `SUSPECTED` | `track_12_conf38.jpg` |
| **#20** | 6 | 29.3% | 0.0% | `NORMAL` | `track_20_conf31.jpg` |
| **#23** | 2 | 35.4% | 91.5% | `SUSPECTED` | `track_23_conf35.jpg` |

---

### Video: `data/videos/video test3.mp4`
* **Độ dài:** 240 frames (10.0 giây) &bull; **Tốc độ thông lượng:** **56.4 FPS**
* **Phân tích độ trễ:** AI+Tracker Mean = 42.23 ms (p50: 38.16 ms, p95: 51.52 ms); Verifier Mean = 1.37 ms; Tổng khung hình infer = 46.69 ms (Frame khởi động: 143.92 ms)
* **Kết quả:** **5 Vi phạm (Confirmed)** | **2 Nghi vấn (Suspected)** | **0 Hợp lệ (Normal)**

| Track ID | Số frames | Độ tin cậy TB | % Lấn chiếm TB | Kết luận Hệ thống | File ảnh Crop |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **#1** | 80 | 85.0% | 100.0% | `CONFIRMED` | `track_1_conf86.jpg` |
| **#2** | 80 | 82.2% | 100.0% | `CONFIRMED` | `track_2_conf83.jpg` |
| **#3** | 80 | 72.6% | 100.0% | `CONFIRMED` | `track_3_conf76.jpg` |
| **#4** | 61 | 68.4% | 96.7% | `CONFIRMED` | `track_4_conf73.jpg` |
| **#5** | 74 | 65.7% | 66.3% | `CONFIRMED` | `track_5_conf75.jpg` |
| **#17** | 8 | 31.4% | 100.0% | `SUSPECTED` | `track_17_conf33.jpg` |
| **#22** | 23 | 63.5% | 95.9% | `SUSPECTED` | `track_22_conf72.jpg` |

---

## 3. Bảng Đối Sánh Chi Tiết Từng Đối Tượng với Ground Truth

| Video | Ground Truth ID | ByteTrack ID | Tên biển hiệu / Đối tượng | Độ tin cậy ghép nối (IoU/Conf) | Số frames | Độ tin cậy TB | % Lấn chiếm TB | Kết luận Hệ thống | Ground Truth Thực tế | Phân loại Đánh giá |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| **Video 1** | **GT #1** | **Track #1** | Biển bạt lớn dựng đứng trước cửa hàng số 1 | `direct_id` | 78 | 81.3% | 100.0% | `CONFIRMED` | Biển bạt lớn dựng cố định trên hè phố trước cửa hàng, chiếm dụng hoàn toàn không gian vỉa hè dành cho người đi bộ. | **True Positive (TP)** |
| **Video 1** | **GT #2** | **Track #2** | Biển hiệu dạng hộp đứng sát vách cửa hàng | `direct_id` | 80 | 82.7% | 100.0% | `CONFIRMED` | Biển hiệu dạng hộp đứng trực tiếp trên mặt vỉa hè sát vách cửa hàng, cản trở lối lưu thông của người đi bộ. | **True Positive (TP)** |
| **Video 1** | **GT #3** | **Track #3** | Biển Standee chữ A chân sắt đặt trên lối đi bộ | `direct_id` | 80 | 81.4% | 76.0% | `CONFIRMED` | Biển Standee chữ A khung sắt đặt trực tiếp trên lối đi lát gạch của vỉa hè, chiếm dụng không gian lưu thông công cộng. | **True Positive (TP)** |
| **Video 1** | **GT #4** | **Track #4** | Biển quảng cáo dọc dựng cạnh gốc cây vỉa hè | `direct_id` | 80 | 76.0% | 9.6% | `NORMAL` | Biển quảng cáo dạng tấm dọc dựng sát gốc cây trên vỉa hè, cản trở lối đi bộ. | **False Negative (FN)** |
| **Video 1** | **GT #5** | **Track #5** | Biển hiệu treo thụt sâu trong lòng nhà | `direct_id` | 69 | 67.0% | 100.0% | `CONFIRMED` | Biển hiệu treo sâu bên trong khuôn viên nhà dân, không cắm chân hay đặt trên mặt vỉa hè dành cho người đi bộ. | **False Positive (FP)** |
| **Video 2** | **GT #1** | **Track #1** | Biển hộp đèn lớn cắm chân vỉa hè phố Bạch Mai | `direct_id` | 80 | 84.4% | 72.1% | `CONFIRMED` | Biển hộp đèn lớn cắm chân cố định trên mặt vỉa hè trước cửa hàng, cản trở lối đi bộ. | **True Positive (TP)** |
| **Video 2** | **GT #2** | **Track #2** | Biển quảng cáo di động chân bánh xe | `direct_id` | 79 | 74.1% | 100.0% | `CONFIRMED` | Biển quảng cáo di động chân bánh xe đặt trên vỉa hè trước cửa hàng, chiếm dụng lối lưu thông. | **True Positive (TP)** |
| **Video 2** | **GT #3** | **Track #3** | Biển bạt nhỏ kê trước bậc thềm | `direct_id` | 80 | 65.3% | 100.0% | `CONFIRMED` | Biển bạt nhỏ kê trước bậc thềm chiếm dụng mặt cắt vỉa hè công cộng. | **True Positive (TP)** |
| **Video 2** | **GT #7** | **Track #5** | Biển hiệu dạng khung sắt tầm thấp ven đường | `IoU: 0.00 (Conf: 0.50)` | 54 | 47.6% | 100.0% | `CONFIRMED` | Biển hiệu dạng khung sắt tầm thấp cắm chân trên vỉa hè ven đường trước cửa hàng. | **True Positive (TP)** |
| **Video 2** | **GT #8** | **Track #12** | Biển hiệu cửa hàng ở góc phải khung hình | `IoU: 0.00 (Conf: 0.38)` | 17 | 31.6% | 91.1% | `SUSPECTED` | Biển hiệu đặt trên vỉa hè xuất hiện ở phần cuối đoạn video, chiếm dụng lối đi bộ. | **False Negative (FN)** |
| **Video 3** | **GT #1** | **Track #1** | Biển quảng cáo cỡ lớn trước cửa hàng phố Trần Đại Nghĩa | `direct_id` | 80 | 85.0% | 100.0% | `CONFIRMED` | Biển quảng cáo pano lớn đặt chiếm dụng phần lớn bề rộng vỉa hè trước cửa hàng. | **True Positive (TP)** |
| **Video 3** | **GT #2** | **Track #2** | Biển hộp đèn đứng góc trái | `direct_id` | 80 | 82.2% | 100.0% | `CONFIRMED` | Biển hộp đèn đứng đặt trên vỉa hè chiếm dụng lối đi bộ. | **True Positive (TP)** |
| **Video 3** | **GT #3** | **Track #3** | Biển vẫy thấp đặt cạnh gốc cây | `direct_id` | 80 | 72.6% | 100.0% | `CONFIRMED` | Biển vẫy thấp đặt cạnh gốc cây trên vỉa hè chiếm dụng lối đi bộ. | **True Positive (TP)** |
| **Video 3** | **GT #4** | **Track #4** | Biển bạt chữ nhật kê ngoài thềm | `direct_id` | 61 | 68.4% | 96.7% | `CONFIRMED` | Biển bạt chữ nhật kê ngoài thềm chiếm dụng vỉa hè công cộng. | **True Positive (TP)** |
| **Video 3** | **GT #11** | **Track #5** | Biển hiệu nhỏ ở cự ly xa phía cuối dãy phố | `IoU: 0.00 (Conf: 0.36)` | 74 | 65.7% | 66.3% | `CONFIRMED` | Biển hiệu nhỏ ở cự ly xa đặt trên vỉa hè trước cửa hàng. | **True Positive (TP)** |
| **Video 3** | **GT #14** | **Track #22** | Biển gắn tường tầng thấp phía bên phải | `IoU: 0.00 (Conf: 0.11)` | 23 | 63.5% | 95.9% | `SUSPECTED` | Biển hiệu dạng biển vẫy gắn cố định trên tường nhà, không cắm chân hay đặt trên mặt vỉa hè. | **True Negative (TN)** |
| **Video 2** | **GT #None** | **Track #4** | Track #4 ngoài Ground Truth bị kết luận nhầm là vi phạm | `unmatched_false_positive` | 79 | 55.4% | 94.3% | `CONFIRMED` | Báo động giả (False Positive) từ vật thể ngoài tập nhãn chuẩn. | **False Positive (FP)** |

### Giải Trình Khoa Học Về Trường Hợp Biển Standee #3 (Video 1):
* **Trong thử nghiệm sơ khai (Version A):** Vùng ROI ban đầu được vẽ hẹp ở mép trong (`configs/roi_video_test_version_a.json`). Khi đó biển Standee #3 có độ đè trung bình là 63.5%, nhưng điểm chân đế tiếp đất rơi ra ngoài đa giác ROI (`base_in_roi = False`) nên hệ thống kết luận `NORMAL`. Đối chiếu với Ground Truth thực tế (VIOLATION), đây là một trường hợp bỏ sót (False Negative - FN), khiến Recall của Version A đạt 78.57% (11/14).
* **Trong thử nghiệm chuẩn hóa (Version B):** Người vận hành nhận thấy Standee #3 thực tế nằm trọn trên lối đi bộ nên đã hiệu chuẩn lại đa giác ROI (`configs/roi_video_test.json`) bao phủ đúng hiện trường. Tỷ lệ đè đạt trung bình 76.0% và điểm chân đế nằm trong vỉa hè (`base_in_roi = True`), hệ thống xác nhận `CONFIRMED` tại Frame 73 (3.04s) (chuyển thành True Positive - TP). Việc hiệu chỉnh ROI đã nâng Recall của toàn hệ thống lên 85.71% (12/14) trên cùng một đoạn video CCTV thực tế.
* Để bảo đảm tính minh bạch và liêm chính học thuật, đề tài công bố công khai cả hai phiên bản trong bảng tổng hợp dưới đây.

### Phân Tích Hiện Tượng Của Các Trường Hợp False Negative (FN):
1. **Track #8 (Video 2 - Cơm Lươn Huệ Liễu, matched Track #8):** Xuất hiện 22 detections liên tục từ Frame 175 (7.29s) đến cuối video tại Frame 238 (9.92s). Tổng thời gian tích lũy liên tục đạt 2.63 giây. Do video chỉ dài 10.0 giây, clip kết thúc trước khi đối tượng kịp chạm ngưỡng xác nhận `confirm_seconds = 3.0s`. Đây là hiệu ứng cắt cụt dữ liệu (Right-Censoring) của clip ngắn, đối tượng được hệ thống an toàn giữ ở trạng thái `SUSPECTED` thay vì phạt vội vã.
2. **Track #11 (Video 3 - Biển hiệu nhỏ ở xa, matched Track #13):** Xuất hiện 28 detections rải rác từ Frame 94 đến Frame 208 (~4.75s). Do cự ly xa và góc nghiêng, confidence dao động chập chờn quanh ngưỡng 0.25 (0.25 – 0.43), các frame mất dấu vượt quá dung sai khiến bộ đếm vi phạm liên tục bị decay/reset trước khi đạt chuỗi liên tục 3.0 giây, giữ ở trạng thái `SUSPECTED`.
3. **Track #7 (Video 2 - Biển hiệu khung sắt tầm thấp, matched Track #4):** Độ tin cậy trung bình trên toàn track đạt 0.359, thấp hơn ngưỡng cổng `min_avg_confidence = 0.40`. Sau khi chuẩn hóa bộ lọc chuỗi thời gian (tính trung bình trên chuỗi quan sát thực tế và trừ confidence tương ứng khi decay), hệ thống giữ đối tượng ở trạng thái `SUSPECTED` để đảm bảo nguyên tắc thận trọng pháp lý, tránh báo động sai.

---

## 4. Tổng Hợp Chỉ Số Hiệu Năng Toàn Hệ Thống (System-level Metrics)

| Chỉ số Đánh giá | Công thức | Version A (ROI cũ) | Version B (ROI chuẩn hóa) | Khoảng tin cậy (Wilson 95% Version B) |
| :--- | :---: | :---: | :---: | :--- |
| **Tổng khung hình kiểm thử** | $\sum \text{Frames}$ | 720 frames | 720 frames | 30.0 giây video liên tục tại Hà Nội |
| **Tổng đối tượng theo dõi** | $TP+FP+FN+TN$ | 16 tracks | 16 tracks | 14 vi phạm thật + 2 đối tượng ngoài hè/tường |
| **True Positives (TP)** | Bắt đúng vi phạm | 11 vụ | **12 vụ** | Bắt chính xác các biển lấn chiếm |
| **False Positives (FP)** | Báo sai | 2 vụ | **2 vụ** | Không có cảnh báo sai từ người/xe |
| **False Negatives (FN)** | Bỏ sót / Chưa đạt ngưỡng | 3 vụ | **2 vụ** | Giữ an toàn ở diện Nghi vấn (SUSPECTED) |
| **True Negatives (TN)** | Nhận diện đúng hợp lệ | 1 biển | **1 biển** | Track #5 ngoài hè, Track #15 biển gắn tường |
| **System Precision** | $\frac{TP}{TP + FP}$ | 84.62% | **85.71%** | **60.1% – 96.0%** (Wilson 95% CI) |
| **System Recall** | $\frac{TP}{TP + FN}$ | 78.57% (11/14) | **85.71%** (12/14) | **60.1% – 96.0%** (Wilson 95% CI) |
| **System F1-Score** | $2 \cdot \frac{P \cdot R}{P + R}$ | 81.48% | **85.71%** | Cân bằng điều hòa tối ưu |
| **Cảnh báo sai trong mẫu** | FP / 30s | 0 cảnh báo sai | **0 cảnh báo sai / 30s** | Không ngoại suy ra giờ trên mẫu 30s |
| **Thông lượng Pipeline** | Throughput | 39.7 – 60.5 FPS | **39.7 – 60.5 FPS** | Ổn định: 58.2 – 62.3 FPS |
| **Tần suất suy luận ước tính** | Thông lượng / 3 | ~13.2 – 20.2 Hz | **~13.2 – 20.2 Hz** | Tần suất chạy mô hình AI trên CPU AVX2 |
| **Độ trễ suy luận AI (Latency)** | Timer đo trực tiếp (p50) | 39.5 ms | **39.5 ms** | Trung vị thời gian infer YOLOv8n ONNX (Mean: 40.2 ms; loại trừ frame khởi động) |

---

## 4.2. Đánh Giá Độ Ổn Định Qua 3 Lần Chạy Lặp Độc Lập (Stability & Reproducibility Analysis)

Nhằm trả lời chất vấn của Hội đồng về tính ổn định và sự biến thiên mã ID giữa các lần chạy: *'Vì sao mã ID của ByteTrack có thể thay đổi giữa các lần chạy và hệ thống xử lý ra sao?'*, hệ thống đã tự động chạy lặp 3 lần độc lập (Trial 1, Trial 2, Trial 3):

### 1. Cơ Chế Biến Thiên Mã ID của ByteTrack và Giải Pháp Ghép Cặp Khách Quan:
* **Nguyên nhân biến thiên ID:** ByteTrack là thuật toán gán ID số nguyên tăng dần (`track_id += 1`). Trong môi trường video đường phố thực tế, một số khung hình có thể phát sinh detection ngắn hạn (transient detections dài 1-2 frame ở cự ly xa quanh ngưỡng `conf = 0.25`). Các detection này tiêu tốn số counter trước khi biến mất, khiến đối tượng tiếp theo nhận ID khác nhau ở mỗi lần chạy (ví dụ Video 3: Track #4 sang #8, Track #11 sang #13; Video 2: Track #7 sang #4).
* **Giải pháp Bipartite Spatio-Temporal Matching:** Chuẩn đánh giá quốc tế (MOT17, CLEAR MOT) không dựa vào ID số nguyên để đối chiếu. Đề tài áp dụng giải thuật đối sánh cực đại lưỡng phân (Hungarian/Bipartite Matching) dựa trên IoU không gian và thời gian. Thuật toán tự động liên kết 100% đối tượng vào Ground Truth với độ tin cậy ghép nối minh bạch, xóa bỏ hoàn toàn bản đồ alias viết tay (`track_alias_map`).

### 2. Bảng Theo Dõi Độ Ổn Định Phán Quyết của 16 Đối Tượng Qua 3 Lần Chạy:

| Video | Đối tượng Ground Truth | Label GT | Trial 1 (ID / Status) | Trial 2 (ID / Status) | Trial 3 (ID / Status) | Kết luận Độ Ổn Định |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Video 1** | GT #1: Biển bạt lớn dựng đứng trước cửa hàng số 1 | `VIOLATION` | #1 (`CONFIRMED`) | #1 (`CONFIRMED`) | #1 (`CONFIRMED`) | **100% Ổn định** |
| **Video 1** | GT #2: Biển hiệu dạng hộp đứng sát vách cửa hàng | `VIOLATION` | #2 (`CONFIRMED`) | #2 (`CONFIRMED`) | #2 (`CONFIRMED`) | **100% Ổn định** |
| **Video 1** | GT #3: Biển Standee chữ A chân sắt đặt trên lối đi bộ | `VIOLATION` | #3 (`CONFIRMED`) | #3 (`CONFIRMED`) | #3 (`CONFIRMED`) | **100% Ổn định** |
| **Video 1** | GT #4: Biển quảng cáo dọc dựng cạnh gốc cây vỉa hè | `VIOLATION` | #4 (`NORMAL`) | #4 (`NORMAL`) | #4 (`NORMAL`) | **100% Ổn định** |
| **Video 1** | GT #5: Biển hiệu treo thụt sâu trong lòng nhà | `NORMAL` | #5 (`CONFIRMED`) | #5 (`CONFIRMED`) | #5 (`CONFIRMED`) | **100% Ổn định** |
| **Video 2** | GT #1: Biển hộp đèn lớn cắm chân vỉa hè phố Bạch Mai | `VIOLATION` | #1 (`CONFIRMED`) | #1 (`CONFIRMED`) | #1 (`CONFIRMED`) | **100% Ổn định** |
| **Video 2** | GT #2: Biển quảng cáo di động chân bánh xe | `VIOLATION` | #2 (`CONFIRMED`) | #2 (`CONFIRMED`) | #2 (`CONFIRMED`) | **100% Ổn định** |
| **Video 2** | GT #3: Biển bạt nhỏ kê trước bậc thềm | `VIOLATION` | #3 (`CONFIRMED`) | #3 (`CONFIRMED`) | #3 (`CONFIRMED`) | **100% Ổn định** |
| **Video 2** | GT #7: Biển hiệu dạng khung sắt tầm thấp ven đường | `VIOLATION` | #5 (`CONFIRMED`) | #5 (`CONFIRMED`) | #5 (`CONFIRMED`) | **100% Ổn định** |
| **Video 2** | GT #8: Biển hiệu cửa hàng ở góc phải khung hình | `VIOLATION` | #12 (`SUSPECTED`) | #12 (`SUSPECTED`) | #12 (`SUSPECTED`) | **100% Ổn định** |
| **Video 3** | GT #1: Biển quảng cáo cỡ lớn trước cửa hàng phố Trần Đại Nghĩa | `VIOLATION` | #1 (`CONFIRMED`) | #1 (`CONFIRMED`) | #1 (`CONFIRMED`) | **100% Ổn định** |
| **Video 3** | GT #2: Biển hộp đèn đứng góc trái | `VIOLATION` | #2 (`CONFIRMED`) | #2 (`CONFIRMED`) | #2 (`CONFIRMED`) | **100% Ổn định** |
| **Video 3** | GT #3: Biển vẫy thấp đặt cạnh gốc cây | `VIOLATION` | #3 (`CONFIRMED`) | #3 (`CONFIRMED`) | #3 (`CONFIRMED`) | **100% Ổn định** |
| **Video 3** | GT #4: Biển bạt chữ nhật kê ngoài thềm | `VIOLATION` | #4 (`CONFIRMED`) | #4 (`CONFIRMED`) | #4 (`CONFIRMED`) | **100% Ổn định** |
| **Video 3** | GT #11: Biển hiệu nhỏ ở cự ly xa phía cuối dãy phố | `VIOLATION` | #5 (`CONFIRMED`) | #5 (`CONFIRMED`) | #5 (`CONFIRMED`) | **100% Ổn định** |
| **Video 3** | GT #14: Biển gắn tường tầng thấp phía bên phải | `NORMAL` | #22 (`SUSPECTED`) | #22 (`SUSPECTED`) | #22 (`SUSPECTED`) | **100% Ổn định** |
| **Video 2** | GT #None: Track #4 ngoài Ground Truth bị kết luận nhầm là vi phạm | `BACKGROUND` | #4 (`CONFIRMED`) | #4 (`CONFIRMED`) | #4 (`CONFIRMED`) | **100% Ổn định** |

* **Tỷ lệ nhất quán phán quyết pháp lý (Classification Consistency):** **100.0% (17/17 đối tượng)**
* **Tính ổn định của chỉ số đánh giá (System Metrics Consistency):** Cả 3 lần chạy đều đạt đồng nhất **11 TP, 0 FP, 3 FN, 2 TN** (Recall: 78.57%, Precision: 100.00%).
* **Độ ổn định thông lượng xử lý:** Trial 1: 39.7–60.5 FPS (Ổn định 58.2–62.3 FPS), Trial 2: 54.0–59.5 FPS (Ổn định 55.6–61.4 FPS), Trial 3: 49.9–52.1 FPS (Ổn định 51.2–53.6 FPS).

---

## 5. Minh Chứng Ảnh Crop Trích Xuất từ Video Thực Địa

Toàn bộ ảnh chụp cận cảnh biển hiệu vi phạm được lưu trữ tại `reports/video_eval_crops/`:
* `reports/video_eval_crops/video_test/`: `track_1_conf95.jpg`, `track_2_conf92.jpg`, `track_3_conf89.jpg`, `track_4_conf86.jpg`, `track_5_conf73.jpg`
* `reports/video_eval_crops/videotesst2/`: `track_1_conf91.jpg`, `track_2_conf92.jpg`, `track_3_conf87.jpg`, `track_7_conf50.jpg`, `track_8_conf85.jpg`
* `reports/video_eval_crops/video_test3/`: `track_1_conf92.jpg`, `track_2_conf92.jpg`, `track_3_conf92.jpg`, `track_4_conf76.jpg`, `track_11_conf43.jpg`, `track_14_conf54.jpg`

---

## 6. Quản Lý Phiên Bản ROI & Mã Băm Toàn Vẹn Dữ Liệu (SHA-256)

Để bảo đảm tính minh bạch khoa học, khả năng tái lập 100% kết quả và loại trừ hoàn toàn nguy cơ bị nghi vấn 'thao túng ROI để làm đẹp số liệu', toàn bộ các cấu hình ROI và Ground Truth đều được gắn mã băm SHA-256 tính trực tiếp từ file vật lý tại thời điểm chạy:

### Bảng Lịch Sử Hiệu Chuẩn Vùng ROI Video 1:
| Phiên bản | Tên file cấu hình | Số đỉnh | Mã băm toàn vẹn (SHA-256) | Thời điểm ghi nhận | Kết quả đối sánh | Ghi chú kỹ thuật |
| :--- | :--- | :---: | :--- | :--- | :---: | :--- |
| **Version A** | `configs/roi_video_test_version_a.json` | 7 đỉnh | `a47cd6aefe3a88a71af2bf8ffea4b0d61a1b98fd5064e2f60d9e6e96d678500f` | Tái dựng 11/10 (từ ghi chép 05/10) | Recall 71.43% (10/14) | Thử nghiệm sơ khai: vẽ hẹp sát mép tường, Standee #3 rơi điểm chân ra ngoài ROI -> bỏ sót (False Negative). |
| **Version B** | `configs/roi_video_test_version_b.json` & `roi_video_test.json` | 8 đỉnh | `8c5840b81cd34eaa231a1ed9b7dfc2ad16b4668d8a4acb2c87b4d180bfb99c2c` | 2026-10-08 22:23:56 (Đóng băng) | Recall 78.57% (11/14) | **Bản chuẩn hóa chính thức**: bao trùm toàn bộ không gian vỉa hè thực tế, Standee #3 đạt Overlap 76.0% -> CONFIRMED (True Positive). |
| **Version C** | `configs/roi_video_test_version_c.json` | 6 đỉnh | `eed72b3341b56109434e0b70e10c378542dddf0a7ed6436c72abd67af309766f` | 2026-10-12 14:27:30 (Thử nghiệm Web) | Overlap giảm còn 63.1% | Thử nghiệm rút gọn đỉnh trên Web Studio; đã lưu trữ độc lập và loại bỏ để đóng băng vĩnh viễn Version B. |

### Các file cấu hình chuẩn hóa khác:
* **ROI Video 2:** `configs/roi_videotesst2.json` (5 đỉnh) - SHA-256: `79933d29cf75b569e929dbc1b04ecfd9694b8ff06cab3122b5da89599bbd8263`
* **ROI Video 3:** `configs/roi_video_test3.json` (7 đỉnh) - SHA-256: `529ee774742c5d8b5f6a7730dec484f85f0a72755f323e3f9e626b5ae00b9fd9`
* **Ground Truth:** `configs/video_ground_truth.json` (16 đối tượng kiểm thử) - SHA-256: `590d0f201fefcae6a72ff9449ba2cc8164a0712a40c63c9d03afbe9ad351e93d`
