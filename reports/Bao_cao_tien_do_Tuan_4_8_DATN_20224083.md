# BÁO CÁO TIẾN ĐỘ ĐỒ ÁN TỐT NGHIỆP
## GIAI ĐOẠN: TUẦN 4 – TUẦN 8 (TỔNG HỢP VIDEO THỬ NGHIỆM, GÁN NHÃN DATASET & THIẾT LẬP ROI ĐA CAMERA)
### BẢN CẬP NHẬT CHUẨN HÓA HỌC THUẬT

---

### THÔNG TIN CHUNG
* **Tên đề tài:** Hệ thống giám sát và phát hiện biển quảng cáo/biển hiệu lấn chiếm vỉa hè qua camera CCTV cố định
* **Sinh viên thực hiện:** Nguyễn Đức Tài Năng — MSSV: 20224083 — Lớp: Điện tử 11 – K67
* **Thành viên phối hợp:** Đinh Văn Tuấn — Lớp: Điện tử 11 – K67
* **Đơn vị đào tạo:** Đại học Bách Khoa Hà Nội
* **Thời gian thực hiện:** Giai đoạn Tuần 4 – Tuần 8 (Theo Kế hoạch Đề cương ĐATN 17 tuần khóa 2026.1)
* **Nhiệm vụ trọng tâm theo Đề cương:**
  1. Thu thập video các tuyến phố có biển quảng cáo/biển hiệu lấn vỉa hè.
  2. Gán nhãn dữ liệu trên Roboflow, đạt tối thiểu 1.000 ảnh chuẩn YOLO.
  3. Hoàn thiện ROI cho nhiều camera dựa trên các góc quay thực tế.
* **Tiêu chuẩn nghiệm thu đề ra:** Dataset $\ge 1.000$ ảnh sẵn sàng train; ROI khớp với các camera thật ngoài hiện trường.

---

> [!NOTE]
> **KẾT LUẬN ĐỐI CHIẾU TIẾN ĐỘ TUẦN 4–8:**
> Căn cứ đối chiếu trực tiếp với dữ liệu lưu trữ trong workspace: Nhóm nghiên cứu đã thực hiện các nội dung kỹ thuật trọng tâm của giai đoạn Tuần 4–8:
> - **Tổng hợp 6 đoạn video clip camera giám sát (CCTV) mẫu phục vụ thử nghiệm** (720p HD, 24 fps, 10.0 giây/video) phản ánh các góc nhìn quan sát hè phố đô thị;
> - **Đóng gói và kiểm toán cấu trúc tập dữ liệu sạch `v13_clean` đạt 2.674 ảnh** (vượt chỉ tiêu quy mô $\ge 1.000$ ảnh, đạt **267,4%**), 8.097 nhãn BBox đạt cú pháp chuẩn YOLO 5 cột, 201 ảnh nền âm tính (7,52%), **0 lỗi cú pháp nhãn**;
> - **Hoàn thiện 6 tệp cấu hình Đa giác ROI vỉa hè** (Static Polygon ROI & Multi-ROI) và kiểm tra trực quan trên khung hình đại diện của cả 6 video thử nghiệm.
> - **Ghi nhận minh bạch các giới hạn khoa học:** việc đồng bộ trực tiếp Roboflow API chưa thực hiện do môi trường cục bộ chưa cấu hình API key; các video clip đóng vai trò là dữ liệu mẫu phục vụ kiểm thử học thuật chưa đại diện toàn bộ mạng lưới camera giao thông; và việc phân chia split dựa trên tiền tố tên tệp duy nhất chưa kiểm định độc lập về mức độ cô lập góc máy.

---

## 1. NHIỆM VỤ 1: THU THẬP VIDEO PHỤC VỤ THỬ NGHIỆM HỆ THỐNG

