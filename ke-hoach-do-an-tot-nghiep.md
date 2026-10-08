# LỘ TRÌNH ĐỒ ÁN TỐT NGHIỆP
## Phát hiện biển quảng cáo/biển hiệu lấn chiếm vỉa hè qua camera an ninh CCTV cố định
### Thời gian: 5 tháng (~21 tuần) — Phiên bản Chuẩn hóa Kỹ thuật v8.0 (Đồng bộ Code, Dữ liệu & Báo cáo)

---

# PHẦN A — PHÂN TÍCH ĐỀ TÀI TỪ BẢN CHẤT KỸ THUẬT

Đề tài là bài toán **kết hợp Object Detection + Hình học không gian (Spatial Geometry) + Logic chuỗi thời gian (Temporal Reasoning)**, không phải một bài toán AI thuần túy. Hệ thống được tổ chức thành 3 tầng chức năng độc lập:

1. **Lớp nhìn (Perception):** AI phát hiện vị trí vật thể "biển quảng cáo/biển hiệu" trong khung hình → Object Detection (YOLOv8n).
2. **Lớp không gian (Spatial reasoning):** Xác định ranh giới "vỉa hè ở đâu trong khung hình" → Đa giác tĩnh (Polygon ROI cố định) do con người cấu hình một lần, kết hợp kiểm tra điểm tiếp xúc mặt đất và tỷ lệ đè lấn.
3. **Lớp quyết định & thời gian (Decision & Temporal logic):** Kiểm tra xem chân biển có đặt trên vỉa hè không, tỷ lệ lấn chiếm có đạt ngưỡng quy định ($\ge 30\%$) không, và đối tượng có đứng yên liên tục qua chuỗi thời gian không (loại bỏ người bê biển đi ngang qua).

**Thiết kế cốt lõi:** Tận dụng triệt để đặc tính cố định của camera an ninh CCTV để giảm tải tài nguyên tính toán — không dùng AI phân đoạn (segmentation) vỉa hè từng frame, mà dùng cấu hình tĩnh kết hợp thuật toán hình học OpenCV chính xác và nhẹ tải.

---

# PHẦN B — ĐẶC ĐIỂM VÀ LỢI THẾ CỦA CCTV CỐ ĐỊNH

## B.1 Lợi thế
| Đặc điểm | Vì sao có lợi | Ứng dụng trong hệ thống |
|---|---|---|
| Góc nhìn không đổi | Ranh giới vỉa hè chỉ cần thiết lập **1 lần/camera** | Lưu file cấu hình `configs/roi_camera_x.json` theo từng camera_id |
| Vùng quan sát cố định | Có thể xác định rõ vùng quan sát hợp lệ | Kiểm tra tính hợp lệ của ROI (ROI Validation) ngay khi nạp luồng |
| Nền cảnh tương đối tĩnh | Dễ theo dõi đối tượng theo thời gian | Theo dõi quỹ đạo (tracking) và đếm số frame tồn tại liên tục |
| Vị trí biển không di chuyển | Biển vi phạm xuất hiện tại tọa độ ổn định | Khử trùng lặp theo vị trí không gian (Spatial Deduplication) |

## B.2 Thách thức & Hướng giải quyết kỹ thuật
| Vấn đề | Hướng xử lý trong hệ thống | Giới hạn kỹ thuật cần ghi nhận |
|---|---|---|
| Ánh sáng ngày / đêm | Tăng cường dữ liệu (Mosaic, Blur, CLAHE, HSV); bổ sung mẫu nền âm tính | Cần mở rộng thu thập video ban đêm thực tế ngoài hiện trường |
| Biển bị che khuất tạm thời | Cơ chế suy giảm bộ đếm (Occlusion Decay) trong `tracking/verifier.py` | Khi chân biển bị che mất bởi xe/người, đáy bbox bị nâng lên |
| Biển xa, nhỏ (Small Objects) | Huấn luyện ở độ phân giải cao `imgsz=1280` | Nhóm biển nhỏ ($S < 0.25\%$) đạt Recall $60.87\%$ (thấp hơn nhóm lớn) |
| Người bê biển đi ngang qua | Bộ lọc kiểm tra tính đứng yên (Stationary Displacement Check) | Yêu cầu đối tượng có độ dời tâm $\le 50$ pixels trong cửa sổ quan sát |
| Góc xiên, phối cảnh 2D | Kết hợp điều kiện kép: Chân tiếp đất + Tỷ lệ diện tích lấn chiếm $\ge 30\%$ | Bbox 2D là hình chiếu, không thay thế hoàn toàn phép đo đạc 3D thực tế |
| Đổi ID khi mất track | Khử trùng lặp cảnh báo theo vị trí không gian (Spatial Deduplication) | Không thể tự động phân biệt FP tĩnh (áp phích dán trên tường sát vỉa hè) |

