"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Báo cáo Tiến độ Kỹ thuật Giai đoạn Tuần 4 – Tuần 8 (Bản Chuẩn Hóa Học Thuật)
Mã sinh viên: 20224083 - Họ và tên: Nguyễn Đức Tài Năng
==============================================================================
Script tự động biên soạn và kết xuất tệp Word (.docx) chuẩn học thuật
áp dụng màu sắc nhận diện Bách Khoa (Navy & Teal) và tích hợp minh chứng thực tế.
Lưu vào: reports/Bao_cao_tien_do_Tuan_4_8_DATN_20224083_ban_cap_nhat.docx
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
OUTPUT_FILE = str(OUTPUT_DIR / "Bao_cao_tien_do_Tuan_4_8_DATN_20224083_ban_cap_nhat.docx")

# Bảng màu chuẩn học thuật (Bách Khoa Navy Blue & Teal)
COLOR_PRIMARY = RGBColor(30, 58, 138)     # Navy #1E3A8A
COLOR_SECONDARY = RGBColor(15, 118, 110)  # Teal #0F766E
COLOR_DARK = RGBColor(30, 41, 59)         # Slate Dark #1E293B
COLOR_MUTED = RGBColor(100, 116, 139)     # Slate Gray #64748B
COLOR_RED = RGBColor(220, 38, 38)         # Red
COLOR_GREEN = RGBColor(16, 185, 129)      # Green

HEX_PRIMARY = "1E3A8A"
HEX_SECONDARY = "0F766E"
HEX_BG_LIGHT = "F8FAFC"
HEX_BORDER = "CBD5E1"
HEX_HEADER_BG = "1E3A8A"
HEX_CALLOUT_BG = "EFF6FF"
HEX_CALLOUT_BORDER = "3B82F6"
HEX_WARNING_BG = "FEF2F2"
HEX_WARNING_BORDER = "EF4444"
HEX_SUCCESS_BG = "ECFDF5"
HEX_SUCCESS_BORDER = "10B981"
HEX_ASSET_BG = "F3F4F6"
HEX_ASSET_BORDER = "6B7280"


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


def format_table_header(row, headers, widths, bg_color=HEX_HEADER_BG):
    for j, h in enumerate(headers):
        cell = row.cells[j]
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, 80, 80, 100, 100)
        cell.width = widths[j]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9.0)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)


def add_callout_box(doc, text, title="LƯU Ý QUAN TRỌNG", box_type="info"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.8)

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
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run_title = p.add_run(f"{title}: ")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(10.0)
    run_title.font.bold = True
    run_title.font.color.rgb = title_color

    run_text = p.add_run(text)
    run_text.font.name = "Arial"
    run_text.font.size = Pt(9.5)
    run_text.font.color.rgb = COLOR_DARK

    doc.add_paragraph()


def add_image_with_caption(doc, img_path, caption, asset_path=None, how_to_get=None, width=Inches(6.2)):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(3)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=width)

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(4)
        run_cap = p_cap.add_run(caption)
        run_cap.font.name = "Arial"
        run_cap.font.size = Pt(9.0)
        run_cap.font.bold = True
        run_cap.font.italic = True
        run_cap.font.color.rgb = COLOR_DARK
    else:
        p_missing = doc.add_paragraph()
        p_missing.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_m = p_missing.add_run(f"[HÌNH ẢNH: {caption} - Đường dẫn: {img_path}]")
        r_m.font.name = "Arial"
        r_m.font.color.rgb = COLOR_RED
        r_m.bold = True

    if asset_path or how_to_get:
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, HEX_ASSET_BG)
        set_cell_margins(cell, top=60, bottom=60, left=120, right=120)

        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'  <w:left w:val="single" w:sz="16" w:space="0" w:color="{HEX_ASSET_BORDER}"/>'
            f'  <w:top w:val="none"/>'
            f'  <w:bottom w:val="none"/>'
            f'  <w:right w:val="none"/>'
            f'</w:tcBorders>'
        )
        cell._tc.get_or_add_tcPr().append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)

        r_lbl1 = p.add_run("📍 Tệp nguồn minh chứng: ")
        r_lbl1.font.name = "Arial"
        r_lbl1.font.size = Pt(8.5)
        r_lbl1.font.bold = True
        r_lbl1.font.color.rgb = COLOR_PRIMARY

        r_val1 = p.add_run(f"{asset_path}\n")
        r_val1.font.name = "Consolas"
        r_val1.font.size = Pt(8.0)
        r_val1.font.color.rgb = COLOR_DARK

        if how_to_get:
            r_lbl2 = p.add_run("💡 Hướng dẫn kiểm tra / tái tạo: ")
            r_lbl2.font.name = "Arial"
            r_lbl2.font.size = Pt(8.5)
            r_lbl2.font.bold = True
            r_lbl2.font.color.rgb = COLOR_SECONDARY

            r_val2 = p.add_run(how_to_get)
            r_val2.font.name = "Arial"
            r_val2.font.size = Pt(8.5)
            r_val2.font.color.rgb = COLOR_DARK

        doc.add_paragraph()


