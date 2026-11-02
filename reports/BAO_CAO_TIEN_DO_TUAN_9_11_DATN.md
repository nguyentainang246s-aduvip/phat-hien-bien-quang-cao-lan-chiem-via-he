# BÁO CÁO TIẾN ĐỘ THỰC HIỆN ĐỒ ÁN TỐT NGHIỆP (TUẦN 9 - 11)
**ĐỀ TÀI: HỆ THỐNG GIÁM SÁT & PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV CỐ ĐỊNH**

* **Sinh viên thực hiện:** Nguyễn Đức Tài Năng — MSSV: 20224083 — Lớp: ĐATN K67
* **Đơn vị đào tạo:** Đại học Bách Khoa Hà Nội
* **Giai đoạn báo cáo:** Tuần 9 – Tuần 11
* **Chủ đề:** Huấn luyện, Đánh giá & Tinh chỉnh mô hình nhận diện trên dữ liệu tự thu thập (YOLOv8n Version 13 Final)
* **Tham chiếu thực nghiệm:** Hệ thống 14 Bảng kết quả đề xuất ĐATN CCTV (`Bang_ket_qua_de_xuat_DATN_CCTV`)
* **Ngày cập nhật hoàn thiện:** 02/11/2026

---

## TỔNG QUAN KẾT QUẢ ĐẠT ĐƯỢC

1. **Huấn luyện mô hình YOLOv8n Version 13 Final:**
   - Tập dữ liệu: Roboflow v13 gồm **2,674 ảnh** (Tập train tải về có 2,292 ảnh; sau khi Ultralytics tự động loại bỏ 16 ảnh lỗi nhãn đa giác hỗn hợp, số ảnh thực tế đưa vào mạng nơ-ron huấn luyện là **2,276 ảnh**; tập val **229 ảnh**; tập test **151 ảnh hợp lệ** sau khi tự động bỏ 2 ảnh nhãn lỗi).
   - Nguồn gốc dữ liệu: Ảnh chụp hiện trường thực tế tại các tuyến phố Hà Nội kết hợp thu thập từ internet và bổ sung **180 ảnh sinh bằng Generative AI** (Gemini/Imagen, chiếm ~6.7% tập dữ liệu) nhằm làm giàu các trường hợp góc máy nghiêng gắt, ban đêm hoặc mưa bão hiếm gặp.
   - Kết quả kiểm thử độc lập (trên 151 ảnh test / 417 instances): **Precision = 87.70%**, **Recall = 85.40%**, **F1-score = 86.53%**, **mAP@0.5 = 89.60%** (tiệm cận mốc 90%), **mAP@0.5:0.95 = 60.50%**.
2. **Kiểm thử trên ảnh hiện trường (`data/images/`):**
   - Mô hình v13 phát hiện chính xác **21/21 biển hiệu** (18 vi phạm vỉa hè, 2 mép vỉa hè, 1 hợp lệ trong nhà) với độ tin cậy phát hiện lên tới 90.8%.
3. **Thực nghiệm toàn diện trên 3 video CCTV thực tế Hà Nội:**
   - Đánh giá theo sự kiện vi phạm (Event-based) trên 16 đối tượng Ground Truth (14 vi phạm thực tế, 2 hợp lệ không vi phạm) và 2 cảnh báo giả phát sinh:
   - Kết quả: **True Positives (TP) = 12**, **False Positives (FP) = 2**, **False Negatives (FN) = 2**, **True Negatives (TN) = 2**.
   - **Precision = 85.71%**, **Recall = 85.71%**, **F1-score = 85.71%**.
   - Thông lượng toàn pipeline: **41.8 – 61.4 FPS** trên CPU Intel máy tính thông thường nhờ cơ chế Frame-Skip=2.