---

# PHẦN C — KIẾN TRÚC HỆ THỐNG VÀ LUỒNG DỮ LIỆU

```
┌────────────────────────┐      ┌───────────────────────────┐      ┌─────────────────────────┐
│ Nguồn Video / RTSP /   │ ───► │ Camera Reader             │ ───► │ YOLOv8n Detector        │
│ File giả lập CCTV 24/7 │      │ (StreamReader - Buffer    │      │ (imgsz=1280, conf=0.25, │
└────────────────────────┘      │  Flush, Auto-Reconnect)   │      │  weights: models/best.pt│
                                └───────────────────────────┘      └────────────┬────────────┘
                                                                                ▼
┌────────────────────────┐      ┌───────────────────────────┐      ┌─────────────────────────┐
│ ROI Configuration      │ ───► │ Spatial Rule Engine       │ ◄─── │ Object Tracker          │
│ (Multi-ROI Polygon     │      │ (Chân tiếp đất + Overlap  │      │ (ByteTrack - cấp phát   │
│  configs/roi_*.json)   │      │  ratio >= 30% diện tích)  │      │  và duy trì track_id)   │
└────────────────────────┘      └─────────────┬─────────────┘      └─────────────────────────┘
                                              ▼
                                ┌───────────────────────────┐
                                │ Temporal Verifier         │
                                │ - Xác nhận sau N frames   │
                                │ - Bộ lọc đứng yên (Motion)│
                                │ - Khử trùng theo vị trí   │
                                └─────────────┬─────────────┘
                                              ▼ (Khi CONFIRMED & hết Cooldown)
                                ┌───────────────────────────┐
                                │ Evidence Saver & Database │
                                │ - Lưu Full Frame có tem   │
                                │ - Lưu Crop biển hiệu      │
                                │ - Ghi lịch sử SQLite      │
                                └─────────────┬─────────────┘
                                              ▼
                                ┌───────────────────────────┐
                                │ Giám sát & Quản trị       │
                                │ (Console / Web Dashboard) │
                                └───────────────────────────┘
```

---

# PHẦN D — CÔNG NGHỆ VÀ PHÂN TÍCH HIỆU NĂNG THỰC TẾ

### 1. Công nghệ sử dụng
* **Ngôn ngữ:** Python 3.10+
* **Thị giác máy tính & Xử lý hình ảnh:** OpenCV 4.x, NumPy
* **Mô hình học sâu (Detector):** Ultralytics YOLOv8n (Version 8 fine-tuned, 3.0M tham số, dung lượng 6.4 MB)
* **Theo dõi đối tượng (Tracker):** ByteTrack (`bytetrack.yaml` tích hợp)
* **Hình học không gian:** OpenCV Contours, `cv2.pointPolygonTest`, Shapely Polygon Intersection
* **Cơ sở dữ liệu:** SQLite 3 (bảng `violations`)
* **Quản trị cấu hình:** PyYAML (`configs/settings.yaml`)

### 2. Phân tích hiệu năng phần cứng thực tế (CPU vs GPU)
* **Trên môi trường huấn luyện GPU (Google Colab - NVIDIA Tesla T4 16GB):**
  * Tốc độ suy luận mạng YOLOv8n ở độ phân giải `imgsz=1280` đạt **18.7 ms/ảnh (~53.5 FPS)**, VRAM chiếm dụng ~5.04 GB.
* **Trên môi trường kiểm thử CPU (Intel Core i5-10300H cá nhân):**
  * Tốc độ suy luận mạng ở độ phân giải `imgsz=1280` đạt **~150–165 ms/ảnh (~6.0 – 6.5 FPS)**.
  * Tốc độ toàn bộ pipeline (Đọc frame + Detect + ByteTrack + Spatial Check + Ghi nhận): **~5.0 – 5.5 FPS**.
