"""
Script xuất bản bài học Ngày 03 thành file Word (.docx) chuyên nghiệp
Lưu trữ vào thư mục: roadmap AI/Ngay_03_Chien_Luoc_Mau_Am_Tinh_Tri_Bao_Dong_Gia.docx
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
OUTPUT_FILE = str(OUTPUT_DIR / "Ngay_03_Chien_Luoc_Mau_Am_Tinh_Tri_Bao_Dong_Gia.docx")

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


def build_day03_document():
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
    r_day = p_main.add_run("NGÀY 03: CHIẾN LƯỢC MẪU ÂM TÍNH (NEGATIVE / BACKGROUND SAMPLES)\nBÍ QUYẾT TRIỆT TIÊU BÁO ĐỘNG GIẢ TRÊN VỈA HÈ\n")
    r_day.font.name = "Arial"
    r_day.font.size = Pt(16)
    r_day.font.bold = True
    r_day.font.color.rgb = COLOR_PRIMARY
    
    r_sub = p_main.add_run("Bản chất toán học của Background Loss, quy tắc nhãn 0 bytes và tỷ lệ vàng 5%–10%")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_SECONDARY

    # Bảng Metadata
    tbl_meta = doc.add_table(rows=4, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_rows = [
        ("Phân hệ phụ trách:", "Track A — AI & Dữ liệu (Dataset Engineering & False Alarm Mitigation)"),
        ("Mã nguồn liên quan:", "datasets/clean_dataset.py, ke-hoach-do-an-tot-nghiep.md, datasets/v8/"),
        ("Kỹ thuật trọng tâm:", "Background Images (Empty Label 0 Bytes), Classification Loss Penalty"),
        ("Mục tiêu ngày 03:", "Nắm vững cơ chế phạt Loss của mẫu âm tính, triệt tiêu báo động giả vào bóng cây, nắp cống.")
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
    
    add_subsection_header(doc, "1. Ẩn dụ bác sĩ thực tập và phim X-quang gãy xương")
    add_body_paragraph(
        doc,
        "Hãy tưởng tượng một bác sĩ thực tập chuyên khoa chấn thương chỉnh hình. Trong suốt thời gian theo học tại trường y, "
        "các giáo sư chỉ toàn phát cho anh ta xem đúng những tấm phim X-quang của những bệnh nhân chắc chắn bị gãy xương. "
        "Anh ta chưa từng một lần nào được xem tấm phim X-quang của một người khỏe mạnh bình thường.\n"
        "Khi bước ra bệnh viện công tác thực tế, điều gì sẽ xảy ra?\n"
        "Bất kỳ người bệnh nào vào chụp X-quang, anh bác sĩ này cũng sẽ 'vạch lá tìm sâu', nhìn một vệt gân xương mờ mờ hay một nếp gấp "
        "tự nhiên của cơ thể cũng run rẩy phán ngay: 'Bác bị rạn xương rồi!' -> Đây chính là hiện tượng Báo động giả (False Positive)!\n"
        "Ngược lại, nếu ngay từ đầu anh ta được quan sát hàng trăm tấm phim X-quang của người khỏe mạnh, anh ta sẽ tự tin nói: "
        "'À, vệt mờ này là cấu trúc xương bình thường, hoàn toàn không có bệnh lý!'."
    )
    
    add_subsection_header(doc, "2. Ẩn dụ Chấm điểm bài thi: Hàm mất mát (Loss) = 'Điểm phạt khi làm sai'")
    add_body_paragraph(
        doc,
        "Để hiểu về học máy một cách mộc mạc nhất: Mô hình AI YOLOv8 trong quá trình huấn luyện giống hệt một bạn học sinh đang làm bài thi trắc nghiệm.\n"
        "• Hàm mất mát (Loss) chính là: SỐ ĐIỂM BỊ THẦY GIÁO PHẠT VÌ LÀM SAI BÀI TẬP.\n"
        "• Mục tiêu của AI khi đi học là làm sao để bị phạt ít điểm nhất có thể (Loss càng nhỏ càng tốt, tiến dần về 0).\n"
        "• Ở dạng bài tập 'Ảnh vỉa hè trống trơn không có biển': Đề bài đưa ra một vỉa hè chỉ có gạch lát, bóng cây và nắp cống. "
        "Tờ đáp án chuẩn (Ground Truth) là MỘT TỜ GIẤY TRẮNG TINH (Không vẽ cái hộp nào cả)!\n"
        "• Nếu học sinh AI ngứa tay vẽ một cái hộp bao quanh cái nắp cống hay bóng cây rồi la lên: 'Em tìm thấy biển hiệu ở đây nè!', "
        "thầy giáo sẽ phạt điểm tối đa: 'Đã bảo là không có biển mà dám vẽ bậy à!'. "
        "Sau nhiều lần bị trừ điểm nặng, AI sẽ học được bài học đắt giá: Gặp bóng cây hay nắp cống thì tốt nhất là ngồi im, không được vẽ bừa!"
    )

    # =========================================================================
    # PHẦN 2: MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC
    # =========================================================================
    add_section_header(doc, "II", "MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC")
    
    add_subsection_header(doc, "1. Cơ chế toán học của Background Images trong YOLOv8")
    add_body_paragraph(
        doc,
        "Khi một bức ảnh được nạp vào mạng nơ-ron YOLOv8, mạng sẽ quét và sinh ra hàng nghìn hộp dự đoán ứng viên (Candidate Boxes) trên toàn bộ khung hình. "
        "Hàm mất mát tổng thể của YOLOv8 bao gồm 3 thành phần chính:"
    )
    add_body_paragraph(
        doc,
        "               L_total = lambda_box * L_box + lambda_cls * L_cls + lambda_dfl * L_dfl\n\n"
        "1. Với ảnh có biển hiệu (Positive Samples):\n"
        "   • Có nhãn thật (Ground Truth). L_box và L_dfl phạt độ lệch tọa độ giữa hộp dự đoán và hộp nhãn thật.\n"
        "   • L_cls phạt nếu mạng không phát hiện ra lớp 'bien-quang-cao'.\n\n"
        "2. Với ảnh vỉa hè trống (Negative / Background Samples):\n"
        "   • Số lượng nhãn thật bằng 0 (N_gt = 0). Không có hộp nào để đối chiếu vị trí -> L_box = 0 và L_dfl = 0.\n"
        "   • Tuy nhiên, hàm mất mát phân loại nhị phân (Binary Cross-Entropy) L_cls sẽ PHẠT CỰC NẶNG bất kỳ hộp ứng viên nào "
        "dám xuất ra độ tự tin p > 0:\n"
        "               L_cls = - Sum_i [ log(1 - p_i) ]\n"
        "   Để L_cls đạt giá trị nhỏ nhất (tiến về 0), mạng bắt buộc phải điều chỉnh các trọng số nơ-ron để đè bẹp xác suất p_i "
        "của toàn bộ các vùng nền gạch, bóng râm, nắp cống, xe cộ xuống sát 0.0! Nhờ cơ chế này, hiện tượng báo động giả bị triệt tiêu tận gốc."
    )

    add_subsection_header(doc, "2. Định dạng file nhãn chuẩn của Mẫu âm tính: Tệp rỗng 0 Bytes")
    add_body_paragraph(
        doc,
        "Trong định dạng dữ liệu YOLO, mỗi dòng trong file .txt đại diện cho đúng một hộp vật thể (Bounding Box):\n"
        "• Có 1 cái biển -> File .txt có 1 dòng: 0 x_center y_center w h\n"
        "• Có 2 cái biển -> File .txt có 2 dòng.\n"
        "• KHÔNG CÓ CÁI BIỂN NÀO -> File .txt có 0 dòng (Tệp hoàn toàn trống rỗng, kích thước đúng 0 bytes)!"
    )
    
    add_callout_box(
        doc,
        "TẠI SAO TUYỆT ĐỐI KHÔNG ĐƯỢC GHI '0 0 0 0 0' VÀO FILE NHÃN?\n\n"
        "Nhiều người mới học thường nghĩ: 'Số 0 nghĩa là không có gì, vậy em ghi 0 0 0 0 0 vào file txt để báo cho máy tính biết là không có biển'.\n"
        "ĐÂY LÀ MỘT SAI LẦM TỬ HUYỆT VÌ:\n"
        "Mỗi dòng trong nhãn YOLO có cấu trúc: [class_id] [x_center] [y_center] [width] [height].\n"
        "Nếu bạn ghi '0 0 0 0 0', máy tính sẽ hiểu theo đúng cú pháp đại số:\n"
        "• class_id = 0 (Lớp 'bien-quang-cao').\n"
        "• x_center = 0.0, y_center = 0.0 (Tâm nằm ở góc trên cùng bên trái của ảnh).\n"
        "• width = 0.0, height = 0.0 (Kích thước bằng 0).\n"
        "-> Bạn vừa chính thức khai báo với AI rằng: 'Ở góc trên bên trái bức ảnh ĐANG CÓ MỘT TẤM BIỂN HIỆU!'.\n"
        "Mô hình sẽ bị dạy sai lệch hoàn toàn, liên tục sinh ra các hộp ảo ở góc màn hình.\n\n"
        "QUY TẮC BẤT DI BẤT DỊCH: Không có biển = File .txt tồn tại nhưng rỗng hoàn toàn 0 bytes!",
        title="CẢNH BÁO TỬ HUYỆT: TẠI SAO KHÔNG ĐƯỢC GHI '0 0 0 0 0'?",
        box_type="warning"
    )

    add_subsection_header(doc, "3. Tỷ lệ vàng (The Golden Ratio): 5% đến 10%")
    add_body_paragraph(
        doc,
        "Tài liệu chính thức của Ultralytics (tác giả YOLOv8) khuyến nghị tỷ lệ mẫu âm tính tối ưu là từ 5% đến 10% tổng số ảnh trong tập dữ liệu. "
        "Ý nghĩa thực tiễn của tỷ lệ này được phân tích qua bảng so sánh dưới đây:"
    )
    
    # Bảng Golden Ratio
    tbl_ratio = doc.add_table(rows=4, cols=3)
    tbl_ratio.alignment = WD_TABLE_ALIGNMENT.CENTER
    ratio_data = [
        ("Tỷ lệ Background", "Hiện tượng xảy ra trên Mô hình AI", "Đánh giá chất lượng thực tế"),
        ("0% (Không có ảnh nền)", "Mô hình bị định kiến: 'Cứ có ảnh là phải có biển'. Ra đường phố thật nhìn đâu cũng thấy biển (bắt nhầm nắp cống, bóng cây, xe máy).", "NGUY HIỂM\n(Báo động giả FP rất cao, hệ thống không dùng được)."),
        ("5% – 10% (Tỷ lệ vàng)", "AI học được sự thận trọng cần thiết: Phân biệt rõ đâu là mặt đường bình thường, đâu là biển hiệu thật. Không bắt bừa vào bóng cây nhưng vẫn bắt trọn biển.", "HOÀN HẢO\n(Cân bằng tối ưu giữa Precision và Recall)."),
        ("> 20% – 30% (Quá nhiều nền)", "AI bị 'sợ phạt quá mức'. Mô hình trở nên cực kỳ nhút nhát, gặp biển thật ở xa hoặc hơi mờ cũng không dám phát hiện vì sợ bị phạt điểm.", "KÉM\n(Bỏ sót vi phạm FN tăng vọt, Recall sụt giảm nghiêm trọng).")
    ]
    for i, row in enumerate(ratio_data):
        for j, text in enumerate(row):
            c = tbl_ratio.cell(i, j)
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
    set_table_borders(tbl_ratio, HEX_BORDER)
    doc.add_paragraph()

    # =========================================================================
    # PHẦN 3: HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN DỰ ÁN
    # =========================================================================
    add_section_header(doc, "III", "HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN DỰ ÁN")
    
    add_subsection_header(doc, "1. Ghi nhận kỹ thuật trong ke-hoach-do-an-tot-nghiep.md")
    add_body_paragraph(
        doc,
        "Trong tài liệu kế hoạch đồ án ke-hoach-do-an-tot-nghiep.md tại Mục B.2 (Thách thức & Hướng giải quyết kỹ thuật), "
        "giải pháp bổ sung mẫu nền âm tính đã được xác định là trụ cột để hệ thống giám sát 24/7 ổn định ngoài hiện trường:"
    )
    add_callout_box(
        doc,
        "'Thách thức ánh sáng ngày / đêm, bóng đổ cây cối, đèn xe quét qua:\n"
        "Hướng xử lý trong hệ thống: Tăng cường dữ liệu (Mosaic, Blur, CLAHE, HSV); bổ sung mẫu nền âm tính (Background samples) "
        "để triệt tiêu các báo động giả xuất phát từ biến thiên ánh sáng môi trường.'",
        title="TRÍCH DẪN TÀI LIỆU KỸ THUẬT ĐATN20224083",
        box_type="info"
    )

    add_subsection_header(doc, "2. Script Python kiểm tra tự động tỷ lệ mẫu âm tính trong Dataset")
    add_body_paragraph(
        doc,
        "Để kiểm tra xem tập dữ liệu hiện tại có bao nhiêu file nhãn rỗng 0 bytes, hãy chạy đoạn mã sau:"
    )
    code_check_bg = (
        "import os\n"
        "\n"
        "def audit_background_samples(label_dir='datasets/v8/train/labels'):\n"
        "    if not os.path.exists(label_dir):\n"
        "        print(f'[!] Thư mục không tồn tại: {label_dir}')\n"
        "        return\n"
        "        \n"
        "    txt_files = [f for f in os.listdir(label_dir) if f.endswith('.txt')]\n"
        "    empty_files = [f for f in txt_files if os.path.getsize(os.path.join(label_dir, f)) == 0]\n"
        "    \n"
        "    total = len(txt_files)\n"
        "    num_empty = len(empty_files)\n"
        "    pct = (num_empty / total * 100) if total > 0 else 0.0\n"
        "    \n"
        "    print('=' * 55)\n"
        "    print('BÁO CÁO KIỂM TOÁN MẪU ÂM TÍNH (BACKGROUND SAMPLES)')\n"
        "    print('=' * 55)\n"
        "    print(f'[+] Tổng số file nhãn kiểm tra  : {total}')\n"
        "    print(f'[+] Số file mẫu âm tính (0 bytes): {num_empty}')\n"
        "    print(f'[+] Tỷ lệ mẫu âm tính đạt được   : {pct:.2f}%')\n"
        "    \n"
        "    if 5.0 <= pct <= 10.0:\n"
        "        print('[V] ĐÁNH GIÁ: Tỷ lệ đạt chuẩn vàng (5% - 10%) của Ultralytics!')\n"
        "    elif pct < 5.0:\n"
        "        print('[!] CẢNH BÁO: Tỷ lệ quá thấp! Cần bổ sung thêm ảnh vỉa hè trống.')\n"
        "    else:\n"
        "        print('[!] CẢNH BÁO: Tỷ lệ quá cao! Có thể làm giảm Recall của mô hình.')\n"
        "    print('=' * 55)"
    )
    add_code_block(doc, code_check_bg)

    # =========================================================================
    # PHẦN 4: SẢN PHẨM BÀN GIAO & CÁCH TỰ KIỂM TRA
    # =========================================================================
    add_section_header(doc, "IV", "SẢN PHẨM BÀN GIAO & TIÊU CHÍ TỰ KIỂM TRA")
    
    tbl_eval = doc.add_table(rows=4, cols=3)
    tbl_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
    eval_data = [
        ("STT", "Tiêu chuẩn đánh giá", "Kết quả nghiệm thu của sinh viên"),
        ("01", "Hiểu bản chất toán học của Background Loss.", "Giải thích được vì sao N_gt=0 thì L_box=0 và L_cls phạt tối đa."),
        ("02", "Hiểu quy chuẩn file nhãn 0 bytes.", "Biết chính xác không được xóa file txt và không được ghi '0 0 0 0 0'."),
        ("03", "Kế hoạch thu thập mẫu âm tính ngoài đời.", "Chuẩn bị sẵn 30–50 ảnh vỉa hè trống (có bóng cây, xe máy, người đi bộ).")
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
    
    add_subsection_header(doc, "CÂU HỎI 1: Bẫy gõ '0 0 0 0 0' vào file nhãn rỗng")
    add_body_paragraph(
        doc,
        "Thầy/Cô Hội đồng hỏi: 'Nếu một thành viên trong nhóm gõ dòng chữ 0 0 0 0 0 vào file nhãn của ảnh vỉa hè trống với suy nghĩ "
        "số 0 đại diện cho việc không có biển, thì mô hình YOLOv8 khi huấn luyện sẽ hiểu bức ảnh đó như thế nào?'"
    )
    add_callout_box(
        doc,
        "ĐÁP ÁN PHẢN BIỆN CHUẨN XÁC:\n"
        "• Theo định dạng chuẩn của YOLO: Mỗi dòng trong file txt là một Bounding Box gồm 5 tham số: class_id, x_center, y_center, width, height.\n"
        "• Khi gõ 0 0 0 0 0, trình đọc nhãn của YOLO sẽ phân giải thành: Có 1 vật thể thuộc class_id 0 (bien-quang-cao), tọa độ tâm x=0, y=0 (góc trên cùng bên trái ảnh) và kích thước w=0, h=0.\n"
        "• Hậu quả: Chúng ta vừa vô tình khẳng định với mô hình rằng ở góc trên bên trái khung hình đang tồn tại một tấm biển quảng cáo! Mô hình sẽ bị học sai lệch, liên tục sinh ra các hộp ảo ở góc màn hình và làm hỏng hoàn toàn độ chính xác.\n"
        "• Chuẩn kỹ thuật bắt buộc: Mẫu âm tính phải là file txt tồn tại nhưng có kích thước đúng 0 bytes (không chứa bất kỳ ký tự nào).",
        title="KỊCH BẢN PHẢN BIỆN CÂU HỎI 1",
        box_type="info"
    )

    add_subsection_header(doc, "CÂU HỎI 2: Phòng vệ trước bóng cây ban ngày và vệt đèn pha xe máy ban đêm")
    add_body_paragraph(
        doc,
        "Thầy/Cô Hội đồng hỏi: 'Camera CCTV hoạt động 24/7 ngoài đường phố. Ban ngày nắng gắt, bóng cây râm mát in hình chữ nhật xuống vỉa hè; "
        "hoặc ban đêm đèn pha xe máy quét qua tạo vệt sáng hình hộp trên mặt đường. Làm sao em chứng minh được AI không bắt nhầm các vệt này?'"
    )
    add_callout_box(
        doc,
        "KỊCH BẢN TRẢ LỜI ĐẠT ĐIỂM XUẤT SẮC TRƯỚC HỘI ĐỒNG:\n"
        "Dạ thưa Thầy/Cô, hệ thống của nhóm em triệt tiêu triệt để hiện tượng này nhờ 2 tầng phòng ngự phối hợp giữa Track A và Track B:\n\n"
        "1. Tầng Dữ liệu & AI (Track A - Phòng ngừa chủ động):\n"
        "   Khi xây dựng dataset, em chủ động đưa vào 5% – 10% Mẫu âm tính (Background Samples) chụp lại chính xác các bối cảnh vỉa hè trống dưới điều kiện nắng gắt có bóng cây rung rinh và vệt sáng đèn xe ban đêm (kèm file nhãn rỗng 0 bytes). Hàm mất mát phân loại BCE Loss đã ép mô hình học cách triệt tiêu xác suất của các đốm sáng và bóng râm này về sát 0.0.\n\n"
        "2. Tầng Thời gian & Hình học (Track B - Chốt chặn kiên cố):\n"
        "   Trong trường hợp hiếm hoi có một vệt sáng bị AI bắt nhầm ở 1 frame đơn lẻ (False Positive tạm thời):\n"
        "   • Vệt đèn xe máy di chuyển liên tục sẽ bị Bộ lọc đứng yên (Stationary Displacement Check) loại bỏ ngay lập tức.\n"
        "   • Bóng cây rung rinh theo gió sẽ bị biến dạng tọa độ, không thể duy trì ổn định liên tục đủ 15 frames (~3.0 giây) để thỏa mãn điều kiện xác nhận vi phạm (Temporal Verifier).\n"
        "-> Nhờ sự phối hợp chặt chẽ giữa 2 tầng, hệ thống hoàn toàn miễn nhiễm với nhiễu ánh sáng môi trường.",
        title="KỊCH BẢN PHẢN BIỆN CÂU HỎI 2 (HỘI ĐỒNG)",
        box_type="success"
    )

    # =========================================================================
    # PHẦN 6: BẢN GHI NHỚ CỐT LÕI (KEY TAKEAWAYS)
    # =========================================================================
    add_section_header(doc, "VI", "BẢN GHI NHỚ CỐT LÕI NGÀY 03 (KEY TAKEAWAYS)")
    
    tbl_sum = doc.add_table(rows=5, cols=2)
    tbl_sum.alignment = WD_TABLE_ALIGNMENT.CENTER
    sum_data = [
        ("Khái niệm cốt lõi", "Quy tắc bắt buộc phải thuộc lòng"),
        ("Mẫu âm tính (Negative)", "Là ảnh vỉa hè trống trơn, hoàn toàn không có biển quảng cáo nào."),
        ("Quy cách file nhãn", "File .txt cùng tên với ảnh, tồn tại trong thư mục nhưng RỖNG HOÀN TOÀN (0 bytes)."),
        ("Sai lầm cấm kỵ", "Không được ghi '0 0 0 0 0' (sẽ tạo ra box ảo ở góc 0,0)."),
        ("Tỷ lệ vàng Ultralytics", "5% – 10% tổng số ảnh. Dưới 5% thì báo giả cao, trên 20% thì AI bị nhút nhát bỏ sót biển.")
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
    print(f"[XUẤT BẢN THÀNH CÔNG] File Word Ngày 03 đã được tạo tại:\n👉 {OUTPUT_FILE}")


if __name__ == "__main__":
    build_day03_document()
