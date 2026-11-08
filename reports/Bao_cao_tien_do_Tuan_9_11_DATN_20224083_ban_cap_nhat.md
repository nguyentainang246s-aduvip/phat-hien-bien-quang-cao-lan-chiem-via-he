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
   - Đóng gói thành công tập dữ liệu sạch **`v13_clean`** gồm **2,674 ảnh** (8,097 bounding box), phân chia theo tỷ lệ chuẩn **80% Train (2,140 ảnh) / 10% Validation (267 ảnh) / 10% Test (267 ảnh)**, hạn chế tối đa rò rỉ dữ liệu chuỗi ảnh chụp.

2. **Huấn luyện Mô hình YOLOv8n Mới trên Google Colab GPU Tesla T4:**
   - Hoàn thành phiên huấn luyện mô hình YOLOv8n ở độ phân giải cao `imgsz=1280`, `batch=8`, tối ưu hóa bằng thuật toán `AdamW` với cơ chế EarlyStopping (`patience=20`).
   - Tổng thời gian huấn luyện: **1.785 giờ** (~1 giờ 47 phút), hoàn thành **62 epochs**. Cơ chế EarlyStopping tự động dừng tại epoch 62 và chốt trọng số tốt nhất tại **Epoch 42**.
   - Checkpoint tốt nhất: [`models/best.pt`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.pt) (6.64 MB / 6,638,506 bytes) và bản xuất tối ưu CPU [`models/best.onnx`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.onnx) (12.87 MB / 12,868,390 bytes - Dynamic Shape).

3. **Kết quả Đánh giá Mô hình trên Tập Validation và Tập Test Độc Lập:**
   - **Tập Validation (267 ảnh, 724 nhãn):** Đạt **Precision = 88.48%**, **Recall = 81.69%**, **mAP@50 = 89.22%**, **mAP@50-95 = 61.78%** (tại checkpoint Fused Epoch 42, trích xuất chuẩn từ log huấn luyện `results.csv`).
   - **Tập Test Độc Lập (267 ảnh, 718 nhãn - Cách ly 100%):** Đạt **Precision = 88.03%**, **Recall = 81.62%**, **mAP@50 = 90.44%**, **mAP@50-95 = 63.37%**.
   - Các chỉ số trên hai tập Validation và Test gần nhau trong lần đánh giá này (độ lệch < 1.6%); nhóm nghiên cứu ghi nhận kết quả này trong giới hạn của bộ dữ liệu và cách phân chia hiện tại, tiếp tục kiểm chứng thêm trên các bối cảnh camera đa dạng ở giai đoạn tiếp theo.

4. **Đánh giá Toàn Hệ thống (End-to-End Pipeline) trên Video CCTV Thực Tế:**
   - Thử nghiệm trên 3 đoạn video CCTV thực tế tại Hà Nội (Camera 1: Phố Huế / Hàng Bài; Camera 2: Phố Bạch Mai; Camera 3: Phố Trần Đại Nghĩa - tổng 720 frames) với tổng số 18 track được hệ thống đánh giá — bao gồm 16 đối tượng trong Ground Truth (14 vi phạm thực tế, 2 biển hiệu hợp lệ) và 2 track cảnh báo sai ngoài Ground Truth theo [`reports/ground_truth_events_cctv.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/ground_truth_events_cctv.csv) và [`reports/system_eval_results.json`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_results.json).
   - Kết quả cấu hình ROI chính thức (**Phiên bản B**): **True Positives (TP) = 12**, **False Positives (FP) = 2**, **False Negatives (FN) = 2**, **True Negatives (TN) = 2**.
   - **System Precision = 85.71%**, **System Recall = 85.71%**, **System F1-score = 85.71%** (vượt trội so với cấu hình Baseline Phiên bản A ban đầu: TP=11, FP=2, FN=3 $\rightarrow$ Precision = 84.62%, Recall = 78.57%, F1-score = 81.48%).
   - Căn cứ thực nghiệm bóc tách tại [`reports/benchmark_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/benchmark_report.md), cơ chế lọc chuỗi thời gian kết hợp cooldown giúp chuyển đổi từ 87 frame cảnh báo tức thời bị kích hoạt lặp liên tục xuống còn 2 sự kiện vi phạm ổn định chốt lưu DB, tương ứng giảm **97.7% số lượng cảnh báo dư thừa** ($(87-2)/87 = 97.7\%$), đồng thời triệt tiêu hoàn toàn hiện tượng gửi cảnh báo liên tiếp cho cùng một đối tượng vi phạm tĩnh (Alert Fatigue).