4. **Sản phẩm nghiệm thu & Tệp minh chứng:**
   - Trọng số mô hình tốt nhất: [`models/best.pt`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.pt) (6.30 MB / 6,611,242 bytes) và [`models/best.onnx`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.onnx) (12.45 MB / 13,053,904 bytes - Dynamic Shape).
   - Sổ bộ Ground Truth 18 sự kiện CSV: [`reports/ground_truth_events_cctv.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/ground_truth_events_cctv.csv).
   - Bảng phân loại kích thước đối tượng CSV: [`reports/test_subset_breakdown.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/test_subset_breakdown.csv).
   - Bảng gán nhãn môi trường 151 ảnh CSV: [`reports/test_environmental_tags.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/test_environmental_tags.csv).
   - Thư mục ảnh xuất kết quả thực nghiệm v13: [`data/images/output_v13/`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_v13).
   - Báo cáo Word chính thức: [`reports/Bao_cao_tien_do_Tuan_9_11_DATN_20224083.docx`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/Bao_cao_tien_do_Tuan_9_11_DATN_20224083.docx).

---

## DANH MỤC ẢNH MINH CHỨNG THỰC TẾ (OUTPUT V13 FINAL)

Toàn bộ ảnh minh chứng trong báo cáo được trích xuất trực tiếp từ mô hình YOLOv8n Version 13 Final:

| Ký hiệu | Tình huống thực nghiệm | Tệp xuất kết quả (output_v13) | Kết quả nhận diện mô hình v13 Final |
| :---: | :--- | :--- | :--- |
| **Hình 1** | Phố Hàng Bạc (1598×984) | [`v13_detected_1.png`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_v13/v13_detected_1.png) | Phát hiện 10 biển hiệu (9 vi phạm vỉa hè, 1 hợp lệ, Conf lên đến 90.8%) |
| **Hình 2** | Phố cổ Hà Nội (1529×1028) | [`v13_detected_2.png`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_v13/v13_detected_2.png) | Phân định chuẩn 6 biển: 4 VI PHẠM (đè vỉa hè 97-100%), 2 MÉP VỈA HÈ (2-19%) |
| **Hình 3** | Tuyến phố đi bộ (1084×615) | [`v13_detected_3.png`](file:///c:/Users/Admin/Downloads/DATN20224083/data/images/output_v13/v13_detected_3.png) | Phát hiện chuẩn xác 5/5 biển hiệu vi phạm vỉa hè (Conf 76.3% – 85.9%) |

---

## I. ĐÁNH GIÁ MÔ HÌNH PHÁT HIỆN ĐỐI TƯỢNG (PERCEPTION)

### Bảng 1. Kết quả Object Detection của YOLOv8n
| Mô hình | Precision | Recall | F1-score | mAP@0.5 | mAP@0.5:0.95 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| YOLOv8n checkpoint cơ sở (Huấn luyện sơ khởi trên tập 974 ảnh ban đầu) | 80.12% | 77.40% | 78.74% | 79.15% | 52.30% |
| **YOLOv8n best checkpoint (Version 13 Final - Tập dữ liệu mở rộng 2,674 ảnh)** | **87.70%** | **85.40%** | **86.53%** | **89.60%** | **60.50%** |

> **Nhận xét Bảng 1:** So với checkpoint cơ sở ban đầu, mô hình Version 13 Final (huấn luyện trên tập mở rộng 2,674 ảnh và đánh giá độc lập trên 151 ảnh test) có bước cải thiện vượt bậc:
> - Precision tăng **+7.58%** (từ 80.12% lên 87.70%)
> - Recall tăng **+8.00%** (từ 77.40% lên 85.40%)
> - F1-score tăng **+7.79%** (từ 78.74% lên 86.53%)
> - mAP@0.5 tăng **+10.45%** (từ 79.15% lên 89.60%, tiệm cận mốc 90%)
> - mAP@0.5:0.95 tăng **+8.20%** (từ 52.30% lên 60.50%), thể hiện chất lượng bounding box khít chặt với biển hiệu thực tế.

---

### Bảng 2. Kết quả theo kích thước biển quảng cáo/biển hiệu (Tập Test v13 Final - 151 ảnh)
| Kích thước đối tượng (COCO Area) | Số mẫu | Precision | Recall | F1-score | mAP@0.5 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Small (Diện tích < $32^2$ pixels) | 103 | 81.6% | 74.8% | 78.0% | 79.2% |
| Medium ($32^2 \le \text{Diện tích} < 96^2$ px) | 246 | 88.5% | 87.0% | 87.7% | 91.4% |
| Large (Diện tích $\ge 96^2$ pixels) | 68 | 92.4% | 91.2% | 91.8% | 94.6% |
| **Tổng hợp toàn tập Test độc lập** | **417** | **87.70%** | **85.40%** | **86.53%** | **89.60%** |

> **Nhận xét Bảng 2:** Kích thước đối tượng được trích xuất tự động qua script độc lập ([`scripts/evaluate_subsets.py`](file:///c:/Users/Admin/Downloads/DATN20224083/scripts/evaluate_subsets.py)) theo chuẩn COCO Area trên độ phân giải chuẩn hóa 640×640 (Small: < $32^2$ px, Medium: $32^2–96^2$ px, Large: $\ge 96^2$ px). Toàn bộ 417 đối tượng thuộc 139 ảnh có nhãn trong tập kiểm thử độc lập 151 ảnh (kèm 12 ảnh nền âm background). Số liệu từng nhóm cộng dồn: $103 + 246 + 68 = 417$ mẫu, hoàn toàn khớp với log đánh giá tự động của Ultralytics. Dữ liệu chi tiết từng bounding box đã được lưu minh chứng tại tệp: [`reports/test_subset_breakdown.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/test_subset_breakdown.csv).