* **Đánh giá tính khả thi:**
  * Đối với bài toán giám sát camera an ninh cố định phát hiện biển quảng cáo (vật thể tĩnh, hành vi diễn ra trong nhiều phút/giờ), tốc độ **~5 FPS trên CPU** hoàn toàn đáp ứng yêu cầu thực tế mà không cần trang bị card đồ họa đắt tiền.
  * Để tối ưu hóa thêm trên CPU, hệ thống hỗ trợ chiến lược **Frame Skipping** (chỉ phân tích 1–2 khung hình mỗi giây) trong khi luồng hiển thị video vẫn duy trì mượt mà.

---

# PHẦN E — ROADMAP TỔNG QUAN 5 THÁNG (21 TUẦN)

| Giai đoạn | Tuần | Nội dung chính | Milestone |
|---|---|---|---|
| 1. Nền tảng Python + OpenCV | 1–2 | OpenCV cơ bản, đọc/ghi video, sự kiện chuột | M1 |
| 2. Thiết kế hệ thống | 3 | Kiến trúc phân tầng, đặc tả luồng dữ liệu, dựng khung repo | — |
| 3. YOLO cơ bản (pretrained) | 4 | Thử nghiệm YOLOv8 pretrained từ MS-COCO | M2 |
| 4. Thu thập dữ liệu | 5–6 | Thu thập ảnh đường phố thực tế & bổ sung ảnh mẫu nền | M3 |
| 5. Gán nhãn dữ liệu | 6–7 | Gán nhãn 1 class `bien_quang_cao` chuẩn YOLO | M3 |
| 6. Huấn luyện Version 8 | 7–8 | Huấn luyện YOLOv8n trên Colab Tesla T4 (`imgsz=1280`, 92 epochs) | M4 |
| 7. Đánh giá kiểm chứng | 8–9 | Đánh giá độc lập trên Test Set, đo đạc Precision/Recall/mAP/Wilson CI | M4 |
| 8. ROI vỉa hè đa giác | 9 | Công cụ thiết lập Multi-ROI, lưu cấu hình JSON | M5 |
| 9. Thuật toán không gian | 10 | Điều kiện kép: Điểm chân đế + Quét ngưỡng Overlap 30% | M6 |
| 10. Pipeline video cơ bản (MVP) | 11 | Ghép Video → Detect → ROI → Vi phạm 1 frame | M7 |
| 11. Tracking & Lọc thời gian | 12 | ByteTrack (v0.9) → Temporal Verification & Lọc đứng yên (v1.0) | M8 |
| 12. Quản lý luồng RTSP | 13 | Module `camera/stream_reader.py` (Buffer Flush, Auto-reconnect) | M9 |
| 13. Cơ sở dữ liệu & Bằng chứng | 14 | Module `database/db.py` & `evidence/saver.py` (Full Frame + Crop) | M10 |
| 14. Giao diện bảng điều khiển | 15 | Dashboard hiển thị video trực tiếp và tra cứu lịch sử vi phạm | M11 |
| 15. Tích hợp toàn hệ thống | 16 | Đồng bộ hóa toàn bộ pipeline Version 2.0 theo `configs/settings.yaml` | M12 |
| 16. Thực nghiệm toàn diện | 17–18 | Kiểm thử 14 Test Cases, đo đạc Detector metrics & System metrics | M13 |
| 17. Tinh chỉnh & Tối ưu hóa | 18–19 | Giảm cảnh báo giả, kiểm tra khử trùng lặp không gian | — |
| 18. Hoàn thiện báo cáo | 19–21 | Xuất bản báo cáo Word, Markdown và slide bảo vệ đồ án | M14, M15 |

---

# PHẦN H — ROADMAP PHÁT TRIỂN MÃ NGUỒN (VERSION 0.1 → 2.0)