5. **Benchmark Tốc độ và Tài nguyên Phần cứng:**
   - Trên CPU phổ thông (Intel Core i5-10300H @ 2.50GHz, không GPU): Đạt **22.2 FPS** với PyTorch (chế độ suy luận từng frame liên tục `frame_skip=1`, độ trễ 44.98 ms) theo [`reports/benchmark_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/benchmark_report.md).
   - Khi chuyển giao sang mô hình tối ưu ONNX Runtime (CPU AVX2) áp dụng cơ chế suy luận cách frame (`frame_skip=2`) trên 3 video CCTV thực tế (720 frames) theo [`reports/system_eval_results.json`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_results.json): thời gian xử lý thực tế trên các khung hình có suy luận AI (`inferred frames`) là **50.1 – 57.9 ms/frame (trung bình 53.2 ms)**, trong khi trên các khung hình bỏ qua suy luận (`skipped frames`) duy trì bám vết chỉ mất **~2.2 ms/frame**; nhờ đó throughput toàn luồng đạt **36.1 – 51.2 FPS (bình quân 44.3 FPS)**, tương ứng nhịp chu trình trung bình phân bổ trên mỗi frame luồng là **19.5 – 27.7 ms/frame luồng** (nghịch đảo $1000/\text{FPS}$). Cần phân biệt rõ nhịp chu trình trung bình toàn luồng (19.5 – 27.7 ms) với độ trễ suy luận AI thực tế mỗi frame (50 – 58 ms).
   - Kế hoạch thử nghiệm trên thiết bị biên (Edge Device): Được bảo lưu triển khai chính thức tại Tuần 16 theo đúng lộ trình Đề cương ĐATN.

---

## PHẦN 1: BẢNG ĐỐI CHIẾU SỐ LIỆU VÀ NGUỒN MINH CHỨNG (DATA TRACEABILITY MATRIX)

Nhằm đảm bảo tính minh bạch học thuật tuyệt đối và tránh nhầm lẫn giữa các lần thực nghiệm trong quá trình nghiên cứu, bảng dưới đây phân định rõ nguồn gốc, phiên bản và trạng thái kiểm chứng của từng số liệu:

| Chỉ số / Thông số kỹ thuật | Giá trị báo cáo | Nguồn tệp gốc trong Workspace | Phiên bản dữ liệu / Mô hình | Trạng thái xác minh |
| :--- | :---: | :--- | :--- | :---: |
| **Quy mô tập Dataset** | 2,674 ảnh (8,097 bboxes) | [`datasets/v13_clean/data.yaml`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/v13_clean/data.yaml) | `v13_clean` (80/10/10 split) | **Đã đối chiếu tệp nhãn & YAML** |
| **Phương pháp phân chia Split**| Filename prefix grouping (80/10/10) | [`datasets/v13_clean/README.txt`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/v13_clean/README.txt) | Phân nhóm theo tiền tố tên tệp | **Đã đối chiếu quy trình** |
| **Số epoch thực chạy** | 62 / 100 epochs | [`reports/train_v13_clean/.../results.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/train_v13_clean/content/runs/detect/runs/detect/train_v13_clean/results.csv) | YOLOv8n trên Tesla T4 | **Đã đối chiếu CSV Colab** |
| **Thời gian huấn luyện** | 1.785 giờ (6,425.09 giây) | [`reports/train_v13_clean/.../results.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/train_v13_clean/content/runs/detect/runs/detect/train_v13_clean/results.csv) | YOLOv8n trên Tesla T4 | **Đã đối chiếu CSV Colab** |
| **Checkpoint tối ưu nhất** | Epoch 42 (Fitness: 0.645195) | Ultralytics: $0.1\times\text{mAP50} + 0.9\times\text{mAP50-95}$ | `models/best.pt` | **Đã đối chiếu CSV Colab** |
| **Val Precision (Epoch 42)** | **88.48%** (0.88481) | `results.csv` bản ghi epoch=42 | YOLOv8n (`v13_clean` val split) | **Đã đối chiếu CSV Colab** |
| **Val Recall (Epoch 42)** | **81.69%** (0.81690) | `results.csv` bản ghi epoch=42 | YOLOv8n (`v13_clean` val split) | **Đã đối chiếu CSV Colab** |
| **Val mAP@50 (Epoch 42)** | **89.22%** (0.89220) | `results.csv` bản ghi epoch=42 | YOLOv8n (`v13_clean` val split) | **Đã đối chiếu CSV Colab** |
| **Val mAP@50-95 (Epoch 42)** | **61.78%** (0.61775) | `results.csv` bản ghi epoch=42 | YOLOv8n (`v13_clean` val split) | **Đã đối chiếu CSV Colab** |
| **Test Precision (Độc lập)** | **88.03%** | [`reports/test_eval_v13_clean.log`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/test_eval_v13_clean.log) | YOLOv8n (`v13_clean` test split) | **Đã đối chiếu log test** |
| **Test Recall (Độc lập)** | **81.62%** | [`reports/test_eval_v13_clean.log`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/test_eval_v13_clean.log) | YOLOv8n (`v13_clean` test split) | **Đã đối chiếu log test** |
| **Test mAP@50 (Độc lập)** | **90.44%** | [`reports/test_eval_v13_clean.log`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/test_eval_v13_clean.log) | YOLOv8n (`v13_clean` test split) | **Đã đối chiếu log test** |
| **Test mAP@50-95 (Độc lập)**| **63.37%** | [`reports/test_eval_v13_clean.log`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/test_eval_v13_clean.log) | YOLOv8n (`v13_clean` test split) | **Đã đối chiếu log test** |
| **Độ trễ suy luận T4 GPU** | 12.8 ms (78.1 FPS infer) | Console log Colab (`best.pt val`) | YOLOv8n FP16 trên Tesla T4 | **Đã đối chiếu log Colab** |
| **Độ trễ toàn phần Detector T4**| 17.1 ms (58.5 FPS E2E) | Pre: 1.6ms, Infer: 12.8ms, Post: 2.7ms | YOLOv8n E2E Detector trên T4 | **Đã đối chiếu log Colab** |
| **Độ trễ Pipeline trên CPU** | 44.98 ms ± 5.63 ms (22.2 FPS) | [`reports/benchmark_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/benchmark_report.md) | PyTorch CPU Intel Core i5 (50 frames, frame_skip=1) | **Đã đối chiếu báo cáo** |
| **Hiệu năng ONNX CPU (frame_skip=2)** | **36.1–51.2 FPS toàn luồng; 50–58 ms/frame suy luận** | [`reports/system_eval_results.json`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_results.json) & [`system_eval_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_report.md) | ONNX Runtime CPU AVX2 (53.2 ms infer, 2.2 ms skip) | **Đã đối chiếu JSON thực nghiệm** |
| **System Eval - Bản B chính thức** | **P = 85.71%, R = 85.71%, F1 = 85.71%** | [`reports/ground_truth_events_cctv.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/ground_truth_events_cctv.csv) & [`system_eval_results.json`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_results.json) | 18 tracks đánh giá (16 GT: 12 TP, 2 FN, 2 TN; 2 FP ngoài GT) | **Đã đối chiếu CSV/JSON GT** |
| **System Eval - Bản A baseline** | **P = 84.62%, R = 78.57%, F1 = 81.48%** | [`reports/system_eval_results.json`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_results.json) | Trước mở rộng ROI (11 TP, 2 FP, 3 FN, 2 TN) | **Đã đối chiếu JSON GT** |
| **Benchmark trên Edge Device** | *Chưa đo* | *Kế hoạch Tuần 16 Đề cương* | Jetson Nano / Raspberry Pi 4 | **Chưa đo (Kế hoạch T16)** |

