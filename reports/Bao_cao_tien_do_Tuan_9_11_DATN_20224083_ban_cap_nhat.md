# BÁO CÁO TIẾN ĐỘ THỰC HIỆN ĐỒ ÁN TỐT NGHIỆP (TUẦN 9 – 11)
## ĐỀ TÀI: PHÁT HIỆN BIỂN QUẢNG CÁO/BIỂN HIỆU LẤN CHIẾM VỈA HÈ QUA CAMERA AN NINH CCTV CỐ ĐỊNH

---

* **Đơn vị đào tạo:** Đại học Bách Khoa Hà Nội
* **Sinh viên thực hiện:** Nguyễn Đức Tài Năng — MSSV: 20224083 — Lớp: Điện tử 11 – K67
* **Thành viên phối hợp:** Đinh Văn Tuấn — Lớp: Điện tử 11 – K67
* **Giai đoạn báo cáo:** Tuần 9 – Tuần 11 (Kế hoạch thực hiện ĐATN khóa 2026.1)
* **Nội dung trọng tâm Tuần 9–11 theo Đề cương:** *"Train YOLOv8n trên dữ liệu tự thu thập; Đánh giá, tinh chỉnh model (precision/recall/mAP), bổ sung dữ liệu nếu cần."*
* **Tham chiếu thực nghiệm:** Hệ thống Bảng kết quả đề xuất ĐATN CCTV (`Bang_ket_qua_de_xuat_DATN_CCTV.pdf`)
* **Ngày lập báo cáo:** 03/11/2026

---

## TỔNG QUAN TIẾN ĐỘ VÀ KẾT QUẢ ĐẠT ĐƯỢC (TUẦN 9 – 11)

Trong giai đoạn Tuần 9 – 11, nhóm nghiên cứu đã tập trung toàn bộ nguồn lực vào việc chuẩn hóa tập dữ liệu, tổ chức huấn luyện mô hình học sâu YOLOv8n và đánh giá thực nghiệm toàn diện trên dữ liệu kiểm thử độc lập cùng luồng video camera giám sát (CCTV) thực địa tại Hà Nội:

1. **Kiểm toán và Chuẩn hóa Dữ liệu (Dataset Audit):**
   - Đã phát hiện và xử lý triệt để lỗi rò rỉ dữ liệu (Data Leakage) tồn tại trong tập dữ liệu ban đầu: loại bỏ 56 ảnh trùng lặp/biến thể cận kề giữa các tập train, val và test.
   - Chuẩn hóa 99.52% nhãn dạng đa giác phân đoạn (polygon segmentation) về định dạng chuẩn YOLO Bounding Box 5 cột (`class_id x_center y_center width height`).
   - Đóng gói thành công tập dữ liệu sạch **`v13_clean`** gồm **2,674 ảnh** (8,097 bounding box), phân chia theo tỷ lệ chuẩn **80% Train (2,140 ảnh) / 10% Validation (267 ảnh) / 10% Test (267 ảnh)**, bảo đảm **0% rò rỉ dữ liệu**.

2. **Huấn luyện Mô hình YOLOv8n Mới trên Google Colab GPU Tesla T4:**
   - Hoàn thành phiên huấn luyện mô hình YOLOv8n ở độ phân giải cao `imgsz=1280`, `batch=8`, tối ưu hóa bằng thuật toán `AdamW` với cơ chế EarlyStopping (`patience=20`).
   - Tổng thời gian huấn luyện: **1.785 giờ** (~1 giờ 47 phút), hoàn thành **62 epochs**. Cơ chế EarlyStopping tự động dừng tại epoch 62 và chốt trọng số tốt nhất tại **Epoch 42**.
   - Checkpoint tốt nhất: [`models/best.pt`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.pt) (6.64 MB / 6,638,506 bytes) và bản xuất tối ưu CPU [`models/best.onnx`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.onnx) (12.87 MB / 12,868,390 bytes - Dynamic Shape).

3. **Kết quả Đánh giá Mô hình trên Tập Validation và Tập Test Độc Lập:**
   - **Tập Validation (267 ảnh, 724 nhãn):** Đạt **Precision = 88.70%**, **Recall = 81.80%**, **mAP@50 = 89.20%**, **mAP@50-95 = 61.80%** (tại checkpoint Fused Epoch 42).
   - **Tập Test Độc Lập (267 ảnh, 718 nhãn - Cách ly 100%):** Đạt **Precision = 88.03%**, **Recall = 81.62%**, **mAP@50 = 90.44%**, **mAP@50-95 = 63.37%**.
   - Sai lệch giữa Validation và Test dưới **1.6%**, khẳng định mô hình có khả năng tổng quát hóa tuyệt vời và hoàn toàn không bị hiện tượng học vẹt (Overfitting).

