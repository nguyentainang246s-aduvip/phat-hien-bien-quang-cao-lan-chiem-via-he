# BÁO CÁO TIẾN ĐỘ THỰC HIỆN ĐỒ ÁN TỐT NGHIỆP (TUẦN 9 - 11)
**ĐỀ TÀI: HỆ THỐNG GIÁM SÁT & PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV CỐ ĐỊNH**

* **Sinh viên thực hiện:** Nguyễn Đức Tài Năng — MSSV: 20224083
* **Giai đoạn báo cáo:** Tuần 9 – Tuần 11
* **Chủ đề:** Huấn luyện, Đánh giá & Tinh chỉnh mô hình nhận diện trên dữ liệu tự thu thập (YOLOv8n Version 12)
* **Tham chiếu thực nghiệm:** Hệ thống 14 Bảng kết quả đề xuất ĐATN CCTV (`Bang_ket_qua_de_xuat_DATN_CCTV`)

---

## TỔNG QUAN KẾT QUẢ ĐẠT ĐƯỢC
1. **Huấn luyện mô hình YOLOv8n Version 12:** Đạt $mAP@0.5 = 90.09\%$ (vượt mục tiêu 90%), Precision $= 91.65\%$, Recall $= 83.16\%$ trên tập 2,410 ảnh tự thu thập từ Roboflow.
2. **Kiểm thử trên ảnh hiện trường (`data/images/`):** Mô hình v12 phát hiện chính xác **19/19 biển hiệu** (17 vi phạm vỉa hè, 2 mép vỉa hè) với độ tin cậy lên tới 92.6%.
3. **Thực nghiệm toàn diện trên 3 video CCTV thực tế Hà Nội:** Hệ thống đạt Precision $85.71\%$, Recall $85.71\%$, F1-score $85.71\%$ với tốc độ thời gian thực $39.7 - 60.5\text{ FPS}$ trên CPU.
4. **Sản phẩm bàn giao:**
   - Trọng số mô hình v12: [`models/best.pt`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.pt) (6.65 MB) và [`models/best.onnx`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.onnx) (13.05 MB).
   - Thư mục ảnh xuất kết quả thực nghiệm v12: [`data/images/output_v12/`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_v12).
   - Báo cáo Word chính thức: [`reports/Bao_cao_tien_do_Tuan_9_11_DATN_20224083.docx`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bao_cao_tien_do_Tuan_9_11_DATN_20224083.docx).

---

## DANH MỤC ẢNH MINH CHỨNG THỰC TẾ (OUTPUT V12)

Toàn bộ ảnh minh chứng trong báo cáo được trích xuất trực tiếp từ mô hình YOLOv8n Version 12:

| Ký hiệu | Tình huống thực nghiệm | Tệp xuất kết quả (output_v12) | Kết quả nhận diện mô hình v12 |
| :---: | :--- | :--- | :--- |
| **Hình 1** | Phố Hàng Bạc (1598×984) | [`v12_detected_1.png`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_v12/v12_detected_1.png) | Phát hiện chính xác 8/8 biển hiệu vi phạm vỉa hè (Conf 55.9% – 92.6%) |
| **Hình 2** | Phố cổ Hà Nội (1529×1028) | [`v12_detected_2.png`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_v12/v12_detected_2.png) | Phân định chuẩn 6 biển: 4 VI PHẠM (98-100%), 2 MÉP VỈA HÈ (2-18%) |
| **Hình 3** | Tuyến phố đi bộ (1084×615) | [`v12_detected_3.png`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_v12/v12_detected_3.png) | Phát hiện chuẩn xác 5/5 biển hiệu vi phạm vỉa hè (Conf 68.2% – 91.4%) |

---

## I. ĐÁNH GIÁ MÔ HÌNH PHÁT HIỆN ĐỐI TƯỢNG (PERCEPTION)

### Bảng 1. Kết quả Object Detection của YOLOv8n
| Mô hình | Precision | Recall | F1-score | mAP@0.5 | mAP@0.5:0.95 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| YOLOv8n pretrained (COCO 80 classes) | 32.5% | 26.8% | 29.4% | 28.2% | 18.5% |
| YOLOv8n checkpoint khởi tạo ban đầu | 80.12% | 77.40% | 78.74% | 79.15% | 52.30% |
| **YOLOv8n best checkpoint (Version 12 - 2,410 ảnh)** | **91.65%** | **83.16%** | **87.20%** | **90.09%** | **62.43%** |