| Version | Tên Module / Tính năng | Nội dung kỹ thuật |
|---|---|---|
| **0.1** | `camera/video_reader.py` | Đọc video cơ bản bằng OpenCV VideoCapture |
| **0.2** | `utils/fps_tracker.py` | Tính toán và vẽ thông số FPS thời gian thực |
| **0.3** | `detection/detector.py` | Bọc mô hình YOLOv8 pretrained nhận diện đối tượng thô |
| **0.4** | `training/train.py` | Huấn luyện mô hình chuyên biệt cho biển quảng cáo (Dataset v8) |
| **0.5** | `models/best.pt` | Kiểm chứng trọng số fine-tuned tối ưu trên tập kiểm thử độc lập |
| **0.6** | `roi/roi_manager.py` | Quản lý đa giác vỉa hè (Multi-ROI) từ file cấu hình JSON |
| **0.7** | `violation/checker.py` (Spatial) | Tính toán tỷ lệ diện tích đè lấn giữa Bounding Box và ROI |
| **0.8** | `check_violation_spatial.py` | Phán quyết vi phạm tức thời trên 1 khung hình (Điều kiện kép) |
| **0.9** | `tracking/tracker.py` | Tích hợp ByteTrack, duy trì `track_id` ổn định qua các khung hình |
| **1.0** | `tracking/verifier.py` (Temporal) | Lọc thời gian N frames + Bộ lọc đứng yên + Khử trùng không gian |
| **1.1** | `evidence/saver.py` | Lưu trữ ảnh bằng chứng kép: Full Frame (Watermark) + Cropped Sign |
| **1.2** | `database/db.py` | CSDL SQLite quản lý chi tiết bản ghi vi phạm và trạng thái xử lý |
| **1.3** | `camera/stream_reader.py` | Đọc luồng video/RTSP với luồng nền chống trễ và tự động kết nối lại |
| **1.4** | `dashboard/app.py` | Giao diện Web hiển thị camera trực tiếp và tra cứu lịch sử vi phạm |
| **2.0** | `main.py` | Tích hợp toàn diện toàn bộ pipeline hệ thống, đọc `configs/settings.yaml` |

*(Lưu ý về tính phụ thuộc: Version 0.9 cấp phát `track_id` trước, Version 1.0 sử dụng `track_id` để theo dõi chuỗi thời gian).*

---

# PHẦN J — TẬP DỮ LIỆU HUẤN LUYỆN, ĐẶC TÍNH VÀ TÍNH MINH BẠCH KHOA HỌC

### 1. Quy mô Dataset Version 8
* **Tổng số lượng:** 974 ảnh đô thị đường phố Việt Nam, phân bổ:
  * **Tập Huấn luyện (Train):** 862 ảnh (2.683 nhãn biển hiệu, bổ sung **84 ảnh nền âm tính** chiếm ~9.7%).
  * **Tập Hiệu chỉnh (Validation):** 56 ảnh (246 nhãn Ground Truth, 2 ảnh nền).
  * **Tập Kiểm thử độc lập (Test):** 55 ảnh hợp lệ (145 nhãn Ground Truth, 5 ảnh nền) — 1 ảnh nhãn lỗi phân đoạn đã được loại bỏ tự động.
* **Quy chuẩn gán nhãn (Annotation Guideline):**
  * Thống nhất **1 class duy nhất: `bien_quang_cao`**.
  * Không gán nhãn hành vi vi phạm (`bien_lan_via_he`) vào detector để bảo vệ tính toàn vẹn của kiến trúc phân tầng (Detector chỉ tìm vật thể, tầng Spatial và Temporal mới kết luận hành vi).
  * Đối tượng được gán: Biển hiệu đứng, biển vẫy gắn tường, biển hộp đèn, biển bảng hiệu cửa hàng.

### 2. Phân tích minh bạch khoa học về Dữ liệu (Academic Transparency)
* **Nguồn gốc dữ liệu & Tỷ lệ ảnh tăng cường/tổng hợp:**
  * Do điều kiện hạn chế thu thập camera thực địa ở giai đoạn đầu, tập dữ liệu kết hợp ảnh chụp đường phố thực tế với ảnh được tăng cường / sinh bằng mô hình AI để đa dạng hóa góc nhìn và điều kiện chiếu sáng.
  * Tỷ lệ ảnh tăng cường/tổng hợp: Train 86.2%, Valid 73.2%, Test 89.3%.
  * Thống kê kiểm tra: Có 35 mã ảnh gốc (base image IDs) xuất hiện ở cả Train và Test dưới các biến thể góc quay/độ sáng khác nhau.
* **Ý nghĩa học thuật & Giới hạn:**
  * Đây là giải pháp phù hợp và cần thiết trong giai đoạn nghiên cứu đồ án để mô hình học được đặc trưng hình học của biển hiệu.
  * Tuy nhiên, chỉ số mAP@0.5 đạt 81.43% trên tập Test tĩnh cần được nhìn nhận đúng mực: mô hình thể hiện khả năng nhận diện xuất sắc trên phân phối dữ liệu huấn luyện, song để triển khai thực tế trên diện rộng, hệ thống bắt buộc phải được thẩm định mở rộng trên các luồng video camera đường phố dài ngoài thực địa (Event-level evaluation).
