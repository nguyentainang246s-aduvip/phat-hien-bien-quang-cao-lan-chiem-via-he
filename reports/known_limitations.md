# GIỚI HẠN ĐÃ BIẾT & HƯỚNG PHÁT TRIỂN (KNOWN LIMITATIONS)

> Tài liệu này ghi nhận minh bạch các giới hạn kỹ thuật của hệ thống trong phạm vi
> đồ án tốt nghiệp (5 tháng), kèm đề xuất hướng phát triển cho từng hạn chế.

---

## 1. Không phân biệt "biển lắp cố định" vs "vật tạm thời" (ISSUE 06)

**Mô tả:** Hệ thống xác nhận vi phạm dựa trên ngưỡng thời gian ngắn (~1.5 giây = 45 frames ở 30FPS). Điều này đủ để loại bỏ nhiễu chớp nhoáng (người đi bộ, xe cộ che khuất), nhưng **chưa đủ** để phân biệt giữa:
- Biển hiệu **lắp đặt cố định** trên vỉa hè (hành vi lấn chiếm hè phố theo Điều 12 Nghị định 168/2024/NĐ-CP có hiệu lực từ 01/01/2025; phạt tiền 2-3 triệu đối với cá nhân, 4-6 triệu đối với tổ chức).
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

**Hạn chế biết trước:** Biển nhỏ nằm gọn trong ROI luôn cho tỷ lệ ~100%, trong khi biển rất lớn chỉ đè nhẹ mép ROI cho tỷ lệ thấp hơn dù diện tích thực tế lớn hơn. Đây là trade-off chấp nhận được vì biển nhỏ nằm hoàn toàn trên vỉa hè rõ ràng là vi phạm.

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

**Mô tả:** Trong lần chạy thử nghiệm ban đầu (v1-v4), `args.yaml` ghi `epochs: 50` nhưng `patience: 100`. Do patience lớn hơn tổng số epoch, early stopping không kích hoạt và chạy trọn vẹn 50 epoch.

**Khắc phục ở phiên bản hoàn thiện (v8):** Trong chu kỳ huấn luyện chính thức cuối cùng (v8), mô hình được cấu hình `epochs: 100` với `patience: 20`, mô hình hội tụ và dừng sớm (early stopped) tại epoch 92 để bảo toàn trọng số tối ưu nhất tránh overfitting.

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

---

## 10. Suy luận hình học 2D thay vì mặt phẳng đất 3D (2D Bounding Box vs Ground Plane)

**Mô tả bài toán:** Hệ thống tính toán sự chồng lấn (overlap) giữa Bounding Box 2D của vật thể và đa giác ROI vỉa hè 2D trên mặt phẳng ảnh của camera CCTV.

**Nguy cơ tiềm ẩn:**
- **Biển hiệu gắn tường / Biển vẫy trên cao:** Với camera có góc nhìn nghiêng (oblique view), phần thân biển hiệu treo ngang tường hoặc vách nhà có thể chiếu đè lên vùng đa giác vỉa hè trong không gian ảnh 2D, dù thực tế chân biển không hề tiếp xúc với vỉa hè.
- **Biển gắn tường tồn tại lâu:** Mặc dù hệ thống đã có quy tắc chân đế tiếp đất (`bottom_left`, `bottom_center`, `bottom_right` nằm trong ROI) kèm dung sai 15px, nhưng nếu một biển gắn tường tầm thấp có cạnh đáy Bbox trùng lọt vào vùng ROI và tồn tại lâu hơn ngưỡng `confirm_seconds` (3.0s), hệ thống 2D có thể phán quyết nhầm thành vi phạm (`CONFIRMED`). Ví dụ thực tế: Track #14 trong Video 3 là biển gắn tường, may mắn chỉ xuất hiện 4 frames nên chưa bị phạt; nếu biển này lọt vào khung hình liên tục nhiều giây, nguy cơ báo sai là có thật.

