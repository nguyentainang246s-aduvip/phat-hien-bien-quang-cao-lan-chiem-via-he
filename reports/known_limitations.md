# GIỚI HẠN ĐÃ BIẾT & HƯỚNG PHÁT TRIỂN (KNOWN LIMITATIONS)

> Tài liệu này ghi nhận minh bạch các giới hạn kỹ thuật của hệ thống trong phạm vi
> đồ án tốt nghiệp (5 tháng), kèm đề xuất hướng phát triển cho từng hạn chế.

---

## 1. Không phân biệt "biển lắp cố định" vs "vật tạm thời" (ISSUE 06)

**Mô tả:** Hệ thống xác nhận vi phạm dựa trên ngưỡng thời gian ngắn (~1.5 giây = 45 frames ở 30FPS). Điều này đủ để loại bỏ nhiễu chớp nhoáng (người đi bộ, xe cộ che khuất), nhưng **chưa đủ** để phân biệt giữa:
- Biển hiệu **lắp đặt cố định** trên vỉa hè (vi phạm thực sự theo Nghị định 100/2019/NĐ-CP).
- Vật thể **tạm thời** đứng yên vài giây (xe tải đỗ mang biển quảng cáo, người cầm banner...).

**Lý do giới hạn:** Phân biệt "tính cố định" đòi hỏi theo dõi xuyên phiên (cross-session tracking) — so sánh track_id qua nhiều ngày để xác nhận "vật thể này vẫn ở đó sau 24 giờ". Yêu cầu này vượt phạm vi đồ án 5 tháng vì cần:
- Hạ tầng lưu trữ dữ liệu dài hạn.
- Thuật toán re-identification xuyên phiên (vật thể không có track_id ổn định qua restart).

**Hướng phát triển:**
1. Thêm ngưỡng xác nhận 2 tầng: `SHORT_CONFIRM` (45 frames, ~1.5s) cho cảnh báo tức thời + `LONG_CONFIRM` (300 frames, ~10s) trước khi lưu DB chính thức.
2. Cross-session deduplication: so sánh bbox mới với các bản ghi trong DB (cùng camera + vị trí tương tự) để xác nhận "biển này đã xuất hiện liên tục qua nhiều phiên giám sát".

---

## 2. Overlap Ratio sử dụng diện tích Bounding Box làm mẫu số (ISSUE 07)

**Mô tả:** Công thức tính tỷ lệ lấn chiếm:
```
Overlap Ratio = Area(Bbox ∩ ROI) / Area(Bbox)
```
Mẫu số là **diện tích Bounding Box** (không phải IoU, không phải diện tích ROI).

**Lý do thiết kế (có chủ đích):**
- Phản ánh đúng câu hỏi pháp lý: *"Bao nhiêu phần trăm CỦA BIỂN HIỆU nằm trên vỉa hè?"*
- Nếu dùng IoU: biển nhỏ nằm gọn trong ROI lớn sẽ cho IoU rất thấp (do Union lớn), dẫn đến bỏ sót vi phạm rõ ràng.
- Nếu dùng diện tích ROI làm mẫu số: kết quả phụ thuộc vào kích thước ROI (vỉa hè rộng/hẹp), không phản ánh mức độ lấn chiếm thực tế.

**Hạn chế biết trước:** Biển nhỏ nằm gọn trong ROI luôn cho tỷ lệ ~100%, trong khi biển rất lớn chỉ đè nhẹ mép ROI cho tỷ lệ thấp hơn dù diện tích tuyệt đối lớn hơn. Đây là trade-off chấp nhận được vì biển nhỏ nằm hoàn toàn trên vỉa hè rõ ràng là vi phạm.

---

## 3. Bounding Box lỏng — Detection vs Segmentation (ISSUE 08)

