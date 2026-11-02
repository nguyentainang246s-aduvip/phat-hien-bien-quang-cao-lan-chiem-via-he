"""
Script xuất bản bài học Ngày 09 thành file Word (.docx) chuyên nghiệp
Lưu trữ vào thư mục: roadmap AI/Ngay_09_Quan_Tri_Du_Lieu_Cloud_Roboflow_API.docx
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
OUTPUT_FILE = str(OUTPUT_DIR / "Ngay_09_Quan_Tri_Du_Lieu_Cloud_Roboflow_API.docx")

# Bảng màu sắc học thuật tiêu chuẩn
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
        f'  <w:top w:val="none"/>'
        f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'  <w:bottom w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    cell._tc.get_or_add_tcPr().append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    run_title = p.add_run(f"📌 {title.upper()}")
    run_title.bold = True
    run_title.font.name = "Arial"
    run_title.font.size = Pt(10.5)
    run_title.font.color.rgb = title_color
    
    p_body = cell.add_paragraph()
    p_body.paragraph_format.space_before = Pt(2)
    p_body.paragraph_format.space_after = Pt(0)
    p_body.paragraph_format.line_spacing = 1.15
    run_body = p_body.add_run(text)
    run_body.font.name = "Arial"
    run_body.font.size = Pt(9.5)
    run_body.font.color.rgb = COLOR_DARK
    
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(4)
    p_spacer.paragraph_format.space_after = Pt(4)


def add_code_block(doc, code_str, language="python"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    
    set_cell_background(cell, HEX_BG_CODE)
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
        f'  <w:left w:val="single" w:sz="16" w:space="0" w:color="{HEX_SECONDARY}"/>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
        f'</w:tcBorders>'
    )
    cell._tc.get_or_add_tcPr().append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_str.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(30, 41, 59)
    
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(4)
    p_spacer.paragraph_format.space_after = Pt(4)


def build_document():
    doc = Document()
    
    # Thiết lập lề 1 inch chuẩn học thuật
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)
        sec.page_width = Inches(8.5)
        sec.page_height = Inches(11.0)

    # Header tài liệu
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    title_run = title_p.add_run("ĐỒ ÁN TỐT NGHIỆP: HỆ THỐNG PHÁT HIỆN BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ")
    title_run.font.name = "Arial"
    title_run.font.size = Pt(11)
    title_run.bold = True
    title_run.font.color.rgb = COLOR_SECONDARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(0)
    sub_p.paragraph_format.space_after = Pt(16)
    sub_run = sub_p.add_run("HƯỚNG DẪN THỰC CHIẾN TRACK A (AI & DỮ LIỆU) — NGÀY 09")
    sub_run.font.name = "Arial"
    sub_run.font.size = Pt(9.5)
    sub_run.font.color.rgb = COLOR_MUTED

    # Tiêu đề bài học
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(6)
    h1.paragraph_format.space_after = Pt(8)
    h1_run = h1.add_run("NGÀY 09: KHỞI TẠO ROBOFLOW WORKSPACE, KẾT NỐI API & QUẢN TRỊ DỰ ÁN DỮ LIỆU TRÊN CLOUD")
    h1_run.font.name = "Arial"
    h1_run.font.size = Pt(15)
    h1_run.bold = True
    h1_run.font.color.rgb = COLOR_PRIMARY

    # Thông tin tổng quan meta
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Phân hệ phụ trách:", "Track A — AI & Dữ liệu (Computer Vision Engineer)"),
        ("Mục tiêu trọng tâm:", "Nắm vững cơ chế Snapshot Versioning, kết nối Roboflow REST API tự động, bảo mật Token và chuẩn hóa đường ống dữ liệu"),
        ("Tài nguyên thực tế:", "Roboflow Project: tai-nang-nguyen-duc/sidewalk-signboard-detection-1 (Version 8)"),
        ("Tập tin liên quan:", "datasets/download_dataset.py, scripts/train_colab.py, datasets/v8/")
    ]
    for row_idx, (k, v) in enumerate(meta_data):
        row = meta_table.rows[row_idx]
        cell_k, cell_v = row.cells[0], row.cells[1]
        cell_k.width = Inches(2.2)
        cell_v.width = Inches(4.3)
        set_cell_margins(cell_k, top=60, bottom=60, left=80, right=80)
        set_cell_margins(cell_v, top=60, bottom=60, left=80, right=80)
        
        pk = cell_k.paragraphs[0]
        pk.paragraph_format.space_before = Pt(0)
        pk.paragraph_format.space_after = Pt(0)
        rk = pk.add_run(k)
        rk.font.name = "Arial"
        rk.font.size = Pt(9)
        rk.bold = True
        rk.font.color.rgb = COLOR_DARK
        
        pv = cell_v.paragraphs[0]
        pv.paragraph_format.space_before = Pt(0)
        pv.paragraph_format.space_after = Pt(0)
        rv = pv.add_run(v)
        rv.font.name = "Arial"
        rv.font.size = Pt(9)
        rv.font.color.rgb = COLOR_DARK
        
    set_table_borders(meta_table)

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(8)
    p_spacer.paragraph_format.space_after = Pt(8)

    # ----------------------------------------------------
    # PHẦN 1: ẨN DỤ ĐỜI SỐNG & TRỰC GIÁC (THE INTUITION)
    # ----------------------------------------------------
    sec1 = doc.add_paragraph()
    sec1_run = sec1.add_run("1. ẨN DỤ ĐỜI SỐNG & TRỰC GIÁC: TẠI SAO CẦN ROBOFLOW CLOUD?")
    sec1_run.font.name = "Arial"
    sec1_run.font.size = Pt(12.5)
    sec1_run.bold = True
    sec1_run.font.color.rgb = COLOR_PRIMARY

    p1 = doc.add_paragraph()
    p1.paragraph_format.line_spacing = 1.2
    p1.paragraph_format.space_after = Pt(6)
    r1 = p1.add_run(
        "Hãy tưởng tượng quy trình làm dữ liệu ảnh truyền thống giống như việc em và cộng sự chia sẻ tài liệu "
        "bằng cách nén file zip gửi qua Zalo hay Google Drive: 'dataset_final.zip', 'dataset_final_fixed.zip', "
        "'dataset_final_chot_that_su.zip'. Hậu quả là sau một vài tuần, không ai biết mô hình AI của mình đang học "
        "từ tập ảnh nào, nhãn nào đã sửa, nhãn nào chưa, và khi huấn luyện lại trên GPU Cloud (như Google Colab) "
        "thì việc tải lên cả Gigabyte file zip thủ công vừa tốn thời gian vừa cực kỳ dễ sai sót.\n\n"
        "Roboflow đóng vai trò chính xác như một 'Hệ thống Quản lý Phiên bản Git dành riêng cho Thị giác máy tính' "
        "(Git for Computer Vision) kết hợp một 'Kho ngoại quan dữ liệu Cloud':"
    )
    r1.font.name = "Arial"
    r1.font.size = Pt(10)
    r1.font.color.rgb = COLOR_DARK

    bullets = [
        ("Nơi lưu trữ và gắn nhãn tập trung (Centralized Annotation Hub):", 
         "Toàn bộ ảnh thô được tải lên Cloud, gắn nhãn trên giao diện web trực quan, không lo mất mát dữ liệu do hỏng ổ cứng cá nhân."),
        ("Đóng băng phiên bản bất biến (Dataset Snapshot):", 
         "Mỗi lần hoàn tất gán nhãn, hệ thống tạo ra một phiên bản độc lập (Version 1, Version 2, ..., Version 8). Dữ liệu của Version 8 một khi đã sinh ra sẽ bị khóa cứng 100%, không bao giờ bị thay đổi hay ghi đè."),
        ("Đường ống phân phối tự động qua API (Automated API Pipeline):", 
         "Máy tính cục bộ hoặc máy chủ Google Colab chỉ cần gọi 1 dòng code Python kèm Token xác thực là toàn bộ 974 ảnh và nhãn chuẩn hóa sẽ tự động tải về giải nén trong vòng chưa đầy 15 giây.")
    ]
    for b_title, b_desc in bullets:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.line_spacing = 1.15
        bp.paragraph_format.space_after = Pt(3)
        b_r1 = bp.add_run(f"{b_title} ")
        b_r1.bold = True
        b_r1.font.name = "Arial"
        b_r1.font.size = Pt(9.5)
        b_r1.font.color.rgb = COLOR_DARK
        b_r2 = bp.add_run(b_desc)
        b_r2.font.name = "Arial"
        b_r2.font.size = Pt(9.5)
        b_r2.font.color.rgb = COLOR_DARK

    add_callout_box(
        doc,
        "Dữ liệu trong kỹ nghệ AI là 'Code của tương lai'. Code Python có GitHub để quản lý commit và tag release, "
        "thì Dataset cũng bắt buộc phải có hệ thống Snapshot Versioning để đảm bảo tính tái lập (Reproducibility). "
        "Dự án của em đang quản trị chuyên nghiệp qua Roboflow Project: 'tai-nang-nguyen-duc/sidewalk-signboard-detection-1' "
        "ở phiên bản chốt chặn Version 8.",
        "TRIẾT LÝ QUẢN TRỊ DỮ LIỆU HIỆN ĐẠI",
        "info"
    )

    # ----------------------------------------------------
    # PHẦN 2: MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC
    # ----------------------------------------------------
    sec2 = doc.add_paragraph()
    sec2_run = sec2.add_run("2. MỔ XẺ BẢN CHẤT KỸ THUẬT: CƠ CHẾ SNAPSHOT & BẢO MẬT API")
    sec2_run.font.name = "Arial"
    sec2_run.font.size = Pt(12.5)
    sec2_run.bold = True
    sec2_run.font.color.rgb = COLOR_PRIMARY

    p2 = doc.add_paragraph()
    p2.paragraph_format.line_spacing = 1.2
    p2.paragraph_format.space_after = Pt(6)
    r2 = p2.add_run(
        "Để bảo vệ tính khoa học của đồ án trước Hội đồng chấm thi, kỹ sư AI cần hiểu thấu đáo 2 cơ chế then chốt: "
        "Tính toàn vẹn của Dataset Version và Kiến trúc xác thực bảo mật API Token."
    )
    r2.font.name = "Arial"
    r2.font.size = Pt(10)
    r2.font.color.rgb = COLOR_DARK

    h2_1 = doc.add_paragraph()
    h2_1.paragraph_format.space_before = Pt(6)
    h2_1.paragraph_format.space_after = Pt(4)
    r2_1 = h2_1.add_run("2.1. Cơ chế Snapshot Versioning (Bản chụp đóng băng dữ liệu bất biến)")
    r2_1.bold = True
    r2_1.font.name = "Arial"
    r2_1.font.size = Pt(11)
    r2_1.font.color.rgb = COLOR_SECONDARY

    p2_1 = doc.add_paragraph()
    p2_1.paragraph_format.line_spacing = 1.15
    p2_1.paragraph_format.space_after = Pt(6)
    r2_1_text = p2_1.add_run(
        "Một sai lầm sơ đẳng của sinh viên làm AI là tải ảnh và nhãn thẳng từ 'Raw Workspace' đang gán nhãn dở dang. "
        "Nếu hôm nay em train model, ngày mai em vào web xóa 10 ảnh xấu, ngày kia bạn cùng nhóm thêm 50 ảnh mới, "
        "thì dataset ở 3 thời điểm đó hoàn toàn khác nhau. Khi đó, kết quả mAP (Mean Average Precision) tăng hay giảm "
        "không thể chứng minh được là do mô hình tối ưu hay do bộ dữ liệu bị biến động ngầm.\n\n"
        "Roboflow giải quyết bài toán này thông qua tính năng 'Generate Version':"
    )
    r2_1_text.font.name = "Arial"
    r2_1_text.font.size = Pt(9.5)
    r2_1_text.font.color.rgb = COLOR_DARK

    steps = [
        ("Bước 1 - Snapshotting:", "Hệ thống chụp lại toàn bộ trạng thái ảnh, nhãn, phân chia Train/Valid/Test tại giây phút nhấn Generate."),
        ("Bước 2 - Tiền xử lý & Tăng cường (Preprocessing & Augmentation):", "Tự động áp dụng kích thước chuẩn (Resize 1280x1280), xoay góc, chỉnh màu sắc theo cấu hình đã chọn."),
        ("Bước 3 - Cố định bất biến (Immutable Lock):", "Sinh ra mã định danh Version duy nhất (Version 8). Một khi đã sinh ra, Version này không cho phép sửa đổi hay xóa nhãn lẻ. Dù em có tiếp tục gán nhãn thêm ảnh mới vào Workspace thì những ảnh mới đó chỉ thuộc về Version 9 trong tương lai.")
    ]
    for s_title, s_desc in steps:
        sp = doc.add_paragraph(style='List Bullet')
        sp.paragraph_format.line_spacing = 1.15
        sp.paragraph_format.space_after = Pt(3)
        sr1 = sp.add_run(f"{s_title} ")
        sr1.bold = True
        sr1.font.name = "Arial"
        sr1.font.size = Pt(9.5)
        sr1.font.color.rgb = COLOR_DARK
        sr2 = sp.add_run(s_desc)
        sr2.font.name = "Arial"
        sr2.font.size = Pt(9.5)
        sr2.font.color.rgb = COLOR_DARK

    h2_2 = doc.add_paragraph()
    h2_2.paragraph_format.space_before = Pt(8)
    h2_2.paragraph_format.space_after = Pt(4)
    r2_2 = h2_2.add_run("2.2. Cơ chế REST API & Nguyên lý bảo mật Biến môi trường (Environment Variable)")
    r2_2.bold = True
    r2_2.font.name = "Arial"
    r2_2.font.size = Pt(11)
    r2_2.font.color.rgb = COLOR_SECONDARY

    p2_2 = doc.add_paragraph()
    p2_2.paragraph_format.line_spacing = 1.15
    p2_2.paragraph_format.space_after = Pt(6)
    r2_2_text = p2_2.add_run(
        "Roboflow cung cấp thư viện Python SDK `roboflow` giao tiếp qua chuẩn REST API với máy chủ cloud. "
        "Mỗi yêu cầu (request) tải dữ liệu bắt buộc phải kèm theo chuỗi xác thực quyền sở hữu (Roboflow Private API Key).\n\n"
        "Nguyên tắc sống còn trong phát triển phần mềm và bảo mật thông tin (theo chuẩn quốc tế The Twelve-Factor App): "
        "TUYỆT ĐỐI KHÔNG HARDCODE MÃ BÍ MẬT (SECRET KEY) TRỰC TIẾP VÀO MÃ NGUỒN!"
    )
    r2_2_text.font.name = "Arial"
    r2_2_text.font.size = Pt(9.5)
    r2_2_text.font.color.rgb = COLOR_DARK

    add_callout_box(
        doc,
        "TẠI SAO PHẢI DÙNG os.environ.get('ROBOFLOW_API_KEY')?\n"
        "1. Chống rò rỉ mã bí mật lên GitHub: Nếu em viết thẳng api_key = 'abcdef123...' vào file code rồi commit lên "
        "GitHub, các bot tự động chuyên quét secret (GitHub Secret Scanner) sẽ phát hiện ra chỉ sau vài giây. Kẻ xấu "
        "có thể chiếm đoạt tài nguyên, đánh cắp bộ dữ liệu đồ án tốt nghiệp của em hoặc làm sai lệch kết quả.\n"
        "2. Tính linh hoạt đa môi trường: Cùng một file code Python, khi chạy ở máy trạm cá nhân, máy của bạn làm Track B, "
        "hay trên GPU Cloud Colab thì code hoàn toàn không phải sửa một chữ nào, chỉ cần nạp khóa bí mật vào môi trường thực thi của máy đó.",
        "NGUYÊN TẮC BẢO MẬT CHUẨN CÔNG NGHIỆP",
        "warning"
    )

    # ----------------------------------------------------
    # PHẦN 3: HƯỚNG DẪN THỰC CHIẾN TRÊN FILE MÃ NGUỒN
    # ----------------------------------------------------
    sec3 = doc.add_paragraph()
    sec3_run = sec3.add_run("3. HƯỚNG DẪN THỰC CHIẾN TRÊN FILE MÃ NGUỒN DỰ ÁN")
    sec3_run.font.name = "Arial"
    sec3_run.font.size = Pt(12.5)
    sec3_run.bold = True
    sec3_run.font.color.rgb = COLOR_PRIMARY

    p3 = doc.add_paragraph()
    p3.paragraph_format.line_spacing = 1.2
    p3.paragraph_format.space_after = Pt(6)
    r3 = p3.add_run(
        "Trong thư mục đồ án, chúng ta đã xây dựng sẵn 2 script kết nối Roboflow chuẩn hóa cao: "
        "`datasets/download_dataset.py` (tải data về máy trạm phục vụ kiểm tra/lưu trữ) và "
        "`scripts/train_colab.py` (tự động kéo data và huấn luyện trên Colab T4 GPU)."
    )
    r3.font.name = "Arial"
    r3.font.size = Pt(10)
    r3.font.color.rgb = COLOR_DARK

    h3_1 = doc.add_paragraph()
    h3_1.paragraph_format.space_before = Pt(4)
    h3_1.paragraph_format.space_after = Pt(2)
    r3_1 = h3_1.add_run("3.1. Phân tích chi tiết file datasets/download_dataset.py")
    r3_1.bold = True
    r3_1.font.name = "Arial"
    r3_1.font.size = Pt(10.5)
    r3_1.font.color.rgb = COLOR_SECONDARY

    code_download = (
        'import os\n'
        'from pathlib import Path\n'
        'from roboflow import Roboflow\n\n'
        '# 1. Đọc khóa API an toàn từ biến môi trường\n'
        'api_key = os.environ.get("ROBOFLOW_API_KEY")\n'
        'if not api_key:\n'
        '    raise ValueError("Chưa thiết lập biến môi trường ROBOFLOW_API_KEY! Hãy đặt trước khi chạy script.")\n\n'
        '# 2. Khởi tạo phiên làm việc với Roboflow Cloud\n'
        'rf = Roboflow(api_key=api_key)\n\n'
        '# 3. Trỏ tới đúng Workspace và Dự án của đồ án\n'
        'workspace = rf.workspace("tai-nang-nguyen-duc")\n'
        'project = workspace.project("sidewalk-signboard-detection-1")\n\n'
        '# 4. Tải chính xác Snapshot Version 8 bất biến ở định dạng YOLOv8\n'
        'target_dir = Path(__file__).resolve().parent / "v8"\n'
        'version = project.version(8)\n'
        'dataset = version.download("yolov8", location=str(target_dir))\n'
        'print(f"[*] Tải thành công Dataset Version 8 về thư mục: {target_dir}")'
    )
    add_code_block(doc, code_download)

    h3_2 = doc.add_paragraph()
    h3_2.paragraph_format.space_before = Pt(6)
    h3_2.paragraph_format.space_after = Pt(2)
    r3_2 = h3_2.add_run("3.2. Cách thiết lập biến môi trường trên Windows & Google Colab")
    r3_2.bold = True
    r3_2.font.name = "Arial"
    r3_2.font.size = Pt(10.5)
    r3_2.font.color.rgb = COLOR_SECONDARY

    p_env = doc.add_paragraph()
    p_env.paragraph_format.line_spacing = 1.15
    p_env.paragraph_format.space_after = Pt(4)
    r_env = p_env.add_run(
        "Kỹ sư AI cần biết cách thiết lập biến môi trường linh hoạt tùy theo nền tảng đang vận hành:"
    )
    r_env.font.name = "Arial"
    r_env.font.size = Pt(9.5)
    r_env.font.color.rgb = COLOR_DARK

    code_env = (
        '# [Cách 1] Trong PowerShell trên máy Windows:\n'
        '$env:ROBOFLOW_API_KEY="ma_api_key_cua_em"\n'
        'python datasets/download_dataset.py\n\n'
        '# [Cách 2] Trong Command Prompt (CMD):\n'
        'set ROBOFLOW_API_KEY=ma_api_key_cua_em\n'
        'python datasets/download_dataset.py\n\n'
        '# [Cách 3] Trong Google Colab (sử dụng Colab Secrets để an toàn tuyệt đối):\n'
        'from google.colab import userdata\n'
        'import os\n'
        'os.environ["ROBOFLOW_API_KEY"] = userdata.get("ROBOFLOW_API_KEY")'
    )
    add_code_block(doc, code_env, language="bash")

    # ----------------------------------------------------
    # PHẦN 4: SẢN PHẨM BÀN GIAO & CÁCH TỰ KIỂM TRA
    # ----------------------------------------------------
    sec4 = doc.add_paragraph()
    sec4_run = sec4.add_run("4. SẢN PHẨM BÀN GIAO & CÁCH TỰ KIỂM TRA (QUALITY AUDIT)")
    sec4_run.font.name = "Arial"
    sec4_run.font.size = Pt(12.5)
    sec4_run.bold = True
    sec4_run.font.color.rgb = COLOR_PRIMARY

    p4 = doc.add_paragraph()
    p4.paragraph_format.line_spacing = 1.2
    p4.paragraph_format.space_after = Pt(6)
    r4 = p4.add_run(
        "Sau khi tải thành công bằng API, bộ dữ liệu tại thư mục `datasets/v8/` phải đáp ứng đầy đủ các tiêu chí "
        "kỹ thuật sau đây trước khi được đưa vào đường ống huấn luyện mô hình YOLOv8:"
    )
    r4.font.name = "Arial"
    r4.font.size = Pt(10)
    r4.font.color.rgb = COLOR_DARK

    tbl_audit = doc.add_table(rows=5, cols=3)
    tbl_audit.alignment = WD_TABLE_ALIGNMENT.CENTER
    audit_data = [
        ("Thành phần / Thư mục", "Quy cách kỹ thuật chuẩn", "Trạng thái kiểm tra thực tế"),
        ("Tập tin cấu hình data.yaml", "Chứa đường dẫn tuyệt đối/tương đối, names: ['bien-quang-cao'], nc: 1", "Đạt chuẩn 100% (Single-class)"),
        ("Tập train (862 ảnh)", "Gồm ảnh tích cực + 84 ảnh Negative (0-byte txt) chống báo động giả", "Đạt chuẩn 100% (9.74% mẫu âm tính)"),
        ("Tập valid (56 ảnh)", "Tỷ lệ ~6% dùng để tính loss validation và kích hoạt Early Stopping", "Đạt chuẩn 100% (Không trùng lặp tập train)"),
        ("Tập test (56 ảnh)", "Tỷ lệ ~6% độc lập dùng để đánh giá mAP50, mAP50-95 khách quan", "Đạt chuẩn 100% (Snapshot v8 đóng băng)")
    ]
    for row_idx, row_vals in enumerate(audit_data):
        row = tbl_audit.rows[row_idx]
        for col_idx, text_val in enumerate(row_vals):
            cell = row.cells[col_idx]
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(0)
            p_cell.paragraph_format.space_after = Pt(0)
            run_c = p_cell.add_run(text_val)
            run_c.font.name = "Arial"
            if row_idx == 0:
                cell.width = Inches(2.1) if col_idx == 0 else Inches(2.2)
                set_cell_background(cell, HEX_HEADER_BG)
                run_c.bold = True
                run_c.font.size = Pt(9.5)
                run_c.font.color.rgb = RGBColor(255, 255, 255)
            else:
                cell.width = Inches(2.1) if col_idx == 0 else Inches(2.2)
                run_c.font.size = Pt(9)
                run_c.font.color.rgb = COLOR_DARK
                if col_idx == 2:
                    run_c.bold = True
                    run_c.font.color.rgb = COLOR_GREEN

    set_table_borders(tbl_audit)

    p_spacer2 = doc.add_paragraph()
    p_spacer2.paragraph_format.space_before = Pt(6)
    p_spacer2.paragraph_format.space_after = Pt(6)

    # ----------------------------------------------------
    # PHẦN 5: GIẢ LẬP VẤN ĐÁP HỘI ĐỒNG BẢO VỆ
    # ----------------------------------------------------
    sec5 = doc.add_paragraph()
    sec5_run = sec5.add_run("5. GIẢ LẬP VẤN ĐÁP HỘI ĐỒNG BẢO VỆ (DEFENSE QUESTIONS & MODEL ANSWERS)")
    sec5_run.font.name = "Arial"
    sec5_run.font.size = Pt(12.5)
    sec5_run.bold = True
    sec5_run.font.color.rgb = COLOR_PRIMARY

    # Câu hỏi 1
    q1_p = doc.add_paragraph()
    q1_p.paragraph_format.space_before = Pt(4)
    q1_p.paragraph_format.space_after = Pt(2)
    q1_run = q1_p.add_run("❓ CÂU HỎI 1 (Quick Check):")
    q1_run.bold = True
    q1_run.font.name = "Arial"
    q1_run.font.size = Pt(10.5)
    q1_run.font.color.rgb = COLOR_SECONDARY

    q1_desc = doc.add_paragraph()
    q1_desc.paragraph_format.line_spacing = 1.15
    q1_desc.paragraph_format.space_after = Pt(4)
    q1_desc_run = q1_desc.add_run(
        "\"Tại sao trong script datasets/download_dataset.py, em phải dùng os.environ.get('ROBOFLOW_API_KEY') "
        "thay vì dán thẳng chuỗi string bí mật api_key = 'abcdef123456' vào mã nguồn cho tiện?\""
    )
    q1_desc_run.italic = True
    q1_desc_run.font.name = "Arial"
    q1_desc_run.font.size = Pt(9.5)
    q1_desc_run.font.color.rgb = COLOR_DARK

    ans1_box = (
        "CÂU TRẢ LỜI MẪU ĐẠT ĐIỂM XUẤT SẮC TRƯỚC HỘI ĐỒNG:\n"
        "Thưa Thầy Cô, việc sử dụng biến môi trường os.environ.get('ROBOFLOW_API_KEY') thay vì hardcode chuỗi API Key "
        "xuất phát từ hai lý do kỹ thuật mang tính chuẩn mực công nghiệp:\n\n"
        "1. Bảo mật tuyệt đối mã nguồn (Security & Anti-Leakage): Mã nguồn đồ án được quản lý trên GitHub và chia sẻ "
        "với Hội đồng chấm thi. Nếu dán trực tiếp API Key vào code, các công cụ quét tự động (GitHub Secret Scanning Bots) "
        "sẽ phát hiện chỉ sau vài giây. Khi đó, tài khoản Roboflow có thể bị kẻ xấu lợi dụng quota, đánh cắp toàn bộ bộ dữ liệu "
        "đồ án hoặc xóa sạch dữ liệu trên đám mây.\n\n"
        "2. Tuân thủ nguyên lý The Twelve-Factor App (Phân tách mã nguồn và cấu hình nhạy cảm): Cùng một tệp mã nguồn "
        "download_dataset.py, hệ thống có thể chạy liền mạch tại máy trạm Windows của em, máy tính của thành viên Track B, "
        "hoặc trên các máy chủ đám mây như Google Colab hay Kaggle mà không cần phải chỉnh sửa hay thay đổi bất kỳ dòng mã nào. "
        "Mỗi môi trường chỉ cần cấu hình khóa bí mật tương ứng."
    )
    add_callout_box(doc, ans1_box, "LỜI GIẢI MẪU CÂU HỎI 1", "success")

    # Câu hỏi 2
    q2_p = doc.add_paragraph()
    q2_p.paragraph_format.space_before = Pt(6)
    q2_p.paragraph_format.space_after = Pt(2)
    q2_run = q2_p.add_run("❓ CÂU HỎI 2 (Hội đồng chất vấn độ tin cậy khoa học):")
    q2_run.bold = True
    q2_run.font.name = "Arial"
    q2_run.font.size = Pt(10.5)
    q2_run.font.color.rgb = COLOR_SECONDARY

    q2_desc = doc.add_paragraph()
    q2_desc.paragraph_format.line_spacing = 1.15
    q2_desc.paragraph_format.space_after = Pt(4)
    q2_desc_run = q2_desc.add_run(
        "\"Em làm đồ án tốt nghiệp trong suốt 3-4 tháng. Làm sao em chứng minh tính 'khoa học lặp lại' "
        "(Scientific Reproducibility) của bộ dữ liệu? Nếu tháng sau em bấm nhầm xóa vài chục ảnh trên web, "
        "hoặc bạn cùng nhóm thêm vào 100 ảnh khác mà không báo, thì làm sao em đảm bảo mô hình huấn luyện sau này "
        "có thể so sánh công bằng (fair comparison) với mô hình ban đầu?\""
    )
    q2_desc_run.italic = True
    q2_desc_run.font.name = "Arial"
    q2_desc_run.font.size = Pt(9.5)
    q2_desc_run.font.color.rgb = COLOR_DARK

    ans2_box = (
        "CÂU TRẢ LỜI MẪU ĐẠT ĐIỂM XUẤT SẮC TRƯỚC HỘI ĐỒNG:\n"
        "Thưa Thầy Cô, đây chính là bài toán cốt tử về 'Tính tái lập khoa học' (Reproducibility) trong nghiên cứu AI. "
        "Nếu bộ dữ liệu kiểm thử (Test Set) bị thay đổi ngầm, mọi đối sánh giữa các mô hình sẽ mất hoàn toàn giá trị khoa học.\n\n"
        "Để giải quyết triệt để rủi ro này, nhóm chúng em đã áp dụng quy trình Đóng băng phiên bản dữ liệu bất biến "
        "(Immutable Dataset Snapshotting) trên nền tảng Roboflow:\n\n"
        "1. Cơ chế đóng băng phiên bản (Immutable Version 8): Sau khi hoàn thiện gán nhãn và kiểm tra chất lượng, "
        "chúng em kích hoạt lệnh Generate Version để sinh ra Version 8. Tại thời điểm này, toàn bộ 974 ảnh, nhãn tọa độ "
        "chuẩn hóa, tỷ lệ phân chia Train/Valid/Test (862/56/56) cùng cấu hình tiền xử lý được 'đóng băng vĩnh viễn' "
        "dưới một Snapshot ID độc lập. Dù sau này có thành viên nào thêm ảnh mới, xóa ảnh cũ hay sửa nhãn trên web "
        "thì những thay đổi đó chỉ nằm trong vùng nháp (Workspace Draft) và nếu sinh mới sẽ mang tên Version 9, "
        "hoàn toàn không thể làm biến đổi dữ liệu của Version 8 dù chỉ 1 pixel.\n\n"
        "2. Khả năng tái lập 100% mọi lúc mọi nơi: Mã nguồn huấn luyện của chúng em (scripts/train_colab.py và "
        "datasets/download_dataset.py) được ràng buộc cứng với project.version(8). Bất kỳ ai trong Hội đồng, hay nhóm em "
        "chạy lại thí nghiệm sau nhiều tháng, hệ thống cũng sẽ tải về chính xác 974 tệp ảnh với mã băm SHA-256 hoàn toàn "
        "đồng nhất, đảm bảo tính khách quan và công bằng tuyệt đối (Fair Benchmark) khi so sánh hiệu năng các mô hình."
    )
    add_callout_box(doc, ans2_box, "LỜI GIẢI MẪU CÂU HỎI 2", "success")

    doc.save(OUTPUT_FILE)
    print(f"[SUCCESS] Đã tạo thành công tài liệu Word: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_document()
