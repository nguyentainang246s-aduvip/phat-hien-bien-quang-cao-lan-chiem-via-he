"""
Script xuất bản bài học Bài 5 thành file Word .docx chuyên nghiệp
Lưu vào thư mục: tai_lieu_hoc_tap/Bai_05_Phan_Quyet_Hinh_Hoc_va_Shapely_Overlap.docx
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
OUTPUT_FILE = str(OUTPUT_DIR / "Bai_05_Phan_Quyet_Hinh_Hoc_va_Shapely_Overlap.docx")

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
    r_b5 = p_title.add_run("BÀI 5: PHÁN QUYẾT HÌNH HỌC KÉP & TỶ LỆ ĐÈ LẤN VỚI SHAPELY\n")
    r_b5.font.name = "Arial"
    r_b5.font.size = Pt(18)
    r_b5.font.bold = True
    r_b5.font.color.rgb = COLOR_PRIMARY
    
    r_b5_sub = p_title.add_run("Công thức tính Overlap Ratio >= 30% và nguyên lý kết hợp Điều kiện kép (Dual-Condition)")
    r_b5_sub.font.name = "Arial"
    r_b5_sub.font.size = Pt(13)
    r_b5_sub.font.bold = True
    r_b5_sub.font.color.rgb = COLOR_SECONDARY

    # Bảng siêu dữ liệu
    tbl_meta = doc.add_table(rows=3, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Tệp mã nguồn tương ứng:", "violation/checker.py (Tham chiếu: reports/threshold_sweep_report.md)"),
        ("Cấp độ bài học:", "Giai đoạn 3 — Spatial Geometry & Violation Decision Engine"),
        ("Đối tượng học tập:", "Người học từ con số 0, cần hiểu cách tính diện tích giao cắt 2D và căn cứ chọn ngưỡng 30%")
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
        "• Tên bài học: Thuật toán tính diện tích giao cắt 2D bằng thư viện Shapely và Logic phán quyết vi phạm Điều kiện kép (Dual-Condition Logic).\n"
        "• Mục tiêu cốt lõi:\n"
        "   1. Hiểu công thức Overlap Ratio = Area(Box ∩ ROI) / Area(Box) và lý do tại sao mẫu số bắt buộc phải là diện tích Bounding Box (không dùng IoU, không dùng diện tích ROI).\n"
        "   2. Đọc hiểu toàn bộ module violation/checker.py: cách tạo hình học box_poly, sidewalk_poly, tính phần giao intersection.area.\n"
        "   3. Nắm vững căn cứ khoa học từ Báo cáo quét ngưỡng (Threshold Sweep): tại sao chọn ngưỡng 30% thay vì 10% hay 50% (F1-score đạt đỉnh 85.7%).\n"
        "• Vì sao quan trọng đối với đồ án?\n"
        "   Nếu chỉ kiểm tra chân tiếp đất (Bài 4), một tấm biển đặt trong nhà nhưng chỉ có 1 góc chân vô tình chạm nhẹ mép vỉa hè có thể bị phạt oan. Điều kiện tỷ lệ đè lấn >= 30% giúp định lượng chính xác mức độ lấn chiếm thực tế của tấm biển."
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
        "1. Thư viện hình học giải tích Shapely (shapely.geometry):\n"
        "OpenCV rất mạnh về xử lý ảnh, nhưng để tính diện tích phần giao nhau giữa một hình chữ nhật nghiêng và một đa giác phức tạp, thư viện Shapely là công cụ chuẩn công nghiệp số 1:\n"
        "   - sg.box(x1, y1, x2, y2): Tạo đối tượng hình chữ nhật từ Bounding Box.\n"
        "   - sg.Polygon(polygon_points): Tạo đối tượng hình đa giác từ danh sách các đỉnh vỉa hè.\n"
        "   - sidewalk_poly.intersection(box_poly): Tính phần giao nhau (phần diện tích chung mà tấm biển đè lên vỉa hè).\n\n"
        "2. Công thức tính Tỷ lệ đè lấn (Overlap Ratio):\n"
        "   Overlap Ratio = Area(Bounding Box ∩ Đa giác Vỉa hè) / Area(Bounding Box)\n\n"
        "3. Tại sao MẪU SỐ bắt buộc phải là Diện tích Bounding Box (Area_Box)? (ĐIỂM CỰC KỲ QUAN TRỌNG):\n"
        "   • Nếu chia cho Diện tích Vỉa hè (Area_ROI): Vỉa hè đường phố rất rộng (ví dụ 200.000 px²), tấm biển chỉ chiếm 2.000 px². Tỷ lệ sẽ chỉ là 1%, hệ thống sẽ không bao giờ phát hiện được vi phạm!\n"
        "   • Nếu dùng IoU (Intersection over Union): Vì ROI quá lớn so với Bounding Box, mẫu số Area(Box ∪ ROI) quá khổng lồ, khiến chỉ số IoU luôn xấp xỉ bằng 0!\n"
        "   • Chia cho Area_Box trả lời chính xác câu hỏi pháp lý: 'Bao nhiêu phần trăm diện tích của chính tấm biển này đang chiếm dụng không gian đi bộ?'\n\n"
        "4. Logic phán quyết Điều kiện kép (Dual-Condition Decision Rule):\n"
        "   is_violation = (is_base_inside AND overlap_ratio >= 0.30)\n"
        "   Một đối tượng CHỈ BỊ KẾT LUẬN VI PHẠM khi đồng thời thỏa mãn:\n"
        "   - Điều kiện 1 (Tiên quyết): Chân tiếp đất chạm vỉa hè (loại bỏ biển treo tường tầng 2).\n"
        "   - Điều kiện 2 (Đủ): Chiếm dụng ít nhất 30% diện tích không gian vỉa hè (loại bỏ biển chỉ chạm nhẹ góc mép)."
    )

    add_callout_box(
        doc,
        "Tại sao lại là ngưỡng 30% mà không phải 10% hay 50%? Trong báo cáo thực nghiệm quét ngưỡng "
        "(reports/threshold_sweep_report.md), tác giả đã quét từ 10% đến 60%. Tại ngưỡng 10-20%, hệ thống quá nhạy, "
        "báo sai nhiều biển chỉ nhô nhẹ 1 góc (Precision chỉ 75%). Tại 50-60%, hệ thống quá khắt khe, bỏ sót nhiều biển lấn vỉa hè thật. "
        "Ngưỡng 30% đạt điểm F1-Score cao nhất (85.7%) với Precision 100%!",
        "CĂN CỨ THỰC NGHIỆM CHỌN NGƯỠNG 30%",
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
        "Hãy tưởng tượng quy định đỗ xe ô tô trong ô kẻ vạch:\n"
        "• Trường hợp 1: Bạn đỗ xe trong gara nhà mình, nhưng do gara hẹp, mũi xe ô tô vô tình nhô ra khỏi vạch ranh giới vỉa hè khoảng 5cm (chỉ chiếm 2% diện tích xe) $\\rightarrow$ Công an phường có phạt bạn tội 'lấn chiếm lòng đường' không? Không, vì mức độ nhô ra không đáng kể, không cản trở người đi bộ.\n"
        "• Trường hợp 2: Bạn đỗ 50% thân xe chình ình trên vỉa hè, 4 bánh xe cắm trên vỉa hè $\\rightarrow$ Đã chạm chân trên vỉa hè VÀ lấn chiếm tới một nửa diện tích $\\rightarrow$ Chắc chắn bị lập biên bản phạt lấn chiếm!\n"
        "• Trong đồ án của chúng ta: Điều kiện kép (chân cắm + đè lấn >= 30%) được thiết kế y hệt như tư duy xử lý của một người cảnh sát trật tự đô thị ngoài đời thực!"
    )

    # --- PHẦN 4: LIÊN HỆ VỚI CODE THẬT ---
    h4 = doc.add_paragraph()
    h4.paragraph_format.space_before = Pt(12)
    h4.paragraph_format.space_after = Pt(4)
    r_h4 = h4.add_run("PHẦN 4: LIÊN HỆ VỚI MÃ NGUỒN THỰC TẾ (violation/checker.py)")
    r_h4.font.name = "Arial"
    r_h4.font.size = Pt(13)
    r_h4.font.bold = True
    r_h4.font.color.rgb = COLOR_PRIMARY

    p_p4 = doc.add_paragraph()
    p_p4.paragraph_format.line_spacing = Pt(14)
    p_p4.paragraph_format.space_after = Pt(4)
    p_p4.add_run("Đoạn mã cốt lõi tính diện tích giao cắt và ra phán quyết vi phạm trong tệp violation/checker.py (dòng 81-115):")

    code_checker_part2 = (
        'import shapely.geometry as sg\n\n'
        '# 1. Khởi tạo đối tượng hình học Shapely từ Bbox và Đa giác vỉa hè\n'
        'box_poly = sg.box(x1, y1, x2, y2)\n'
        'sidewalk_poly = sg.Polygon(polygon_points)\n\n'
        '# Tự động sửa lỗi nếu đa giác bị tự cắt (self-intersecting)\n'
        'if not sidewalk_poly.is_valid:\n'
        '    sidewalk_poly = sidewalk_poly.buffer(0)\n\n'
        '# 2. Tính tỷ lệ diện tích giao nhau\n'
        'overlap_ratio = 0.0\n'
        'if box_poly.area > 0:\n'
        '    intersection = sidewalk_poly.intersection(box_poly)\n'
        '    # Mẫu số là diện tích Bounding Box\n'
        '    overlap_ratio = float(intersection.area / box_poly.area)\n\n'
        '# 3. Phán quyết vi phạm theo ĐIỀU KIỆN KÉP (Dual-Condition)\n'
        'is_violation = (is_base_inside and overlap_ratio >= self.threshold)\n\n'
        'overlap_pct = round(overlap_ratio * 100, 1)\n'
        'if is_violation:\n'
        '    status_text = f"VI PHAM LAN CHIEM ({overlap_pct}%)"\n'
        'elif is_base_inside and overlap_ratio < self.threshold:\n'
        '    status_text = f"CHAM MEP VIA HE ({overlap_pct}%)"\n'
        'else:\n'
        '    status_text = f"HOP LE (NGOAI VIA HE)"'
    )
    add_code_block(doc, code_checker_part2)

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
        "1. Tự động sửa lỗi đa giác (sidewalk_poly.buffer(0)):\n"
        "• Khi người dùng vẽ ROI, các đỉnh có thể tạo thành đa giác lỗi hình học (đa giác tự cắt - self-intersecting polygon). Nếu để nguyên, Shapely sẽ văng lỗi TopologicalError.\n"
        "• Lệnh buffer(0) là kỹ thuật kinh điển trong GIS (Hệ thông tin địa lý), giúp tự động gỡ các nút thắt hình học và biến đa giác thành dạng hợp lệ (valid polygon) mà không làm thay đổi diện tích.\n\n"
        "2. Tính phần giao nhau (sidewalk_poly.intersection(box_poly)):\n"
        "• Lệnh intersection() tìm ra đa giác con chung giữa tấm biển và vỉa hè. Biến intersection.area chính là diện tích pixel của phần biển đang đè lên mặt gạch vỉa hè.\n\n"
        "3. Công thức tính tỷ lệ (overlap_ratio = intersection.area / box_poly.area):\n"
        "• box_poly.area chính là diện tích toàn bộ tấm biển: (x2 - x1) * (y2 - y1).\n"
        "• overlap_ratio là một số thực từ 0.0 đến 1.0 (ví dụ 0.64 tương đương 64% diện tích tấm biển đè lên vỉa hè).\n\n"
        "4. Phán quyết Điều kiện kép (is_violation = is_base_inside and overlap_ratio >= self.threshold):\n"
        "• Chỉ khi CẢ HAI điều kiện cùng mang giá trị True thì is_violation mới bằng True. Nếu thiếu một trong hai, biến này sẽ mang giá trị False ngay lập tức!"
    )

    # --- PHẦN 6: MINH HỌA QUÁ TRÌNH CHẠY ---
    h6 = doc.add_paragraph()
    h6.paragraph_format.space_before = Pt(12)
    h6.paragraph_format.space_after = Pt(4)
    r_h6 = h6.add_run("PHẦN 6: MINH HỌA QUÁ TRÌNH PHÁN XỬ ĐIỀU KIỆN KÉP")
    r_h6.font.name = "Arial"
    r_h6.font.size = Pt(13)
    r_h6.font.bold = True
    r_h6.font.color.rgb = COLOR_PRIMARY

    p_p6 = doc.add_paragraph()
    p_p6.paragraph_format.space_after = Pt(6)
    p_p6.add_run("Bảng mô phỏng kết quả phán quyết đối với các tình huống thực tế ngoài đời:")

    tbl_flow = doc.add_table(rows=5, cols=5)
    tbl_flow.alignment = WD_TABLE_ALIGNMENT.CENTER
    flow_headers = ["Tình huống quan sát", "Điều kiện 1: Chân tiếp đất?", "Điều kiện 2: Overlap Ratio?", "Kết luận vi phạm?", "Trạng thái hiển thị"]
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
        ("Biển standee đặt chình ình giữa lối đi", "True (Cắm chân trên vỉa hè)", "85.4% (>= 30%)", "VI PHẠM (True)", "VI PHAM LAN CHIEM (85.4%)"),
        ("Biển đặt trong nhà, nhô mép ra 5%", "True (Chạm nhẹ mép hè)", "5.2% (< 30%)", "HỢP LỆ (False)", "CHAM MEP VIA HE (5.2%)"),
        ("Biển hiệu treo tường tầng 2 nhô ra hè", "False (Gắn trên tường nhà)", "92.0% (Bóng trùm vỉa hè)", "HỢP LỆ (False)", "HOP LE (NGOAI VIA HE)"),
        ("Biển đặt dưới lòng đường mép ngoài", "False (Chân dưới lòng đường)", "12.0% (< 30%)", "HỢP LỆ (False)", "HOP LE (NGOAI VIA HE)")
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
            if j == 3 and "VI PHẠM" in val:
                r.font.bold = True
                r.font.color.rgb = COLOR_RED
            else:
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
        "1. Lỗi nhầm lẫn giữa Overlap Ratio và IoU (Intersection over Union):\n"
        "• Sai lầm: Đi bảo vệ đồ án nói rằng 'hệ thống dùng IoU để tính tỷ lệ lấn chiếm'.\n"
        "• Thực tế: IoU dùng mẫu số là Diện tích HỢP (Area_Box ∪ Area_ROI). Vì vỉa hè quá rộng, IoU luôn tiệm cận 0! Bạn phải khẳng định rõ ràng: Đồ án dùng Overlap Ratio = Area_Intersection / Area_Box!\n\n"
        "2. Quên kiểm tra box_poly.area > 0:\n"
        "• Nguyên nhân: Khi tọa độ Bounding Box bị lỗi khiến x1 == x2 hoặc y1 == y2, diện tích box_poly.area = 0. Nếu không có lệnh if box_poly.area > 0, chương trình sẽ sập ngay vì lỗi chia cho 0 (ZeroDivisionError)."
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
        "Bạn hãy tự trả lời 3 câu hỏi dưới đây trước khi chuyển sang Bài học số 6:\n\n"
        "• Câu 1: Tại sao trong công thức Overlap Ratio, mẫu số bắt buộc phải là Diện tích Bounding Box (box_poly.area) mà KHÔNG ĐƯỢC chia cho Diện tích Vỉa hè (sidewalk_poly.area) hay dùng chỉ số IoU?\n\n"
        "• Câu 2: Giả sử một tấm biển có tỷ lệ đè lấn lên vỉa hè là 80% (overlap_ratio = 0.80), nhưng điểm chân tiếp đất của nó nằm ngoài vỉa hè (is_base_inside = False). Hệ thống có kết luận biển này vi phạm không? Tại sao?\n\n"
        "• Câu 3: Dựa trên thực nghiệm quét ngưỡng (threshold sweep), lý do vì sao hệ thống lại chọn ngưỡng vi phạm là 30% thay vì chọn ngưỡng 10% hay 60%?"
    )

    doc.save(OUTPUT_FILE)
    print(f"[THÀNH CÔNG] Đã tạo tệp tài liệu bài học: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_document()