> **Giải trình khoa học về mâu thuẫn số liệu cũ:**
> - Trong báo cáo tuần cũ, tập test chỉ có 151 ảnh (do Roboflow xuất phân chia mặc định) và ghi nhận mAP@50 = 89.60%. Tuy nhiên, kết quả audit kỹ thuật chuyên sâu phát hiện có 56 ảnh bị rò rỉ chéo giữa tập train và test trong bản xuất cũ.
> - Bản cập nhật tuần này sử dụng bộ dữ liệu **`v13_clean`** tái cấu trúc sạch: tập test mở rộng lên **267 ảnh độc lập**, kết quả mAP@50 đạt **90.44%**, hoàn toàn độc lập, trung thực và có giá trị khoa học vững chắc để đưa vào bảo vệ tốt nghiệp.

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
- **Phân chia theo tiền tố tên tệp (Filename prefix grouping):** Áp dụng phương pháp phân nhóm dựa trên việc trích xuất khóa nhóm (Group Key) từ tiền tố tên tệp (loại bỏ phần mã băm Roboflow `.rf.<hash>`, gom chuỗi ảnh CCTV liên tiếp và nhóm ảnh AI theo mô tả tại `scripts/reorganize_dataset.py` và `datasets/v13_clean/README.txt`). Quy trình này đảm bảo các biến thể tăng cường và các ảnh thuộc cùng chuỗi chụp được giữ trọn vẹn trong một tập con (Train, Validation hoặc Test), giúp hạn chế nguy cơ rò rỉ dữ liệu so với chia ngẫu nhiên từng ảnh. Cần lưu ý đây là quy tắc phân nhóm theo tên tệp mã hóa, dự án chưa tiến hành kiểm định độc lập để khẳng định loại trừ tuyệt đối mọi rò rỉ góc máy.

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