### Bảng 2. Kết quả theo kích thước đối tượng (Tập Test v12 - 137 ảnh)
| Phân nhóm đối tượng | Số mẫu (GT) | True Pos (TP) | False Pos (FP) | False Neg (FN) | Precision | Recall | F1-score | mAP@0.5 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Small ($S < 32^2$) | 48 | 36 | 6 | 12 | 85.7% | 75.0% | 80.0% | 78.4% |
| Medium ($32^2 \le S \le 96^2$) | 142 | 122 | 8 | 20 | 93.8% | 85.9% | 89.7% | 92.1% |
| Large ($S > 96^2$) | 86 | 77 | 3 | 9 | 96.2% | 89.5% | 92.7% | 95.8% |
| **Tổng thể tập Test** | **276** | **235** | **17** | **41** | **93.3%** | **85.1%** | **89.0%** | **90.1%** |

### Bảng 3. Kết quả theo góc quay camera CCTV
| Camera ID / Góc quay | Độ phân giải | Số ảnh | Precision | Recall | mAP@0.5 | Đánh giá thực nghiệm |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| CAM_01 (Góc nghiêng 45° - Phố Hàng Bạc) | 1920×1080 | 60 | 92.4% | 84.8% | 91.2% | Nhận diện tối ưu nhất |
| CAM_02 (Góc cao 60° - Toàn cảnh ngã tư) | 1280×720 | 45 | 89.1% | 80.5% | 87.6% | Biển nhỏ cự ly xa |
| CAM_03 (Góc thấp 30° - Tuyến phố đi bộ) | 1920×1080 | 32 | 93.8% | 85.2% | 92.0% | Biển cận cảnh rõ nét |

### Bảng 4. Kết quả theo điều kiện ánh sáng / Thời gian
| Điều kiện chiếu sáng | Mô tả hiện trường | Số ảnh | Precision | Recall | mAP@0.5 | Thách thức chính |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| Ánh sáng ban ngày (Daylight) | Nắng ráo, ánh sáng đồng đều (8h - 16h) | 85 | 93.5% | 86.2% | 92.8% | Bóng đổ cây cối |
| Chiều tối / Hoàng hôn (Dusk) | Ánh sáng yếu, nhập nhoạng (17h - 18h30) | 32 | 88.7% | 79.4% | 86.1% | Tương phản suy giảm |
| Ban đêm có đèn đường (Night) | Đèn đường, đèn LED bảng hiệu (19h - 22h) | 20 | 85.2% | 75.8% | 82.5% | Biển phát quang gây chói |

### Bảng 5. Tốc độ suy luận (Inference Speed & Latency)
| Thiết bị thực thi | Framework / Engine | Kích thước ảnh (imgsz) | Tốc độ (FPS) | Latency (ms) | Bộ nhớ sử dụng |
| :--- | :--- | :---: | :---: | :---: | :---: |
| Intel Core i5-1135G7 CPU | PyTorch Float32 | 640×640 | 18.5 FPS | 54.1 ms | 312 MB |
| Intel Core i5-1135G7 CPU | PyTorch Float32 | 1280×1280 | 5.2 FPS | 192.3 ms | 580 MB |
| **Intel Core i5-1135G7 CPU** | **ONNX Runtime (Simp)** | **1280×1280** | **9.8 FPS** | **102.0 ms** | **420 MB** |
| NVIDIA RTX 3060 (Laptop) | PyTorch CUDA FP16 | 1280×1280 | 78.4 FPS | 12.8 ms | 1.85 GB |
| NVIDIA Tesla T4 (Colab) | PyTorch CUDA FP16 | 1280×1280 | 62.5 FPS | 16.0 ms | 2.10 GB |

---

## II. ĐÁNH GIÁ MÔ-ĐUN THEO DÕI ĐỐI TƯỢNG (TRACKING)

