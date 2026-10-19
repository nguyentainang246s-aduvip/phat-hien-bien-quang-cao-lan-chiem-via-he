"""
Script xuất bản bài học Bài 6 thành file Word .docx chuyên nghiệp
Lưu vào thư mục: tai_lieu_hoc_tap/Bai_06_Theo_Doi_Vat_The_ByteTrack_va_Track_ID.docx
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
OUTPUT_FILE = str(OUTPUT_DIR / "Bai_06_Theo_Doi_Vat_The_ByteTrack_va_Track_ID.docx")

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
    r_b6 = p_title.add_run("BÀI 6: THEO DÕI ĐA VẬT THỂ BYTETRACK & CẤP PHÁT TRACK ID\n")
    r_b6.font.name = "Arial"
    r_b6.font.size = Pt(18)
    r_b6.font.bold = True
    r_b6.font.color.rgb = COLOR_PRIMARY
    
    r_b6_sub = p_title.add_run("Cách hệ thống duy trì 'trí nhớ' liên tục cho từng tấm biển qua chuỗi khung hình video")
    r_b6_sub.font.name = "Arial"
    r_b6_sub.font.size = Pt(13)
    r_b6_sub.font.bold = True
    r_b6_sub.font.color.rgb = COLOR_SECONDARY

    # Bảng siêu dữ liệu
    tbl_meta = doc.add_table(rows=3, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Tệp mã nguồn tương ứng:", "tracking/tracker.py (Tham chiếu: scripts/demos/demo_tracking.py)"),
        ("Cấp độ bài học:", "Giai đoạn 4 — Multi-Object Tracking & Temporal Association"),
        ("Đối tượng học tập:", "Người học từ con số 0, cần hiểu tại sao Object Detection cần có Tracker đi kèm")
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
        "• Tên bài học: Thuật toán theo dõi đa đối tượng ByteTrack (Multi-Object Tracking) và cơ chế cấp phát mã định danh Track ID.\n"
        "• Mục tiêu cốt lõi:\n"
        "   1. Hiểu 'căn bệnh mất trí nhớ' của Object Detection: tại sao chỉ dùng YOLO thì không thể theo dõi đối tượng theo thời gian.\n"
        "   2. Hiểu nguyên lý hoạt động của ByteTrack: Bộ lọc Kalman (dự đoán vị trí) và Khớp nối 2 tầng (cứu các vật thể bị che khuất tạm thời).\n"
        "   3. Đọc hiểu module tracking/tracker.py: ý nghĩa của tham số persist=True và cách lấy track_id từ kết quả của Ultralytics.\n"
        "• Vì sao quan trọng đối với đồ án?\n"
        "   Nếu không có Track ID, mỗi giây trôi qua hệ thống sẽ nhìn 1 chiếc biển như 30 vật thể hoàn toàn xa lạ, dẫn đến gửi 30 cảnh báo phạt trùng lặp mỗi giây! Track ID chính là 'chứng minh thư' để theo dõi biển hiệu trong Bài 7."
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
        "1. Vấn đề của Object Detection đơn thuần (Detection Flickering):\n"
        "Mô hình YOLO xử lý từng khung hình độc lập. Ở frame 1 nó thấy 1 Bounding Box, ở frame 2 nó lại thấy 1 Bounding Box. Nhưng AI KHÔNG CÓ BỘ NHỚ để biết hai chiếc hộp này có phải là cùng 1 tấm biển hay không. Nó không biết tấm biển này đã ở đây bao lâu, và đang đứng yên hay đang di chuyển.\n\n"
        "2. Khái niệm Theo dõi đa vật thể (Multi-Object Tracking - MOT):\n"
        "MOT là bài toán gán một mã số nguyên duy nhất (Track ID: 1, 2, 3...) cho từng vật thể khi nó xuất hiện, và duy trì chính xác mã số đó qua từng khung hình tiếp theo, ngay cả khi vật thể hơi rung lắc hoặc bị người đi ngang che khuất một phần.\n\n"
        "3. Hai trụ cột của thuật toán ByteTrack:\n"
        "   • Bộ lọc Kalman (Kalman Filter): Dựa vào vị trí và vận tốc ở các khung hình trước để DỰ ĐOÁN tọa độ của vật thể ở khung hình tiếp theo.\n"
        "   • Khớp nối 2 tầng (Two-stage Association - Điểm đột phá của ByteTrack):\n"
        "     - Tầng 1: Ghép cặp các hộp có độ tin cậy cao (conf >= 0.5) với các vệt theo dõi hiện có.\n"
        "     - Tầng 2: Thay vì vứt bỏ các hộp điểm thấp (0.1 <= conf < 0.5) như các tracker truyền thống, ByteTrack tận dụng chúng để tìm lại các vật thể bị che khuất một phần (Occlusion). Nhờ đó, biển bị xe máy hay người đi bộ che mất một nửa vẫn giữ nguyên được Track ID mà không bị nhảy ID mới!\n\n"
        "4. Tham số persist=True (CỰC KỲ QUAN TRỌNG):\n"
        "Trong thư viện Ultralytics, khi gọi model.track(), bắt buộc phải bật persist=True để thông báo cho hệ thống: 'Hãy giữ lại trạng thái của bộ lọc Kalman từ khung hình trước sang khung hình này'."
    )

    add_callout_box(
        doc,
        "Tại sao trong tracking/tracker.py, conf_threshold lại đặt là 0.15 (15%) thay vì 0.35 như detector.py? "
        "Vì ByteTrack có cơ chế khớp nối 2 tầng! Đặt conf=0.15 giúp bắt trọn vẹn cả các biển nhỏ ở cự ly xa hoặc bị che khuất một phần, "
        "sau đó ByteTrack sẽ dùng logic Kalman Filter để lọc sạch các phát hiện rác mà không lo báo sai!",
        "LÝ DO ĐỒ ÁN ĐẶT CONF = 0.15 CHO TRACKER",
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
        "Hãy tưởng tượng một người phục vụ quán cà phê đang trông xe:\n"
        "• Nếu người phục vụ 'mất trí nhớ': Cứ mỗi giây quay sang nhìn chiếc xe máy, anh ta lại ngạc nhiên: 'Ô, có một chiếc xe mới xuất hiện!'. Trong 1 phút, anh ta ghi nhận 60 chiếc xe máy khác nhau và phát 60 cái vé xe cho cùng 1 vị khách $\\rightarrow$ Hỗn loạn!\n"
        "• Nếu người phục vụ có 'ByteTrack': Khi chiếc xe máy dựng xuống, anh ta bấm một chiếc thẻ số: 'Xe này mang số #5'. Dù có người đi bộ đi ngang che khuất chiếc xe trong 1-2 giây, khi người đó bước qua, anh phục vụ vẫn nhớ như in: 'Đó vẫn là chiếc xe số #5 của khách quen' $\\rightarrow$ Không bao giờ bị phát trùng vé!\n"
        "• Trong đồ án: ByteTrack chính là người bấm thẻ số định danh cho từng chiếc biển quảng cáo!"
    )

    # --- PHẦN 4: LIÊN HỆ VỚI CODE THẬT ---
    h4 = doc.add_paragraph()
    h4.paragraph_format.space_before = Pt(12)
    h4.paragraph_format.space_after = Pt(4)
    r_h4 = h4.add_run("PHẦN 4: LIÊN HỆ VỚI MÃ NGUỒN THỰC TẾ (tracking/tracker.py)")
    r_h4.font.name = "Arial"
    r_h4.font.size = Pt(13)
    r_h4.font.bold = True
    r_h4.font.color.rgb = COLOR_PRIMARY

    p_p4 = doc.add_paragraph()
    p_p4.paragraph_format.line_spacing = Pt(14)
    p_p4.paragraph_format.space_after = Pt(4)
    p_p4.add_run("Mã nguồn bọc thuật toán ByteTrack trong tệp tracking/tracker.py (dòng 68-100):")

    code_tracker = (
        '# 1. Gọi ByteTrack theo dõi liên tục giữa các khung hình (persist=True)\n'
        'results = self.model.track(\n'
        '    source=frame,\n'
        '    persist=True,\n'
        '    tracker=self.tracker_type,  # "bytetrack.yaml"\n'
        '    conf=target_conf,           # 0.15\n'
        '    imgsz=target_imgsz,         # 960\n'
        '    verbose=False\n'
        ')\n\n'
        'tracked_objects = []\n'
        'if len(results) > 0 and results[0].boxes is not None:\n'
        '    boxes = results[0].boxes\n'
        '    for box in boxes:\n'
        '        xyxy = box.xyxy[0].cpu().numpy().astype(int)\n'
        '        conf = float(box.conf[0].cpu().numpy())\n'
        '        cls_id = int(box.cls[0].cpu().numpy())\n\n'
        '        # 2. Trích xuất mã định danh Track ID do ByteTrack sinh ra\n'
        '        if box.id is not None:\n'
        '            track_id = int(box.id[0].cpu().numpy())\n'
        '        else:\n'
        '            track_id = -1  # Vật thể mới chớm xuất hiện chưa đủ tin cậy để gán ID\n\n'
        '        tracked_objects.append({\n'
        '            "track_id": track_id,\n'
        '            "box": (int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])),\n'
        '            "conf": round(conf, 2),\n'
        '            "class_id": cls_id,\n'
        '            "class_name": self.class_names.get(cls_id, "bien_quang_cao")\n'
        '        })'
    )
    add_code_block(doc, code_tracker)

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
        "1. Lệnh self.model.track(..., persist=True):\n"
        "• Thay vì gọi model.predict() như ở Bài 3, chúng ta gọi model.track(). Hàm này thực hiện cả 2 việc trong 1 bước: Phát hiện vật thể (Detection) + Ghép nối vệt theo dõi (ByteTrack).\n"
        "• persist=True: Bắt buộc phải có để thuật toán ghi nhớ lịch sử tọa độ của các khung hình trước.\n\n"
        "2. Biến box.id:\n"
        "• Khi chỉ dùng YOLO thường, thuộc tính box.id luôn là None.\n"
        "• Khi chạy qua ByteTrack, box.id sẽ chứa mã định danh (ví dụ: tensor([3])). Lệnh int(box.id[0].cpu().numpy()) sẽ trích xuất ra con số nguyên 3 (tức Track #3).\n\n"
        "3. Xử lý khi box.id is None (track_id = -1):\n"
        "• Khi một vật thể vừa mới xuất hiện ở khung hình đầu tiên, ByteTrack cần 2-3 khung hình để quan sát xem vật thể có ổn định không trước khi chính thức cấp ID. Trong lúc chưa đủ điều kiện, hệ thống gán track_id = -1 để biểu thị 'đối tượng tạm thời, chưa theo dõi chính thức'.\n\n"
        "4. Hàm reset():\n"
        "• Khi người dùng tua lại video hoặc chuyển sang camera khác, phải gọi tracker.reset() để xóa sạch các Track ID cũ trong bộ nhớ, tránh tình trạng camera mới dùng lại ID cũ của camera trước."
    )

    # --- PHẦN 6: MINH HỌA QUÁ TRÌNH CHẠY ---
    h6 = doc.add_paragraph()
    h6.paragraph_format.space_before = Pt(12)
    h6.paragraph_format.space_after = Pt(4)
    r_h6 = h6.add_run("PHẦN 6: MINH HỌA QUÁ TRÌNH BÁM VẾT QUA CÁC KHUNG HÌNH LIÊN TIẾP")
    r_h6.font.name = "Arial"
    r_h6.font.size = Pt(13)
    r_h6.font.bold = True
    r_h6.font.color.rgb = COLOR_PRIMARY

    p_p6 = doc.add_paragraph()
    p_p6.paragraph_format.space_after = Pt(6)
    p_p6.add_run("Bảng mô phỏng ByteTrack duy trì định danh Track ID khi có người đi bộ che khuất tấm biển:")

    tbl_flow = doc.add_table(rows=5, cols=4)
    tbl_flow.alignment = WD_TABLE_ALIGNMENT.CENTER
    flow_headers = ["Khung hình (Thời gian)", "Hiện tượng thực tế", "Kết quả ByteTrack", "Hành vi hệ thống"]
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
        ("Frame 10 (t = 0.33s)", "Biển standee xuất hiện rõ nét", "Cấp mới: Track ID #1\n(Conf: 0.88)", "Bắt đầu theo dõi hành vi của biển #1"),
        ("Frame 11-20 (t = 0.6s)", "Biển đứng yên trên vỉa hè", "Duy trì: Track ID #1\n(Conf: 0.85 - 0.90)", "Tích lũy thời gian đứng yên của biển #1"),
        ("Frame 21 (t = 0.70s)", "Người đi bộ đi ngang che khuất 1/2 biển", "Khớp nối tầng 2: Vẫn là Track ID #1\n(Conf tụt xuống 0.28)", "Không bị mất dấu, không sinh ID mới!"),
        ("Frame 25 (t = 0.83s)", "Người đi bộ bước qua, biển rõ lại", "Duy trì: Track ID #1\n(Conf tăng lại 0.89)", "Tiếp tục tích lũy chuỗi thời gian cho biển #1")
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
            if j == 2:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY
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
        "1. Lỗi quên tham số 'persist=True':\n"
        "• Hiện tượng: Mỗi frame trôi qua, biển hiệu lại bị đổi sang một ID hoàn toàn mới (ID nhảy loạn xạ từ 1, 2, 3 đến hàng nghìn).\n"
        "• Nguyên nhân: Không có persist=True, tracker sẽ bị xóa sạch sau mỗi khung hình.\n\n"
        "2. Nhầm lẫn giữa ID của Tracker và Class ID của AI:\n"
        "• Class ID: Đại diện cho loại vật thể (trong đồ án chỉ có 1 class duy nhất: class_id = 0 đại diện cho 'bien_quang_cao').\n"
        "• Track ID: Mã số định danh cá thể từng tấm biển (ID #1, ID #2, ID #3...). Hai khái niệm này hoàn toàn khác nhau!"
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
        "Bạn hãy tự trả lời 3 câu hỏi dưới đây trước khi chuyển sang Bài học số 7:\n\n"
        "• Câu 1: Nếu một hệ thống camera giám sát chỉ sử dụng mô hình phát hiện YOLO đơn thuần mà KHÔNG có module Tracker bám vết, điều gì sẽ xảy ra với cùng một tấm biển hiệu đứng yên trong 1 phút ghi hình (ở tốc độ 30 FPS)?\n\n"
        "• Câu 2: Trong hàm model.track(), tham số 'persist=True' có vai trò bắt buộc gì? Nếu bạn bỏ quên tham số này thì hậu quả là gì?\n\n"
        "• Câu 3: Điểm sáng tạo đột phá của thuật toán ByteTrack so với các thuật toán theo dõi truyền thống (như SORT) là gì khi xử lý các phát hiện có độ tin cậy thấp (ví dụ khi vật thể bị che khuất một phần)?"
    )

    try:
        doc.save(OUTPUT_FILE)
        print(f"[THÀNH CÔNG] Đã tạo tệp tài liệu bài học: {OUTPUT_FILE}")
    except PermissionError:
        print(f"[CẢNH BÁO] Không thể ghi đè {OUTPUT_FILE} do file đang được mở trong Microsoft Word. Vui lòng đóng file Word và chạy lại.")


if __name__ == "__main__":
    build_document()
