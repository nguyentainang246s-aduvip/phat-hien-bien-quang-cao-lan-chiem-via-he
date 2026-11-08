# Prompt nhận xét báo cáo Word tuần 9–11

Sao chép prompt bên dưới khi yêu cầu AI kiểm tra báo cáo. Đính kèm `reports/Bao_cao_tien_do_Tuan_9_11_DATN_20224083_v13_clean_chuan.docx` và, nếu AI không truy cập được thư mục dự án, đính kèm thêm các tệp nguồn được nêu trong prompt.

```text
Hãy đọc và nhận xét báo cáo Word tiến độ đồ án tuần 9–11 tại:
`reports/Bao_cao_tien_do_Tuan_9_11_DATN_20224083_v13_clean_chuan.docx`

Đây là báo cáo tiến độ kỹ thuật của đồ án tốt nghiệp, không phải bài báo khoa học. Hãy viết phản hồi bằng tiếng Việt, công tâm, cụ thể và có tính hướng dẫn để sinh viên hoàn thiện báo cáo. Chỉ đánh giá đúng phiên bản Word được chỉ định; không trộn nội dung từ các bản báo cáo tuần 9–11 khác trong `reports/` hoặc `report2/`. Tài liệu khác trong dự án chỉ được dùng làm nguồn kiểm chứng, không thay thế bản cần nhận xét.

## Quy trình và skill cần áp dụng

1. Dùng skill `docx` để đọc toàn bộ tài liệu Word. Kiểm tra cả nội dung văn bản, bảng và cách trình bày nếu có khả năng render. Phân biệt lỗi nội dung với lỗi bố cục; nếu chưa xem được bản render, nói rõ giới hạn này.
2. Dùng skill `academic-paper-reviewer` theo hướng kiểm tra có căn cứ: xác định đúng bản và phạm vi; đọc toàn bộ báo cáo; nêu vị trí chính xác của từng nhận xét; phân biệt lỗi đã xác minh, điểm chưa đủ bằng chứng và đề xuất tùy chọn. Đây là báo cáo tiến độ nên không áp máy móc tiêu chí bài báo, trích dẫn hay chấm điểm học thuật không được yêu cầu.
3. Dùng các phần phù hợp của `yolo-training` và `yolo-datasets` để kiểm tra cách diễn giải quá trình huấn luyện, chọn checkpoint, metric validation, cấu hình và hạn chế dữ liệu. Dùng `yolo-inference` khi nhận xét về cấu hình chạy dự đoán hoặc đánh giá trên ảnh/video. Chỉ dùng hướng dẫn kỹ năng để định hướng kiểm tra, không coi chúng là bằng chứng rằng dự án đã thực hiện một việc nào đó.

## Tệp cần đối chiếu trong workspace

- `runs/detect/train_v13/results.csv`
- `runs/detect/train_v13/args.yaml`
- `configs/settings.yaml`
- `models/best.pt` và `models/best.onnx` (nếu cần xác minh sự tồn tại/kích thước)
- `reports/figures/v13_clean/` (bao gồm log, bảng, biểu đồ và ma trận nhầm lẫn được trích dẫn trong báo cáo)
- `reports/benchmark_report.md`, `reports/system_eval_report.md` và script sinh kết quả, nếu có
- Dataset `v13_clean`, cấu hình `data.yaml`, log đánh giá val/test và các tệp kiểm toán trùng lặp/nhãn được trích dẫn trong báo cáo, nếu chúng hiện diện và truy cập được
- Ảnh minh họa được nhắc trong báo cáo như `data/images/output_v13_clean/` (chỉ xác minh nội dung ảnh nếu có thể xem trực tiếp)

Không dùng tên tệp làm bằng chứng thay cho việc kiểm tra nội dung. Không chạy huấn luyện lại, không sửa tài liệu, mã nguồn, dữ liệu hoặc kết quả. Nếu không thể truy cập một nguồn, đánh dấu nội dung liên quan là “chưa xác minh”, không kết luận là sai.

Lưu ý về định danh lần chạy: báo cáo gọi lần huấn luyện là `v13_clean`, trong khi workspace cũng có `runs/detect/train_v13/`. Không mặc định hai tên này chỉ cùng một lần chạy. Trước khi dùng `train_v13/results.csv` hay `args.yaml` để đối chiếu, xác minh quan hệ bằng run ID, log, cấu hình, thời điểm, checkpoint hoặc locator nguồn được báo cáo dẫn. Ưu tiên các log/artefact của `v13_clean` được nêu trong chính báo cáo. Nếu không chứng minh được hai lần chạy là một, báo rõ chưa xác minh và không dùng số liệu của lần chạy kia để phủ định hoặc xác nhận báo cáo.

## Các điểm kiểm tra trọng tâm

- Đối chiếu số epoch hoàn tất, epoch có mAP@0.5 cao nhất và các giá trị Precision, Recall, mAP@0.5, mAP@0.5:0.95 trực tiếp từ log/CSV của đúng lần chạy `v13_clean`. Nêu rõ cách làm tròn và tên cột/epoch làm căn cứ; không dùng CSV của lần chạy khác nếu chưa xác minh được định danh.
- Kiểm tra cách gọi các số liệu là metric trên tập validation trong quá trình huấn luyện; không để người đọc hiểu nhầm đó là kết quả test độc lập, kết quả video thực địa hoặc metric của toàn pipeline.
- Đối chiếu cấu hình train với cấu hình suy luận đang dùng. Nếu kích thước ảnh train và inference khác nhau (ví dụ 1280 và 640), nêu đây là điểm cần giải thích hoặc xác minh ảnh hưởng, không tự kết luận mô hình sai.
- Kiểm tra sự nhất quán giữa mô tả “tối đa 100 epoch”, số epoch thực chạy và lý do dừng nếu có thể xác định từ log/cấu hình. Phân biệt early stopping với hoàn thành đủ số epoch; không suy diễn nguyên nhân nếu thiếu bằng chứng.
- Kiểm tra liệu báo cáo nêu rõ tập dữ liệu/split, nguồn nhãn, cỡ mẫu, ngưỡng và điều kiện đánh giá hay chưa. Không tự tạo số lượng ảnh. Lưu ý nguy cơ rò rỉ dữ liệu nếu các ảnh cùng video/cùng bối cảnh xuất hiện ở nhiều split, nhưng chỉ gọi là nguy cơ cần kiểm tra khi chưa kiểm chứng được.
- Kiểm tra tính nhất quán số học giữa các bảng: tổng ảnh/nhãn theo split; số TP/FP/FN với Precision/Recall/F1; dải kết quả tổng hợp so với kết quả từng camera; ngưỡng chọn so với bảng khảo sát; số đối tượng test theo kích thước so với tổng số nhãn; và các số benchmark với độ trễ/FPS. Nêu công thức, phép tính và dòng/bảng nguồn cho mọi mâu thuẫn.
- Kiểm tra các tuyên bố mạnh như “độc lập tuyệt đối”, “rò rỉ 0%”, “đã xác minh 100%”, “tổng quát hóa xuất sắc”, “không bị overfitting” và “đáp ứng thời gian thực” có được bằng chứng và phạm vi đo hỗ trợ đầy đủ hay không. Hạ mức khẳng định khi bằng chứng chỉ cho phép kết luận hạn chế; không biến sự tương đồng giữa hai split thành bằng chứng tổng quát hóa.
- Xác minh quan hệ giữa bảng kết quả, đoạn diễn giải, hình minh họa, log nguồn và mã lệnh tạo kết quả. Ghi rõ tệp nguồn nào tồn tại/đọc được, tệp nào thiếu hoặc không đủ chứng minh; đừng chấp nhận nhãn “đã xác minh” trong báo cáo như bằng chứng tự thân.
- Kiểm tra hình thức trích dẫn các bảng đề xuất/PDF: tài liệu đó có thực sự được cung cấp không, tên gọi và số thứ tự có nhất quán không; không khẳng định tuân thủ đề cương nếu chưa đọc được bản gốc.
- Đánh giá xem ảnh minh họa có được mô tả đúng là minh chứng định tính và có bị dùng thay cho đánh giá định lượng hay không.
- Nhận xét kế hoạch tiếp theo có đo được và bám sát hạn chế đã nêu không; ưu tiên phân biệt đánh giá detector với đánh giá sự kiện của pipeline detector–tracking–ROI.
- Kiểm tra tính rõ ràng, chính tả, thuật ngữ, cấu trúc, tiêu đề, bảng, ngày tháng và mức độ phù hợp của độ dài với một báo cáo tiến độ tuần.

## Định dạng kết quả

### 1. Nhận xét chung
Tóm tắt mục đích báo cáo, điểm làm tốt nhất và vấn đề quan trọng nhất cần xử lý. Không chấm điểm tổng thể trừ khi có rubric được cung cấp.

### 2. Bảng nhận xét theo vị trí

| Mức độ | Vị trí trong Word | Nhận xét và bằng chứng | Vì sao cần sửa | Hướng sửa cụ thể |
|---|---|---|---|---|

Chỉ đưa vào bảng các nhận xét hữu ích. Gắn mức độ “Nghiêm trọng”, “Cần sửa” hoặc “Gợi ý”. Ghi tiêu đề/mục và một cụm từ ngắn để định vị; không chỉ nhận xét chung chung như “cần viết rõ hơn”.

### 3. Đối chiếu số liệu

Liệt kê số trong báo cáo, số đọc từ nguồn, kết quả khớp/không khớp/chưa xác minh và đường dẫn nguồn cụ thể. Không làm tròn lại nếu không giải thích.

### 4. Việc nên sửa trước khi nộp

Đưa danh sách ngắn theo thứ tự ưu tiên. Nếu có thể, đề xuất câu thay thế cho các câu đang gây hiểu nhầm; giữ nguyên kết quả thực tế và không thêm tuyên bố chưa có minh chứng.

### 5. Giới hạn kiểm tra

Nêu rõ tài liệu/ảnh/cấu hình nào đã xem, phần nào chưa truy cập hoặc chưa render, và kết luận nào vì vậy chỉ là nhận định sơ bộ. Không khẳng định đã chạy lại thí nghiệm nếu thực tế không chạy.
```