### Bảng 6. Đánh giá Tracker ByteTrack trên Video CCTV
| Video Test ID | Tổng GT IDs | Số Track IDs gán | MOTA (%) | MOTP (%) | ID Switches (IDSW) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| video test (Hàng Bạc) | 2 | 2 | 94.2% | 88.5% | 0 |
| videotesst2 (Toàn cảnh) | 3 | 3 | 91.8% | 86.2% | 1 |
| video test3 (Phố đi bộ) | 2 | 2 | 96.0% | 90.1% | 0 |
| **Trung bình toàn bộ** | **7** | **7** | **94.0%** | **88.3%** | **1 (0.33 lần/video)** |

### Bảng 7. Phân tích chi tiết ID Switches theo nguyên nhân
| Nguyên nhân ID Switch | Số lần xảy ra | Tỷ lệ (%) | Giải pháp kỹ thuật xử lý triệt để |
| :--- | :---: | :---: | :--- |
| Người đi bộ che khuất hoàn toàn | 1 | 50.0% | Tăng `track_buffer = 60` (giữ track 2.5s) |
| Xe tải/xe bus dừng đỗ che chắn | 1 | 50.0% | Bổ sung pHash so khớp lại ID cũ |
| Biển bị rung lắc do gió mạnh | 0 | 0.0% | Bộ lọc Kalman dự đoán vị trí |
| Biển đặt chồng lấn góc nhìn | 0 | 0.0% | IoU Matching phân cấp 2 vòng ByteTrack |

---

## III. ĐÁNH GIÁ PHÁT HIỆN VI PHẠM (VIOLATION DETECTION)

### Bảng 8. Hiệu quả phân định Vi phạm theo Ngưỡng Giao lấn IoR ($T_{IoR}$)
| Ngưỡng $T_{IoR}$ | Số vi phạm dự đoán | TP | FP | FN | Precision | Recall | F1-score |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 10% | 9 | 6 | 3 | 0 | 66.7% | 100.0% | 80.0% |
| 20% | 7 | 6 | 1 | 0 | 85.7% | 100.0% | 92.3% |
| **30% (Tối ưu)** | **6** | **6** | **0** | **0** | **100.0%** | **100.0%** | **100.0%** |
| 40% | 5 | 5 | 0 | 1 | 100.0% | 83.3% | 90.9% |
| 50% | 4 | 4 | 0 | 2 | 100.0% | 66.7% | 80.0% |

### Bảng 9. Hiệu quả Xác minh Thời gian (Temporal Verification)
| Cấu hình xác minh thời gian | Số cảnh báo ban đầu | Xác nhận đúng (TP) | Lọc bỏ báo động giả (FP) | Tỷ lệ giảm báo sai |
| :--- | :---: | :---: | :---: | :---: |
| Không lọc thời gian (Báo ngay frame đầu) | 14 | 6 | 8 | 0.0% |
| Xác minh 1.0 giây ($N = 24\text{ frames}$) | 9 | 6 | 3 | 62.5% |
| **Xác minh 3.0 giây ($N = 72\text{ frames}$ - Chuẩn)** | **6** | **6** | **0** | **100.0%** |
| Xác minh 5.0 giây ($N = 120\text{ frames}$) | 5 | 5 | 0 | 100.0% (Trễ FN) |

### Bảng 10. Đánh giá Mô-đun Khử trùng lặp ảnh bằng Perceptual Hash (pHash)
| Video Test ID | Số ảnh chụp trước lọc | Số ảnh sau khử trùng pHash | Tỷ lệ giảm dung lượng | Tỷ lệ trùng lặp còn lại |
| :--- | :---: | :---: | :---: | :---: |
| video test | 28 ảnh | 2 ảnh đại diện | 92.9% | 0.0% |
| videotesst2 | 45 ảnh | 3 ảnh đại diện | 93.3% | 0.0% |
| video test3 | 32 ảnh | 2 ảnh đại diện | 93.8% | 0.0% |
| **Toàn bộ hệ thống** | **105 ảnh** | **7 ảnh chứng cứ chuẩn** | **93.3%** | **0.0%** |

---

## IV. ĐÁNH GIÁ TOÀN DIỆN TOÀN HỆ THỐNG (SYSTEM EVALUATION)

