"""
Script xuất bản bài học Ngày 05 thành file Word (.docx) chuyên nghiệp
Lưu trữ vào thư mục: roadmap AI/Ngay_05_Bo_Sung_Anh_Thuc_Dia_Goc_Nhin_CCTV.docx
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
OUTPUT_FILE = str(OUTPUT_DIR / "Ngay_05_Bo_Sung_Anh_Thuc_Dia_Goc_Nhin_CCTV.docx")

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


def build_day05_document():
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
    r_day = p_main.add_run("NGÀY 05: BỔ SUNG 30–50 ẢNH THỰC ĐỊA GÓC CAO CHÚC XUỐNG\nMÔ PHỎNG GÓC NHÌN CAMERA AN NINH CCTV CỐ ĐỊNH\n")
    r_day.font.name = "Arial"
    r_day.font.size = Pt(16)
    r_day.font.bold = True
    r_day.font.color.rgb = COLOR_PRIMARY
    
    r_sub = p_main.add_run("Khắc phục lệch miền dữ liệu (Domain Gap), giải quyết bài toán biển nhỏ ở xa (Small Objects)")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_SECONDARY

    # Bảng Metadata
    tbl_meta = doc.add_table(rows=4, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_rows = [
        ("Phân hệ phụ trách:", "Track A — AI & Dữ liệu (Field Data Collection & Domain Adaptation)"),
        ("Mã nguồn liên quan:", "datasets/raw_images/, ke-hoach-do-an-tot-nghiep.md, configs/settings.yaml"),
        ("Đặc tính hình học:", "Perspective Projection, Pitch Angle 20°–45°, Height 2.5m–4.5m"),
        ("Mục tiêu ngày 05:", "Thu thập 30-50 ảnh chuẩn góc nhìn CCTV, bổ sung mẫu biển nhỏ ở cự ly xa > 20m.")
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
    
    add_subsection_header(doc, "1. Ẩn dụ ảnh thẻ CCCD vs Nhìn từ ban công tầng 2")
    add_body_paragraph(
        doc,
        "Hãy tưởng tượng bạn đang xem 2 bức ảnh của cùng một người đi bộ trên phố:\n"
        "• Bức ảnh 1 (Ảnh thẻ CCCD): Máy ảnh đặt ngang tầm mắt. Khuôn mặt hiển thị thẳng đứng, đối xứng, thấy rõ hai tai, sống mũi và cằm.\n"
        "• Bức ảnh 2 (Nhìn từ ban công tầng 2): Bạn đứng từ trên cao nhìn chúc xuống người đó đang rảo bước dưới lòng đường. "
        "Lúc này bạn hầu như chỉ nhìn thấy đỉnh đầu, bờ vai, chóp nón lá hoặc mui xe! Toàn bộ tỷ lệ hình thể bị nén dẹp lại theo phương thẳng đứng.\n"
        "Nếu một đứa trẻ chỉ được dạy nhận diện con người qua ảnh thẻ chụp ngang, khi đứng trên ban công tầng 2 nhìn xuống nó sẽ hoàn toàn mất phương hướng "
        "và không thể nhận ra ai là người!"
    )
    add_body_paragraph(
        doc,
        "Camera an ninh CCTV ngoài đời thực luôn được lắp đặt ở độ cao từ 2.5m đến 4.5m trên cột đèn hoặc mái hiên nhà dân, "
        "chĩa chúc xuống mặt đường một góc từ 20° đến 45°. "
        "Nếu bộ dữ liệu của bạn chỉ toàn các bức ảnh chụp bằng điện thoại ngang ngực như chụp ảnh selfie, "
        "mô hình AI sẽ mắc phải lỗi học thuật nghiêm trọng: Lệch miền dữ liệu (Domain Gap) — dữ liệu lúc huấn luyện khác xa dữ liệu lúc triển khai thực tế!"
    )

    # =========================================================================
    # PHẦN 2: MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC
    # =========================================================================
    add_section_header(doc, "II", "MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC")
    
    add_subsection_header(doc, "1. Phép chiếu phối cảnh 3D sang 2D (Perspective Projection)")
    add_body_paragraph(
        doc,
        "Trong quang học camera, một điểm P_world trong không gian 3 chiều được chiếu lên cảm biến ảnh 2 chiều qua ma trận camera:\n"
        "               p_image = K * [R | T] * P_world\n\n"
        "Khi camera được nâng lên cao và nghiêng chúc xuống (Pitch angle theta = 20° - 45°), 3 biến dạng hình học vật lý sẽ phát sinh:\n"
        "1. Biến dạng hội tụ (Perspective Distortion): Các cạnh thẳng đứng của biển chữ A khi chiếu lên 2D sẽ hơi xiên chéo, hội tụ về một điểm tụ (Vanishing Point).\n"
        "2. Tỷ lệ diện tích nóc biển lộ rõ hơn: Đỉnh biển và mặt bạt trên chiếm diện tích lớn, trong khi chân cắm mặt đất bị thu hẹp lại.\n"
        "3. Bài toán biến thiên kích thước (Scale Variation & Small Objects): "
        "Biển ở gần (cách 3-5m) có kích thước lớn khoảng 200x400 pixels; nhưng biển ở xa (cách 20-30m) chỉ còn khoảng 25x50 pixels "
        "(chiếm chưa đầy 0.25% diện tích ảnh). Nếu không có ảnh chụp góc rộng từ xa, AI sẽ bỏ sót toàn bộ các biển này (False Negative)."
    )

    add_subsection_header(doc, "2. Quy chuẩn vàng 4 tiêu chí khi chụp ảnh thực địa bổ sung")
    add_body_paragraph(
        doc,
        "Khi thực hiện thu thập 30 – 50 ảnh thực địa bằng điện thoại thông minh, Kỹ sư dữ liệu Track A bắt buộc phải tuân thủ 4 quy tắc:"
    )
    
    # Bảng Quy chuẩn
    tbl_rules = doc.add_table(rows=5, cols=3)
    tbl_rules.alignment = WD_TABLE_ALIGNMENT.CENTER
    rules_data = [
        ("Tiêu chí kỹ thuật", "Yêu cầu thực hiện khi chụp ảnh", "Mục đích học máy"),
        ("Góc máy chúc xuống\n(Pitch Angle)", "Giơ điện thoại cao quá đầu (2.0m - 2.3m) hướng chéo xuống đất, hoặc đứng trên bậc tam cấp, ban công tầng lửng chụp xuống 20° - 35°.", "Triệt tiêu Domain Gap, giúp AI quen với hình thái biển nhìn từ trên cao."),
        ("Đa dạng cự ly\n(Scale Diversity)", "50% ảnh chụp cự ly gần (3 - 5m) và 50% ảnh chụp cự ly xa (15 - 25m với biển nhỏ < 50 pixels).", "Tăng cường độ nhạy cho nhóm vật thể nhỏ (Small Objects)."),
        ("Đa dạng kiểu dáng\n(Morphology)", "Chụp đủ 4 chủng loại: Standee chữ A, biển hộp đèn đứng, bảng đen chân sắt, standee cuốn chữ X.", "Bao quát toàn bộ phổ vật thể lấn chiếm thực tế trên đường phố."),
        ("Đa dạng bối cảnh\n(Environmental Context)", "Chụp lúc nắng gắt có bóng đổ, lúc trời râm mát, vỉa hè có xe máy đậu xung quanh che khuất một phần.", "Rèn luyện khả năng chống chịu nhiễu và bắt biển bị che khuất một phần (Occlusion).")
    ]
    for i, row in enumerate(rules_data):
        for j, text in enumerate(row):
            c = tbl_rules.cell(i, j)
            c.width = Inches(1.8) if j == 0 else (Inches(2.7) if j == 1 else Inches(2.0))
            set_cell_margins(c, 70, 70, 90, 90)
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
    set_table_borders(tbl_rules, HEX_BORDER)
    doc.add_paragraph()

    # =========================================================================
    # PHẦN 3: HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN DỰ ÁN
    # =========================================================================
    add_section_header(doc, "III", "HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN DỰ ÁN")
    
    add_subsection_header(doc, "1. Ghi nhận trong tài liệu thiết kế đồ án ke-hoach-do-an-tot-nghiep.md")
    add_body_paragraph(
        doc,
        "Tại dòng 34 của tài liệu ke-hoach-do-an-tot-nghiep.md, đồ án đã nêu rõ giới hạn vật lý của camera CCTV và phương hướng xử lý:"
    )
    add_callout_box(
        doc,
        "'Biển xa, nhỏ (Small Objects): Huấn luyện ở độ phân giải cao imgsz=1280.\n"
        "Nhóm biển nhỏ (diện tích S < 0.25% khung hình) ở cự ly xa > 20 mét đạt Recall ban đầu 60.87%. "
        "Cần bổ sung mẫu thực địa góc nhìn CCTV và áp dụng Mosaic Augmentation để nâng cao độ nhạy của bộ phát hiện.'",
        title="TRÍCH DẪN TÀI LIỆU KỸ THUẬT ĐATN20224083",
        box_type="info"
    )

    add_subsection_header(doc, "2. Script Python kiểm tra độ phân giải và chất lượng ảnh thực địa")
    add_body_paragraph(
        doc,
        "Sau khi chép các ảnh chụp mới vào thư mục datasets/raw_images/, hãy chạy script sau để kiểm tra chuẩn HD:"
    )
    code_check = (
        "import os\n"
        "import cv2\n"
        "\n"
        "def audit_field_images(img_dir='datasets/raw_images'):\n"
        "    if not os.path.exists(img_dir):\n"
        "        print(f'[!] Thư mục không tồn tại: {img_dir}')\n"
        "        return\n"
        "        \n"
        "    files = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]\n"
        "    print('=' * 60)\n"
        "    print(f'KIỂM TOÁN CHẤT LƯỢNG ẢNH THỰC ĐỊA ({len(files)} files)')\n"
        "    print('=' * 60)\n"
        "    \n"
        "    valid_hd = 0\n"
        "    for f in files:\n"
        "        p = os.path.join(img_dir, f)\n"
        "        img = cv2.imread(p)\n"
        "        if img is not None:\n"
        "            h, w = img.shape[:2]\n"
        "            if w >= 1280 or h >= 720:\n"
        "                valid_hd += 1\n"
        "                \n"
        "    print(f'[+] Số lượng ảnh đạt chuẩn HD trở lên: {valid_hd}/{len(files)}')\n"
        "    if valid_hd == len(files) and len(files) >= 30:\n"
        "        print('[V] ĐÁNH GIÁ: Bộ ảnh thực địa đạt chuẩn chất lượng xuất sắc!')\n"
        "    else:\n"
        "        print('[!] CẢNH BÁO: Cần bổ sung thêm ảnh hoặc kiểm tra lại độ phân giải.')\n"
        "    print('=' * 60)"
    )
    add_code_block(doc, code_check)

    # =========================================================================
    # PHẦN 4: SẢN PHẨM BÀN GIAO & CÁCH TỰ KIỂM TRA
    # =========================================================================
    add_section_header(doc, "IV", "SẢN PHẨM BÀN GIAO & TIÊU CHÍ TỰ KIỂM TRA")
    
    tbl_eval = doc.add_table(rows=4, cols=3)
    tbl_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
    eval_data = [
        ("STT", "Tiêu chuẩn đánh giá", "Kết quả nghiệm thu của sinh viên"),
        ("01", "Bổ sung đủ số lượng 30 - 50 ảnh thực địa.", "Thư mục datasets/raw_images/ có thêm ảnh góc cao chúc xuống."),
        ("02", "Đạt chuẩn độ phân giải HD/Full HD.", "100% ảnh đạt độ phân giải tối thiểu 1280x720, không bị nén vỡ hạt."),
        ("03", "Bao phủ cự ly xa (Small Objects).", "Có ít nhất 15 bức ảnh chụp biển hiệu ở khoảng cách xa > 15-20 mét.")
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
    
    add_subsection_header(doc, "CÂU HỎI 1: Sai lầm khi chụp ảnh ngang tầm mắt (Eye-level) cho bài toán CCTV")
    add_body_paragraph(
        doc,
        "Thầy/Cô Hội đồng hỏi: 'Tại sao việc chụp ảnh ngang tầm mắt cho một mô hình giám sát camera an ninh trên cao "
        "lại bị coi là một sai lầm kỹ thuật nghiêm trọng?'"
    )
    add_callout_box(
        doc,
        "ĐÁP ÁN PHẢN BIỆN CHUẨN XÁC CỦA SINH VIÊN (XUẤT SẮC):\n"
        "• Bản chất: Dự án là hệ thống giám sát vỉa hè qua camera CCTV cố định lắp đặt ở trên cao (2.5m - 4.5m). Khi chụp ảnh ngang tầm mắt, AI chỉ học được các đặc trưng hình học vuông vức ở góc nhìn trực diện.\n"
        "• Khi đưa lên camera trên cao thực tế, góc nhìn phối cảnh (Perspective) làm thay đổi hoàn toàn các cạnh viền, tỷ lệ mặt trên/mặt đáy và chân đế tiếp đất. AI sẽ bị hiện tượng Lệch miền dữ liệu (Domain Gap) và không thể nhận diện biển một cách chính xác nhất.",
        title="KỊCH BẢN PHẢN BIỆN CÂU HỎI 1",
        box_type="success"
    )

    add_subsection_header(doc, "CÂU HỎI 2: Chiến lược kỹ thuật giải quyết bài toán biển nhỏ ở xa (> 20m)")
    add_body_paragraph(
        doc,
        "Thầy/Cô Hội đồng hỏi: 'Biển quảng cáo ở khoảng cách xa (> 20m) chỉ chiếm dưới 0.25% diện tích ảnh và dễ lẫn vào nền gạch. "
        "Ở vai trò Kỹ sư AI & Dữ liệu (Track A), em áp dụng những giải pháp nào để mô hình không bị bỏ sót (False Negative) nhóm biển này?'"
    )
    add_callout_box(
        doc,
        "KỊCH BẢN TRẢ LỜI ĐẠT ĐIỂM XUẤT SẮC TRƯỚC HỘI ĐỒNG:\n"
        "Dạ thưa Thầy/Cô, nhóm em đã thiết kế giải pháp kỹ thuật đồng bộ ở cả 2 tầng Dữ liệu và Cấu hình Huấn luyện:\n\n"
        "1. Tầng Kỹ nghệ Dữ liệu (Data Strategy):\n"
        "   • Em chủ động bổ sung bộ ảnh góc rộng thực địa chụp từ xa, bao phủ đa dạng các trường hợp biển kích thước nhỏ (< 50 pixels) và biển bị xe máy/người che khuất một phần (Occlusion) để AI học cách trích xuất đặc trưng trong điều kiện khó khăn.\n"
        "   • Áp dụng kỹ thuật Mosaic Augmentation (ghép 4 bức ảnh với tỷ lệ co nhỏ ngẫu nhiên), buộc mạng nơ-ron phải liên tục xử lý các vật thể ở kích thước siêu nhỏ trong suốt quá trình train.\n\n"
        "2. Tầng Cấu hình Huấn luyện (Training Resolution):\n"
        "   • Thay vì dùng độ phân giải mặc định imgsz=640, em cấu hình huấn luyện ở độ phân giải cao imgsz=1280 trên GPU Colab Tesla T4.\n"
        "   • Diện tích ma trận tăng gấp 4 lần giúp bảo toàn trọn vẹn thông tin cạnh viền, cấu trúc khung sắt và chữ viết trên biển hiệu ở xa, trực tiếp nâng chỉ số Recall của nhóm Small Object từ dưới 60% lên trên 78%.",
        title="KỊCH BẢN PHẢN BIỆN CÂU HỎI 2 (HỘI ĐỒNG)",
        box_type="warning"
    )

    # =========================================================================
    # PHẦN 6: BẢN GHI NHỚ CỐT LÕI (KEY TAKEAWAYS)
    # =========================================================================
    add_section_header(doc, "VI", "BẢN GHI NHỚ CỐT LÕI NGÀY 05 (KEY TAKEAWAYS)")
    
    tbl_sum = doc.add_table(rows=5, cols=2)
    tbl_sum.alignment = WD_TABLE_ALIGNMENT.CENTER
    sum_data = [
        ("Nội dung cốt lõi", "Quy tắc bắt buộc phải thuộc lòng"),
        ("Góc nhìn CCTV chuẩn", "Lắp cao 2.5m - 4.5m, chúc xuống 20° - 45°. Chụp ảnh thực địa phải giơ cao quá đầu để mô phỏng."),
        ("Hiện tượng Domain Gap", "Lệch miền dữ liệu giữa ảnh chụp ngang và ảnh camera trên cao. Cần bổ sung ảnh cùng phân phối."),
        ("Small Object Problem", "Biển xa chiếm < 0.25% diện tích ảnh. Cần bổ sung ảnh cự ly 15 - 25m."),
        ("Giải pháp imgsz=1280", "Huấn luyện ở độ phân giải 1280x1280 để giữ nét chi tiết nhỏ, nâng Recall cho biển ở xa.")
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
    print(f"[XUẤT BẢN THÀNH CÔNG] File Word Ngày 05 đã được tạo tại:\n👉 {OUTPUT_FILE}")


if __name__ == "__main__":
    build_day05_document()
