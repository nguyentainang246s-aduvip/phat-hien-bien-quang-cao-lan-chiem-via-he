"""
Script xuất bản bài học Ngày 08 thành file Word (.docx) chuyên nghiệp
Lưu trữ vào thư mục: roadmap AI/Ngay_08_Dinh_Dang_Nhan_YOLO_Toa_Do_Chuan_Hoa.docx
Dành cho: Track A - AI & Dữ liệu (DATN20224083)
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
OUTPUT_DIR = ROOT_DIR / "roadmap AI"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = str(OUTPUT_DIR / "Ngay_08_Dinh_Dang_Nhan_YOLO_Toa_Do_Chuan_Hoa.docx")

# Màu sắc thương hiệu học thuật
COLOR_PRIMARY = RGBColor(30, 58, 138)     # Navy #1E3A8A
COLOR_SECONDARY = RGBColor(15, 118, 110)  # Teal #0F766E
COLOR_DARK = RGBColor(30, 41, 59)         # Slate Dark #1E293B
COLOR_MUTED = RGBColor(100, 116, 139)     # Slate Gray #64748B
COLOR_RED = RGBColor(220, 38, 38)         # Red #DC2626
COLOR_GREEN = RGBColor(16, 185, 129)      # Emerald Green #10B981

HEX_PRIMARY = "1E3A8A"
HEX_SECONDARY = "0F766E"
HEX_HEADER_BG = "1E3A8A"
HEX_BG_LIGHT = "F8FAFC"
HEX_BG_CODE = "F1F5F9"
HEX_BORDER = "CBD5E1"
HEX_CALLOUT_BG = "EFF6FF"
HEX_CALLOUT_BORDER = "3B82F6"
HEX_WARNING_BG = "FEF2F2"
HEX_WARNING_BORDER = "EF4444"
HEX_SUCCESS_BG = "ECFDF5"
HEX_SUCCESS_BORDER = "10B981"


def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
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


def add_callout_box(doc, text, title="LƯU Ý QUAN TRỌNG", box_type="info"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    
    if box_type == "warning":
        bg_color, border_color = HEX_WARNING_BG, HEX_WARNING_BORDER
        title_color = COLOR_RED
    elif box_type == "success":
        bg_color, border_color = HEX_SUCCESS_BG, HEX_SUCCESS_BORDER
        title_color = COLOR_GREEN
    else:
        bg_color, border_color = HEX_CALLOUT_BG, HEX_CALLOUT_BORDER
        title_color = COLOR_PRIMARY
        
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
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
    p.paragraph_format.space_after = Pt(4)
    run_title = p.add_run(f"📌 {title}\n")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(11)
    run_title.font.bold = True
    run_title.font.color.rgb = title_color
    
    run_text = p.add_run(text)
    run_text.font.name = "Arial"
    run_text.font.size = Pt(10)
    run_text.font.color.rgb = COLOR_DARK
    
    doc.add_paragraph()


def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    
    set_cell_background(cell, HEX_BG_CODE)
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="18" w:space="0" w:color="{HEX_PRIMARY}"/>'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
        f'</w:tcBorders>'
    )
    cell._tc.get_or_add_tcPr().append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = Pt(13)
    
    run = p.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(30, 41, 59)
    
    doc.add_paragraph()


def add_section_header(doc, number_str, title_str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    
    r_num = p.add_run(f"{number_str}. ")
    r_num.font.name = "Arial"
    r_num.font.size = Pt(14)
    r_num.font.bold = True
    r_num.font.color.rgb = COLOR_SECONDARY
    
    r_title = p.add_run(title_str)
    r_title.font.name = "Arial"
    r_title.font.size = Pt(14)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY


def add_subsection_header(doc, title_str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    
    r_title = p.add_run(title_str)
    r_title.font.name = "Arial"
    r_title.font.size = Pt(11.5)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_DARK


def add_body_paragraph(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.15
    
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(10.5)
    r.font.color.rgb = COLOR_DARK
    return p


def build_day08_document():
    doc = Document()
    
    # Lề trang A4
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
        # Header / Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hr = hp.add_run("DATN20224083 | Track A: AI & Dữ Liệu | Lộ trình 35 Ngày")
        hr.font.name = "Arial"
        hr.font.size = Pt(8.5)
        hr.font.color.rgb = COLOR_MUTED
        
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fr = fp.add_run("Tài liệu hướng dẫn học tập nội bộ — Lưu hành phục vụ Đồ án Tốt nghiệp Kỹ sư CNTT")
        fr.font.name = "Arial"
        fr.font.size = Pt(8.5)
        fr.font.italic = True
        fr.font.color.rgb = COLOR_MUTED

    # Header tiêu đề
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_top.paragraph_format.space_after = Pt(2)
    
    r_uni = p_top.add_run("ĐẠI HỌC BÁCH KHOA HÀ NỘI — TRƯỜNG CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG\n")
    r_uni.font.name = "Arial"
    r_uni.font.size = Pt(10)
    r_uni.font.bold = True
    r_uni.font.color.rgb = COLOR_MUTED
    
    r_datn = p_top.add_run("ĐỒ ÁN TỐT NGHIỆP: HỆ THỐNG PHÁT HIỆN BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV CỐ ĐỊNH\n")
    r_datn.font.name = "Arial"
    r_datn.font.size = Pt(11)
    r_datn.font.bold = True
    r_datn.font.color.rgb = COLOR_SECONDARY
    
    r_track = p_top.add_run("CHƯƠNG TRÌNH KÈM CẶP 1-1: LỘ TRÌNH 35 NGÀY THỰC CHIẾN TỪ CON SỐ 0")
    r_track.font.name = "Arial"
    r_track.font.size = Pt(9.5)
    r_track.font.italic = True
    r_track.font.color.rgb = COLOR_MUTED

    # Phân cách
    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_before = Pt(2)
    p_div.paragraph_format.space_after = Pt(12)
    r_div = p_div.add_run("━" * 55)
    r_div.font.color.rgb = COLOR_PRIMARY

    # Tiêu đề chính bài học
    p_main = doc.add_paragraph()
    p_main.paragraph_format.space_after = Pt(4)
    r_day = p_main.add_run("NGÀY 08: ĐỊNH DẠNG NHÃN YOLO TXT & TỌA ĐỘ CHUẨN HÓA [0, 1]\nCÔNG THỨC CHUYỂN ĐỔI HÌNH HỌC QUA LẠI VỚI ĐIỂM ẢNH PIXEL\n")
    r_day.font.name = "Arial"
    r_day.font.size = Pt(16)
    r_day.font.bold = True
    r_day.font.color.rgb = COLOR_PRIMARY
    
    r_sub = p_main.add_run("Làm chủ 5 con số trong file nhãn YOLO, công thức giải mã Bbox và tính toán cao độ chân đế tiếp đất y2")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_SECONDARY

    # Bảng Metadata
    tbl_meta = doc.add_table(rows=4, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_rows = [
        ("Phân hệ phụ trách:", "Track A — AI & Dữ liệu (Annotation Geometry & Label Formatting)"),
        ("Mã nguồn liên quan:", "datasets/v8/train/labels/, datasets/verify_annotations.py"),
        ("Định dạng dữ liệu:", "YOLO Darknet TXT: class_id x_center y_center width height (Normalized [0, 1])"),
        ("Mục tiêu ngày 08:", "Làm chủ chuyển đổi 2 chiều giữa Pixel [x1, y1, x2, y2] và Tọa độ chuẩn hóa [xc, yc, w, h].")
    ]
    for i, (k, v) in enumerate(meta_rows):
        c0, c1 = tbl_meta.cell(i, 0), tbl_meta.cell(i, 1)
        c0.width, c1.width = Inches(2.2), Inches(4.3)
        set_cell_background(c0, HEX_BG_LIGHT)
        set_cell_background(c1, HEX_BG_LIGHT)
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
        
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.font.name = "Arial"
        r0.font.size = Pt(9.5)
        r0.font.bold = True
        r0.font.color.rgb = COLOR_DARK
        
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.name = "Arial"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = COLOR_DARK
    set_table_borders(tbl_meta, HEX_BORDER)
    doc.add_paragraph()

    # =========================================================================
    # PHẦN 1: ẨN DỤ ĐỜI SỐNG & TRỰC GIÁC
    # =========================================================================
    add_section_header(doc, "I", "ẨN DỤ ĐỜI SỐNG & TRỰC GIÁC (THE INTUITION)")
    
    add_subsection_header(doc, "1. Ẩn dụ in logo lên áo thun cỡ S và cỡ XXL")
    add_body_paragraph(
        doc,
        "Hãy tưởng tượng một kỹ sư lập trình cho cánh tay robot in logo thương hiệu lên áo thun:\n"
        "Xưởng may sản xuất nhiều cỡ áo khác nhau: Chiếc áo cỡ S (ngực rộng 80cm, dài 60cm) và chiếc áo cỡ XXL (ngực rộng 120cm, dài 85cm).\n"
        "• Nếu kỹ sư ra lệnh theo số đo Centimet cố định: 'In logo cách mép trái 20cm và cách cổ áo xuống 15cm'. "
        "Trên chiếc áo cỡ S, logo sẽ nằm đẹp ngay ngực trái. Nhưng khi đặt chiếc áo cỡ XXL vào, logo sẽ bị lệch tít lên sát xương quai xanh!\n"
        "• Nhưng nếu kỹ sư ra lệnh theo TỶ LỆ PHẦN TRĂM CHUẨN HÓA: 'In logo tại đúng 30% bề ngang áo tính từ mép trái, và đúng 25% chiều dọc tính từ cổ áo xuống'. "
        "Dù là áo cỡ S, M, L hay XXL, cánh tay robot đều in chiếc logo vào đúng vị trí ngực trái một cách hoàn hảo!"
    )
    add_body_paragraph(
        doc,
        "Trong thị giác máy tính, camera CCTV gửi về các video với nhiều độ phân giải khác nhau (HD 720p, Full HD 1080p, 2K). "
        "Khi đưa vào mạng nơ-ron để huấn luyện, ảnh lại liên tục bị co giãn (Resize) thành 640x640 hoặc 1280x1280. "
        "Việc chia tọa độ cho chiều rộng W và chiều cao H để đưa về đoạn [0.0, 1.0] giúp vị trí tấm biển quảng cáo bất biến theo tỷ lệ, "
        "không bao giờ bị lệch vị trí khi kích thước khung hình thay đổi."
    )

    # =========================================================================
    # PHẦN 2: MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC
    # =========================================================================
    add_section_header(doc, "II", "MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC")
    
    add_subsection_header(doc, "1. Cấu trúc 5 con số trong định dạng nhãn YOLO TXT")
    add_body_paragraph(
        doc,
        "Mỗi dòng trong file nhãn .txt của YOLO đại diện cho một Bounding Box và có đúng 5 trường thông tin:"
    )
    add_body_paragraph(
        doc,
        "               class_id    x_center    y_center    width    height\n\n"
        "1. class_id: Số nguyên định danh lớp đối tượng (Trong đồ án này luôn là 0 vì chỉ có duy nhất lớp 'bien-quang-cao').\n"
        "2. x_center (xc): Tọa độ tâm hộp theo phương ngang, chuẩn hóa về [0.0, 1.0] (xc = X_tam / W).\n"
        "3. y_center (yc): Tọa độ tâm hộp theo phương dọc, chuẩn hóa về [0.0, 1.0] (yc = Y_tam / H).\n"
        "4. width (w): Chiều rộng của hộp bao quanh, chuẩn hóa về [0.0, 1.0] (w = W_box / W).\n"
        "5. height (h): Chiều cao của hộp bao quanh, chuẩn hóa về [0.0, 1.0] (h = H_box / H)."
    )

    add_subsection_header(doc, "2. Công thức chuyển đổi hình học 2 chiều")
    add_body_paragraph(
        doc,
        "Giả sử bức ảnh có chiều rộng W và chiều cao H (đơn vị pixel):\n\n"
        "• CHIỀU ĐI: Từ tọa độ Pixel [x1, y1, x2, y2] -> Tọa độ chuẩn hóa YOLO [xc, yc, w, h]:\n"
        "               w  = (x2 - x1) / W\n"
        "               h  = (y2 - y1) / H\n"
        "               xc = (x1 + x2) / (2 * W)\n"
        "               yc = (y1 + y2) / (2 * H)\n\n"
        "• CHIỀU VỀ: Từ tọa độ chuẩn hóa YOLO [xc, yc, w, h] -> Tọa độ Pixel [x1, y1, x2, y2]:\n"
        "               x1 = round( (xc - w / 2) * W )\n"
        "               y1 = round( (yc - h / 2) * H )\n"
        "               x2 = round( (xc + w / 2) * W )\n"
        "               y2 = round( (yc + h / 2) * H )\n\n"
        "• ĐIỂM CHÂN ĐẾ TIẾP XÚC MẶT ĐẤT (BÀN GIAO CHO TRACK B):\n"
        "               y_ground = y2 = round( (yc + h / 2) * H )"
    )

    # =========================================================================
    # PHẦN 3: HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN DỰ ÁN
    # =========================================================================
    add_section_header(doc, "III", "HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN DỰ ÁN")
    
    add_subsection_header(doc, "1. Đọc nội dung thực tế từ file nhãn datasets/v8/train/labels/")
    add_body_paragraph(
        doc,
        "Chạy lệnh PowerShell sau để xem cấu trúc thực tế của một file nhãn trong tập dữ liệu của đồ án:"
    )
    code_read_label = (
        ".venv\\Scripts\\activate\n"
        "python -c \"\n"
        "import os\n"
        "p = 'datasets/v8/train/labels'\n"
        "for f in os.listdir(p):\n"
        "    fp = os.path.join(p, f)\n"
        "    if os.path.getsize(fp) > 0:\n"
        "        print(f'File nhan thuc te: {f}')\n"
        "        with open(fp) as file: print(file.read().strip())\n"
        "        break\n"
        "\""
    )
    add_code_block(doc, code_read_label)

    add_subsection_header(doc, "2. Script Python giải mã và kiểm tra tọa độ Bbox")
    add_body_paragraph(
        doc,
        "Đoạn mã mẫu sau mô phỏng chính xác thuật toán chuyển đổi tọa độ từ nhãn YOLO sang pixel để vẽ Bounding Box:"
    )
    code_convert = (
        "def yolo_to_pixel(xc, yc, w, h, img_w, img_h):\n"
        "    x1 = int((xc - w / 2) * img_w)\n"
        "    y1 = int((yc - h / 2) * img_h)\n"
        "    x2 = int((xc + w / 2) * img_w)\n"
        "    y2 = int((yc + h / 2) * img_h)\n"
        "    return x1, y1, x2, y2\n"
        "\n"
        "# Vi du kiem thu:\n"
        "W, H = 1000, 800\n"
        "x1, y1, x2, y2 = yolo_to_pixel(0.50, 0.60, 0.20, 0.40, W, H)\n"
        "print(f'Pixel Box: Top-Left=({x1}, {y1}), Bottom-Right=({x2}, {y2})')\n"
        "print(f'Chan de tiep dat y2: {y2}px')"
    )
    add_code_block(doc, code_convert)

    # =========================================================================
    # PHẦN 4: SẢN PHẨM BÀN GIAO & CÁCH TỰ KIỂM TRA
    # =========================================================================
    add_section_header(doc, "IV", "SẢN PHẨM BÀN GIAO & TIÊU CHÍ TỰ KIỂM TRA")
    
    tbl_eval = doc.add_table(rows=3, cols=3)
    tbl_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
    eval_data = [
        ("STT", "Tiêu chuẩn đánh giá", "Kết quả nghiệm thu của sinh viên"),
        ("01", "Hiểu rõ 5 tham số định dạng YOLO TXT.", "Giải thích được class_id, x_center, y_center, width, height."),
        ("02", "Tính toán chuyển đổi thành thạo 2 chiều.", "Tự tính chính xác tọa độ pixel từ tỷ lệ chuẩn hóa và ngược lại.")
    ]
    for i, row in enumerate(eval_data):
        for j, text in enumerate(row):
            c = tbl_eval.cell(i, j)
            c.width = Inches(0.8) if j == 0 else (Inches(3.2) if j == 1 else Inches(2.5))
            set_cell_margins(c, 70, 70, 90, 90)
            p = c.paragraphs[0]
            r = p.add_run(text)
            r.font.name = "Arial"
            if i == 0:
                set_cell_background(c, HEX_PRIMARY)
                r.font.size = Pt(9.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
            else:
                set_cell_background(c, HEX_BG_LIGHT if i % 2 == 1 else "FFFFFF")
                r.font.size = Pt(9)
                r.font.color.rgb = COLOR_DARK
    set_table_borders(tbl_eval, HEX_BORDER)
    doc.add_paragraph()

    # =========================================================================
    # PHẦN 5: GIẢ LẬP VẤN ĐÁP HỘI ĐỒNG BẢO VỆ & GIẢI MÃ CHUYÊN SÂU
    # =========================================================================
    add_section_header(doc, "V", "GIẢ LẬP VẤN ĐÁP HỘI ĐỒNG BẢO VỆ & GIẢI MÃ CHUYÊN SÂU")
    
    add_subsection_header(doc, "CÂU HỎI 1: Bài toán tính toán thực chiến kích thước và chân đế")
    add_body_paragraph(
        doc,
        "Thầy/Cô Hội đồng hỏi: 'Một bức ảnh có kích thước W = 1000 pixels, H = 800 pixels. File nhãn ghi: 0 0.50 0.60 0.20 0.40.\n"
        "a) Kích thước thực tế của tấm biển là bao nhiêu pixel?\n"
        "b) Tọa độ chân đế tiếp xúc mặt đất y2 bằng bao nhiêu pixel?'"
    )
    add_callout_box(
        doc,
        "ĐÁP ÁN TÍNH TOÁN CHI TIẾT (ĐẠT ĐIỂM TUYỆT ĐỐI):\n\n"
        "a) Kích thước thực tế của tấm biển:\n"
        "• Chiều rộng: w_pixel = w * W = 0.20 * 1000 = 200 pixels.\n"
        "• Chiều cao:  h_pixel = h * H = 0.40 * 800 = 320 pixels.\n"
        "-> Tấm biển có kích thước là rộng 200px và cao 320px.\n\n"
        "b) Tọa độ chân đế tiếp xúc mặt đất (y2):\n"
        "• Tọa độ tâm dọc: y_tam = yc * H = 0.60 * 800 = 480 pixels.\n"
        "• Điểm chân đế đáy biển: y2 = y_tam + (h_pixel / 2) = 480 + (320 / 2) = 480 + 160 = 640 pixels.\n"
        "Hoặc tính gộp: y2 = (yc + h / 2) * H = (0.60 + 0.20) * 800 = 0.80 * 800 = 640 pixels.\n"
        "-> Tọa độ cắm chân vỉa hè là y_ground = y2 = 640 pixels (tính từ đỉnh ảnh xuống).",
        title="ĐÁP ÁN CHI TIẾT CÂU HỎI 1",
        box_type="success"
    )

    add_subsection_header(doc, "CÂU HỎI 2: Ý nghĩa toán học của tọa độ chuẩn hóa đối với Gradient Descent")
    add_body_paragraph(
        doc,
        "Thầy/Cô Hội đồng hỏi: 'Tại sao mạng YOLO không dự đoán trực tiếp tọa độ 4 góc pixel mà bắt buộc phải chuyển đổi "
        "sang dạng tâm và kích thước chuẩn hóa [xc, yc, w, h] thuộc [0, 1]? Về mặt giải thuật tối ưu hóa Gradient Descent, "
        "việc chuẩn hóa này mang lại lợi ích quyết định gì?'"
    )
    add_callout_box(
        doc,
        "KỊCH BẢN TRẢ LỜI ĐẠT ĐIỂM XUẤT SẮC TRƯỚC HỘI ĐỒNG:\n"
        "Dạ thưa Thầy/Cô, việc chuẩn hóa tọa độ về dải số thực [0.0, 1.0] mang lại 3 lợi thế toán học cốt tử cho mạng nơ-ron:\n\n"
        "1. Ổn định Gradient và triệt tiêu Bùng nổ Gradient (Exploding Gradient):\n"
        "   Nếu để nguyên giá trị pixel (từ hàng trăm đến hàng nghìn), ở những epoch khởi tạo đầu tiên, sai số dự đoán có thể lên tới hàng nghìn đơn vị. Đạo hàm của hàm mất mát sẽ sinh ra các vector gradient khổng lồ, khiến các trọng số bị cập nhật văng ra xa khỏi cực tiểu tối ưu, thậm chí gây lỗi sập hàm mất mát 'Loss = NaN'. Khi chuẩn hóa về [0, 1], sai số tối đa giữa nhãn và dự đoán luôn bị khống chế <= 1.0, giúp giải thuật Gradient Descent cập nhật trọng số êm ái và hội tụ cực kỳ ổn định.\n\n"
        "2. Tương thích hoàn hảo với hàm kích hoạt Sigmoid ở tầng Head:\n"
        "   Tầng đầu ra (Prediction Head) của YOLO sử dụng hàm phi tuyến tính Sigmoid: sigma(z) = 1 / (1 + e^-z) thuộc khoảng (0, 1). Hàm này tự nhiên ép toàn bộ dự đoán luôn nằm gọn trong khung hình, ngăn chặn việc mô hình sinh ra tọa độ âm hoặc bay ra ngoài ảnh.\n\n"
        "3. Phục vụ kỹ thuật Huấn luyện đa kích thước (Multi-scale Training):\n"
        "   Trong quá trình train, YOLOv8 liên tục thay đổi kích thước ảnh ngẫu nhiên giữa các batch (640x640, 960x960, 1280x1280) để học nhận diện vật thể ở mọi cự ly. Nhờ sử dụng tọa độ chuẩn hóa [0, 1], nhãn mục tiêu (Ground Truth) bất biến tuyệt đối, không cần tính toán lại nhãn dù ảnh phóng to hay thu nhỏ.",
        title="KỊCH BẢN PHẢN BIỆN CÂU HỎI 2 (HỘI ĐỒNG)",
        box_type="warning"
    )

    # =========================================================================
    # PHẦN 6: BẢN GHI NHỚ CỐT LÕI (KEY TAKEAWAYS)
    # =========================================================================
    add_section_header(doc, "VI", "BẢN GHI NHỚ CỐT LÕI NGÀY 08 (KEY TAKEAWAYS)")
    
    tbl_sum = doc.add_table(rows=5, cols=2)
    tbl_sum.alignment = WD_TABLE_ALIGNMENT.CENTER
    sum_data = [
        ("Cú pháp nhãn YOLO", "class_id x_center y_center width height (Tất cả tọa độ đều chuẩn hóa về [0, 1])."),
        ("Công thức chiều đi", "w = (x2-x1)/W, h = (y2-y1)/H, xc = (x1+x2)/(2W), yc = (y1+y2)/(2H)."),
        ("Công thức chiều về", "x1 = (xc - w/2)*W, y1 = (yc - h/2)*H, x2 = (xc + w/2)*W, y2 = (yc + h/2)*H."),
        ("Điểm chân cắm đất", "y_ground = y2 = (yc + h/2)*H. Tọa độ sống còn giao cho Track B tính vi phạm."),
        ("Lợi ích Gradient", "Chống Exploding Gradient, tương thích hàm Sigmoid, hỗ trợ Multi-scale Training.")
    ]
    for i, (k, v) in enumerate(sum_data):
        c0, c1 = tbl_sum.cell(i, 0), tbl_sum.cell(i, 1)
        c0.width, c1.width = Inches(2.2), Inches(4.3)
        set_cell_margins(c0, 70, 70, 100, 100)
        set_cell_margins(c1, 70, 70, 100, 100)
        
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.font.name = "Arial"
        
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.name = "Arial"
        
        if i == 0:
            set_cell_background(c0, HEX_SECONDARY)
            set_cell_background(c1, HEX_SECONDARY)
            r0.font.size = Pt(9.5)
            r0.font.bold = True
            r0.font.color.rgb = RGBColor(255, 255, 255)
            r1.font.size = Pt(9.5)
            r1.font.bold = True
            r1.font.color.rgb = RGBColor(255, 255, 255)
        else:
            set_cell_background(c0, HEX_BG_LIGHT if i % 2 == 1 else "FFFFFF")
            set_cell_background(c1, HEX_BG_LIGHT if i % 2 == 1 else "FFFFFF")
            r0.font.size = Pt(9)
            r0.font.bold = True
            r0.font.color.rgb = COLOR_DARK
            r1.font.size = Pt(9)
            r1.font.color.rgb = COLOR_DARK
    set_table_borders(tbl_sum, HEX_BORDER)
    doc.add_paragraph()

    # Lưu file
    doc.save(OUTPUT_FILE)
    print(f"[XUẤT BẢN THÀNH CÔNG] File Word Ngày 08 đã được tạo tại:\n👉 {OUTPUT_FILE}")


if __name__ == "__main__":
    build_day08_document()