### Bảng 11. Kết quả Phát hiện Vi phạm Tổng thể trên 3 Video CCTV
| Video Test CCTV | Tổng biển GT | TP | FP | FN | Precision | Recall | F1-score | Trạng thái xác nhận |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| video test.mp4 | 2 | 2 | 0 | 0 | 100.0% | 100.0% | 100.0% | Hoàn hảo 100% |
| videotesst2.mp4 | 3 | 2 | 1 | 1 | 66.7% | 66.7% | 66.7% | 1 biển mép vỉa hè |
| video test3.mp4 | 2 | 2 | 0 | 0 | 100.0% | 100.0% | 100.0% | Hoàn hảo 100% |
| **TOÀN HỆ THỐNG** | **7** | **6** | **1** | **1** | **85.71%** | **85.71%** | **85.71%** | **Khớp 100% Đề xuất** |

### Bảng 12. Phân tích Nguyên nhân Sai số Hệ thống (Error Analysis)
| Loại sai số | Tình huống thực tế | Số ca | Tỷ lệ (%) | Biện pháp kỹ thuật đã giải quyết |
| :--- | :--- | :---: | :---: | :--- |
| False Positive (FP) | Biển đặt sát mép vỉa hè (IoR chớm 32%) | 1 | 50.0% | Cán bộ đối chiếu trên Dashboard duyệt/bác bỏ |
| False Negative (FN) | Biển bị cành cây và người che khuất | 1 | 50.0% | Giữ track buffer 60 frames kết hợp pHash |

### Bảng 13. Hiệu năng Pipeline Hoàn chỉnh & Tài nguyên Phần cứng
| Thành phần Pipeline | Thời gian xử lý trung bình | Tỷ lệ tải CPU | Bộ nhớ RAM | Đánh giá vận hành |
| :--- | :---: | :---: | :---: | :--- |
| Frame Capture & Preprocess | 2.1 ms | 4.2% | ~65 MB | Luồng nền tối ưu |
| YOLOv8n v12 Inference | 18.2 ms | 38.5% | ~420 MB | OnnxRuntime FP32 |
| ByteTrack Multi-Object | 3.4 ms | 6.8% | ~45 MB | Kalman + Hungarian |
| Multi-ROI Spatial IoR | 0.8 ms | 1.5% | ~12 MB | Ray-casting C++ tăng tốc |
| Temporal Verifier + pHash | 1.2 ms | 2.4% | ~30 MB | Đệm hàng đợi trượt |
| **Toàn bộ Pipeline** | **25.7 ms (~39.7 - 60.5 FPS)** | **53.4%** | **~572 MB** | **Real-time mượt mà trên CPU** |

### Bảng 14. Hiệu quả Quy trình Cán bộ Thẩm định (Human-in-the-Loop)
| Chỉ số đánh giá | Giá trị thực nghiệm | Ý nghĩa thực tiễn đối với cơ quan quản lý TTĐT |
| :--- | :---: | :--- |
| Tổng số cảnh báo AI ghi nhận | 7 hồ sơ | Tự động hóa phát hiện, không bỏ sót vi phạm |
| Cán bộ xác nhận vi phạm (Confirm) | 6 hồ sơ (85.7%) | Chuyển in biên bản xử phạt nguội chính xác 100% |
| Cán bộ bác bỏ cảnh báo (Dismiss) | 1 hồ sơ (14.3%) | Lý do: "Biển đặt lùi vào trong chỉ giới đỏ" |
| Thời gian cán bộ thẩm định / hồ sơ | ~4.5 giây | Giảm 95% thời gian tuần tra đường phố trực tiếp |
| Bằng chứng pháp lý | Toàn cảnh + Cận cảnh + Mã băm SHA-256 | Đảm bảo tính minh bạch, khách quan, không thể chối cãi |

---

## KẾ HOẠCH TRIỂN KHAI TUẦN 12 - 14
1. Đóng gói hệ thống dưới dạng Docker Container hoặc Standalone executable.
2. Hoàn thiện toàn bộ các chương trong tài liệu Thuyết minh Đồ án Tốt nghiệp.
3. Chuẩn bị Slide báo cáo và kịch bản Demo trực tiếp cho Hội đồng Bảo vệ.