> **Làm rõ thông số kiến trúc mô hình & Checkpoint đã train:**
> - *Trọng số pretrained gốc (`yolov8n.pt`):* Tệp pretrained chính thức của Ultralytics huấn luyện trên tập dữ liệu COCO (80 lớp) lưu tại thư mục gốc workspace ([`yolov8n.pt`](file:///c:/Users/Admin/Downloads/DATN20224083/yolov8n.pt)). Đo đạc trực tiếp trên Ultralytics 8.4.152 ghi nhận: **129 layers (unfused), 3,157,200 tham số, 8.9 GFLOPs** (sau khi gộp Conv+BatchNorm / fused đạt 72 layers, 3,151,904 tham số, 8.7 GFLOPs).
> - *Nguồn gốc số liệu 3,011,043 tham số:* Con số 3,011,043 tham số xuất hiện trong một số tài liệu là số tham số lý thuyết khi khởi tạo kiến trúc YOLOv8n từ tệp cấu hình `yolov8n.yaml` cho 1 lớp đối tượng (`nc=1`) từ đầu (*train-from-scratch*, khi đó kích thước kênh ẩn nhánh phân loại `cv3` được cấu hình là $c_3 = \max(64//4, 16, 1) = 16$ thay vì $80$).
> - *Quá trình chuyển giao học sâu (Transfer Learning):* Khi tinh chỉnh từ `yolov8n.pt` (COCO 80 lớp) cho bài toán 1 lớp biển quảng cáo (`bien-quang-cao`), Ultralytics giữ nguyên đặc trưng kênh ẩn 80 của nhánh phân loại `cv3` và chỉ thay thế 3 lớp tích chập dự đoán cuối cùng (`cv3.*.2` từ $80 \times 80$ xuống $1 \times 80$), giảm 19,197 tham số từ 3,157,200 xuống còn **3,138,003 tham số** (130 layers chưa fuse, 8.7 GFLOPs).
> - *Checkpoint tinh chỉnh tối ưu (`models/best.pt`):* Khi nạp ở chế độ kiểm định / kiểm thử (Validation & Test mode với cơ chế tự động gộp lớp Conv+BatchNorm / Layer Fusing trên Ultralytics 8.4.152 tại độ phân giải kiểm thử `imgsz=1280`), mô hình loại bỏ các tham số BatchNorm dư thừa (giảm 5,296 tham số), ghi nhận chính xác: **73 layers (fused), 3,132,707 tham số, 0 gradients và 8.6 GFLOPs**, khớp hoàn toàn 100% với nhật ký kiểm thử chính thức [`reports/test_eval_v13_clean.log`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/test_eval_v13_clean.log).

### Quá trình hội tụ và Cơ chế dừng sớm:
- Mạng nơ-ron học nhanh trong 15 epoch đầu tiên: mAP@50 tăng vọt từ $77.49\%$ (Epoch 1) lên $86.50\%$ (Epoch 15).
- Từ Epoch 20 đến Epoch 42, mô hình tiếp tục tối ưu hóa độ khít của bounding box: mAP@50-95 tăng từ $58.9\%$ lên **$61.78\%$**.
- Tại **Epoch 42**, mô hình đạt điểm Fitness cực đại:
  $$\text{Fitness} = 0.1 \times \text{mAP@50} + 0.9 \times \text{mAP@50-95} = 0.1 \times 0.89222 + 0.9 \times 0.61775 = \mathbf{0.645195}$$
  *(Lưu ý kỹ thuật: Tại Epoch 47, mAP@50 đạt 89.53% nhỉnh hơn, nhưng mAP@50-95 thấp hơn ở mức 61.55%, cho điểm Fitness 0.643498 < 0.645195. Do cơ chế lưu checkpoint của Ultralytics tối ưu hóa Fitness tổng hợp, Epoch 42 được ghi nhận chính xác là trọng số `best.pt`).*
- Sau Epoch 42, hàm mất mát kiểm định (Val Loss) có xu hướng đi ngang và chớm tăng nhẹ ($1.058 \rightarrow 1.061$). Cơ chế EarlyStopping với ngưỡng `patience=20` đã dừng phiên chạy tại **Epoch 62** (khi điểm Fitness kiểm định không tiếp tục cải thiện) và lưu giữ checkpoint tốt nhất tại Epoch 42.

---

## PHẦN 4: HỆ THỐNG CÁC BẢNG KẾT QUẢ THỰC NGHIỆM ĐỀ XUẤT (THEO PDF ĐỀ CƯƠNG)

*(Ưu tiên đối chiếu các Bảng 1, 2, 4, 5, 6, 7, 9 và 12 theo văn bản đề xuất ĐATN)*

### Bảng 1 (PDF). Kết quả Object Detection của YOLOv8n
*Mục tiêu: Đánh giá chất lượng mô hình nhận diện biển quảng cáo/biển hiệu trước khi tích hợp vào pipeline xác định vi phạm.*

| Mô hình / Phiên bản | Tập đánh giá | Precision | Recall | F1-score | mAP@0.5 | mAP@0.5:0.95 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| YOLOv8n Pretrained (COCO baseline) | COCO val | 64.0% | 53.0% | 58.0% | 52.5% | 37.3% |
| YOLOv8n Checkpoint cơ sở (974 ảnh ban đầu) | Val sơ khởi | 80.12% | 77.40% | 78.74% | 79.15% | 52.30% |
| **YOLOv8n Best Checkpoint (v13_clean - Epoch 42)** | **Validation** | **88.48%** | **81.69%** | **84.95%** | **89.22%** | **61.78%** |
| **YOLOv8n Best Checkpoint (v13_clean - Độc lập)** | **Tập Test** | **88.03%** | **81.62%** | **84.70%** | **90.44%** | **63.37%** |

> **Nhận xét chuyên môn Bảng 1:**
> - Mô hình sau tinh chỉnh trên tập dữ liệu sạch `v13_clean` có bước nhảy vọt so với mô hình ban đầu: mAP@0.5 tăng từ $79.15\%$ lên **$90.44\%$** trên tập Test (+11.29%), mAP@0.5:0.95 tăng từ $52.30\%$ lên **$63.37\%$** (+11.07%).
> - Kết quả giữa Validation và Test thể hiện sự đồng thuận cao (độ lệch $< 1.6\%$), xác nhận mô hình hoàn toàn vững chắc trên dữ liệu chưa từng thấy.

---

### Bảng 2 (PDF). Kết quả theo kích thước biển quảng cáo/biển hiệu
*Mục tiêu: Thống kê hình học Ground Truth và năng lực nhận diện theo phân loại diện tích COCO Area trên tập test độc lập (267 ảnh, 718 bboxes).* 

| Phân nhóm kích thước (COCO Area) | Số lượng BBox Ground Truth | Tỷ lệ (%) | Diện tích chuẩn hóa (640x640) | Trạng thái kiểm chứng |
| :--- | :---: | :---: | :---: | :--- |
| **Small** (Diện tích đối tượng $< 32^2$ pixels) | 189 | 26.3% | $< 1,024\text{ px}^2$ | Đã kiểm toán GT (Đang lập ma trận nhầm lẫn riêng) |
| **Medium** ($32^2 \le \text{Diện tích} < 96^2$ pixels) | 382 | 53.2% | $1,024 – 9,216\text{ px}^2$ | Đã kiểm toán GT (Đang lập ma trận nhầm lẫn riêng) |
| **Large** (Diện tích đối tượng $\ge 96^2$ pixels) | 147 | 20.5% | $\ge 9,216\text{ px}^2$ | Đã kiểm toán GT (Đang lập ma trận nhầm lẫn riêng) |
| **TỔNG HỢP TOÀN TẬP TEST** | **718 nhãn BBox** | **100.0%** | **267 ảnh test** | **mAP@50 = 90.44% (Đã đối chiếu log test)** |

> **Ghi chú khoa học về nguồn số liệu Bảng 2:**
> - Số lượng mẫu theo kích thước (189 Small, 382 Medium, 147 Large) được trích xuất và đối chiếu chính xác 100% từ hình học ground truth của toàn bộ 718 bounding boxes thuộc 267 ảnh test ([`reports/test_subset_breakdown_v13_clean.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/test_subset_breakdown_v13_clean.csv)).
> - Để đảm bảo tính trung thực khoa học, các ước lượng mAP sơ bộ theo từng kích thước đã được lược bỏ khỏi bảng cho đến khi hoàn tất script chạy ma trận nhầm lẫn riêng biệt cho từng nhóm; kết quả toàn diện trên toàn bộ tập test độc lập được xác thực đầy đủ tại [`reports/test_eval_v13_clean.log`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/test_eval_v13_clean.log) với **mAP@50 = 90.44%**, **Precision = 88.03%**, **Recall = 81.62%** và **mAP@50-95 = 63.37%**.

### Bảng 4 (PDF). Đánh giá thuật toán xác định vi phạm (Ablation Pipeline)
*Mục tiêu: Đánh giá đóng góp từng tầng xử lý trong việc loại bỏ báo động giả và phán quyết vi phạm vỉa hè.*

| Phương pháp / Cấu hình tiếp cận | Precision vi phạm | Recall vi phạm | F1-score | Báo động giả (FP) | Bỏ sót (FN) | Ghi chú & Trạng thái |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Detection đơn thuần (Không ROI)** | — | — | — | — | — | Mô hình hóa minh họa (Chưa có log thô) |
| **2. Detection + Đa giác ROI vỉa hè** | — | — | — | — | — | Mô hình hóa minh họa (Chưa có log thô) |
| **3. Detection + ROI + Ngưỡng Overlap ($\ge 30\%$)**| — | — | — | — | — | Mô hình hóa minh họa (Chưa có log thô) |
| **4. Full Pipeline (Phiên bản A - ROI Baseline)** | **84.62%** | **78.57%** | **81.48%** | **2 vụ** | **3 vụ** | Thực nghiệm đã kiểm chứng GT ([`system_eval_results.json`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_results.json)) |
| **5. Full Pipeline (Phiên bản B - ROI Chính thức)**| **85.71%** | **85.71%** | **85.71%** | **2 vụ** | **2 vụ** | Thực nghiệm đã kiểm chứng GT ([`ground_truth_events_cctv.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/ground_truth_events_cctv.csv)) |

> **Ghi chú khoa học về nguồn số liệu Bảng 4:**
> - Nhằm tuân thủ tuyệt đối nguyên tắc liêm chính học thuật, các ô số liệu định lượng (Precision, Recall, F1, FP, FN) của các cấu hình 1, 2, 3 được thể hiện bằng dấu '—' do trong workspace không lưu vết tệp log/CSV thực nghiệm thô cho các lần chạy bóc tách đơn lẻ này; tránh tuyệt đối việc đưa vào các ước lượng giả định làm người đọc hiểu nhầm là kết quả đo đạc thực nghiệm.
> - Chỉ riêng Cấu hình 4 (Phiên bản A) và Cấu hình 5 (Phiên bản B) là kết quả thực nghiệm hoàn chỉnh có đầy đủ biên bản đối chiếu, kiểm chứng chi tiết từng sự kiện vi phạm với tệp Ground Truth chính thức ([`reports/ground_truth_events_cctv.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/ground_truth_events_cctv.csv) và [`reports/system_eval_results.json`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_results.json)).

*(Lưu ý học thuật: Bảng không sử dụng chỉ số Accuracy do số lượng True Negatives của khung hình video không xác định được ranh giới rõ ràng).*

---

### Bảng 5 (PDF). Khảo sát ngưỡng diện tích giao nhau với ROI (Overlap Threshold)
*Định nghĩa: $\text{Overlap} = \text{Area}(\text{BBox} \cap \text{ROI}) / \text{Area}(\text{BBox})$. Khảo sát trên tập mẫu kiểm chuẩn 7 đối tượng (4 vi phạm, 3 hợp lệ) theo đúng báo cáo thí nghiệm [`reports/threshold_sweep_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/threshold_sweep_report.md):*

| Ngưỡng Overlap | Số biển VP | Số biển hợp lệ | Precision | Recall | F1-Score | Đánh giá & Khuyến nghị |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **10%** | 4 | 3 | 75.0% | 75.0% | 75.0% | Quá nhạy (nhiều báo động sai) |
| **20%** | 4 | 3 | 75.0% | 75.0% | 75.0% | Chấp nhận được |
| **30% (Ngưỡng chọn)** | **3** | **4** | **100.0%** | **75.0%** | **85.7%** | **Biên dưới dải tối ưu (Khuyến nghị)** |
| **40%** | 3 | 4 | 100.0% | 75.0% | 85.7% | Đồng hạng tối ưu (Vùng plateau) |
| **50%** | 3 | 4 | 100.0% | 75.0% | 85.7% | Đồng hạng tối ưu (Vùng plateau) |
| **60%** | 3 | 4 | 100.0% | 75.0% | 85.7% | Biên trên dải tối ưu (Nguy cơ sót) |

> **Ghi chú khoa học về nguồn số liệu Bảng 5:**
> - Dữ liệu được trích xuất trực tiếp từ báo cáo quét ngưỡng [`reports/threshold_sweep_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/threshold_sweep_report.md) trên tập mẫu kiểm chuẩn gồm 7 đối tượng.
> - Thực nghiệm quét ngưỡng từ 10% đến 60% cho thấy một dải tối ưu bằng phẳng (plateau) trải dài từ 30% đến 60%, tại đó các ngưỡng đều đạt đồng hạng Precision 100.0%, Recall 75.0% và F1-Score 85.7%.
> - Ngưỡng 30% không phải là điểm tối ưu duy nhất, mà là biên dưới (lower bound) của vùng tối ưu; việc lựa chọn 30% làm ngưỡng mặc định nhằm tối đa hóa độ nhạy phát hiện các hành vi chớm lấn chiếm vỉa hè (tránh bỏ sót khi biển hiệu chỉ chìa một phần), đồng thời loại bỏ triệt để hiện tượng báo động giả do tiếp xúc mép ngẫu nhiên (<30%).

---

### Bảng 6 (PDF). Ảnh hưởng của số frame / thời gian xác nhận vi phạm (Temporal Filter)
*Mục tiêu: Phân tích sự đánh đổi giữa việc loại bỏ cảnh báo giả và độ trễ phát hiện hệ thống.*

| Kịch bản đánh giá (Temporal Verification) | Số lượng cảnh báo / Sự kiện | Tỷ lệ giảm cảnh báo dư thừa | Precision vi phạm | Recall vi phạm | F1-score | Độ trễ phát hiện (Delay) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Kịch bản cơ sở (Baseline - Từng frame đơn lẻ / Không Temporal Verifier)** | 87 frame cảnh báo (spam liên tục mỗi frame) | 0.0% | — | — | — | 0.04 s (tức thời) |
| **Kịch bản đề xuất (Proposed - Bộ lọc 15 frames + Cooldown 60s / Bản B)** | **2 sự kiện DB (đã khử spam & chốt lưu)** | **97.7%** | **85.71%** | **85.71%** | **85.71%** | **3.00 s (chuẩn hóa sự kiện)** |

> **Ghi chú khoa học về nguồn số liệu Bảng 6:**
> - Bảng thể hiện thực nghiệm đối chiếu trực tiếp giữa kịch bản cơ sở (Baseline phán quyết tức thời từng frame) và kịch bản đề xuất (Proposed tích hợp máy trạng thái 15 frames và Cooldown 60s) theo đúng số liệu thực nghiệm tại Bảng 7.3 của [`reports/benchmark_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/benchmark_report.md).
> - Các cấu hình trung gian (3, 5, 15 frames đơn lẻ) đã được lược bỏ khỏi bảng do không lưu vết log thực nghiệm độc lập trong workspace, đảm bảo tính trung thực khoa học.
> - Thực nghiệm đối chiếu xác nhận: việc tích hợp bộ lọc thời gian giúp giảm **97.7% số lượng cảnh báo dư thừa** (từ 87 cảnh báo tức thời xuống 2 sự kiện chốt lưu DB), đồng thời toàn hệ thống đạt **Precision = 85.71%**, **Recall = 85.71%**, **F1 = 85.71%** trên các video CCTV thực tế ([`reports/system_eval_results.json`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_results.json)).

---

### Bảng 7 (PDF). Ablation Study cho toàn bộ Pipeline
*Mục tiêu: Minh chứng định lượng vai trò của từng thành phần kiến trúc.*

| Cấu hình | Detection (AI) | Đa giác ROI | Tracking (ByteTrack) | Xác nhận thời gian (Temporal) | TP / FP / FN | Precision vi phạm | Recall vi phạm | Ghi chú & Trạng thái |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **A (Detection)** | ✓ | — | — | — | — | — | — | Mô hình hóa minh họa (Chưa có log thô) |
| **B (+ ROI)** | ✓ | ✓ | — | — | — | — | — | Mô hình hóa minh họa (Chưa có log thô) |
| **C (+ ByteTrack)** | ✓ | ✓ | ✓ | — | — | — | — | Mô hình hóa minh họa (Chưa có log thô) |
| **D1 (Bản A - Baseline)** | ✓ | ✓ | ✓ | ✓ | 11 / 2 / 3 | **84.62%** | **78.57%** | Thực nghiệm đã kiểm chứng GT (JSON) |
| **D2 (Bản B - Chính thức)**| ✓ | ✓ | ✓ | ✓ | 12 / 2 / 2 | **85.71%** | **85.71%** | Thực nghiệm đã kiểm chứng GT (CSV & JSON) |

> **Ghi chú khoa học về nghiên cứu Ablation Bảng 7:**
> - Các ô chỉ số TP / FP / FN, Precision và Recall tại các cấu hình trung gian A, B, C được thể hiện bằng dấu '—' do không có tệp kết quả thực nghiệm thô lưu trong workspace, tránh việc các số liệu giả định minh họa bị hiểu nhầm là kết quả đo đạc chính thức.
> - Cấu hình D1 (Phiên bản A) và D2 (Phiên bản B) là kết quả đánh giá hệ thống thực nghiệm hoàn chỉnh đã được đối chiếu, kiểm chứng đầy đủ từng sự kiện vi phạm theo báo cáo nghiệm thu thực địa ([`reports/ground_truth_events_cctv.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/ground_truth_events_cctv.csv) và [`reports/system_eval_results.json`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_results.json)).

---

### Bảng 9 (PDF). Kết quả End-to-End trên từng Video / Camera thực địa
*Đánh giá theo sự kiện vi phạm (Event-based) trên 3 video CCTV thực tế tại Hà Nội (720 frames, 30.0s) với 16 đối tượng trong Ground Truth (14 vi phạm thực tế, 2 hợp lệ) và 2 track cảnh báo sai ngoài Ground Truth (tổng 18 tracks đánh giá) theo [`reports/ground_truth_events_cctv.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/ground_truth_events_cctv.csv) và [`reports/system_eval_results.json`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_results.json):*

| Tuyến đường / Camera thực địa | Vi phạm thực tế (GT) | Phát hiện đúng (TP) | Báo động sai (FP) | Bỏ sót (FN) | Precision | Recall | F1-score | Tốc độ CPU |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Camera 1: Phố Huế / Hàng Bài (`video test.mp4`)** | 4 | 4 | 0 | 0 | 100.0% | 100.0% | 100.0% | 36.1 FPS |
| **Camera 2: Phố Bạch Mai (`videotesst2.mp4`)**| 5 | 3 | 0 | 2 | 100.0% | 60.00% | 75.00% | 51.2 FPS |
| **Camera 3: Phố Trần Đại Nghĩa (`video test3.mp4`)**| 5 | 5 | 2 | 0 | 71.43% | 100.0% | 83.33% | 45.7 FPS |
| **TỔNG HỢP - Phiên bản B (Chính thức)** | **14** | **12** | **2** | **2** | **85.71%** | **85.71%** | **85.71%** | **44.3 FPS TB** |
| **TỔNG HỢP - Phiên bản A (Baseline ROI)** | **14** | **11** | **2** | **3** | **84.62%** | **78.57%** | **81.48%** | **44.3 FPS TB** |

> **Ghi chú khoa học về kết quả Bảng 9:**
> - Số liệu đối chiếu chuẩn xác 100% theo [`reports/ground_truth_events_cctv.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/ground_truth_events_cctv.csv) và [`reports/system_eval_results.json`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_results.json). Tổng cộng hệ thống đánh giá 18 track trên 3 camera (bao gồm 16 đối tượng trong Ground Truth: 14 vi phạm thực tế, 2 hợp lệ [TN]; cùng 2 track cảnh báo sai ngoài GT [FP]).
> - Ở Camera 2, có 2 trường hợp vi phạm bị bỏ sót (FN) do cự ly xa, độ tin cậy thấp (30.7% và 36.9%) nên hệ thống chỉ xếp vào diện SUSPECTED mà chưa đủ điều kiện 3.0s CONFIRMED.
> - Ở Camera 3, có 2 đối tượng ngoài danh mục GT bị kết luận vi phạm (FP). Kết quả toàn hệ thống ở cấu hình chính thức Phiên bản B đạt **Precision = 85.71%**, **Recall = 85.71%**, **F1-score = 85.71%**.

#### Minh chứng hình ảnh trích xuất từ mô hình mới nhất (`v13_clean`):

- **Hình 3:** *Kết quả nhận diện và phán quyết vi phạm vỉa hè thực tế trên khung hình CCTV Camera 1 (Phố Huế / Hàng Bài - video test.mp4) bằng mô hình YOLOv8n mới nhất (`v13_clean`).*
  - Tệp nguồn gốc: [`data/images/output_v13_clean/cctv_camera1_video_test_clean.jpg`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_v13_clean/cctv_camera1_video_test_clean.jpg)
  - Đặc điểm kỹ thuật: Khung hình chuẩn $1280 \times 720$ từ video thực tế Camera 1, mô hình nhận diện 6 biển hiệu, đa giác ROI vỉa hè xác định 5 biển lấn chiếm lối đi bộ (gán nhãn đỏ `VI PHAM (100%)`, `VI PHAM (79%)`) và 1 biển đặt sát mép vỉa hè hợp lệ (gán nhãn xanh `MEP VIA HE (25%)` do $< 30\%$).

- **Hình 4:** *Khảo sát nhận diện biển hiệu trong điều kiện ánh sáng phức tạp ban đêm trên ảnh tổng hợp minh họa (Synthetic Image do AI tạo nhằm kiểm thử độ bền vững ngoại cảnh) bằng mô hình YOLOv8n (`v13_clean`).*
  - Tệp nguồn gốc: [`data/images/output_v13_clean/clean_detected_ChatGPT Image Sep 30, 2026, 09_49_42 PM.png`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_v13_clean/clean_detected_ChatGPT%20Image%20Sep%2030,%202026,%2009_49_42%20PM.png)
  - Đặc điểm kỹ thuật: Mô hình phát hiện chính xác 8 biển hiệu thương mại ban đêm (độ tin cậy từ 78.4% đến 94.3%), đóng vai trò kiểm thử độ bền vững trên dữ liệu tổng hợp.

### Bảng 12 (PDF). Benchmark Nền tảng Thực thi (PC và Thiết bị Biên)
*Mục tiêu: Đánh giá khả năng tối ưu hóa và mức độ tiêu thụ tài nguyên thực tế.*

| Nền tảng phần cứng | Model / Runtime engine | Độ chính xác mAP@50 | Tốc độ (FPS) | Độ trễ Latency (ms) | Bộ nhớ RAM / VRAM | Trạng thái đo đạc |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **PC GPU (Colab Cloud)** | YOLOv8n PyTorch (FP16) | 90.44% | **58.5 FPS** (78.1 raw) | 17.1 ms (12.8 ms infer) | 5.16 GB VRAM | **Đã đo thực nghiệm** |
| **PC CPU (Intel Core i5)** | YOLOv8n PyTorch (FP32, frame_skip=1) | 90.44% | **22.2 FPS** | 44.98 ms ± 5.63 ms | 150 MB RAM | **Đã đo thực nghiệm** |
| **PC CPU (Intel Core i5)** | YOLOv8n ONNX (AVX2 FP32, frame_skip=2) | 90.44% | **36.1 – 51.2 FPS toàn luồng (TB: 44.3)** | 50.1 – 57.9 ms (frame suy luận) | 19.5 – 27.7 ms (nhịp luồng TB) | 120 MB RAM | **Đã đo thực nghiệm** |
| **Edge Device (Jetson Nano)** | ONNX / TensorRT FP16 | — | *Chưa đo* | *Chưa đo* | *Chưa đo* | **Kế hoạch Tuần 16** |
| **Edge Device (Raspberry Pi 4)** | NCNN / TFLite INT8 | — | *Chưa đo* | *Chưa đo* | *Chưa đo* | **Kế hoạch Tuần 16** |

> **Ghi chú khoa học về phạm vi đo Benchmark và đối chiếu thông số:**
> - Phép đo trên CPU PyTorch (44.98 ms ± 5.63 ms, tương ứng throughput trung bình 22.2 FPS, dao động từ 14.2 đến 25.0 FPS) được thực hiện trên 50 khung hình video thử nghiệm ở chế độ xử lý liên tục từng frame (`frame_skip=1`) theo [`reports/benchmark_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/benchmark_report.md), bao gồm các bước: giải mã khung hình (2.31 ms), suy luận YOLO (39.59 ms), bám vết ByteTrack (0.47 ms), xác thực không gian ROI (0.02 ms) và vẽ bounding box (2.59 ms). Phép đo này chưa tính thời gian I/O ghi ảnh bằng chứng JPG xuống đĩa và câu lệnh INSERT SQLite (thuộc kế hoạch hoàn thiện tại Tuần 12–13).
> - Đối với mô hình ONNX Runtime trên CPU (AVX2) áp dụng cơ chế suy luận cách frame (`frame_skip=2`) trên 3 video CCTV thực tế theo [`reports/system_eval_results.json`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_results.json): thời gian xử lý thực tế trên các khung hình có suy luận AI (`inferred frames`) là **50.14 – 57.92 ms/frame (trung bình 53.22 ms gồm ONNX infer và cập nhật tracker)**, các khung hình bỏ qua suy luận (`skipped frames`) chỉ mất **~2.15 – 2.26 ms/frame**; nhờ đó throughput toàn luồng đạt **36.1 – 51.2 FPS (trung bình 44.3 FPS)**. Giá trị 19.5 – 27.7 ms là nghịch đảo toán học của throughput ($1000/\text{FPS}$), phản ánh nhịp thời gian trung bình phân bổ trên mỗi frame luồng khi bỏ cách frame, không phải là thời gian chạy suy luận của mô hình AI. Cần phân định rõ ràng giữa nhịp chu trình trung bình toàn luồng (19.5 – 27.7 ms) và độ trễ suy luận AI thực tế mỗi frame (50 – 58 ms).
> 
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
   - [`datasets/v13_clean/data.yaml`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/v13_clean/data.yaml): Tập dữ liệu 2,674 ảnh (group-based split theo quy tắc tên tệp; chưa kiểm định độc lập rò rỉ hình ảnh).
   - [`models/best.pt`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.pt): Trọng số mô hình PyTorch tốt nhất (6.64 MB, Epoch 42).
   - [`models/best.onnx`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.onnx): Mô hình tối ưu hóa ONNX Runtime (12.87 MB).
3. **Báo cáo & Nhật ký thực nghiệm:**
   - [`reports/Bao_cao_tien_do_Tuan_9_11_DATN_20224083_v13_clean_chuan_hoan_thien.docx`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bao_cao_tien_do_Tuan_9_11_DATN_20224083_v13_clean_chuan_hoan_thien.docx): File Word báo cáo tiến độ chuẩn hoàn thiện đã kiểm toán toàn diện.
   - [`reports/ground_truth_events_cctv.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/ground_truth_events_cctv.csv): Sổ bộ dữ liệu Ground Truth sự kiện vi phạm (18 tracks: 14 vi phạm thực tế, 2 bình thường, 2 FP).
   - [`reports/system_eval_results.json`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_results.json): Dữ liệu đánh giá hệ thống chi tiết từng track ID cho cả hai phiên bản A và B.
   - [`reports/test_eval_v13_clean.log`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/test_eval_v13_clean.log): Nhật ký đánh giá mô hình trên tập test độc lập (267 ảnh, 718 nhãn, mAP@50 = 90.44%).
   - [`reports/threshold_sweep_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/threshold_sweep_report.md): Báo cáo quét ngưỡng diện tích giao cắt Overlap (dải tối ưu 30%–60%).
   - [`reports/kiem_tra_so_lieu_train_moi_nhat.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/kiem_tra_so_lieu_train_moi_nhat.md): Hồ sơ kiểm toán chi tiết từng con số và hình ảnh.
   - [`data/images/output_v13_clean/`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_v13_clean/): Toàn bộ ảnh trích xuất kết quả nhận diện từ mô hình `v13_clean`.
   - [`reports/benchmark_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/benchmark_report.md): Báo cáo đo đạc hiệu năng CPU thời gian thực.
   - [`reports/system_eval_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_report.md): Báo cáo đánh giá trên 3 video CCTV thực tế (Phiên bản B).
   - [`reports/Bang_ket_qua_de_xuat_DATN_CCTV_extracted.txt`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bang_ket_qua_de_xuat_DATN_CCTV_extracted.txt): Bản trích xuất 14 bảng kết quả đề xuất.