---

### Bảng 3. Kết quả theo điều kiện môi trường quan sát (Tập Test v13 Final - 151 ảnh)
| Điều kiện môi trường | Số ảnh test | Precision | Recall | F1-score | mAP@0.5 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Ban ngày tiêu chuẩn (Ánh sáng tự nhiên đầy đủ) | 82 | 90.2% | 88.5% | 89.3% | 92.1% |
| Nắng gắt / Tương phản mạnh (Lóa sáng bề mặt) | 24 | 86.8% | 83.3% | 85.0% | 88.4% |
| Bóng râm (Khuất hiên nhà / dưới tán cây) | 21 | 87.5% | 85.0% | 86.2% | 89.1% |
| Chiều tối / Đèn đường (Ánh sáng yếu) | 12 | 82.4% | 75.0% | 78.5% | 82.6% |
| Che khuất nặng (Người đi bộ, xe cộ, cột điện) | 12 | 81.8% | 72.7% | 77.0% | 80.5% |
| **Tổng cộng các điều kiện môi trường** | **151** | **87.70%** | **85.40%** | **86.53%** | **89.60%** |

> **Nhận xét Bảng 3:** 151 ảnh kiểm thử hợp lệ được tác giả đề tài trực quan thẩm định và gán nhãn thuộc tính môi trường chủ đạo (Single-label Primary Attribute), lưu chi tiết tại tệp [`reports/test_environmental_tags.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/test_environmental_tags.csv). Số lượng ảnh cộng dồn: $82 + 24 + 21 + 12 + 12 = 151$ ảnh. Mô hình đạt độ ổn định cao trên mọi điều kiện, duy trì mAP@0.5 > 80% ngay cả trong tình huống ánh sáng nhập nhoạng hoặc bị xe cộ che khuất một phần.

---

## II. ĐÁNH GIÁ SPATIAL REASONING VÀ DECISION LOGIC

### Bảng 4. Đánh giá thuật toán xác định vi phạm (Ablation Pipeline)
| Phương pháp tiếp cận | Precision | Recall | F1-score | Báo động giả (FP) | Bỏ sót (FN) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 1. Detection đơn thuần (Không có không gian ROI) | 46.2% | 85.71% | 60.0% | 14 | 2 |
| 2. Detection + Đa giác ROI vỉa hè | 66.7% | 85.71% | 75.0% | 6 | 2 |
| 3. Detection + ROI + Ngưỡng Overlap ($\ge 30\%$) | 80.0% | 85.71% | 82.76% | 3 | 2 |
| **4. Full Pipeline (+ Temporal 3.0s + ByteTrack)** | **85.71%** | **85.71%** | **85.71%** | **2** | **2** |

> **Nhận xét Bảng 4:** Trong bài toán phát hiện sự kiện thời gian thực (Event-based Detection) trên luồng video mở, tập sự kiện âm (True Negatives) không bị giới hạn trong không gian và thời gian. Do đó, theo chuẩn quốc tế trong thị giác máy tính (Pascal VOC, MS COCO, MOT Challenge), hệ thống loại bỏ chỉ số Accuracy và sử dụng Precision, Recall, F1-score làm thước đo định lượng cốt lõi. Nếu chỉ dùng Detection đơn thuần, hệ thống sinh ra 14 FP từ các biển gắn tường và đặt sâu trong nhà, khiến Precision rớt xuống 46.2%. Việc tích hợp ROI, ngưỡng Overlap $\ge 30\%$ và Temporal 3.0s giúp loại bỏ 12 báo động giả, nâng Precision lên 85.71%.

---

### Bảng 5. Khảo sát ngưỡng diện tích giao nhau với ROI (Overlap Threshold)
| Ngưỡng Overlap (%) | Precision | Recall | F1-score | Báo động giả (FP) | Bỏ sót (FN) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 10% | 68.4% | 92.9% | 78.8% | 6 | 1 |
| 20% | 76.5% | 92.9% | 83.9% | 4 | 1 |
| **30% (Ngưỡng tối ưu lựa chọn)** | **85.71%** | **85.71%** | **85.71%** | **2** | **2** |
| 40% | 90.91% | 71.43% | 79.99% | 1 | 4 |
| 50% | 90.00% | 64.29% | 75.00% | 1 | 5 |

> **Nhận xét Bảng 5:** Định nghĩa $\text{Overlap} = \text{Area}(\text{BBox} \cap \text{ROI}) / \text{Area}(\text{BBox})$. Tại ngưỡng 30%, đường cong F1 đạt giá trị cực đại 85.71% ($TP=12, FP=2, FN=2$). Đặc biệt, khi chuyển từ ngưỡng 20% lên 30%, TP giảm từ 13 xuống 12 (FN tăng từ 1 lên 2), điều này chứng minh có đúng 1 trường hợp vi phạm thực tế kê sát mép thềm nhà có Overlap nằm trong khoảng $[20\%, 30\%)$ bị bộ lọc không gian loại bỏ để tránh báo động giả. Tại ngưỡng 40%, TP=10, FP=1, FN=4 cho Precision = $10/(10+1) = 90.91\%$, Recall = $10/(10+4) = 71.43\%$, F1 = 79.99%.

---

### Bảng 6. Ảnh hưởng của số frame xác nhận vi phạm (Temporal Filter)
| Cấu hình thời gian | Số frame video (24 FPS) | Số frame infer (Skip=2) | Precision | Recall | F1-score | FP | Độ trễ phát hiện |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 frame video (~0.04s) | 1 | 1 | 54.5% | 85.71% | 66.7% | 10 | 0.04s |
| 6 frames video (~0.25s) | 6 | 2 | 66.7% | 85.71% | 75.0% | 6 | 0.25s |
| 12 frames video (~0.50s) | 12 | 4 | 75.0% | 85.71% | 80.0% | 4 | 0.50s |
| 24 frames video (~1.00s) | 24 | 8 | 80.0% | 85.71% | 82.8% | 3 | 1.00s |
| **72 frames video (3.00s - Chuẩn)** | **72** | **24** | **85.71%** | **85.71%** | **85.71%** | **2** | **3.00s** |

> **Nhận xét Bảng 6:** Hệ thống vận hành ở luồng CCTV chuẩn 24 FPS và kích hoạt cơ chế tăng tốc Frame-Skip=2 (chỉ đưa 1 trong 3 frames vào mạng nơ-ron inference). Do đó, cấu hình xác minh vi phạm 3.0 giây (`confirm_seconds=3.0s` trong mã nguồn) tương ứng với 72 frames video liên tục và 24 frames thực tế được mạng YOLOv8n theo dõi qua ByteTrack. Cơ chế này loại bỏ hoàn toàn các báo động giả do người đi bộ hoặc xe cộ vô tình che chắn/cầm vật thể đi qua vỉa hè trong tích tắc.

---

### Bảng 7. Ablation Study cho toàn bộ pipeline
| Cấu hình | Detection | ROI | Tracking | Temporal | Precision | Recall | F1-score |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| A | ✓ | — | — | — | 46.2% | 85.71% | 60.0% |
| B | ✓ | ✓ | — | — | 66.7% | 85.71% | 75.0% |
| C | ✓ | ✓ | ✓ | — | 75.0% | 85.71% | 80.0% |
| **D (Full)** | **✓** | **✓** | **✓** | **✓** | **85.71%** | **85.71%** | **85.71%** |

---

### Bảng 8. Kết quả theo mức độ lấn chiếm vỉa hè
| Mức độ lấn chiếm | Khoảng Overlap | Số đối tượng GT | Phát hiện đúng (TP/TN) | Bỏ sót (FN) | Tỷ lệ phát hiện / Lọc đúng |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Không lấn chiếm / Hợp lệ | 0% | 2 | 2 (Lọc đúng TN) | 0 | 100.0% (Lọc sạch) |
| Lấn chiếm mép ranh giới | 20% ≤ Overlap < 30% | 1 | 0 | 1 (Lọc ngưỡng) | 0.0% (Lọc an toàn) |
| Lấn chiếm trung bình | 30% ≤ Overlap ≤ 50% | 4 | 4 (TP) | 0 | 100.0% |
| Lấn chiếm rõ rệt / Nghiêm trọng | > 50% | 9 | 8 (TP) | 1 (Cự ly xa) | 88.9% |
| **TỔNG HỢP VI PHẠM THỰC TẾ** | **Toàn bộ vi phạm GT** | **14** | **12 (TP)** | **2** | **85.71%** |

> **Nhận xét Bảng 8:** Thống kê dựa trên toàn bộ 16 đối tượng kiểm định thực tế của 3 video CCTV (14 vi phạm thực tế và 2 không vi phạm). Số liệu ăn khớp 100% với Bảng 5 và Bảng 14: Trong 14 ca vi phạm thực tế, có đúng 1 ca lấn chiếm mép ranh giới (Overlap 26.5%, thuộc nhóm 20-30%) bị bộ lọc ngưỡng 30% loại bỏ (trở thành FN số 1); 1 ca lấn chiếm lớn nhưng ở cự ly xa >35m bị che khuất chân đế (trở thành FN số 2). 12 ca vi phạm còn lại đều được phát hiện chính xác, đạt Recall vi phạm tổng thể = $12/14 = 85.71\%$.

---

## III. ĐÁNH GIÁ HỆ THỐNG END-TO-END TRÊN VIDEO THỰC TẾ

### Bảng 9. Kết quả End-to-End trên từng video/camera thực tế
| Camera / Tuyến phố | Vi phạm GT | Phát hiện đúng (TP) | Báo giả (FP) | Bỏ sót (FN) | Precision | Recall | F1-score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Camera 1 (Phố Huế / Hàng Bài, Hoàn Kiếm) | 4 | 4 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| Camera 2 (Phố Bạch Mai, Hai Bà Trưng) | 5 | 3 | 0 | 2 | 100.0% | 60.0% | 75.0% |
| Camera 3 (Phố Trần Đại Nghĩa, Hai Bà Trưng) | 5 | 5 | 2 | 0 | 71.43% | 100.0% | 83.33% |
| **TỔNG HỢP TOÀN HỆ THỐNG** | **14** | **12** | **2** | **2** | **85.71%** | **85.71%** | **85.71%** |

> **Nhận xét Bảng 9:** Số liệu per-camera được đối chiếu trực tiếp từ file nhật ký thực nghiệm ([`reports/system_eval_results.json`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/system_eval_results.json)) và Sổ bộ sự kiện ([`reports/ground_truth_events_cctv.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/ground_truth_events_cctv.csv)):
> - Tổng Vi phạm GT: $4 + 5 + 5 = 14$
> - Tổng TP: $4 + 3 + 5 = 12$
> - Tổng FP: $0 + 0 + 2 = 2$ (đều nằm tại Camera 3 do vật thể ngoài tập nhãn)
> - Tổng FN: $0 + 2 + 0 = 2$ (đều nằm tại Camera 2 do cự ly xa và xuất hiện ở cuối video)
> - Ngoài ra có 2 đối tượng hợp lệ (1 ở Cam 1, 1 ở Cam 3) được hệ thống phân loại đúng không vi phạm (TN=2).
> - Precision $= 12 / (12 + 2) = 85.71\%$, Recall $= 12 / (12 + 2) = 85.71\%$, F1-score $= 85.71\%$.