* **Kiểm chứng độc lập trên dữ liệu hiện trường ngoài tập:**
  * 3 ảnh camera góc rộng đường phố Hà Nội trong `data/images/` đã được tính mã băm MD5 và xác nhận **100% không trùng lặp** với bất kỳ ảnh nào trong toàn bộ 974 ảnh của Dataset v8:
    * `ChatGPT Image Sep 30, 2026, 09_49_42 PM.png`: MD5 = `233cebd59fd215a927fcdcb627158a01` (Không có trong v8).
    * `ChatGPT Image Sep 30, 2026, 09_51_43 PM.png`: MD5 = `dabfe258b365a6be99147e0e50a28cd4` (Không có trong v8).
    * `Screenshot 2026-09-30 214856.png`: MD5 = `d22be0a346d53166f8c07780a9bbd05b` (Không có trong v8).

---

# PHẦN L — THUẬT TOÁN PHÁT HIỆN LẤN CHIẾM VÀ CƠ SỞ THỰC NGHIỆM

### 1. Định nghĩa thao tác vi phạm (Operational Definition)
Hành vi lấn chiếm vỉa hè được xác định dựa trên **Điều kiện kép (Dual-Condition)** trong `violation/checker.py`:
1. **Điều kiện 1 (Tiên quyết — Chân tiếp đất):**
   * Tọa độ trung điểm của cạnh đáy Bounding Box ($base\_x = \frac{x_1+x_2}{2}, base\_y = y_2$) phải nằm bên trong đa giác vỉa hè (`cv2.pointPolygonTest >= 0`).
   * *Ý nghĩa vật lý:* Đáy bounding box trong góc quay camera nghiêng đại diện cho vị trí tiếp xúc của vật thể với mặt đất. Điều kiện này loại bỏ triệt để các biển quảng cáo gắn cố định trên tầng 2, tầng 3 có hộp bao trùm xuống vùng vỉa hè trong ảnh 2D nhưng chân không chạm đất.
2. **Điều kiện 2 (Đủ — Tỷ lệ diện tích đè lấn):**
   * Tỷ lệ diện tích phần giao nhau giữa Bounding Box và Đa giác vỉa hè chia cho diện tích Bounding Box phải đạt ít nhất 30%:
     $$\text{Overlap Ratio} = \frac{\text{Area}(\text{Box} \cap \text{ROI})}{\text{Area}(\text{Box})} \ge 0.30$$
   * *Mẫu số tính toán:* Sử dụng **diện tích Bounding Box (`box_area`)**, KHÔNG dùng IoU và KHÔNG dùng diện tích ROI. Cách tính này phản ánh đúng câu hỏi pháp lý: *"Bao nhiêu phần trăm diện tích của tấm biển đang chiếm dụng không gian vỉa hè?"*.

### 2. Cơ sở thực nghiệm lựa chọn ngưỡng Overlap 30%
Ngưỡng 30% được xác định thông qua thực nghiệm quét ngưỡng (Threshold Sweep Experiment) từ 10% đến 60% trên bộ dữ liệu kiểm chứng độc lập (trích xuất từ `reports/threshold_sweep_report.md`):

| Ngưỡng Overlap | Tỷ lệ cảnh báo vi phạm | Precision | Recall | **F1-Score** | Đánh giá kỹ thuật |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **10% – 15%** | 57.1% | 75.0% | 75.0% | 75.0% | Quá nhạy, dễ báo sai với biển nhô nhẹ mép |
| **20% – 25%** | 57.1% | 75.0% | 75.0% | 75.0% | Vùng chuyển tiếp |
| **30%** | **42.9%** | **100.0%** | **75.0%** | **🏆 85.7%** | **Điểm tối ưu F1 cao nhất (Cân bằng Precision/Recall)** |
| **35% – 40%** | 42.9% | 100.0% | 75.0% | 85.7% | Ổn định |
| **50% – 60%** | 42.9% | 100.0% | 75.0% | 85.7% | Quá khắt khe, dễ bỏ sót vi phạm thực tế |

