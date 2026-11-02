"""
Script xuất bản bài học Ngày 10 thành file Word (.docx) chuyên nghiệp
Lưu trữ vào thư mục: roadmap AI/Ngay_10_Quy_Chuan_Dan_Nhan_Vang_Gold_Standard.docx
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
OUTPUT_FILE = str(OUTPUT_DIR / "Ngay_10_Quy_Chuan_Dan_Nhan_Vang_Gold_Standard.docx")

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
    
    # Cấu hình lề 1 inch chuẩn học thuật
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
    sub_run = sub_p.add_run("HƯỚNG DẪN THỰC CHIẾN TRACK A (AI & DỮ LIỆU) — NGÀY 10")
    sub_run.font.name = "Arial"
    sub_run.font.size = Pt(9.5)
    sub_run.font.color.rgb = COLOR_MUTED

    # Tiêu đề bài học
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(6)
    h1.paragraph_format.space_after = Pt(8)
    h1_run = h1.add_run("NGÀY 10: QUY CHUẨN DÁN NHÃN VÀNG (GOLD LABELING STANDARD)")
    h1_run.font.name = "Arial"
    h1_run.font.size = Pt(15)
    h1_run.bold = True
    h1_run.font.color.rgb = COLOR_PRIMARY

    h1_sub = doc.add_paragraph()
    h1_sub.paragraph_format.space_before = Pt(0)
    h1_sub.paragraph_format.space_after = Pt(12)
    h1_sub_run = h1_sub.add_run("ÔM SÁT MÉP (TIGHT BBOX) & BAO TRỌN CHÂN ĐẾ CHẠM ĐẤT PHỤC VỤ GIẢI THUẬT TRACK B")
    h1_sub_run.font.name = "Arial"
    h1_sub_run.font.size = Pt(11)
    h1_sub_run.bold = True
    h1_sub_run.font.color.rgb = COLOR_SECONDARY

    # Thông tin tổng quan meta
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Phân hệ phụ trách:", "Track A — AI & Dữ liệu (Computer Vision Engineer)"),
        ("Mục tiêu trọng tâm:", "Nắm vững quy chuẩn dán nhãn vàng: bao trọn chân cọc tiếp đất, ôm sát biên độ, xử lý che khuất và đảm bảo tính tương thích với Track B"),
        ("Điểm neo hình học:", "Tọa độ đáy hộp y2 kết hợp hoành độ trung tâm xc xác định điểm chạm đất P_ground = (xc, y2)"),
        ("Đơn vị phối hợp:", "Track B — Giải thuật kiểm tra không gian Đa giác Vỉa hè (Shapely Point-in-Polygon)")
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
    sec1_run = sec1.add_run("1. ẨN DỤ ĐỜI SỐNG & TRỰC GIÁC: BÀN CHÂN CHẠM ĐẤT VÀ RANH GIỚI HỆ THỐNG")
    sec1_run.font.name = "Arial"
    sec1_run.font.size = Pt(12.5)
    sec1_run.bold = True
    sec1_run.font.color.rgb = COLOR_PRIMARY

    p1 = doc.add_paragraph()
    p1.paragraph_format.line_spacing = 1.2
    p1.paragraph_format.space_after = Pt(6)
    r1 = p1.add_run(
        "Hãy tưởng tượng một người cảnh sát giao thông đứng nhìn một người đi bộ để xác định xem người đó có đang "
        "dẫm chân lên thảm cỏ công viên hay không. Người cảnh sát sẽ nhìn vào đâu? Chắc chắn không phải là chiếc mũ "
        "hay màu áo sặc sỡ, mà là nhìn thẳng vào MŨI GIÀY TIẾP XÚC VỚI MẶT ĐẤT.\n\n"
        "Trong đồ án tốt nghiệp của chúng ta, sự phối hợp giữa hai thành viên diễn ra như sau:\n"
        "• Track B quản lý Đa giác Vỉa hè (Sidewalk Polygon ROI). Track B không quan tâm bảng hiệu bán bún chả hay trà đá, "
        "thứ duy nhất bạn ấy cần từ mô hình AI của em là: 'Tọa độ điểm tiếp xúc mặt đất của cái biển đó nằm ở đâu?'\n"
        "• Nếu em dán nhãn cẩu thả — chỉ dùng chuột khoanh cái mặt bảng hình chữ nhật có chữ mà BỎ QUÊN CHÂN ĐẾ cắm xuống đất — "
        "thì đáy hộp nhận diện (y2) sẽ bị nhấc bổng lơ lửng trên không trung (cách mặt đất từ 0.5m đến 1m). "
        "Khi Track B lấy điểm đáy đó chiếu xuống bản đồ không gian, giải thuật sẽ kết luận: 'Biển đang bay trên trời, "
        "không chạm vào vỉa hè, nên không có vi phạm!'. Toàn bộ hệ thống đồ án sẽ bỏ lọt vi phạm hàng loạt!"
    )
    r1.font.name = "Arial"
    r1.font.size = Pt(10)
    r1.font.color.rgb = COLOR_DARK

    add_callout_box(
        doc,
        "ĐỊNH LUẬT VẬT LÝ TRONG GÁN NHÃN THỊ GIÁC MÁY TÍNH:\n"
        "Dán nhãn không phải là vẽ tranh tự do, dán nhãn là truyền đạt định luật vật lý cho mạng Nơ-ron. "
        "Một Bounding Box đúng chuẩn vàng (Gold Standard) bắt buộc phải ôm khít từ đỉnh cao nhất cho tới tận cùng "
        "điểm tiếp xúc mặt đất của chân cọc/chân đế.",
        "TRIẾT LÝ DÁN NHÃN VÀNG",
        "info"
    )

    # ----------------------------------------------------
    # PHẦN 2: MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC
    # ----------------------------------------------------
    sec2 = doc.add_paragraph()
    sec2_run = sec2.add_run("2. MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC: ĐIỂM CHẠM ĐẤT P_ground")
    sec2_run.font.name = "Arial"
    sec2_run.font.size = Pt(12.5)
    sec2_run.bold = True
    sec2_run.font.color.rgb = COLOR_PRIMARY

    p2 = doc.add_paragraph()
    p2.paragraph_format.line_spacing = 1.2
    p2.paragraph_format.space_after = Pt(6)
    r2 = p2.add_run(
        "Mô hình YOLOv8 dự đoán hộp bao Bounding Box dưới dạng (x1, y1, x2, y2). Để xác định điểm neo không gian "
        "tiếp xúc thực địa (Ground Contact Point), hệ thống sử dụng công thức toán học:"
    )
    r2.font.name = "Arial"
    r2.font.size = Pt(10)
    r2.font.color.rgb = COLOR_DARK

    math_box = (
        "CÔNG THỨC ĐIỂM TIẾP XÚC MẶT ĐẤT (GROUND CONTACT POINT):\n\n"
        "x_ground = (x1 + x2) / 2 = x_center * W\n"
        "y_ground = y2 = (y_center + h / 2) * H\n\n"
        "Điều kiện vi phạm không gian: P_ground(x_ground, y_ground) ∈ Polygon_vỉa_hè"
    )
    add_code_block(doc, math_box, language="python")

    h2_1 = doc.add_paragraph()
    h2_1.paragraph_format.space_before = Pt(6)
    h2_1.paragraph_format.space_after = Pt(4)
    r2_1 = h2_1.add_run("2.1. Phân tích sai lệch hình học dưới góc nhìn camera phối cảnh (Perspective CCTV)")
    r2_1.bold = True
    r2_1.font.name = "Arial"
    r2_1.font.size = Pt(11)
    r2_1.font.color.rgb = COLOR_SECONDARY

    p2_1 = doc.add_paragraph()
    p2_1.paragraph_format.line_spacing = 1.15
    p2_1.paragraph_format.space_after = Pt(6)
    r2_1_text = p2_1.add_run(
        "Camera an ninh CCTV thực tế được gắn ở độ cao từ 2.5m - 4.5m và chếch một góc nghiêng chúi xuống từ 20° đến 45°. "
        "Trong phép chiếu phối cảnh (Perspective Projection):\n"
        "• Trục tung ảnh (y) đại diện cho chiều sâu không gian (depth). Càng lên trên (y nhỏ) là càng ở xa camera, càng xuống dưới (y lớn) là càng gần camera.\n"
        "• Nếu người gán nhãn bỏ quên chân đế dài h_leg (ví dụ 100 - 150 pixel trên ảnh Full HD), điểm y_ground bị co thụt lên trên một đoạn h_leg.\n"
        "• Sai lệch này biến đổi một vật thể đang cắm chân ngay giữa lòng vỉa hè thành một vật thể lùi xa hàng mét về phía sau tường nhà hoặc bay lơ lửng, "
        "khiến giải thuật kiểm tra Đa giác của Track B hoàn toàn bị vô hiệu hóa."
    )
    r2_1_text.font.name = "Arial"
    r2_1_text.font.size = Pt(9.5)
    r2_1_text.font.color.rgb = COLOR_DARK

    h2_2 = doc.add_paragraph()
    h2_2.paragraph_format.space_before = Pt(6)
    h2_2.paragraph_format.space_after = Pt(4)
    r2_2 = h2_2.add_run("2.2. Hai lỗi sai kinh điển: Hộp quá lỏng (Loose Box) và Hộp quá chật (Cut-off Box)")
    r2_2.bold = True
    r2_2.font.name = "Arial"
    r2_2.font.size = Pt(11)
    r2_2.font.color.rgb = COLOR_SECONDARY

    p2_2 = doc.add_paragraph()
    p2_2.paragraph_format.line_spacing = 1.15
    p2_2.paragraph_format.space_after = Pt(6)
    r2_2_text = p2_2.add_run(
        "1. Lỗi Hộp quá lỏng (Loose Bounding Box): Vẽ thừa khoảng trống lớn xung quanh biển quảng cáo. "
        "Khi đó, mạng YOLO sẽ học cả các hoa văn gạch lát vỉa hè, vết sơn kẻ đường hay bóng râm vào làm đặc trưng nhận dạng của biển. "
        "Hệ quả là mô hình sinh ra vô số báo động giả (False Positive) khi gặp các mảng gạch lát tương tự.\n\n"
        "2. Lỗi Hộp quá chật hoặc Cắt cụt (Cut-off Box): Cắt xén mất mép chữ, mất viền khung nhôm hoặc cắt ngang cọc chân sắt. "
        "Hệ quả là làm mất đi đặc trưng biên độ sắc nét, khiến hàm mất mát vị trí hộp CIoU/DFL gặp khó khăn trong việc hội tụ."
    )
    r2_2_text.font.name = "Arial"
    r2_2_text.font.size = Pt(9.5)
    r2_2_text.font.color.rgb = COLOR_DARK

    # ----------------------------------------------------
    # PHẦN 3: BỘ 5 QUY TẮC DÁN NHÃN VÀNG (GOLD STANDARDS)
    # ----------------------------------------------------
    sec3 = doc.add_paragraph()
    sec3_run = sec3.add_run("3. BỘ 5 QUY TẮC DÁN NHÃN VÀNG (GOLD LABELING STANDARDS)")
    sec3_run.font.name = "Arial"
    sec3_run.font.size = Pt(12.5)
    sec3_run.bold = True
    sec3_run.font.color.rgb = COLOR_PRIMARY

    p3 = doc.add_paragraph()
    p3.paragraph_format.line_spacing = 1.2
    p3.paragraph_format.space_after = Pt(6)
    r3 = p3.add_run(
        "Để đảm bảo chất lượng nhãn đạt cấp độ sản phẩm công nghiệp (Production-grade), toàn bộ nhãn trong dự án "
        "phải tuân thủ nghiêm ngặt bảng quy chuẩn 5 tình huống sau:"
    )
    r3.font.name = "Arial"
    r3.font.size = Pt(10)
    r3.font.color.rgb = COLOR_DARK

    tbl_rules = doc.add_table(rows=6, cols=3)
    tbl_rules.alignment = WD_TABLE_ALIGNMENT.CENTER
    rules_data = [
        ("Tên Quy Tắc", "Tình Huống Thực Địa", "Quy Chuẩn Thao Tác Kỹ Sư AI"),
        ("Quy tắc 1: Bao trọn chân cọc", "Biển đứng chữ A, Standee cuốn, biển hộp có chân cắm đất", "Kéo mép dưới y2 xuống chạm đúng điểm tiếp xúc với vỉa hè/mặt đất. Tuyệt đối không dừng ở mép dưới bảng chữ."),
        ("Quy tắc 2: Ôm sát biên (Tightness)", "Mọi loại biển quảng cáo", "Hộp bao phải tiếp tuyến khít khao với 4 mép ngoài cùng (trên, dưới, trái, phải). Sai số thừa biên không quá 2-3 pixel."),
        ("Quy tắc 3: Biển treo tường / Biển vẫy", "Biển gắn cố định trên tường nhà, gắn cột cao", "Khoanh khít toàn bộ mặt biển nhô ra. Do không có chân cắm đất, y2 chính là mép đáy của khung biển."),
        ("Quy tắc 4: Che khuất nhẹ (< 30%)", "Xe máy hoặc người đi bộ che mất một phần chân cọc", "Áp dụng 'Ước lượng tinh thần' (Mental Projection): Kéo hộp xuống vị trí chân đế tiếp đất để bảo toàn tọa độ y2 cho Track B."),
        ("Quy tắc 5: Cụm biển đứng liền kề", "Nhiều quán ăn để 2-3 biển cạnh nhau hoặc chồng lên nhau", "Phải tách biệt thành từng Bounding Box riêng biệt (Overlapping Boxes). Tuyệt đối không gộp chung vào 1 hộp lớn!")
    ]
    for row_idx, row_vals in enumerate(rules_data):
        row = tbl_rules.rows[row_idx]
        for col_idx, text_val in enumerate(row_vals):
            cell = row.cells[col_idx]
            set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
            p_c = cell.paragraphs[0]
            p_c.paragraph_format.space_before = Pt(0)
            p_c.paragraph_format.space_after = Pt(0)
            rc = p_c.add_run(text_val)
            rc.font.name = "Arial"
            if row_idx == 0:
                cell.width = Inches(1.8) if col_idx == 0 else (Inches(2.1) if col_idx == 1 else Inches(2.6))
                set_cell_background(cell, HEX_HEADER_BG)
                rc.bold = True
                rc.font.size = Pt(9.5)
                rc.font.color.rgb = RGBColor(255, 255, 255)
            else:
                cell.width = Inches(1.8) if col_idx == 0 else (Inches(2.1) if col_idx == 1 else Inches(2.6))
                rc.font.size = Pt(8.5)
                rc.font.color.rgb = COLOR_DARK
                if col_idx == 0:
                    rc.bold = True
                    rc.font.color.rgb = COLOR_PRIMARY

    set_table_borders(tbl_rules)

    p_spacer2 = doc.add_paragraph()
    p_spacer2.paragraph_format.space_before = Pt(8)
    p_spacer2.paragraph_format.space_after = Pt(8)

    # ----------------------------------------------------
    # PHẦN 4: HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN
    # ----------------------------------------------------
    sec4 = doc.add_paragraph()
    sec4_run = sec4.add_run("4. HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN KẾT NỐI HỆ THỐNG")
    sec4_run.font.name = "Arial"
    sec4_run.font.size = Pt(12.5)
    sec4_run.bold = True
    sec4_run.font.color.rgb = COLOR_PRIMARY

    p4 = doc.add_paragraph()
    p4.paragraph_format.line_spacing = 1.2
    p4.paragraph_format.space_after = Pt(6)
    r4 = p4.add_run(
        "Dưới đây là đoạn mã thực tế minh chứng cách Track B tiếp nhận kết quả nhận diện từ mô hình Track A để "
        "tính toán điểm chạm đất và xác định hành vi vi phạm lấn chiếm vỉa hè:"
    )
    r4.font.name = "Arial"
    r4.font.size = Pt(10)
    r4.font.color.rgb = COLOR_DARK

    code_conn = (
        'from shapely.geometry import Point, Polygon\n\n'
        'def extract_ground_contact_point(detection_box):\n'
        '    """\n'
        '    Trích xuất tọa độ tiếp xúc mặt đất P_ground từ Bounding Box của Track A.\n'
        '    detection_box: [x1, y1, x2, y2, confidence, class_id]\n'
        '    """\n'
        '    x1, y1, x2, y2 = detection_box[:4]\n'
        '    x_ground = (x1 + x2) / 2.0\n'
        '    y_ground = y2  # Điểm đáy của hộp (đòi hỏi nhãn phải bao trọn chân đế cọc sắt)\n'
        '    return Point(x_ground, y_ground)\n\n'
        '# Giả định Đa giác Vỉa hè được cấu hình bởi Track B\n'
        'sidewalk_roi = Polygon([(120, 450), (850, 450), (980, 720), (50, 720)])\n\n'
        '# Trường hợp A: Nhãn chuẩn vàng (Bao trọn chân cọc tiếp đất, y2=580)\n'
        'box_gold = [380, 320, 460, 580, 0.92, 0]\n'
        'p_gold = extract_ground_contact_point(box_gold)\n'
        'is_violation = sidewalk_roi.contains(p_gold)\n'
        'print(f"[*] Nhãn chuẩn vàng: P_ground = ({p_gold.x}, {p_gold.y}) -> Lấn chiếm: {is_violation}")\n'
        '# Kết quả: True (Phát hiện chính xác hành vi lấn chiếm!)\n\n'
        '# Trường hợp B: Nhãn cẩu thả (Chỉ khoanh mặt biển, bỏ quên chân cọc, y2=410)\n'
        'box_faulty = [380, 320, 460, 410, 0.92, 0]\n'
        'p_faulty = extract_ground_contact_point(box_faulty)\n'
        'is_violation_faulty = sidewalk_roi.contains(p_faulty)\n'
        'print(f"[!] Nhãn cẩu thả: P_ground = ({p_faulty.x}, {p_faulty.y}) -> Lấn chiếm: {is_violation_faulty}")\n'
        '# Kết quả: False (Bỏ lọt vi phạm do y2 bị nhấc bổng ra ngoài Đa giác vỉa hè!)'
    )
    add_code_block(doc, code_conn)

    # ----------------------------------------------------
    # PHẦN 5: GIẢ LẬP VẤN ĐÁP HỘI ĐỒNG BẢO VỆ
    # ----------------------------------------------------
    sec5 = doc.add_paragraph()
    sec5_run = sec5.add_run("5. GIẢ LẬP VẤN ĐÁP HỘI ĐỒNG BẢO VỆ (DEFENSE QUESTIONS & MODEL ANSWERS)")
    sec5_run.font.name = "Arial"
    sec5_run.font.size = Pt(12.5)
    sec5_run.bold = True
    sec5_run.font.color.rgb = COLOR_PRIMARY

    # Câu 1
    q1_p = doc.add_paragraph()
    q1_p.paragraph_format.space_before = Pt(4)
    q1_p.paragraph_format.space_after = Pt(2)
    q1_run = q1_p.add_run("❓ CÂU HỎI 1 (Quick Check - Kiểm tra sự thấu hiểu bài toán):")
    q1_run.bold = True
    q1_run.font.name = "Arial"
    q1_run.font.size = Pt(10.5)
    q1_run.font.color.rgb = COLOR_SECONDARY

    q1_desc = doc.add_paragraph()
    q1_desc.paragraph_format.line_spacing = 1.15
    q1_desc.paragraph_format.space_after = Pt(4)
    q1_desc_run = q1_desc.add_run(
        "\"Tại sao khi dán nhãn một biển quảng cáo dạng hộp đứng có chân sắt trên vỉa hè, em không được chỉ khoanh "
        "phần mặt bảng hiệu có chữ mà bắt buộc phải kéo hộp Bounding Box xuống chạm đáy của chân sắt tiếp xúc với mặt đất?\""
    )
    q1_desc_run.italic = True
    q1_desc_run.font.name = "Arial"
    q1_desc_run.font.size = Pt(9.5)
    q1_desc_run.font.color.rgb = COLOR_DARK

    ans1_box = (
        "CÂU TRẢ LỜI MẪU ĐẠT ĐIỂM XUẤT SẮC TRƯỚC HỘI ĐỒNG:\n"
        "Thưa Thầy Cô, việc bao trọn chân đế cắm đất trong Bounding Box xuất phát từ bản chất hình học không gian của hệ thống:\n\n"
        "1. Sự phụ thuộc giữa hai phân hệ (Track A và Track B): Phân hệ AI của em không tồn tại độc lập mà là đầu vào "
        "trực tiếp cho giải thuật phân tích không gian của Track B. Để xác định biển quảng cáo có lấn chiếm vỉa hè hay không, "
        "hệ thống bắt buộc phải tính toán điểm tiếp xúc mặt đất P_ground = (x_center, y2) và kiểm tra điểm này có nằm trong "
        "Đa giác Vỉa hè (Sidewalk Polygon ROI) hay không.\n\n"
        "2. Điểm chạm đất thực tế: Biển quảng cáo có thể có mặt bảng nhô cao, nhưng chính chân cọc sắt dựng trên mặt gạch mới "
        "là vật thể trực tiếp chiếm dụng không gian của người đi bộ. Nếu em chỉ khoanh mặt bảng có chữ mà bỏ chân cọc, "
        "đáy hộp y2 sẽ bị lơ lửng trên không trung. Dưới góc nhìn phối cảnh camera CCTV chếch từ trên cao, sai lệch hàng chục pixel "
        "trục dọc sẽ khiến điểm chạm đất bị dịch chuyển ra ngoài vỉa hè, dẫn tới việc hệ thống bỏ lọt hành vi vi phạm nghiêm trọng."
    )
    add_callout_box(doc, ans1_box, "LỜI GIẢI MẪU CÂU HỎI 1", "success")

    # Câu 2
    q2_p = doc.add_paragraph()
    q2_p.paragraph_format.space_before = Pt(6)
    q2_p.paragraph_format.space_after = Pt(2)
    q2_run = q2_p.add_run("❓ CÂU HỎI 2 (Chất vấn hóc búa về Hiện tượng Che khuất - Occlusion):")
    q2_run.bold = True
    q2_run.font.name = "Arial"
    q2_run.font.size = Pt(10.5)
    q2_run.font.color.rgb = COLOR_SECONDARY

    q2_desc = doc.add_paragraph()
    q2_desc.paragraph_format.line_spacing = 1.15
    q2_desc.paragraph_format.space_after = Pt(4)
    q2_desc_run = q2_desc.add_run(
        "\"Trên vỉa hè thực tế, có rất nhiều trường hợp chân đế của biển quảng cáo bị xe máy đỗ che khuất, "
        "hoặc người đi bộ đi ngang qua che mất phần chân chạm đất. Khi dán nhãn huấn luyện, em xử lý tình huống chân biển "
        "bị che khuất này như thế nào? Và nếu mô hình dự đoán ra một Bounding Box có đáy y2 bị lơ lửng do xe máy che chân, "
        "phân hệ Track A của em có cơ chế nào để cảnh báo hoặc hỗ trợ Track B không?\""
    )
    q2_desc_run.italic = True
    q2_desc_run.font.name = "Arial"
    q2_desc_run.font.size = Pt(9.5)
    q2_desc_run.font.color.rgb = COLOR_DARK

    ans2_box = (
        "CÂU TRẢ LỜI MẪU ĐẠT ĐIỂM XUẤT SẮC TRƯỚC HỘI ĐỒNG:\n"
        "Thưa Thầy Cô, đây là một thách thức thực tế rất kinh điển trong Thị giác máy tính và nhóm em giải quyết đồng thời ở 2 tầng:\n\n"
        "1. Tầng dữ liệu huấn luyện (Chiến lược dán nhãn có kiểm soát che khuất - Occlusion Labeling Policy):\n"
        "• Che khuất nhẹ (< 30% diện tích, chân bị che thoáng qua): Chúng em áp dụng nguyên lý 'Ước lượng tinh thần' "
        "(Mental Projection / Amodal Completion). Nếu hướng đi của thân cọc rõ ràng, người gán nhãn chủ động kéo mép hộp y2 "
        "chạm vị trí tiếp đất giả định. Nhờ đó, mạng Nơ-ron học được khả năng khôi phục toàn thể vật thể ngay cả khi bị che khuất cục bộ.\n"
        "• Che khuất nặng (> 50% hoặc hoàn toàn không thấy chân): Chúng em chỉ đóng khung phần nhìn thấy rõ (Visible Box) "
        "hoặc loại bỏ ảnh gây mập mờ để tránh làm rối loạn hàm mất mát tọa độ hộp của mạng.\n\n"
        "2. Tầng suy luận luồng video (Cơ chế liên kết Track A và Track B trên luồng thời gian):\n"
        "• Không xử lý trên frame đơn lẻ: Một người đi bộ đi qua che chân biển chỉ diễn ra trong khoảng 1 đến 2 giây (30-60 frames). "
        "Hệ thống không đánh giá vi phạm trên một khung hình đơn lẻ. Thay vào đó, Track B kết hợp thuật toán ByteTrack gán track_id "
        "xuyên suốt chuỗi khung hình.\n"
        "• Cơ chế lọc cửa sổ thời gian (Time-Window Aggregation): Track A cung cấp thêm thuộc tính hình học (chiều cao h và tỷ lệ h/w). "
        "Khi chân biển bị xe máy che làm chiều cao h sụt giảm đột ngột so với các khung hình ổn định trước đó, hệ thống nhận diện "
        "vật thể đang ở trạng thái 'Bị che khuất tạm thời' và giữ nguyên tọa độ chân đế hợp lệ đã ghi nhận trước đó. Hành vi vi phạm "
        "chỉ được chốt khi vật thể cố định lấn chiếm liên tục vượt ngưỡng thời gian quy định (ví dụ T > 30 giây)."
    )
    add_callout_box(doc, ans2_box, "LỜI GIẢI MẪU CÂU HỎI 2", "success")

    doc.save(OUTPUT_FILE)
    print(f"[SUCCESS] Đã tạo thành công tài liệu Word: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_document()
