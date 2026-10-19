"""
Script xuất bản bài học Bài 4 thành file Word .docx chuyên nghiệp
Lưu vào thư mục: tai_lieu_hoc_tap/Bai_04_Da_Giac_Via_He_va_Diem_Tiep_Dat.docx
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
OUTPUT_FILE = str(OUTPUT_DIR / "Bai_04_Da_Giac_Via_He_va_Diem_Tiep_Dat.docx")

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
    r_b4 = p_title.add_run("BÀI 4: ĐA GIÁC VỈA HÈ (ROI) & THUẬT TOÁN ĐIỂM TIẾP ĐẤT\n")
    r_b4.font.name = "Arial"
    r_b4.font.size = Pt(18)
    r_b4.font.bold = True
    r_b4.font.color.rgb = COLOR_PRIMARY
    
    r_b4_sub = p_title.add_run("Kiểm tra vị trí tiếp xúc mặt đất của biển quảng cáo với thuật toán Point-in-Polygon")
    r_b4_sub.font.name = "Arial"
    r_b4_sub.font.size = Pt(13)
    r_b4_sub.font.bold = True
    r_b4_sub.font.color.rgb = COLOR_SECONDARY

    # Bảng siêu dữ liệu
    tbl_meta = doc.add_table(rows=3, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Tệp mã nguồn tương ứng:", "roi/roi_manager.py, violation/checker.py (Tham chiếu: scripts/demos/check_violation_spatial.py)"),
        ("Cấp độ bài học:", "Giai đoạn 3 — Spatial Reasoning & Point-in-Polygon Algorithm"),
        ("Đối tượng học tập:", "Người học từ con số 0, cần hiểu cách xác định chân biển có cắm trên vỉa hè không")
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
        "• Tên bài học: Quản lý đa giác vỉa hè (Multi-ROI) và Thuật toán kiểm tra điểm nằm trong đa giác (cv2.pointPolygonTest).\n"
        "• Mục tiêu cốt lõi:\n"
        "   1. Hiểu cách đọc file cấu hình vỉa hè JSON và cơ chế tự động co giãn tọa độ (Auto-Scale Resolution) trong roi/roi_manager.py.\n"
        "   2. Hiểu nguyên lý vật lý của Điểm tiếp xúc mặt đất (Ground Contact Point): tại sao lại lấy đáy Bounding Box (y = y2).\n"
        "   3. Nắm vững thuật toán cv2.pointPolygonTest và cơ chế kiểm tra 3 điểm chân đế (Trái, Giữa, Phải) có dung sai 15px trong violation/checker.py.\n"
        "• Vì sao quan trọng đối với đồ án?\n"
        "   Trong góc nhìn camera CCTV 2D chiếu xiên, một biển quảng cáo gắn trên tường tầng 2 có thể vô tình đè lên phần hình ảnh vỉa hè trong ảnh. Nhưng chân của nó KHÔNG chạm vỉa hè! Thuật toán kiểm tra điểm tiếp đất là điều kiện tiên quyết loại bỏ 100% các biển treo trên cao không vi phạm."
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
        "1. Bản chất hình học của Vùng quan tâm Vỉa hè (Sidewalk ROI):\n"
        "Được lưu dưới dạng file JSON (ví dụ configs/roi_camera1.json) gồm camera_id, độ phân giải gốc lúc vẽ (width, height), và mảng các đỉnh [[x1, y1], [x2, y2], [x3, y3], [x4, y4]].\n\n"
        "2. Điểm tiếp xúc mặt đất (Ground Contact Point - P_base):\n"
        "Camera CCTV nhìn từ trên cao chúc xuống. Một vật thể đứng trên mặt đất (như biển standee, biển hộp đèn chân sắt) có điểm tiếp xúc với mặt sàn tại CẠNH ĐÁY của Bounding Box:\n"
        "   - Tọa độ Y đáy: y = y2.\n"
        "   - Trung điểm chân đế: base_x = (x1 + x2) / 2, base_y = y2.\n"
        "   - Chân trái: (x1, y2); Chân phải: (x2, y2).\n\n"
        "3. Thuật toán Point-in-Polygon (cv2.pointPolygonTest):\n"
        "Là thuật toán kinh điển trong đồ họa máy tính (dựa trên thuật toán Bắn tia Ray Casting), kiểm tra xem một điểm P(x, y) nằm trong, nằm ngoài hay nằm trên cạnh của đa giác:\n"
        "   - Trả về > 0: Điểm nằm HOÀN TOÀN BÊN TRONG đa giác vỉa hè.\n"
        "   - Trả về = 0: Điểm nằm NGAY TRÊN ĐƯỜNG BIÊN mép vỉa hè.\n"
        "   - Trả về < 0: Điểm nằm NGOÀI vỉa hè (trên lòng đường hoặc trong nhà).\n"
        "   - Nếu đặt tham số measureDist=True: Nó trả về khoảng cách hình học ngắn nhất từ điểm P đến mép đa giác (tính bằng pixel). Giá trị âm thể hiện khoảng cách hụt ngoài mép."
    )

    add_callout_box(
        doc,
        "Đồ án cải tiến cơ chế kiểm tra chân tiếp đất: thay vì chỉ kiểm tra 1 điểm tâm đáy duy nhất, "
        "violation/checker.py kiểm tra 3 điểm (Chân trái, Chân giữa, Chân phải) kèm dung sai mép 15 pixel. "
        "Chỉ cần 1 trong 3 điểm chạm vỉa hè là thỏa mãn điều kiện cắm chân! Điều này giúp không bỏ sót biển đặt sát mép vỉa hè.",
        "CẢI TIẾN 3 ĐIỂM TIẾP ĐẤT CỦA ĐỒ ÁN",
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
        "Hãy tưởng tượng bạn vẽ một ô phấn hình chữ nhật trên sân nhà và đặt tên là 'Vùng vỉa hè':\n"
        "• Trường hợp 1: Có người đặt một chiếc quạt cây đứng trên sân. Chiếc chân đế hình tròn của quạt chạm đất nằm lọt thỏm trong ô phấn $\\rightarrow$ Chân quạt chạm vỉa hè!\n"
        "• Trường hợp 2: Có một chiếc quạt trần treo trên trần nhà, bóng của chiếc quạt trần in xuống trúng ô phấn $\\rightarrow$ Nếu chỉ nhìn 'bóng' (hình chiếu 2D) thì tưởng quạt đè lên ô phấn, nhưng chân quạt có chạm sân không? Không hề! Quạt gắn trên trần nhà!\n"
        "• Trong camera CCTV cũng y hệt: Biển hiệu tầng 2 tầng 3 nhô ra khoảng không vỉa hè nhưng chân gắn chặt vào tường nhà, chỉ có biển đặt chân cắm trên nền gạch mới là đối tượng lấn chiếm vỉa hè!"
    )

    # --- PHẦN 4: LIÊN HỆ VỚI CODE THẬT ---
    h4 = doc.add_paragraph()
    h4.paragraph_format.space_before = Pt(12)
    h4.paragraph_format.space_after = Pt(4)
    r_h4 = h4.add_run("PHẦN 4: LIÊN HỆ VỚI MÃ NGUỒN THỰC TẾ (roi/roi_manager.py & violation/checker.py)")
    r_h4.font.name = "Arial"
    r_h4.font.size = Pt(13)
    r_h4.font.bold = True
    r_h4.font.color.rgb = COLOR_PRIMARY

    p_p4 = doc.add_paragraph()
    p_p4.paragraph_format.line_spacing = Pt(14)
    p_p4.paragraph_format.space_after = Pt(4)
    p_p4.add_run("1. Hàm kiểm tra điểm nằm trong vỉa hè trong roi/roi_manager.py (dòng 120-126):")

    code_roi = (
        'def is_point_inside(self, point: tuple) -> bool:\n'
        '    """Kiểm tra điểm (x, y) có nằm trong BẤT KỲ vùng vỉa hè nào không"""\n'
        '    for pts in self.polygons:\n'
        '        pts_arr = np.array(pts, dtype=np.int32)\n'
        '        # cv2.pointPolygonTest >= 0 nghĩa là nằm TRONG hoặc TRÊN CẠNH vỉa hè\n'
        '        if cv2.pointPolygonTest(pts_arr, point, measureDist=False) >= 0:\n'
        '            return True\n'
        '    return False'
    )
    add_code_block(doc, code_roi)

    p_p4_2 = doc.add_paragraph()
    p_p4_2.paragraph_format.space_after = Pt(4)
    p_p4_2.add_run("2. Cơ chế kiểm tra 3 điểm tiếp đất với dung sai 15px trong violation/checker.py (dòng 60-77):")

    code_checker = (
        'x1, y1, x2, y2 = box\n\n'
        '# Xác định tọa độ 3 điểm chân tiếp đất của Bounding Box\n'
        'pt_left = (int(x1), int(y2))                    # Chân góc trái\n'
        'pt_center = (int((x1 + x2) / 2), int(y2))       # Chân giữa\n'
        'pt_right = (int(x2), int(y2))                   # Chân góc phải\n\n'
        'pts_array = np.array(polygon_points, dtype=np.int32)\n'
        'base_margin = 15.0  # Dung sai mép 15 pixel cho phép người dùng click lệch nhẹ\n\n'
        'left_inside = cv2.pointPolygonTest(pts_array, pt_left, measureDist=True) >= -base_margin\n'
        'center_inside = cv2.pointPolygonTest(pts_array, pt_center, measureDist=True) >= -base_margin\n'
        'right_inside = cv2.pointPolygonTest(pts_array, pt_right, measureDist=True) >= -base_margin\n\n'
        '# Thỏa mãn nếu BẤT KỲ điểm nào trong 3 điểm tiếp đất trên vỉa hè\n'
        'is_base_inside = left_inside or center_inside or right_inside'
    )
    add_code_block(doc, code_checker)

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
        "1. Tọa độ 3 điểm tiếp đất:\n"
        "• pt_center = (int((x1 + x2) / 2), int(y2)): Tâm đáy của khung bao. x là trung bình cộng giữa mép trái và mép phải, y là cạnh đáy y2.\n"
        "• pt_left và pt_right: Hai góc chân đáy của biển hiệu (ví dụ chân sắt standee thường có 2 chân choãi ra hai bên).\n\n"
        "2. Dung sai mép (base_margin = 15.0):\n"
        "• Ngoài thực tế, khi người vận hành dùng chuột chấm điểm vỉa hè ở mép dưới màn hình, tay người thường hụt 3-5 pixel so với mép thực tế. Nếu không có dung sai, một tấm biển đặt ngay sát mép sẽ bị tính là 'nằm ngoài' và bỏ sót vi phạm.\n"
        "• Khi đặt measureDist=True, nếu điểm cách mép ngoài 10px thì hàm trả về -10.0. Vì -10.0 >= -15.0 nên hệ thống vẫn công nhận chân biển nằm trên vỉa hè!\n\n"
        "3. Cơ chế tự động co giãn độ phân giải (Auto-Scale trong roi_manager.py):\n"
        "• scale_x = target_width / float(orig_width)\n"
        "• scale_y = target_height / float(orig_height)\n"
        "• Ý nghĩa: Nếu bạn vẽ vỉa hè trên video 720p (1280x720) nhưng sau này camera nâng cấp lên Full HD 1080p (1920x1080), ROIManager tự động nhân tỷ lệ scale_x = 1.5 và scale_y = 1.5 cho toàn bộ các đỉnh đa giác, không bắt người dùng phải vẽ lại từ đầu!"
    )

    # --- PHẦN 6: MINH HỌA QUÁ TRÌNH CHẠY ---
    h6 = doc.add_paragraph()
    h6.paragraph_format.space_before = Pt(12)
    h6.paragraph_format.space_after = Pt(4)
    r_h6 = h6.add_run("PHẦN 6: MINH HỌA QUÁ TRÌNH PHÁN XỬ ĐIỂM TIẾP ĐẤT")
    r_h6.font.name = "Arial"
    r_h6.font.size = Pt(13)
    r_h6.font.bold = True
    r_h6.font.color.rgb = COLOR_PRIMARY

    p_p6 = doc.add_paragraph()
    p_p6.paragraph_format.space_after = Pt(6)
    p_p6.add_run("Bảng mô phỏng kết quả kiểm tra điểm tiếp đất đối với các loại biển hiệu khác nhau:")

    tbl_flow = doc.add_table(rows=4, cols=4)
    tbl_flow.alignment = WD_TABLE_ALIGNMENT.CENTER
    flow_headers = ["Đối tượng quan sát", "Tọa độ đáy chân (y = y2)", "pointPolygonTest", "Kết luận chân tiếp đất"]
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
        ("Biển standee chân sắt\nđặt giữa vỉa hè", "Tâm chân: (450, 500)\nNằm giữa ô đa giác", "dist = +45.2 px\n(Lớn hơn 0)", "is_base_inside = True\n-> Thỏa mãn điều kiện 1"),
        ("Biển vẫy gắn tường\ntreo trên cao tầng 2", "Tâm chân: (150, 200)\nChân gắn vào tường", "dist = -85.0 px\n(Nhỏ hơn -15px)", "is_base_inside = False\n-> Loại ngay, không phạt nhầm"),
        ("Biển đặt mép ngoài\nchớm lấn nhẹ mép hè", "Tâm chân: (605, 520)\nHụt ngoài mép 6px", "dist = -6.0 px\n(-6 >= -15px dung sai)", "is_base_inside = True\n-> Cứu được ca vi phạm sát mép")
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
        "1. Lỗi kiểm tra tâm hình hộp chữ nhật thay vì chân đáy:\n"
        "• Sai lầm: Lấy tâm đối tượng center = ((x1+x2)/2, (y1+y2)/2) để kiểm tra pointPolygonTest.\n"
        "• Hậu quả: Một biển quảng cáo treo trên cao nhưng có tâm rơi vào vùng vỉa hè sẽ bị kết luận nhầm là vi phạm!\n"
        "• Khắc phục: Phải luôn lấy cạnh đáy y = y2 (điểm tiếp xúc mặt đất) để kiểm tra.\n\n"
        "2. Đa giác vỉa hè bị tự cắt chéo (Self-intersecting polygon):\n"
        "• Sai lầm: Người vận hành click chuột theo hình chữ X (chéo cánh bướm) thay vì click theo vòng kim đồng hồ.\n"
        "• Khắc phục: Luôn hướng dẫn click lần lượt theo chiều kim đồng hồ quanh mép vỉa hè."
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
        "Bạn hãy tự trả lời 3 câu hỏi dưới đây trước khi chuyển sang Bài học số 5:\n\n"
        "• Câu 1: Hàm cv2.pointPolygonTest(polygon, point, measureDist=False) trả về các giá trị >0, =0, <0 có ý nghĩa gì đối với vị trí của điểm point so với vỉa hè?\n\n"
        "• Câu 2: Tại sao khi kiểm tra chân biển hiệu tiếp đất, ta phải lấy y = y2 (cạnh đáy) mà KHÔNG ĐƯỢC lấy tâm hình hộp y = (y1 + y2) / 2?\n\n"
        "• Câu 3: Mục đích của biến base_margin = 15.0 (dung sai 15 pixel) trong violation/checker.py là gì?"
    )

    doc.save(OUTPUT_FILE)
    print(f"[THÀNH CÔNG] Đã tạo tệp tài liệu bài học: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_document()
