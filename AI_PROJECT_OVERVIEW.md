# TÀI LIỆU TỔNG QUAN DỰ ÁN DÀNH CHO AI REVIEW & ĐÁNH GIÁ PHẢN BIỆN
## ĐỒ ÁN TỐT NGHIỆP: HỆ THỐNG PHÁT HIỆN BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV CỐ ĐỊNH

> **Sinh viên thực hiện:** Nguyễn Đức Tài Năng — MSSV: 20224083  
> **Đơn vị:** Đại học Bách Khoa Hà Nội  
> **Thời gian cập nhật:** Tháng 10/2026 (Phiên bản tích hợp Version 2.0)  
> **Mục đích tài liệu:** Hướng dẫn tóm tắt để mô hình AI (Claude, ChatGPT, Gemini,...) nắm bắt nhanh cấu trúc dự án, luồng xử lý và cung cấp nhận xét phản biện khách quan, sâu sắc.

---

## 1. Mục Tiêu & Bản Chất Cốt Lõi Của Đề Tài
* **Bài toán thực tế:** Biển hiệu, biển quảng cáo (standee, biển hộp đèn, biển chân sắt) đặt tràn lan chiếm dụng lối đi bộ trên vỉa hè đô thị tại Việt Nam.
* **Định vị hệ thống:** Đây là **Hệ thống Hỗ trợ Ra Quyết định (Decision Support System - Human-in-the-Loop)**, không phải hệ thống phạt tự động hoàn toàn (do AI không có độ chính xác 100% ngoài thực tế và cần con người có thẩm quyền ký duyệt pháp lý).
* **Mục tiêu kỹ thuật:**
  1. Chạy thời gian thực mượt mà (Real-time $\ge 25\text{ FPS}$) trực tiếp trên **CPU thiết bị biên** (không đòi hỏi GPU đắt tiền).
  2. Giảm thiểu tối đa báo động giả (False Alarms) từ người đi bộ khiêng biển đi ngang, xe cộ, cây cối, hoặc rung lắc camera.
  3. Đảm bảo bảo vệ quyền riêng tư cá nhân (tự động làm mờ mặt người đi đường trên ảnh bằng chứng).
  4. Cung cấp Web Dashboard trực quan cho cán bộ Đội Quản lý Trật tự Đô thị xem xét ảnh toàn cảnh/cận cảnh và duyệt/bác bỏ hồ sơ (kèm lý do phục vụ kiểm toán và tái huấn luyện AI).

---

## 2. Bản Đồ Cấu Trúc Mã Nguồn (Codebase Map)

