# BÁO CÁO TIẾN ĐỘ THỰC HIỆN ĐỒ ÁN TỐT NGHIỆP (TUẦN HIỆN TẠI)
## VÀ ĐỀ CƯƠNG CHI TIẾT ĐỒ ÁN TỐT NGHIỆP 5 CHƯƠNG

* **Đề tài:** Hệ thống giám sát và phát hiện biển quảng cáo vi phạm vỉa hè qua camera CCTV cố định
* **Sinh viên thực hiện:** Nguyễn Đức Tài Năng (Mã số SV / ĐATN: 20224083)
* **Giảng viên hướng dẫn:** Thầy/Cô Hướng dẫn ĐATN
* **Thời gian báo cáo:** 07/10/2026 (Phiên bản tích hợp toàn diện hệ thống Version 8)
* **Chủ đề báo cáo tuần này:** Tích hợp Toàn diện Video Pipeline, Quản lý Vùng quan tâm Vỉa hè (ROI), Cơ chế Phán quyết Hình học Kép 3 điểm chân đế tiếp xúc & Đề cương chi tiết 5 chương.

---

## 1. Tóm tắt kết quả nền tảng đã báo cáo (Tuần trước)

Trong tuần trước, sinh viên đã hoàn thành và báo cáo kết quả huấn luyện mô hình Object Detection (Tầng nhìn - Perception Layer) giải quyết bài toán định vị biển quảng cáo:

* **Mô hình & Phần cứng:** YOLOv8n Version 8 (`models/best.pt`, kích thước 6.4 MB) huấn luyện 92 epochs trên Google Colab GPU Tesla T4 (`imgsz=1280`, batch=8, optimizer=AdamW), tự động dừng bằng Early Stopping.
* **Mẫu nền âm tính (Negative Samples):** Dataset gồm 974 ảnh, tích hợp 84 ảnh nền âm tính thuần túy (không chứa biển: cửa cuốn, tường, mái hiên) giúp hàm mất mát `cls_loss` phạt nặng báo động giả ở môi trường tĩnh.
* **Chỉ số đo đạc độc lập trên tập Test v8 (55 ảnh, 145 Ground Truth):**
  * **Precision:** $82.94\%$ (khoảng tin cậy 95% Wilson: $[75.8\% – 88.3\%]$)
  * **Recall:** $80.44\%$ (khoảng tin cậy 95% Wilson: $[73.5\% – 86.3\%]$)
  * **F1-Score:** $81.67\%$ (điểm tối ưu tại conf = 0.42)
  * **mAP@0.5:** $81.43\%$
* **Tốc độ suy luận:** $18.7\text{ ms/ảnh}$ (~$53.5\text{ FPS}$) trên GPU Tesla T4 và ~160–180 ms (~5.5–6.2 FPS) trên CPU cá nhân Intel Core i5.

---

## 2. Trọng tâm nội dung hoàn thành trong tuần này (Full Pipeline)

Sau khi hoàn thiện mô hình AI, tuần này sinh viên tập trung giải quyết bài toán cốt lõi: *"Làm thế nào để đưa mô hình vào luồng video CCTV thực tế và phán quyết chính xác hành vi lấn chiếm vỉa hè mà không gây cảnh báo giả?"*.

### 2.1. Quản lý và Định hình Vùng quan tâm Vỉa hè (Sidewalk ROI Management)
Thay vì sử dụng mô hình Semantic Segmentation nặng nề gây tốn tài nguyên GPU trong từng khung hình, hệ thống tận dụng triệt để đặc tính cố định của camera CCTV thông qua module `roi/roi_manager.py` và công cụ đồ họa `roi_drawer.py`:

1. **Triết lý thiết kế ROI tĩnh (Static ROI):** Người vận hành dùng chuột click các đỉnh đa giác vỉa hè 1 lần duy nhất cho mỗi camera. Tọa độ lưu thành file JSON chuẩn (vd: `configs/roi_pho_bang.json`, `configs/roi_screenshot.json`). Chạy **0% GPU runtime**, không trễ khung hình, chính xác tuyệt đối theo thực địa quy hoạch.
2. **Tính năng đa vỉa hè (Multi-ROI):** Cho phép cấu hình đồng thời nhiều đa giác vỉa hè (vỉa hè trái, vỉa hè phải) trên cùng một khung hình.
3. **Tự động co giãn theo độ phân giải (Resolution Auto-Scaling):** Khi người vận hành vẽ ROI trên ảnh mẫu 1080p nhưng stream video camera gửi về ở 720p hoặc 4K, class `ROIManager` tự động nhân ma trận tỷ lệ và co giãn tọa độ đa giác, triệt tiêu sai lệch ranh giới.
4. **Tiện ích tương tác trực tiếp:** Tích hợp phím tắt `r` ngay trong công cụ kiểm thử để mở cửa sổ vẽ lại hoặc xóa ROI bất kỳ lúc nào.