def add_body_paragraph(doc, text, bold_prefix=None, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_bp = p.add_run(bold_prefix)
        r_bp.font.name = "Arial"
        r_bp.font.size = Pt(10)
        r_bp.font.bold = True
        r_bp.font.color.rgb = COLOR_DARK
    r_txt = p.add_run(text)
    r_txt.font.name = "Arial"
    r_txt.font.size = Pt(10)
    r_txt.font.color.rgb = COLOR_DARK
    return p


def style_section_heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(4)
    run = h.runs[0]
    run.font.name = "Arial"
    if level == 1:
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
    elif level == 2:
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = COLOR_SECONDARY
    return h


def build_progress_report_tuan_4_8():
    doc = Document()

    # Cấu hình lề trang chuẩn A4
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(0.8)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)

    # 1. Tiêu đề chính
    title = doc.add_heading("BÁO CÁO TIẾN ĐỘ ĐỒ ÁN TỐT NGHIỆP", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_before = Pt(0)
    title.paragraph_format.space_after = Pt(2)
    title.runs[0].font.name = "Arial"
    title.runs[0].font.size = Pt(17)
    title.runs[0].font.bold = True
    title.runs[0].font.color.rgb = COLOR_PRIMARY

    sub_title = doc.add_paragraph()
    sub_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_title.paragraph_format.space_before = Pt(0)
    sub_title.paragraph_format.space_after = Pt(12)
    sub_run = sub_title.add_run("GIAI ĐOẠN: TUẦN 4 – TUẦN 8 (TỔNG HỢP VIDEO THỬ NGHIỆM, GÁN NHÃN DATASET & THIẾT LẬP ROI ĐA CAMERA)")
    sub_run.font.name = "Arial"
    sub_run.font.size = Pt(11)
    sub_run.font.bold = True
    sub_run.font.color.rgb = COLOR_SECONDARY

    # Khung Thông tin chung
    info_tbl = doc.add_table(rows=6, cols=2)
    info_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(info_tbl)

    meta_data = [
        ("Tên đề tài:", "Hệ thống giám sát và phát hiện biển quảng cáo/biển hiệu lấn chiếm vỉa hè qua camera CCTV cố định"),
        ("Sinh viên thực hiện:", "Nguyễn Đức Tài Năng — MSSV: 20224083 — Lớp: Điện tử 11 – K67\nThành viên phối hợp: Đinh Văn Tuấn — Lớp: Điện tử 11 – K67"),
        ("Đơn vị đào tạo:", "Đại học Bách Khoa Hà Nội"),
        ("Thời gian thực hiện:", "Giai đoạn Tuần 4 – Tuần 8 (Kế hoạch Đề cương ĐATN 17 tuần khóa 2026.1)"),
        ("Nhiệm vụ trọng tâm theo Đề cương:", "1. Thu thập video các tuyến phố có biển quảng cáo/biển hiệu lấn vỉa hè.\n2. Gán nhãn dữ liệu trên Roboflow, đạt tối thiểu 1.000 ảnh chuẩn YOLO.\n3. Hoàn thiện ROI cho nhiều camera dựa trên các góc quay thực tế."),
        ("Tiêu chuẩn nghiệm thu đề ra:", "Dataset >= 1.000 ảnh sẵn sàng train; ROI khớp với các camera thật ngoài hiện trường.")
    ]

    for i, (k, v) in enumerate(meta_data):
        row = info_tbl.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width, c1.width = Inches(2.3), Inches(4.5)
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
        set_cell_background(c0, HEX_BG_LIGHT)

        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.font.name = "Arial"
        r0.font.size = Pt(9.5)
        r0.font.bold = True
        r0.font.color.rgb = COLOR_PRIMARY

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.name = "Arial"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = COLOR_DARK

    doc.add_paragraph()

    # KẾT LUẬN NGHIỆM THU
    add_callout_box(
        doc,
        "Căn cứ đối chiếu trực tiếp với dữ liệu lưu trữ trong workspace: Nhóm nghiên cứu đã thực hiện các nội dung kỹ thuật trọng tâm của giai đoạn Tuần 4–8: "
        "Tổng hợp 6 đoạn video clip camera giám sát (CCTV) mẫu phục vụ thử nghiệm (720p HD, 24 fps, 10.0s) phản ánh các góc nhìn quan sát hè phố đô thị; "
        "Đóng gói và kiểm toán cấu trúc tập dữ liệu sạch v13_clean đạt 2,674 ảnh (vượt chỉ tiêu quy mô >= 1.000 ảnh, đạt 267.4%), 8,097 nhãn BBox đạt cú pháp chuẩn YOLO 5 cột, 201 ảnh nền âm tính (7.52%), 0 lỗi cú pháp nhãn; "
        "Hoàn thiện 6 tệp cấu hình Đa giác ROI vỉa hè (Static Polygon ROI & Multi-ROI) và kiểm tra trực quan trên khung hình đại diện của cả 6 video thử nghiệm. "
        "Đồng thời, báo cáo ghi nhận minh bạch các giới hạn khoa học: việc đồng bộ trực tiếp Roboflow API chưa thực hiện do môi trường cục bộ chưa cấu hình API key; các video clip đóng vai trò là dữ liệu mẫu phục vụ kiểm thử học thuật chưa đại diện toàn bộ mạng lưới camera giao thông; và việc phân chia split dựa trên tiền tố tên tệp duy nhất chưa kiểm định độc lập về mức độ cô lập góc máy.",
        title="KẾT LUẬN ĐỐI CHIẾU TIẾN ĐỘ TUẦN 4–8",
        box_type="info"
    )

    # =========================================================================
    # PHẦN 1: NHIỆM VỤ 1 - THU THẬP VIDEO THỬ NGHIỆM
    # =========================================================================
    style_section_heading(doc, "1. NHIỆM VỤ 1: THU THẬP VIDEO PHỤC VỤ THỬ NGHIỆM HỆ THỐNG", level=1)
    
    add_body_paragraph(
        doc,
        "Để phục vụ việc kiểm thử thuật toán và đánh giá mô hình thị giác máy tính trong bài toán giám sát đô thị, "
        "nhóm nghiên cứu đã tổng hợp 6 đoạn video clip camera giám sát (CCTV) mẫu phục vụ thử nghiệm hệ thống (test benchmark clips), "
        "được lưu trữ tại thư mục data/videos/."
    )

    add_body_paragraph(
        doc,
        "Nguồn gốc dữ liệu video: Các đoạn clip video mẫu được tổng hợp từ nguồn dữ liệu công khai trên Internet / mạng xã hội và camera giám sát cộng đồng "
        "(nguồn chưa xác minh độc lập giấy phép bản quyền gốc hoặc biên bản khảo sát hiện trường); nhóm nghiên cứu không trực tiếp lắp đặt hoặc vận hành các camera vật lý này ngoài thực địa. "
        "Trong đó, 3 video đầu (video test.mp4, videotesst2.mp4, video test3.mp4) phản ánh bối cảnh góc nhìn tương ứng khu vực các tuyến phố kinh doanh tại Hà Nội "
        "(khu vực Phố Huế / Hàng Bài, Bạch Mai, Trần Đại Nghĩa); 3 video bổ sung (videotest4.mp4, videotest5.mp4, videotest6.mp4) ghi nhận các luồng camera quan sát đường phố đô thị có biển hiệu ven đường."
    )

    add_body_paragraph(
        doc,
        "Mục đích sử dụng và tính riêng tư: Video được sử dụng thuần túy cho mục đích nghiên cứu học thuật, phi thương mại trong khuôn khổ Đồ án tốt nghiệp; "
        "video không được dùng để nhận dạng cá nhân; hình ảnh có thể ghi nhận người đi đường và phương tiện giao thông ngoài ý muốn."
    )

    add_body_paragraph(
        doc,
        "Mô tả đúng giới hạn của căn cứ pháp lý: Về mặt nghiệp vụ đô thị, bài toán được xây dựng dựa trên cơ sở tham khảo Điều 12 Nghị định 168/2024/NĐ-CP "
        "(quy định xử phạt vi phạm hành chính đối với hành vi đặt, treo biển hiệu, biển quảng cáo lấn chiếm lòng đường, hè phố). "
        "Quy định này được dùng làm căn cứ tham khảo định hình bài toán 'phát hiện dấu hiệu nghi vấn biển quảng cáo/biển hiệu lấn chiếm hè phố'. "
        "Cần lưu ý rằng hệ thống AI chỉ đóng vai trò cảnh báo sớm dấu hiệu nghi vấn; việc xác định và kết luận hành vi vi phạm pháp luật chính thức thuộc thẩm quyền của cơ quan chức năng "
        "sau khi kiểm tra bối cảnh cụ thể, đo đạc thực tế và xem xét các quy định cấp phép sử dụng tạm thời hè phố (nếu có). "
        "Nghị định 168/2024/NĐ-CP không phải là văn bản cấp quyền thu thập hay sử dụng dữ liệu video cho dự án."
    )

    style_section_heading(doc, "Bảng 1. Danh mục 6 Video CCTV Mẫu Thử Nghiệm trong Workspace", level=2)

    tbl_vids = doc.add_table(rows=1, cols=7)
    tbl_vids.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_vids)

    v_headers = ["Video / Camera ID", "Bối cảnh quan trắc", "Độ phân giải", "FPS", "Thời lượng", "Đặc điểm góc nhìn", "Cấu hình ROI tương ứng"]
    v_widths = [Inches(1.2), Inches(1.4), Inches(0.8), Inches(0.5), Inches(0.7), Inches(1.2), Inches(1.0)]
    format_table_header(tbl_vids.rows[0], v_headers, v_widths)

    vid_rows = [
        ("video test.mp4", "Bối cảnh Phố Huế / Hàng Bài, Q. Hoàn Kiếm", "1280x720", "24.0", "10.0s (240f)", "Góc ngang hướng vỉa hè thương mại", "roi_video_test.json"),
        ("videotesst2.mp4", "Bối cảnh Phố Bạch Mai, Q. Hai Bà Trưng", "1280x720", "24.0", "10.0s (240f)", "Góc nghiêng 45 độ vỉa hè & cửa hàng", "roi_videotesst2.json"),
        ("video test3.mp4", "Bối cảnh Phố Trần Đại Nghĩa, Q. Hai Bà Trưng", "1280x720", "24.0", "10.0s (240f)", "Góc cao nhìn xuống vỉa hè trước quán", "roi_video_test3.json"),
        ("videotest4.mp4", "Luồng camera quan sát đô thị (Cam 4)", "1280x720", "24.0", "10.0s (240f)", "Góc trực diện nhìn trục đường hai bên", "roi_videotest4.json"),
        ("videotest5.mp4", "Luồng camera quan sát đô thị (Cam 5)", "1280x720", "24.0", "10.0s (240f)", "Góc cận cảnh dãy cửa hàng kinh doanh", "roi_videotest5.json"),
        ("videotest6.mp4", "Luồng camera quan sát đô thị (Cam 6)", "1280x720", "24.0", "10.0s (240f)", "Góc toàn cảnh trục đường giao thông", "roi_videotest6.json"),
    ]

    for row_data in vid_rows:
        row = tbl_vids.add_row()
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            set_cell_margins(cell, 50, 50, 70, 70)
            cell.width = v_widths[j]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            if j in [2, 3, 4]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if j == 0:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            elif j == 6:
                r.font.color.rgb = COLOR_SECONDARY
            else:
                r.font.color.rgb = COLOR_DARK

    doc.add_paragraph()

    add_body_paragraph(
        doc,
        "Đặc điểm kỹ thuật nguồn video: Toàn bộ 6 tệp video được lưu trữ tại data/videos/, định dạng nén chuẩn H.264/MP4, "
        "độ phân giải chuẩn HD 1280x720 pixels, tốc độ quét 24.0 khung hình/giây. Video thu thập đa dạng các hình thái vi phạm: "
        "biển hiệu bạt lớn dựng cố định chắn ngang lối đi bộ, biển Standee chân sắt chữ A, biển hộp đèn đứng lấn hè, "
        "đồng thời ghi nhận các góc nhìn CCTV đa dạng (góc ngang, góc nghiêng 45 độ, góc cao từ tầng 2 nhìn xuống)."
    )

    # =========================================================================
    # PHẦN 2: NHIỆM VỤ 2 - GÁN NHÃN VÀ ĐÓNG GÓI DATASET CHUẨN YOLO
    # =========================================================================
    style_section_heading(doc, "2. NHIỆM VỤ 2: GÁN NHÃN VÀ ĐÓNG GÓI DATASET CHUẨN YOLO", level=1)

    add_body_paragraph(
        doc,
        "Dữ liệu hình ảnh được quản lý và gán nhãn trên nền tảng Roboflow "
        "(Workspace: 'tai-nang-nguyen-duc', Project: 'sidewalk-signboard-detection-1', Version 13 theo tài liệu nguồn datasets/v13/README.roboflow.txt và datasets/raw_images/SOURCES.md). "
        "Do phiên làm việc môi trường cục bộ hiện tại không cấu hình biến môi trường ROBOFLOW_API_KEY, các thao tác đồng bộ trực tuyến API được tạm thời đóng băng, "
        "và toàn bộ dữ liệu đã được xuất bản, làm sạch và đóng gói hoàn chỉnh thành tập dữ liệu cục bộ datasets/v13_clean."
    )

    style_section_heading(doc, "Bảng 2. Thống kê Chi tiết Cơ cấu Tập Dữ liệu v13_clean Đã Kiểm toán", level=2)

    tbl_ds = doc.add_table(rows=1, cols=6)
    tbl_ds.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_ds)

    d_headers = ["Tập con (Split)", "Số lượng ảnh", "Tỷ lệ phân chia", "Ảnh nền âm tính (BG)", "Số nhãn BBox (GT)", "Định dạng nhãn"]
    d_widths = [Inches(1.8), Inches(0.9), Inches(0.9), Inches(1.3), Inches(1.1), Inches(0.8)]
    format_table_header(tbl_ds.rows[0], d_headers, d_widths)

    ds_rows = [
        ("Tập Huấn luyện (Train)", "2,140 ảnh", "80.03%", "164 ảnh (7.7%)", "6,655 boxes", "YOLO 5 cột"),
        ("Tập Kiểm định (Validation)", "267 ảnh", "9.99%", "17 ảnh (6.4%)", "724 boxes", "YOLO 5 cột"),
        ("Tập Kiểm thử Độc lập (Test)", "267 ảnh", "9.99%", "20 ảnh (7.5%)", "718 boxes", "YOLO 5 cột"),
        ("TỔNG CỘNG TOÀN BỘ", "2,674 ảnh", "100.0%", "201 ảnh (7.5%)", "8,097 boxes", "100% HỢP LỆ")
    ]

    for row_data in ds_rows:
        row = tbl_ds.add_row()
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            set_cell_margins(cell, 50, 50, 70, 70)
            cell.width = d_widths[j]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            if j in [1, 2, 3, 4, 5]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if "TỔNG" in row_data[0]:
                r.font.bold = True
                set_cell_background(cell, HEX_BG_LIGHT)
                r.font.color.rgb = COLOR_PRIMARY
            else:
                r.font.color.rgb = COLOR_DARK

    doc.add_paragraph()

    add_body_paragraph(
        doc,
        "Đặc điểm phân chia tập dữ liệu và giải trình con số 1.327 tiền tố tên tệp duy nhất: "
        "Áp dụng phương pháp phân chia dựa trên quy tắc tiền tố tên tệp (filename prefix grouping: bóc tách đuôi băm Roboflow .rf.<hash> "
        "theo scripts/reorganize_dataset.py). Khi chuẩn hóa 2.674 ảnh bằng cách bỏ chuỗi mã băm, tập dữ liệu ghi nhận đúng 1.327 tiền tố tên tệp duy nhất (unique filename prefixes). "
        "Sự chênh lệch so với giả định 1.337 cặp (nếu chia đôi từ 2.674) xuất phát từ việc chính sách tăng cường (augmentation) trên Roboflow không sinh đều đúng 2 phiên bản cho mọi ảnh: "
        "trong đó 933 nhóm tiền tố có 2 ảnh (1.866 ảnh), 307 nhóm chỉ có 1 ảnh không qua tăng cường (307 ảnh), "
        "và 87 nhóm còn lại có từ 3 đến 13 ảnh (501 ảnh). Tổng cộng: 1.866 + 307 + 501 = 2.674 ảnh. "
        "Cần lưu ý đây là quy ước phân nhóm hình thức theo tiền tố tên tệp mã hóa; phép đếm này chưa tự chứng minh chúng hoàn toàn là 1.327 ảnh nguồn độc lập về bối cảnh thực địa, "
        "đồng thời dự án chưa kiểm định độc lập về mức độ cô lập tuyệt đối mọi góc quay hay bối cảnh thực địa giữa các split."
    )

    add_body_paragraph(
        doc,
        "Cơ sở kỹ thuật tích hợp 201 mẫu nền âm tính (Negative Background Samples): "
        "Theo tài liệu kỹ thuật chính thức của Ultralytics (Ultralytics YOLO Docs: Tips for Best Training Results - Background Images: "
        "'Background images are images with no objects that are added to a dataset to reduce False Positives. Ultralytics recommends ~0-10% background images to help reduce FPs (COCO has 1000 background images for reference, 1% of total)'), "
        "nhóm nghiên cứu đã tích hợp 201 bức ảnh nền âm tính thuần túy (chiếm 7.52% toàn bộ dataset, nằm trong dải khuyến nghị 0%–10%). "
        "Các mẫu này bao gồm: hè phố trống vắng ban đêm, cửa cuốn nhà dân đóng kín, tường hoa, mái tôn không có biển hiệu, "
        "nhằm giúp mạng nơ-ron giảm thiểu các kích hoạt cảnh báo giả (False Positives) ở vùng hậu cảnh tĩnh không có biển hiệu."
    )

    # Chèn Hình 1 & 2 đã chuẩn hóa
    add_image_with_caption(
        doc,
        "reports/figures/roboflow_sample_annotated.jpg",
        "Hình 1. Mẫu ảnh gán nhãn chuẩn YOLO (5 cột: class_id cx cy w h) trích xuất trực tiếp từ datasets/v13_clean/train/",
        asset_path="reports/figures/roboflow_sample_annotated.jpg (ảnh mẫu chuẩn hóa, người dùng có thể tùy chọn thêm từ reports/figures/annotated_samples/)",
        how_to_get="Trích xuất từ datasets/v13_clean/train/images/ và vẽ nhãn tọa độ từ datasets/v13_clean/train/labels/."
    )

    add_image_with_caption(
        doc,
        "reports/figures/negative_samples_grid.jpg",
        "Hình 2. Lưới 4 mẫu nền âm tính thuần túy (Negative Background Samples, nhãn rỗng 0 byte) trích xuất từ datasets/v13_clean/train/",
        asset_path="reports/figures/negative_samples_grid.jpg (gồm 4 ảnh nền âm tính đại diện: 100_png, 12_png, 14_png, 16_png)",
        how_to_get="Trích xuất trực tiếp từ các tệp ảnh có nhãn rỗng (0 KB .txt) trong datasets/v13_clean/train/labels/."
    )

    style_section_heading(doc, "Bảng 3. Bảng Kiểm toán Toàn vẹn Cấu trúc Dataset YOLO theo Quy chuẩn Ultralytics", level=2)

    tbl_audit = doc.add_table(rows=1, cols=4)
    tbl_audit.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_audit)

    aud_headers = ["Hạng mục kiểm tra", "Quy chuẩn kỹ thuật Ultralytics", "Kết quả thực tế đo đạc", "Trạng thái"]
    aud_widths = [Inches(1.8), Inches(2.2), Inches(1.8), Inches(1.0)]
    format_table_header(tbl_audit.rows[0], aud_headers, aud_widths)

    aud_rows = [
        ("Cấu hình data.yaml", "Khai báo nc, names, train/val/test path", "nc: 1, names: {0: 'bien-quang-cao'}, đường dẫn chuẩn", "ĐẠT CHUẨN"),
        ("Quy tắc Mirror Rule", "Ánh xạ 1:1 giữa images/ và labels/", "2,674 ảnh đều có tệp nhãn tương ứng (2,674 tệp .txt)", "ĐẠT CHUẨN"),
        ("Cú pháp nhãn BBox", "Chuẩn 5 cột: class_id cx cy w h", "100% nhãn đúng 5 cột, tọa độ chuẩn hóa trong khoảng [0, 1]", "ĐẠT CHUẨN"),
        ("Tỷ lệ mẫu âm tính", "Khuyến nghị Ultralytics: 0% - 10% ảnh nền (COCO ~1%)", "201 ảnh nền âm tính (chiếm 7.52% toàn bộ dataset)", "ĐẠT CHUẨN"),
        ("Quy mô ảnh huấn luyện", "Tối thiểu 1.000 ảnh sẵn sàng train", "2,674 ảnh (1,327 tiền tố tên tệp duy nhất)", "VƯỢT CHỈ TIÊU"),
        ("Kiểm toán cấu trúc cú pháp", "0 lỗi cú pháp, 0 box ngoài ranh giới [0, 1]", "Đã quét bằng validate_dataset.py: 0 lỗi, 0 cảnh báo", "ĐẠT CÚ PHÁP (VALID SYNTAX)")
    ]

    for row_data in aud_rows:
        row = tbl_audit.add_row()
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            set_cell_margins(cell, 50, 50, 70, 70)
            cell.width = aud_widths[j]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            if j == 3:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if j == 0:
                r.font.bold = True
                r.font.color.rgb = COLOR_DARK
            elif j == 3:
                r.font.bold = True
                r.font.color.rgb = COLOR_GREEN
            else:
                r.font.color.rgb = COLOR_DARK

    doc.add_paragraph()

    # =========================================================================
    # PHẦN 3: NHIỆM VỤ 3 - HOÀN THIỆN ROI ĐA CAMERA
    # =========================================================================
    style_section_heading(doc, "3. NHIỆM VỤ 3: THIẾT LẬP ROI ĐA CAMERA VÀ KIỂM TRA TRỰC QUAN", level=1)

    add_body_paragraph(
        doc,
        "Để hệ thống AI có căn cứ không gian phán quyết hành vi lấn chiếm hè phố, "
        "nhóm nghiên cứu đã thiết lập các tệp cấu hình Đa giác ROI vỉa hè (Static Polygon ROI & Multi-ROI) riêng biệt cho từng camera trong configs/. "
        "Các đa giác này đã được cấu hình và kiểm tra trực quan trên khung hình đại diện của cả 6 video thử nghiệm, "
        "bao trọn phần không gian hành lang vỉa hè dành cho người đi bộ quan sát được qua ống kính camera từ chân tường nhà dân đến mép bo vỉa hè tiếp giáp lòng đường xe chạy."
    )

    style_section_heading(doc, "Bảng 4. Đặc tả Kỹ thuật 6 Cấu hình ROI Đa Camera trong Workspace", level=2)

    tbl_roi = doc.add_table(rows=1, cols=6)
    tbl_roi.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_roi)

    r_headers = ["Camera / Video ID", "Tệp cấu hình JSON", "Độ phân giải", "Số vùng ROI", "Số đỉnh Polygon", "Mô tả ranh giới vỉa hè quan trắc"]
    r_widths = [Inches(1.2), Inches(1.3), Inches(0.8), Inches(0.7), Inches(0.7), Inches(2.1)]
    format_table_header(tbl_roi.rows[0], r_headers, r_widths)

    roi_rows = [
        ("video test.mp4", "roi_video_test.json", "1280x720", "1 vùng", "8 đỉnh", "Bao trọn mặt hè phố từ chân tường đến mép bo hè đường Phố Huế"),
        ("videotesst2.mp4", "roi_videotesst2.json", "1280x720", "1 vùng", "5 đỉnh", "Bao phủ hành lang vỉa hè rộng phía trước dãy cửa hàng Bạch Mai"),
        ("video test3.mp4", "roi_video_test3.json", "1280x720", "1 vùng", "7 đỉnh", "Mô phỏng góc cua vỉa hè tại nút giao đường Trần Đại Nghĩa"),
        ("videotest4.mp4", "roi_videotest4.json", "1280x720", "2 vùng (Multi)", "11 đỉnh", "Bao phủ cả 2 dải vỉa hè bên trái (5 đỉnh) và bên phải (6 đỉnh)"),
        ("videotest5.mp4", "roi_videotest5.json", "1280x720", "1 vùng", "4 đỉnh", "Hình thang bao trọn hành lang đi bộ cự ly gần trước dãy ki-ốt"),
        ("videotest6.mp4", "roi_videotest6.json", "1280x720", "2 vùng (Multi)", "9 đỉnh", "Multi-ROI chia hai bên trục đường chính: hè trái 5 đỉnh, hè phải 4 đỉnh")
    ]

    for row_data in roi_rows:
        row = tbl_roi.add_row()
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            set_cell_margins(cell, 50, 50, 70, 70)
            cell.width = r_widths[j]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            if j in [2, 3, 4]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if j == 0:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            elif j == 1:
                r.font.color.rgb = COLOR_SECONDARY
            else:
                r.font.color.rgb = COLOR_DARK

    doc.add_paragraph()

    # Chèn Hình 3: Composite 6 Camera ROI
    add_image_with_caption(
        doc,
        "reports/figures/tuan_4_8/all_6_cameras_roi_composite.jpg",
        "Hình 3. Lớp phủ Đa giác ROI vỉa hè (màu xanh lá) đối chiếu trực quan trên khung hình đại diện của cả 6 Video Thử nghiệm",
        asset_path="reports/figures/tuan_4_8/all_6_cameras_roi_composite.jpg (ghép từ camera_1 đến camera_6)",
        how_to_get="Chạy script kiểm tra 'python scripts/verify_and_render_rois.py' để tự động nạp video và kết xuất hình ảnh đối chiếu."
    )

    add_body_paragraph(
        doc,
        "Giới hạn kỹ thuật của cơ chế co giãn tọa độ theo độ phân giải (Resolution Scaling): "
        "Tất cả các tệp ROI lưu trữ tọa độ đỉnh dạng pixel ở độ phân giải gốc 1280x720. "
        "Module roi/roi_manager.py hỗ trợ tính năng co giãn tọa độ tuyến tính theo ma trận (Sx = W_stream / 1280, Sy = H_stream / 720). "
        "Tuy nhiên, cần nhấn mạnh giới hạn kỹ thuật: phép co tọa độ theo độ phân giải chỉ bảo toàn ranh giới ROI khi luồng video giữ nguyên góc đặt camera, "
        "khung cắt và tỷ lệ khung hình tương ứng (aspect ratio). Nếu camera thay đổi góc nhìn (xoay góc, pan/tilt/zoom), "
        "thay đổi vị trí lắp đặt hoặc chuyển sang camera khác, vùng vỉa hè thực tế sẽ biến đổi và người quản trị bắt buộc phải kiểm tra lại "
        "cũng như tái thiết lập đa giác ROI cho phù hợp với khung hình mới."
    )

    # =========================================================================
    # PHẦN 4: BẢNG PHÂN ĐỊNH HIỆN TRẠNG TIẾN ĐỘ TUẦN 4–8
    # =========================================================================
    style_section_heading(doc, "4. BẢNG PHÂN ĐỊNH HIỆN TRẠNG TIẾN ĐỘ TUẦN 4–8 (AUDIT MATRIX)", level=1)

    add_body_paragraph(
        doc,
        "Nhằm đảm bảo tính minh bạch học thuật tuyệt đối theo yêu cầu của Giảng viên hướng dẫn, "
        "bảng dưới đây phân định rõ ràng các hạng mục đã hoàn thành, hạng mục chưa hoàn thành và các giới hạn kỹ thuật cần tiếp tục hoàn thiện:"
    )

    tbl_status = doc.add_table(rows=1, cols=4)
    tbl_status.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_status)

    s_headers = ["Hạng mục công việc", "Hiện trạng thực hiện", "Minh chứng đối chiếu trong Workspace", "Đánh giá nghiệm thu"]
    s_widths = [Inches(1.8), Inches(2.2), Inches(1.8), Inches(1.0)]
    format_table_header(tbl_status.rows[0], s_headers, s_widths)

    status_rows = [
        ("Thu thập video thử nghiệm", "Tổng hợp 6 video CCTV mẫu phục vụ kiểm thử bài toán lấn chiếm hè phố (nguồn công khai, chưa xác minh bản quyền/giấy phép khảo sát hiện trường).", "data/videos/*.mp4 (6 tệp, 240 frames/video)", "ĐÃ TỔNG HỢP MẪU"),
        ("Quy mô Dataset chuẩn YOLO", "Đã đóng gói tập dữ liệu sạch v13_clean gồm 2,674 ảnh, 8,097 BBoxes chuẩn YOLO, 201 ảnh nền âm tính (1,327 tiền tố tên tệp duy nhất).", "datasets/v13_clean/data.yaml & README.txt", "VƯỢT CHỈ TIÊU (267%)"),
        ("Kiểm toán cấu trúc nhãn", "100% tệp nhãn đạt cú pháp 5 cột chuẩn và tọa độ chuẩn hóa [0, 1] theo validator (chưa chứng minh nội dung ngữ nghĩa mọi nhãn đều hoàn hảo).", "datasets/validate_dataset.py (Exit code 0)", "ĐẠT CÚ PHÁP CHUẨN"),
        ("Đồng bộ trực tiếp Roboflow API", "Chưa thể gọi API trực tiếp do phiên làm việc local không có biến môi trường ROBOFLOW_API_KEY. Dữ liệu đã quản lý và xuất bản hoàn chỉnh qua v13_clean.", "datasets/download_dataset.py & README.roboflow.txt", "CHƯA HOÀN THÀNH (API KEY)"),
        ("Cấu hình ROI cho từng camera", "Hoàn thành 6 tệp cấu hình JSON tương ứng 6 video mẫu, kiểm tra trực quan bao quát hành lang vỉa hè trên khung hình đại diện (thay đổi góc quay cần vẽ lại).", "configs/roi_*.json & reports/figures/tuan_4_8/*.jpg", "ĐÃ THIẾT LẬP ROI MẪU"),
        ("Mức độ cách ly tuyệt đối góc quay giữa các split", "Phân chia dựa trên quy tắc tiền tố tên tệp duy nhất; chưa thực hiện kiểm định độc lập phân loại góc quay riêng biệt.", "reports/known_limitations.md", "GIỚI HẠN KHOA HỌC"),
        ("Thử nghiệm trên Edge Device", "Chưa thực hiện; kế hoạch bố trí tại Tuần 16 theo đúng lộ trình Đề cương ĐATN.", "Đề cương ĐATN khóa 2026.1", "ĐÚNG LỘ TRÌNH (T16)")
    ]

    for row_data in status_rows:
        row = tbl_status.add_row()
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            set_cell_margins(cell, 50, 50, 70, 70)
            cell.width = s_widths[j]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            if j == 3:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if j == 0:
                r.font.bold = True
                r.font.color.rgb = COLOR_DARK
            elif j == 3 and ("HOÀN THÀNH" in val or "VƯỢT" in val or "CHUẨN" in val or "MẪU" in val):
                r.font.bold = True
                r.font.color.rgb = COLOR_GREEN
            elif j == 3 and "CHƯA" in val:
                r.font.bold = True
                r.font.color.rgb = COLOR_RED
            elif j == 3:
                r.font.italic = True
                r.font.color.rgb = COLOR_MUTED
            else:
                r.font.color.rgb = COLOR_DARK

    doc.add_paragraph()

    # =========================================================================
    # PHẦN 5: KẾ HOẠCH BÀN GIAO CHO GIAI ĐOẠN TUẦN 9–11
    # =========================================================================
    style_section_heading(doc, "5. KẾ HOẠCH BÀN GIAO CHO GIAI ĐOẠN TUẦN 9–11", level=1)

    add_body_paragraph(
        doc,
        "Với việc hoàn thành các nội dung kỹ thuật trọng tâm của giai đoạn Tuần 4–8 (Dataset >= 1000 ảnh sạch chuẩn YOLO "
        "và hệ thống ROI đa camera kiểm tra trực quan trên video thử nghiệm), dữ liệu và cấu hình đã sẵn sàng chuyển giao sang giai đoạn Tuần 9–11:"
    )

    doc.add_paragraph("1. Huấn luyện Mô hình YOLOv8n trên Google Colab GPU Tesla T4: Nạp dataset v13_clean, cấu hình imgsz=1280, batch=8, thuật toán tối ưu AdamW với cơ chế EarlyStopping (patience=20).", style='List Bullet')
    doc.add_paragraph("2. Đánh giá và Tinh chỉnh Mô hình: Đo lường Precision, Recall, mAP@50 và mAP@50-95 trên tập Validation và tập Test độc lập 267 ảnh.", style='List Bullet')
    doc.add_paragraph("3. Thử nghiệm Pipeline Toàn phần: Kết nối mô hình nhận diện với bộ lọc không gian ROI và thuật toán bám vết ByteTrack trên chuỗi video CCTV thử nghiệm.", style='List Bullet')

    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign.paragraph_format.space_before = Pt(16)
    r_sig = p_sign.add_run("Hà Nội, Ngày 05 Tháng 11 Năm 2026\nSinh viên thực hiện kính báo,\n\n\nNguyễn Đức Tài Năng — MSSV: 20224083")
    r_sig.font.name = "Arial"
    r_sig.font.size = Pt(10)
    r_sig.font.bold = True
    r_sig.font.italic = True
    r_sig.font.color.rgb = COLOR_PRIMARY

    # Lưu sang các tệp đích
    for target_path in [
        OUTPUT_DIR / "Bao_cao_tien_do_Tuan_4_8_DATN_20224083_ban_cap_nhat.docx",
        OUTPUT_DIR / "Bao_cao_tien_do_Tuan_4_8_DATN_20224083_v2.docx",
        OUTPUT_DIR / "Bao_cao_tien_do_Tuan_4_8_DATN_20224083.docx"
    ]:
        try:
            doc.save(str(target_path))
            print(f"[✓] Đã lưu thành công tệp Word: {target_path}")
        except PermissionError:
            print(f"[!] Tệp đang mở trong Word (bị khóa ghi): {target_path.name}")


if __name__ == "__main__":
    build_progress_report_tuan_4_8()