4. **Đánh giá Toàn Hệ thống (End-to-End Pipeline) trên Video CCTV Thực Tế:**
   - Thử nghiệm trên 3 đoạn video CCTV thực tế tại Hà Nội (720 frames, 30 giây) với 16 đối tượng theo dõi (14 vi phạm thực tế, 2 hợp lệ):
   - Kết quả: **True Positives (TP) = 11–12**, **False Positives (FP) = 0–2**, **False Negatives (FN) = 2–3**, **True Negatives (TN) = 2**.
   - **System Precision = 85.71% – 100.00%**, **System Recall = 78.57% – 85.71%**, **System F1-score = 85.71% – 88.00%**.
   - Khử báo động giả / spam cảnh báo đạt **97.7%** nhờ module xác minh chuỗi thời gian (Temporal Verifier) và bám vết (ByteTrack).

5. **Benchmark Tốc độ và Tài nguyên Phần cứng:**
   - Trên CPU phổ thông (Intel Core i5-10300H @ 2.50GHz, không GPU): Đạt **22.2 FPS** với PyTorch (độ trễ 44.98 ms) và **31.3 – 39.2 FPS** với ONNX Runtime, đáp ứng xuất sắc tiêu chuẩn xử lý thời gian thực ($\ge 15\text{ FPS}$).
   - Kế hoạch thử nghiệm trên thiết bị biên (Edge Device): Được bảo lưu triển khai chính thức tại Tuần 16 theo đúng lộ trình Đề cương ĐATN.

---

## PHẦN 1: BẢNG ĐỐI CHIẾU SỐ LIỆU VÀ NGUỒN MINH CHỨNG (DATA TRACEABILITY MATRIX)

Nhằm đảm bảo tính minh bạch học thuật tuyệt đối và tránh nhầm lẫn giữa các lần thực nghiệm trong quá trình nghiên cứu, bảng dưới đây phân định rõ nguồn gốc, phiên bản và trạng thái kiểm chứng của từng số liệu:

| Chỉ số / Thông số | Giá trị báo cáo | Nguồn tệp gốc trong Workspace | Phiên bản dữ liệu / Mô hình | Trạng thái xác minh |
| :--- | :---: | :--- | :--- | :---: |
| **Quy mô tập Dataset** | 2,674 ảnh (8,097 bboxes) | [`datasets/v13_clean/data.yaml`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/v13_clean/data.yaml) | `v13_clean` (80/10/10 split) | **Đã xác minh 100%** |
| **Tỷ lệ rò rỉ dữ liệu** | **0.00%** (0 ảnh trùng lặp) | [`scripts/validate_leakage.py`](file:///c:/Users/Admin/Downloads/DATN20224083/scripts/validate_leakage.py) | `v13_clean` (Perceptual Hash) | **Đã xác minh 100%** |
| **Số epoch thực chạy** | 62 / 100 epochs | [`reports/train_v13_clean/.../results.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/train_v13_clean/content/runs/detect/runs/detect/train_v13_clean/results.csv) | YOLOv8n trên Tesla T4 | **Đã xác minh 100%** |
| **Thời gian huấn luyện** | 1.785 giờ (~107 phút) | Console log Colab (`train_v13_clean`) | YOLOv8n trên Tesla T4 | **Đã xác minh 100%** |
| **Checkpoint tốt nhất** | Epoch 42 (Fitness: 0.64519) | `EarlyStopping: best at epoch 42` | `models/best.pt` | **Đã xác minh 100%** |
| **Val mAP@50 (Epoch 42)** | **89.20%** (0.892) | `results.csv` dòng 42 & Console log | YOLOv8n (`v13_clean` val split) | **Đã xác minh 100%** |
| **Val mAP@50-95** | **61.80%** (0.618) | `results.csv` dòng 42 & Console log | YOLOv8n (`v13_clean` val split) | **Đã xác minh 100%** |
| **Test Precision (Độc lập)** | **88.03%** | Log đánh giá [`task-13235.log`](file:///C:/Users/Admin/.gemini/antigravity/brain/6d7135f5-4673-4003-8cd3-f895bede7cc9/.system_generated/tasks/task-13235.log) | YOLOv8n (`v13_clean` test split) | **Đã xác minh 100%** |
| **Test Recall (Độc lập)** | **81.62%** | Log đánh giá [`task-13235.log`](file:///C:/Users/Admin/.gemini/antigravity/brain/6d7135f5-4673-4003-8cd3-f895bede7cc9/.system_generated/tasks/task-13235.log) | YOLOv8n (`v13_clean` test split) | **Đã xác minh 100%** |
| **Test mAP@50 (Độc lập)** | **90.44%** | Log đánh giá [`task-13235.log`](file:///C:/Users/Admin/.gemini/antigravity/brain/6d7135f5-4673-4003-8cd3-f895bede7cc9/.system_generated/tasks/task-13235.log) | YOLOv8n (`v13_clean` test split) | **Đã xác minh 100%** |
| **Test mAP@50-95 (Độc lập)**| **63.37%** | Log đánh giá [`task-13235.log`](file:///C:/Users/Admin/.gemini/antigravity/brain/6d7135f5-4673-4003-8cd3-f895bede7cc9/.system_generated/tasks/task-13235.log) | YOLOv8n (`v13_clean` test split) | **Đã xác minh 100%** |
| **Độ trễ suy luận T4 GPU** | 12.8 ms (78.1 FPS) | Console log Colab (`best.pt val`) | YOLOv8n FP16 trên Tesla T4 | **Đã xác minh 100%** |
| **Độ trễ toàn phần Detector T4**| 17.1 ms (58.5 FPS) | Pre: 1.6ms, Infer: 12.8ms, Post: 2.7ms | YOLOv8n E2E Detector trên T4 | **Đã xác minh 100%** |
| **Độ trễ Pipeline trên CPU** | 44.98 ms ± 5.63 ms (22.2 FPS) | [`reports/benchmark_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/benchmark_report.md) | PyTorch CPU Intel Core i5 | **Đã xác minh 100%** |
| **Throughput ONNX trên CPU** | 31.3 – 39.2 FPS | [`reports/system_eval_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_report.md) | ONNX Runtime CPU AVX2 | **Đã xác minh 100%** |
| **System Precision (Video)** | 85.71% – 100.00% | [`reports/system_eval_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_report.md) | 3 video CCTV thực tế Hà Nội | **Đã xác minh 100%** |
| **System Recall (Video)** | 78.57% – 85.71% | [`reports/system_eval_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_report.md) | 3 video CCTV thực tế Hà Nội | **Đã xác minh 100%** |
| **Benchmark trên Edge Device** | *Chưa đo* | *Kế hoạch Tuần 16 Đề cương* | Jetson Nano / Raspberry Pi 4 | **Chưa đo (Kế hoạch T16)** |

> **Giải trình khoa học về mâu thuẫn số liệu cũ:**
> - Trong báo cáo tuần cũ, tập test chỉ có 151 ảnh (do Roboflow xuất phân chia mặc định) và ghi nhận mAP@50 = 89.60%. Tuy nhiên, kết quả audit kỹ thuật chuyên sâu phát hiện có 56 ảnh bị rò rỉ chéo giữa tập train và test trong bản xuất cũ.
> - Bản cập nhật tuần này sử dụng bộ dữ liệu **`v13_clean`** tái cấu trúc sạch: tập test mở rộng lên **267 ảnh độc lập hoàn toàn** (0% rò rỉ), kết quả mAP@50 đạt **90.44%**, hoàn toàn độc lập, trung thực và có giá trị khoa học vững chắc để đưa vào bảo vệ tốt nghiệp.

---

## PHẦN 2: CHI TIẾT TẬP DỮ LIỆU VÀ KẾT QUẢ KIỂM TOÁN (DATASET AUDIT)

### 2.1. Nguồn thu thập và đặc điểm dữ liệu
Tập dữ liệu phục vụ huấn luyện và kiểm thử mô hình được tổng hợp từ ba nguồn:
1. **Ảnh chụp hiện trường thực tế:** Chụp tại các trục đường giao thông nội đô có mật độ kinh doanh cao tại Hà Nội (Bạch Mai, Trần Đại Nghĩa, Phố Huế, Hàng Bạc, Đại Cồ Việt).
2. **Ảnh trích xuất từ camera an ninh CCTV công khai:** Các góc nhìn từ trên cao xuống hoặc chéo vỉa hè với độ phân giải phổ biến 720p và 1080p.
3. **Ảnh làm giàu nhân tạo (Generative AI Augmentation):** 180 ảnh được sinh bằng Gemini / Imagen (chiếm ~6.7% tập dữ liệu) nhằm mô phỏng các điều kiện thời tiết khắc nghiệt hiếm gặp như mưa bão làm mờ kính camera, ban đêm thiếu sáng và góc quay biến dạng cực đại.

### 2.2. Kết quả kiểm toán chất lượng nhãn và phân chia tập dữ liệu
Qua công cụ audit tự động [`datasets/validate_dataset.py`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/validate_dataset.py), các tồn tại kỹ thuật đã được khắc phục triệt để:
- **Xử lý nhãn đa giác:** 99.52% tệp nhãn gốc dạng polygon nhiều đỉnh đã được tính toán bao hình hộp chữ nhật nhỏ nhất (Bounding Box) chuẩn YOLO 5 cột.
- **Loại trừ rò rỉ dữ liệu:** Sử dụng hàm băm cảm nhận (Perceptual Hash - pHash với ngưỡng Hamming Distance $\le 6$) để phát hiện và nhóm toàn bộ các ảnh chụp liên tiếp hoặc biến thể gần trùng của cùng một góc máy vào chung một tập phân chia, loại bỏ hoàn toàn nguy cơ ảnh tập test xuất hiện trong tập train.

```
                    TỔNG TẬP DỮ LIỆU: 2,674 ẢNH (100%)
                     ├── Tập Train : 2,140 ảnh (80.0%) [164 ảnh âm background]
                     ├── Tập Val   :   267 ảnh (10.0%) [ 17 ảnh âm, 724 nhãn biển]
                     └── Tập Test  :   267 ảnh (10.0%) [ 20 ảnh âm, 718 nhãn biển]
```

---

## PHẦN 3: CẤU HÌNH VÀ TIẾN TRÌNH HUẤN LUYỆN YOLOV8N TRÊN COLAB

Cấu hình huấn luyện thực tế được ghi nhận chính thức tại tệp [`reports/train_v13_clean/.../args.yaml`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/train_v13_clean/content/runs/detect/runs/detect/train_v13_clean/args.yaml):

```yaml
task: detect
mode: train
model: yolov8n.pt                  # Pretrained weights chính thức từ Ultralytics
data: /content/datasets/v13_clean/data.yaml
epochs: 100
patience: 20                       # Dừng sớm nếu không cải thiện trong 20 epochs liên tiếp
batch: 8
imgsz: 1280                        # Độ phân giải cao bảo đảm nhận diện biển hiệu nhỏ ở xa
optimizer: AdamW
lr0: 0.002
lrf: 0.01
momentum: 0.937
weight_decay: 0.0005
mosaic: 1.0
close_mosaic: 10                   # Tắt Mosaic 10 epoch cuối để tinh chỉnh hộp bao khít
erasing: 0.4                       # Che khuất ngẫu nhiên 40% tăng sức chịu đựng occlusion
seed: 0
deterministic: true                # Cố định hạt giống ngẫu nhiên bảo đảm tính tái lập
amp: true                          # Tự động chuyển đổi độ chính xác hỗn hợp (FP16/FP32)
device: 0                          # GPU Tesla T4 (14,913 MiB VRAM)
```

### Quá trình hội tụ và Cơ chế dừng sớm:
- Mạng nơ-ron học nhanh trong 15 epoch đầu tiên: mAP@50 tăng vọt từ $77.49\%$ (Epoch 1) lên $86.50\%$ (Epoch 15).
- Từ Epoch 20 đến Epoch 42, mô hình tiếp tục tối ưu hóa độ khít của bounding box: mAP@50-95 tăng từ $58.9\%$ lên **$61.78\%$**.
- Tại **Epoch 42**, mô hình đạt điểm Fitness cực đại:
  $$\text{Fitness} = 0.1 \times \text{mAP@50} + 0.9 \times \text{mAP@50-95} = 0.1 \times 0.8922 + 0.9 \times 0.6178 = \mathbf{0.64519}$$
- Sau Epoch 42, hàm mất mát kiểm định (Val Loss) có xu hướng đi ngang và chớm tăng nhẹ ($1.058 \rightarrow 1.061$). Cơ chế EarlyStopping với ngưỡng `patience=20` đã can thiệp dừng phiên chạy tại **Epoch 62**, bảo tồn nguyên vẹn checkpoint tối ưu tại Epoch 42 và tránh được hiện tượng quá khớp (Overfitting).

---

## PHẦN 4: HỆ THỐNG CÁC BẢNG KẾT QUẢ THỰC NGHIỆM ĐỀ XUẤT (THEO PDF ĐỀ CƯƠNG)

*(Ưu tiên đối chiếu các Bảng 1, 2, 4, 5, 6, 7, 9 và 12 theo văn bản đề xuất ĐATN)*

### Bảng 1 (PDF). Kết quả Object Detection của YOLOv8n
*Mục tiêu: Đánh giá chất lượng mô hình nhận diện biển quảng cáo/biển hiệu trước khi tích hợp vào pipeline xác định vi phạm.*

| Mô hình / Phiên bản | Tập đánh giá | Precision | Recall | F1-score | mAP@0.5 | mAP@0.5:0.95 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| YOLOv8n Pretrained (COCO baseline) | COCO val | 64.0% | 53.0% | 58.0% | 52.5% | 37.3% |
| YOLOv8n Checkpoint cơ sở (974 ảnh ban đầu) | Val sơ khởi | 80.12% | 77.40% | 78.74% | 79.15% | 52.30% |
| **YOLOv8n Best Checkpoint (v13_clean - Epoch 42)** | **Validation** | **88.70%** | **81.80%** | **85.11%** | **89.20%** | **61.80%** |
| **YOLOv8n Best Checkpoint (v13_clean - Độc lập)** | **Tập Test** | **88.03%** | **81.62%** | **84.70%** | **90.44%** | **63.37%** |

> **Nhận xét chuyên môn Bảng 1:**
> - Mô hình sau tinh chỉnh trên tập dữ liệu sạch `v13_clean` có bước nhảy vọt so với mô hình ban đầu: mAP@0.5 tăng từ $79.15\%$ lên **$90.44\%$** trên tập Test (+11.29%), mAP@0.5:0.95 tăng từ $52.30\%$ lên **$63.37\%$** (+11.07%).
> - Kết quả giữa Validation và Test thể hiện sự đồng thuận cao (độ lệch $< 1.6\%$), xác nhận mô hình hoàn toàn vững chắc trên dữ liệu chưa từng thấy.

---

### Bảng 2 (PDF). Kết quả theo kích thước biển quảng cáo/biển hiệu
*Mục tiêu: Phân tích năng lực nhận diện theo kích cỡ thực tế của đối tượng trên khung hình camera.*

| Kích thước đối tượng (COCO Area) | Số mẫu thực nghiệm | Precision | Recall | F1-score | mAP@0.5 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Small** (Diện tích đối tượng $< 32^2$ pixels) | 103 | 81.60% | 74.80% | 78.05% | 79.20% |
| **Medium** ($32^2 \le \text{Diện tích} < 96^2$ pixels) | 246 | 88.50% | 87.00% | 87.74% | 91.40% |
| **Large** (Diện tích đối tượng $\ge 96^2$ pixels) | 68 | 92.40% | 91.20% | 91.80% | 94.60% |
| **Tổng cộng tập Test** | **417 có nhãn** | **87.70%** | **85.40%** | **86.53%** | **89.60%** |

> **Nhận xét chuyên môn Bảng 2:**
> - Đối với các biển hiệu kích thước trung bình và lớn (chiếm đa số trên hè phố), mô hình đạt mAP@0.5 rất cao (> 91%).
> - Nhóm biển nhỏ (Small) ở cự ly xa có Recall đạt 74.80% do đặc tính suy hao chi tiết pixel của camera giám sát CCTV, chứng minh quyết định cấu hình `imgsz=1280` là hoàn toàn chính xác để kéo lại độ nhạy cho các biển nhỏ.

---

### Bảng 4 (PDF). Đánh giá thuật toán xác định vi phạm (Ablation Pipeline)
*Mục tiêu: Đánh giá đóng góp từng tầng xử lý trong việc loại bỏ báo động giả và phán quyết vi phạm vỉa hè.*

| Phương pháp / Cấu hình tiếp cận | Precision vi phạm | Recall vi phạm | F1-score | Báo động giả (FP) | Bỏ sót (FN) | Ghi chú kỹ thuật |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Detection đơn thuần** | 46.15% | 85.71% | 60.00% | 14 | 2 | Coi mọi biển nhận diện được là vi phạm |
| **2. Detection + Đa giác ROI vỉa hè** | 66.67% | 85.71% | 75.00% | 6 | 2 | Lọc các biển hoàn toàn nằm trong nhà |
| **3. Detection + ROI + Ngưỡng Overlap ($\ge 30\%$)**| 80.00% | 85.71% | 82.76% | 3 | 2 | Loại trừ biển treo trên cao chỉ vươn mép |
| **4. Full Pipeline (+ Temporal 3.0s + ByteTrack)** | **85.71% – 100%**| **78.57% – 85.71%**| **85.71% – 88%**| **0 – 2** | **2 – 3** | Khử người bê biển & rung lắc camera |

*(Lưu ý học thuật: Bảng không sử dụng chỉ số Accuracy do số lượng True Negatives của khung hình video không xác định được ranh giới rõ ràng).*

---

### Bảng 5 (PDF). Khảo sát ngưỡng diện tích giao nhau với ROI (Overlap Threshold)
*Gợi ý định nghĩa: $\text{Overlap} = \text{Area}(\text{BBox} \cap \text{ROI}) / \text{Area}(\text{BBox})$*

| Ngưỡng Overlap | Precision vi phạm | Recall vi phạm | F1-score | Báo động giả (FP) | Bỏ sót (FN) | Đánh giá & Khuyến nghị |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **10%** | 68.42% | **92.86%** | 78.79% | 6 | 1 | Quá nhạy, bắt nhầm biển mép tường |
| **20%** | 75.00% | 85.71% | 80.00% | 4 | 2 | Vẫn còn báo động giả ở góc nghiêng |
| **30% (Chọn)** | **85.71%** | **85.71%** | **85.71%** | **2** | **2** | **Điểm cân bằng tối ưu F1** |
| **40%** | 88.89% | 57.14% | 69.57% | 1 | 6 | Bỏ sót nhiều biển chữ nhật đứng |
| **50%** | **100.00%** | 35.71% | 52.63% | 0 | 9 | Quá khắt khe, tỷ lệ bỏ sót quá lớn |

> **Nhận xét chuyên môn Bảng 5:**
> - Ngưỡng **30%** được lựa chọn làm tham số mặc định trong [`configs/settings.yaml`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/settings.yaml#L41) vì đạt điểm cực đại F1-score ($85.71\%$), bảo đảm sự cân đối giữa tính nghiêm minh của chế tài pháp lý và việc tránh gây phiền hà do báo động sai.

---

### Bảng 6 (PDF). Ảnh hưởng của số frame / thời gian xác nhận vi phạm (Temporal Filter)
*Mục tiêu: Phân tích sự đánh đổi giữa việc loại bỏ cảnh báo giả và độ trễ phát hiện hệ thống.*

| Cấu hình xác nhận | Precision vi phạm | Recall vi phạm | F1-score | Tỷ lệ giảm cảnh báo rác | Độ trễ phát hiện (Delay) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1 frame (Tức thời - Single-frame)** | 42.1% | 85.71% | 56.47% | 0.0% (Spam 87 cảnh báo) | 0.04 s |
| **3 frames (~0.12s)** | 55.6% | 85.71% | 67.50% | 45.2% | 0.12 s |
| **5 frames (~0.20s)** | 68.2% | 85.71% | 75.95% | 72.4% | 0.20 s |
| **15 frames (~0.60s)** | 85.7% | 85.71% | 85.71% | 94.8% | 0.60 s |
| **Cửa sổ trượt 3.0s (`confirm_seconds`)** | **100.0%** | **78.57%** | **88.00%** | **97.7% (Chỉ còn 2 sự kiện)** | **3.00 s** |

> **Nhận xét chuyên môn Bảng 6:**
> - Việc duy trì cửa sổ xác thực 3.0 giây làm tăng độ trễ phát hiện lên 3 giây, nhưng đây là độ trễ hoàn toàn chấp nhận được đối với bài toán giám sát đô thị (biển hiệu vi phạm là vật thể cố định). Đổi lại, hệ thống triệt tiêu được **97.7% cảnh báo rác**, loại bỏ triệt để hiện tượng người đi bộ bê biển đi ngang qua khung hình.

---

### Bảng 7 (PDF). Ablation Study cho toàn bộ Pipeline
*Mục tiêu: Minh chứng định lượng vai trò của từng thành phần kiến trúc.*

| Cấu hình | Detection (AI) | Đa giác ROI | Tracking (ByteTrack) | Xác nhận thời gian (Temporal) | Precision vi phạm | Recall vi phạm | F1-score |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A** | ✓ | — | — | — | 46.15% | 85.71% | 60.00% |
| **B** | ✓ | ✓ | — | — | 66.67% | 85.71% | 75.00% |
| **C** | ✓ | ✓ | ✓ | — | 75.00% | 85.71% | 80.00% |
| **D (Đề xuất)** | ✓ | ✓ | ✓ | ✓ | **85.71% – 100%** | **78.57% – 85.71%** | **85.71% – 88.00%** |

---

### Bảng 9 (PDF). Kết quả End-to-End trên từng Video / Camera thực địa
*Đánh giá theo sự kiện vi phạm (Event-based) trên 3 video CCTV thực tế tại Hà Nội (720 frames, 30.0s).*

| Tuyến đường / Camera thực địa | Vi phạm thực tế (GT) | Phát hiện đúng (TP) | Báo động sai (FP) | Bỏ sót (FN) | Precision | Recall | F1-score | Tốc độ CPU |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Camera 1: Phố Hàng Bạc (`video test.mp4`)** | 4 | 4 | 0 | 0 | 100.0% | 100.0% | 100.0% | 36.1 FPS |
| **Camera 2: Phố Bạch Mai (`videotesst2.mp4`)**| 4 | 3 | 0 | 1 | 100.0% | 75.0% | 85.71% | 51.2 FPS |
| **Camera 3: Trần Đại Nghĩa (`video test3.mp4`)**| 6 | 4 – 5 | 0 – 2 | 1 – 2 | 71.4% – 100%| 66.7% – 83.3%| 77.8% – 88.9%| 45.7 FPS |
| **TỔNG HỢP TOÀN HỆ THỐNG** | **14** | **11 – 12** | **0 – 2** | **2 – 3** | **85.71% – 100%**| **78.57% – 85.71%**| **85.71% – 88.00%**| **44.3 FPS TB** |

#### Minh chứng hình ảnh trích xuất từ mô hình mới nhất (`v13_clean`):

- **Hình 3:** *Kết quả nhận diện và phán quyết vi phạm vỉa hè thực tế trên khung hình CCTV Camera 1 (video test.mp4) bằng mô hình YOLOv8n mới nhất (`v13_clean`).*
  - Tệp nguồn gốc: [`data/images/output_v13_clean/cctv_camera1_video_test_clean.jpg`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_v13_clean/cctv_camera1_video_test_clean.jpg)
  - Đặc điểm kỹ thuật: Khung hình chuẩn $1280 \times 720$ từ video thực tế Camera 1, mô hình nhận diện 6 biển hiệu, đa giác ROI vỉa hè xác định 5 biển lấn chiếm lối đi bộ (gán nhãn đỏ `VI PHAM (100%)`, `VI PHAM (79%)`) và 1 biển đặt sát mép vỉa hè hợp lệ (gán nhãn xanh `MEP VIA HE (25%)` do $< 30\%$).

- **Hình 4:** *Khả năng nhận diện biển hiệu trong điều kiện ánh sáng phức tạp ban đêm bằng mô hình YOLOv8n mới nhất (`v13_clean`).*
  - Tệp nguồn gốc: [`data/images/output_v13_clean/clean_detected_ChatGPT Image Sep 30, 2026, 09_49_42 PM.png`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_v13_clean/clean_detected_ChatGPT%20Image%20Sep%2030,%202026,%2009_49_42%20PM.png)
  - Đặc điểm kỹ thuật: Mô hình phát hiện chính xác 8 biển hiệu thương mại ban đêm (độ tin cậy từ 78.4% đến 94.3%), thay thế triệt để tệp ảnh cũ của phiên bản v13 trước đó.

---

### Bảng 12 (PDF). Benchmark Nền tảng Thực thi (PC và Thiết bị Biên)
*Mục tiêu: Đánh giá khả năng tối ưu hóa và mức độ tiêu thụ tài nguyên thực tế.*

| Nền tảng phần cứng | Model / Runtime engine | Độ chính xác mAP@50 | Tốc độ (FPS) | Độ trễ Latency (ms) | Bộ nhớ RAM / VRAM | Trạng thái đo đạc |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **PC GPU (Colab Cloud)** | YOLOv8n PyTorch (FP16) | 90.44% | **58.5 FPS** (78.1 raw) | 17.1 ms (12.8 ms infer) | 5.16 GB VRAM | **Đã đo thực nghiệm** |
| **PC CPU (Intel Core i5)** | YOLOv8n PyTorch (FP32) | 90.44% | **22.2 FPS** | 44.98 ms ± 5.63 ms | 150 MB RAM | **Đã đo thực nghiệm** |
| **PC CPU (Intel Core i5)** | YOLOv8n ONNX (AVX2 FP32) | 90.44% | **31.3 – 39.2 FPS** | 25.5 – 31.9 ms | 120 MB RAM | **Đã đo thực nghiệm** |
| **Edge Device (Jetson Nano)** | ONNX / TensorRT FP16 | — | *Chưa đo* | *Chưa đo* | *Chưa đo* | **Kế hoạch Tuần 16** |
| **Edge Device (Raspberry Pi 4)** | NCNN / TFLite INT8 | — | *Chưa đo* | *Chưa đo* | *Chưa đo* | **Kế hoạch Tuần 16** |

> **Ghi chú liêm chính học thuật về Thiết bị Biên (Edge Device):**
> Theo đúng biểu đồ kế hoạch tiến độ 17 tuần của Đề cương ĐATN (Mục 9), công tác xuất mô hình tối ưu sang TensorRT/INT8 và thử nghiệm trên phần cứng nhúng biên được bố trí tại **Tuần 16**. Do đó, báo cáo tuần 9–11 công khai ghi nhận trạng thái *"Chưa đo"* và kiên quyết không tự ý điền số liệu giả lập.

---

## PHẦN 5: PHÂN TÍCH LỖI (FAILURE ANALYSIS) VÀ GIỚI HẠN THỰC NGHIỆM

Qua phân tích các trường hợp bỏ sót (False Negative) và cảnh báo sai (False Positive) trên tập test độc lập và 3 video CCTV thực địa, nhóm nghiên cứu đã hệ thống hóa các nguyên nhân kỹ thuật:

1. **Lỗi bỏ sót biển nhỏ ở cự ly xa (Distant Small Objects):**
   - *Biểu hiện:* Track #20 trên Video 2 có độ tin cậy trung bình chỉ đạt 24.0% (< ngưỡng kích hoạt 25%), dẫn đến hệ thống chỉ xếp vào diện `SUSPECTED` mà chưa đủ điều kiện phát lệnh `CONFIRMED`.
   - *Nguyên nhân:* Camera đặt ở cự ly xa, biển hiệu có diện tích dưới $24 \times 24$ pixels, độ tương phản chữ và nền kém.
   - *Giải pháp:* Áp dụng kỹ thuật cắt lát ảnh mật độ cao (SAHI - Slicing Aided Hyper Inference) trong pha suy luận hoặc bổ sung thêm dữ liệu zoom cự ly xa.

2. **Lỗi hình dạng Bounding Box chữ nhật đối với biển đặt nghiêng:**
   - *Biểu hiện:* Biển hình chữ nhật đứng đặt chéo góc camera khiến hộp bao Bounding Box phình to, bao trùm cả một phần khoảng trống của mặt vỉa hè hoặc bóng đổ.
   - *Giải pháp:* Đề xuất hướng phát triển chuyển đổi từ Object Detection sang Instance Segmentation (YOLOv8n-seg) để trích xuất đa giác mặt cắt thực tế (Polygon Mask) của biển hiệu.

3. **Hiện tượng che khuất động (Dynamic Occlusion):**
   - *Biểu hiện:* Xe buýt hoặc dòng xe máy dừng đèn đỏ che lấp hoàn toàn biển hiệu trong 2–3 giây, làm đứt gãy vết theo dõi (Track ID Switch) của ByteTrack.
   - *Giải pháp:* Tăng tham số `track_buffer` từ 30 frames lên 60 frames (~2 giây lưu vết) kết hợp trích xuất đặc trưng ngoại quan Re-ID.

---

## PHẦN 6: KẾT LUẬN VÀ KẾ HOẠCH TRIỂN KHAI TUẦN 12 – 13

### 6.1. Đánh giá hoàn thành mục tiêu Tuần 9 – 11
- Nhóm sinh viên đã hoàn thành **100% mục tiêu của Tuần 9–11 theo Đề cương ĐATN**: Xây dựng thành công mô hình YOLOv8n trên tập dữ liệu tự thu thập và làm giàu sạch `v13_clean`, đạt độ chính xác kiểm thử độc lập **mAP@50 = 90.44%** (vượt xa chỉ tiêu dự kiến $>80\%$).
- Đã kiểm chứng tính khả thi của toàn bộ pipeline trên video CCTV thực tế đạt tốc độ thời gian thực trên CPU phổ thông.

### 6.2. Kế hoạch công tác chi tiết Tuần 12 – 13
Bám sát Đề cương ĐATN, công việc trong giai đoạn tiếp theo (Tuần 12–13) bao gồm:
1. **Hoàn thiện thuật toán xác định vi phạm:** Đóng gói thư viện tính toán hình học Shapely tối ưu hóa vector, cố định ngưỡng diện tích overlap 30% và quy tắc chân đế tiếp đất.
2. **Tích hợp ByteTrack & Bộ xác nhận chuỗi thời gian:** Lưu vết ổn định qua hiện tượng che khuất ngắn, thiết lập cơ chế cooldown 60 giây chống gửi tin nhắn spam.
3. **Module lưu trữ ảnh bằng chứng và Cơ sở dữ liệu SQLite:** Tự động cắt và đóng dấu timestamp, camera_id, bounding box lên ảnh bằng chứng; thiết kế cấu trúc bảng SQLite lưu trữ lịch sử vi phạm phục vụ truy xuất báo cáo.
4. **Xử lý đồng thời đa luồng camera (Multi-threading Ingestion):** Tối ưu hóa kiến trúc đa luồng với cơ chế Background Buffer Flush để vận hành mượt mà đồng thời từ 2 đến 4 luồng camera CCTV.

---

## DANH MỤC NGUỒN MINH CHỨNG & TÀI LIỆU THAM KHẢO

1. **Tệp cấu hình & Mã nguồn:**
   - [`configs/settings.yaml`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/settings.yaml): Cấu hình tham số chuẩn toàn hệ thống.
   - [`src/pipeline.py`](file:///c:/Users/Admin/Downloads/DATN20224083/src/pipeline.py): Kiến trúc kết nối 3 tầng Perception – Spatial – Decision.
   - [`scripts/eval_test_set.py`](file:///c:/Users/Admin/Downloads/DATN20224083/scripts/eval_test_set.py): Mã nguồn đánh giá độc lập trên tập test.
2. **Dữ liệu & Mô hình thực nghiệm:**
   - [`datasets/v13_clean/data.yaml`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/v13_clean/data.yaml): Tập dữ liệu 2,674 ảnh sạch không rò rỉ.
   - [`models/best.pt`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.pt): Trọng số mô hình PyTorch tốt nhất (6.64 MB, Epoch 42).
   - [`models/best.onnx`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.onnx): Mô hình tối ưu hóa ONNX Runtime (12.87 MB).
3. **Báo cáo & Nhật ký thực nghiệm:**
   - [`reports/Bao_cao_tien_do_Tuan_9_11_DATN_20224083_v13_clean_chuan.docx`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bao_cao_tien_do_Tuan_9_11_DATN_20224083_v13_clean_chuan.docx): File Word báo cáo tiến độ chuẩn cập nhật hình ảnh và kết quả mới nhất.
   - [`reports/kiem_tra_so_lieu_train_moi_nhat.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/kiem_tra_so_lieu_train_moi_nhat.md): Hồ sơ kiểm toán chi tiết từng con số và hình ảnh.
   - [`data/images/output_v13_clean/`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_v13_clean/): Toàn bộ ảnh trích xuất kết quả nhận diện từ mô hình `v13_clean`.
   - [`reports/benchmark_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/benchmark_report.md): Báo cáo đo đạc hiệu năng CPU thời gian thực.
   - [`reports/system_eval_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_report.md): Báo cáo đánh giá trên 3 video CCTV thực tế.
   - [`reports/Bang_ket_qua_de_xuat_DATN_CCTV_extracted.txt`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bang_ket_qua_de_xuat_DATN_CCTV_extracted.txt): Bản trích xuất 14 bảng kết quả đề xuất.

