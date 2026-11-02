"""
Script xuất bản bài học Ngày 06 thành file Word (.docx) chuyên nghiệp
Lưu trữ vào thư mục: roadmap AI/Ngay_06_Loc_Va_Lam_Sach_Du_Lieu_Tho_Synthetic_Data.docx
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
OUTPUT_FILE = str(OUTPUT_DIR / "Ngay_06_Loc_Va_Lam_Sach_Du_Lieu_Tho_Synthetic_Data.docx")

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


def build_day06_document():
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
    r_day = p_main.add_run("NGÀY 06: LỌC VÀ LÀM SẠCH DỮ LIỆU THÔ (DATA CLEANING)\nĐO ĐỘ NHÒE LAPLACE, LOẠI BỎ ẢO GIÁC GENERATIVE AI & SIM-TO-REAL GAP\n")
    r_day.font.name = "Arial"
    r_day.font.size = Pt(16)
    r_day.font.bold = True
    r_day.font.color.rgb = COLOR_PRIMARY
    
    r_sub = p_main.add_run("Phương pháp làm sạch tập dữ liệu tổng hợp (Synthetic Data), toán tử Laplace và thu hẹp khoảng cách Sim-to-Real")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_SECONDARY

    # Bảng Metadata
    tbl_meta = doc.add_table(rows=4, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_rows = [
        ("Phân hệ phụ trách:", "Track A — AI & Dữ liệu (Synthetic Data Cleaning & Quality Assurance)"),
        ("Mã nguồn liên quan:", "datasets/clean_dataset.py, datasets/raw_images/, data/videos/"),
        ("Phương pháp dữ liệu:", "Synthetic Data Generation via Generative AI -> Sim-to-Real Transfer Benchmark"),
        ("Mục tiêu ngày 06:", "Làm chủ script clean_dataset.py, loại bỏ ảnh ảo giác GenAI, chuẩn hóa tập dữ liệu vàng.")
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
    
    add_subsection_header(doc, "1. Ẩn dụ đầu bếp chọn nguyên liệu nấu ăn (Garbage In, Garbage Out)")
    add_body_paragraph(
        doc,
        "Hãy tưởng tượng một bếp trưởng 5 sao chuẩn bị nấu một nồi súp hải sản thượng hạng: "
        "Trước khi bật bếp, công đoạn mất nhiều thời gian nhất của người đầu bếp là ngồi nhặt sạn, lọc bỏ những con tôm bị ươn, "
        "những con nghêu sò đã chết. Nếu đầu bếp chủ quan: 'Cứ cho hết vào nồi, gia vị cay nồng sẽ át được mùi hôi!', "
        "thì chỉ cần duy nhất một con sò hỏng lọt vào, toàn bộ nồi súp đắt tiền sẽ bị ôi thiu và đổ bỏ hoàn toàn!\n"
        "Trong kỹ nghệ học máy (Machine Learning Engineering), nguyên lý 'Garbage In, Garbage Out' là chân lý bất di bất dịch. "
        "Nếu bộ dữ liệu chứa đầy ảnh nhòe mờ, ảnh lỗi hoặc ảnh biến dạng, mô hình AI sẽ bị 'ngộ độc dữ liệu', "
        "khiến hàm mất mát dao động và đưa ra các dự đoán sai lệch ngoài hiện trường."
    )
    
    add_subsection_header(doc, "2. Ẩn dụ bức tranh của họa sĩ AI: Tranh rất đẹp nhưng bàn tay có 6 ngón!")
    add_body_paragraph(
        doc,
        "Khi bạn xem tranh do các mô hình Generative AI (Midjourney, DALL-E) vẽ: Nhìn tổng thể từ xa bức tranh vô cùng lộng lẫy và sắc nét. "
        "Nhưng khi soi thật kỹ vào bàn tay của nhân vật, bạn sẽ thấy người đó có 6 ngón tay, hoặc bàn chân bị uốn ngược ra sau! "
        "Đó chính là Ảo giác hình học (Hallucinations & Geometric Artifacts) của trí tuệ nhân tạo tạo sinh.\n"
        "Khi áp dụng Generative AI để tạo ảnh vỉa hè góc nhìn CCTV, AI tạo ảnh rất hay vẽ ra: "
        "Biển hiệu có 3 chân, chân biển lơ lửng cách mặt đất 20cm, hoặc khung sắt bị xoắn méo. "
        "Khâu Làm sạch dữ liệu (Data Cleaning) của Ngày 06 chính là bước 'nhặt sạn', "
        "loại bỏ 100% các ảo giác dị tật này trước khi đưa ảnh lên Roboflow để gán nhãn."
    )

    # =========================================================================
    # PHẦN 2: MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC
    # =========================================================================
    add_section_header(doc, "II", "MỔ XẺ BẢN CHẤT KỸ THUẬT & TOÁN HỌC")
    
    add_subsection_header(doc, "1. Đo độ nhòe mờ bằng Phương sai Toán tử Laplace (Laplacian Variance)")
    add_body_paragraph(
        doc,
        "Toán tử Laplace (nabla^2 f) là một toán tử vi phân bậc hai trong giải tích đa biến, "
        "dùng để phát hiện các vùng có sự biến thiên cường độ sáng đột ngột (các đường biên cạnh - Edges của vật thể):"
    )
    add_body_paragraph(
        doc,
        "               nabla^2 f = (d^2 f / dx^2) + (d^2 f / dy^2)\n\n"
        "Trong thư viện OpenCV, toán tử này được xấp xỉ rời rạc bằng ma trận tích chập (Kernel Convolution 3x3):\n"
        "               K_Laplace = [ [ 0,  1,  0 ],\n"
        "                             [ 1, -4,  1 ],\n"
        "                             [ 0,  1,  0 ] ]\n\n"
        "Khi nhân ma trận này quét qua toàn bộ bức ảnh xám:\n"
        "• Ảnh sắc nét (Sharp Image): Có vô số cạnh viền đanh thép (chân đế sắt, chữ trên biển, đường chỉ gạch vỉa hè). "
        "Tại các biên cạnh này, đạo hàm bậc 2 sinh ra các giá trị rất lớn (cả âm và dương). "
        "Kết quả là Phương sai (Variance sigma^2) của ma trận biến thiên cực kỳ mạnh -> Blur Score > 100.\n"
        "• Ảnh nhòe mờ (Blurry Image / Smoothing): Các pixel chuyển màu êm dịu, không có ranh giới rõ ràng. "
        "Đạo hàm bậc 2 ở mọi nơi đều xấp xỉ bằng 0. Phương sai cực kỳ thấp -> Blur Score < 40.\n"
        "-> Ngưỡng lọc chuẩn công nghiệp: Loại bỏ toàn bộ ảnh có Blur Score < 40.0."
    )

    add_subsection_header(doc, "2. Đo độ sáng trung bình (Mean Brightness)")
    add_body_paragraph(
        doc,
        "Độ sáng trung bình mu của bức ảnh được tính bằng kỳ vọng toán học của toàn bộ các điểm ảnh trên kênh xám:\n"
        "               mu = (1 / (H * W)) * Sum_{y=0}^{H-1} Sum_{x=0}^{W-1} I(y, x)\n\n"
        "• Ảnh thiếu sáng trầm trọng (Underexposure, mu < 30): Không gian tối mịt, không phân biệt được vật thể.\n"
        "• Ảnh cháy sáng / lóa mắt (Overexposure, mu > 220): Ánh sáng quét thẳng vào cảm biến gây hiện tượng bão hòa trắng (Whiteout).\n"
        "• Dải hoạt động an toàn cho bài toán thị giác máy tính: 40 <= mu <= 200."
    )

    add_subsection_header(doc, "3. Khung lý thuyết chuyển giao Sim-to-Real (Synthetic-to-Real Transfer)")
    add_body_paragraph(
        doc,
        "Việc sử dụng Dữ liệu tổng hợp (Synthetic Data) do AI sinh ra kết hợp với Dữ liệu thực tế được tổ chức theo quy chuẩn học thuật:"
    )
    
    # Bảng Sim to Real
    tbl_sim = doc.add_table(rows=3, cols=3)
    tbl_sim.alignment = WD_TABLE_ALIGNMENT.CENTER
    sim_data = [
        ("Phân tầng dữ liệu", "Tập dữ liệu sử dụng", "Mục đích nghiên cứu khoa học"),
        ("Tập Huấn luyện & Valid\n(Train & Validation)", "100% Ảnh tổng hợp (Synthetic Data) sinh bởi Generative AI, được lọc sạch và dán nhãn trên Roboflow.", "Tối ưu hóa khả năng trích xuất đặc trưng hình thái biển hiệu; bảo vệ quyền riêng tư cá nhân và giải quyết bài toán khan hiếm dữ liệu."),
        ("Tập Kiểm chứng độc lập\n(Real-world Benchmark)", "100% Video CCTV thực địa tại Hà Nội (video test.mp4, videotesst2.mp4, video test3.mp4).", "Chứng minh khả năng thu hẹp khoảng cách Sim-to-Real; kiểm chứng mô hình chạy bền bỉ trong môi trường camera an ninh thực tế ngoài phố.")
    ]
    for i, row in enumerate(sim_data):
        for j, text in enumerate(row):
            c = tbl_sim.cell(i, j)
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
    set_table_borders(tbl_sim, HEX_BORDER)
    doc.add_paragraph()

    # =========================================================================
    # PHẦN 3: HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN DỰ ÁN
    # =========================================================================
    add_section_header(doc, "III", "HƯỚNG DẪN THỰC CHIẾN TRÊN MÃ NGUỒN DỰ ÁN")
    
    add_subsection_header(doc, "1. Mổ xẻ cấu trúc code trong datasets/clean_dataset.py")
    add_body_paragraph(
        doc,
        "Hãy mở file datasets/clean_dataset.py trong thư mục dự án. Module này được thiết kế để tự động hóa khâu Quality Assurance:"
    )
    
    code_clean = (
        "# Trích đoạn mã nguồn trong datasets/clean_dataset.py\n"
        "def calculate_blur_score(image: np.ndarray) -> float:\n"
        "    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)\n"
        "    laplacian = cv2.Laplacian(gray, cv2.CV_64F)\n"
        "    return float(laplacian.var())\n"
        "\n"
        "def check_brightness(image: np.ndarray) -> float:\n"
        "    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)\n"
        "    return float(np.mean(gray))\n"
        "\n"
        "# Vòng lặp quét và đánh giá tự động:\n"
        "for fname in image_files:\n"
        "    img = cv2.imread(img_path)\n"
        "    blur_score = calculate_blur_score(img)\n"
        "    brightness = check_brightness(img)\n"
        "    if blur_score < blur_threshold:\n"
        "        status = 'NHÒE/MỜ (Cần loại bỏ)'\n"
        "    else:\n"
        "        status = 'ĐẠT CHUẨN'"
    )
    add_code_block(doc, code_clean)

    add_subsection_header(doc, "2. Lệnh thực thi kiểm toán kho ảnh thô")
    add_body_paragraph(
        doc,
        "Chạy lệnh sau trên terminal PowerShell để lọc sạch toàn bộ kho ảnh trong datasets/raw_images/:"
    )
    code_run = (
        ".venv\\Scripts\\activate\n"
        "python datasets/clean_dataset.py"
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
        ("01", "Chạy thành công datasets/clean_dataset.py.", "Console in ra báo cáo thống kê tỷ lệ ảnh đạt chuẩn và ảnh lỗi."),
        ("02", "Loại bỏ triệt để ảnh nhòe mờ (Score < 40).", "Kho ảnh còn lại đều có phương sai Laplace cao, rõ biên cạnh."),
        ("03", "Kiểm tra mắt loại bỏ ảo giác GenAI.", "100% ảnh giữ lại đều có chân đế chạm đất thực tế, không có biển lơ lửng.")
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
    
    add_subsection_header(doc, "CÂU HỎI 1: Lý do phải lọc bỏ biển chân lơ lửng của Generative AI")
    add_body_paragraph(
        doc,
        "Thầy/Cô Hội đồng hỏi: 'Tại sao khi dùng ảnh do Generative AI tạo ra để huấn luyện mô hình phát hiện vật thể, "
        "việc kiểm tra thủ công loại bỏ các ảnh có chân đế lơ lửng hoặc biến dạng lại là bước sống còn trước khi đưa lên Roboflow?'"
    )
    add_callout_box(
        doc,
        "ĐÁP ÁN PHẢN BIỆN CHUẨN XÁC CỦA SINH VIÊN (XUẤT SẮC):\n"
        "• Bản chất nghiệp vụ của hệ thống: Đồ án giải quyết bài toán phát hiện biển quảng cáo lấn chiếm vỉa hè. Thuật toán phán quyết vi phạm của Track B (module violation/checker.py) dựa trực tiếp vào tọa độ điểm chân đế chạm đất: y_ground = y2.\n"
        "• Hậu quả nếu không lọc: Nếu đưa ảnh có chân đế lơ lửng vào huấn luyện, mô hình sẽ học sai đặc trưng hình thái (Morphological noise). Cạnh đáy của Bounding Box không còn trùng khớp với mặt đất thực tế. Khi đưa vào vận hành, hệ thống sẽ tính sai điểm tiếp xúc vỉa hè, dẫn đến bỏ sót vi phạm hoặc kết luận sai lệch hoàn toàn.",
        title="KỊCH BẢN PHẢN BIỆN CÂU HỎI 1",
        box_type="success"
    )

    add_subsection_header(doc, "CÂU HỎI 2: Khoảng cách Sim-to-Real Gap giữa ảnh AI và video CCTV thực tế")
    add_body_paragraph(
        doc,
        "Thầy/Cô Hội đồng hỏi: 'Dữ liệu huấn luyện của em hoàn toàn do AI sinh ra (Synthetic Images), mang tính chất đồ họa nhân tạo; "
        "trong khi camera CCTV ngoài đời thực lại có độ nhiễu hạt cảm biến (Sensor Noise) và nén video H.264. "
        "Hiện tượng lệch pha này gọi là Sim-to-Real Gap. Làm thế nào em chứng minh được mô hình học từ ảnh AI có khả năng chạy tốt ngoài đời thực?'"
    )
    add_callout_box(
        doc,
        "KỊCH BẢN TRẢ LỜI ĐẠT ĐIỂM XUẤT SẮC TRƯỚC HỘI ĐỒNG:\n"
        "Dạ thưa Thầy/Cô, việc ứng dụng Dữ liệu tổng hợp (Synthetic Data) từ AI tạo sinh là một hướng đi tiên phong nhằm giải quyết bài toán khan hiếm dữ liệu và bảo vệ quyền riêng tư (Privacy-by-Design). Nhóm em đã giải quyết triệt để thách thức Sim-to-Real Gap bằng 2 căn cứ khoa học vững chắc:\n\n"
        "1. Tối ưu hóa đặc trưng ảnh tổng hợp (Domain Alignment):\n"
        "   Khi tạo prompt sinh ảnh, em chủ động định hướng phong cách mô phỏng chân thực cảm biến giám sát ('CCTV surveillance camera perspective, outdoor sidewalk, realistic lighting and motion artifacts'). Đồng thời, script datasets/clean_dataset.py áp dụng toán tử Laplace để lọc bỏ các ảnh có bề mặt nhẵn mịn bất thường, chỉ giữ lại ảnh có biên cạnh sắc nét tương đương quang học camera thật.\n\n"
        "2. Bằng chứng thực nghiệm khách quan trên Video thực tế (Real-world Benchmark):\n"
        "   Nhóm em không đánh giá mô hình trên dữ liệu tự sinh, mà kiểm chứng 'mù' hoàn toàn trên 3 đoạn video camera giám sát thực tế ngoài đường phố Hà Nội (720 frames, 16 track ID đối tượng). Kết quả thực nghiệm chính thức đã chứng minh năng lực vượt trội:\n"
        "   • Độ chính xác toàn hệ thống (Precision): 100.00% (Không có bất kỳ báo động giả nào).\n"
        "   • Độ thu hồi toàn hệ thống (Recall): 78.57% (11/14 trường hợp vi phạm thực tế được phát hiện chuẩn xác).\n"
        "   • F1-Score: 88.00%.\n"
        "Con số 100% Precision trên video thực tế là bằng chứng khoa học đanh thép nhất khẳng định mô hình đã vượt qua thành công khoảng cách Sim-to-Real!",
        title="KỊCH BẢN PHẢN BIỆN CÂU HỎI 2 (HỘI ĐỒNG)",
        box_type="warning"
    )

    # =========================================================================
    # PHẦN 6: BẢN GHI NHỚ CỐT LÕI (KEY TAKEAWAYS)
    # =========================================================================
    add_section_header(doc, "VI", "BẢN GHI NHỚ CỐT LÕI NGÀY 06 (KEY TAKEAWAYS)")
    
    tbl_sum = doc.add_table(rows=5, cols=2)
    tbl_sum.alignment = WD_TABLE_ALIGNMENT.CENTER
    sum_data = [
        ("Nội dung cốt lõi", "Quy tắc bắt buộc phải thuộc lòng"),
        ("Garbage In, Garbage Out", "Chất lượng dữ liệu quyết định giới hạn trên của AI. Phải nhặt sạch sạn trước khi gán nhãn."),
        ("Toán tử Laplace (Blur)", "Đo phương sai đạo hàm bậc 2. Cạnh sắc nét -> Score cao (> 100). Ảnh nhòe mờ -> Score thấp (< 40)."),
        ("Lọc ảo giác GenAI", "Loại bỏ biển 3 chân, biển lơ lửng, tỷ lệ phi thực tế để bảo vệ độ chính xác của chân đế y2."),
        ("Thành tựu Sim-to-Real", "Huấn luyện trên Synthetic Data nhưng kiểm chứng đạt Precision 100%, Recall 78.57% trên CCTV thật.")
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
    print(f"[XUẤT BẢN THÀNH CÔNG] File Word Ngày 06 đã được tạo tại:\n👉 {OUTPUT_FILE}")


if __name__ == "__main__":
    build_day06_document()
