"""
Script xuất bản bài học Ngày 02 thành file Word (.docx) chuyên nghiệp
Lưu trữ vào thư mục: roadmap AI/Ngay_02_Dinh_Nghia_Bai_Toan_Du_Lieu_Va_Phan_Loai_Doi_Tuong.docx
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
OUTPUT_FILE = str(OUTPUT_DIR / "Ngay_02_Dinh_Nghia_Bai_Toan_Du_Lieu_Va_Phan_Loai_Doi_Tuong.docx")

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


def build_day02_document():
    doc = Document()
    
    # Lề trang tiêu chuẩn
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
    r_day = p_main.add_run("NGÀY 02: ĐỊNH NGHĨA BÀI TOÁN DỮ LIỆU & PHÂN LOẠI\nĐỐI TƯỢNG BIỂN HIỆU CẦN NHẬN DIỆN\n")
    r_day.font.name = "Arial"
    r_day.font.size = Pt(16)
    r_day.font.bold = True
    r_day.font.color.rgb = COLOR_PRIMARY
    
    r_sub = p_main.add_run("Xây dựng Bộ quy chuẩn nhận diện (Taxonomy Rubric) chuẩn xác để tránh bẫy báo động giả")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_SECONDARY

    # Bảng Metadata
    tbl_meta = doc.add_table(rows=4, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_rows = [
        ("Phân hệ phụ trách:", "Track A — AI & Dữ liệu (Dataset Engineering & Annotation Standards)"),
        ("Mã nguồn liên quan:", "datasets/v8/data.yaml, detection/detector.py, datasets/validate_dataset.py"),
        ("Kiến trúc phân loại:", "Single-Class Object Detection (nc: 1, class duy nhất: 'bien-quang-cao')"),
        ("Mục tiêu ngày 02:", "Nắm vững danh mục Positive, Hard Negative và Edge Cases để dán nhãn chuẩn 100%.")
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
    
    add_subsection_header(doc, "1. Ẩn dụ bác bảo vệ cổng trường mới nhận việc")
    add_body_paragraph(
        doc,
        "Hãy tưởng tượng một bác bảo vệ mới đến làm việc tại trường đại học. Hiệu trưởng giao nhiệm vụ: "
        "'Bác đứng ở cổng, thấy ai là người ngoài trường vào bán hàng rong thì chặn lại nhé!'.\n"
        "Nếu bác bảo vệ chỉ được dặn chung chung: 'Cứ ai mang đồ cồng kềnh là người bán hàng rong', thì bác sẽ chặn nhầm cả bạn sinh viên "
        "đang mang đàn guitar đi tập văn nghệ, bác giảng viên xách cặp lồng cơm, hoặc anh nhân viên bưu điện giao thư tín!\n"
        "Nhưng nếu bác bảo vệ được dặn dò với tiêu chí rõ ràng:\n"
        "• Dấu hiệu cần chặn: Người đẩy xe nước mía, người xách mẹt hoa quả, người gánh hàng rong chiếm dụng lối đi chung.\n"
        "• Dấu hiệu loại trừ: Sinh viên có đeo thẻ, giảng viên, người đi bộ đi thẳng qua cổng trường không dừng lại."
    )
    add_body_paragraph(
        doc,
        "Mô hình học sâu YOLOv8 thực chất là một 'bác bảo vệ' cực kỳ chăm chỉ nhưng hoàn toàn ngây thơ. "
        "Nếu người kỹ sư dữ liệu không định nghĩa sắc bén những gì cần bắt và những gì cần bỏ qua, "
        "AI sẽ bắt nhầm mọi thứ có chữ trên đường: từ cái áo phông in chữ của người đi bộ, biển số xe máy, "
        "đến tờ rơi dán trên cột điện hay ô dù che nắng quán nước!"
    )

    # =========================================================================
    # PHẦN 2: MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC
    # =========================================================================
    add_section_header(doc, "II", "MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC")
    
    add_subsection_header(doc, "1. Chiến lược Single-Class: Tại sao đồ án dùng duy nhất 1 lớp (nc: 1)?")
    add_body_paragraph(
        doc,
        "Trong file cấu hình datasets/v8/data.yaml, số lượng lớp được thiết lập là nc: 1 với tên lớp duy nhất là 'bien-quang-cao'. "
        "Tại sao chúng ta không chia nhỏ thành: standee_chu_A, bien_hop_den, bien_chan_sat, bien_menu? "
        "Quyết định này dựa trên 3 căn cứ khoa học và kỹ thuật vững chắc:"
    )
    add_body_paragraph(
        doc,
        "1. Căn cứ Pháp lý & Thực tiễn nghiệp vụ:\n"
        "   Theo Điều 12 Nghị định 168/2024/NĐ-CP của Chính phủ, hành vi bị chế tài xử phạt là 'đặt, treo biển hiệu, biển quảng cáo "
        "trên lòng đường, hè phố trái quy định'. Luật pháp bảo vệ không gian đi bộ và mỹ quan đô thị, không phân biệt biển làm bằng "
        "bạt Hiflex, đèn LED hay khung sắt. Chia nhiều lớp không mang lại giá trị thực tế cho cán bộ xử lý vi phạm.\n\n"
        "2. Căn cứ Toán học hàm mất mát (Classification Loss):\n"
        "   Khi nc = 1, bài toán chuyển từ phân loại đa lớp (Categorical Softmax Cross-Entropy) sang phân loại nhị phân "
        "Binary Cross-Entropy (BCE Loss):\n"
        "               L_cls = - [ y * log(p) + (1 - y) * log(1 - p) ]\n"
        "   Trong đó y thuộc {0, 1} là nhãn thực tế và p là xác suất dự đoán. Mạng chỉ cần ước lượng xác suất đối tượng có phải là biển hay không, "
        "giúp giảm bớt tính toán và hội tụ nhanh hơn gấp nhiều lần.\n\n"
        "3. Tối ưu hóa tính toán cho CPU thiết bị biên & Triệt tiêu nhầm lẫn nội bộ (Inter-class Confusion):\n"
        "   Số lượng tham số tại lớp dự đoán cuối cùng (Head) tỉ lệ thuận với số lượng class. Giảm về 1 class giúp tiết kiệm RAM và giảm FLOPs. "
        "Đặc biệt, nó loại trừ hoàn toàn hiện tượng 'phân vân' của mô hình khi gặp một tấm biển lai (vừa có đèn vừa có khung sắt chữ A), "
        "giúp điểm tự tin (Confidence score) và chỉ số mAP50 luôn đạt mức tối đa."
    )

    add_subsection_header(doc, "2. Bảng quy chuẩn phân loại đối tượng chuẩn (Taxonomy Rubric)")
    add_body_paragraph(
        doc,
        "Dưới đây là bộ quy chuẩn phân loại vàng mà Kỹ sư dữ liệu Track A bắt buộc phải tuân thủ nghiêm ngặt:"
    )
    
    # Bảng Taxonomy
    tbl_tax = doc.add_table(rows=6, cols=3)
    tbl_tax.alignment = WD_TABLE_ALIGNMENT.CENTER
    tax_data = [
        ("Phân nhóm đối tượng", "Các trường hợp thực tế ngoài đường phố", "Quy tắc gán nhãn của Track A"),
        ("BẮT BUỘC NHẬN DIỆN\n(Positive Samples)", "• Biển standee khung sắt chữ A, chữ X.\n• Biển hộp đèn đứng độc lập có chân đế.\n• Biển bảng đen phấn viết menu của quán ăn/cafe.\n• Biển bạt đứng dựng tạm trên hè phố.", "GÁN NHÃN: bien-quang-cao\n(Kéo Bounding Box ôm trọn thân biển và chân đế chạm đất)."),
        ("TUYỆT ĐỐI BỎ QUA\n(Hard Negative)", "• Biển hiệu lớn gắn cố định trên tường nhà, gắn trên mái hiên công trình xây dựng.\n• Biển số nhà, biển tên ngõ phố.", "BỎ QUA (KHÔNG GÁN)\n(Biển gắn tường hợp pháp, không chiếm dụng mặt bằng vỉa hè)."),
        ("TUYỆT ĐỐI BỎ QUA\n(Hard Negative)", "• Áp phích, tờ rơi dán phẳng trên cột điện, tường nhà (quảng cáo khoan cắt bê tông, tuyển dụng).", "BỎ QUA (KHÔNG GÁN)\n(Mặt phẳng 2D không có chân đế tiếp xúc mặt đất)."),
        ("TUYỆT ĐỐI BỎ QUA\n(Hard Negative)", "• Xe đẩy bán hàng rong, xe nước mía, xe bánh mì.\n• Ô dù che nắng cỡ lớn có in logo thương hiệu nước ngọt.", "BỎ QUA (KHÔNG GÁN)\n(Đây là phương tiện/thiết bị che chắn, không phải biển hiệu độc lập)."),
        ("TRƯỜNG HỢP ĐẶC BIỆT\n(Edge Case)", "• Người đi bộ đang bưng/vác tấm biển quảng cáo đi ngang qua vỉa hè.", "VẪN GÁN NHÃN: bien-quang-cao\n(Về thị giác nó là tấm biển. Việc lọc người di chuyển do Temporal Verifier của Track B xử lý).")
    ]
    for i, row in enumerate(tax_data):
        for j, text in enumerate(row):
            c = tbl_tax.cell(i, j)
            c.width = Inches(1.8) if j == 0 else (Inches(2.5) if j == 1 else Inches(2.2))
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
    set_table_borders(tbl_tax, HEX_BORDER)
    doc.add_paragraph()

    # =========================================================================
    # PHẦN 3: HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN DỰ ÁN
    # =========================================================================
    add_section_header(doc, "III", "HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN DỰ ÁN")
    
    add_subsection_header(doc, "1. Kiểm tra cấu hình trong datasets/v8/data.yaml")
    add_body_paragraph(
        doc,
        "Hãy mở file datasets/v8/data.yaml trong thư mục dự án. Cấu trúc định nghĩa dữ liệu hiển thị như sau:"
    )
    code_yaml = (
        "# Nội dung datasets/v8/data.yaml\n"
        "names:\n"
        "- bien-quang-cao\n"
        "nc: 1\n"
        "train: ../train/images\n"
        "val: ../valid/images\n"
        "test: ../test/images\n"
        "roboflow:\n"
        "  project: sidewalk-signboard-detection-1\n"
        "  version: 8"
    )
    add_code_block(doc, code_yaml)

    add_subsection_header(doc, "2. Kiểm tra tính toàn vẹn của nhãn bằng datasets/validate_dataset.py")
    add_body_paragraph(
        doc,
        "Để đảm bảo không có file nhãn nào bị dán nhầm sang class_id khác 0, hãy chạy script kiểm thử tự động:"
    )
    code_val_cmd = (
        "# Kích hoạt môi trường và kiểm tra cấu trúc dataset\n"
        ".venv\\Scripts\\activate\n"
        "python datasets/validate_dataset.py"
    )
    add_code_block(doc, code_val_cmd)
    add_body_paragraph(
        doc,
        "Script sẽ duyệt toàn bộ các thư mục train, valid, test; đếm số lượng file ảnh (.jpg) và file nhãn (.txt), "
        "đảm bảo tỷ lệ ghép cặp đạt 100% và không có class rác nằm ngoài danh mục."
    )

    # =========================================================================
    # PHẦN 4: SẢN PHẨM BÀN GIAO & CÁCH TỰ KIỂM TRA
    # =========================================================================
    add_section_header(doc, "IV", "SẢN PHẨM BÀN GIAO & TIÊU CHÍ TỰ KIỂM TRA")
    
    tbl_eval = doc.add_table(rows=3, cols=3)
    tbl_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
    eval_data = [
        ("STT", "Tiêu chuẩn đánh giá", "Kết quả nghiệm thu của sinh viên"),
        ("01", "Nắm chắc quy chuẩn phân biệt Positive vs Hard Negative.", "Tự tin chỉ ra các vật thể cần bắt và cần loại bỏ trên ảnh phố thực tế."),
        ("02", "Chạy thành công datasets/validate_dataset.py.", "Màn hình console báo cáo 100% nhãn hợp lệ, nc: 1, không có lỗi phân giải.")
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
    
    add_subsection_header(doc, "CÂU HỎI 1: Xử lý tình huống người vác biển đi ngang vỉa hè")
    add_body_paragraph(
        doc,
        "Thầy/Cô Hội đồng hỏi: 'Tại sao khi một người đi bộ vác tấm biển quảng cáo đi ngang qua vỉa hè, "
        "mô hình AI của em vẫn phát hiện nó là biển hiệu mà không tìm cách loại trừ ngay từ tầng thị giác?'"
    )
    add_callout_box(
        doc,
        "ĐÁP ÁN PHẢN BIỆN CHUẨN XÁC TỪ SINH VIÊN (XUẤT SẮC):\n"
        "• Bản chất thị giác: Mô hình Detector trong từng frame tĩnh chỉ làm nhiệm vụ nhận diện hình thái vật thể. Tấm biển được người vác trên vai về mặt thị giác vẫn mang 100% đặc trưng của một tấm biển quảng cáo. Ép AI phân biệt 'vác' hay 'đặt' trong một khung hình duy nhất là phi khoa học.\n"
        "• Tính linh hoạt trong thực tế: Người bán hàng hoàn toàn có thể đang vác biển và chỉ 5 giây sau họ đặt phịch tấm biển xuống mặt vỉa hè! Khi đó hành vi vi phạm lập tức phát sinh.\n"
        "• Sự phối hợp kiến trúc: Track A phát hiện Bounding Box và bàn giao sang Track B. Module tracking/verifier.py của Track B áp dụng Bộ lọc đứng yên (Stationary Displacement Check, delta_d <= 50px). Khi người vác biển di chuyển liên tục, hệ thống giữ trạng thái SUSPECTED và không hề phát cảnh báo. Khi biển đặt đứng yên đủ 15 frames (~3 giây), hệ thống mới kích hoạt CONFIRMED vi phạm.",
        title="KỊCH BẢN PHẢN BIỆN CÂU HỎI 1 (ĐẠT ĐIỂM TUYỆT ĐỐI)",
        box_type="success"
    )

    add_subsection_header(doc, "CÂU HỎI 2: Nguy cơ phạt oan đối với xe đẩy bán hàng, ô dù có in logo")
    add_body_paragraph(
        doc,
        "Thầy/Cô Hội đồng hỏi: 'Trên vỉa hè có nhiều xe bánh mì gắn biển menu, hoặc ô dù che nắng in logo nhãn hàng. "
        "AI có bắt nhầm không và hệ thống làm thế nào để không lập biên bản phạt oan người dân?'"
    )
    add_callout_box(
        doc,
        "KỊCH BẢN TRẢ LỜI ĐẠT ĐIỂM XUẤT SẮC TRƯỚC HỘI ĐỒNG:\n"
        "Dạ thưa Thầy/Cô, hệ thống của nhóm em giải quyết triệt để nguy cơ này qua 2 tầng bảo vệ:\n\n"
        "1. Tầng Kỹ nghệ Dữ liệu (Track A):\n"
        "   Khi gán nhãn, em tuyệt đối không gán nhãn lên xe đẩy, tủ kính hay ô dù. Mô hình YOLOv8n học được đặc trưng hình thái học (Morphology): biển quảng cáo là dạng phẳng/hộp chữ nhật tự đứng có chân cắm, khác biệt hoàn toàn với kết cấu cơ khí của xe đẩy hay tán tròn của ô dù.\n\n"
        "2. Tầng Nghiệp vụ & Pháp lý (Human-in-the-Loop Decision Support System):\n"
        "   Đồ án định vị đây là Hệ thống Hỗ trợ Ra Quyết định, không tự động phạt máy móc. Khi phát hiện nghi vấn, hệ thống trích xuất ảnh toàn cảnh có đóng mộc thời gian và ảnh crop cận cảnh gửi về Web Dashboard. Cán bộ Đội Quản lý Trật tự Đô thị là người xem xét trực quan và có thẩm quyền bấm nút 'Phê duyệt' hoặc 'Bác bỏ' (kèm ghi nhận lý do kiểm toán). Nhờ đó, rủi ro phạt oan người dân được triệt tiêu 100%.",
        title="KỊCH BẢN PHẢN BIỆN CÂU HỎI 2 (HỘI ĐỒNG)",
        box_type="warning"
    )

    # =========================================================================
    # PHẦN 6: BẢN GHI NHỚ CỐT LÕI (KEY TAKEAWAYS)
    # =========================================================================
    add_section_header(doc, "VI", "BẢN GHI NHỚ CỐT LÕI NGÀY 02 (KEY TAKEAWAYS)")
    
    tbl_sum = doc.add_table(rows=5, cols=2)
    tbl_sum.alignment = WD_TABLE_ALIGNMENT.CENTER
    sum_data = [
        ("Nội dung cốt lõi", "Quy tắc bắt buộc phải nhớ"),
        ("Cấu hình class", "Duy nhất 1 class (nc: 1, 'bien-quang-cao'). Tối ưu hàm mất mát BCE, tiết kiệm RAM/CPU biên."),
        ("Positive (Phải gán)", "Standee chữ A, hộp đèn đứng, bảng đen menu, standee cuốn tự đứng trên vỉa hè."),
        ("Hard Negative (Bỏ qua)", "Biển gắn tường nhà, áp phích cột điện, xe đẩy hàng rong, ô dù che nắng."),
        ("Triết lý hệ thống", "AI phát hiện vật thể tĩnh (Track A) -> Bộ lọc thời gian khử di động (Track B) -> Cán bộ duyệt (Dashboard).")
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
    print(f"[XUẤT BẢN THÀNH CÔNG] File Word Ngày 02 đã được tạo tại:\n👉 {OUTPUT_FILE}")


if __name__ == "__main__":
    build_day02_document()
