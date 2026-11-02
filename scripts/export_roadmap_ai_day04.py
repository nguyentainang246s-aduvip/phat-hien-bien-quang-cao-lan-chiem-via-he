"""
Script xuất bản bài học Ngày 04 thành file Word (.docx) chuyên nghiệp
Lưu trữ vào thư mục: roadmap AI/Ngay_04_Script_Trich_Xuat_Anh_Tu_Dong_Extract_Frames.docx
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
OUTPUT_FILE = str(OUTPUT_DIR / "Ngay_04_Script_Trich_Xuat_Anh_Tu_Dong_Extract_Frames.docx")

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


def build_day04_document():
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
    r_day = p_main.add_run("NGÀY 04: LÀM CHỦ SCRIPT TRÍCH XUẤT ẢNH TỰ ĐỘNG EXTRACT_FRAMES.PY\nCƠ CHẾ NHẢY CÓC INTERVAL CHỐNG DƯ THỪA DỮ LIỆU\n")
    r_day.font.name = "Arial"
    r_day.font.size = Pt(16)
    r_day.font.bold = True
    r_day.font.color.rgb = COLOR_PRIMARY
    
    r_sub = p_main.add_run("Tự động hóa thu thập khung hình từ video CCTV, nén ảnh JPEG 95 và phòng tránh rò rỉ dữ liệu (Data Leakage)")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_SECONDARY

    # Bảng Metadata
    tbl_meta = doc.add_table(rows=4, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_rows = [
        ("Phân hệ phụ trách:", "Track A — AI & Dữ liệu (Data Collection & Frame Extraction)"),
        ("Mã nguồn liên quan:", "datasets/extract_frames.py, data/videos/, datasets/raw_images/"),
        ("Kỹ thuật cốt lõi:", "Downsampling Interval, Modulo Subsampling, Zero-padded Naming (:04d)"),
        ("Mục tiêu ngày 04:", "Làm chủ script trích xuất, thu hoạch hàng trăm ảnh thô sắc nét, hiểu rõ ranh giới Data Leakage.")
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
    
    add_subsection_header(doc, "1. Ẩn dụ chụp ảnh kỷ yếu chế độ Burst Mode")
    add_body_paragraph(
        doc,
        "Hãy tưởng tượng một nhiếp ảnh gia chụp ảnh kỷ yếu cho một lớp học. Khi cả lớp đang đứng nghiêm trang trên bục suốt 10 giây để chụp ảnh lưu niệm:\n"
        "Nếu người thợ ảnh bấm giữ nút chụp liên thanh (Burst Mode với tốc độ 30 kiểu/giây), máy ảnh sẽ bấm tanh tách và sinh ra 300 bức ảnh. "
        "Tuy nhiên, khi mở máy ra kiểm tra: 300 bức ảnh này giống hệt nhau từng sợi tóc, từng nếp áo và nụ cười!\n"
        "Nếu người thợ ảnh đem in rửa toàn bộ 300 bức ảnh này rồi đóng thành cuốn album dày cộp:\n"
        "• Vừa lãng phí tiền bạc in ấn và công sức cắt dán.\n"
        "• Người mở cuốn album lật từ trang 1 đến trang 300 chỉ thấy đúng 1 khung cảnh y xì đúc, không học hỏi thêm được bất kỳ góc nhìn mới nào!"
    )
    add_body_paragraph(
        doc,
        "Trong huấn luyện AI, camera an ninh CCTV quay với tốc độ 30 khung hình/giây (30 FPS). "
        "Giữa 2 frame liên tiếp cách nhau chỉ 33 mili-giây, tấm biển quảng cáo ngoài vỉa hè đứng yên bất động, xe máy mới lăn bánh vài centimet. "
        "Nếu lấy toàn bộ 30 frame/giây để dán nhãn và train, mô hình sẽ bị 'học vẹt' (Overfitting) — nó thuộc lòng khung cảnh đó nhưng gặp góc phố mới là mù tịt. "
        "Người kỹ sư dữ liệu thông minh sẽ áp dụng Cơ chế nhảy cóc chu kỳ (Sampling Interval): Cứ cách 1.0 giây hoặc 2.0 giây mới bấm máy lưu lại 1 bức ảnh duy nhất."
    )

    # =========================================================================
    # PHẦN 2: MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC
    # =========================================================================
    add_section_header(doc, "II", "MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC")
    
    add_subsection_header(doc, "1. Công thức toán học tính Bước nhảy khung hình (frame_step)")
    add_body_paragraph(
        doc,
        "Để thực hiện việc lấy mẫu định kỳ theo thời gian thực, script datasets/extract_frames.py áp dụng công thức sau:"
    )
    add_body_paragraph(
        doc,
        "               frame_step = max(1, floor(FPS * interval_sec))\n\n"
        "Trong đó:\n"
        "• FPS (Frames Per Second): Tốc độ khung hình vật lý của video nguồn (thường là 25 hoặc 30 FPS).\n"
        "• interval_sec: Chu kỳ lấy mẫu mong muốn tính bằng giây (ví dụ: 1.0s lấy 1 ảnh, 2.0s lấy 1 ảnh).\n"
        "• floor(x): Phép làm tròn số nguyên xuống (hàm int trong Python).\n\n"
        "Ví dụ tính toán thực tế:\n"
        "Nếu video có FPS = 25 và interval_sec = 2.0 giây:\n"
        "               frame_step = int(25 * 2.0) = 50 frames\n"
        "Trong vòng lặp đọc video, điều kiện lưu ảnh là phép chia lấy dư: current_frame % frame_step == 0. "
        "Chỉ các frame thứ 0, 50, 100, 150... mới được lưu vào đĩa. "
        "Với đoạn video dài 40 giây (tổng 1000 frames), script sẽ thu hoạch chính xác: 1000 / 50 = 20 bức ảnh sạch."
    )

    add_subsection_header(doc, "2. Tiêu chuẩn nén ảnh bảo toàn chi tiết: IMWRITE_JPEG_QUALITY = 95")
    add_body_paragraph(
        doc,
        "Khi lưu ảnh ra file bằng cv2.imwrite, nếu không cấu hình chất lượng nén, OpenCV sẽ áp dụng mức nén mặc định (80-85%). "
        "Mức nén này tạo ra các khối vỡ hạt (Compression Artifacts), làm mờ các chi tiết chân đế sắt mảnh và các tấm biển ở xa.\n"
        "Trong mã nguồn dự án, cấu hình được thiết lập ở mức 95:\n"
        "               cv2.imwrite(save_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])\n"
        "Mức 95 giữ lại 99% độ sắc nét quang học ban đầu mà dung lượng mỗi ảnh chỉ khoảng 250–400 KB (so với file PNG nặng 2–4 MB), "
        "tối ưu hóa băng thông tải lên Roboflow và GPU Colab."
    )

    add_subsection_header(doc, "3. Quy tắc định danh đệm số 0 (Zero-padded Naming: :04d)")
    add_body_paragraph(
        doc,
        "Tên file ảnh được format bằng cú pháp chuẩn: f'{video_name}_frame_{saved_count:04d}.jpg' -> ví dụ: video_test_frame_0001.jpg.\n"
        "Lý do kỹ thuật bắt buộc: Hệ điều hành (Windows, Linux) sắp xếp danh sách file theo thứ tự từ điển (Lexicographical order). "
        "Nếu không có số 0 ở đầu (frame_1.jpg, frame_2.jpg... frame_10.jpg), hệ thống sẽ sắp xếp frame_10.jpg đứng ngay sau frame_1.jpg! "
        "Điều này sẽ làm lệch thứ tự giữa danh sách file ảnh và danh sách file nhãn khi DataLoader nạp vào mạng nơ-ron."
    )

    # =========================================================================
    # PHẦN 3: HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN DỰ ÁN
    # =========================================================================
    add_section_header(doc, "III", "HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN DỰ ÁN")
    
    add_subsection_header(doc, "1. Mổ xẻ các khối lệnh chính trong datasets/extract_frames.py")
    add_body_paragraph(
        doc,
        "Hãy mở file datasets/extract_frames.py trong thư mục dự án. Cấu trúc hàm extract_frames_from_video được tổ chức như sau:"
    )
    
    code_extract = (
        "# Trích đoạn mã nguồn trong datasets/extract_frames.py\n"
        "cap = cv2.VideoCapture(video_path)\n"
        "fps = cap.get(cv2.CAP_PROP_FPS) or 30.0\n"
        "total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))\n"
        "frame_step = max(1, int(fps * interval_sec))\n"
        "\n"
        "current_frame = 0\n"
        "saved_count = 0\n"
        "while True:\n"
        "    ret, frame = cap.read()\n"
        "    if not ret:\n"
        "        break\n"
        "        \n"
        "    # Nhảy cóc chu kỳ\n"
        "    if current_frame % frame_step == 0:\n"
        "        saved_count += 1\n"
        "        image_filename = f'{video_name}_frame_{saved_count:04d}.jpg'\n"
        "        save_path = os.path.join(output_dir, image_filename)\n"
        "        cv2.imwrite(save_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])\n"
        "        \n"
        "    current_frame += 1\n"
        "cap.release()"
    )
    add_code_block(doc, code_extract)

    add_subsection_header(doc, "2. Lệnh thực thi trích xuất toàn bộ video kiểm thử")
    add_body_paragraph(
        doc,
        "Chạy lệnh sau trên terminal PowerShell để thu hoạch ảnh từ 3 video CCTV thực tế:"
    )
    code_run = (
        ".venv\\Scripts\\activate\n"
        "python -c \"from datasets.extract_frames import extract_frames_from_video; \" \\\n"
        "\"extract_frames_from_video('data/videos/video test.mp4', 'datasets/raw_images', 1.0); \" \\\n"
        "\"extract_frames_from_video('data/videos/videotesst2.mp4', 'datasets/raw_images', 1.0); \" \\\n"
        "\"extract_frames_from_video('data/videos/video test3.mp4', 'datasets/raw_images', 1.0)\""
    )
    add_code_block(doc, code_run)

    # =========================================================================
    # PHẦN 4: SẢN PHẨM BÀN GIAO & CÁCH TỰ KIỂM TRA
    # =========================================================================
    add_section_header(doc, "IV", "SẢN PHẨM BÀN GIAO & TIÊU CHÍ TỰ KIỂM TRA")
    
    tbl_eval = doc.add_table(rows=4, cols=3)
    tbl_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
    eval_data = [
        ("STT", "Tiêu chuẩn đánh giá", "Kết quả nghiệm thu của sinh viên"),
        ("01", "Chạy thành công script trích xuất ảnh.", "Thư mục datasets/raw_images/ chứa hàng trăm ảnh .jpg sắc nét."),
        ("02", "Định danh file chuẩn 4 chữ số :04d.", "Tên file chuẩn: video_test_frame_0001.jpg, không bị lỗi thứ tự từ điển."),
        ("03", "Giải thích trôi chảy công thức frame_step.", "Tự tính nhẩm chính xác số ảnh trích xuất dựa vào FPS và interval_sec.")
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
    
    add_subsection_header(doc, "CÂU HỎI 1: Tính toán bước nhảy khung hình")
    add_body_paragraph(
        doc,
        "Thầy/Cô Hội đồng hỏi: 'Một đoạn video camera an ninh dài 40 giây có tốc độ 25 FPS. "
        "Nếu cấu hình interval_sec = 2.0 (cứ 2 giây lấy 1 ảnh), thì frame_step bằng bao nhiêu và kết thúc video thu được bao nhiêu ảnh?'"
    )
    add_callout_box(
        doc,
        "ĐÁP ÁN PHẢN BIỆN CHUẨN XÁC CỦA SINH VIÊN (XUẤT SẮC):\n"
        "• Bước nhảy khung hình: frame_step = int(FPS * interval_sec) = int(25 * 2.0) = 50 frames.\n"
        "• Tổng số khung hình của đoạn video: Total = 40 giây * 25 FPS = 1000 frames.\n"
        "• Số lượng ảnh thu hoạch được: Count = 1000 / 50 = 20 bức ảnh chất lượng cao.",
        title="KỊCH BẢN PHẢN BIỆN CÂU HỎI 1",
        box_type="success"
    )

    add_subsection_header(doc, "CÂU HỎI 2: Nguy cơ Rò rỉ Dữ liệu (Data Leakage) khi chia tập ngẫu nhiên")
    add_body_paragraph(
        doc,
        "Thầy/Cô Hội đồng hỏi: 'Khi cắt ảnh từ video camera với chu kỳ 1 giây/ảnh để huấn luyện AI, "
        "nếu em gom toàn bộ số ảnh này lại rồi dùng hàm chia ngẫu nhiên (Random Split) 70% vào Train và 30% vào Test, "
        "mô hình có bị phạm lỗi học thuật Data Leakage không? Tại sao? Em phòng tránh lỗi này như thế nào?'"
    )
    add_callout_box(
        doc,
        "KỊCH BẢN TRẢ LỜI ĐẠT ĐIỂM XUẤT SẮC TRƯỚC HỘI ĐỒNG:\n"
        "Dạ thưa Thầy/Cô, việc chia ngẫu nhiên từng frame rời rạc (Random frame-level split) CHẮC CHẮN sẽ phạm phải lỗi học thuật nghiêm trọng là Rò rỉ Dữ liệu (Data Leakage):\n\n"
        "1. Nguyên nhân bản chất:\n"
        "   Các khung hình trích xuất từ cùng một đoạn video có mối tương quan không gian - thời gian (Spatio-temporal correlation) cực kỳ cao. Khung hình ở giây thứ 10 và giây thứ 11 có cùng góc chiếu sáng, cùng nền vỉa hè, và tấm biển hiệu đứng yên tại cùng một vị trí. Nếu frame thứ 10 rơi vào Train và frame thứ 11 rơi vào Test, mô hình thực chất đã 'học thuộc lòng' khung cảnh đó từ trước. Điểm số mAP trên tập Test sẽ cao ảo nhưng khi mang sang camera ở góc phố khác mô hình sẽ thất bại hoàn toàn.\n\n"
        "2. Giải pháp khoa học của nhóm em (Video / Location-based Split):\n"
        "   Nhóm em tuyệt đối KHÔNG chia ngẫu nhiên từng ảnh rời rạc. Toàn bộ quá trình phân chia Train/Valid/Test được thực hiện theo từng VIDEO ĐỘC LẬP:\n"
        "   • Video 1 và Video 2 (hai góc phố A và B) được dùng trọn vẹn cho tập Train và Validation.\n"
        "   • Video 3 (một góc phố C hoàn toàn mới lạ với điều kiện ánh sáng và loại biển hiệu khác biệt) được giữ riêng 100% làm tập Test độc lập.\n"
        "Nhờ đó, tập Test giữ nguyên tính chất 'mù' khách quan, phản ánh chính xác năng lực tổng quát hóa (Generalization) thực tế của mô hình.",
        title="KỊCH BẢN PHẢN BIỆN CÂU HỎI 2 (HỘI ĐỒNG)",
        box_type="warning"
    )

    # =========================================================================
    # PHẦN 6: BẢN GHI NHỚ CỐT LÕI (KEY TAKEAWAYS)
    # =========================================================================
    add_section_header(doc, "VI", "BẢN GHI NHỚ CỐT LÕI NGÀY 04 (KEY TAKEAWAYS)")
    
    tbl_sum = doc.add_table(rows=5, cols=2)
    tbl_sum.alignment = WD_TABLE_ALIGNMENT.CENTER
    sum_data = [
        ("Kỹ thuật cốt lõi", "Quy tắc bắt buộc phải thuộc lòng"),
        ("Công thức frame_step", "frame_step = max(1, int(FPS * interval_sec)). Nhảy cóc chu kỳ để chống dư thừa dữ liệu."),
        ("Chuẩn nén JPEG 95", "IMWRITE_JPEG_QUALITY = 95. Bảo toàn 99% chi tiết sắc nét của biển hiệu mà dung lượng nhẹ."),
        ("Format tên file :04d", "{video_name}_frame_{saved_count:04d}.jpg để bảo vệ thứ tự từ điển Lexicographical."),
        ("Chống Data Leakage", "Chia tập dữ liệu theo từng Video/Góc phố độc lập, tuyệt đối không random split từng frame.")
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
    print(f"[XUẤT BẢN THÀNH CÔNG] File Word Ngày 04 đã được tạo tại:\n👉 {OUTPUT_FILE}")


if __name__ == "__main__":
    build_day04_document()
