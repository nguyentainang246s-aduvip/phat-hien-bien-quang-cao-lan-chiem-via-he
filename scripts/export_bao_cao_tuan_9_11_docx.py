"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Script xuất Báo cáo tiến độ Tuần 9 - 11 ra file Microsoft Word (.docx)
SỬ DỤNG 100% SỐ LIỆU VÀ ẢNH THỰC NGHIỆM TỪ MÔ HÌNH V13 FINAL (data/images/output_v13/)
Đảm bảo tính nhất quán toán học 100%, có thể truy vết trên 14 Bảng kết quả thực nghiệm.
Sinh viên thực hiện: Nguyễn Đức Tài Năng - MSSV: 20224083
==============================================================================
"""

import os
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = str(OUTPUT_DIR / "Bao_cao_tien_do_Tuan_9_11_DATN_20224083.docx")

# Màu sắc nhận diện chuẩn ĐHBK Hà Nội (HUST Navy Blue, Teal & Slate)
COLOR_PRIMARY = RGBColor(30, 58, 138)     # Navy #1E3A8A
COLOR_SECONDARY = RGBColor(15, 118, 110)  # Teal #0F766E
COLOR_DARK = RGBColor(30, 41, 59)         # Slate Dark #1E293B
COLOR_MUTED = RGBColor(100, 116, 139)     # Slate Gray #64748B
COLOR_RED = RGBColor(220, 38, 38)         # Red #DC2626
COLOR_GREEN = RGBColor(16, 185, 129)      # Emerald Green #10B981

HEX_PRIMARY = "1E3A8A"
HEX_SECONDARY = "0F766E"
HEX_BG_LIGHT = "F8FAFC"
HEX_BG_ZEBRA = "F1F5F9"
HEX_BORDER = "CBD5E1"
HEX_HEADER_BG = "1E3A8A"
HEX_CALLOUT_BG = "EFF6FF"
HEX_CALLOUT_BORDER = "3B82F6"
HEX_SUCCESS_BG = "ECFDF5"
HEX_SUCCESS_BORDER = "10B981"
HEX_WARNING_BG = "FEF2F2"
HEX_WARNING_BORDER = "EF4444"


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def set_cell_background(cell, hex_color):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)


def set_table_borders(table, hex_color=HEX_BORDER):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="{hex_color}"/>'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{hex_color}"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{hex_color}"/>'
        f'  <w:insideV w:val="none"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def format_table_header(row, headers, col_widths=None):
    for j, h in enumerate(headers):
        cell = row.cells[j]
        set_cell_background(cell, HEX_HEADER_BG)
        set_cell_margins(cell, 90, 90, 110, 110)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        if col_widths and j < len(col_widths):
            cell.width = col_widths[j]


def add_callout_box(doc, text, title="KẾT LUẬN QUAN TRỌNG", box_type="info"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    
    if box_type == "success":
        bg_color, border_color = HEX_SUCCESS_BG, HEX_SUCCESS_BORDER
        title_color = COLOR_GREEN
    elif box_type == "warning":
        bg_color, border_color = HEX_WARNING_BG, HEX_WARNING_BORDER
        title_color = COLOR_RED
    else:
        bg_color, border_color = HEX_CALLOUT_BG, HEX_CALLOUT_BORDER
        title_color = COLOR_PRIMARY
        
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'  <w:top w:val="none"/>'
        f'  <w:bottom w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    cell._tc.get_or_add_tcPr().append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    run_title = p.add_run(f"{title}: ")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(10)
    run_title.font.bold = True
    run_title.font.color.rgb = title_color
    
    run_text = p.add_run(text)
    run_text.font.name = "Arial"
    run_text.font.size = Pt(9.5)
    run_text.font.color.rgb = COLOR_DARK
    
    doc.add_paragraph()


def add_image_with_caption(doc, img_path, caption, asset_path=None, width=Inches(6.0)):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=width)
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(4)
        run_cap = p_cap.add_run(caption)
        run_cap.font.name = "Arial"
        run_cap.font.size = Pt(9.0)
        run_cap.font.bold = True
        run_cap.font.italic = True
        run_cap.font.color.rgb = COLOR_DARK
    else:
        p_missing = doc.add_paragraph()
        p_missing.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_m = p_missing.add_run(f"[HÌNH ẢNH: {caption}]")
        r_m.font.name = "Arial"
        r_m.font.color.rgb = COLOR_MUTED
        r_m.italic = True

    if asset_path:
        p_src = doc.add_paragraph()
        p_src.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_src.paragraph_format.space_before = Pt(0)
        p_src.paragraph_format.space_after = Pt(6)
        r_src = p_src.add_run(f"📍 Tệp kết quả xuất từ mô hình v13 Final: {asset_path}")
        r_src.font.name = "Consolas"
        r_src.font.size = Pt(8.0)
        r_src.font.color.rgb = COLOR_MUTED


def build_tuan_9_11_report():
    doc = Document()
    
    # Cấu hình lề trang chuẩn A4
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(0.8)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)

    # =========================================================================
    # TIÊU ĐỀ CHÍNH
    # =========================================================================
    title = doc.add_heading("BÁO CÁO TIẾN ĐỘ ĐỒ ÁN TỐT NGHIỆP", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.name = "Arial"
    title.runs[0].font.size = Pt(17)
    title.runs[0].font.bold = True
    title.runs[0].font.color.rgb = COLOR_PRIMARY

    sub_title = doc.add_paragraph()
    sub_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_title.add_run(
        "GIAI ĐOẠN: TUẦN 9 – TUẦN 11\n"
        "CHỦ ĐỀ: HUẤN LUYỆN, ĐÁNH GIÁ & TINH CHỈNH MÔ HÌNH YOLOV8N TRÊN DỮ LIỆU TỰ THU THẬP\n"
        "(Tham chiếu chi tiết: Hệ thống 14 Bảng Kết Quả Đề Xuất ĐATN CCTV)"
    )
    sub_run.font.name = "Arial"
    sub_run.font.size = Pt(11)
    sub_run.font.bold = True
    sub_run.font.color.rgb = COLOR_SECONDARY

    # =========================================================================
    # KHUNG THÔNG TIN HÀNH CHÍNH
    # =========================================================================
    info_tbl = doc.add_table(rows=6, cols=2)
    info_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(info_tbl)
    
    meta_data = [
        ("Tên đề tài:", "Hệ thống giám sát và phát hiện biển quảng cáo/biển hiệu lấn chiếm vỉa hè qua camera CCTV cố định"),
        ("Sinh viên thực hiện:", "Nguyễn Đức Tài Năng — MSSV: 20224083 — Lớp: ĐATN K67"),
        ("Đơn vị đào tạo:", "Đại học Bách Khoa Hà Nội"),
        ("Giảng viên hướng dẫn:", "Thầy/Cô Cán bộ Hướng dẫn ĐATN"),
        ("Kế hoạch Tuần 9 - 11:", "• Thu thập & làm sạch dữ liệu hình ảnh (Roboflow v13: 2,674 ảnh; train thực tế 2,276 ảnh sau lọc).\n• Train YOLOv8n, tối ưu hóa siêu tham số, khảo sát phân nhóm kích thước đối tượng & môi trường.\n• Đo đạc thực nghiệm toàn diện theo 14 Bảng kết quả đề xuất trên 3 video CCTV thực địa Hà Nội."),
        ("Sản phẩm nghiệm thu:", "• Trọng số mô hình: models/best.pt (6.30 MB) & models/best.onnx (12.45 MB - Dynamic Shape).\n• Dữ liệu minh chứng CSV: reports/test_subset_breakdown.csv & reports/ground_truth_events_cctv.csv.\n• Thư mục kết quả nhận diện thực tế: data/images/output_v13/ (21 biển phát hiện).")
    ]
    
    for i, (k, v) in enumerate(meta_data):
        row = info_tbl.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width, c1.width = Inches(2.2), Inches(4.3)
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
        set_cell_background(c0, HEX_BG_LIGHT)
        
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.font.name = "Arial"
        r0.font.size = Pt(9.5)
        r0.font.bold = True
        r0.font.color.rgb = COLOR_PRIMARY
        
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.name = "Arial"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = COLOR_DARK

    doc.add_paragraph()

    # =========================================================================
    # DANH MỤC HÌNH ẢNH MINH HỌA XUẤT TỪ MÔ HÌNH V13 FINAL
    # =========================================================================
    doc.add_heading("DANH MỤC HÌNH ẢNH MINH CHỨNG THỰC NGHIỆM MÔ HÌNH V13 FINAL", level=1)
    doc.add_paragraph(
        "Toàn bộ hình ảnh minh chứng trong báo cáo này được trích xuất trực tiếp từ mô hình YOLOv8n Version 13 Final "
        "(models/best.pt) trên tập ảnh hiện trường đường phố tại data/images/ và lưu tại thư mục data/images/output_v13/:"
    )

    tbl_asset_guide = doc.add_table(rows=4, cols=4)
    tbl_asset_guide.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_asset_guide)
    
    format_table_header(
        tbl_asset_guide.rows[0],
        ["Ký hiệu", "Tên ảnh & Tình huống thực nghiệm", "Tệp xuất kết quả (output_v13)", "Kết quả phát hiện của mô hình v13 Final"],
        [Inches(0.8), Inches(2.2), Inches(2.1), Inches(1.4)]
    )

    asset_guide_rows = [
        ("Hình 1", "Ảnh thực nghiệm 1: Phố Hàng Bạc (1598×984)", "data/images/output_v13/v13_detected_1.png", "Phát hiện 10 biển hiệu (9 vi phạm, 1 hợp lệ, Conf lên đến 90.8%)"),
        ("Hình 2", "Ảnh thực nghiệm 2: Phố cổ Hà Nội (1529×1028)", "data/images/output_v13/v13_detected_2.png", "Phát hiện 6 biển: 4 vi phạm (đè vỉa hè 97-100%), 2 mép vỉa hè (2-19%)"),
        ("Hình 3", "Ảnh thực nghiệm 3: Tuyến phố đi bộ (1084×615)", "data/images/output_v13/v13_detected_3.png", "Phát hiện 5/5 biển vi phạm vỉa hè (Conf 76.3% - 85.9%)")
    ]

    for idx, (fig_id, name, path_val, desc) in enumerate(asset_guide_rows):
        row = tbl_asset_guide.rows[idx + 1]
        bg = HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF"
        for j, val in enumerate([fig_id, name, path_val, desc]):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j == 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Consolas" if j == 2 else "Arial"
            r.font.size = Pt(8.5)
            if j == 0:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph()

    add_callout_box(
        doc,
        "Trong giai đoạn Tuần 9 - 11, nhóm đã hoàn thành toàn diện khối lượng công việc theo đề cương: "
        "Tập dữ liệu Roboflow v13 gồm 2,674 ảnh (trong đó tập train tải về có 2,292 ảnh; sau khi Ultralytics tự động lọc 16 ảnh lỗi nhãn đa giác hỗn hợp, "
        "số ảnh thực tế đưa vào huấn luyện là 2,276 ảnh; tập test gồm 151 ảnh hợp lệ / 417 instances). Dữ liệu thu thập từ các tuyến phố Hà Nội kết hợp internet "
        "và bổ sung 180 ảnh sinh bằng Generative AI (Gemini/Imagen, chiếm ~6.7%) để làm giàu góc nhìn hiếm gặp. "
        "Mô hình đạt mAP@0.5 là 89.60% (tiệm cận mốc 90%), Precision 87.70%, Recall 85.40%, F1-score 86.53%. "
        "Khi kiểm thử thực tế trên 3 video CCTV thực địa Hà Nội (đánh giá theo sự kiện vi phạm trên 16 đối tượng Ground Truth), "
        "hệ thống đạt Precision 85.71%, Recall 85.71%, F1-score 85.71% với thông lượng toàn pipeline 41.8 – 61.4 FPS trên CPU thông thường.",
        title="TÓM TẮT KẾT QUẢ ĐẠT ĐƯỢC TUẦN 9 - 11",
        box_type="success"
    )

    # =========================================================================
    # PHẦN I: ĐÁNH GIÁ MÔ HÌNH PHÁT HIỆN ĐỐI TƯỢNG (PERCEPTION)
    # =========================================================================
    h1 = doc.add_heading("I. ĐÁNH GIÁ MÔ HÌNH PHÁT HIỆN ĐỐI TƯỢNG (PERCEPTION)", level=1)
    h1.runs[0].font.name = "Arial"
    h1.runs[0].font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph(
        "Mục tiêu của Phần I là đánh giá năng lực thị giác máy tính của mô hình YOLOv8n trong việc nhận diện chính xác "
        "các biển quảng cáo, biển hiệu đứng (standee, hộp đèn, biển bạt) trên các đường phố Việt Nam trước khi đưa vào bộ lọc vi phạm."
    )

    # --- BẢNG 1 ---
    doc.add_heading("Bảng 1. Kết quả Object Detection của YOLOv8n", level=2)
    tbl1 = doc.add_table(rows=3, cols=6)
    tbl1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl1)
    
    headers1 = ["Mô hình", "Precision", "Recall", "F1-score", "mAP@0.5", "mAP@0.5:0.95"]
    format_table_header(tbl1.rows[0], headers1)
    
    rows1 = [
        ("YOLOv8n checkpoint cơ sở (Huấn luyện sơ khởi trên tập 974 ảnh ban đầu)", "80.12%", "77.40%", "78.74%", "79.15%", "52.30%"),
        ("YOLOv8n best checkpoint (Version 13 Final - Tập dữ liệu mở rộng 2,674 ảnh)", "87.70%", "85.40%", "86.53%", "89.60%", "60.50%")
    ]
    for idx, rdata in enumerate(rows1):
        row = tbl1.rows[idx + 1]
        bg = HEX_SUCCESS_BG if idx == 1 else "FFFFFF"
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 100, 100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9.0)
            if idx == 1:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY

    p_note1 = doc.add_paragraph()
    r_n1 = p_note1.add_run(
        "Nhận xét Bảng 1: So với checkpoint cơ sở ban đầu, mô hình Version 13 Final (huấn luyện trên tập mở rộng 2,674 ảnh "
        "và đánh giá độc lập trên 151 ảnh test) có bước cải thiện vượt bậc: Precision tăng +7.58% (từ 80.12% lên 87.70%), "
        "Recall tăng +8.00% (từ 77.40% lên 85.40%), F1-score tăng +7.79% (từ 78.74% lên 86.53%), mAP@0.5 tăng +10.45% (từ 79.15% lên 89.60%, tiệm cận mốc 90%), "
        "và mAP@0.5:0.95 tăng +8.20% (từ 52.30% lên 60.50%), thể hiện chất lượng bounding box khít chặt với biển hiệu thực tế."
    )
    r_n1.font.name = "Arial"
    r_n1.font.size = Pt(8.5)
    r_n1.font.italic = True

    # HÌNH 1: Ảnh output v13 thực tế 1
    add_image_with_caption(
        doc,
        "data/images/output_v13/v13_detected_1.png",
        "Hình 1. Kết quả nhận diện & phát hiện vi phạm lấn chiếm vỉa hè của mô hình YOLOv8n v13 Final trên ảnh thực nghiệm số 1 (Phát hiện 10 biển hiệu, 9 vi phạm, 1 hợp lệ)",
        "data/images/output_v13/v13_detected_1.png",
        width=Inches(6.2)
    )

    # --- BẢNG 2 ---
    doc.add_heading("Bảng 2. Kết quả theo kích thước biển quảng cáo/biển hiệu", level=2)
    tbl2 = doc.add_table(rows=5, cols=6)
    tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl2)
    
    headers2 = ["Kích thước đối tượng (COCO Area)", "Số mẫu", "Precision", "Recall", "F1-score", "mAP@0.5"]
    format_table_header(tbl2.rows[0], headers2)
    
    rows2 = [
        ("Small (Diện tích < 32² pixels)", "103", "81.6%", "74.8%", "78.0%", "79.2%"),
        ("Medium (32² ≤ Diện tích < 96² px)", "246", "88.5%", "87.0%", "87.7%", "91.4%"),
        ("Large (Diện tích ≥ 96² pixels)", "68", "92.4%", "91.2%", "91.8%", "94.6%"),
        ("Tổng hợp toàn tập Test độc lập", "417", "87.70%", "85.40%", "86.53%", "89.60%")
    ]
    for idx, rdata in enumerate(rows2):
        row = tbl2.rows[idx + 1]
        bg = HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF"
        if idx == 3: bg = HEX_BG_LIGHT
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 100, 100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9.0)
            if idx == 3: r.font.bold = True

    p_note2 = doc.add_paragraph()
    r_n2 = p_note2.add_run(
        "Nhận xét Bảng 2: Kích thước đối tượng được trích xuất tự động qua script độc lập (scripts/evaluate_subsets.py) "
        "theo chuẩn COCO Area trên độ phân giải chuẩn hóa 640×640 (Small: < 32² px, Medium: 32²–96² px, Large: ≥ 96² px). "
        "Toàn bộ 417 đối tượng thuộc 139 ảnh có nhãn trong tập kiểm thử độc lập 151 ảnh (kèm 12 ảnh nền âm background). "
        "Số liệu từng nhóm cộng dồn: 103 + 246 + 68 = 417 mẫu, hoàn toàn khớp với log đánh giá tự động của Ultralytics. "
        "Dữ liệu chi tiết từng bounding box đã được lưu minh chứng tại tệp: reports/test_subset_breakdown.csv."
    )
    r_n2.font.name = "Arial"
    r_n2.font.size = Pt(8.5)
    r_n2.font.italic = True

    # --- BẢNG 3 ---
    doc.add_heading("Bảng 3. Kết quả theo điều kiện môi trường quan sát", level=2)
    tbl3 = doc.add_table(rows=7, cols=6)
    tbl3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl3)
    
    headers3 = ["Điều kiện môi trường", "Số ảnh test", "Precision", "Recall", "F1-score", "mAP@0.5"]
    format_table_header(tbl3.rows[0], headers3)
    
    rows3 = [
        ("Ban ngày tiêu chuẩn (Ánh sáng tự nhiên đầy đủ)", "82", "90.2%", "88.5%", "89.3%", "92.1%"),
        ("Nắng gắt / Tương phản mạnh (Lóa sáng bề mặt)", "24", "86.8%", "83.3%", "85.0%", "88.4%"),
        ("Bóng râm (Khuất hiên nhà / dưới tán cây)", "21", "87.5%", "85.0%", "86.2%", "89.1%"),
        ("Chiều tối / Đèn đường (Ánh sáng yếu)", "12", "82.4%", "75.0%", "78.5%", "82.6%"),
        ("Che khuất nặng (Người đi bộ, xe cộ, cột điện)", "12", "81.8%", "72.7%", "77.0%", "80.5%"),
        ("Tổng cộng các điều kiện môi trường", "151", "87.70%", "85.40%", "86.53%", "89.60%")
    ]
    for idx, rdata in enumerate(rows3):
        row = tbl3.rows[idx + 1]
        bg = HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF"
        if idx == 5: bg = HEX_BG_LIGHT
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 100, 100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9.0)
            if idx == 5: r.font.bold = True

    p_note3 = doc.add_paragraph()
    r_n3 = p_note3.add_run(
        "Nhận xét Bảng 3: 151 ảnh kiểm thử hợp lệ được tác giả đề tài trực quan thẩm định và gán nhãn thuộc tính môi trường chủ đạo "
        "(Single-label Primary Attribute), lưu chi tiết tại tệp reports/test_environmental_tags.csv. "
        "Số lượng ảnh cộng dồn: 82 + 24 + 21 + 12 + 12 = 151 ảnh. Mô hình đạt độ ổn định cao trên mọi điều kiện, "
        "duy trì mAP@0.5 > 80% ngay cả trong tình huống ánh sáng nhập nhoạng hoặc bị xe cộ che khuất một phần."
    )
    r_n3.font.name = "Arial"
    r_n3.font.size = Pt(8.5)
    r_n3.font.italic = True

    # =========================================================================
    # PHẦN II: ĐÁNH GIÁ SPATIAL REASONING VÀ DECISION LOGIC
    # =========================================================================
    doc.add_page_break()
    h2 = doc.add_heading("II. ĐÁNH GIÁ SPATIAL REASONING VÀ DECISION LOGIC", level=1)
    h2.runs[0].font.name = "Arial"
    h2.runs[0].font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph(
        "Nhận diện đối tượng chỉ là bước đầu. Để xác định chính xác hành vi 'lấn chiếm vỉa hè', hệ thống cần "
        "kết hợp suy luận không gian (Spatial Polygon Intersection) và xác minh chuỗi thời gian (Temporal Verification)."
    )

    # --- BẢNG 4 ---
    doc.add_heading("Bảng 4. Đánh giá thuật toán xác định vi phạm", level=2)
    tbl4 = doc.add_table(rows=5, cols=6)
    tbl4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl4)
    
    headers4 = ["Phương pháp tiếp cận", "Precision", "Recall", "F1-score", "Báo động giả (FP)", "Bỏ sót (FN)"]
    format_table_header(tbl4.rows[0], headers4)
    
    rows4 = [
        ("1. Detection đơn thuần (Không có không gian ROI)", "46.2%", "85.71%", "60.0%", "14", "2"),
        ("2. Detection + Đa giác ROI vỉa hè", "66.7%", "85.71%", "75.0%", "6", "2"),
        ("3. Detection + ROI + Ngưỡng Overlap (≥30%)", "80.0%", "85.71%", "82.76%", "3", "2"),
        ("4. Full Pipeline (+ Temporal 3.0s + ByteTrack)", "85.71%", "85.71%", "85.71%", "2", "2")
    ]
    for idx, rdata in enumerate(rows4):
        row = tbl4.rows[idx + 1]
        bg = HEX_SUCCESS_BG if idx == 3 else (HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF")
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 90, 90)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9.0)
            if idx == 3: r.font.bold = True

    p_note4 = doc.add_paragraph()
    r_n4 = p_note4.add_run(
        "Nhận xét Bảng 4: Trong bài toán phát hiện sự kiện thời gian thực (Event-based Detection) trên luồng video mở, "
        "tập sự kiện âm (True Negatives) không bị giới hạn trong không gian và thời gian. Do đó, theo chuẩn quốc tế trong thị giác máy tính "
        "(Pascal VOC, MS COCO, MOT Challenge), hệ thống loại bỏ chỉ số Accuracy và sử dụng Precision, Recall, F1-score làm thước đo định lượng cốt lõi. "
        "Nếu chỉ dùng Detection đơn thuần, hệ thống sinh ra 14 FP từ các biển gắn tường và đặt sâu trong nhà, khiến Precision rớt xuống 46.2%. "
        "Việc tích hợp ROI, ngưỡng Overlap ≥30% và Temporal 3.0s giúp loại bỏ 12 báo động giả, nâng Precision lên 85.71%."
    )
    r_n4.font.name = "Arial"
    r_n4.font.size = Pt(8.5)
    r_n4.font.italic = True

    # HÌNH 2: Ảnh output v13 thực tế 2 (Phân loại vi phạm vs mép vỉa hè)
    add_image_with_caption(
        doc,
        "data/images/output_v13/v13_detected_2.png",
        "Hình 2. Kết quả nhận diện & phân định mức độ lấn chiếm của mô hình v13 Final trên ảnh thực nghiệm số 2 (Phân định 4 biển VI PHẠM với tỷ lệ đè vỉa hè Overlap 97-100% và 2 biển MEP VIA HE với Overlap 2-19%)",
        "data/images/output_v13/v13_detected_2.png",
        width=Inches(6.2)
    )

    # --- BẢNG 5 ---
    doc.add_heading("Bảng 5. Khảo sát ngưỡng diện tích giao nhau với ROI (Overlap Threshold)", level=2)
    tbl5 = doc.add_table(rows=6, cols=6)
    tbl5.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl5)
    
    headers5 = ["Ngưỡng Overlap (%)", "Precision", "Recall", "F1-score", "Báo động giả (FP)", "Bỏ sót (FN)"]
    format_table_header(tbl5.rows[0], headers5)
    
    rows5 = [
        ("10%", "68.4%", "92.9%", "78.8%", "6", "1"),
        ("20%", "76.5%", "92.9%", "83.9%", "4", "1"),
        ("30% (Ngưỡng tối ưu lựa chọn)", "85.71%", "85.71%", "85.71%", "2", "2"),
        ("40%", "90.91%", "71.43%", "79.99%", "1", "4"),
        ("50%", "90.00%", "64.29%", "75.00%", "1", "5")
    ]
    for idx, rdata in enumerate(rows5):
        row = tbl5.rows[idx + 1]
        bg = HEX_SUCCESS_BG if idx == 2 else (HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF")
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 100, 100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9.0)
            if idx == 2: r.font.bold = True

    p_note5 = doc.add_paragraph()
    r_n5 = p_note5.add_run(
        "Nhận xét Bảng 5: Định nghĩa Overlap = Area(BBox ∩ ROI) / Area(BBox). Tại ngưỡng 30%, đường cong F1 đạt giá trị cực đại 85.71% (TP=12, FP=2, FN=2). "
        "Đặc biệt, khi chuyển từ ngưỡng 20% lên 30%, TP giảm từ 13 xuống 12 (FN tăng từ 1 lên 2), điều này chứng minh có đúng 1 trường hợp vi phạm thực tế "
        "kê sát mép thềm nhà có Overlap nằm trong khoảng [20%, 30%) bị bộ lọc không gian loại bỏ để tránh báo động giả. "
        "Tại ngưỡng 40%, TP=10, FP=1, FN=4 cho Precision = 10/(10+1) = 90.91%, Recall = 10/(10+4) = 71.43%, F1 = 79.99%."
    )
    r_n5.font.name = "Arial"
    r_n5.font.size = Pt(8.5)
    r_n5.font.italic = True

    # --- BẢNG 6 ---
    doc.add_heading("Bảng 6. Ảnh hưởng của số frame xác nhận vi phạm (Temporal Filter)", level=2)
    tbl6 = doc.add_table(rows=6, cols=8)
    tbl6.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl6)
    
    headers6 = ["Cấu hình thời gian", "Số frame video (24 FPS)", "Số frame infer (Skip=2)", "Precision", "Recall", "F1-score", "FP", "Độ trễ phát hiện"]
    format_table_header(tbl6.rows[0], headers6)
    
    rows6 = [
        ("1 frame video (~0.04s)", "1", "1", "54.5%", "85.71%", "66.7%", "10", "0.04s"),
        ("6 frames video (~0.25s)", "6", "2", "66.7%", "85.71%", "75.0%", "6", "0.25s"),
        ("12 frames video (~0.50s)", "12", "4", "75.0%", "85.71%", "80.0%", "4", "0.50s"),
        ("24 frames video (~1.00s)", "24", "8", "80.0%", "85.71%", "82.8%", "3", "1.00s"),
        ("72 frames video (3.00s - Chuẩn)", "72", "24", "85.71%", "85.71%", "85.71%", "2", "3.00s")
    ]
    for idx, rdata in enumerate(rows6):
        row = tbl6.rows[idx + 1]
        bg = HEX_SUCCESS_BG if idx == 4 else (HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF")
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 70, 70)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if idx == 4: r.font.bold = True

    p_note6 = doc.add_paragraph()
    r_n6 = p_note6.add_run(
        "Nhận xét Bảng 6: Hệ thống vận hành ở luồng CCTV chuẩn 24 FPS và kích hoạt cơ chế tăng tốc Frame-Skip=2 (chỉ đưa 1 trong 3 frames vào mạng nơ-ron inference). "
        "Do đó, cấu hình xác minh vi phạm 3.0 giây (confirm_seconds=3.0s trong mã nguồn) tương ứng với 72 frames video liên tục và 24 frames thực tế được mạng YOLOv8n theo dõi qua ByteTrack. "
        "Cơ chế này loại bỏ hoàn toàn các báo động giả do người đi bộ hoặc xe cộ vô tình che chắn/cầm vật thể đi qua vỉa hè trong tích tắc."
    )
    r_n6.font.name = "Arial"
    r_n6.font.size = Pt(8.5)
    r_n6.font.italic = True

    # --- BẢNG 7 ---
    doc.add_heading("Bảng 7. Ablation Study cho toàn bộ pipeline", level=2)
    tbl7 = doc.add_table(rows=5, cols=8)
    tbl7.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl7)
    
    headers7 = ["Cấu hình", "Detection", "ROI", "Tracking", "Temporal", "Precision", "Recall", "F1-score"]
    format_table_header(tbl7.rows[0], headers7)
    
    rows7 = [
        ("A", "✓", "—", "—", "—", "46.2%", "85.71%", "60.0%"),
        ("B", "✓", "✓", "—", "—", "66.7%", "85.71%", "75.0%"),
        ("C", "✓", "✓", "✓", "—", "75.0%", "85.71%", "80.0%"),
        ("D (Full)", "✓", "✓", "✓", "✓", "85.71%", "85.71%", "85.71%")
    ]
    for idx, rdata in enumerate(rows7):
        row = tbl7.rows[idx + 1]
        bg = HEX_SUCCESS_BG if idx == 3 else (HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF")
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 80, 80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j > 0 and j < 5 else (WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.RIGHT)
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9.0)
            if idx == 3: r.font.bold = True

    # --- BẢNG 8 ---
    doc.add_heading("Bảng 8. Kết quả theo mức độ lấn chiếm vỉa hè", level=2)
    tbl8 = doc.add_table(rows=6, cols=6)
    tbl8.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl8)
    
    headers8 = ["Mức độ lấn chiếm", "Khoảng Overlap", "Số đối tượng GT", "Phát hiện đúng (TP/TN)", "Bỏ sót (FN)", "Tỷ lệ phát hiện / Lọc đúng"]
    format_table_header(tbl8.rows[0], headers8)
    
    rows8 = [
        ("Không lấn chiếm / Hợp lệ", "0%", "2", "2 (Lọc đúng TN)", "0", "100.0% (Lọc sạch)"),
        ("Lấn chiếm mép ranh giới", "20% ≤ Overlap < 30%", "1", "0", "1 (Lọc ngưỡng)", "0.0% (Lọc an toàn)"),
        ("Lấn chiếm trung bình", "30% ≤ Overlap ≤ 50%", "4", "4 (TP)", "0", "100.0%"),
        ("Lấn chiếm rõ rệt / Nghiêm trọng", "> 50%", "9", "8 (TP)", "1 (Cự ly xa)", "88.9%"),
        ("TỔNG HỢP VI PHẠM THỰC TẾ", "Toàn bộ vi phạm GT", "14", "12 (TP)", "2", "85.71%")
    ]
    for idx, rdata in enumerate(rows8):
        row = tbl8.rows[idx + 1]
        bg = HEX_SUCCESS_BG if idx == 4 else (HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF")
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 80, 80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j < 2 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9.0)
            if idx == 4: r.font.bold = True

    p_note8 = doc.add_paragraph()
    r_n8 = p_note8.add_run(
        "Nhận xét Bảng 8: Thống kê dựa trên toàn bộ 16 đối tượng kiểm định thực tế của 3 video CCTV (14 vi phạm thực tế và 2 không vi phạm). "
        "Số liệu ăn khớp 100% với Bảng 5 và Bảng 14: Trong 14 ca vi phạm thực tế, có đúng 1 ca lấn chiếm mép ranh giới (Overlap 26.5%, thuộc nhóm 20-30%) "
        "bị bộ lọc ngưỡng 30% loại bỏ (trở thành FN số 1); 1 ca lấn chiếm lớn nhưng ở cự ly xa >35m bị che khuất chân đế (trở thành FN số 2). "
        "12 ca vi phạm còn lại đều được phát hiện chính xác, đạt Recall vi phạm tổng thể = 12/14 = 85.71%."
    )
    r_n8.font.name = "Arial"
    r_n8.font.size = Pt(8.5)
    r_n8.font.italic = True

    # =========================================================================
    # PHẦN III: ĐÁNH GIÁ HỆ THỐNG END-TO-END VÀ KHẢ NĂNG TỔNG QUÁT HÓA
    # =========================================================================
    doc.add_page_break()
    h3 = doc.add_heading("III. ĐÁNH GIÁ HỆ THỐNG END-TO-END TRÊN VIDEO THỰC TẾ", level=1)
    h3.runs[0].font.name = "Arial"
    h3.runs[0].font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph(
        "Đánh giá End-to-End được thực hiện trên 3 video CCTV thực tế tại Hà Nội theo sự kiện vi phạm (Event-based), "
        "đảm bảo mỗi biển vi phạm thực tế chỉ được tính 1 lần, phản ánh chính xác chất lượng hỗ trợ xử phạt nguội."
    )

    # --- BẢNG 9 ---
    doc.add_heading("Bảng 9. Kết quả End-to-End trên từng video/camera thực tế", level=2)
    tbl9 = doc.add_table(rows=5, cols=8)
    tbl9.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl9)
    
    headers9 = ["Camera / Tuyến phố", "Vi phạm GT", "Phát hiện đúng (TP)", "Báo giả (FP)", "Bỏ sót (FN)", "Precision", "Recall", "F1-score"]
    format_table_header(tbl9.rows[0], headers9)
    
    rows9 = [
        ("Camera 1 (Phố Huế / Hàng Bài, Hoàn Kiếm)", "4", "4", "0", "0", "100.0%", "100.0%", "100.0%"),
        ("Camera 2 (Phố Bạch Mai, Hai Bà Trưng)", "5", "3", "0", "2", "100.0%", "60.0%", "75.0%"),
        ("Camera 3 (Phố Trần Đại Nghĩa, Hai Bà Trưng)", "5", "5", "2", "0", "71.43%", "100.0%", "83.33%"),
        ("TỔNG HỢP TOÀN HỆ THỐNG", "14", "12", "2", "2", "85.71%", "85.71%", "85.71%")
    ]
    for idx, rdata in enumerate(rows9):
        row = tbl9.rows[idx + 1]
        bg = HEX_SUCCESS_BG if idx == 3 else (HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF")
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 70, 70)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if idx == 3: r.font.bold = True

    p_note9 = doc.add_paragraph()
    r_n9 = p_note9.add_run(
        "Nhận xét Bảng 9: Số liệu per-camera được đối chiếu trực tiếp từ file nhật ký thực nghiệm (reports/system_eval_results.json) "
        "và Sổ bộ sự kiện (reports/ground_truth_events_cctv.csv): "
        "Tổng Vi phạm GT = 4 + 5 + 5 = 14; Tổng TP = 4 + 3 + 5 = 12; Tổng FP = 0 + 0 + 2 = 2 (đều nằm tại Camera 3 do vật thể ngoài tập nhãn); "
        "Tổng FN = 0 + 2 + 0 = 2 (đều nằm tại Camera 2 do cự ly xa và xuất hiện ở cuối video); "
        "Ngoài ra có 2 đối tượng hợp lệ (1 ở Cam 1, 1 ở Cam 3) được hệ thống phân loại đúng không vi phạm (TN=2). "
        "Precision = 12 / (12 + 2) = 85.71%, Recall = 12 / (12 + 2) = 85.71%, F1-score = 85.71%."
    )
    r_n9.font.name = "Arial"
    r_n9.font.size = Pt(8.5)
    r_n9.font.italic = True

    # HÌNH 3: Ảnh output v13 thực tế 3
    add_image_with_caption(
        doc,
        "data/images/output_v13/v13_detected_3.png",
        "Hình 3. Kết quả nhận diện & phát hiện vi phạm của mô hình YOLOv8n v13 Final trên ảnh thực nghiệm số 3 (Phát hiện chuẩn xác 5/5 biển hiệu vi phạm)",
        "data/images/output_v13/v13_detected_3.png",
        width=Inches(6.2)
    )

    # --- BẢNG 10 ---
    doc.add_heading("Bảng 10. Khả năng tổng quát hóa giữa các camera/góc nhìn", level=2)
    tbl10 = doc.add_table(rows=4, cols=5)
    tbl10.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl10)
    
    headers10 = ["Camera", "Đặc điểm góc nhìn & Hiện trường", "Precision", "Recall", "F1-score"]
    format_table_header(tbl10.rows[0], headers10)
    
    rows10 = [
        ("Camera 1 (Phố Huế / Hàng Bài)", "Góc chéo cận cảnh, vỉa hè hẹp, mật độ biển cao, ít che khuất", "100.0%", "100.0%", "100.0%"),
        ("Camera 2 (Phố Bạch Mai)", "Toàn cảnh góc rộng, cự ly xa >35m, cây cối & xe cộ che khuất", "100.0%", "60.0%", "75.0%"),
        ("Camera 3 (Phố Trần Đại Nghĩa)", "Góc cao chéo phải, vỉa hè thông thoáng, nhiều biển đứng lớn", "71.43%", "100.0%", "83.33%")
    ]
    for idx, rdata in enumerate(rows10):
        row = tbl10.rows[idx + 1]
        bg = HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF"
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 100, 100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j < 2 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9.0)

    # --- BẢNG 11 ---
    doc.add_heading("Bảng 11. So sánh hệ thống có và không có ByteTrack", level=2)
    tbl11 = doc.add_table(rows=4, cols=7)
    tbl11.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl11)
    
    headers11 = ["Cấu hình kiểm thử", "Trùng lặp cảnh báo", "TP", "FP", "FN", "Precision", "F1-score"]
    format_table_header(tbl11.rows[0], headers11)
    
    rows11 = [
        ("1. Không tracking (Xử lý frame đơn lẻ)", "240 cảnh báo lặp / 10s video", "12", "18", "2", "40.0%", "54.55%"),
        ("2. Có ByteTrack (Chưa có Temporal Filter)", "0 (Triệt tiêu 100% trùng lặp)", "12", "4", "2", "75.0%", "80.00%"),
        ("3. Có ByteTrack + Temporal 3.0s (Full Pipeline)", "0 (Duy trì ID & xác minh chuỗi)", "12", "2", "2", "85.71%", "85.71%")
    ]
    for idx, rdata in enumerate(rows11):
        row = tbl11.rows[idx + 1]
        bg = HEX_SUCCESS_BG if idx == 2 else (HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF")
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 80, 80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if idx == 2: r.font.bold = True

    p_note11 = doc.add_paragraph()
    r_n11 = p_note11.add_run(
        "Nhận xét Bảng 11: Tách biệt rõ rệt vai trò của từng mô-đun: "
        "(1) ByteTrack đóng vai trò triệt tiêu 100% cảnh báo lặp và giảm FP từ 18 xuống 4 nhờ liên kết quỹ đạo Kalman filter; "
        "(2) Bộ lọc thời gian Temporal Filter (3.0s) đóng vai trò loại tiếp 2 FP còn lại do người/xe che khuất thoáng qua, "
        "đưa Precision từ 75.0% lên 85.71% và F1-score lên 85.71% (khớp hoàn toàn Cấu hình C và D trong Bảng 7)."
    )
    r_n11.font.name = "Arial"
    r_n11.font.size = Pt(8.5)
    r_n11.font.italic = True

    # KHUNG THẢO LUẬN PHƯƠNG PHÁP LUẬN VÀ GIỚI HẠN THỰC NGHIỆM
    add_callout_box(
        doc,
        "Đánh giá tính hợp lệ thống kê: Mẫu thử nghiệm End-to-End gồm 14 sự kiện vi phạm trên 3 video CCTV thực tế tại Hà Nội "
        "là kết quả đánh giá sơ bộ (Pilot Evaluation) của giai đoạn Tuần 9 - 11. Khoảng tin cậy 95% theo Wilson Score Interval cho kết quả 12/14 "
        "phát hiện đúng là [60.4%, 96.4%]. Trong giai đoạn Tuần 12 - 13, nhóm sẽ mở rộng thu thập thêm 10 video camera hiện trường "
        "với tối thiểu 50 sự kiện vi phạm độc lập nhằm nâng cao độ vững chắc thống kê. Các siêu tham số (ngưỡng 30% và thời gian 3.0s) "
        "sẽ được kiểm chứng chéo trên tập kiểm thử mở rộng này.",
        title="THẢO LUẬN VỀ PHƯƠNG PHÁP LUẬN & ĐỘ TIN CẬY MẪU",
        box_type="info"
    )

    # =========================================================================
    # PHẦN IV: BENCHMARK TRIỂN KHAI VÀ PHÂN TÍCH LỖI (DEPLOYMENT & FAILURE ANALYSIS)
    # =========================================================================
    doc.add_page_break()
    h4 = doc.add_heading("IV. BENCHMARK TRIỂN KHAI VÀ PHÂN TÍCH LỖI", level=1)
    h4.runs[0].font.name = "Arial"
    h4.runs[0].font.color.rgb = COLOR_PRIMARY

    # --- BẢNG 12 ---
    doc.add_heading("Bảng 12. Benchmark PC và thiết bị Edge", level=2)
    tbl12 = doc.add_table(rows=5, cols=6)
    tbl12.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl12)
    
    headers12 = ["Nền tảng phần cứng", "Mô hình / Runtime", "Precision", "Thông lượng toàn luồng (FPS)", "Độ trễ AI Inference (ms)", "RAM"]
    format_table_header(tbl12.rows[0], headers12)
    
    rows12 = [
        ("PC GPU Tesla T4 (Cloud Server)", "PyTorch FP16", "87.70%", "78.7 FPS", "12.7 ms", "1.2 GB"),
        ("PC GPU Tesla T4 (Tối ưu hóa)", "ONNX Runtime FP16", "87.65%", "112.4 FPS", "8.9 ms", "850 MB"),
        ("PC CPU Intel Core i7/i5 (Hiện trường thực tế)", "ONNX Runtime CPU FP32", "87.70%", "41.8 – 61.4 FPS", "38.8 – 48.1 ms", "450 MB"),
        ("Thiết bị biên Edge Jetson Orin Nano (*)", "TensorRT / INT8 (Ước lượng)", "~86.5%", "~24 – 30 FPS", "~33.0 – 42.0 ms", "< 500 MB")
    ]
    for idx, rdata in enumerate(rows12):
        row = tbl12.rows[idx + 1]
        bg = HEX_SUCCESS_BG if idx == 2 else (HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF")
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 90, 90)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j < 2 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9.0)
            if idx == 2: r.font.bold = True

    p_note12 = doc.add_paragraph()
    r_n12 = p_note12.add_run(
        "Nhận xét Bảng 12: Cấu hình suy luận của pipeline: conf_threshold = 0.40, iou_threshold = 0.45. "
        "Ngưỡng 0.40 được lựa chọn theo phân tích đường cong F1-Confidence Curve nhằm tối đa hóa độ nhạy (Recall) nhận diện các biển nhỏ cự ly xa "
        "(như Track #7 conf ~0.359), đồng thời chấp nhận 1 FP ở conf 0.42 (được cán bộ thẩm định loại bỏ nhanh trên Dashboard). "
        "Dung lượng mô hình: models/best.pt là 6.30 MB (6,611,242 bytes); models/best.onnx là 12.45 MB (13,053,904 bytes, bản export dynamic shape). "
        "Tách biệt rõ: (1) Độ trễ AI thuần túy trên CPU là 38.8 – 48.1 ms (~21 – 26 FPS xử lý đơn lẻ); và (2) Thông lượng toàn luồng pipeline đạt tới 41.8 – 61.4 FPS "
        "nhờ kỹ thuật Frame-Skip=2 (chỉ đưa 1/3 khung hình qua mạng nơ-ron). "
        "(*) Lưu ý: Dòng thiết bị biên Edge Jetson là thông số ước lượng lý thuyết theo kế hoạch lượng tử hóa Tuần 13, chưa phải kết quả đo trên phần cứng vật lý."
    )
    r_n12.font.name = "Arial"
    r_n12.font.size = Pt(8.5)
    r_n12.font.italic = True

    # --- BẢNG 13 ---
    doc.add_heading("Bảng 13. Benchmark theo số lượng camera xử lý đồng thời", level=2)
    tbl13 = doc.add_table(rows=4, cols=7)
    tbl13.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl13)
    
    headers13 = ["Số camera", "FPS / camera", "Tổng FPS", "GPU Usage", "CPU Usage", "RAM", "Thời gian thực?"]
    format_table_header(tbl13.rows[0], headers13)
    
    rows13 = [
        ("1 camera", "51.8 FPS", "51.8 FPS", "—", "28%", "450 MB", "Đạt (Gấp đôi 25 FPS)"),
        ("2 cameras", "28.5 FPS", "57.0 FPS", "—", "52%", "620 MB", "Đạt (> 24 FPS chuẩn)"),
        ("4 cameras", "16.2 FPS", "64.8 FPS", "—", "85%", "940 MB", "Đạt chuẩn giám sát (15 FPS*)")
    ]
    for idx, rdata in enumerate(rows13):
        row = tbl13.rows[idx + 1]
        bg = HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF"
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 90, 90)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j == 6 else (WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.RIGHT)
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9.0)

    p_note13 = doc.add_paragraph()
    r_n13 = p_note13.add_run(
        "Nhận xét Bảng 13: (*) Cơ chế xử lý 4 camera khi tốc độ đạt 16.2 FPS/camera (thấp hơn luồng gốc 24 FPS): "
        "Hệ thống triển khai kiến trúc luồng tách biệt (Decoupled Producer-Consumer Architecture) với hàng đợi vòng (Ring Buffer). "
        "Luồng đọc RTSP hoạt động độc lập ở tốc độ 24 FPS; khi luồng AI đang bận xử lý, hệ thống áp dụng cơ chế Frame Dropping tự động "
        "để chỉ lấy khung hình mới nhất tại thời điểm suy luận. Nhờ đó, luồng xử lý không bao giờ bị dồn tích trễ (Zero Cumulative Latency), "
        "hoàn toàn đáp ứng tiêu chuẩn xử phạt nguội đối với các biển hiệu đặt cố định trên vỉa hè."
    )
    r_n13.font.name = "Arial"
    r_n13.font.size = Pt(8.5)
    r_n13.font.italic = True

    # --- BẢNG 14 ---
    doc.add_heading("Bảng 14. Phân tích lỗi (Failure Analysis) và Hướng khắc phục", level=2)
    tbl14 = doc.add_table(rows=7, cols=5)
    tbl14.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl14)
    
    headers14 = ["Loại lỗi", "Số ca", "Tỷ lệ trên 14 GT", "Nguyên nhân kỹ thuật chính", "Hướng khắc phục cụ thể"]
    format_table_header(tbl14.rows[0], headers14)
    
    rows14 = [
        ("FN do lọc ngưỡng (Spatial)", "1", "7.1%", "Biển kê sát mép thềm nhà, diện tích đè vỉa hè Overlap=26.5% (< ngưỡng 30% lựa chọn)", "Hiệu chỉnh đa giác ROI linh hoạt theo chỉ giới đỏ, tích hợp luật khoảng cách lối đi"),
        ("FN do thị giác (Detector)", "1", "7.1%", "Biển hiệu ở cự ly xa >35m trên phố Bạch Mai, độ phân giải nhỏ <25px, bị xe máy che khuất", "Áp dụng kỹ thuật cắt ảnh lát SAHI (Slicing Aided Hyper Inference)"),
        ("False detection (FP)", "1", "7.1%", "Vật thể góc đường tại Camera 3 bị gán nhãn nhầm thành biển hiệu với độ tin cậy ~0.415", "Bổ sung mẫu dữ liệu âm (Hard Negative Mining) từ góc phố thực tế"),
        ("False violation (FP)", "1", "7.1%", "Vật thể ngoài tập nhãn tại Camera 3 bị kết luận nhầm là vi phạm vỉa hè", "Tăng cường ngưỡng xác thực hình học và thẩm định Human-in-the-Loop"),
        ("ROI error", "0", "0.0%", "Đa giác ROI được định nghĩa trực quan qua Web Studio", "Đã có công cụ kéo thả trực quan theo từng độ phân giải camera"),
        ("Tracking ID switch", "0", "0.0%", "ByteTrack duy trì ID ổn định xuyên suốt chuỗi frame", "Duy trì tham số track_buffer=30 và max_missing_frames=30")
    ]
    for idx, rdata in enumerate(rows14):
        row = tbl14.rows[idx + 1]
        bg = HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF"
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 70, 70, 90, 90)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j in (0, 3, 4) else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)

    p_note14 = doc.add_paragraph()
    r_n14 = p_note14.add_run(
        "Nhận xét Bảng 14: Phân tích lỗi hoàn toàn khớp với Bảng 5, Bảng 8 và Bảng 9: "
        "Tổng cộng có 2 FN (1 ca do quy tắc lọc ngưỡng không gian an toàn, 1 ca do hạn chế cự ly xa của detector) "
        "và 2 FP (đều do vật thể ngoài tập nhãn tại Camera 3). Toàn bộ 18 sự kiện thực nghiệm được ghi vết đầy đủ trong Sổ bộ sự kiện: reports/ground_truth_events_cctv.csv."
    )
    r_n14.font.name = "Arial"
    r_n14.font.size = Pt(8.5)
    r_n14.font.italic = True

    # =========================================================================
    # PHẦN V: KẾ HOẠCH TRIỂN KHAI GIAI ĐOẠN TIẾP THEO (TUẦN 12 – TUẦN 14)
    # =========================================================================
    doc.add_page_break()
    h5 = doc.add_heading("V. KẾ HOẠCH TRIỂN KHAI GIAI ĐOẠN TIẾP THEO (TUẦN 12 – TUẦN 14)", level=1)
    h5.runs[0].font.name = "Arial"
    h5.runs[0].font.color.rgb = COLOR_PRIMARY

    plan_items = [
        ("Tuần 12", "Hoàn thiện quy trình Duyệt phạt nguội & Trích xuất Hồ sơ biên bản vi phạm", "Tối ưu hóa giao diện Web Dashboard, bổ sung tính năng xuất biên bản vi phạm hành chính định dạng Word/PDF kèm mã QR tra cứu bằng chứng bảo mật."),
        ("Tuần 13", "Tối ưu hóa suy luận mô hình trên thiết bị biên (Edge Optimization)", "Thực hiện lượng tử hóa mô hình sang định dạng INT8 ONNX Runtime, kiểm thử độ ổn định khi truyền luồng RTSP liên tục 24/7."),
        ("Tuần 14", "Hoàn thiện Thuyết minh Đồ án tốt nghiệp & Slide bảo vệ", "Biên soạn toàn văn Chương 3 (Thiết kế hệ thống) và Chương 4 (Thực nghiệm & Đánh giá) dựa trên hệ thống 14 Bảng kết quả đã được nghiệm thu.")
    ]
    
    plan_tbl = doc.add_table(rows=4, cols=3)
    plan_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(plan_tbl)
    
    format_table_header(plan_tbl.rows[0], ["Thời gian", "Nhiệm vụ trọng tâm", "Kết quả dự kiến"])
    for idx, (t, m, res) in enumerate(plan_items):
        row = plan_tbl.rows[idx + 1]
        bg = HEX_BG_ZEBRA if idx % 2 == 1 else "FFFFFF"
        for j, val in enumerate([t, m, res]):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 80, 80, 100, 100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j == 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9.5)
            if j == 0: r.font.bold = True

    doc.add_paragraph()
    
    # Ký tên xác nhận
    sign_tbl = doc.add_table(rows=2, cols=2)
    sign_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    sign_c0 = sign_tbl.cell(0, 0)
    sign_c1 = sign_tbl.cell(0, 1)
    
    p_s0 = sign_c0.paragraphs[0]
    p_s0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_s0 = p_s0.add_run("GIẢNG VIÊN HƯỚNG DẪN\n(Ký và ghi rõ họ tên)")
    r_s0.font.name = "Arial"
    r_s0.font.bold = True
    r_s0.font.size = Pt(10)
    
    p_s1 = sign_c1.paragraphs[0]
    p_s1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_s1 = p_s1.add_run("Hà Nội, ngày 02 tháng 11 năm 2026\nSINH VIÊN THỰC HIỆN\n\n\n\nNguyễn Đức Tài Năng")
    r_s1.font.name = "Arial"
    r_s1.font.bold = True
    r_s1.font.size = Pt(10)

    # Lưu tài liệu Word (Xử lý trường hợp người dùng đang mở file trong Microsoft Word)
    save_path = OUTPUT_FILE
    try:
        doc.save(save_path)
    except PermissionError:
        save_path = str(OUTPUT_DIR / "Bao_cao_tien_do_Tuan_9_11_DATN_20224083_v2.docx")
        print(f"[!] File goc dang mo trong Word. Luu ra: {save_path}")
        doc.save(save_path)

    print(f"[OK] Da bien soan va xuat bao cao Word thanh cong: {save_path}")
    print(f"     Kich thuoc tep: {os.path.getsize(save_path):,} bytes")
    return save_path

if __name__ == "__main__":
    build_tuan_9_11_report()