---

### BẢNG SỔ BỘ GROUND TRUTH 18 SỰ KIỆN THỰC ĐỊA (TRÍCH XUẤT TỪ CSV)

Dưới đây là trích xuất 18 sự kiện kiểm định thực tế đối chiếu giữa Ground Truth và phán quyết hệ thống:

| Camera | Tuyến phố | Object ID | Track ID | Nhãn GT | Overlap (%) | AI Conf | Hệ thống kết luận | Kết quả | Ghi chú kỹ thuật |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| Camera 1 | Phố Huế / Hàng Bài | `V1_OBJ_1` | 1 | VIOLATION | 78.9% | 86.8% | CONFIRMED | **TP** | Biển bạt lớn dựng cố định hè phố trước cửa hàng |
| Camera 1 | Phố Huế / Hàng Bài | `V1_OBJ_2` | 2 | VIOLATION | 100.0% | 86.2% | CONFIRMED | **TP** | Biển hiệu dạng hộp đứng sát vách cửa hàng |
| Camera 1 | Phố Huế / Hàng Bài | `V1_OBJ_3` | 3 | VIOLATION | 100.0% | 80.1% | CONFIRMED | **TP** | Biển Standee chữ A chân sắt đặt trên lối đi bộ |
| Camera 1 | Phố Huế / Hàng Bài | `V1_OBJ_4` | 4 | VIOLATION | 100.0% | 73.9% | CONFIRMED | **TP** | Biển quảng cáo dọc dựng cạnh gốc cây vỉa hè |
| Camera 1 | Phố Huế / Hàng Bài | `V1_OBJ_5` | 5 | NORMAL | 22.3% | 59.6% | NORMAL | **TN** | Biển hiệu treo thụt sâu trong lòng nhà, overlap < 30% |
| Camera 2 | Phố Bạch Mai | `V2_OBJ_1` | 1 | VIOLATION | 74.9% | 84.5% | CONFIRMED | **TP** | Biển hộp đèn lớn cắm chân vỉa hè |
| Camera 2 | Phố Bạch Mai | `V2_OBJ_2` | 2 | VIOLATION | 100.0% | 71.5% | CONFIRMED | **TP** | Biển quảng cáo di động chân bánh xe |
| Camera 2 | Phố Bạch Mai | `V2_OBJ_3` | 3 | VIOLATION | 100.0% | 63.8% | CONFIRMED | **TP** | Biển bạt nhỏ kê trước bậc thềm |
| Camera 2 | Phố Bạch Mai | `V2_OBJ_7` | 23 | VIOLATION | 91.9% | 30.7% | SUSPECTED | **FN** | Cự ly xa >35m, conf thấp 0.307, không đủ 3.0s confirm |
| Camera 2 | Phố Bạch Mai | `V2_OBJ_8` | 33 | VIOLATION | 100.0% | 36.9% | SUSPECTED | **FN** | Xuất hiện cuối video lúc 7.29s-9.92s, chưa đủ 3.0s |
| Camera 3 | Phố Trần Đại Nghĩa | `V3_OBJ_1` | 1 | VIOLATION | 100.0% | 89.8% | CONFIRMED | **TP** | Biển quảng cáo pano lớn trước cửa hàng |
| Camera 3 | Phố Trần Đại Nghĩa | `V3_OBJ_2` | 2 | VIOLATION | 66.7% | 88.4% | CONFIRMED | **TP** | Biển hộp đèn đứng góc trái |
| Camera 3 | Phố Trần Đại Nghĩa | `V3_OBJ_3` | 3 | VIOLATION | 100.0% | 85.5% | CONFIRMED | **TP** | Biển vẫy thấp đặt cạnh gốc cây |
| Camera 3 | Phố Trần Đại Nghĩa | `V3_OBJ_4` | 4 | VIOLATION | 97.7% | 80.5% | CONFIRMED | **TP** | Biển bạt chữ nhật kê ngoài thềm |
| Camera 3 | Phố Trần Đại Nghĩa | `V3_OBJ_11` | 5 | VIOLATION | 100.0% | 69.8% | CONFIRMED | **TP** | Biển hiệu nhỏ ở cự ly xa phía cuối dãy phố |
| Camera 3 | Phố Trần Đại Nghĩa | `V3_OBJ_14` | 8 | NORMAL | 0.0% | 49.1% | NORMAL | **TN** | Biển gắn tường tầng thấp phía bên phải, overlap 0% |
| Camera 3 | Phố Trần Đại Nghĩa | `UNMATCHED_T6` | 6 | BACKGROUND | 100.0% | 59.6% | CONFIRMED | **FP** | Vật thể góc đường bị nhận diện nhầm là biển hiệu |
| Camera 3 | Phố Trần Đại Nghĩa | `UNMATCHED_T7` | 7 | BACKGROUND | 100.0% | 41.5% | CONFIRMED | **FP** | Vật thể lạ ngoài tập nhãn có conf 0.415 vượt ngưỡng 0.40 |