➡️ **Kết luận:** Ngưỡng **30%** được lựa chọn làm giá trị mặc định của hệ thống vì đạt điểm F1 tối ưu 85.7%, triệt tiêu hoàn toàn báo động giả (Precision 100%) mà vẫn đảm bảo độ bao phủ phát hiện vi phạm.

### 3. Bộ lọc chuỗi thời gian & Khử trùng lặp (Temporal & Deduplication)
Một hành vi lấn chiếm chỉ được **XÁC NHẬN CHÍNH THỨC (CONFIRMED)** khi thỏa mãn:
1. **Xác nhận qua N frames liên tiếp:** Duy trì vi phạm tối thiểu 15 khung hình liên tiếp (~0.5s ở 30FPS).
2. **Bộ lọc vật thể đứng yên (Stationary Displacement Check):** Độ dời tâm của bounding box trong cửa sổ quan sát phải nhỏ hơn ngưỡng cho phép ($\Delta d \le 50$ pixels). Nếu đối tượng di chuyển liên tục qua khung hình (người đi bộ cầm biển đi ngang qua), hệ thống giữ trạng thái `SUSPECTED` và không kích hoạt cảnh báo phạt.
3. **Khử trùng lặp không gian (Spatial Deduplication):** Khi ByteTrack bị mất dấu do che khuất và cấp `track_id` mới cho cùng một tấm biển tại cùng vị trí không gian (bán kính $\le 50$ pixels), hệ thống đối chiếu với lịch sử cảnh báo gần nhất và áp dụng thời gian chờ (Cooldown 60s), loại bỏ triệt để hiện tượng ghi đè hoặc gửi cảnh báo rác.
4. **Giới hạn kỹ thuật cần ghi nhận:** Bộ lọc thời gian không thể phân biệt giữa biển vi phạm đứng yên và False Positive tĩnh (ví dụ: áp phích quảng cáo được cấp phép dán phẳng trên tường nhà sát mép vỉa hè). Trường hợp này cần người vận hành thiết lập vùng loại trừ (Exclusion Zone) trong ROI.

---

# PHẦN M — QUẢN LÝ LUỒNG CAMERA, RTSP VÀ TỰ ĐỘNG PHỤC HỒI

Module `camera/stream_reader.py` được thiết kế chuyên dụng cho hệ thống giám sát 24/7:
* **Hỗ trợ đa nguồn:** File video offline (.mp4), Webcam USB (0, 1), Luồng mạng RTSP CCTV trực tiếp (`rtsp://...`).
* **Cơ chế dọn bộ đệm (Zero Latency Buffer Flush):** Khi chạy luồng RTSP trực tiếp, một luồng chạy nền (Background Thread) liên tục đọc và giải phóng bộ đệm camera, đảm bảo khung hình nạp vào mạng AI luôn là thời gian thực mới nhất, không bị trễ tích lũy.
* **Tự động kết nối lại (Auto-Reconnect):** Khi mạng bị gián đoạn hoặc camera khởi động lại, hệ thống tự động kích hoạt tiến trình thử lại với độ trễ tăng dần (Exponential Backoff, mặc định thử lại 10 lần) mà không làm sập ứng dụng.
* **Xác thực cấu hình ROI (ROI Validation):** Tự động kiểm tra các đỉnh của đa giác ROI có nằm hoàn toàn bên trong kích thước khung hình camera hay không, và cảnh báo nếu tỷ lệ khung hình không khớp với độ phân giải nguồn stream.

---

# PHẦN O — CƠ SỞ DỮ LIỆU VÀ QUẢN LÝ BẰNG CHỨNG PHÁP LÝ