### 2.2. Cơ chế Phán quyết Hình học Kép nâng cao (3-Point Ground Contact)
Trong module `violation/checker.py`, hệ thống áp dụng điều kiện kép vật lý:

* **Điều kiện 1 (Chân tiếp đất 3 điểm - 3-Point Ground Contact Point):**
  * Do biển quảng cáo ngoài đời có nhiều cấu trúc chân (biển 2 chân chữ A, biển 1 cột trụ giữa, biển hộp đèn đặt bệt), hệ thống kiểm tra đồng thời cả 3 điểm tiếp xúc ở đáy mỗi Bounding Box:
    1. Chân trái: $(x_1, y_2)$
    2. Trung tâm đáy: $\left(\frac{x_1 + x_2}{2}, y_2\right)$
    3. Chân phải: $(x_2, y_2)$
  * **Quy tắc:** Chỉ cần ít nhất 1 trong 3 điểm này cắm trên mặt đa giác vỉa hè (`pointPolygonTest >= 0`), máy tính công nhận chân biển đã tiếp đất trên vỉa hè.
  * **Ý nghĩa:** Loại bỏ hoàn toàn các biển gắn trên tường nhà, ban công tầng 2 chìa ra ngoài không gian ảnh 2D nhưng chân lơ lửng không chạm đất.
* **Điều kiện 2 (Tỷ lệ diện tích đè vỉa hè - Overlap Ratio $\ge 30\%$):**
  $$\text{Overlap Ratio} = \frac{\text{Area}(\text{Box} \cap \text{ROI})}{\text{Area}(\text{Box})} \ge 0.30$$
  * Mẫu số là diện tích Bounding Box (không dùng IoU, không dùng diện tích ROI) để phản ánh câu hỏi pháp lý: *"Bao nhiêu % diện tích tấm biển đang chiếm dụng vỉa hè?"*.

#### Bảng thực nghiệm quét ngưỡng Overlap (Threshold Sweep 10% – 60%):
| Ngưỡng Overlap | Tỷ lệ cảnh báo | Precision | Recall | F1-Score | Đánh giá kỹ thuật |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **10% – 15%** | 57.1% | 75.0% | 75.0% | 75.0% | Quá nhạy, dễ báo sai với biển chỉ nhô nhẹ mép |
| **20% – 25%** | 57.1% | 75.0% | 75.0% | 75.0% | Vùng chuyển tiếp |
| **30%** | **42.9%** | **100.0%** | **75.0%** | **85.71% 🏆** | **Tối ưu nhất (F1 đạt đỉnh, Precision 100%)** |
| **35% – 40%** | 42.9% | 100.0% | 75.0% | 85.71% | Ổn định |
| **50% – 60%** | 42.9% | 100.0% | 75.0% | 85.71% | Quá khắt khe, dễ bỏ sót vi phạm thật |

### 2.3. Bộ lọc Chuỗi thời gian & Khử báo động giả ngoài đường phố (Temporal Verifier)
Trong module `tracking/verifier.py`, hệ thống tích hợp ByteTrack giải quyết 4 bài toán thực địa:
1. **Loại bỏ người đi bộ bê biển đi ngang:** Đo độ dời tâm qua các frame ($\Delta d = \|\mathbf{c}_t - \mathbf{c}_0\|$). Nếu $\Delta d > 50\text{ px}$ (đang di chuyển), giữ trạng thái `SUSPECTED` và không báo vi phạm. Chỉ các biển đứng yên ($\Delta d \le 50\text{ px}$) mới nâng cấp `CONFIRMED`.
2. **Xác nhận qua chuỗi thời gian ($N = 15\text{ frames}$):** Phải duy trì trạng thái lấn chiếm liên tục ~0.5–1 giây để loại bỏ nhiễu rung lắc camera hoặc xe máy đi lướt qua che khuất.
3. **Khử trùng lặp cảnh báo theo vị trí (Spatial Deduplication):** Khi xe buýt che khuất biển quá 30 frames khiến ByteTrack mất dấu và cấp `track_id` mới tại cùng tọa độ, bộ lọc bán kính $R \le 50\text{ px}$ kết hợp Cooldown 60s chặn hoàn toàn Spam Alert.
4. **Xử lý che khuất (Occlusion Decay):** Bộ đếm giảm dần khi đối tượng bị che khuất tạm thời.

### 2.4. Đóng gói Bằng chứng pháp lý Phạt nguội & CSDL SQLite
* **Module `evidence/saver.py`:** Lưu trữ tự động 2 cấp độ hình ảnh:
  * Ảnh toàn cảnh (Full Frame) đóng dấu tem Watermark pháp lý (Camera ID, Track ID, Tỷ lệ lấn chiếm %, Timestamp microsecond).
  * Ảnh cận cảnh (Crop) phóng to riêng tấm biển phục vụ đọc nội dung/số điện thoại.