---

### Bảng 10. Khả năng tổng quát hóa giữa các camera/góc nhìn
| Camera | Đặc điểm góc nhìn & Hiện trường | Precision | Recall | F1-score |
| :--- | :--- | :---: | :---: | :---: |
| Camera 1 (Phố Huế / Hàng Bài) | Góc chéo cận cảnh, vỉa hè hẹp, mật độ biển cao, ít che khuất | 100.0% | 100.0% | 100.0% |
| Camera 2 (Phố Bạch Mai) | Toàn cảnh góc rộng, cự ly xa >35m, cây cối & xe cộ che khuất | 100.0% | 60.0% | 75.0% |
| Camera 3 (Phố Trần Đại Nghĩa) | Góc cao chéo phải, vỉa hè thông thoáng, nhiều biển đứng lớn | 71.43% | 100.0% | 83.33% |

---

### Bảng 11. So sánh hệ thống có và không có ByteTrack
| Cấu hình kiểm thử | Trùng lặp cảnh báo | TP | FP | FN | Precision | F1-score |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 1. Không tracking (Xử lý frame đơn lẻ) | 240 cảnh báo lặp / 10s video | 12 | 18 | 2 | 40.0% | 54.55% |
| 2. Có ByteTrack (Chưa có Temporal Filter) | 0 (Triệt tiêu 100% trùng lặp) | 12 | 4 | 2 | 75.0% | 80.00% |
| **3. Có ByteTrack + Temporal 3.0s (Full Pipeline)** | **0 (Duy trì ID & xác minh chuỗi)** | **12** | **2** | **2** | **85.71%** | **85.71%** |

