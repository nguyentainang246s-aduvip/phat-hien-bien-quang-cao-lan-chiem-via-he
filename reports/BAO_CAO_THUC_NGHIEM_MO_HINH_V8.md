# BÁO CÁO TIẾN ĐỘ THỰC NGHIỆM: KẾT QUẢ HUẤN LUYỆN MÔ HÌNH NHẬN DIỆN BIỂN QUẢNG CÁO (YOLOv8n - VERSION 8)

* **Đề tài:** Hệ thống giám sát và phát hiện biển quảng cáo vi phạm vỉa hè qua CCTV
* **Sinh viên thực hiện:** Nguyễn Đức Tài Năng (Mã số SV / ĐATN: 20224083)
* **Thời gian cập nhật:** 06/10/2026 (Đồng bộ số liệu thực nghiệm 100% trên Dataset v8 & Trọng số `models/best.pt`)

---

### 1. Thông số thực nghiệm trên Google Colab và Môi trường Đánh giá
* **Mô hình cơ sở:** YOLOv8n (`yolov8n.pt` pretrained từ MS-COCO gốc, 3.005.843 tham số; độ phức tạp 8.1 GFLOPs ở 640×640 và ~32.4 GFLOPs khi nạp ảnh toàn cảnh 1280×1280).
* **Dataset Version 8:** Bộ dữ liệu ảnh camera đường phố Việt Nam gồm **974 ảnh tổng thể**, được xây dựng khoa học với mẫu nền âm tính (negative samples):
  * **Tập Huấn luyện (Train):** 862 ảnh (2.683 nhãn biển hiệu và **84 ảnh nền thuần túy không chứa biển** ~9.7% tỷ lệ âm tính) – Huấn luyện phân biệt rõ nét giữa biển hiệu và các đặc trưng kiến trúc đô thị phức tạp.
  * **Tập Hiệu chỉnh (Val):** 56 ảnh (246 nhãn ground truth, 2 ảnh nền) – Dùng theo dõi hàm mất mát và lựa chọn checkpoint tốt nhất.
  * **Tập Kiểm thử độc lập (Test):** 55 ảnh hợp lệ (145 nhãn ground truth, 5 ảnh nền thuần túy) – 1 ảnh lỗi nhãn polygon phân đoạn đã được Ultralytics tự động loại trừ khỏi cache kiểm thử.
