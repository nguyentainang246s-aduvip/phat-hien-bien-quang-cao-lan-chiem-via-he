"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Script xuất Báo cáo tiến độ Tuần 12 - 13 (BẢN CẬP NHẬT CHÍNH THỨC) ra file .docx
Chủ đề: Hoàn thiện Pipeline Phát Hiện, Theo Dõi, Xác Nhận Vi Phạm và Quản Lý Dữ Liệu CCTV
Đối chiếu với Đề cương ĐATN chính thức (Biểu đồ 17 tuần)
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
PRIMARY_FILE = str(OUTPUT_DIR / "Bao_cao_tien_do_Tuan_12_13_DATN_20224083_ban_cap_nhat.docx")
FALLBACK_FILE = str(OUTPUT_DIR / "Bao_cao_tien_do_Tuan_12_13_DATN_20224083_v2.docx")

# Bảng màu chuẩn ĐHBK Hà Nội (HUST Navy, Teal, Slate)
COLOR_PRIMARY = RGBColor(30, 58, 138)     # Navy #1E3A8A
COLOR_SECONDARY = RGBColor(15, 118, 110)  # Teal #0F766E
COLOR_DARK = RGBColor(30, 41, 59)         # Slate Dark #1E293B
COLOR_MUTED = RGBColor(100, 116, 139)     # Slate Gray #64748B
COLOR_RED = RGBColor(220, 38, 38)         # Red #DC2626
COLOR_GREEN = RGBColor(16, 185, 129)      # Emerald Green #10B981
COLOR_AMBER = RGBColor(217, 119, 6)       # Amber #D97706

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
HEX_ALERT_AMBER_BG = "FFFBEB"
HEX_ALERT_AMBER_BORDER = "F59E0B"


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
    elif box_type == "amber":
        bg_color, border_color = HEX_ALERT_AMBER_BG, HEX_ALERT_AMBER_BORDER
        title_color = COLOR_AMBER
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
    
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(4)


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
        p_cap.paragraph_format.space_after = Pt(2)
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
        r_src = p_src.add_run(f"📍 Tệp nguồn: {asset_path}")
        r_src.font.name = "Consolas"
        r_src.font.size = Pt(8.0)
        r_src.font.color.rgb = COLOR_MUTED


def style_section_heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(5)
    h.paragraph_format.keep_with_next = True
    r = h.runs[0]
    r.font.name = "Arial"
    if level == 1:
        r.font.size = Pt(13.0)
        r.font.bold = True
        r.font.color.rgb = COLOR_PRIMARY
    elif level == 2:
        r.font.size = Pt(11.0)
        r.font.bold = True
        r.font.color.rgb = COLOR_SECONDARY
    else:
        r.font.size = Pt(10.0)
        r.font.bold = True
        r.font.color.rgb = COLOR_DARK
    return h


def add_body_paragraph(doc, text, bold_prefix=None, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_bp = p.add_run(bold_prefix)
        r_bp.font.name = "Arial"
        r_bp.font.size = Pt(9.5)
        r_bp.font.bold = True
        r_bp.font.color.rgb = COLOR_DARK
    r_text = p.add_run(text)
    r_text.font.name = "Arial"
    r_text.font.size = Pt(9.5)
    r_text.font.color.rgb = COLOR_DARK
    return p


def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
    
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="12" w:space="0" w:color="94A3B8"/>'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'</w:tcBorders>'
    )
    cell._tc.get_or_add_tcPr().append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(30, 41, 59)
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)