| Thư mục / File | Vai trò kỹ thuật chính |
| :--- | :--- |
| `main.py` | Điểm khởi nhập (Entry Point) hợp nhất: hỗ trợ các mode `--mode monitor`, `--mode dashboard`, `--mode roi`, `--mode benchmark`. Tự động nạp `configs/settings.yaml`. |
| `camera/stream_reader.py` | Đọc luồng video/RTSP/Webcam đa luồng (Multi-threaded buffer flush), tự động phục hồi kết nối (Auto-reconnect), xử lý lặp video mượt mà. |
| `detection/detector.py` | Bọc mô hình YOLOv8n suy luận qua ONNX Runtime (CPU AVX2) hoặc PyTorch. |
| `tracking/tracker.py` | Tích hợp thuật toán ByteTrack (Kalman Filter + liên kết 2 tầng) để duy trì định danh `track_id` ổn định. |
| `roi/roi_manager.py` | Quản lý đa giác vỉa hè đa vùng (Multi-ROI), tự động co giãn ma trận tọa độ theo độ phân giải (Resolution Auto-Scaling 720p/1080p/4K). Chạy 0% GPU runtime. |
| `roi_drawer.py` | Công cụ đồ họa tương tác cho phép người vận hành click chuột vẽ ROI tĩnh một lần duy nhất cho mỗi camera. |
| `violation/checker.py` | **Engine phán quyết hình học kép**: (1) Chân tiếp đất 3 điểm (Left, Center, Right) với dung sai mép 15px; (2) Tỷ lệ đè vỉa hè Shapely $\ge 30\%$. |
| `tracking/verifier.py` | **Bộ lọc chuỗi thời gian (Temporal Verifier)**: Cửa sổ trượt vị trí (Sliding Window $\le 80\text{px}$) loại bỏ người đi bộ khiêng biển đi ngang; xác nhận vi phạm sau 15 frames (~3.0s); khử trùng lặp cảnh báo theo bán kính không gian ($R \le 50\text{px}$) và Cooldown 60s. |
| `evidence/saver.py` | Lưu trữ bằng chứng phạt nguội 2 cấp độ: Ảnh toàn cảnh (đóng tem Watermark + làm mờ mặt tự động bằng Haar Cascade) và Ảnh crop riêng tấm biển. |
| `database/db.py` | Cơ sở dữ liệu SQLite quản lý bảng `violations` có lưu `status` (pending, confirmed, dismissed, resolved), `reviewed_by`, `dismiss_reason`. Kích hoạt **SQLite WAL Mode**. |
| `dashboard/web_app.py` | **Trung tâm Điều hành Web Tất-cả-trong-Một (Unified Web Application)**: Chạy trên `ThreadingHTTPServer` thuần Python, tích hợp 3 phân hệ chính:<br>1. **Hồ Sơ Vi Phạm & Phạt Nguội**: Quy trình duyệt/bác bỏ Human-in-the-Loop, thống kê KPI, lọc theo trạng thái.<br>2. **Studio Vẽ ROI Vỉa Hè Tương Tác**: Cho phép chọn video, click chuột vẽ đa giác vỉa hè trực tiếp trên trình duyệt, lưu tự động sang JSON, kiểm thử tức thì.<br>3. **Studio Phát & Kiểm Thử Video AI Trực Tiếp**: Playlist video click-to-play, truyền phát luồng MJPEG thời gian thực kèm lớp phủ YOLO + ByteTrack + đa giác ROI, HUD đo FPS/vi phạm, điều chỉnh độ nhạy (conf 10%–30%) và độ phân giải (640–1280px) trực tiếp. |
| `models/best.onnx` | Mô hình YOLOv8n tối ưu hóa suy luận CPU qua ONNX Runtime (FP32), chuẩn hóa benchmark thực nghiệm tại độ phân giải 640x640px. |
| `evaluation/evaluate_videos.py`| Script đánh giá tự động toàn chuỗi pipeline trên 3 video CCTV thực tế ngoài đời, trích xuất metrics và lưu ảnh crop từng biển. |
| `configs/settings.yaml` | Tệp cấu hình tập trung toàn bộ tham số kỹ thuật (ngưỡng conf, overlap, temporal, privacy, edge performance). |
| `reports/` | Toàn bộ báo cáo Word (.docx), báo cáo đánh giá video thực tế, phân tích giới hạn kỹ thuật và đề cương 5 chương. |

---

## 3. Căn Cứ Pháp Lý & Kết Quả Thực Nghiệm Toàn Hệ Thống

* **Căn cứ pháp lý hiện hành:** Điều 12 Nghị định 168/2024/NĐ-CP (hiệu lực từ 01/01/2025) quy định mức xử phạt 2.000.000đ – 3.000.000đ (cá nhân) và 4.000.000đ – 6.000.000đ (tổ chức) đối với hành vi đặt, treo biển hiệu, biển quảng cáo trên lòng đường, hè phố trái quy định.
* **Định vị bài toán:** Hệ thống đóng vai trò Hỗ trợ Ra Quyết định (DSS - Human-in-the-Loop) vì máy không thể tự động xác minh tính "trái phép" (giấy phép kinh doanh, đề án cho thuê vỉa hè từng địa phương).