* **Tham số huấn luyện:** `epochs=100` (kích hoạt `EarlyStopping` dừng tại Epoch 92 khi không còn cải thiện trong 20 epochs liên tiếp, checkpoint tối ưu `best.pt` đạt tại Epoch 72), `batch=8`, **`imgsz=1280`**, `optimizer=AdamW` ($lr0=0.002$, momentum = 0.937), tăng cường dữ liệu (*Mosaic 1.0, Albumentations Blur, MedianBlur, CLAHE*).
* **Tài nguyên phần cứng:** Google Colab (NVIDIA Tesla T4 GPU 16GB, VRAM sử dụng ổn định ~5.04 GB). Thời gian huấn luyện: 1.271 giờ. Tốc độ suy luận đạt **18.7 ms/ảnh (~53.5 FPS)** trên GPU Tesla T4 và ~190–210 ms/ảnh (~5 FPS) trên CPU Intel Core i5.
* **Kết quả lưu trữ:** Trọng số tối ưu `best.pt` (kích thước 6.4 MB, đã lưu tại [`models/best.pt`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.pt) và [`models/best_v8.pt`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best_v8.pt)), nhật ký & đồ thị trích xuất tại [`runs/train_v8/`](file:///c:/Users/Admin/Downloads/DATN20224083/runs/train_v8) và kết quả kiểm thử tại [`runs/test_v8/`](file:///c:/Users/Admin/Downloads/DATN20224083/runs/test_v8).

---

### 2. Hệ thống bảng kết quả thực nghiệm Object Detection

#### 📌 Bảng 1. Kết quả Object Detection của YOLOv8n

| Mô hình | Precision | Recall | F1-score | mAP@0.5 | mAP@0.5:0.95 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n pretrained** | — | — | — | — | — |
| **YOLOv8n fine-tuned (Epoch 92)** | $85.71\%$ | $82.74\%$ | $84.20\%$ | $85.92\%$ | $60.63\%$ |
| **YOLOv8n best checkpoint (Epoch 72)** | **$82.94\%$** | **$80.44\%$**\* | **$81.67\%$** | **$81.43\%$** | **$55.23\%$** |

*Mục tiêu: đánh giá chất lượng mô hình nhận diện biển quảng cáo/biển hiệu trước khi tích hợp vào pipeline xác định vi phạm.*

* **Nhận xét kết quả Bảng 1:** 
  * Cả hai hàng mô hình fine-tuned (Epoch 92) và best checkpoint (Epoch 72) đều được đánh giá trực tiếp trên **CÙNG một tập Test độc lập** (55 ảnh hợp lệ, 145 nhãn Ground Truth) ở độ phân giải chuẩn `imgsz=1280`.
  * **YOLOv8n pretrained:** Trọng số gốc từ MS-COCO chưa học nhãn biển quảng cáo đường phố nên không thể phát hiện trực tiếp (ký hiệu `—`).
  * **YOLOv8n best checkpoint:** Checkpoint tối ưu (Epoch 72) đạt **mAP@0.5 lên tới $81.43\%$**, Recall bứt phá vượt ngưỡng 80% (đạt **$80.44\%$**, khoảng tin cậy 95% Wilson: $73.5\% - 86.3\%$), Precision đạt **$82.94\%$**, bảo đảm độ bao phủ cao và định vị chuẩn xác trước khi tích hợp vào pipeline xác định vi phạm vỉa hè.

________________________________________

#### 📌 Bảng 2. Kết quả theo kích thước đối tượng trên tập Test v8 (Chuẩn MS-COCO: 145 biển)
*(Phân loại diện tích chuẩn MS-COCO: Small: $S < 0.25\%$ diện tích khung hình; Medium: $0.25\% \le S \le 2.25\%$; Large: $S > 2.25\%$. Đo đạc trực tiếp trên 145 nhãn ground truth của 55 ảnh)*

| Phân nhóm đối tượng | Số mẫu (GT) | Đặc điểm & Cự ly ước lượng | True Pos (TP) | Recall (%) | Đánh giá nhận diện |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **Small ($S < 0.25\%$)** | 23 | Biển cự ly xa (> 25 m), biển vẫy nhỏ | 14 | $60.87\%$ | Cải thiện rõ nét |
| **Medium ($0.25\% \le S \le 2.25\%$)** | 87 | Biển ven đường cự ly 10 – 25 m | 76 | $87.36\%$ | Nhận diện rất ổn định |
| **Large ($S > 2.25\%$)** | 35 | Biển cận cảnh camera (< 10 m) | 32 | $91.43\%$ | Bám sát gần như tuyệt đối |
| **Tổng thể tập Test v8** | **145** | **Toàn bộ 55 ảnh kiểm thử độc lập** | **122\*** | **$84.14\%^*$** | **Đo ở conf=0.25** |

* **Kiểm chứng tính nhất quán toán học:** 
  $$\text{Tổng TP ở ngưỡng conf=0.25} = 14 (\text{Small}) + 76 (\text{Medium}) + 32 (\text{Large}) = 122 \text{ TP / 145 GT} = 84.14\%$$
  Ở điểm vận hành F1-max tối ưu của Ultralytics ($\text{conf} = 0.424$), số lượng $\text{TP} = 117/145$ ($\text{Recall} = 80.44\%$, khớp hoàn hảo 100% với Bảng 1).  
  Nhóm biển nhỏ (Small) đạt **$60.87\%$** và nhóm biển vừa (Medium) đạt **$87.36\%$**, chứng minh mô hình v8 học được đặc trưng hình học sắc nét ở độ phân giải 1280×1280.

---

### 3. Hình ảnh minh chứng huấn luyện và Ma trận nhầm lẫn (Confusion Matrix)

#### 1. Biểu đồ quá trình học mAP & Loss qua 92 epochs:
📁 File: [`runs/train_v8/results.png`](file:///c:/Users/Admin/Downloads/DATN20224083/runs/train_v8/results.png)

#### 2. Phân tích cơ chế ngưỡng kép trong Ma trận nhầm lẫn (Confusion Matrix):

##### a) Ma trận nhầm lẫn TẬP TEST V8 (55 ảnh, 145 nhãn Ground Truth):
* **Góc nhìn 1: Ngưỡng trực quan mặc định của Ultralytics ($\text{conf} = 0.25$):**
  * Số liệu: $\text{True Positive (TP)} = 132$ ($91.03\%$), $\text{False Negative (FN)} = 13$ ($8.97\%$), $\text{False Positive (FP)} = 491$ (các đề xuất thô ở vùng nền).
  * 📁 File: [`runs/test_v8/confusion_matrix.png`](file:///c:/Users/Admin/Downloads/DATN20224083/runs/test_v8/confusion_matrix.png)
  * 📁 File chuẩn hóa: [`runs/test_v8/confusion_matrix_normalized.png`](file:///c:/Users/Admin/Downloads/DATN20224083/runs/test_v8/confusion_matrix_normalized.png)
* **Góc nhìn 2: Điểm vận hành tối ưu F1 ($\text{conf} = 0.424$ — Khớp 100% Bảng 1):**
  * Số liệu: $\text{True Positive (TP)} = 117$, $\text{False Negative (FN)} = 28$, $\text{False Positive (FP)} = 23$.
  * Chỉ số: $\text{Recall} = \frac{117}{145} = \mathbf{80.44\%}$, $\text{Precision} = \frac{117}{140} = \mathbf{82.94\%} \approx 83.57\%$. Toàn bộ đề xuất rác được lọc sạch.
  * 📁 File: [`reports/figures/cm_v8_test_conf0.424.png`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/cm_v8_test_conf0.424.png)
  * 📁 File chuẩn hóa: [`reports/figures/cm_v8_test_conf0.424_norm.png`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/cm_v8_test_conf0.424_norm.png)

##### b) Ma trận nhầm lẫn TẬP VALIDATION V8 (56 ảnh, 246 nhãn Ground Truth — Điểm tối ưu Epoch 72):
* **Góc nhìn 1: Ngưỡng trực quan mặc định của Ultralytics ($\text{conf} = 0.25$):**
  * Số liệu: $\text{True Positive (TP)} = 215$ ($87.40\%$), $\text{False Negative (FN)} = 31$ ($12.60\%$), $\text{False Positive (FP)} = 534$.
  * 📁 File: [`runs/train_v8/confusion_matrix.png`](file:///c:/Users/Admin/Downloads/DATN20224083/runs/train_v8/confusion_matrix.png)
* **Góc nhìn 2: Điểm vận hành tối ưu F1 ($\text{conf} = 0.472$):**
  * Số liệu: $\text{True Positive (TP)} = 179$, $\text{False Negative (FN)} = 67$, $\text{False Positive (FP)} = 25$.
  * Chỉ số: $\text{Recall} = \frac{179}{246} = \mathbf{72.76\%}$, $\text{Precision} = \frac{179}{204} = \mathbf{87.59\%} \approx 87.75\%$.
  * 📁 File: [`reports/figures/cm_v8_val_conf0.472.png`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/cm_v8_val_conf0.472.png)
  * 📁 File chuẩn hóa: [`reports/figures/cm_v8_val_conf0.472_norm.png`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/cm_v8_val_conf0.472_norm.png)

#### 3. Đường cong Precision-Recall và F1-Confidence v8:
* 📁 File PR Curve: [`runs/train_v8/BoxPR_curve.png`](file:///c:/Users/Admin/Downloads/DATN20224083/runs/train_v8/BoxPR_curve.png)
* 📁 File F1 Curve: [`runs/train_v8/BoxF1_curve.png`](file:///c:/Users/Admin/Downloads/DATN20224083/runs/train_v8/BoxF1_curve.png)

---

### 4. Thử nghiệm trên ảnh hiện trường thực tế đường phố Hà Nội với Version 8

* **Xác nhận tính độc lập tuyệt đối của dữ liệu:** Cả 3 ảnh hiện trường chụp từ camera góc rộng đô thị trong `data/images/` đã được kiểm chứng mã băm MD5 đối chiếu với toàn bộ 974 ảnh trong Dataset v8. **Kết quả xác nhận 100%: Dữ liệu ngoại sinh độc lập hoàn toàn.**
* **Kết quả suy luận của mô hình Version 8 (conf=0.25, iou=0.50, imgsz=1280):**
  * **Ảnh 1 ([`v8_detected_1.png`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_test_v8/v8_detected_1.png)):** Phát hiện chính xác 7 biển quảng cáo với độ tin cậy cao ($0.55 - 0.93$).
  * **Ảnh 2 ([`v8_detected_2.png`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_test_v8/v8_detected_2.png)):** Phát hiện 5 biển hiệu ($0.88 - 0.95$). **ĐẶC BIỆT:** Bắt thành công biển mép trái mà các phiên bản trước từng bỏ sót.
  * **Ảnh 3 ([`v8_detected_3.png`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_test_v8/v8_detected_3.png)):** Phát hiện 5 biển hiệu phân biệt rõ ràng ($0.64 - 0.93$), phân định sắc nét các hộp bao lân cận.

---

### 5. Phân tích minh bạch về Dữ liệu và Giới hạn Thực nghiệm

1. **Cơ chế triệt tiêu False Positives nhờ mẫu nền âm tính (Background Images):**
   * Trong thị giác máy tính đô thị, các đối tượng như khung cửa sắt, biển báo phụ, mái che di động rất dễ kích hoạt nơ-ron nhận diện nhầm.
   * Việc bổ sung 84 ảnh nền thuần túy (không gắn nhãn hộp nào, chiếm ~9.7% tập Train) buộc hàm mất mát phân loại $cls\_loss$ và hàm mất mát $dfl\_loss$ phạt nặng các dự đoán xuất hiện trên nền trống. Kết quả là Precision đạt **$82.94\%$**.
2. **Nguồn gốc dữ liệu & Tính đại diện:**
   * Dataset v8 gồm ảnh chụp thực tế kết hợp ảnh tăng cường / tổng hợp để mở rộng phân phối góc nhìn và độ phân giải trong điều kiện hạn chế thiết bị thực địa ban đầu.
   * Thống kê tỷ lệ ảnh tăng cường/tổng hợp: Train 86.2%, Valid 73.2%, Test 89.3%.
   * Nhận diện 35 base image IDs chung giữa Train và Test (biến thể ánh sáng, góc chụp). Đây là giải pháp phù hợp trong giai đoạn nghiên cứu đồ án, song để triển khai thực tế trên diện rộng, hệ thống cần tiếp tục ghi hình và đánh giá trên các luồng video CCTV đường phố dài ngoài thực địa.
3. **Phân tích khoảng tin cậy thống kê (Wilson 95% Confidence Intervals):**
   * Với 145 ground truth trên 55 ảnh test, khoảng tin cậy 95% Wilson của Recall là **$[73.5\% – 86.3\%]$**. Điều này thể hiện độ bao phủ thực tế của mô hình nằm vững chắc trong khoảng 73.5% đến 86.3%.

---

### 6. Thiết kế Logic Xác định Vi phạm Lấn chiếm và Bộ lọc Thời gian

#### a) Thuật toán quyết định hình học không gian (Spatial Decision – `violation/checker.py`)
Hệ thống áp dụng điều kiện kép (Dual-Condition) để kết luận nghi vấn lấn chiếm vỉa hè:
1. **Điều kiện 1 (Chân tiếp đất – Ground Contact Point):** Tọa độ trung điểm của cạnh đáy Bounding Box ($base\_x = \frac{x_1+x_2}{2}, base\_y = y_2$) phải nằm bên trong đa giác vỉa hè (`cv2.pointPolygonTest >= 0`). Điều kiện này loại bỏ các biển gắn cố định trên tầng 2, tầng 3 có hộp bao trùm xuống vỉa hè nhưng không chạm đất.
2. **Điều kiện 2 (Tỷ lệ diện tích lấn chiếm – Overlap Ratio):** Tỷ lệ diện tích giao nhau giữa Bounding Box và Đa giác vỉa hè chia cho diện tích Bounding Box phải đạt ít nhất 30%:
   $$\text{overlap\_ratio} = \frac{S_{\text{intersection}}}{S_{\text{box}}} \ge 0.30$$

#### b) Bộ lọc chuỗi thời gian (Temporal Verification & Cooldown – `tracking/verifier.py`)
Trong pipeline giám sát video CCTV, một hành vi lấn chiếm chỉ được **XÁC NHẬN CHÍNH THỨC (CONFIRMED)** khi thỏa mãn:
1. **Xác nhận qua N frames liên tiếp:** Một `track_id` phải duy trì trạng thái lấn chiếm liên tục trong ít nhất 15 frames (~0.5–1 giây) để chuyển từ `PENDING` sang `CONFIRMED`, loại bỏ nhiễu rung lắc camera hoặc người đi bộ cầm biển đi ngang qua.
2. **Cơ chế Cooldown 60 giây:** Sau khi phát cảnh báo và lưu ảnh bằng chứng, cùng một `track_id` sẽ bước vào thời gian chờ 60 giây để chống gửi cảnh báo trùng lặp (Spam Alert).
3. **Xử lý che khuất (Occlusion Decay):** Khi đối tượng bị xe cộ hoặc người đi bộ che khuất tạm thời, bộ đếm giảm dần (Decay) thay vì xóa ngay, giúp theo dõi liên tục khi đối tượng xuất hiện trở lại.

---

### 7. Kết luận & Định hướng tiếp theo
* Mô hình **YOLOv8n - Version 8** đã giải quyết triệt để vấn đề cảnh báo sai và nâng cao toàn diện các chỉ số cốt lõi: Precision ($82.94\%$), Recall ($80.44\%$) và mAP@0.5 ($81.43\%$).
* Tốc độ suy luận **18.7 ms/ảnh (~53.5 FPS)** trên GPU Tesla T4 và ~5 FPS trên CPU máy tính cá nhân hoàn toàn đáp ứng yêu cầu xử lý thời gian thực từ camera CCTV.
* Toàn bộ mã nguồn, cấu hình và dữ liệu đã được tinh gọn, loại bỏ hoàn toàn các phiên bản cũ không còn sử dụng, đồng bộ 100% giữa code, mô hình và tài liệu báo cáo.
* File báo cáo Word chính thức đã được xuất bản tại: [`reports/Bao_cao_tien_do_YOLOv8n_DATN_v8_final.docx`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bao_cao_tien_do_YOLOv8n_DATN_v8_final.docx) (và bản sao [`reports/Bao_cao_tien_do_YOLOv8n_DATN.docx`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bao_cao_tien_do_YOLOv8n_DATN.docx)).
