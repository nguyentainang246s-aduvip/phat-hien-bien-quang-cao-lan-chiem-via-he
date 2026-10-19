"""
Script xuất bản bài học Bài 2 thành file Word .docx chuyên nghiệp
Lưu vào thư mục: tai_lieu_hoc_tap/Bai_02_Ve_Do_Hoa_va_Su_Kien_Chuot_ROI.docx
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
OUTPUT_DIR = ROOT_DIR / "tai_lieu_hoc_tap"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = str(OUTPUT_DIR / "Bai_02_Ve_Do_Hoa_va_Su_Kien_Chuot_ROI.docx")

COLOR_PRIMARY = RGBColor(30, 58, 138)     # Navy #1E3A8A
COLOR_SECONDARY = RGBColor(15, 118, 110)  # Teal #0F766E
COLOR_DARK = RGBColor(30, 41, 59)         # Slate Dark #1E293B
COLOR_MUTED = RGBColor(100, 116, 139)     # Slate Gray #64748B
COLOR_RED = RGBColor(220, 38, 38)         # Red

HEX_PRIMARY = "1E3A8A"
HEX_SECONDARY = "0F766E"
HEX_BG_LIGHT = "F8FAFC"
HEX_BG_CODE = "F1F5F9"
HEX_BORDER = "CBD5E1"
HEX_HEADER_BG = "1E3A8A"
HEX_CALLOUT_BG = "EFF6FF"
HEX_CALLOUT_BORDER = "3B82F6"
HEX_WARNING_BG = "FEF2F2"
HEX_WARNING_BORDER = "EF4444"
HEX_CONFIRMED = "DBEAFE"


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


def add_callout_box(doc, text, title="LƯU Ý QUAN TRỌNG", is_warning=False):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    
    bg_color = HEX_WARNING_BG if is_warning else HEX_CALLOUT_BG
    border_color = HEX_WARNING_BORDER if is_warning else HEX_CALLOUT_BORDER
    
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
    run_title = p.add_run(f"{title}: ")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(10.5)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(220, 38, 38) if is_warning else COLOR_PRIMARY
    
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
        f'  <w:left w:val="single" w:sz="16" w:space="0" w:color="{HEX_PRIMARY}"/>'
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


def build_document():
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
    # --- HEADER TIÊU ĐỀ ---
    p_header = doc.add_paragraph()
    p_header.paragraph_format.space_after = Pt(2)
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_uni = p_header.add_run("ĐẠI HỌC BÁCH KHOA HÀ NỘI — TRƯỜNG CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG\n")
    r_uni.font.name = "Arial"
    r_uni.font.size = Pt(10)
    r_uni.font.bold = True
    r_uni.font.color.rgb = COLOR_MUTED
    
    r_sub = p_header.add_run("ĐỒ ÁN TỐT NGHIỆP: HỆ THỐNG PHÁT HIỆN BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV\n")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = COLOR_SECONDARY
    
    r_badge = p_header.add_run("CHƯƠNG TRÌNH ĐÀO TẠO NỘI BỘ — HỌC HIỂU ĐỒ ÁN TỪ CON SỐ 0")
    r_badge.font.name = "Arial"
    r_badge.font.size = Pt(9.5)
    r_badge.font.italic = True
    r_badge.font.color.rgb = COLOR_MUTED

    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(4)
    p_div.paragraph_format.space_after = Pt(14)
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_div = p_div.add_run("━" * 50)
    r_div.font.color.rgb = COLOR_PRIMARY

    # Tiêu đề bài học
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_after = Pt(8)
    p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_b2 = p_title.add_run("BÀI 2: VẼ ĐỒ HỌA & BẮT SỰ KIỆN CHUỘT (MOUSE CALLBACK)\n")
    r_b2.font.name = "Arial"
    r_b2.font.size = Pt(18)
    r_b2.font.bold = True
    r_b2.font.color.rgb = COLOR_PRIMARY
    
    r_b2_sub = p_title.add_run("Cơ chế để con người thiết lập ranh giới vỉa hè đa giác (ROI) trên màn hình Camera")
    r_b2_sub.font.name = "Arial"
    r_b2_sub.font.size = Pt(13)
    r_b2_sub.font.bold = True
    r_b2_sub.font.color.rgb = COLOR_SECONDARY

    # Bảng siêu dữ liệu
    tbl_meta = doc.add_table(rows=3, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Tệp mã nguồn tương ứng:", "scripts/demos/mouse_events.py (Tham chiếu: roi_drawer.py)"),
        ("Cấp độ bài học:", "Giai đoạn 1 — Tương tác giao diện & Thiết lập cấu hình CCTV"),
        ("Đối tượng học tập:", "Người học từ con số 0, cần hiểu cách vẽ và lấy tọa độ đỉnh vỉa hè")
    ]
    for i, (k, v) in enumerate(meta_data):
        c0 = tbl_meta.cell(i, 0)
        c1 = tbl_meta.cell(i, 1)
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
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

    # --- PHẦN 1: HÔM NAY HỌC GÌ? ---
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(4)
    r_h1 = h1.add_run("PHẦN 1: HÔM NAY HỌC GÌ?")
    r_h1.font.name = "Arial"
    r_h1.font.size = Pt(13)
    r_h1.font.bold = True
    r_h1.font.color.rgb = COLOR_PRIMARY

    p_p1 = doc.add_paragraph()
    p_p1.paragraph_format.line_spacing = Pt(14)
    p_p1.paragraph_format.space_after = Pt(6)
    p_p1.add_run(
        "• Tên bài học: Cơ chế Lập trình hướng sự kiện (Event-driven Programming) với Chuột và các hàm vẽ đồ họa của OpenCV.\n"
        "• Mục tiêu cốt lõi:\n"
        "   1. Hiểu khái niệm Hàm gọi lại (Callback Function) trong OpenCV: cách máy tính 'nghe ngóng' khi người dùng click chuột.\n"
        "   2. Sử dụng thành thạo các hàm vẽ đồ họa: cv2.circle (vẽ điểm), cv2.line (vẽ đoạn thẳng), cv2.putText (viết chữ lên ảnh).\n"
        "   3. Hiểu cơ chế hoạt động của công cụ vẽ vỉa hè roi_drawer.py thông qua bài thực hành mẫu scripts/demos/mouse_events.py.\n"
        "• Vì sao quan trọng đối với đồ án?\n"
        "   Đồ án của chúng ta không dùng AI để tự nhận diện vỉa hè (vì rất tốn GPU và hay nhận diện sai mép). Thay vào đó, người vận hành chỉ cần click chuột một lần duy nhất để định nghĩa đa giác vỉa hè cho mỗi camera. Bài học này sẽ giúp bạn hiểu các tọa độ đỉnh vỉa hè từ đâu mà có!"
    )

    # --- PHẦN 2: KIẾN THỨC NỀN TẢNG ---
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r_h2 = h2.add_run("PHẦN 2: KIẾN THỨC NỀN TẢNG")
    r_h2.font.name = "Arial"
    r_h2.font.size = Pt(13)
    r_h2.font.bold = True
    r_h2.font.color.rgb = COLOR_PRIMARY

    p_p2 = doc.add_paragraph()
    p_p2.paragraph_format.line_spacing = Pt(14)
    p_p2.paragraph_format.space_after = Pt(6)
    p_p2.add_run(
        "1. Lập trình hướng sự kiện (Event-driven Programming):\n"
        "Bình thường code chạy tuần tự từ trên xuống dưới. Nhưng khi có giao diện tương tác, chương trình phải ở chế độ 'chờ đợi'. Khi người dùng click chuột, một sự kiện (Event) được phát ra và chương trình lập tức nhảy vào hàm xử lý sự kiện đó.\n\n"
        "2. Hàm gọi lại (Callback Function):\n"
        "Là một hàm do bạn viết ra, nhưng bạn KHÔNG trực tiếp gọi nó trong code. Bạn chỉ đem tên hàm đó 'đăng ký' với OpenCV bằng lệnh cv2.setMouseCallback(). Mỗi khi bạn click chuột lên cửa sổ video, OpenCV sẽ tự động gọi hàm đó và truyền tọa độ chính xác (x, y) của con trỏ chuột vào cho bạn.\n\n"
        "3. Các hàm vẽ đồ họa trực quan trong OpenCV:\n"
        "   • cv2.circle(ảnh, tâm_điểm, bán_kính, màu_BGR, độ_dày): Vẽ chấm tròn. Nếu độ dày = -1 thì tô kín hình tròn.\n"
        "   • cv2.line(ảnh, điểm_đầu, điểm_cuối, màu_BGR, độ_dày): Vẽ đoạn thẳng nối 2 điểm.\n"
        "   • cv2.putText(ảnh, nội_dung, tọa_độ, font, cỡ_chữ, màu_BGR, độ_dày): Viết chữ số lên ảnh.\n\n"
        "4. Chuẩn màu BGR của OpenCV (Blue - Green - Red):\n"
        "Khác với chuẩn RGB thông thường, OpenCV dùng thứ tự (B, G, R):\n"
        "   - Màu Đỏ: (0, 0, 255)\n"
        "   - Màu Xanh lá: (0, 255, 0)\n"
        "   - Màu Xanh dương: (255, 0, 0)\n"
        "   - Màu Vàng: (0, 255, 255)"
    )

    add_callout_box(
        doc,
        "Đa giác vỉa hè (ROI - Region of Interest) thực chất chỉ là một danh sách các điểm tọa độ 2D: "
        "[(x1, y1), (x2, y2), (x3, y3), (x4, y4)]. Người dùng click 4 điểm quanh mép vỉa hè, chương trình nối 4 điểm đó lại "
        "thành một hình tứ giác khép kín đại diện cho lối đi bộ!",
        "BẢN CHẤT VÙNG VỈA HÈ ROI",
        is_warning=False
    )

    # --- PHẦN 3: VÍ DỤ ĐỜI SỐNG ---
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(12)
    h3.paragraph_format.space_after = Pt(4)
    r_h3 = h3.add_run("PHẦN 3: VÍ DỤ ĐỜI SỐNG MINH HỌA")
    r_h3.font.name = "Arial"
    r_h3.font.size = Pt(13)
    r_h3.font.bold = True
    r_h3.font.color.rgb = COLOR_PRIMARY

    p_p3 = doc.add_paragraph()
    p_p3.paragraph_format.line_spacing = Pt(14)
    p_p3.paragraph_format.space_after = Pt(6)
    p_p3.add_run(
        "1. Ví dụ về Callback — Chuông cửa thông minh:\n"
        "Bạn không cần ngồi canh cửa 24/24. Bạn lắp một nút bấm chuông ở cổng và dặn chuông: 'Hễ có ai bấm nút (sự kiện), chuông hãy reo lên (hàm callback)'. OpenCV cũng vậy: Bạn đăng ký hàm mouse_callback, và mỗi khi người dùng click chuột, OpenCV tự động kích hoạt hàm đó.\n\n"
        "2. Ví dụ về vẽ đa giác vỉa hè — Trò chơi chấm điểm nối hình:\n"
        "Ngày bé bạn hay chơi trò nối các điểm số 1, 2, 3, 4 lại để tạo thành hình ngôi nhà. Trên video camera, người vận hành chấm điểm 1 ở góc trên vỉa hè, điểm 2 ở góc dưới, điểm 3 ở mép đường, điểm 4 ở chân tường. Khi nối 4 điểm lại, chúng ta đóng khung được toàn bộ diện tích vỉa hè dành cho người đi bộ!"
    )

    # --- PHẦN 4: LIÊN HỆ VỚI CODE THẬT ---
    h4 = doc.add_paragraph()
    h4.paragraph_format.space_before = Pt(12)
    h4.paragraph_format.space_after = Pt(4)
    r_h4 = h4.add_run("PHẦN 4: LIÊN HỆ VỚI MÃ NGUỒN THỰC TẾ (scripts/demos/mouse_events.py)")
    r_h4.font.name = "Arial"
    r_h4.font.size = Pt(13)
    r_h4.font.bold = True
    r_h4.font.color.rgb = COLOR_PRIMARY

    p_p4 = doc.add_paragraph()
    p_p4.paragraph_format.line_spacing = Pt(14)
    p_p4.paragraph_format.space_after = Pt(4)
    p_p4.add_run("Trích đoạn code thu thập tọa độ chuột và vẽ điểm nối đa giác trong tệp scripts/demos/mouse_events.py:")

    code_content = (
        'clicked_points = []  # Danh sách lưu tọa độ các điểm đã click\n\n'
        'def mouse_callback(event, x, y, flags, param):\n'
        '    global clicked_points\n'
        '    # Khi người dùng click chuột trái: lưu tọa độ (x, y)\n'
        '    if event == cv2.EVENT_LBUTTONDOWN:\n'
        '        clicked_points.append((x, y))\n'
        '        print(f"[CLICK TRÁI] Điểm #{len(clicked_points)}: (X={x}, Y={y})")\n'
        '    # Khi người dùng click chuột phải: xóa điểm gần nhất (Undo)\n'
        '    elif event == cv2.EVENT_RBUTTONDOWN:\n'
        '        if clicked_points:\n'
        '            clicked_points.pop()\n\n'
        '# Đăng ký hàm với OpenCV trên cửa sổ hiển thị\n'
        'cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)\n'
        'cv2.setMouseCallback(window_name, mouse_callback)\n\n'
        '# Vòng lặp vẽ các điểm và đường nối lên từng frame\n'
        'for idx, (px, py) in enumerate(clicked_points):\n'
        '    cv2.circle(frame, (px, py), 6, (0, 0, 255), -1)  # Chấm đỏ\n'
        '    cv2.putText(frame, f"P{idx+1}", (px + 10, py - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)\n\n'
        'if len(clicked_points) >= 2:\n'
        '    for i in range(len(clicked_points) - 1):\n'
        '        cv2.line(frame, clicked_points[i], clicked_points[i + 1], (0, 255, 0), 2)  # Nối đường xanh'
    )
    add_code_block(doc, code_content)

    # --- PHẦN 5: GIẢI THÍCH CODE TỪNG DÒNG ---
    h5 = doc.add_paragraph()
    h5.paragraph_format.space_before = Pt(12)
    h5.paragraph_format.space_after = Pt(4)
    r_h5 = h5.add_run("PHẦN 5: GIẢI THÍCH CODE TỪNG DÒNG VÀ Ý NGHĨA KỸ THUẬT")
    r_h5.font.name = "Arial"
    r_h5.font.size = Pt(13)
    r_h5.font.bold = True
    r_h5.font.color.rgb = COLOR_PRIMARY

    p_p5 = doc.add_paragraph()
    p_p5.paragraph_format.line_spacing = Pt(14)
    p_p5.paragraph_format.space_after = Pt(6)
    p_p5.add_run(
        "1. Biến toàn cục clicked_points:\n"
        "• clicked_points = []: Một danh sách (List) dùng để chứa các cặp tọa độ (x, y). Khi người dùng click 4 lần, danh sách này sẽ có dạng: [(100, 200), (450, 210), (520, 680), (80, 670)].\n\n"
        "2. Hàm Callback (mouse_callback):\n"
        "• def mouse_callback(event, x, y, flags, param): Khai báo đủ 5 tham số chuẩn theo yêu cầu của OpenCV. Trong đó event là mã sự kiện, còn x và y là tọa độ điểm ảnh chính xác tại vị trí con trỏ chuột.\n"
        "• global clicked_points: Từ khóa global báo cho Python biết rằng hàm này sẽ thay đổi danh sách clicked_points ở bên ngoài phạm vi hàm.\n"
        "• if event == cv2.EVENT_LBUTTONDOWN: Kiểm tra xem sự kiện có phải là bấm phím chuột trái hay không. Nếu đúng, lệnh clicked_points.append((x, y)) sẽ lưu điểm mới vào danh sách.\n"
        "• elif event == cv2.EVENT_RBUTTONDOWN: Hỗ trợ tính năng hoàn tác (Undo). Lệnh clicked_points.pop() sẽ xóa bỏ phần tử cuối cùng vừa thêm nếu người vận hành lỡ tay click nhầm.\n\n"
        "3. Đăng ký sự kiện:\n"
        "• cv2.setMouseCallback(window_name, mouse_callback): Bắt buộc cửa sổ video (window_name) phải được tạo trước bằng cv2.namedWindow(). Dòng lệnh này liên kết cửa sổ đó với hàm callback.\n\n"
        "4. Vòng lặp vẽ trực quan trên từng frame:\n"
        "• cv2.circle(frame, (px, py), 6, (0, 0, 255), -1): Vẽ một chấm tròn màu đỏ rực có bán kính 6 pixel tại vị trí đỉnh vừa click.\n"
        "• cv2.line(frame, clicked_points[i], clicked_points[i + 1], (0, 255, 0), 2): Lấy 2 điểm liên tiếp nối lại với nhau bằng một nét kẻ màu xanh lá cây dày 2 pixel, tạo thành các cạnh của đa giác vỉa hè."
    )

    # --- PHẦN 6: MINH HỌA QUÁ TRÌNH CHẠY ---
    h6 = doc.add_paragraph()
    h6.paragraph_format.space_before = Pt(12)
    h6.paragraph_format.space_after = Pt(4)
    r_h6 = h6.add_run("PHẦN 6: MINH HỌA QUÁ TRÌNH DỮ LIỆU BIẾN ĐỔI KHI NGƯỜI DÙNG CLICK")
    r_h6.font.name = "Arial"
    r_h6.font.size = Pt(13)
    r_h6.font.bold = True
    r_h6.font.color.rgb = COLOR_PRIMARY

    p_p6 = doc.add_paragraph()
    p_p6.paragraph_format.space_after = Pt(6)
    p_p6.add_run("Bảng mô phỏng tương tác thực tế của người vận hành khi thiết lập đa giác vỉa hè:")

    tbl_flow = doc.add_table(rows=5, cols=4)
    tbl_flow.alignment = WD_TABLE_ALIGNMENT.CENTER
    flow_headers = ["Thao tác người dùng", "Sự kiện kích hoạt", "Trạng thái mảng clicked_points", "Hiển thị trên màn hình"]
    for j, h in enumerate(flow_headers):
        c = tbl_flow.cell(0, j)
        set_cell_background(c, HEX_HEADER_BG)
        set_cell_margins(c, 100, 100, 120, 120)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    flow_rows = [
        ("Click trái điểm 1", "EVENT_LBUTTONDOWN\n(x=150, y=300)", "[(150, 300)]", "Xuất hiện chấm đỏ P1"),
        ("Click trái điểm 2", "EVENT_LBUTTONDOWN\n(x=600, y=320)", "[(150, 300), (600, 320)]", "Chấm P1, P2 + Đoạn thẳng nối P1-P2"),
        ("Click trái điểm 3 & 4", "EVENT_LBUTTONDOWN\n(x=700, y=700), ...", "4 điểm tọa độ hoàn chỉnh", "Khung đa giác 4 cạnh bao quanh vỉa hè"),
        ("Bấm phím 's' (Save)", "cv2.waitKey() == ord('s')", "Lưu sang file configs/roi.json", "Đóng file JSON sẵn sàng cho main.py dùng")
    ]
    for i, row in enumerate(flow_rows):
        for j, val in enumerate(row):
            c = tbl_flow.cell(i + 1, j)
            bg = HEX_BG_LIGHT if i % 2 == 0 else "FFFFFF"
            set_cell_background(c, bg)
            set_cell_margins(c, 80, 80, 100, 100)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9)
            r.font.color.rgb = COLOR_DARK
    set_table_borders(tbl_flow, HEX_BORDER)
    doc.add_paragraph()

    # --- PHẦN 7: LỖI THƯỜNG GẶP ---
    h7 = doc.add_paragraph()
    h7.paragraph_format.space_before = Pt(12)
    h7.paragraph_format.space_after = Pt(4)
    r_h7 = h7.add_run("PHẦN 7: LỖI THƯỜNG GẶP CỦA NGƯỜI MỚI BẮT ĐẦU VÀ CÁCH KHẮC PHỤC")
    r_h7.font.name = "Arial"
    r_h7.font.size = Pt(13)
    r_h7.font.bold = True
    r_h7.font.color.rgb = COLOR_PRIMARY

    p_p7 = doc.add_paragraph()
    p_p7.paragraph_format.line_spacing = Pt(14)
    p_p7.paragraph_format.space_after = Pt(6)
    p_p7.add_run(
        "1. Lỗi quên từ khóa 'global clicked_points':\n"
        "• Hiện tượng: Click chuột không thấy điểm nào được lưu lại.\n"
        "• Nguyên nhân: Trong Python, nếu bạn gán hoặc sửa một biến trong hàm mà không khai báo global, Python sẽ coi đó là biến cục bộ và hủy ngay sau khi thoát hàm.\n\n"
        "2. Nhầm lẫn mã màu BGR thay vì RGB:\n"
        "• Hiện tượng: Muốn vẽ nét kẻ màu Đỏ nhưng màn hình lại hiện màu Xanh lam.\n"
        "• Nguyên nhân: Truyền nhầm (255, 0, 0) thay vì (0, 0, 255). Hãy luôn nhớ thứ tự BGR: Blue - Green - Red.\n\n"
        "3. Gọi cv2.setMouseCallback trước khi tạo cửa sổ:\n"
        "• Hiện tượng: Báo lỗi OpenCV Error: Null pointer hoặc không bắt được chuột.\n"
        "• Khắc phục: Phải luôn gọi cv2.namedWindow(window_name) TRƯỚC khi gọi cv2.setMouseCallback(window_name, callback)."
    )

    # --- PHẦN 8: BÀI TẬP KIỂM TRA ---
    h8 = doc.add_paragraph()
    h8.paragraph_format.space_before = Pt(12)
    h8.paragraph_format.space_after = Pt(4)
    r_h8 = h8.add_run("PHẦN 8: BÀI TẬP KIỂM TRA HIỂU BÀI (TỰ ÔN TẬP)")
    r_h8.font.name = "Arial"
    r_h8.font.size = Pt(13)
    r_h8.font.bold = True
    r_h8.font.color.rgb = COLOR_PRIMARY

    p_p8 = doc.add_paragraph()
    p_p8.paragraph_format.line_spacing = Pt(14)
    p_p8.paragraph_format.space_after = Pt(10)
    p_p8.add_run(
        "Bạn hãy tự trả lời 3 câu hỏi dưới đây trước khi chuyển sang Bài học số 3:\n\n"
        "• Câu 1: Hàm mouse_callback có phải do chính bạn trực tiếp gọi trong vòng lặp while True không? Ai hoặc cái gì là bên thực sự kích hoạt hàm này?\n\n"
        "• Câu 2: Trong thư viện OpenCV, nếu muốn vẽ một vòng tròn màu XANH LÁ CÂY, bạn sẽ truyền bộ màu (B, G, R) có giá trị là bao nhiêu?\n\n"
        "• Câu 3: Để tạo thành một hình đa giác vỉa hè khép kín (Polygon ROI), danh sách clicked_points cần có tối thiểu bao nhiêu điểm tọa độ?"
    )

    doc.save(OUTPUT_FILE)
    print(f"[THÀNH CÔNG] Đã tạo tệp tài liệu bài học: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_document()