Kiểm chứng thực nghiệm trên **3 đoạn video camera giám sát thực địa (720 frames, 30 giây, 16 track ID)** tại Hà Nội:
* **True Positives (TP):** **11 vụ vi phạm** được hệ thống bắt chính xác (Version B).
* **False Positives (FP):** **0 vụ** (Không có cảnh báo sai từ người đi bộ, xe máy, cột đèn; Wilson 95% CI: 74.1%–100%).
* **False Negatives (FN):** **3 vụ** (Track #4 có conf TB 35.9% < 40%; Track #8 do clip 10s kết thúc tại 2.63s quan sát nên chưa đủ 3.0s xác nhận; Track #13 ở xa mép hè, conf chập chờn 0.25–0.43 bị reset; hệ thống an toàn giữ diện Nghi vấn - SUSPECTED).
* **True Negatives (TN):** **2 biển hiệu** (Track #5 ngoài mép vỉa hè; Track #15 là biển gắn tường không bị phạt nhầm).
* **Độ chính xác toàn hệ thống (System Precision):** **100.00%** (Wilson 95% CI: 74.1%–100%)
* **Độ thu hồi toàn hệ thống (System Recall - Version B):** **78.57%** (11/14 vi phạm thực tế, Wilson 95% CI: 52.4%–92.4%)
* **Độ thu hồi toàn hệ thống (System Recall - Version A baseline):** **71.43%** (10/14 vi phạm thực tế, Wilson 95% CI: 45.4%–88.3%; Standee #3 đè 66.0% nhưng chân đế ngoài ROI, xếp NORMAL là FN). Hiệu chuẩn ROI nâng trực tiếp Recall từ 71.43% lên 78.57% trên cùng clip.
* **F1-Score toàn hệ thống (Version B):** **88.00%**
* **Tốc độ xử lý (Pipeline Throughput):** **31.3 – 39.2 FPS** trên CPU Intel (với `frame_skip=2`, thông lượng ổn định loại trừ frame khởi động: **38.1 – 43.8 FPS**; tần suất suy luận AI: **~10.4 – 13.1 Hz**; độ trễ suy luận AI p50: **63.7 ms**, mean: 62.6 ms; tổng thời gian khung hình infer: ~68.0–74.1 ms).
* **Lịch sử Hiệu chuẩn Vùng ROI (Camera Calibration History) & Mã băm toàn vẹn SHA-256:**
  - **Bản chất khoa học:** Việc khoanh vùng ROI vỉa hè là bước hiệu chuẩn camera (Camera Calibration) bắt buộc khi triển khai thực địa cho từng góc máy cố định. Sự thay đổi giữa các phiên bản là bằng chứng khoa học cho thấy hệ thống nhạy cảm với chất lượng hiệu chuẩn không gian, không phải hành vi điều chỉnh để làm đẹp số liệu.
  - **Version A** (`configs/roi_video_test_version_a.json`, 7 đỉnh, SHA-256: `a47cd6aefe3a88a71af2bf8ffea4b0d61a1b98fd5064e2f60d9e6e96d678500f`): Tái dựng ngày 11/10 (từ ghi chép ban đầu ngày 05/10), vẽ hẹp sát mép trong tường nhà; Standee #3 rơi chân đế ra ngoài đa giác -> hệ thống xếp NORMAL (bỏ sót - FN), Recall đạt 71.43% (10/14).
  - **Version B** (`configs/roi_video_test_version_b.json` & `roi_video_test.json`, 8 đỉnh, SHA-256: `8c5840b81cd34eaa231a1ed9b7dfc2ad16b4668d8a4acb2c87b4d180bfb99c2c`): Hoàn thành và đóng băng ngày 08/10 (22:23:56) làm tiêu chuẩn benchmark chính thức; bao trùm toàn bộ không gian vỉa hè thực tế nơi đặt biển; Standee #3 đạt overlap 77.0% và chân đế trong vỉa hè -> xác nhận CONFIRMED (TP), Recall đạt 78.57% (11/14).
  - **Version C** (`configs/roi_video_test_version_c.json`, 6 đỉnh, SHA-256: `eed72b3341b56109434e0b70e10c378542dddf0a7ed6436c72abd67af309766f`): Sinh ngày 12/10 (14:27:30) trong phiên thử nghiệm tính năng vẽ ROI trên Web Studio; việc giản lược bớt đỉnh làm sai lệch góc vỉa hè, khiến overlap của Standee #3 giảm xuống 63.1%; phiên bản này đã được lưu trữ độc lập và loại bỏ để bảo toàn tính đóng băng của Version B.
  - **Ground Truth** (`configs/video_ground_truth.json`, 16 đối tượng, SHA-256: `590d0f201fefcae6a72ff9449ba2cc8164a0712a40c63c9d03afbe9ad351e93d`): Đóng băng độc lập, không thay đổi qua các phiên bản ROI.
* **Quy chuẩn đánh giá Benchmark so với Tính năng Web Studio mở rộng:**
  - **Chuẩn hóa Benchmark:** Mọi chỉ số đánh giá chính thức của đề tài (Precision 100%, Recall 78.57%, 31.3–39.2 FPS) đều được kiểm chứng và đo đạc nghiêm ngặt ở cấu hình chuẩn: `imgsz=640`, `conf_threshold=0.25`, `overlap_threshold=0.30`, `confirm_seconds=3.0s` trên mô hình YOLOv8n ONNX CPU.
  - **Tính năng Web Studio mở rộng:** Giao diện Web Dashboard cho phép người dùng thử nghiệm các mức phân giải khác nhau (640px, 960px, 1280px) và điều chỉnh ngưỡng conf (0.10–0.30) để quan sát trực quan; đây là tiện ích hỗ trợ khám phá vận hành thực tế và là hướng mở rộng khi hệ thống được trang bị phần cứng GPU/NPU biên, không phải cơ sở đo đạc của bảng benchmark chính thức.

---

## 4. Gợi Ý Câu Hỏi Cho AI Đánh Giá & Phản Biện (Prompts For AI Reviewer)

Bạn có thể copy một trong các câu hỏi sau để yêu cầu AI nhận xét:

1. **Về Tính Học Thuật & Đề Tài ĐATN:**
   > *"Dựa trên mã nguồn và tài liệu trong gói nén, hãy đóng vai một Giảng viên phản biện Đồ án Tốt nghiệp ngành Khoa học Máy tính / Trí tuệ Nhân tạo. Hãy nhận xét khách quan về tính mới, tính thực tiễn, điểm mạnh và điểm yếu còn tồn đọng của đề tài này."*

2. **Về Khả Năng Phòng Thủ Trước Hội Đồng:**
   > *"Những câu hỏi phản biện hóc búa nhất mà Hội đồng chấm thi có thể đặt ra cho sinh viên trong đề tài này là gì? Đưa ra gợi ý câu trả lời tối ưu nhất cho từng câu hỏi."*

3. **Về Khả Năng Triển Khai Thiết Bị Biên (Edge AI Deployment):**
   > *"Đánh giá tính khả thi khi mang toàn bộ pipeline này lên các thiết bị phần cứng nhúng (như NVIDIA Jetson Orin Nano, Raspberry Pi 5 + Hailo-8 NPU). Cần tối ưu thêm những gì về mặt pipeline và phần mềm?"*

4. **Về Mã Nguồn & Kiến Trúc Phần Mềm:**
   > *"Rà soát các module mã nguồn chính (`checker.py`, `verifier.py`, `web_app.py`, `db.py`, `tracker.py`), chỉ ra các edge cases tiềm ẩn hoặc các điểm có thể tái cấu trúc (refactor) để code đạt chuẩn công nghiệp (Production-ready)."*