Để phục vụ việc kiểm thử thuật toán và đánh giá mô hình thị giác máy tính trong bài toán giám sát đô thị, nhóm nghiên cứu đã tổng hợp 6 đoạn video clip camera giám sát (CCTV) mẫu phục vụ thử nghiệm hệ thống (test benchmark clips), được lưu trữ tại thư mục [`data/videos/`](file:///c:/Users/Admin/Downloads/DATN20224083/data/videos/).

### Nguồn gốc dữ liệu video:
Các đoạn clip video mẫu được tổng hợp từ nguồn dữ liệu công khai trên Internet / mạng xã hội và camera giám sát cộng đồng (nguồn chưa xác minh độc lập giấy phép bản quyền gốc hoặc biên bản khảo sát hiện trường); nhóm nghiên cứu không trực tiếp lắp đặt hoặc vận hành các camera vật lý này ngoài thực địa. Trong đó:
- 3 video đầu ([`video test.mp4`](file:///c:/Users/Admin/Downloads/DATN20224083/data/videos/video%20test.mp4), [`videotesst2.mp4`](file:///c:/Users/Admin/Downloads/DATN20224083/data/videos/videotesst2.mp4), [`video test3.mp4`](file:///c:/Users/Admin/Downloads/DATN20224083/data/videos/video%20test3.mp4)) phản ánh bối cảnh góc nhìn tương ứng khu vực các tuyến phố kinh doanh tại Hà Nội (khu vực Phố Huế / Hàng Bài, Bạch Mai, Trần Đại Nghĩa);
- 3 video bổ sung ([`videotest4.mp4`](file:///c:/Users/Admin/Downloads/DATN20224083/data/videos/videotest4.mp4), [`videotest5.mp4`](file:///c:/Users/Admin/Downloads/DATN20224083/data/videos/videotest5.mp4), [`videotest6.mp4`](file:///c:/Users/Admin/Downloads/DATN20224083/data/videos/videotest6.mp4)) ghi nhận các luồng camera quan sát đường phố đô thị có biển hiệu ven đường.

### Mục đích sử dụng và tính riêng tư:
Video được sử dụng thuần túy cho mục đích nghiên cứu học thuật, phi thương mại trong khuôn khổ Đồ án tốt nghiệp; **video không được dùng để nhận dạng cá nhân; hình ảnh có thể ghi nhận người đi đường và phương tiện giao thông ngoài ý muốn**.

### Mô tả đúng giới hạn của căn cứ pháp lý:
Về mặt nghiệp vụ đô thị, bài toán được xây dựng dựa trên cơ sở tham khảo [Điều 12 Nghị định 168/2024/NĐ-CP trên Cổng TTĐT Chính phủ](https://xaydungchinhsach.chinhphu.vn/toan-van-nghi-dinh-168-2024-nd-cp-quy-dinh-xu-phat-vi-pham-hanh-chinh-ve-trat-tu-atgt-duong-bo-119241231164556785.htm) (quy định xử phạt vi phạm hành chính đối với hành vi đặt, treo biển hiệu, biển quảng cáo lấn chiếm lòng đường, hè phố). Quy định này được dùng làm căn cứ tham khảo định hình bài toán "phát hiện dấu hiệu nghi vấn biển quảng cáo/biển hiệu lấn chiếm hè phố". Cần lưu ý rằng hệ thống AI chỉ đóng vai trò cảnh báo sớm dấu hiệu nghi vấn; việc xác định và kết luận hành vi vi phạm pháp luật chính thức thuộc thẩm quyền của cơ quan chức năng sau khi kiểm tra bối cảnh cụ thể, đo đạc thực tế và xem xét các quy định cấp phép sử dụng tạm thời hè phố (nếu có). Nghị định 168/2024/NĐ-CP không phải là văn bản cấp quyền thu thập hay sử dụng dữ liệu video cho dự án.

### Bảng 1. Danh mục 6 Video CCTV Mẫu Thử Nghiệm trong Workspace

| Camera / Video ID | Bối cảnh quan trắc | Độ phân giải | FPS | Thời lượng | Đặc điểm góc nhìn | Cấu hình ROI tương ứng |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| [`video test.mp4`](file:///c:/Users/Admin/Downloads/DATN20224083/data/videos/video%20test.mp4) | Bối cảnh Phố Huế / Hàng Bài, Q. Hoàn Kiếm | 1280×720 | 24.0 | 10.0s (240f) | Góc ngang hướng vỉa hè thương mại | [`roi_video_test.json`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/roi_video_test.json) |
| [`videotesst2.mp4`](file:///c:/Users/Admin/Downloads/DATN20224083/data/videos/videotesst2.mp4) | Bối cảnh Phố Bạch Mai, Q. Hai Bà Trưng | 1280×720 | 24.0 | 10.0s (240f) | Góc nghiêng 45° vỉa hè & cửa hàng | [`roi_videotesst2.json`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/roi_videotesst2.json) |
| [`video test3.mp4`](file:///c:/Users/Admin/Downloads/DATN20224083/data/videos/video%20test3.mp4) | Bối cảnh Phố Trần Đại Nghĩa, Q. Hai Bà Trưng | 1280×720 | 24.0 | 10.0s (240f) | Góc cao nhìn xuống vỉa hè trước quán | [`roi_video_test3.json`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/roi_video_test3.json) |
| [`videotest4.mp4`](file:///c:/Users/Admin/Downloads/DATN20224083/data/videos/videotest4.mp4) | Luồng camera quan sát đô thị (Cam 4) | 1280×720 | 24.0 | 10.0s (240f) | Góc trực diện nhìn trục đường hai bên | [`roi_videotest4.json`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/roi_videotest4.json) |
| [`videotest5.mp4`](file:///c:/Users/Admin/Downloads/DATN20224083/data/videos/videotest5.mp4) | Luồng camera quan sát đô thị (Cam 5) | 1280×720 | 24.0 | 10.0s (240f) | Góc cận cảnh dãy cửa hàng kinh doanh | [`roi_videotest5.json`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/roi_videotest5.json) |
| [`videotest6.mp4`](file:///c:/Users/Admin/Downloads/DATN20224083/data/videos/videotest6.mp4) | Luồng camera quan sát đô thị (Cam 6) | 1280×720 | 24.0 | 10.0s (240f) | Góc toàn cảnh trục đường giao thông | [`roi_videotest6.json`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/roi_videotest6.json) |

---

## 2. NHIỆM VỤ 2: GÁN NHÃN VÀ ĐÓNG GÓI DATASET CHUẨN YOLO

Dữ liệu hình ảnh được quản lý và gán nhãn trên nền tảng **Roboflow** (Workspace: `tai-nang-nguyen-duc`, Project: `sidewalk-signboard-detection-1`, Version 13 theo tài liệu nguồn [`datasets/v13/README.roboflow.txt`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/v13/README.roboflow.txt) và [`datasets/raw_images/SOURCES.md`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/raw_images/SOURCES.md)).

Do phiên làm việc môi trường cục bộ hiện tại không cấu hình biến môi trường `ROBOFLOW_API_KEY`, các thao tác đồng bộ trực tuyến API được tạm thời đóng băng, và toàn bộ dữ liệu đã được xuất bản, làm sạch và đóng gói hoàn chỉnh thành tập dữ liệu cục bộ [`datasets/v13_clean/`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/v13_clean/).

### Bảng 2. Thống kê Chi tiết Cơ cấu Tập Dữ liệu `v13_clean` Đã Kiểm toán

| Tập con (Split) | Số lượng ảnh | Tỷ lệ phân chia | Ảnh nền âm tính (BG) | Số nhãn BBox (GT) | Định dạng nhãn |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tập Huấn luyện (Train)** | 2.140 ảnh | 80,03% | 164 ảnh (7,66%) | 6.655 boxes | YOLO 5 cột (`0 cx cy w h`) |
| **Tập Kiểm định (Validation)** | 267 ảnh | 9,99% | 17 ảnh (6,37%) | 724 boxes | YOLO 5 cột (`0 cx cy w h`) |
| **Tập Kiểm thử Độc lập (Test)** | 267 ảnh | 9,99% | 20 ảnh (7,49%) | 718 boxes | YOLO 5 cột (`0 cx cy w h`) |
| **TỔNG CỘNG TOÀN BỘ** | **2.674 ảnh** | **100,0%** | **201 ảnh (7,52%)** | **8.097 boxes** | **100% HỢP LỆ** |

> [!TIP]
> **Đặc điểm phân chia tập dữ liệu và giải trình con số 1.327 tiền tố tên tệp duy nhất:**
> Áp dụng phương pháp phân chia dựa trên quy tắc tiền tố tên tệp (*filename prefix grouping*: bóc tách đuôi băm Roboflow `.rf.<hash>` theo [`scripts/reorganize_dataset.py`](file:///c:/Users/Admin/Downloads/DATN20224083/scripts/reorganize_dataset.py)). Khi chuẩn hóa 2.674 ảnh bằng cách bỏ chuỗi mã băm, tập dữ liệu ghi nhận đúng **1.327 tiền tố tên tệp duy nhất** (*unique filename prefixes*).
> 
> Sự chênh lệch so với giả định 1.337 cặp (nếu chia đôi từ 2.674) xuất phát từ việc chính sách tăng cường (*augmentation*) trên Roboflow không sinh đều đúng 2 phiên bản cho mọi ảnh:
> - **933 nhóm tiền tố** có đúng 2 phiên bản ảnh (tương ứng **1.866 ảnh**).
> - **307 nhóm tiền tố** chỉ có 1 ảnh duy nhất không qua tăng cường (**307 ảnh**).
> - **87 nhóm tiền tố** còn lại có từ 3 đến 13 ảnh (**501 ảnh**).
> - Tổng cộng: $1.866 + 307 + 501 = \mathbf{2.674}$ ảnh thuộc 1.327 nhóm tiền tố tên tệp duy nhất.
> 
> *Lưu ý khoa học:* Đây là quy ước phân nhóm hình thức theo tiền tố tên tệp mã hóa; phép đếm này chưa tự chứng minh chúng hoàn toàn là 1.327 ảnh nguồn độc lập về bối cảnh thực địa, đồng thời dự án chưa kiểm định độc lập về mức độ cô lập tuyệt đối mọi góc quay hay bối cảnh thực địa giữa các split.

> [!NOTE]
> **Cơ sở kỹ thuật tích hợp 201 mẫu nền âm tính (Negative Background Samples):**
> Theo tài liệu kỹ thuật chính thức của Ultralytics ([Ultralytics YOLO Docs: Tips for Best Training Results - Background Images](https://docs.ultralytics.com/yolov5/tutorials/tips-for-best-training-results)):
> *"Background images are images with no objects that are added to a dataset to reduce False Positives. Ultralytics recommends ~0-10% background images to help reduce FPs (COCO has 1000 background images for reference, 1% of total)"*.
> 
> Nhóm nghiên cứu đã tích hợp **201 bức ảnh nền âm tính thuần túy** (chiếm 7,52% toàn bộ dataset, nằm trong dải khuyến nghị 0%–10%). Các mẫu này bao gồm: hè phố trống vắng ban đêm, cửa cuốn nhà dân đóng kín, tường hoa, mái tôn không có biển hiệu, nhằm giúp mạng nơ-ron giảm thiểu các kích hoạt cảnh báo giả (*False Positives*) ở vùng hậu cảnh tĩnh không có biển hiệu.

### Bảng 3. Bảng Kiểm toán Toàn vẹn Cấu trúc Dataset YOLO theo Quy chuẩn Ultralytics

| Hạng mục kiểm tra | Quy chuẩn kỹ thuật Ultralytics | Kết quả thực tế đo đạc trong Workspace | Đánh giá nghiệm thu |
| :--- | :--- | :--- | :---: |
| **Cấu hình `data.yaml`** | Khai báo `nc: 1`, `names: ['bien-quang-cao']`, đường dẫn split | `nc: 1`, `names: {0: 'bien-quang-cao'}`, cấu trúc đường dẫn phân cấp chuẩn | **ĐẠT CHUẨN** |
| **Quy tắc Mirror Rule** | Ánh xạ 1:1 giữa thư mục `images/` và `labels/` | 2.674 ảnh đều có tệp nhãn tương ứng (2.674 tệp `.txt`, không thiếu tệp) | **ĐẠT CHUẨN** |
| **Cú pháp nhãn BBox** | Chuẩn 5 cột: `class_id cx cy w h` | 100% nhãn đúng 5 cột, tọa độ chuẩn hóa trong khoảng $[0, 1]$ | **ĐẠT CHUẨN** |
| **Tỷ lệ mẫu âm tính** | Khuyến nghị Ultralytics: 0% – 10% ảnh nền (COCO ~1%) | 201 ảnh nền âm tính (chiếm 7,52% toàn bộ dataset) | **ĐẠT CHUẨN** |
| **Quy mô ảnh huấn luyện** | Tối thiểu 1.000 ảnh sẵn sàng train | **2.674 ảnh** (1.327 tiền tố tên tệp duy nhất) | **VƯỢT CHỈ TIÊU (267%)** |
| **Kiểm toán cấu trúc cú pháp** | 0 lỗi cú pháp, 0 box ngoài ranh giới $[0, 1]$ | Kiểm tra bằng [`datasets/validate_dataset.py`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/validate_dataset.py): Exit code 0, 0 cảnh báo | **ĐẠT CÚ PHÁP (VALID SYNTAX)** |

### Minh chứng Trực quan Gán nhãn YOLO & Ảnh nền Âm tính

![Mẫu ảnh gán nhãn chuẩn YOLO trích xuất từ datasets/v13_clean/train/](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/roboflow_sample_annotated.jpg)
*Hình 1. Mẫu ảnh gán nhãn chuẩn YOLO (5 cột: class_id cx cy w h) trích xuất trực tiếp từ datasets/v13_clean/train/ (Tệp nguồn: [`reports/figures/roboflow_sample_annotated.jpg`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/roboflow_sample_annotated.jpg)).*

![Lưới mẫu nền âm tính thuần túy từ datasets/v13_clean/train/](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/negative_samples_grid.jpg)
*Hình 2. Lưới 4 mẫu nền âm tính thuần túy (Negative Background Samples, nhãn rỗng 0 byte) trích xuất trực tiếp từ datasets/v13_clean/train/ (Tệp nguồn: [`reports/figures/negative_samples_grid.jpg`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/negative_samples_grid.jpg)).*

---

## 3. NHIỆM VỤ 3: THIẾT LẬP ROI ĐA CAMERA VÀ KIỂM TRA TRỰC QUAN

Để hệ thống thị giác máy tính có căn cứ không gian phán quyết hành vi lấn chiếm hè phố, nhóm nghiên cứu đã thiết lập các tệp cấu hình **Đa giác ROI vỉa hè (Static Polygon ROI & Multi-ROI)** riêng biệt cho từng camera tại thư mục [`configs/`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/). Các đa giác này đã được cấu hình và kiểm tra trực quan trên khung hình đại diện của cả 6 video thử nghiệm, bao trọn phần không gian hành lang vỉa hè dành cho người đi bộ quan sát được qua ống kính camera từ chân tường nhà dân đến mép bo vỉa hè tiếp giáp lòng đường xe chạy.

### Bảng 4. Đặc tả Kỹ thuật 6 Cấu hình ROI Đa Camera trong Workspace

| Camera / Video ID | Tệp cấu hình JSON | Độ phân giải | Số vùng ROI | Số đỉnh Polygon | Mô tả ranh giới vỉa hè quan trắc |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `video test.mp4` | [`roi_video_test.json`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/roi_video_test.json) | 1280×720 | 1 vùng | 8 đỉnh | Bao trọn mặt hè phố từ chân tường đến mép bo hè đường Phố Huế |
| `videotesst2.mp4` | [`roi_videotesst2.json`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/roi_videotesst2.json) | 1280×720 | 1 vùng | 5 đỉnh | Bao phủ hành lang vỉa hè rộng phía trước dãy cửa hàng Bạch Mai |
| `video test3.mp4` | [`roi_video_test3.json`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/roi_video_test3.json) | 1280×720 | 1 vùng | 7 đỉnh | Mô phỏng góc cua vỉa hè tại nút giao đường Trần Đại Nghĩa |
| `videotest4.mp4` | [`roi_videotest4.json`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/roi_videotest4.json) | 1280×720 | 2 vùng (Multi-ROI) | 11 đỉnh | Bao phủ cả 2 dải vỉa hè bên trái (5 đỉnh) và bên phải (6 đỉnh) |
| `videotest5.mp4` | [`roi_videotest5.json`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/roi_videotest5.json) | 1280×720 | 1 vùng | 4 đỉnh | Hình thang bao trọn hành lang đi bộ cự ly gần trước dãy ki-ốt |
| `videotest6.mp4` | [`roi_videotest6.json`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/roi_videotest6.json) | 1280×720 | 2 vùng (Multi-ROI) | 9 đỉnh | Multi-ROI chia hai bên trục đường chính: hè trái 5 đỉnh, hè phải 4 đỉnh |

### Giới hạn kỹ thuật của cơ chế co giãn tọa độ theo độ phân giải:
Tất cả các tệp ROI lưu trữ tọa độ đỉnh dạng pixel ở độ phân giải gốc 1280×720. Module [`roi/roi_manager.py`](file:///c:/Users/Admin/Downloads/DATN20224083/roi/roi_manager.py) hỗ trợ tính năng co giãn tọa độ tuyến tính theo ma trận ($S_x = W_{\text{stream}} / 1280, S_y = H_{\text{stream}} / 720$). 

**Tuy nhiên, cần nhấn mạnh giới hạn kỹ thuật:** Phép co tọa độ theo độ phân giải chỉ bảo toàn ranh giới ROI khi luồng video giữ nguyên góc đặt camera, khung cắt và tỷ lệ khung hình tương ứng (*aspect ratio*). Nếu camera thay đổi góc nhìn (xoay góc, pan/tilt/zoom), thay đổi vị trí lắp đặt hoặc chuyển sang camera khác, vùng vỉa hè thực tế sẽ biến đổi và người quản trị bắt buộc phải kiểm tra lại cũng như tái thiết lập đa giác ROI cho phù hợp với khung hình mới.

### Minh chứng Đối chiếu Trực quan Lớp phủ ROI trên Khung hình Đại diện 6 Video:

![Lớp phủ Đa giác ROI vỉa hè đối chiếu trên 6 Video CCTV Mẫu](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/tuan_4_8/all_6_cameras_roi_composite.jpg)
*Hình 3. Lớp phủ Đa giác ROI vỉa hè (màu xanh lá) đối chiếu trực quan trên khung hình đại diện của cả 6 Video Thử nghiệm (Tệp gốc: [`reports/figures/tuan_4_8/all_6_cameras_roi_composite.jpg`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/tuan_4_8/all_6_cameras_roi_composite.jpg)).*

---

## 4. BẢNG PHÂN ĐỊNH HIỆN TRẠNG TIẾN ĐỘ TUẦN 4–8 (AUDIT MATRIX)

Nhằm đảm bảo tính minh bạch học thuật tuyệt đối theo yêu cầu của Giảng viên hướng dẫn, bảng dưới đây phân định rõ ràng các hạng mục đã hoàn thành, hạng mục chưa hoàn thành và các giới hạn kỹ thuật cần tiếp tục hoàn thiện:

### Bảng 5. Bảng Phân định Hiện trạng Tiến độ Giai đoạn Tuần 4–8

| Hạng mục công việc | Hiện trạng thực hiện | Minh chứng đối chiếu trong Workspace | Đánh giá nghiệm thu |
| :--- | :--- | :--- | :---: |
| **Thu thập video thử nghiệm** | Tổng hợp 6 video CCTV mẫu phục vụ kiểm thử bài toán lấn chiếm hè phố (nguồn công khai, chưa xác minh bản quyền/giấy phép khảo sát hiện trường). | [`data/videos/`](file:///c:/Users/Admin/Downloads/DATN20224083/data/videos/) (6 tệp `.mp4`, 240 frames/video) | **ĐÃ TỔNG HỢP MẪU** |
| **Quy mô Dataset chuẩn YOLO** | Đã đóng gói tập dữ liệu sạch `v13_clean` gồm 2.674 ảnh, 8.097 BBoxes chuẩn YOLO, 201 ảnh nền âm tính (1.327 tiền tố tên tệp duy nhất). | [`datasets/v13_clean/data.yaml`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/v13_clean/data.yaml) & [`README.txt`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/v13_clean/README.txt) | **VƯỢT CHỈ TIÊU (267%)** |
| **Kiểm toán cấu trúc nhãn** | 100% tệp nhãn đạt cú pháp 5 cột chuẩn và tọa độ chuẩn hóa $[0, 1]$ theo validator (chưa chứng minh nội dung ngữ nghĩa mọi nhãn đều hoàn hảo). | [`datasets/validate_dataset.py`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/validate_dataset.py) (Exit code 0) | **ĐẠT CÚ PHÁP CHUẨN** |
| **Đồng bộ trực tiếp Roboflow API** | Chưa thể gọi API trực tiếp do phiên làm việc local không có biến môi trường `ROBOFLOW_API_KEY`. Dữ liệu đã quản lý và xuất bản hoàn chỉnh qua `v13_clean`. | [`datasets/download_dataset.py`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/download_dataset.py) & [`README.roboflow.txt`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/v13/README.roboflow.txt) | **CHƯA HOÀN THÀNH (API KEY)** |
| **Cấu hình ROI cho từng camera** | Hoàn thành 6 tệp cấu hình JSON tương ứng 6 video mẫu, kiểm tra trực quan bao quát hành lang vỉa hè trên khung hình đại diện (thay đổi góc quay cần vẽ lại). | [`configs/`](file:///c:/Users/Admin/Downloads/DATN20224083/configs/) & [`reports/figures/tuan_4_8/`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/tuan_4_8/) | **ĐÃ THIẾT LẬP ROI MẪU** |
| **Mức độ cách ly tuyệt đối góc quay giữa các split** | Phân chia dựa trên quy tắc tiền tố tên tệp duy nhất; chưa thực hiện kiểm định độc lập phân loại góc quay riêng biệt. | [`reports/known_limitations.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/known_limitations.md) | **GIỚI HẠN KHOA HỌC** |
| **Thử nghiệm trên Edge Device** | Chưa thực hiện; kế hoạch bố trí tại Tuần 16 theo đúng lộ trình Đề cương ĐATN. | Đề cương ĐATN khóa 2026.1 | **ĐÚNG LỘ TRÌNH (T16)** |

---

## 5. KẾ HOẠCH BÀN GIAO CHO GIAI ĐOẠN TUẦN 9–11

Với việc hoàn thành các nội dung kỹ thuật trọng tâm của giai đoạn Tuần 4–8 (Dataset $\ge 1.000$ ảnh sạch chuẩn YOLO và hệ thống ROI đa camera kiểm tra trực quan trên video thử nghiệm), dữ liệu và cấu hình đã sẵn sàng chuyển giao sang giai đoạn Tuần 9–11:

1. **Huấn luyện Mô hình YOLOv8n trên Google Colab GPU Tesla T4:** Nạp dataset `v13_clean`, cấu hình `imgsz=1280`, `batch=8`, thuật toán tối ưu `AdamW` với cơ chế `EarlyStopping` (`patience=20`).
2. **Đánh giá và Tinh chỉnh Mô hình:** Đo lường Precision, Recall, mAP@50 và mAP@50-95 trên tập Validation và tập Test độc lập 267 ảnh.
3. **Thử nghiệm Pipeline Toàn phần:** Kết nối mô hình nhận diện với bộ lọc không gian ROI và thuật toán bám vết ByteTrack trên chuỗi video CCTV thử nghiệm.

---

### DANH MỤC TỆP MINH CHỨNG & BÁO CÁO ĐÃ XUẤT BẢN

1. **Tệp Báo cáo Tiến độ Word (.docx):**
   - Bản cập nhật hoàn thiện: [`reports/Bao_cao_tien_do_Tuan_4_8_DATN_20224083_ban_cap_nhat.docx`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bao_cao_tien_do_Tuan_4_8_DATN_20224083_ban_cap_nhat.docx).
   - Bản gốc đã cập nhật: [`reports/Bao_cao_tien_do_Tuan_4_8_DATN_20224083.docx`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bao_cao_tien_do_Tuan_4_8_DATN_20224083.docx).
   - Bản v2 dự phòng: [`reports/Bao_cao_tien_do_Tuan_4_8_DATN_20224083_v2.docx`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bao_cao_tien_do_Tuan_4_8_DATN_20224083_v2.docx).
2. **Tệp Báo cáo Tiến độ Markdown (.md):**
   - [`reports/Bao_cao_tien_do_Tuan_4_8_DATN_20224083.md`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bao_cao_tien_do_Tuan_4_8_DATN_20224083.md).
3. **Bộ sưu tập 8 mẫu ảnh gán nhãn tùy chọn & Catalog:**
   - Thư mục ảnh mẫu: [`reports/figures/annotated_samples/`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/annotated_samples/).
   - Bảng Catalog preview cả 8 mẫu: [`reports/figures/annotated_samples/catalog_all_8_samples.jpg`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/annotated_samples/catalog_all_8_samples.jpg).
4. **Hình ảnh minh chứng đã tạo từ `datasets/v13_clean/train/`:**
   - Hình 1 (Mẫu ảnh gán nhãn 5 cột): [`reports/figures/roboflow_sample_annotated.jpg`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/roboflow_sample_annotated.jpg).
   - Hình 2 (Lưới mẫu nền âm tính 0 byte): [`reports/figures/negative_samples_grid.jpg`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/negative_samples_grid.jpg).
   - Hình 3 (Lưới ảnh ghép 6 camera phủ ROI): [`reports/figures/tuan_4_8/all_6_cameras_roi_composite.jpg`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/figures/tuan_4_8/all_6_cameras_roi_composite.jpg).
5. **Tập dữ liệu sạch `v13_clean`:**
   - Cấu hình YAML: [`datasets/v13_clean/data.yaml`](file:///c:/Users/Admin/Downloads/DATN20224083/datasets/v13_clean/data.yaml).
   - Lệnh kiểm tra cú pháp nhãn:
     ```powershell
     .\.venv\Scripts\python.exe datasets/validate_dataset.py
     ```