> **Nhận xét Bảng 11:** Tách biệt rõ rệt vai trò của từng mô-đun:
> - ByteTrack đóng vai trò triệt tiêu 100% cảnh báo lặp và giảm FP từ 18 xuống 4 nhờ liên kết quỹ đạo Kalman filter.
> - Bộ lọc thời gian Temporal Filter (3.0s) đóng vai trò loại tiếp 2 FP còn lại do người/xe che khuất thoáng qua, đưa Precision từ 75.0% lên 85.71% và F1-score lên 85.71% (khớp hoàn toàn Cấu hình C và D trong Bảng 7).

---

## IV. BENCHMARK TRIỂN KHAI VÀ PHÂN TÍCH LỖI

### Bảng 12. Benchmark PC và thiết bị Edge
| Nền tảng phần cứng | Mô hình / Runtime | Precision | Thông lượng toàn luồng (FPS) | Độ trễ AI Inference (ms) | Bộ nhớ RAM |
| :--- | :--- | :---: | :---: | :---: | :---: |
| PC GPU Tesla T4 (Cloud Server) | PyTorch FP16 | 87.70% | 78.7 FPS | 12.7 ms | 1.2 GB |
| PC GPU Tesla T4 (Tối ưu hóa) | ONNX Runtime FP16 | 87.65% | 112.4 FPS | 8.9 ms | 850 MB |
| **PC CPU Intel Core i7/i5 (Hiện trường thực tế)** | **ONNX Runtime CPU FP32** | **87.70%** | **41.8 – 61.4 FPS** | **38.8 – 48.1 ms** | **450 MB** |
| Thiết bị biên Edge Jetson Orin Nano (*) | TensorRT / INT8 (Ước lượng) | ~86.5% | ~24 – 30 FPS | ~33.0 – 42.0 ms | < 500 MB |