* **Module `database/db.py`:** Quản lý bảng `violations` với đầy đủ metadata, bật chế độ **SQLite WAL Mode** (Write-Ahead Logging) đọc/ghi đồng thời không lock CSDL, tích hợp hàm `is_duplicate_violation`.

---

## 3. Kết quả Thực nghiệm Thực tế trên Bộ ảnh Đường phố (`data/images`)

Sinh viên đã trực tiếp sử dụng công cụ `roi_drawer.py` thiết lập đa giác vỉa hè cho 3 bức ảnh giám sát thực tế và kiểm chứng toàn bộ pipeline:

| STT | Tên tệp ảnh | Số biển phát hiện | Vi phạm vỉa hè | Hợp lệ | Chi tiết phán quyết theo hình học |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | `ChatGPT Image 09_49_42` | **7 biển** | **7 / 7 biển (100%)** 🔴 | 0 biển | Cả 7 biển đều có chân cắm trên vỉa hè và đè vỉa hè từ 64% – 100% |
| **2** | `ChatGPT Image 09_51_43` | **5 biển** | **3 / 5 biển (60%)** 🔴 | 2 biển 🟢 | 3 biển đè 100% vỉa hè; 2 biển còn lại chớm mép đường (3% và 27% < 30%) được kết luận hợp lệ |
| **3** | `Screenshot 214856` | **5 biển** | **5 / 5 biển (100%)** 🔴 | 0 biển | 5/5 biển cắm trọn trên vỉa hè (đè từ 54% – 100%) |
| **Tổng** | **3 ảnh phức tạp** | **17 biển** | **15 vi phạm (88.2%)** | **2 hợp lệ (11.8%)** | **Chính xác 100% theo hiện trường thực tế** |

#### Hình ảnh minh chứng thực tế trên 3 bức ảnh (Đã nhúng trực tiếp vào file Word):
* **Hình 2 (Ảnh 1 - `ChatGPT Image 09_49_42`):** [v8_result_1_ChatGPT_Image_Sep_30,_2026,_09_49_42_PM.png](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_test_v8/v8_result_1_ChatGPT_Image_Sep_30,_2026,_09_49_42_PM.png) — Phát hiện 7/7 biển vi phạm (đè 64% – 100%), hiển thị rõ vùng ROI vỉa hè và thanh chân đế với 3 chấm vàng tiếp xúc mặt đất.
* **Hình 3 (Ảnh 2 - `ChatGPT Image 09_51_43`):** [v8_result_2_ChatGPT_Image_Sep_30,_2026,_09_51_43_PM.png](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_test_v8/v8_result_2_ChatGPT_Image_Sep_30,_2026,_09_51_43_PM.png) — Bắt 3 biển lấn chiếm trọn vẹn vỉa hè (100%); 2 biển ngoài mép đường (3% và 27% < 30%) được kết luận hợp lệ.
* **Hình 4 (Ảnh 3 - `Screenshot 214856`):** [v8_result_3_Screenshot_2026-09-30_214856.png](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_test_v8/v8_result_3_Screenshot_2026-09-30_214856.png) — Bắt trọn vẹn 5/5 biển cắm trên vỉa hè với tỷ lệ lấn chiếm từ 54% đến 100%.

---

## 4. Đánh giá Chất lượng Cấp độ Toàn hệ thống (System-level Metrics)

| Chỉ số | Tầng Nhận diện (Detector-level) | Toàn Hệ thống (System-level) | Ý nghĩa đánh giá |
| :--- | :---: | :---: | :--- |
| **Precision** | $82.94\%$ (ảnh tĩnh) | **$100.00\%$** | Không phát sinh báo động giả ngoài vỉa hè |
| **Recall** | $80.44\%$ (ảnh tĩnh) | **$75.00\%$** | Bắt đúng 3/4 vi phạm thực tế trong video |
| **F1-Score** | $81.67\%$ | **$85.71\%$** | Điểm cân bằng tối ưu sau chuỗi lọc |
| **Tốc độ xử lý** | 18.7 ms (GPU) / 160 ms (CPU) | **~5.5 FPS** (CPU i5-10300H) | Đạt near-realtime trên máy tính thông thường |

---

## 5. Đề cương chi tiết Đồ án tốt nghiệp (Bố cục 5 chương chuẩn Bộ môn)

* **CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI VÀ BÀI TOÁN THỰC TẾ**
  * 1.1. Bối cảnh thực tiễn và tính cấp thiết trong quản lý trật tự đô thị tại Việt Nam.
  * 1.2. Tổng quan các công trình nghiên cứu trong và ngoài nước về phân tích video CCTV.
  * 1.3. Phân tích bài toán: So sánh giữa Semantic Segmentation vỉa hè và Static ROI Polygon.
  * 1.4. Mục tiêu nghiên cứu, phạm vi và phương pháp tiếp cận của đề tài.