**Định vị & Biện pháp khắc phục:**
1. **Định vị DSS (Human-in-the-Loop):** Đây là lý do cốt tử khiến hệ thống chỉ đóng vai trò hỗ trợ ra quyết định, lưu ảnh toàn cảnh góc rộng để cán bộ trật tự đô thị thẩm định bằng mắt thường trước khi lập biên bản.
2. **Hướng phát triển kỹ thuật (Homography / IPM):** Hiệu chuẩn camera bằng ma trận biến đổi phối cảnh ngược (Inverse Perspective Mapping - IPM) sử dụng ma trận Homography $H$ ($3 \times 3$) dựa trên 4 điểm mốc mặt đường thực tế. Khi đó, toàn bộ tọa độ chân biển được ánh xạ về mặt phẳng mặt đất thực (Bird's-Eye View Ground Plane), giảm đáng kể sự sai lệch do góc chiếu giữa biển treo tường trên cao và vật thể đặt dưới đất (với điều kiện camera cố định và được hiệu chuẩn chuẩn xác theo các mốc mặt đường; đây là hướng phát triển tương lai, chưa có thực nghiệm trong phạm vi đồ án).
3. **Instance Segmentation (YOLOv8-seg):** Huấn luyện tách mặt nạ phân đoạn (segmentation mask) cho riêng phần chân đế tiếp đất của biển hiệu, thay vì dùng khung chữ nhật bao trọn toàn bộ thân biển.

---

## 11. Mối đe dọa đến tính hợp lệ của thực nghiệm (Threats to Validity)

Để đảm bảo tính trung thực và khách quan khoa học trong Đồ án Tốt nghiệp, các mối đe dọa sau đây cần được công khai minh bạch:

1. **Quy mô tập thực nghiệm video còn hạn chế:**
   - Thực nghiệm toàn hệ thống hiện được thực hiện trên 3 đoạn video clip thực tế tại Hà Nội với tổng cộng 720 frames (30.0 giây) và 16 lượt đối tượng (Track IDs).
   - *Hạn chế:* Cỡ mẫu 30 giây là tập kiểm chứng sơ bộ (Proof-of-Concept) để thẩm định chuỗi pipeline liên kết (YOLOv8n + ByteTrack + TemporalVerifier), chưa đại diện đầy đủ cho vận hành liên tục 24/7 dưới thời tiết khắc nghiệt (mưa bão, ban đêm thiếu sáng, sương mù dày).
   - *Hiệu chỉnh học thuật:* Không ngoại suy kết quả "0 cảnh báo sai trong 30 giây" thành chỉ số giờ "0.0 FA/h" một cách vội vã; cần báo cáo kèm khoảng tin cậy Wilson 95%. Với cỡ mẫu 16 track và chỉ có 2 mẫu âm thực tế (TN), độ đặc hiệu (specificity) của hệ thống thực tế gần như chưa được thử thách đầy đủ.

2. **Rò rỉ dữ liệu (Data Leakage) ở tập ảnh tĩnh và Tỷ lệ dữ liệu tổng hợp (Synthetic Data):**
   - Trong tổng số 862 ảnh huấn luyện (trên 974 ảnh tổng thể của tập dữ liệu tĩnh), có hiện tượng các biến thể tăng cường (augmented) từ 35 nhóm đối tượng/ảnh gốc (base ID) xuất hiện phân tán ở cả tập Train và Val/Test. Việc các biến thể ảnh gốc xuất hiện ở cả hai tập dẫn đến hiện tượng rò rỉ dữ liệu (data leakage), khiến chỉ số mAP@0.5 (81.4%) trên tập ảnh tĩnh có phần lạc quan.
   - **Tỷ lệ ảnh tổng hợp (Synthetic Data):** Thống kê tên tệp cho thấy có 782/862 ảnh (90.7%) trong tập huấn luyện là ảnh tổng hợp sinh bởi các công cụ Generative AI (Google Gemini, ChatGPT DALL-E, Duck AI). Dữ liệu tổng hợp đóng vai trò quan trọng trong việc bổ sung các dạng biển hiệu hiếm gặp (biển chân sắt chữ A, biển hộp đèn cũ) và đa dạng hóa bối cảnh vỉa hè ban đầu. Tuy nhiên, khoảng cách phân phối (domain shift / sim-to-real gap) giữa ảnh sinh và cảm biến camera CCTV thực tế (nhiễu hạt cảm biến, ánh sáng phức tạp ban đêm, độ mờ chuyển động) có thể ảnh hưởng đến khả năng tổng quát hóa trên các địa bàn mới.
   - **Kiểm chứng Perceptual Hash (dHash 64-bit):** Thực nghiệm đối chiếu mã băm tri giác (`scripts/verify_perceptual_hash.py`, xuất ra `reports/perceptual_hash_distances.csv`) giữa 862 ảnh train và 72 khung hình video lấy mẫu (chu kỳ 10 frame/lần) ghi nhận:
     - Khoảng cách Hamming nhỏ nhất là 13/64 bits (không có cặp nào $\le 12$ bits).
     - Toàn bộ 72 cặp khung hình video đều có ảnh train gần nhất trỏ về 13 ảnh train tổng hợp khác nhau.
     - *Đánh giá trung thực:* Kết quả này đưa ra bằng chứng khiêm tốn rằng "không phát hiện trùng lặp gần giống ở mức toàn cục (global image level)". Tuy nhiên, dHash toàn ảnh là bằng chứng yếu (chỉ đo gradient độ sáng toàn khung hình, không đo riêng vùng crop biển hiệu), do đó kết quả thực nghiệm trên 3 video vẫn chỉ là thử nghiệm sơ bộ (preliminary validation), chưa thể coi là thước đo kiểm chứng độc lập hoàn toàn.

3. **Tính độc lập của Ground Truth và Độ nhạy của cỡ mẫu nhỏ:**
   - **Quy trình gán nhãn:** Ground Truth trong `configs/video_ground_truth.json` do một người gán (tác giả đề tài), chưa qua quy trình kiểm định chéo độc lập hai chiều (Double-blind annotation). Vùng ROI vỉa hè được vẽ thủ công cho từng góc máy.
   - **Độ nhạy của mẫu (Sample Sensitivity):** Do quy mô thực nghiệm video gồm 14 mẫu dương (biển vi phạm thật), các chỉ số rất nhạy cảm với cách đánh giá:
     - Recall đạt **71.43%** (10/14) ở Version A khi Standee #3 bị bỏ sót do ROI hẹp (xếp là FN).
     - Recall đạt **78.57%** (11/14) ở Version B khi hiệu chuẩn ROI bao trọn vỉa hè (Standee #3 thành TP, còn Track #7, #8, #11 là FN).
     - Recall có thể lên **84.62%** (11/13) nếu loại trừ Track #8 với lý do video quá ngắn (2.63s < 3.0s confirm_seconds - Right-Censoring).
     - Khoảng tin cậy Wilson 95% của Recall Version B là **52.4% – 92.4%** — biên độ sai số lên tới $\pm 20\%$, rộng hơn nhiều so với chênh lệch giữa các phương án đếm. Báo cáo cần công khai minh bạch khoảng tin cậy này thay vì chỉ đưa ra một con số điểm duy nhất. Cần mở rộng thu thập video dài (vài phút mỗi camera, nhiều camera đa dạng địa bàn) và mời kiểm định viên độc lập để củng cố vững chắc tính hợp lệ của chương thực nghiệm.