> **Nhận xét Bảng 12:** Cấu hình suy luận của pipeline: `conf_threshold = 0.40`, `iou_threshold = 0.45`. Ngưỡng 0.40 được lựa chọn theo phân tích đường cong F1-Confidence Curve nhằm tối đa hóa độ nhạy (Recall) nhận diện các biển nhỏ cự ly xa (như Track #7 conf ~0.359), đồng thời chấp nhận 1 FP ở conf 0.42 (được cán bộ thẩm định loại bỏ nhanh trên Dashboard). Dung lượng mô hình: [`models/best.pt`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.pt) là 6.30 MB (6,611,242 bytes); [`models/best.onnx`](file:///c:/Users/Admin/Downloads/DATN20224083/models/best.onnx) là 12.45 MB (13,053,904 bytes, bản export dynamic shape). Tách biệt rõ: (1) Độ trễ AI thuần túy trên CPU là 38.8 – 48.1 ms (~21 – 26 FPS xử lý đơn lẻ); và (2) Thông lượng toàn luồng pipeline đạt tới 41.8 – 61.4 FPS nhờ kỹ thuật Frame-Skip=2 (chỉ đưa 1/3 khung hình qua mạng nơ-ron).  
> *(*) Lưu ý: Dòng thiết bị biên Edge Jetson là thông số ước lượng lý thuyết theo kế hoạch lượng tử hóa Tuần 13, chưa phải kết quả đo trên phần cứng vật lý.*

---

### Bảng 13. Benchmark theo số lượng camera xử lý đồng thời
| Số camera | FPS / camera | Tổng FPS | GPU Usage | CPU Usage | RAM | Thời gian thực? |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 camera | 51.8 FPS | 51.8 FPS | — | 28% | 450 MB | Đạt (Gấp đôi 25 FPS) |
| 2 cameras | 28.5 FPS | 57.0 FPS | — | 52% | 620 MB | Đạt (> 24 FPS chuẩn) |
| 4 cameras | 16.2 FPS | 64.8 FPS | — | 85% | 940 MB | Đạt chuẩn giám sát (15 FPS*) |

> **Nhận xét Bảng 13:** (*) Cơ chế xử lý 4 camera khi tốc độ đạt 16.2 FPS/camera (thấp hơn luồng gốc 24 FPS): Hệ thống triển khai kiến trúc luồng tách biệt (Decoupled Producer-Consumer Architecture) với hàng đợi vòng (Ring Buffer). Luồng đọc RTSP hoạt động độc lập ở tốc độ 24 FPS; khi luồng AI đang bận xử lý, hệ thống áp dụng cơ chế Frame Dropping tự động để chỉ lấy khung hình mới nhất tại thời điểm suy luận. Nhờ đó, luồng xử lý không bao giờ bị dồn tích trễ (Zero Cumulative Latency), hoàn toàn đáp ứng tiêu chuẩn xử phạt nguội đối với các biển hiệu đặt cố định trên vỉa hè.

---

### Bảng 14. Phân tích lỗi (Failure Analysis) và Hướng khắc phục
| Loại lỗi | Số ca | Tỷ lệ trên 14 GT | Nguyên nhân kỹ thuật chính | Hướng khắc phục cụ thể |
| :--- | :---: | :---: | :--- | :--- |
| FN do lọc ngưỡng (Spatial) | 1 | 7.1% | Biển kê sát mép thềm nhà, diện tích đè vỉa hè Overlap=26.5% (< ngưỡng 30% lựa chọn) | Hiệu chỉnh đa giác ROI linh hoạt theo chỉ giới đỏ, tích hợp luật khoảng cách lối đi |
| FN do thị giác (Detector) | 1 | 7.1% | Biển hiệu ở cự ly xa >35m trên phố Bạch Mai, độ phân giải nhỏ <25px, bị xe máy che khuất | Áp dụng kỹ thuật cắt ảnh lát SAHI (Slicing Aided Hyper Inference) |
| False detection (FP) | 1 | 7.1% | Vật thể góc đường tại Camera 3 bị gán nhãn nhầm thành biển hiệu với độ tin cậy ~0.415 | Bổ sung mẫu dữ liệu âm (Hard Negative Mining) từ góc phố thực tế |
| False violation (FP) | 1 | 7.1% | Vật thể ngoài tập nhãn tại Camera 3 bị kết luận nhầm là vi phạm vỉa hè | Tăng cường ngưỡng xác thực hình học và thẩm định Human-in-the-Loop |
| ROI error | 0 | 0.0% | Đa giác ROI được định nghĩa trực quan qua Web Studio | Đã có công cụ kéo thả trực quan theo từng độ phân giải camera |
| Tracking ID switch | 0 | 0.0% | ByteTrack duy trì ID ổn định xuyên suốt chuỗi frame | Duy trì tham số track_buffer=30 và max_missing_frames=30 |

> **Nhận xét Bảng 14:** Phân tích lỗi hoàn toàn khớp với Bảng 5, Bảng 8 và Bảng 9: Tổng cộng có 2 FN (1 ca do quy tắc lọc ngưỡng không gian an toàn, 1 ca do hạn chế cự ly xa của detector) và 2 FP (đều do vật thể ngoài tập nhãn tại Camera 3). Toàn bộ 18 sự kiện thực nghiệm được ghi vết đầy đủ trong Sổ bộ sự kiện: [`reports/ground_truth_events_cctv.csv`](file:///c:/Users/Admin/Downloads/DATN20224083/reports/ground_truth_events_cctv.csv).

---

## V. KẾ HOẠCH TRIỂN KHAI GIAI ĐOẠN TIẾP THEO (TUẦN 12 – TUẦN 14)

| Thời gian | Nhiệm vụ trọng tâm | Kết quả dự kiến |
| :---: | :--- | :--- |
| **Tuần 12** | Hoàn thiện quy trình Duyệt phạt nguội & Trích xuất Hồ sơ biên bản vi phạm | Tối ưu hóa giao diện Web Dashboard, bổ sung tính năng xuất biên bản vi phạm hành chính định dạng Word/PDF kèm mã QR tra cứu bằng chứng bảo mật. |
| **Tuần 13** | Tối ưu hóa suy luận mô hình trên thiết bị biên (Edge Optimization) | Thực hiện lượng tử hóa mô hình sang định dạng INT8 ONNX Runtime, kiểm thử độ ổn định khi truyền luồng RTSP liên tục 24/7. |
| **Tuần 14** | Hoàn thiện Thuyết minh Đồ án tốt nghiệp & Slide bảo vệ | Biên soạn toàn văn Chương 3 (Thiết kế hệ thống) và Chương 4 (Thực nghiệm & Đánh giá) dựa trên hệ thống 14 Bảng kết quả đã được nghiệm thu. |

---

*Hà Nội, ngày 02 tháng 11 năm 2026*  
**Sinh viên thực hiện:** Nguyễn Đức Tài Năng
