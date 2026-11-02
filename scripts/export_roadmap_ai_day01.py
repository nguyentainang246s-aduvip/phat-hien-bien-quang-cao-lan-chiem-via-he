"""
Script xuất bản bài học Ngày 01 thành file Word (.docx) chuyên nghiệp
Lưu trữ vào thư mục: roadmap AI/Ngay_01_Ban_Chat_Anh_So_Va_He_Toa_Do_OpenCV.docx
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
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "roadmap AI"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = str(OUTPUT_DIR / "Ngay_01_Ban_Chat_Anh_So_Va_He_Toa_Do_OpenCV.docx")

# Màu sắc thương hiệu học thuật sang trọng
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


def build_day01_document():
    doc = Document()
    
    # 1. Cấu hình lề trang (Margins A4)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        section.different_first_page_header_footer = False
        
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

    # 2. Tiêu đề đầu trang
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
    r_day = p_main.add_run("NGÀY 01: BẢN CHẤT ẢNH SỐ, MA TRẬN ĐIỂM ẢNH (NUMPY HWC),\nHỆ MÀU BGR & HỆ TỌA ĐỘ OPENCV\n")
    r_day.font.name = "Arial"
    r_day.font.size = Pt(16)
    r_day.font.bold = True
    r_day.font.color.rgb = COLOR_PRIMARY
    
    r_sub = p_main.add_run("Nền tảng thị giác máy tính cốt lõi dành cho Kỹ sư AI & Dữ liệu (Track A)")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_SECONDARY

    # Bảng Metadata
    tbl_meta = doc.add_table(rows=4, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_rows = [
        ("Phân hệ phụ trách:", "Track A — AI & Dữ liệu (Phát hiện vật thể, Dataset, Model & Tối ưu biên)"),
        ("Mã nguồn liên quan:", "detection/detector.py, scripts/demos/read_video.py, data/videos/"),
        ("Phương pháp tiếp cận:", "Ẩn dụ trực quan -> Bản chất toán học ma trận -> Code thực chiến -> Phản biện"),
        ("Mục tiêu ngày 01:", "Làm chủ ma trận ảnh HWC, quy ước BGR, Bounding Box (x1, y1, x2, y2) và điểm chân đế.")
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
    
    add_subsection_header(doc, "1. Ẩn dụ màn xếp hình cổ động trên khán đài sân vận động")
    add_body_paragraph(
        doc,
        "Hãy tưởng tượng bạn đang đứng tại sân vận động Mỹ Đình để theo dõi một màn xếp hình nghệ thuật: "
        "Khi đứng từ khán đài đối diện nhìn từ xa, mắt người nhìn thấy rất rõ ràng một lá cờ đỏ sao vàng hoặc một khẩu hiệu cổ động. "
        "Tuy nhiên, nếu bạn bước lại thật gần từng hàng ghế, thực chất chẳng hề có 'lá cờ' nào ở đó cả! "
        "Bạn chỉ nhìn thấy hàng nghìn cổ động viên ngồi ngay ngắn. Mỗi người cầm trên tay một tấm bìa màu và giơ lên ở đúng vị trí: "
        "hàng ghế thứ Y, cột ghế thứ X."
    )
    add_body_paragraph(
        doc,
        "Ảnh số trong máy tính chính xác là một màn xếp hình cổ động như vậy. Mỗi 'cổ động viên' là một điểm ảnh (Pixel - Picture Element). "
        "Máy tính không hề có tri giác để tự hiểu 'đây là cái biển quảng cáo' hay 'đây là mặt vỉa hè'. "
        "Thứ duy nhất máy tính nhìn thấy là một bảng số liệu khổng lồ gồm hàng triệu con số. "
        "Nhiệm vụ của người làm AI (Track A) là dạy cho mô hình tìm ra những quy luật số học đặc thù của cái biển quảng cáo giữa hàng triệu con số đó."
    )
    
    add_subsection_header(doc, "2. Ẩn dụ bảng danh sách điểm danh lớp học (Hàng trước, Cột sau)")
    add_body_paragraph(
        doc,
        "Khi mở một bảng tính Excel hay một sổ điểm danh, mắt bạn luôn tìm kiếm theo quy tắc: 'Tìm ở DÒNG (Hàng) thứ mấy trước', "
        "rồi mới gióng mắt sang 'CỘT thứ mấy'. Trong toán học ma trận và lập trình khoa học dữ liệu, quy ước quốc tế luôn là "
        "[Hàng, Cột] — nghĩa là chiều dọc (trục Y) được chỉ định trước, chiều ngang (trục X) được chỉ định sau. "
        "Nắm chắc trực giác này sẽ giúp bạn không bao giờ bị rơi vào bẫy nghịch đảo tọa độ của OpenCV."
    )

    # =========================================================================
    # PHẦN 2: MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC
    # =========================================================================
    add_section_header(doc, "II", "MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC")
    
    add_subsection_header(doc, "1. Ma trận 3 chiều NumPy: Cấu trúc (Height, Width, Channels)")
    add_body_paragraph(
        doc,
        "Khi một khung hình từ camera CCTV được giải mã vào bộ nhớ RAM bằng OpenCV, nó được tổ chức thành một mảng NumPy 3 chiều: "
        "Shape = (H, W, C) = (Chiều cao, Chiều rộng, Số kênh màu)."
    )
    
    # Bảng giải thích Shape
    tbl_shape = doc.add_table(rows=4, cols=3)
    tbl_shape.alignment = WD_TABLE_ALIGNMENT.CENTER
    shape_data = [
        ("Chiều (Axis)", "Ý nghĩa trong Thị giác máy tính", "Ví dụ chuẩn Camera Full HD"),
        ("Height (H)", "Số lượng hàng điểm ảnh theo phương thẳng đứng (Trục Y).", "1080 hàng (pixels)"),
        ("Width (W)", "Số lượng cột điểm ảnh theo phương nằm ngang (Trục X).", "1920 cột (pixels)"),
        ("Channels (C)", "Số lớp màu xếp chồng lên nhau tạo nên màu sắc tổng hợp.", "3 lớp màu (B, G, R)")
    ]
    for i, row in enumerate(shape_data):
        for j, text in enumerate(row):
            c = tbl_shape.cell(i, j)
            c.width = Inches(2.1)
            set_cell_margins(c, 80, 80, 100, 100)
            p = c.paragraphs[0]
            r = p.add_run(text)
            r.font.name = "Arial"
            if i == 0:
                set_cell_background(c, HEX_HEADER_BG)
                r.font.size = Pt(9.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
            else:
                set_cell_background(c, HEX_BG_LIGHT if i % 2 == 1 else "FFFFFF")
                r.font.size = Pt(9)
                r.font.color.rgb = COLOR_DARK
    set_table_borders(tbl_shape, HEX_BORDER)
    doc.add_paragraph()

    add_body_paragraph(
        doc,
        "Kiểu dữ liệu của mỗi giá trị pixel là uint8 (Unsigned 8-bit Integer — số nguyên không dấu 8 bit). "
        "Bộ nhớ dành đúng 1 byte (8 bit) để lưu trữ cường độ của một kênh màu, do đó giá trị số chỉ có thể biến thiên trong đoạn: "
        "0 ≤ Pixel ≤ 2^8 - 1 = 255. "
        "Giá trị 0 đại diện cho màu đen tuyệt đối (tắt sáng), và 255 đại diện cho màu sáng rực rỡ nhất."
    )

    add_subsection_header(doc, "2. Nguồn gốc lịch sử của hệ màu BGR trong OpenCV (Tại sao không phải RGB?)")
    add_body_paragraph(
        doc,
        "Mọi màn hình máy tính và máy ảnh số ngày nay đều hiển thị theo chuẩn RGB (Red - Green - Blue). "
        "Tuy nhiên, khi bạn nạp ảnh bằng OpenCV, thứ tự 3 kênh màu luôn luôn bị đảo ngược thành B - G - R (Blue trước, Green giữa, Red sau)."
    )
    add_callout_box(
        doc,
        "LÝ DO SÂU XA VỀ MẶT KỸ THUẬT PHẦN CỨNG:\n"
        "Vào năm 1999, khi tập đoàn Intel khởi xướng phát triển thư viện OpenCV tại trung tâm nghiên cứu Nizhny Novgorod, "
        "các card bắt hình camera công nghiệp và bộ nhớ đồ họa thời bấy giờ lưu trữ dữ liệu theo kiến trúc Little-Endian "
        "(byte có trọng số thấp nhất được lưu ở địa chỉ bộ nhớ đầu tiên). "
        "Chuẩn màu RGB khi đi vào bộ nhớ Little-Endian tự nhiên bị đảo ngược thành BGR. "
        "Để đạt tốc độ tối đa cho các hệ thống thời gian thực, các kỹ sư Intel đã quyết định giữ nguyên thứ tự BGR nhằm triệt tiêu "
        "hoàn toàn chi phí tính toán cho thao tác hoán đổi byte (Byte Swapping). "
        "OpenCV bảo tồn thiết kế này suốt 25 năm qua để đảm bảo tính tương thích ngược.",
        title="BẢN CHẤT KỸ THUẬT: TẠI SAO OPENCV DÙNG HỆ MÀU BGR?",
        box_type="info"
    )

    add_subsection_header(doc, "3. Hệ tọa độ màn hình & Định vị Bounding Box (x1, y1, x2, y2)")
    add_body_paragraph(
        doc,
        "Khác hoàn toàn với hệ tọa độ Descartes trong toán học phổ thông (gốc O ở góc dưới bên trái, trục Y hướng lên trên), "
        "trong màn hình máy tính và thị giác máy tính:\n"
        "• Gốc tọa độ (0, 0) nằm tại GÓC TRÊN CÙNG BÊN TRÁI của khung hình.\n"
        "• Trục X tăng dần từ TRÁI sang PHẢI (từ cột 0 đến cột Width - 1).\n"
        "• Trục Y tăng dần từ TRÊN xuống DƯỚI (từ hàng 0 đến hàng Height - 1)."
    )
    add_body_paragraph(
        doc,
        "Khi mô hình YOLOv8n phát hiện một vật thể, hộp bao hình chữ nhật (Bounding Box) được biểu diễn bằng 4 tọa độ cực trị:\n"
        "• (x1, y1): Điểm góc Trên - Trái (Top-Left corner).\n"
        "• (x2, y2): Điểm góc Dưới - Phải (Bottom-Right corner).\n"
        "• Tính chất toán học bất biến: Luôn luôn có x2 > x1 và y2 > y1.\n"
        "• Chiều rộng hộp: w = x2 - x1. Chiều cao hộp: h = y2 - y1."
    )
    
    add_callout_box(
        doc,
        "GIAO DIỆN BÀN GIAO SỐNG CÒN SANG PHÂN HỆ TRACK B:\n"
        "Bạn Track B phụ trách module violation/checker.py cần biết tọa độ chân biển cắm trên vỉa hè để đối chiếu với đa giác ROI vỉa hè. "
        "Từ 4 con số (x1, y1, x2, y2) của Track A, điểm chân đế tiếp xúc mặt đất (Ground Contact Point) được tính chính xác bằng công thức:\n"
        "               x_ground = (x1 + x2) / 2       và       y_ground = y2\n"
        "Điểm (x_ground, y_ground) là điểm đáy chính giữa của hộp chữ nhật, đại diện cho vị trí cắm chân của biển quảng cáo trên vỉa hè.",
        title="GIAO DIỆN BÀN GIAO SỐNG CÒN GIỮA TRACK A VÀ TRACK B",
        box_type="success"
    )

    # =========================================================================
    # PHẦN 3: HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN DỰ ÁN
    # =========================================================================
    add_section_header(doc, "III", "HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN DỰ ÁN")
    
    add_subsection_header(doc, "1. Mổ xẻ điểm chuẩn hóa dữ liệu trong detection/detector.py")
    add_body_paragraph(
        doc,
        "Hãy mở file detection/detector.py trong mã nguồn dự án tại các dòng 70–83. "
        "Đây là nơi mô hình YOLOv8 xuất dữ liệu thô từ PyTorch Tensor trên card đồ họa và được ép kiểu về số nguyên thuần túy:"
    )
    
    code_detector = (
        "# Trích đoạn mã nguồn trong detection/detector.py (Chuẩn hóa đầu ra AI)\n"
        "boxes = results[0].boxes\n"
        "for box in boxes:\n"
        "    # 1. Ép kiểu PyTorch Tensor (trên GPU/CPU) sang mảng NumPy số nguyên (x1, y1, x2, y2)\n"
        "    xyxy = box.xyxy[0].cpu().numpy().astype(int)\n"
        "    conf = float(box.conf[0].cpu().numpy())\n"
        "    cls_id = int(box.cls[0].cpu().numpy())\n"
        "    cls_name = self.class_names.get(cls_id, f'class_{cls_id}')\n"
        "    \n"
        "    # 2. Đóng gói dữ liệu sạch thành Dictionary Python native\n"
        "    detections.append({\n"
        "        'box': (int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])),\n"
        "        'conf': round(conf, 2),\n"
        "        'class_id': cls_id,\n"
        "        'class_name': cls_name\n"
        "    })"
    )
    add_code_block(doc, code_detector)

    add_subsection_header(doc, "2. Bài tập thực hành dòng lệnh: Đọc ma trận và cắt Bounding Box (Lab Ngày 01)")
    add_body_paragraph(
        doc,
        "Mở terminal PowerShell trong thư mục gốc của dự án, kích hoạt môi trường ảo và thực thi script kiểm tra sau:"
    )
    
    code_lab = (
        "import cv2\n"
        "import numpy as np\n"
        "\n"
        "# 1. Đọc frame đầu tiên từ video kiểm thử thực tế của đồ án\n"
        "cap = cv2.VideoCapture('data/videos/video test.mp4')\n"
        "ret, frame = cap.read()\n"
        "cap.release()\n"
        "\n"
        "if ret:\n"
        "    # 2. In các thuộc tính vật lý của ma trận ảnh\n"
        "    h, w, c = frame.shape\n"
        "    print(f'[*] Kích thước khung hình: Cao (H)={h}px, Rộng (W)={w}px, Kênh màu (C)={c}')\n"
        "    print(f'[*] Kiểu dữ liệu điểm ảnh : {frame.dtype}')\n"
        "    \n"
        "    # 3. Truy cập giá trị màu tại điểm ảnh (x=300, y=500)\n"
        "    # Lưu ý: Cú pháp ma trận NumPy bắt buộc là [Hàng, Cột] -> [y, x]\n"
        "    blue, green, red = frame[500, 300]\n"
        "    print(f'[*] Màu sắc tại pixel (x=300, y=500): B={blue}, G={green}, R={red}')\n"
        "    \n"
        "    # 4. Trích xuất một vùng biển hiệu (Crop Bounding Box) giả lập: x1=150, y1=200, x2=400, y2=600\n"
        "    # Trong NumPy: frame[y1:y2, x1:x2]\n"
        "    crop_signboard = frame[200:600, 150:400]\n"
        "    cv2.imwrite('datasets/crop_test_day01.jpg', crop_signboard)\n"
        "    print('[+] Đã cắt và lưu thành công ảnh crop vào: datasets/crop_test_day01.jpg')\n"
        "else:\n"
        "    print('[!] Lỗi: Không thể mở file video.')"
    )
    add_code_block(doc, code_lab)

    # =========================================================================
    # PHẦN 4: SẢN PHẨM BÀN GIAO & CÁCH TỰ KIỂM TRA
    # =========================================================================
    add_section_header(doc, "IV", "SẢN PHẨM BÀN GIAO & TIÊU CHÍ TỰ KIỂM TRA")
    add_body_paragraph(
        doc,
        "Để đánh giá bạn đã hoàn thành xuất sắc mục tiêu học tập của Ngày 01 hay chưa, "
        "hãy đối chiếu với checklist 3 tiêu chí kỹ thuật dưới đây:"
    )
    
    tbl_check = doc.add_table(rows=4, cols=3)
    tbl_check.alignment = WD_TABLE_ALIGNMENT.CENTER
    check_data = [
        ("STT", "Tiêu chí kỹ thuật cần đạt", "Phương pháp kiểm tra kết quả"),
        ("01", "Chạy thành công đoạn code Lab Ngày 01 trên PowerShell.", "Console in ra đúng kích thước ảnh H, W, C và kiểu uint8."),
        ("02", "Tạo ra file ảnh crop trong thư mục datasets/.", "File datasets/crop_test_day01.jpg tồn tại, mở lên xem rõ nét."),
        ("03", "Giải thích trôi chảy quy ước BGR và tọa độ Bbox.", "Tự trả lời tự tin 2 câu hỏi phản biện ở Phần V.")
    ]
    for i, row in enumerate(check_data):
        for j, text in enumerate(row):
            c = tbl_check.cell(i, j)
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
    set_table_borders(tbl_check, HEX_BORDER)
    doc.add_paragraph()

    # =========================================================================
    # PHẦN 5: GIẢ LẬP VẤN ĐÁP HỘI ĐỒNG BẢO VỆ & GIẢI MÃ CHUYÊN SÂU
    # =========================================================================
    add_section_header(doc, "V", "GIẢ LẬP VẤN ĐÁP HỘI ĐỒNG BẢO VỆ & GIẢI MÃ CHUYÊN SÂU")
    
    add_subsection_header(doc, "CÂU HỎI 1: Bẫy cú pháp frame[500, 300] vs (300, 500)")
    add_body_paragraph(
        doc,
        "Thầy/Cô Hội đồng hỏi: 'Tại sao khi lập trình với OpenCV, để lấy giá trị màu tại điểm ảnh (x=300, y=500), "
        "bạn lại phải viết trong code là frame[500, 300], nhưng khi dùng hàm vẽ hình cv2.rectangle hay cv2.circle lại truyền tham số (300, 500)? "
        "Nếu viết nhầm thì hệ thống sẽ xảy ra lỗi gì?'"
    )
    add_callout_box(
        doc,
        "ĐÁP ÁN PHẢN BIỆN CHUẨN XÁC:\n"
        "• Bản chất: Đây là sự khác biệt giữa hai góc nhìn: Góc nhìn Ma trận số học (Matrix indexing) và Góc nhìn Tọa độ không gian (Geometric coordinate).\n"
        "  1. Khi truy cập mảng NumPy: Thư viện tuân theo chuẩn đại số tuyến tính: Ma trận[Hàng, Cột]. Do đó, Hàng dọc chính là trục Y, Cột ngang chính là trục X -> Cú pháp bắt buộc là frame[y, x] = frame[500, 300].\n"
        "  2. Khi gọi hàm đồ họa OpenCV: Hàm nhận đầu vào là tọa độ điểm không gian Descartes chuẩn (X, Y) để vẽ vector -> Cú pháp là cv2.circle(img, (x, y), ...).\n"
        "• Hậu quả nếu nhầm lẫn: Nếu viết nhầm thành frame[300, 500], ảnh sẽ bị truy cập lệch điểm sang hàng 300 cột 500 (bị xoay gương qua đường chéo ma trận). Nếu ảnh có chiều cao 720 và chiều rộng 1280, việc gọi pixel ngoài biên như frame[1000, 200] sẽ lập tức gây sập chương trình với ngoại lệ 'IndexError: index out of bounds'.",
        title="BẢN LĨNH PHẢN BIỆN CÂU HỎI 1",
        box_type="info"
    )

    add_subsection_header(doc, "CÂU HỎI 2: Sai số của Hộp chữ nhật 2D khi biển đặt nghiêng/xiên trong không gian phối cảnh 3D")
    add_body_paragraph(
        doc,
        "Thầy/Cô Hội đồng hỏi: 'Trong thực tế phố xá Việt Nam, biển hiệu chân sắt chữ A hoặc biển quảng cáo hộp đèn thường đặt nghiêng, "
        "xoay chéo theo góc nhìn phối cảnh (Perspective) của camera CCTV. Bounding Box của bạn là hình chữ nhật 2D song song trục tọa độ "
        "(Axis-Aligned Bounding Box). Việc xấp xỉ này chắc chắn tạo ra khoảng thừa (Background Padding) ở hai bên đáy. "
        "Liệu công thức chân đế y_ground = y2 có gây sai số làm kết luận sai vi phạm vỉa hè không? Bạn giải quyết thế nào?'"
    )
    
    add_callout_box(
        doc,
        "KỊCH BẢN TRẢ LỜI ĐẠT ĐIỂM XUẤT SẮC TRƯỚC HỘI ĐỒNG:\n"
        "Em xin cảm ơn Thầy/Cô đã đặt một câu hỏi rất sâu về bản chất hình học thị giác máy tính. Nhóm em đã lường trước giới hạn vật lý này và thiết kế kiến trúc xử lý 3 tầng để triệt tiêu hoàn toàn sai số:\n\n"
        "1. Về phía Track A (AI & Gán nhãn):\n"
        "   Khi dán nhãn dữ liệu trên Roboflow, em tuân thủ nguyên tắc vàng: cạnh đáy Bounding Box (y2) luôn được kéo chạm sát điểm tiếp đất thấp nhất của chân biển. Nhờ đó, cao độ tiếp đất y_ground = y2 luôn chính xác tuyệt đối theo phương đứng (trục Y).\n\n"
        "2. Về phía sai số phương ngang (Do hộp 2D có khoảng trống thừa 2 bên):\n"
        "   Nhóm em không chỉ kiểm tra 1 điểm tâm đáy duy nhất. Module violation/checker.py (do bạn Track B xây dựng) áp dụng cơ chế KIỂM TRA 3 ĐIỂM TIẾP XÚC ĐÁY: Chân Trái (x1, y2), Chân Giữa (x_mid, y2), và Chân Phải (x2, y2) kết hợp với Ngưỡng dung sai biên độ (Edge Tolerance = 15 pixels). Biển chỉ bị nghi ngờ khi điểm chân thực sự nằm trong đa giác vỉa hè.\n\n"
        "3. Điều kiện bảo vệ kép (Tỷ lệ diện tích đè vỉa hè Overlap Ratio ≥ 30%):\n"
        "   Hệ thống yêu cầu thêm điều kiện thứ hai: Tỷ lệ giao cắt diện tích giữa Bounding Box và Đa giác ROI vỉa hè (tính qua thư viện hình học Shapely) phải đạt từ 30% trở lên. Do đó, nếu một tấm biển đặt trên bậc thềm nhà hợp pháp mà chỉ có một góc hộp chữ nhật 2D lấn nhẹ vào vỉa hè, hệ thống vẫn an toàn xếp loại BÌNH THƯỜNG (NORMAL), hoàn toàn không xảy ra báo động giả (False Alarm).",
        title="KỊCH BẢN PHẢN BIỆN THUYẾT PHỤC CÂU HỎI 2 (HỘI ĐỒNG)",
        box_type="warning"
    )

    # =========================================================================
    # PHẦN 6: BẢNG TỔNG HỢP KIẾN THỨC CỐT LÕI (KEY TAKEAWAYS)
    # =========================================================================
    add_section_header(doc, "VI", "BẢN GHI NHỚ CỐT LÕI NGÀY 01 (KEY TAKEAWAYS)")
    
    tbl_summary = doc.add_table(rows=6, cols=2)
    tbl_summary.alignment = WD_TABLE_ALIGNMENT.CENTER
    summary_data = [
        ("Thuật ngữ / Khái niệm", "Quy tắc cốt lõi cần thuộc lòng"),
        ("Cấu trúc ảnh NumPy", "Shape = (Height, Width, Channels) = (H, W, 3). Dtype luôn là uint8 (0-255)."),
        ("Hệ màu OpenCV", "BGR (Blue - Green - Red). Cần chuyển cv2.cvtColor(img, cv2.COLOR_BGR2RGB) khi dùng Matplotlib."),
        ("Gốc tọa độ ảnh", "Gốc (0, 0) ở GÓC TRÊN CÙNG BÊN TRÁI. Trục X sang phải, Trục Y xuống dưới."),
        ("Bounding Box chuẩn", "4 tọa độ: (x1, y1, x2, y2). Chiều rộng w = x2 - x1, chiều cao h = y2 - y1."),
        ("Điểm chân cắm vỉa hè", "Tọa độ bàn giao cho Track B: x_ground = (x1 + x2)/2, y_ground = y2.")
    ]
    for i, (k, v) in enumerate(summary_data):
        c0, c1 = tbl_summary.cell(i, 0), tbl_summary.cell(i, 1)
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
    set_table_borders(tbl_summary, HEX_BORDER)
    doc.add_paragraph()

    # Lưu tài liệu
    doc.save(OUTPUT_FILE)
    print(f"[XUẤT BẢN THÀNH CÔNG] File Word Ngày 01 đã được tạo tại:\n👉 {OUTPUT_FILE}")


if __name__ == "__main__":
    build_day01_document()
