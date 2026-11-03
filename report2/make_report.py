from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

out = Path(__file__).parent / 'Bao_cao_tuan_9_11.docx'
doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(.72); sec.bottom_margin = Inches(.72)
sec.left_margin = Inches(.82); sec.right_margin = Inches(.82)
styles = doc.styles
styles['Normal'].font.name = 'Arial'; styles['Normal'].font.size = Pt(10)
styles['Normal'].font.color.rgb = RGBColor(35, 45, 60)
for s in ['Heading 1','Heading 2']:
    styles[s].font.name='Arial'; styles[s].font.color.rgb=RGBColor(30,58,138)

p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('BÁO CÁO TIẾN ĐỘ ĐỒ ÁN'); r.bold=True; r.font.size=Pt(18); r.font.color.rgb=RGBColor(30,58,138)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('TUẦN 9–11 | HUẤN LUYỆN, ĐÁNH GIÁ VÀ TINH CHỈNH YOLOv8n'); r.bold=True; r.font.size=Pt(11); r.font.color.rgb=RGBColor(15,118,110)

t=doc.add_table(rows=3, cols=2); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.style='Light Shading Accent 1'
for row, vals in zip(t.rows,[('Sinh viên','Nguyễn Đức Tài Năng — MSSV 20224083'),('Đề tài','Hệ thống phát hiện biển quảng cáo lấn chiếm vỉa hè qua camera CCTV'),('Ngày lập','03/11/2026')]):
    for c,v in zip(row.cells, vals): c.text=v; c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER

doc.add_heading('1. Mục tiêu giai đoạn', level=1)
doc.add_paragraph('Huấn luyện YOLOv8n trên dữ liệu biển hiệu/biển quảng cáo; đánh giá bằng Precision, Recall, mAP; rà soát nhu cầu làm sạch hoặc bổ sung dữ liệu.')
doc.add_heading('2. Công việc và kết quả', level=1)
items=[
('Huấn luyện mô hình.',' Cấu hình tại runs/detect/train_v13/args.yaml: tối đa 100 epoch, ảnh 1280×1280, batch 8, optimizer AdamW. Nhật ký results.csv ghi 51 epoch hoàn tất; epoch 49 là tốt nhất theo mAP@0.5.'),
('Đánh giá detector.',' Tại epoch 49: Precision 90.45%, Recall 82.87%, mAP@0.5 90.03%, mAP@0.5:0.95 61.69%. Đây là metric validation trong quá trình huấn luyện, không phải đánh giá video thực địa.'),
('Sản phẩm.',' Có models/best.pt (6,611,242 byte) và models/best.onnx (13,053,904 byte). Cấu hình hệ thống dùng models/best.pt và imgsz=640.'),
('Minh chứng.',' Có 3 ảnh nhận diện trong data/images/output_v13/. Ảnh minh họa kết quả chạy trên ảnh hiện trường, không thay thế phép đo Precision/Recall.'),
('Việc cần rà soát.',' Kiểm tra riêng lỗi bỏ sót biển nhỏ/xa, độ tin cậy theo bối cảnh và hiệu chuẩn ROI trước khi chốt kết quả cấp hệ thống. Không đưa số lượng ảnh dataset vào báo cáo do chưa kiểm kê trực tiếp trong lần lập này.')]
for head,body in items:
    p=doc.add_paragraph(style='List Bullet'); rr=p.add_run(head); rr.bold=True; p.add_run(body)

doc.add_heading('3. Đánh giá chung', level=1)
doc.add_paragraph('Đã có checkpoint YOLOv8n và bộ chỉ số validation cụ thể; mAP@0.5 của checkpoint tốt nhất đạt 90.03%. Recall 82.87% cho thấy cần rà soát các trường hợp bị bỏ sót. Chỉ số detector được trình bày riêng, không gộp với chỉ số phán quyết vi phạm của toàn pipeline.')
doc.add_heading('4. Kế hoạch tiếp theo', level=1)
for x in ['Đối chiếu lỗi dự đoán với nhãn trên tập test độc lập; phân loại false positive và false negative.','Bổ sung hoặc làm sạch mẫu khó khi có bằng chứng lỗi, ưu tiên biển nhỏ, che khuất và điều kiện ánh sáng khác nhau.','Đo lại metric sau tinh chỉnh, ghi rõ tập dữ liệu, checkpoint, cấu hình và ngưỡng.','Đánh giá riêng detector–tracking–ROI trên video theo Precision/Recall cấp sự kiện và tốc độ xử lý.']:
    doc.add_paragraph(x, style='List Bullet')
doc.add_heading('5. Nguồn số liệu', level=1)
doc.add_paragraph('runs/detect/train_v13/results.csv; runs/detect/train_v13/args.yaml; configs/settings.yaml; models/best.pt; models/best.onnx; data/images/output_v13/.')
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('Báo cáo được tổng hợp từ các tệp nguồn của đồ án; không đọc hoặc sử dụng tài liệu trong thư mục reports.'); r.italic=True; r.font.size=Pt(8); r.font.color.rgb=RGBColor(100,116,139)
doc.save(out)
print(out)