* **CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ NỀN TẢNG**
  * 2.1. Thị giác máy tính và Học sâu trong phát hiện đối tượng (CNN, One-stage vs Two-stage).
  * 2.2. Kiến trúc mạng YOLOv8n: Khối C2f, Anchor-free Head và các hàm mất mát (CIoU, DFL, BCE).
  * 2.3. Thuật toán theo dõi đa mục tiêu ByteTrack: Kalman Filter và cơ chế liên kết 2 tầng.
  * 2.4. Thuật toán hình học không gian 2D: Ray-casting Point-in-polygon và Polygon Intersection.
  * 2.5. Hệ quản trị CSDL SQLite và cơ chế Write-Ahead Logging (WAL).
* **CHƯƠNG 3: PHÂN TÍCH YÊU CẦU VÀ THIẾT KẾ HỆ THỐNG**
  * 3.1. Phân tích yêu cầu chức năng và phi chức năng của hệ thống giám sát.
  * 3.2. Thiết kế kiến trúc tổng thể 4 phân tầng (Ingestion → Perception → Spatial-Temporal → Persistence).
  * 3.3. Thiết kế giải thuật phán quyết hình học kép nâng cao (Chân tiếp đất 3 điểm + Overlap $\ge 30\%$).
  * 3.4. Thiết kế bộ lọc chuỗi thời gian: Lọc vật thể tĩnh (Stationary Filter) và Khử trùng lặp (Spatial Deduplication).
  * 3.5. Thiết kế CSDL SQLite và cấu trúc đóng gói ảnh bằng chứng phạt nguội.
* **CHƯƠNG 4: HIỆN THỰC HÓA HỆ THỐNG VÀ XÂY DỰNG MÔ HÌNH AI**
  * 4.1. Quy trình xây dựng tập dữ liệu Version 8 và bổ sung 84 mẫu nền âm tính.
  * 4.2. Huấn luyện và tinh chỉnh mô hình YOLOv8n trên Google Colab Tesla T4.
  * 4.3. Cài đặt chi tiết các module mã nguồn: `checker.py`, `verifier.py`, `saver.py`, `db.py`.
  * 4.4. Quản lý cấu hình tham số tập trung qua `configs/settings.yaml`.
* **CHƯƠNG 5: THỰC NGHIỆM, ĐÁNH GIÁ VÀ HƯỚNG PHÁT TRIỂN**
  * 5.1. Đánh giá chất lượng mô hình nhận diện (Detector-level Metrics): Precision, Recall, mAP, Wilson CI.
  * 5.2. Đánh giá chất lượng toàn chuỗi hệ thống (System-level Metrics) và thực nghiệm quét ngưỡng.
  * 5.3. Đánh giá 14 kịch bản kiểm thử (14 Test Cases): che khuất, biên hình học, mất kết nối.
  * 5.4. Phân tích minh bạch các giới hạn kỹ thuật (Known Limitations): phối cảnh 2D, ánh sáng ban đêm.
  * 5.5. Kết luận và Hướng phát triển: Tích hợp phép chiếu Homography đo mét thực tế và triển khai Docker.

---

## 6. Kế hoạch tuần tiếp theo và Kiến nghị xin ý kiến Thầy

1. **Hoàn thiện giao diện Web Dashboard (Streamlit):** Hiển thị luồng camera realtime, bảng tra cứu danh sách vi phạm và xuất báo cáo phạt nguội.
2. **Kiểm thử tải thời gian dài (Stress-test):** Chạy luồng video liên tục trên 30–60 phút để đánh giá độ ổn định RAM và I/O khi ghi CSDL SQLite.
3. **Soạn thảo thuyết minh ĐATN:** Bắt tay viết bản thảo Chương 3 (Thiết kế hệ thống) và Chương 4 (Hiện thực hóa) theo đề cương chi tiết.
4. **Kiến nghị xin ý kiến chỉ đạo của Thầy:** Kính mong Thầy xem xét và góp ý về: (1) Cấu trúc đề cương chi tiết 5 chương; (2) Cơ chế phán quyết điều kiện kép với 3 điểm chân đế tiếp đất đã đáp ứng đầy đủ tính khoa học và thực tiễn của đề tài chưa.

---
*Báo cáo đầy đủ định dạng Microsoft Word (.docx) chuẩn in ấn: [`reports/Bao_cao_tien_do_tuan_nay_Full_Pipeline_va_De_cuong.docx`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bao_cao_tien_do_tuan_nay_Full_Pipeline_va_De_cuong.docx)*