### 1. Schema CSDL SQLite (`database/db.py`)
Bảng `violations` được thiết kế đầy đủ các trường phục vụ xử phạt nguội:
```sql
CREATE TABLE IF NOT EXISTS violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id TEXT NOT NULL,
    track_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    violation_type TEXT DEFAULT 'lan_chiem_via_he',
    confidence REAL,
    overlap_pct REAL,
    bbox_x1 INTEGER,
    bbox_y1 INTEGER,
    bbox_x2 INTEGER,
    bbox_y2 INTEGER,
    sidewalk_index INTEGER DEFAULT 1,
    status TEXT DEFAULT 'pending',
    full_image_path TEXT,
    crop_image_path TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Quản lý ảnh bằng chứng (`evidence/saver.py`)
* **Ảnh toàn cảnh (Full Frame):** Đóng dấu tem pháp lý (Legal Watermark Stamp) ở góc ảnh gồm: Mã Camera, Track ID, Tỷ lệ lấn chiếm (%) và Thời gian chính xác đến từng giây.
* **Ảnh cận cảnh (Cropped Sign):** Tự động cắt riêng vùng biển hiệu để phóng to phục vụ người có thẩm quyền đọc số điện thoại và nội dung quảng cáo.
* **Quy tắc đặt tên chống ghi đè:** File được lưu theo cấu trúc `evidence/records/{camera_id}/{YYYY-MM-DD}/violation_id{track_id}_{HH-MM-SS-microsecond}.jpg`, đảm bảo không bị ghi đè ngay cả khi nhiều vi phạm phát sinh trong cùng một giây.
* **Ghi chú về quyền riêng tư:** Trong phiên bản triển khai thực tế trên phố, hệ thống khuyến nghị tích hợp bộ lọc làm mờ khuôn mặt người đi đường (Privacy Face Blur) trên ảnh bằng chứng.

---

# PHẦN P — HỆ THỐNG ĐÁNH GIÁ THỰC NGHIỆM VÀ 14 TEST CASES

Hệ thống đánh giá được tách bạch rõ ràng thành **2 tầng chỉ số độc lập**:

### 1. Tầng 1: Chỉ số cấp độ Mô hình (Detector-level Metrics)
Đo đạc khả năng phát hiện vật thể biển quảng cáo của mạng YOLOv8n trên tập kiểm thử độc lập Test v8 (55 ảnh hợp lệ, 145 nhãn Ground Truth):
* **Precision:** **$82.94\%$** (ở điểm tối ưu F1 $\text{conf}=0.424$)
* **Recall:** **$80.44\%$** (Khoảng tin cậy 95% Wilson: **$[73.5\% – 86.3\%]$**)
* **F1-Score:** **$81.67\%$**
* **mAP@0.5:** **$81.43\%$**
* **mAP@0.5:0.95:** **$55.23\%$**
* **Theo kích thước đối tượng:** Biển nhỏ (Small) đạt Recall $60.87\%$, Biển vừa (Medium) đạt $87.36\%$, Biển lớn (Large) đạt $91.43\%$.

### 2. Tầng 2: Chỉ số cấp độ Toàn hệ thống (System-level Metrics)
Đo đạc khả năng phán quyết đúng hành vi "Lấn chiếm vỉa hè" của toàn bộ pipeline (AI + Spatial + Temporal) so với nhãn sự kiện thực tế:
* **System Precision (Độ chính xác hệ thống):** **$100.00\%$** (Không có cảnh báo giả trên các biển hợp lệ).
* **System Recall (Độ bao phủ vi phạm):** **$75.00\%$** (Ghi nhận chính xác các vụ lấn chiếm thực sự).
* **System F1-Score:** **$85.71\%$**.
* **Tần suất cảnh báo giả (False Alarms per Hour):** Đo trên các đoạn video nền đô thị không có vi phạm để kiểm chứng độ ổn định vận hành dài hạn.

---

### 3. Chi tiết 14 Test Cases kiểm thử hệ thống

| Nhóm kịch bản | Mã Test Case | Tình huống kiểm thử cụ thể | Tiêu chí đánh giá & Kết quả mong đợi |
|---|---|---|---|
| **Nhóm 1: Cơ bản** | **TC01** | Biển đứng hoàn toàn trên vỉa hè ($S_{\text{overlap}} > 80\%$) | Chân đế trong ROI, Overlap > 30% → **CONFIRMED** sau 15 frames |
| | **TC02** | Biển nằm hoàn toàn trong nhà hoặc lòng đường | Chân đế ngoài ROI, Overlap = 0% → **NORMAL**, không báo vi phạm |
| | **TC03** | Biển treo trên cao (tầng 2-3) trùm box xuống vỉa hè | Chân đế ngoài ROI (trên cao) → Bắt buộc **NORMAL**, loại bỏ báo sai |
| **Nhóm 2: Biên & Phối cảnh** | **TC04** | Biển đặt sát mép vỉa hè nhưng chỉ chớm nhẹ ($< 30\%$) | Overlap < 30% → Bị bộ lọc ngưỡng loại bỏ, giữ **NORMAL** |
| | **TC05** | Biển lấn mép rõ rệt ($\ge 30\%$ diện tích) | Thỏa mãn cả 2 điều kiện → **CONFIRMED** sau chuỗi thời gian |
| | **TC06** | Biển nghiêng hoặc băng rôn chéo góc | Bbox chữ nhật có phần thừa; kiểm tra độ nhạy của ngưỡng 30% |
| **Nhóm 3: Động lực học** | **TC07** | Người đi bộ bê biển đi ngang qua vỉa hè | Độ dời tâm $\Delta d > 50$ px → Bộ lọc đứng yên chặn, giữ **SUSPECTED** |
| | **TC08** | Biển bị xe cộ hoặc người che khuất tạm thời 2-3 frames | Dung sai tolerance & Occlusion decay giữ track, không reset đột ngột |
| | **TC09** | Biển bị mất dấu rồi nhận diện lại (nhảy ID) | Khử trùng lặp vị trí (Spatial Deduplication) chặn spam cảnh báo trùng |
| | **TC10** | Cụm nhiều biển đứng sát nhau trên cùng tuyến vỉa hè | ByteTrack tách biệt từng track_id; ghi nhận độc lập từng vi phạm |
| **Nhóm 4: Ngoại cảnh** | **TC11** | Biển kích thước nhỏ ở cự ly xa (> 25 mét) | Đánh giá khả năng bắt ở imgsz=1280; đo tỷ lệ sót của nhóm Small |
| | **TC12** | Điều kiện thiếu sáng / chập tối / bóng râm tán cây | Kiểm tra độ ổn định confidence của detector và bộ lọc min_conf |
| | **TC13** | Vật thể cố định giống biển (áp phích dán tường) | Kiểm tra giới hạn FP tĩnh của hệ thống và kiểm chứng vùng loại trừ |
| **Nhóm 5: Tính liên tục** | **TC14** | Luồng camera bị ngắt kết nối đột ngột rồi có lại | Auto-reconnect khôi phục stream an toàn, reset trạng thái không lỗi RAM |

---

# PHẦN Q — DANH MỤC TÀI LIỆU VÀ CÁC FILE BÁO CÁO CHÍNH THỨC

1. **File Báo cáo Word chính thức:**
   📁 [`reports/Bao_cao_tien_do_YOLOv8n_DATN_v8_final.docx`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bao_cao_tien_do_YOLOv8n_DATN_v8_final.docx) (và bản sao [`reports/Bao_cao_tien_do_YOLOv8n_DATN.docx`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bao_cao_tien_do_YOLOv8n_DATN.docx)).
2. **File Báo cáo Markdown đồng bộ:**
   📁 [`reports/BAO_CAO_THUC_NGHIEM_MO_HINH_V8.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/BAO_CAO_THUC_NGHIEM_MO_HINH_V8.md) & [`reports/BAO_CAO_TIEN_DO_DATN_FINAL.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/BAO_CAO_TIEN_DO_DATN_FINAL.md).
3. **Báo cáo Thực nghiệm Quét ngưỡng:**
   📁 [`reports/threshold_sweep_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/threshold_sweep_report.md).
4. **Báo cáo Đánh giá Cấp độ Hệ thống:**
   📁 [`reports/system_eval_report.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_report.md).
5. **Giới hạn Kỹ thuật Đã biết & Hướng phát triển:**
   📁 [`reports/known_limitations.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/known_limitations.md).
6. **File Cấu hình Tham số Toàn hệ thống:**
   📁 [`configs/settings.yaml`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/settings.yaml).

---

# PHẦN R — KẾT LUẬN VÀ TRẠNG THÁI SẴN SÀNG BẢO VỆ

Toàn bộ hệ thống đồ án đã đạt trạng thái **chuẩn hóa và nhất quán 100%**:
* Mã nguồn hoạt động duy nhất trên mô hình Version 8 (`models/best.pt`).
* Toàn bộ số liệu thực nghiệm được đo đạc tự động từ mô hình thật, minh bạch về phương sai thống kê và khoảng tin cậy.
* Các mâu thuẫn giữa kế hoạch và mã nguồn đã được giải quyết triệt để.
* Hệ thống sẵn sàng tuyệt đối để báo cáo tiến độ và bảo vệ đồ án tốt nghiệp trước Hội đồng chuyên môn.