**Mô tả:** Hệ thống sử dụng **bounding box hình chữ nhật** (từ YOLOv8 Detection) để đại diện cho diện tích biển hiệu. Với biển nghiêng hoặc hình dạng bất thường, box bao gồm cả khoảng trống/bóng đổ xung quanh, làm sai lệch overlap ratio.

**Hướng phát triển:** Chuyển sang **Instance Segmentation** (YOLOv8-seg) để có mask pixel chính xác, thay thế box polygon bằng contour thực tế của biển hiệu.

---

## 4. Trạng thái Temporal mất khi restart (ISSUE 09)

**Mô tả:** `TemporalVerifier.track_records` lưu hoàn toàn trong RAM. Khi chương trình restart (mất điện, crash, cập nhật), tất cả biển đang theo dõi bị coi là mới → ghi trùng vi phạm.

**Giải pháp đã triển khai:** Thêm cơ chế **Database-level Deduplication** — trước khi insert vi phạm mới, kiểm tra xem đã có bản ghi tương tự (cùng camera + bbox gần giống + trong vòng N phút) hay chưa.

**Hướng phát triển:** Persist `track_records` xuống file JSON hoặc SQLite định kỳ (mỗi 30 giây), khôi phục khi khởi động lại.

---

## 5. FPS đo trên kịch bản nhẹ tải (ISSUE 12)

**Mô tả:** Con số FPS trong báo cáo benchmark đo trên kịch bản có ít hoặc không có vi phạm → chưa tính đến overhead I/O khi ghi ảnh bằng chứng + ghi SQLite liên tục ở kịch bản nhiều vi phạm đồng thời.

**Hướng phát triển:** Đo FPS trên kịch bản stress-test (nhiều biển vi phạm kích hoạt evidence saving đồng thời), so sánh với baseline để đánh giá mức sụt giảm.

---

## 6. Training Config: patience > epochs (ISSUE 16)

**Mô tả:** `args.yaml` ghi `epochs: 50` nhưng `patience: 100`. Do patience lớn hơn tổng số epoch, early stopping hoàn toàn không có tác dụng trong lần huấn luyện này.

**Nhận xét:** Điều này có nghĩa mô hình đã chạy đủ 50 epoch. Nếu muốn early stopping hoạt động, cần đặt `patience` < `epochs` (khuyến nghị 20-30).

---

## 7. Sụt giảm Precision/Recall bất thường tại Epoch 3 (ISSUE 17)

**Mô tả:** `results.csv` cho thấy Precision sụt xuống 0.447 và Recall xuống 0.056 ở epoch 3, sau đó hồi phục dần.

**Giải thích:** Đây là hiện tượng thường gặp trong giai đoạn **learning rate warmup** của YOLOv8 — learning rate tăng dần từ 0 trong 3 epoch đầu (warmup_epochs=3), gây bất ổn định tạm thời. Mô hình hồi phục hoàn toàn sau epoch 5-6, khẳng định warmup hoạt động đúng thiết kế.

---

## 8. Phát hiện camera bị xê dịch góc (ISSUE 20)

**Hướng phát triển:** Thêm module giám sát scene stability — so sánh histogram ảnh hoặc structural similarity (SSIM) giữa frame hiện tại và frame tham chiếu lưu sẵn. Nếu SSIM < ngưỡng, cảnh báo "Camera có thể đã thay đổi góc — ROI cần cập nhật".

---

## 9. RTSP chưa có bằng chứng kiểm thử thực tế (ISSUE 21)

**Mô tả:** `camera/stream_reader.py` có logic auto-reconnect hợp lý (retry, backoff) nhưng chỉ được kiểm thử với video file và webcam. Chưa có bằng chứng chạy trên luồng RTSP thật.

**Khuyến nghị:** Trước khi khẳng định trong báo cáo, nên kiểm thử ít nhất 1 lần với RTSP giả lập:
```bash
ffmpeg -re -i data/videos/sample.mp4 -f rtsp rtsp://localhost:8554/test
python main.py --mode monitor --source rtsp://localhost:8554/test
```