def build_tuan_12_13_ban_cap_nhat_report():
    doc = Document()
    
    # Cấu hình lề trang chuẩn A4
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.8)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        
        # Header & Footer
        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_hdr = p_hdr.add_run("ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU LẤN CHIẾM VỈA HÈ QUA CCTV | BÁO CÁO TIẾN ĐỘ TUẦN 12–13")
        r_hdr.font.name = "Arial"
        r_hdr.font.size = Pt(8.0)
        r_hdr.font.color.rgb = COLOR_MUTED
        
        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_ftr = p_ftr.add_run("Đại học Bách Khoa Hà Nội — Sinh viên thực hiện: Nguyễn Đức Tài Năng (MSSV: 20224083)")
        r_ftr.font.name = "Arial"
        r_ftr.font.size = Pt(8.0)
        r_ftr.font.color.rgb = COLOR_MUTED

    # =========================================================================
    # TIÊU ĐỀ BÁO CÁO
    # =========================================================================
    title = doc.add_heading("BÁO CÁO TIẾN ĐỘ ĐỒ ÁN TỐT NGHIỆP", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_before = Pt(0)
    title.paragraph_format.space_after = Pt(2)
    title.runs[0].font.name = "Arial"
    title.runs[0].font.size = Pt(16.5)
    title.runs[0].font.bold = True
    title.runs[0].font.color.rgb = COLOR_PRIMARY

    sub_title = doc.add_paragraph()
    sub_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_title.paragraph_format.space_before = Pt(0)
    sub_title.paragraph_format.space_after = Pt(8)
    sub_run = sub_title.add_run(
        "GIAI ĐOẠN: TUẦN 12 – TUẦN 13 (KẾ HOẠCH 17 TUẦN ĐỀ CƯƠNG ĐATN)\n"
        "CHỦ ĐỀ: HOÀN THIỆN PIPELINE PHÁT HIỆN, THEO DÕI, XÁC NHẬN VI PHẠM VÀ QUẢN LÝ DỮ LIỆU CCTV\n"
        "NGHIỆM THU TIÊU CHÍ CỐT LÕI: PIPELINE DETECT – TRACK – XÁC NHẬN VI PHẠM – LƯU DB CHẠY TRÊN 1 CAMERA"
    )
    sub_run.font.name = "Arial"
    sub_run.font.size = Pt(10.0)
    sub_run.font.bold = True
    sub_run.font.color.rgb = COLOR_SECONDARY

    # =========================================================================
    # BẢNG THÔNG TIN HÀNH CHÍNH & ĐỐI CHIẾU ĐỀ CƯƠNG
    # =========================================================================
    info_tbl = doc.add_table(rows=6, cols=2)
    info_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(info_tbl)
    
    meta_data = [
        ("Tên đề tài:", "Nghiên cứu và xây dựng hệ thống phát hiện biển hiệu, biển quảng cáo lấn chiếm vỉa hè qua camera giám sát CCTV cố định"),
        ("Sinh viên thực hiện:", "Nguyễn Đức Tài Năng — MSSV: 20224083 — Lớp: Kỹ thuật Máy tính K67\nĐơn vị: Đại học Bách Khoa Hà Nội"),
        ("Thời gian thực hiện:", "Giai đoạn Tuần 12 – Tuần 13 theo biểu đồ tiến độ 17 tuần của Đề cương ĐATN chính thức"),
        ("Mục tiêu tuần 12–13 theo Đề cương:", "1. Hoàn thiện thuật toán xác định vi phạm (tính % giao nhau + ngưỡng).\n2. Tích hợp ByteTrack, xác nhận vi phạm ổn định theo thời gian.\n3. Xây dựng module lưu ảnh bằng chứng.\n4. Xây dựng cơ sở dữ liệu SQLite lưu lịch sử vi phạm.\n5. Xử lý đồng thời nhiều luồng camera, tối ưu hiệu năng."),
        ("Tiêu chí nghiệm thu cốt lõi:", "Pipeline detect – track – xác nhận vi phạm – lưu DB chạy được với 1 camera.\n(Khảo sát và phân định rạch ròi khả năng xử lý đơn camera thực tế với đa camera đồng thời)"),
        ("Trạng thái nghiệm thu:", "• 4/5 Hạng mục hoàn thành xuất sắc 100% kèm bộ unit test tự động (16 passed, 1 skipped) và nhật ký thực thi.\n• 1/5 Hạng mục (Đa luồng đồng thời) đạt mức Một phần (Partial) / Đa camera: Chưa kiểm chứng.\n• Tiêu chí nghiệm thu cốt lõi trên 1 camera: ĐẠT 100% (minh chứng trên Video CCTV Camera 1 Phố Huế / Hàng Bài).")
    ]
    
    for i, (k, v) in enumerate(meta_data):
        row = info_tbl.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width, c1.width = Inches(2.3), Inches(4.2)
        set_cell_margins(c0, 60, 60, 90, 90)
        set_cell_margins(c1, 60, 60, 90, 90)
        set_cell_background(c0, HEX_BG_LIGHT)
        
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.font.name = "Arial"
        r0.font.size = Pt(9.0)
        r0.font.bold = True
        r0.font.color.rgb = COLOR_PRIMARY
        
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.name = "Arial"
        r1.font.size = Pt(9.0)
        r1.font.color.rgb = COLOR_DARK

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

    # =========================================================================
    # TỔNG QUAN TIẾN ĐỘ VÀ TIÊU CHÍ ĐỐI CHIẾU
    # =========================================================================
    style_section_heading(doc, "TỔNG QUAN TIẾN ĐỘ TUẦN 12–13 VÀ TIÊU CHÍ ĐỐI CHIẾU ĐỀ CƯƠNG", level=1)
    
    add_body_paragraph(
        doc,
        "Theo biểu đồ kế hoạch 17 tuần được phê duyệt trong Đề cương Đồ án Tốt nghiệp (ĐATN), giai đoạn Tuần 12–13 là dấu mốc kỹ thuật bản lề chuyển dịch từ mô hình nhận diện thị giác thuần túy (Perception Layer đã hoàn thành ở Tuần 9–11) sang hệ thống giám sát thời gian thực tích hợp toàn diện (End-to-End Edge Surveillance System).",
        bold_prefix="Bối cảnh kỹ thuật: "
    )

    # Thêm Hình 1: Kế hoạch Đề cương
    img_kehoach = str(OUTPUT_DIR / "figures" / "tuan_12_13" / "ke_hoach_tuan_12_13.png")
    add_image_with_caption(
        doc,
        img_kehoach,
        "Hình 1. Trích lục nội dung kế hoạch 5 hạng mục và tiêu chí nghiệm thu Tuần 12–13 từ Đề cương ĐATN chính thức",
        asset_path="Đề cương ĐATN - Biểu đồ kế hoạch thực hiện 17 tuần",
        width=Inches(6.2)
    )

    add_callout_box(
        doc,
        "Nội dung trong biểu đồ kế hoạch Đề cương được dùng làm THƯỚC ĐO ĐỐI CHIẾU (Benchmark Baseline). Theo nguyên tắc liêm chính học thuật, sinh viên tuyệt đối không tự coi nội dung trong kế hoạch là đã hoàn thành mà phải căn cứ vào mã nguồn thực tế, nhật ký kiểm thử độc lập (unit tests) và dữ liệu hồ sơ phát sinh trong CSDL.",
        title="NGUYÊN TẮC LIÊM CHÍNH HỌC THUẬT & ĐỐI CHIẾU",
        box_type="info"
    )

    add_body_paragraph(
        doc,
        "Đề cương ĐATN quy định rõ sản phẩm giao nộp trọng tâm của Tuần 12–13 là: 'Pipeline detect – track – xác nhận vi phạm – lưu DB chạy được với 1 camera'. Đối với hệ thống nhiều camera, đề tài hướng đến tối ưu hóa kiến trúc, đồng thời phân định rạch ròi giữa việc đã chạy hoàn chỉnh trên 1 camera thực tế với năng lực chịu tải đồng thời nhiều luồng camera.",
        bold_prefix="Tiêu chí nghiệm thu cốt lõi: "
    )

    # =========================================================================
    # BẢNG ĐỐI CHIẾU TIẾN ĐỘ 5 HẠNG MỤC CÔNG VIỆC
    # =========================================================================
    style_section_heading(doc, "BẢNG ĐỐI CHIẾU TIẾN ĐỘ 5 HẠNG MỤC CÔNG VIỆC TUẦN 12–13", level=1)
    
    add_body_paragraph(
        doc,
        "Dưới đây là bảng đối chiếu chi tiết 5 hạng mục công việc được giao theo Đề cương, tình trạng đáp ứng thực tế trong mã nguồn, bằng chứng kiểm thử tự động và các vấn đề kỹ thuật còn tồn tại:"
    )

    # Bảng 1: Bảng tổng hợp đối chiếu
    tbl_checklist = doc.add_table(rows=6, cols=6)
    tbl_checklist.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_checklist)
    
    headers_checklist = [
        "STT",
        "Hạng mục công việc\n(Theo Đề cương)",
        "Nội dung kỹ thuật &\nTiêu chí cần đạt",
        "Trạng thái\nthực tế",
        "Tệp mã nguồn, Cấu hình &\nBằng chứng Log kiểm thử",
        "Tồn tại kỹ thuật &\nKế hoạch hoàn thiện"
    ]
    col_widths_c = [Inches(0.4), Inches(1.2), Inches(1.3), Inches(0.9), Inches(1.4), Inches(1.3)]
    format_table_header(tbl_checklist.rows[0], headers_checklist, col_widths_c)
    
    items_checklist = [
        (
            "1",
            "Hoàn thiện thuật toán xác định vi phạm",
            "• Tính % giao nhau (Overlap Ratio) 2D giữa BBox và đa giác vỉa hè.\n• So sánh với ngưỡng threshold.\n• Kiểm tra điểm tiếp đất chân biển.",
            "HOÀN THÀNH\n(100%)",
            "• violation/checker.py: Thuật toán lai kép (3 điểm đáy chân biển + Shapely Polygon 2D).\n• Ngưỡng: threshold=0.30 (30%).\n• tests/test_violation_checker.py: Đạt 4/4 kịch bản (100% pass).",
            "BBox 2D chữ nhật bị phình to diện tích khi biển đặt chéo góc camera. Giai đoạn sau sẽ nghiên cứu nâng cấp sang Instance Segmentation Mask để ôm sát biên dạng."
        ),
        (
            "2",
            "Tích hợp ByteTrack & Xác nhận ổn định theo thời gian",
            "• Gán và duy trì ID qua các khung hình.\n• Lọc chuỗi thời gian loại trừ cảnh báo giả do người xách biển hoặc bóng đổ.",
            "HOÀN THÀNH\n(100%)",
            "• tracking/tracker.py: ByteTrack 2 vòng tối ưu (track_high=0.25, track_low=0.10).\n• tracking/verifier.py: Máy trạng thái 3 cấp (confirm_sec=3.0s, require_stationary=True).\n• tests/test_temporal_verifier.py: Đạt 7/7 kịch bản (100% pass).",
            "Khi camera bị rung lắc mạnh do gió bão làm rung cột CCTV, cần tích hợp thêm thuật toán bù trừ rung lắc toàn khung hình (Global Motion Compensation - GMC)."
        ),
        (
            "3",
            "Xây dựng module lưu ảnh bằng chứng",
            "• Tự động chụp và lưu trữ hình ảnh hiện trường vi phạm.\n• Đóng tem pháp lý.\n• Phục vụ xử phạt nguội.",
            "HOÀN THÀNH\n(100%)",
            "• evidence/saver.py: Lưu 2 cấp độ: Ảnh toàn cảnh (Full Frame) đóng tem thông tin và ảnh crop cận cảnh biển hiệu.\n• Cây thư mục: evidence/records/ và evidence/crops/.\n• tests/test_evidence_saver.py: Đạt 100% pass.\n• Hỗ trợ _safe_imwrite chống lỗi Unicode.",
            "Tính năng làm mờ khuôn mặt (Face Blur) hiện phụ thuộc tệp Haar cascade OpenCV ngoài. Thao tác ghi đĩa hiện chạy đồng bộ (sync), cần chuyển sang async worker."
        ),
        (
            "4",
            "Cơ sở dữ liệu SQLite lưu lịch sử vi phạm",
            "• Xây dựng CSDL quan hệ lưu trữ hồ sơ vi phạm.\n• Hỗ trợ quy trình phê duyệt Human-in-the-Loop.",
            "HOÀN THÀNH\n(100%)",
            "• database/db.py: Quản trị CSDL data/surveillance.db.\n• Bảng violations với 19 trường dữ liệu chuẩn hóa.\n• Thuật toán khử trùng lặp theo ca trực ngày mới.\n• tests/test_database.py: Đạt 100% pass.\n• CSDL hiện lưu giữ 284 hồ sơ vi phạm thực tế.",
            "Chưa có cơ chế mã hóa dữ liệu nhạy cảm ở mức tệp (file-level encryption) và quy trình tự động dọn dẹp/lưu trữ dữ liệu cũ (auto-purge) sau 90 ngày theo luật định."
        ),
        (
            "5",
            "Xử lý đồng thời nhiều luồng camera & Hiệu năng",
            "• Xử lý song song nhiều luồng camera CCTV (RTSP/Webcam/Video).\n• Tối ưu hóa tài nguyên phần cứng (FPS, Latency).",
            "MỘT PHẦN\n(PARTIAL)\n\n[Đa luồng: Chưa kiểm chứng]",
            "• camera/stream_reader.py: Đọc luồng nền threading.Thread xả bộ đệm (Buffer Flush) và Auto-reconnect.\n• dashboard/web_app.py: Dùng ThreadingHTTPServer.\n• Đã đo trên 1 camera: CPU i5 đạt 22.2 FPS (PyTorch), 39.2 FPS (ONNX); Tesla T4 đạt 58.5 FPS.\n• Chưa có orchestrator chạy song song >=4 camera trên main.py.",
            "Cần xây dựng module Multi-Camera Ingestion Manager (mỗi camera 1 process/thread riêng biệt với Queue chung) và đo đạc độ trễ/sụt giảm FPS khi tải đồng thời 2, 4, 8 camera."
        )
    ]
    
    for row_idx, item in enumerate(items_checklist, start=1):
        row = tbl_checklist.rows[row_idx]
        for col_idx, text in enumerate(item):
            cell = row.cells[col_idx]
            cell.width = col_widths_c[col_idx]
            set_cell_margins(cell, 60, 60, 80, 80)
            
            if row_idx % 2 == 1:
                set_cell_background(cell, HEX_BG_ZEBRA)
                
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            
            if col_idx in [0, 3]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
            run = p.add_run(text)
            run.font.name = "Arial"
            run.font.size = Pt(8.5)
            
            if col_idx == 3:
                run.font.bold = True
                if "HOÀN THÀNH" in text:
                    run.font.color.rgb = COLOR_GREEN
                else:
                    run.font.color.rgb = COLOR_AMBER
            elif col_idx == 0:
                run.font.bold = True
                run.font.color.rgb = COLOR_PRIMARY
            else:
                run.font.color.rgb = COLOR_DARK

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

    # =========================================================================
    # PHẦN 1: RÀ SOÁT CHI TIẾT TỪNG HẠNG MỤC KỸ THUẬT
    # =========================================================================
    style_section_heading(doc, "PHẦN 1: RÀ SOÁT CHI TIẾT 5 HẠNG MỤC KỸ THUẬT", level=1)

    # 1. Thuật toán xác định vi phạm không gian
    style_section_heading(doc, "1. Thuật toán xác định vi phạm không gian (Spatial Logic & Overlap Ratio)", level=2)
    
    add_body_paragraph(
        doc,
        "Module violation/checker.py đóng vai trò là 'bộ não phán quyết không gian' của toàn hệ thống, chuyển đổi kết quả phát hiện vật thể dạng Bounding Box sang kết luận pháp lý về hành vi lấn chiếm vỉa hè.",
        bold_prefix="Vai trò module: "
    )
    
    add_body_paragraph(
        doc,
        "Hệ thống không chỉ dựa vào diện tích đè lên vỉa hè mà cài đặt Thuật toán lai kép (Dual-Condition Engine) kết hợp kiểm tra chân đế thực tế và diện tích giao cắt hình học 2D:\n"
        "• Điều kiện 1 — Tọa độ chân đế tiếp xúc mặt đất (3-Point Ground Contact Rule): Biển hiệu đứng trên vỉa hè có bản chất vật lý là chân đế phải chạm mặt đất. Thuật toán trích xuất 3 điểm tại cạnh đáy hộp bao: pt_left = (x1, y2), pt_center = ((x1+x2)/2, y2), pt_right = (x2, y2). Sử dụng hàm cv2.pointPolygonTest với dung sai tiếp đất base_margin = 15.0 px. Nếu bất kỳ điểm nào trong 3 điểm nằm bên trong đa giác vỉa hè, cờ is_base_inside được bật. Quy tắc này loại bỏ hoàn toàn các biển quảng cáo gắn trên tường cao hoặc biển treo ban công tầng 2 (vốn có hình chiếu 2D đè lên vỉa hè nhưng chân đế không chạm đất).\n"
        "• Điều kiện 2 — Tỷ lệ diện tích lấn chiếm 2D (Overlap Ratio với Shapely Polygon): Biểu diễn Bounding Box thành đa giác chữ nhật P_box và vỉa hè thành đa giác P_sidewalk. Tỷ lệ lấn chiếm được tính bằng: Overlap Ratio = Area(P_sidewalk ∩ P_box) / Area(P_box). Lưu ý mẫu số là diện tích hộp bao P_box, không phải IoU giữa 2 vật thể và không phải diện tích vỉa hè. Tích hợp phép toán sidewalk_poly.buffer(0) để tự động sửa lỗi đa giác tự cắt (Self-intersection Polygon).\n"
        "• Ra quyết định vi phạm & Ngưỡng kích hoạt: Một đối tượng bị kết luận là VI PHẠM khi và chỉ khi thỏa mãn đồng thời: (is_base_inside == True) và (Overlap Ratio >= 0.30). Nếu Overlap Ratio < 0.30, hệ thống phân loại là CHẠM MÉP VỈA HÈ (hợp lệ). Hàm check_multi() hỗ trợ quản lý nhiều đa giác vỉa hè độc lập (Multi-ROI).",
        bold_prefix="Cơ chế hoạt động: "
    )

    # Thêm Hình 2: Minh họa ma trận nhầm lẫn chuẩn hóa
    img_v13_cm = str(OUTPUT_DIR / "figures" / "v13_clean" / "confusion_matrix_normalized.png")
    add_image_with_caption(
        doc,
        img_v13_cm,
        "Hình 2. Ma trận nhầm lẫn chuẩn hóa của mô hình v13_clean trên tập validation — nền tảng nhận diện biển hiệu chính xác trước khi đưa vào bộ phán quyết không gian",
        asset_path="reports/figures/v13_clean/confusion_matrix_normalized.png",
        width=Inches(5.5)
    )

    # Bảng 2: Kết quả test violation checker
    add_body_paragraph(doc, "Bảng 2. Kết quả kiểm thử tự động module xác định vi phạm không gian (tests/test_violation_checker.py):")
    tbl_test_v = doc.add_table(rows=5, cols=4)
    tbl_test_v.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_test_v)
    format_table_header(tbl_test_v.rows[0], ["Kịch bản kiểm thử", "Dữ liệu đầu vào mô phỏng", "Kết quả kỳ vọng", "Thực tế kiểm thử"], [Inches(1.8), Inches(2.2), Inches(1.3), Inches(1.2)])
    
    v_cases = [
        ("Biển vi phạm rõ ràng", "BBox nằm trọn vẹn 100% trong đa giác vỉa hè", "is_violation=True, overlap=1.0", "ĐẠT (PASSED)"),
        ("Biển hợp lệ ngoài vỉa hè", "BBox nằm hoàn toàn ở lòng đường (cách xa vỉa hè)", "is_violation=False, overlap=0.0", "ĐẠT (PASSED)"),
        ("Biển chạm nhẹ mép vỉa hè", "BBox lấn mép 15% (nhỏ hơn ngưỡng threshold 30%)", "is_violation=False (Chạm mép)", "ĐẠT (PASSED)"),
        ("Biển treo tường / ban công", "BBox đè 60% vỉa hè nhưng chân đế không chạm đất", "is_violation=False (Loại trừ)", "ĐẠT (PASSED)")
    ]
    for r_idx, c_data in enumerate(v_cases, start=1):
        row = tbl_test_v.rows[r_idx]
        for c_idx, val in enumerate(c_data):
            cell = row.cells[c_idx]
            set_cell_margins(cell, 50, 50, 70, 70)
            if r_idx % 2 == 1:
                set_cell_background(cell, HEX_BG_ZEBRA)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if c_idx == 3:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r.font.bold = True
                r.font.color.rgb = COLOR_GREEN
            else:
                r.font.color.rgb = COLOR_DARK

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

    # 2. Tích hợp ByteTrack & Bộ lọc xác nhận chuỗi thời gian
    style_section_heading(doc, "2. Tích hợp ByteTrack & Bộ lọc xác nhận chuỗi thời gian (Temporal Verification)", level=2)
    
    add_body_paragraph(
        doc,
        "Để khắc phục triệt để điểm yếu cố hữu của mạng nơ-ron nhận diện ảnh tĩnh (nhấp nháy bounding box, mất nhận diện tạm thời khi có xe cộ che khuất, báo động giả khi người đi bộ xách túi/bê biển đi ngang), nhóm nghiên cứu đã xây dựng tầng xử lý chuỗi thời gian tại tracking/tracker.py và tracking/verifier.py.",
        bold_prefix="Mục tiêu kỹ thuật: "
    )
    
    add_body_paragraph(
        doc,
        "• Bộ bám vết ByteTrack tùy biến (ObjectTracker): Phân tách quá trình liên kết đối tượng thành 2 vòng: Vòng 1 (track_high_thresh = 0.25) ghép cặp các hộp độ tin cậy cao với quỹ đạo hiện có; Vòng 2 (track_low_thresh = 0.10) tận dụng các hộp độ tin cậy thấp (thường bị mờ do chuyển động hoặc bị xe máy che khuất một phần) để duy trì quỹ đạo, ngăn ngừa hiện tượng nhảy mã Track ID. Cấu hình chuẩn hóa tại configs/bytetrack_custom.yaml.\n"
        "• Máy trạng thái xác thực thời gian (TemporalVerifier): Mỗi đối tượng được quản lý qua một máy trạng thái 3 cấp: NORMAL (Hợp lệ) -> SUSPECTED (Nghi vấn vi phạm) -> CONFIRMED (Xác nhận vi phạm).\n"
        "• Quy tắc chuyển trạng thái & Cửa sổ thời gian: Khi biển hiệu đè vỉa hè >= 30%, trạng thái chuyển sang SUSPECTED. Chỉ khi vi phạm duy trì liên tục trong cửa sổ thời gian tối thiểu T_confirm = 3.0 giây (tương đương 20 khung hình suy luận), trạng thái mới được nâng cấp lên CONFIRMED.\n"
        "• Bộ lọc đứng yên liên tục (Continuous Stationary Filter): Tính toán độ dịch chuyển tâm hộp bao Delta d trong cửa sổ trượt 1.0s kết hợp Perspective-Adaptive Check. Nếu đối tượng di chuyển với vận tốc vượt ngưỡng max_displacement_pixels = 50.0 px, hệ thống xác định đây là người đi bộ hoặc phương tiện chở hàng di động và từ chối nâng cấp lên CONFIRMED. Đối tượng phải đứng yên liên tục tối thiểu min_stationary_seconds = 2.0s.\n"
        "• Khử trùng lặp cảnh báo (Alert Cooldown & Spatial Dedup): Sau khi phát cảnh báo cho một Track ID, cờ is_new_alert chỉ bật đúng 1 lần duy nhất. Nếu Track ID bị mất tạm thời do xe buýt che khuất trong 1–2 giây rồi xuất hiện lại tại cùng tọa độ, cơ chế Spatial Dedup (bán kính 50.0 px) nhận diện đây là cùng một vật thể và ức chế báo động lặp.",
        bold_prefix="Chi tiết giải pháp: "
    )

    # Bảng 3: Kết quả test tracking
    add_body_paragraph(doc, "Bảng 3. Kết quả kiểm thử tự động module ByteTrack và Temporal Verifier (tests/test_temporal_verifier.py):")
    tbl_test_t = doc.add_table(rows=8, cols=4)
    tbl_test_t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_test_t)
    format_table_header(tbl_test_t.rows[0], ["Kịch bản chuỗi thời gian", "Cấu hình thử nghiệm", "Kết quả kỳ vọng", "Thực tế kiểm thử"], [Inches(1.8), Inches(2.2), Inches(1.3), Inches(1.2)])
    
    t_cases = [
        ("Biển đứng yên liên tục > 3.0s", "20 frames vi phạm, vị trí đứng yên cố định", "Chuyển sang CONFIRMED, phát cảnh báo", "ĐẠT (PASSED)"),
        ("Người mang biển đi qua", "Vị trí tâm dịch chuyển > 50px mỗi frame", "Giữ SUSPECTED, không CONFIRMED", "ĐẠT (PASSED)"),
        ("Biển nhấp nháy 1-2 frames", "Vi phạm trong 0.2s rồi biến mất", "Bộ đếm reset về 0, không báo động", "ĐẠT (PASSED)"),
        ("Khử báo động lặp (Cooldown)", "Biển đã báo vi phạm tiếp tục đứng yên", "is_new_alert=False (Không spam alert)", "ĐẠT (PASSED)"),
        ("Bù trừ che khuất tạm thời (Occlusion)", "Mất Track ID trong 1.5s rồi xuất hiện lại", "Quỹ đạo được khôi phục, không tạo ID giả", "ĐẠT (PASSED)"),
        ("Người dừng lại nghỉ tạm thời", "Dừng lại < 1.0s chưa đủ thời gian quy định", "Giữ SUSPECTED, yêu cầu đứng yên >= 2.0s", "ĐẠT (PASSED)"),
        ("Khử trùng lặp không gian khi đổi ID", "ByteTrack nhảy ID mới tại cùng vị trí", "Spatial Dedup chặn cảnh báo trùng", "ĐẠT (PASSED)")
    ]
    for r_idx, c_data in enumerate(t_cases, start=1):
        row = tbl_test_t.rows[r_idx]
        for c_idx, val in enumerate(c_data):
            cell = row.cells[c_idx]
            set_cell_margins(cell, 50, 50, 70, 70)
            if r_idx % 2 == 1:
                set_cell_background(cell, HEX_BG_ZEBRA)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if c_idx == 3:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r.font.bold = True
                r.font.color.rgb = COLOR_GREEN
            else:
                r.font.color.rgb = COLOR_DARK

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

    # 3. Module lưu ảnh bằng chứng vi phạm
    style_section_heading(doc, "3. Module lưu ảnh bằng chứng vi phạm (Evidence Management)", level=2)
    
    add_body_paragraph(
        doc,
        "Module evidence/saver.py đảm nhiệm việc tạo lập hồ sơ bằng chứng số phục vụ công tác thanh tra trật tự đô thị và xử phạt vi phạm hành chính.",
        bold_prefix="Mục tiêu module: "
    )
    
    add_body_paragraph(
        doc,
        "• Cấu trúc lưu trữ 2 cấp độ ảnh:\n"
        "  1. Ảnh toàn cảnh hiện trường (Full Frame Evidence): Lưu ảnh toàn cảnh độ phân giải gốc của camera; vẽ lớp phủ bán trong suốt thể hiện vùng đa giác vỉa hè (ROI Overlay); đóng khung hộp bao đối tượng vi phạm (màu đỏ) kèm tem thông tin pháp lý (Banner Footer): Mã Camera, Mốc thời gian chính xác đến mili-giây, Mã Track ID, Tỷ lệ diện tích đè vỉa hè và Độ tin cậy AI. Đường dẫn: evidence/records/<cam>/<YYYY-MM-DD>/violation_id<track_id>_<time>.jpg.\n"
        "  2. Ảnh cận cảnh phóng to biển hiệu (Cropped Evidence): Tự động cắt riêng khu vực hộp bao biển hiệu có bổ sung lề an toàn (padding 10%). Phục vụ Cán bộ Quản lý Trật tự Đô thị phóng to đọc rõ nội dung chữ in, tên cửa hàng kinh doanh, số điện thoại hotline hoặc địa chỉ in trên biển. Đường dẫn: evidence/crops/<cam>/<YYYY-MM-DD>/crop_id<track_id>_<time>.jpg.\n"
        "• Cơ chế _safe_imwrite: Sử dụng cv2.imencode kết hợp tệp nhị phân nhằm ngăn ngừa 100% lỗi ghi đĩa khi đường dẫn chứa ký tự tiếng Việt có dấu trên hệ điều hành Windows.",
        bold_prefix="Đặc tả kỹ thuật: "
    )

    # Thêm Hình 3 & 4: Mẫu ảnh toàn cảnh và crop
    img_full = str(OUTPUT_DIR / "figures" / "tuan_12_13" / "full_evidence_sample.jpg")
    img_crop = str(OUTPUT_DIR / "figures" / "tuan_12_13" / "crop_evidence_sample.jpg")
    
    add_image_with_caption(
        doc,
        img_full,
        "Hình 3. Mẫu ảnh bằng chứng toàn cảnh (Full Frame) trích xuất tự động kèm tem pháp lý chân trang",
        asset_path="evidence/records/video_test/2026-11-03/violation_id1_22-59-27-772025.jpg",
        width=Inches(6.0)
    )
    
    add_image_with_caption(
        doc,
        img_crop,
        "Hình 4. Mẫu ảnh bằng chứng cận cảnh (Cropped Image) phóng to chi tiết biển hiệu phục vụ trích xuất thông tin cửa hàng",
        asset_path="evidence/crops/video_test/2026-11-03/crop_id1_22-59-27-772025.jpg",
        width=Inches(3.2)
    )

    # Bảng 4: Cấu trúc tem pháp lý
    add_body_paragraph(doc, "Bảng 4. Đặc tả cấu trúc tem thông tin pháp lý trên ảnh toàn cảnh vi phạm:")
    tbl_stamp = doc.add_table(rows=6, cols=3)
    tbl_stamp.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_stamp)
    format_table_header(tbl_stamp.rows[0], ["Thành phần tem thông tin", "Định dạng hiển thị mẫu", "Ý nghĩa nghiệp vụ pháp lý"], [Inches(1.8), Inches(2.2), Inches(2.5)])
    
    stamp_items = [
        ("Mã định danh Camera", "CAM: video_test (Phố Huế / Hàng Bài)", "Xác định chính xác vị trí địa lý của camera giám sát"),
        ("Mốc thời gian vi phạm", "2026-11-05 15:47:00.212", "Thời điểm phát hiện vi phạm chính xác đến mili-giây"),
        ("Mã bám vết Track ID", "TRACK_ID: #1", "Mã định danh đối tượng được theo dõi liên tục trong video"),
        ("Tỷ lệ lấn chiếm vỉa hè", "OVERLAP: 100.0%", "Căn cứ định lượng mức độ vi phạm không gian"),
        ("Độ tin cậy mô hình AI", "CONF: 87.2%", "Độ chính xác nhận diện biển hiệu của mô hình YOLOv8n ONNX")
    ]
    for r_idx, c_data in enumerate(stamp_items, start=1):
        row = tbl_stamp.rows[r_idx]
        for c_idx, val in enumerate(c_data):
            cell = row.cells[c_idx]
            set_cell_margins(cell, 50, 50, 70, 70)
            if r_idx % 2 == 1:
                set_cell_background(cell, HEX_BG_ZEBRA)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            else:
                r.font.color.rgb = COLOR_DARK

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

    # 4. Cơ sở dữ liệu SQLite lưu lịch sử vi phạm
    style_section_heading(doc, "4. Cơ sở dữ liệu SQLite lưu lịch sử vi phạm (Database & Audit Workflow)", level=2)
    
    add_body_paragraph(
        doc,
        "Module database/db.py quản lý tệp cơ sở dữ liệu quan hệ nhẹ data/surveillance.db, không đòi hỏi cài đặt máy chủ CSDL phức tạp (Zero-configuration), tối ưu cho triển khai thực địa trên thiết bị biên.",
        bold_prefix="Mục tiêu module: "
    )
    
    # Lược đồ SQL
    add_body_paragraph(doc, "Lược đồ bảng violations (19 trường dữ liệu chuẩn hóa):")
    sql_schema = (
        "CREATE TABLE IF NOT EXISTS violations (\n"
        "    id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "    camera_id TEXT NOT NULL,                -- Mã định danh camera giám sát\n"
        "    track_id INTEGER NOT NULL,              -- Mã bám vết đối tượng của ByteTrack\n"
        "    timestamp DATETIME NOT NULL,            -- Mốc thời gian phát sinh vi phạm\n"
        "    violation_type TEXT DEFAULT 'lan_chiem_via_he', -- Phân loại hành vi vi phạm\n"
        "    confidence REAL,                        -- Độ tin cậy nhận diện của AI (0.0 - 1.0)\n"
        "    overlap_pct REAL,                       -- Tỷ lệ diện tích đè vỉa hè (0.0 - 100.0%)\n"
        "    bbox_x1 INTEGER, bbox_y1 INTEGER, bbox_x2 INTEGER, bbox_y2 INTEGER, -- Tọa độ BBox\n"
        "    sidewalk_index INTEGER DEFAULT 1,       -- Đa giác vỉa hè tương ứng\n"
        "    status TEXT DEFAULT 'pending',          -- 'pending' | 'confirmed' | 'dismissed' | 'resolved'\n"
        "    reviewed_by TEXT DEFAULT NULL,          -- Cán bộ phê duyệt hồ sơ phạt nguội\n"
        "    dismiss_reason TEXT DEFAULT NULL,       -- Lý do miễn trừ hoặc bác bỏ hồ sơ\n"
        "    reviewed_at DATETIME DEFAULT NULL,      -- Mốc thời gian thẩm định nghiệp vụ\n"
        "    full_image_path TEXT,                   -- Đường dẫn tệp ảnh toàn cảnh đóng tem\n"
        "    crop_image_path TEXT,                   -- Đường dẫn tệp ảnh crop cận cảnh biển\n"
        "    created_at DATETIME DEFAULT (datetime('now', 'localtime'))\n"
        ");"
    )
    add_code_block(doc, sql_schema)

    add_body_paragraph(
        doc,
        "• Quy trình thẩm định Human-in-the-Loop: Trạng thái pending (Chờ duyệt do AI tự động ghi nhận) -> confirmed (Cán bộ thẩm định duyệt lập biên bản xử phạt) hoặc dismissed (Bác bỏ / Miễn trừ đối với biển có giấy phép tạm thời, hệ thống tự động ức chế cảnh báo lặp lại trong 24h) -> resolved (Hộ kinh doanh đã thu dọn biển hoặc chấp hành nộp phạt).\n"
        "• Thuật toán khử trùng lặp theo ca trực ngày mới: Hàm is_duplicate_violation so sánh tọa độ không gian kết hợp kiểm tra ngày (DATE(timestamp) = DATE('now', 'localtime')). Nhờ đó, sang ngày làm việc mới hệ thống vẫn tiếp tục lập hồ sơ vi phạm mới nếu hộ kinh doanh tái phạm, đồng thời tránh ghi trùng lặp hàng trăm bản ghi cho cùng một biển hiệu trong cùng một ca trực.",
        bold_prefix="Quy trình nghiệp vụ: "
    )

    # Bảng 5: Thống kê số lượng bản ghi trong DB
    add_body_paragraph(doc, "Bảng 5. Thống kê hiện trạng dữ liệu thực tế lưu trữ trong CSDL data/surveillance.db (Kiểm toán ngày 05/11/2026):")
    tbl_db_stat = doc.add_table(rows=7, cols=4)
    tbl_db_stat.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_db_stat)
    format_table_header(tbl_db_stat.rows[0], ["Khoảng thời gian ghi nhận", "Số hồ sơ vi phạm", "Mô hình & Nguồn dữ liệu thực thi", "Trạng thái thẩm định"], [Inches(1.8), Inches(1.3), Inches(2.1), Inches(1.3)])
    
    db_stat_rows = [
        ("Ngày 05/11/2026 (Hôm nay)", "4 hồ sơ mới", "Phiên chạy kiểm chứng trực tiếp pipeline 1 camera", "Chờ duyệt (#281 – #284)"),
        ("Ngày 03/11/2026", "41 hồ sơ", "Model v13_clean mới nhất trên 3 camera CCTV thực địa", "Chờ duyệt & Đã duyệt"),
        ("Ngày 02/11/2026", "80 hồ sơ", "Chạy thực nghiệm tổng hợp video CCTV", "Lưu trữ lịch sử"),
        ("Ngày 01/11/2026", "31 hồ sơ", "Chạy thực nghiệm chuỗi video phố đêm", "Lưu trữ lịch sử"),
        ("Các ngày trước (15/09 - 25/10)", "128 hồ sơ", "Dữ liệu kiểm thử các giai đoạn phát triển ban đầu", "Lưu trữ lịch sử"),
        ("TỔNG CỘNG TOÀN CSDL", "284 hồ sơ", "Đã lập chỉ mục, truy vấn thời gian thực < 5ms", "Toàn vẹn 100%")
    ]
    for r_idx, c_data in enumerate(db_stat_rows, start=1):
        row = tbl_db_stat.rows[r_idx]
        for c_idx, val in enumerate(c_data):
            cell = row.cells[c_idx]
            set_cell_margins(cell, 50, 50, 70, 70)
            if r_idx == 6:
                set_cell_background(cell, HEX_BG_LIGHT)
            elif r_idx % 2 == 1:
                set_cell_background(cell, HEX_BG_ZEBRA)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if r_idx == 6 or c_idx in [0, 1]:
                r.font.bold = True
            if c_idx == 1:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r.font.color.rgb = COLOR_PRIMARY
            else:
                r.font.color.rgb = COLOR_DARK

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

    # 5. Xử lý đồng thời nhiều luồng camera và tối ưu hóa hiệu năng
    style_section_heading(doc, "5. Xử lý đồng thời nhiều luồng camera và tối ưu hóa hiệu năng", level=2)
    
    add_body_paragraph(
        doc,
        "Lớp StreamReader tại camera/stream_reader.py cài đặt cơ chế chạy luồng nền (threading.Thread) độc lập cho từng nguồn cấp camera RTSP hoặc Webcam. Luồng nền liên tục thực hiện vòng lặp cap.read() để làm rỗng bộ đệm khung hình của OpenCV (Buffer Flush), triệt tiêu hoàn toàn độ trễ tích lũy (Zero Latency), bảo đảm khung hình đưa vào mô hình AI luôn là hình ảnh trực tiếp theo thời gian thực. Hỗ trợ tự động kết nối lại (Auto-reconnect) với thời gian chờ 2.0s và giới hạn 10 lần thử khi camera bị ngắt sóng hoặc mất nguồn. Ngoài ra máy chủ Web Dashboard dashboard/web_app.py sử dụng ThreadingHTTPServer phục vụ đồng thời các kết nối xem camera.",
        bold_prefix="Hiện trạng kỹ thuật đã đạt được: "
    )

    add_callout_box(
        doc,
        "Trong mã nguồn chương trình chạy chính main.py, hệ thống hiện tại CHỈ TIẾP NHẬN 1 THAM SỐ --source TẠI MỘT THỜI ĐIỂM (chạy cho 1 camera đơn lẻ). Trong kịch bản đánh giá video CCTV evaluation/evaluate_videos.py, chương trình xử lý LẦN LƯỢT TUẦN TỰ từng video, chưa có bộ điều phối đa luồng (Multi-Camera Orchestrator) chia tải song song >=4 luồng camera đồng thời trên cùng luồng suy luận AI. Do đó, nội dung xử lý đồng thời nhiều luồng camera được đánh giá trung thực là 'MỘT PHẦN (PARTIAL)' và khả năng chịu tải đa luồng đồng thời được ghi nhận chính xác là 'CHƯA KIỂM CHỨNG'.",
        title="ĐÁNH GIÁ LIÊM CHÍNH HỌC THUẬT VỀ ĐA CAMERA ĐỒNG THỜI",
        box_type="amber"
    )

    # Bảng 6: Đo đạc hiệu năng thực tế
    add_body_paragraph(doc, "Bảng 6. Kết quả đo đạc thực nghiệm hiệu năng hệ thống trên 1 camera và hiện trạng đa camera:")
    tbl_perf = doc.add_table(rows=6, cols=5)
    tbl_perf.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_perf)
    format_table_header(tbl_perf.rows[0], ["Cấu hình phần cứng", "Độ phân giải & Runtime", "Tốc độ xử lý (FPS)", "Thời gian trễ (Latency)", "Trạng thái kiểm chứng"], [Inches(1.5), Inches(1.5), Inches(1.1), Inches(1.1), Inches(1.3)])
    
    perf_rows = [
        ("Intel Core i5 (CPU máy trạm)", "imgsz=1280 (PyTorch CPU)", "22.2 FPS", "45.0 ms / frame", "Đã kiểm chứng (1 camera)"),
        ("Intel Core i5 (CPU máy trạm)", "imgsz=640 (ONNX Runtime, skip=2)", "31.3 – 39.2 FPS", "25.5 – 31.9 ms", "Đã kiểm chứng (1 camera)"),
        ("NVIDIA Tesla T4 (GPU Colab)", "imgsz=1280 (PyTorch CUDA)", "58.5 FPS", "17.1 ms / frame", "Đã kiểm chứng (1 camera)"),
        ("Tải đồng thời 2 luồng camera", "imgsz=640/1280 (CPU/GPU)", "Chưa đo đạc thực nghiệm", "Chưa đo đạc", "CHƯA KIỂM CHỨNG"),
        ("Tải đồng thời >=4 luồng camera", "imgsz=640/1280 (CPU/GPU)", "Chưa có module điều phối", "Chưa đo đạc", "CHƯA KIỂM CHỨNG")
    ]
    for r_idx, c_data in enumerate(perf_rows, start=1):
        row = tbl_perf.rows[r_idx]
        for c_idx, val in enumerate(c_data):
            cell = row.cells[c_idx]
            set_cell_margins(cell, 50, 50, 70, 70)
            if r_idx in [4, 5]:
                set_cell_background(cell, HEX_ALERT_AMBER_BG)
            elif r_idx % 2 == 1:
                set_cell_background(cell, HEX_BG_ZEBRA)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if c_idx in [2, 3]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if c_idx == 4:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r.font.bold = True
                if "Đã kiểm chứng" in val:
                    r.font.color.rgb = COLOR_GREEN
                else:
                    r.font.color.rgb = COLOR_AMBER
            else:
                r.font.color.rgb = COLOR_DARK

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

    # =========================================================================
    # PHẦN 2: XÁC NHẬN CHUYÊN BIỆT TIÊU CHÍ NGHIỆM THU: PIPELINE VỚI 1 CAMERA
    # =========================================================================
    style_section_heading(doc, "PHẦN 2: XÁC NHẬN CHUYÊN BIỆT TIÊU CHÍ NGHIỆM THU: PIPELINE VỚI 1 CAMERA", level=1)

    add_callout_box(
        doc,
        "Nhóm sinh viên thực hiện đồ án chính thức xác nhận: PIPELINE HOÀN CHỈNH GỒM 4 TẦNG LIÊN HOÀN (Detect -> Track -> Xác nhận vi phạm -> Lưu DB) ĐÃ ĐƯỢC XÂY DỰNG HOÀN TẤT, TÍCH HỢP ĐỒNG BỘ VÀ CHẠY THỰC TẾ THÀNH CÔNG 100% TRÊN 1 CAMERA ĐƠN LẺ. Toàn bộ chuỗi vận hành diễn ra tự động hoàn toàn, không yêu cầu can thiệp thủ công giữa các khâu.",
        title="KẾT LUẬN NGHIỆM THU HỌC THUẬT: ĐẠT TIÊU CHÍ 100%",
        box_type="success"
    )

    add_body_paragraph(
        doc,
        "Quá trình kiểm thử tích hợp toàn trình (End-to-End Integration Test) được thực hiện trên luồng video CCTV Camera 1 thực tế tại Phố Huế / Hàng Bài, Hoàn Kiếm, Hà Nội (tệp data/videos/video test.mp4, cấu hình ROI configs/roi_video_test.json):",
        bold_prefix="Minh chứng thực nghiệm trên Camera 1: "
    )

    flow_text = (
        "[CCTV CAMERA 1] Khởi chạy Pipeline tích hợp 4 tầng (Model: models/best.onnx - imgsz: 640)\n"
        "├── [TẦNG 1: DETECT]\n"
        "│   └── Mô hình YOLOv8n ONNX Runtime phát hiện các biển hiệu trên khung hình\n"
        "├── [TẦNG 2: TRACK]\n"
        "│   └── ByteTrack gán mã định danh duy nhất: Track #1, #2, #3, #4\n"
        "├── [TẦNG 3: SPATIAL & TEMPORAL DECISION]\n"
        "│   ├── Thuật toán Shapely tính tỷ lệ giao cắt với đa giác vỉa hè (configs/roi_video_test.json):\n"
        "│   │   ├── Track #1: Overlap = 100.0% -> Vi phạm không gian\n"
        "│   │   ├── Track #2: Overlap = 77.3%  -> Vi phạm không gian\n"
        "│   │   ├── Track #3: Overlap = 100.0% -> Vi phạm không gian\n"
        "│   │   └── Track #4: Overlap = 100.0% -> Vi phạm không gian\n"
        "│   └── Bộ lọc TemporalVerifier đếm đủ 20 frames liên tục (> 3.0s) & đứng yên:\n"
        "│       └── Nâng cấp trạng thái từ SUSPECTED -> CONFIRMED (is_new_alert = True)\n"
        "└── [TẦNG 4: EVIDENCE & DATABASE STORAGE]\n"
        "    ├── EvidenceSaver xuất ảnh toàn cảnh có tem: evidence/records/video_test/2026-11-05/...\n"
        "    ├── EvidenceSaver xuất ảnh crop cận cảnh biển: evidence/crops/video_test/2026-11-05/...\n"
        "    └── CSDL SQLite insert_violation ghi nhận thành công bản ghi #281 - #284 vào data/surveillance.db"
    )
    add_code_block(doc, flow_text)

    # Bảng 7: Bản ghi vi phạm sinh ra trong lần chạy test
    add_body_paragraph(doc, "Bảng 7. Chi tiết các bản ghi phạt nguội phát sinh tự động trong phiên chạy tích hợp trên Camera 1 (Ngày 05/11/2026):")
    tbl_rec = doc.add_table(rows=5, cols=5)
    tbl_rec.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_rec)
    format_table_header(tbl_rec.rows[0], ["Mã Record", "Camera ID & Track", "Thời gian ghi nhận", "Tỷ lệ lấn chiếm / Conf", "Đường dẫn ảnh bằng chứng lưu trữ"], [Inches(1.0), Inches(1.5), Inches(1.4), Inches(1.3), Inches(1.3)])
    
    rec_items = [
        ("#281", "video_test (Track #1)", "2026-11-05 15:47:00", "Overlap: 100.0% | Conf: 87.2%", ".../violation_id1_15-47-00.jpg"),
        ("#282", "video_test (Track #2)", "2026-11-05 15:47:00", "Overlap: 77.3% | Conf: 74.5%", ".../violation_id2_15-47-00.jpg"),
        ("#283", "video_test (Track #3)", "2026-11-05 15:47:00", "Overlap: 100.0% | Conf: 82.1%", ".../violation_id3_15-47-00.jpg"),
        ("#284", "video_test (Track #4)", "2026-11-05 15:47:00", "Overlap: 100.0% | Conf: 65.8%", ".../violation_id4_15-47-00.jpg")
    ]
    for r_idx, c_data in enumerate(rec_items, start=1):
        row = tbl_rec.rows[r_idx]
        for c_idx, val in enumerate(c_data):
            cell = row.cells[c_idx]
            set_cell_margins(cell, 50, 50, 70, 70)
            if r_idx % 2 == 1:
                set_cell_background(cell, HEX_BG_ZEBRA)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if c_idx in [0, 3]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if c_idx == 0:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            else:
                r.font.color.rgb = COLOR_DARK

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

    # =========================================================================
    # PHẦN 3: KẾ HOẠCH HÀNH ĐỘNG TUẦN 14–15 TIẾP THEO
    # =========================================================================
    style_section_heading(doc, "PHẦN 3: KẾ HOẠCH HÀNH ĐỘNG TUẦN 14–15 TIẾP THEO", level=1)
    
    add_body_paragraph(
        doc,
        "Theo đúng lộ trình 17 tuần của Đề cương ĐATN, sau khi hoàn thành nghiệm thu pipeline lõi cho 1 camera tại Tuần 12–13, nhóm nghiên cứu sẽ tập trung thực hiện 4 trọng tâm công việc trong giai đoạn Tuần 14–15:"
    )

    plans = [
        ("1. Nâng cấp giao diện Web Dashboard Giám sát & Quản trị Vi phạm: ", "Hoàn thiện các tính năng quản lý hồ sơ vi phạm theo quy trình Human-in-the-Loop; tối ưu thanh công cụ lọc ngày để luôn hiển thị đầy đủ các ngày có hồ sơ thực tế; tích hợp bản đồ số GIS trực quan vị trí các camera; biểu đồ phân tích vi phạm theo tuyến đường và khung giờ cao điểm."),
        ("2. Xây dựng module gửi cảnh báo thời gian thực (Real-time Notification): ", "Tích hợp dịch vụ Telegram Bot hoặc Zalo Official Account (OA) để tự động bắn tin nhắn kèm hình ảnh bằng chứng đến điện thoại của Đội Quản lý Trật tự Đô thị ngay khi phát hiện vi phạm mới."),
        ("3. Mở rộng kiến trúc đa tiến trình cho hệ thống nhiều camera (Multi-Camera Stream Pipeline): ", "Thiết kế module quản lý hàng đợi đa tiến trình (multiprocessing.Queue) để nạp song song nhiều luồng RTSP camera vào luồng suy luận AI tập trung; đo đạc thực nghiệm độ trễ, mức tiêu thụ tài nguyên và tốc độ khung hình (FPS) khi chạy đồng thời 2, 4, 8 camera."),
        ("4. Chuẩn bị tối ưu hóa mô hình sang TensorRT / INT8: ", "Hoàn thiện kịch bản lượng tử hóa mô hình để sẵn sàng triển khai thử nghiệm trên các thiết bị nhúng biên (NVIDIA Jetson Nano, Raspberry Pi) tại Tuần 16 theo đúng lộ trình Đề cương.")
    ]
    for b_prefix, b_text in plans:
        add_body_paragraph(doc, b_text, bold_prefix=b_prefix, space_after=3)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

    # =========================================================================
    # PHẦN 4: DANH MỤC TÀI LIỆU VÀ MINH CHỨNG THỰC NGHIỆM
    # =========================================================================
    style_section_heading(doc, "PHẦN 4: DANH MỤC TÀI LIỆU VÀ MINH CHỨNG THỰC NGHIỆM", level=1)
    
    add_body_paragraph(
        doc,
        "Toàn bộ mã nguồn, cấu hình, dữ liệu kiểm thử và kết quả thực nghiệm của Tuần 12–13 được lưu trữ minh bạch và có thể tái lập hoàn toàn tại workspace đồ án:"
    )

    # Bảng 8: Danh mục tài liệu tham chiếu
    tbl_ref = doc.add_table(rows=8, cols=3)
    tbl_ref.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_ref)
    format_table_header(tbl_ref.rows[0], ["Hạng mục tài nguyên", "Đường dẫn tệp trong Workspace", "Nội dung & Vai trò trong hệ thống"], [Inches(1.8), Inches(2.3), Inches(2.4)])
    
    ref_items = [
        ("Thuật toán vi phạm", "violation/checker.py", "Thuật toán lai kép: 3 điểm tiếp đất + Overlap Ratio Shapely"),
        ("Bộ bám vết ByteTrack", "tracking/tracker.py\nconfigs/bytetrack_custom.yaml", "Bộ bám vết 2 vòng duy trì Track ID, chống vỡ quỹ đạo"),
        ("Xác thực thời gian", "tracking/verifier.py", "Máy trạng thái 3 cấp, bộ lọc đứng yên và cửa sổ thời gian 3.0s"),
        ("Lưu trữ bằng chứng", "evidence/saver.py", "Xuất ảnh toàn cảnh đóng tem pháp lý và ảnh crop cận cảnh"),
        ("Cơ sở dữ liệu SQLite", "database/db.py\ndata/surveillance.db", "Quản lý 284 hồ sơ vi phạm, khử trùng lặp theo ca trực ngày"),
        ("Bộ kiểm thử tự động", "tests/test_violation_checker.py\ntests/test_temporal_verifier.py\ntests/test_evidence_saver.py\ntests/test_database.py", "Hệ thống unit tests kiểm tra toàn diện 100% các kịch bản biên (16 passed)"),
        ("Pipeline chính & Dashboard", "main.py\ndashboard/web_app.py", "Tích hợp toàn trình từ video đầu vào đến Web Dashboard")
    ]
    for r_idx, c_data in enumerate(ref_items, start=1):
        row = tbl_ref.rows[r_idx]
        for c_idx, val in enumerate(c_data):
            cell = row.cells[c_idx]
            set_cell_margins(cell, 50, 50, 70, 70)
            if r_idx % 2 == 1:
                set_cell_background(cell, HEX_BG_ZEBRA)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            elif c_idx == 1:
                r.font.name = "Consolas"
                r.font.size = Pt(8.0)
                r.font.color.rgb = COLOR_SECONDARY
            else:
                r.font.color.rgb = COLOR_DARK

    # Lưu tài liệu
    saved_paths = []
    for out_path in [PRIMARY_FILE, FALLBACK_FILE]:
        try:
            doc.save(out_path)
            print(f"[THÀNH CÔNG] Đã lưu báo cáo Tuần 12-13: {out_path}")
            saved_paths.append(out_path)
        except PermissionError:
            print(f"[CẢNH BÁO] Không thể ghi đè {out_path} (đang mở trong Word).")
        except Exception as e:
            print(f"[LỖI] Lưu {out_path} thất bại: {e}")

    return saved_paths


if __name__ == "__main__":
    build_tuan_12_13_ban_cap_nhat_report()

