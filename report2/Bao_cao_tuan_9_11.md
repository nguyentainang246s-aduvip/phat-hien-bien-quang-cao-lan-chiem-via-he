# BÁO CÁO TIẾN ĐỘ ĐỒ ÁN – TUẦN 9–11

**Ngày lập:** 03/11/2026  
**Sinh viên:** Nguyễn Đức Tài Năng — MSSV 20224083  
**Đề tài:** Hệ thống phát hiện biển quảng cáo lấn chiếm vỉa hè qua camera CCTV

## Mục tiêu giai đoạn

- Huấn luyện YOLOv8n trên bộ dữ liệu biển hiệu/biển quảng cáo.
- Đánh giá và tinh chỉnh mô hình bằng Precision, Recall, mAP; xem xét bổ sung/làm sạch dữ liệu khi cần.

## Công việc và kết quả

1. **Huấn luyện:** cấu hình huấn luyện trong `runs/detect/train_v13/args.yaml` cho thấy YOLOv8n được huấn luyện tối đa 100 epoch, ảnh đầu vào 1280×1280, batch 8, optimizer AdamW. Nhật ký `results.csv` ghi nhận 51 epoch hoàn tất; checkpoint tốt nhất theo mAP@0.5 là epoch 49.
2. **Đánh giá detector:** tại epoch 49, Precision = **90.45%**, Recall = **82.87%**, mAP@0.5 = **90.03%**, mAP@0.5:0.95 = **61.69%**. Đây là chỉ số validation trong nhật ký huấn luyện, không phải kết quả đánh giá video thực địa.
3. **Đầu ra mô hình:** có `models/best.pt` (6,611,242 byte) và `models/best.onnx` (13,053,904 byte). Cấu hình hệ thống trỏ tới checkpoint `models/best.pt`; kích thước suy luận cấu hình là 640.
4. **Minh chứng nhận diện:** có 3 ảnh kết quả trong `data/images/output_v13/`. Các ảnh này thể hiện kết quả chạy mô hình trên ảnh hiện trường; không suy diễn chúng thành phép đo Precision/Recall.
5. **Tinh chỉnh tiếp:** cần kiểm tra riêng lỗi bỏ sót biển nhỏ/xa, độ tin cậy theo bối cảnh và hiệu chuẩn ROI trước khi chốt kết quả cấp hệ thống. Bộ dữ liệu hiện có các tập train/valid/test; số ảnh không ghi trong báo cáo vì chưa được kiểm kê trực tiếp trong lần lập này.

## Đánh giá chung

Đã có checkpoint YOLOv8n và bộ chỉ số validation cụ thể; mAP@0.5 của checkpoint tốt nhất đạt 90.03%. Kết quả cho thấy mô hình có khả năng phát hiện tốt trên tập validation, trong khi Recall 82.87% cho thấy vẫn cần tiếp tục rà soát các trường hợp bị bỏ sót. Không gộp chỉ số detector với chỉ số phán quyết vi phạm của toàn pipeline.

## Kế hoạch tiếp theo

- Đối chiếu lỗi dự đoán với nhãn trên tập test độc lập và phân loại false positive/false negative.
- Bổ sung hoặc làm sạch mẫu khó khi có bằng chứng lỗi, nhất là biển nhỏ, bị che khuất và điều kiện ánh sáng khác nhau.
- Đo lại các chỉ số sau tinh chỉnh; ghi rõ tập dữ liệu, checkpoint, cấu hình và ngưỡng đánh giá.
- Kiểm tra kết quả tích hợp detector–tracking–ROI trên video, báo cáo riêng Precision/Recall cấp sự kiện và tốc độ xử lý.

## Nguồn số liệu trong đồ án

- `runs/detect/train_v13/results.csv` — nhật ký metric theo epoch; checkpoint tốt nhất chọn theo mAP@0.5.
- `runs/detect/train_v13/args.yaml` — cấu hình huấn luyện.
- `configs/settings.yaml` — cấu hình chạy hệ thống.
- `models/best.pt`, `models/best.onnx` — tệp trọng số hiện có.
- `data/images/output_v13/` — ảnh minh chứng nhận diện.

*Ghi chú: Báo cáo được tổng hợp từ các tệp nguồn của đồ án; không mở hoặc sử dụng bất kỳ báo cáo nào trong thư mục `reports`.*
