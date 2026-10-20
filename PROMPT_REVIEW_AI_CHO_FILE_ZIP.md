# HƯỚNG DẪN & PROMPT MẪU GỬI CHO AI ĐỂ NHẬN XÉT, PHẢN BIỆN VÀ CHẤM ĐIỂM ĐỒ ÁN TỐT NGHIỆP

> **Tệp đính kèm gửi kèm cho AI:** `DATN_AI_Review_Package.zip` (Dung lượng: ~0.95 MB, chứa 111 tệp gồm toàn bộ mã nguồn, cấu hình, dữ liệu thực nghiệm và tài liệu giải trình kỹ thuật).

---

## 📋 HƯỚNG DẪN THỰC HIỆN KHI GỬI CHO AI (ChatGPT / Claude / Gemini / DeepSeek)
1. Mở cửa sổ chat mới với mô hình AI mạnh nhất (khuyến nghị: **Claude 3.5 Sonnet**, **GPT-4o**, **o1**, **Gemini 1.5 Pro** hoặc **DeepSeek R1**).
2. Tải tệp `DATN_AI_Review_Package.zip` lên khung chat (nút kẹp giấy / đính kèm tệp).
3. Sao chép toàn bộ nội dung trong phần **`[NỘI DUNG PROMPT CHÍNH THỨC]`** bên dưới và dán vào ô chat rồi nhấn Gửi.

---

## 🚀 [NỘI DUNG PROMPT CHÍNH THỨC - COPY TOÀN BỘ PHẦN DƯỚI ĐÂY]

```text
Xin chào chuyên gia! Tôi gửi kèm tệp nén "DATN_AI_Review_Package.zip" chứa toàn bộ mã nguồn, cấu hình, dữ liệu thực nghiệm và báo cáo kỹ thuật của Đồ án tốt nghiệp Đại học ngành Công nghệ Thông tin / Khoa học Máy tính.

Bạn hãy đóng vai trò là một "Chuyên gia Trưởng về Thị giác Máy tính (Principal Computer Vision Architect) kiêm Ủy viên Phản biện Hội đồng Chấm Đồ án Tốt nghiệp", tiến hành mổ xẻ, rà soát chi tiết mã nguồn và đưa ra bản nhận xét khoa học, khách quan, sâu sắc và chấm điểm toàn diện cho đồ án này.

================================================================================
THÔNG TIN TỔNG QUAN VỀ ĐỒ ÁN
================================================================================
• Tên đề tài: "Hệ thống giám sát và phát hiện biển quảng cáo/biển hiệu lấn chiếm vỉa hè qua camera CCTV cố định"
• Sinh viên thực hiện: Nguyễn Đức Tài Năng (MSSV: 20224083)
• Mục tiêu & Định vị: Xây dựng Hệ thống Hỗ trợ Ra Quyết định (Decision Support System - Human-in-the-Loop) giúp lực lượng Quản lý Trật tự Đô thị phát hiện, xác minh và lưu trữ bằng chứng phục vụ xử phạt vi phạm lấn chiếm lòng đường hè phố (theo Nghị định 168/2024/NĐ-CP).
• Ràng buộc thực tế: Chạy trực tiếp thời gian thực (>= 30 FPS) trên CPU AVX2 phổ thông (Intel Core i5/i7, không đòi hỏi GPU rời đắt tiền), suy luận qua ONNX Runtime 1.30.

================================================================================
HƯỚNG DẪN RÀ SOÁT TỆP ZIP
================================================================================
Trước khi đưa ra nhận xét, xin vui lòng đọc và kiểm tra các tệp quan trọng trong tệp ZIP:
1. "PROJECT_ESSENTIALS_FOR_AI.txt" & "AI_PROJECT_OVERVIEW.md": Tóm tắt toàn diện bài toán, kiến trúc 5 tầng, số liệu thực nghiệm chuẩn và cơ sở toán học.
2. "tracking/verifier.py": Bộ xác minh chuỗi thời gian (Sliding Window, Perspective-Adaptive Stationary Threshold, Cooldown logic).
3. "evaluation/evaluate_videos.py": Kịch bản đánh giá toàn diện hệ thống trên 3 video CCTV thực tế (720 frames, 16 đối tượng Ground Truth) áp dụng Bipartite Hungarian Matching (Pass 2) và Spatial IoU cực đại.
4. "violation/checker.py" & "roi/roi_manager.py": Thuật toán kiểm tra không gian, Đa giác vỉa hè Multi-ROI, Quy tắc tiếp đất (Base Contact Rule) và tỷ lệ đè vỉa hè (Overlap Ratio >= 30%).
5. "detection/detector.py" & "tracking/tracker.py": Tầng tri giác YOLOv8n ONNX và bám vết đa đối tượng ByteTrack.
6. "dashboard/web_app.py" & "database/db.py": Web Dashboard giám sát trực quan, quy trình Cán bộ phê duyệt/bác bỏ hồ sơ (Human-in-the-Loop), trích xuất bằng chứng (Watermark tem pháp lý + Face Blurring) và cơ chế lọc phân chia theo từng ngày.
7. "tests/": Bộ 15 bài kiểm thử tự động pytest.

================================================================================
CÁC YÊU CẦU ĐÁNH GIÁ CHI TIẾT
================================================================================
Bạn hãy phân tích và trình bày bản đánh giá theo đúng cấu trúc sau:

I. ĐÁNH GIÁ TỔNG QUAN & ẤN TƯỢNG BAN ĐẦU
1. Đánh giá tính thời sự và giá trị ứng dụng thực tế của đề tài đối với bài toán trật tự đô thị thông minh (Smart City) tại Việt Nam.
2. Nhận xét về kiến trúc tổng thể (Phân tách 5 tầng: Reader -> YOLO -> ByteTrack -> Temporal/Spatial Verifier -> Human-in-the-Loop Dashboard).

II. PHÂN TÍCH CÁC ĐIỂM MẠNH CỐT LÕI (STRENGTHS)
Hãy chỉ rõ các ưu điểm nổi bật (kèm dẫn chứng cụ thể từ tệp mã nguồn / giải thuật), tập trung vào:
1. Tư duy kỹ nghệ phần mềm (Software Engineering) và tối ưu hóa hiệu năng biên (Edge Optimization: Frame-Skip, ONNX Runtime CPU, cấu trúc module tách bạch, Clean Code).
2. Chiều sâu thuật toán thị giác máy tính:
   - Quy tắc chân đế tiếp đất (Base Contact Rule) kết hợp Overlap Ratio giải quyết bài toán biển treo tường vs biển đặt đất thế nào?
   - Bộ lọc đứng yên thích ứng phối cảnh (Perspective-Adaptive Stationary Check) trong tracking/verifier.py giải quyết biến dạng cự ly xa ra sao?
   - Khái niệm "Continuous Observation Streak" và cơ chế Decay dung sai 1-2 frame flicker.
3. Tính chuẩn mực khoa học trong thực nghiệm:
   - Cách nhóm tác giả xử lý bài toán ByteTrack ID biến thiên giữa các lần chạy bằng Spatio-Temporal Bipartite Matching (Hungarian algorithm).
   - Sự minh bạch trong phân tích 3 trường hợp False Negative (Right-Censoring, cự ly xa) và 2 True Negative (biển trong nhà, biển gắn tường).
4. Tính hoàn thiện sản phẩm thực tế:
   - Quy trình Human-in-the-Loop, bảo vệ quyền riêng tư (Face Blurring), tem đóng dấu pháp lý (Legal Watermark), và giao diện phân chia hồ sơ theo ngày.

III. PHÂN TÍCH ĐIỂM YẾU, HẠN CHẾ & GÓC KHUẤT KỸ THUẬT (WEAKNESSES)
Hãy đóng vai phản biện nghiêm khắc, chỉ ra các lỗ hổng tiềm ẩn:
1. Hạn chế về tập dữ liệu (Dataset) và mô hình nhận diện: Các trường hợp thời tiết xấu (mưa bão, ban đêm thiếu sáng, sương mù, vật cản che khuất một phần).
2. Hạn chế của phép chiếu 2D sang đa giác vỉa hè: Khả năng xảy ra sai số khi camera bị rung lắc hoặc góc nhìn camera quá thấp / quá phẳng.
3. Khả năng mở rộng (Scalability): Khi hệ thống mở rộng lên hàng chục luồng camera CCTV đồng thời thì kiến trúc SQLite và Web Handler hiện tại gặp nút thắt (bottleneck) ở đâu?

IV. CÁC ĐỀ XUẤT CẢI THIỆN ĐỂ NÂNG TẦM ĐỒ ÁN (RECOMMENDATIONS)
1. Các việc nhỏ sinh viên nên làm ngay trước ngày bảo vệ để bài thuyết minh thêm hoàn hảo.
2. Hướng phát triển dài hạn (nếu phát triển lên bậc Thạc sĩ / Dự án khởi nghiệp thương mại).

V. DỰ ĐOÁN 5 CÂU HỎI HỘI ĐỒNG SẼ XOÁY VÀO & GỢI Ý CÂU TRẢ LỜI ĐIỂM 10 (DEFENSE Q&A SIMULATION)
Hãy mô phỏng 5 câu hỏi "hóc búa" nhất mà các Thầy/Cô trong Hội đồng có thể chất vấn, cùng câu trả lời mẫu ngắn gọn, bản lĩnh, đanh thép và thuyết phục nhất dựa trên mã nguồn.

VI. BẢNG CHẤM ĐIỂM TOÀN DIỆN (THEO THANG ĐIỂM 10 VÀ 100)
Chấm điểm chi tiết từng tiêu chí:
1. Tính cấp thiết, tính mới & giá trị thực tiễn (Trọng số 20%): .../10
2. Chất lượng thiết kế kiến trúc & Kỹ nghệ mã nguồn (Trọng số 25%): .../10
3. Chiều sâu thuật toán AI, Tracking & Logic lọc vi phạm (Trọng số 25%): .../10
4. Phương pháp thực nghiệm, độ tin cậy dữ liệu & kiểm thử (Trọng số 15%): .../10
5. Mức độ hoàn thiện sản phẩm & Khả năng triển khai thực tế (Trọng số 15%): .../10
--------------------------------------------------------------------------------
=> TỔNG ĐIỂM CHUNG CUỘC: .../10 (hoặc .../100)
=> XẾP LOẠI HỌC THUẬT: (Xuất sắc / Giỏi / Khá)
=> KẾT LUẬN & LỜI NHẬN XÉT DÀNH CHO SINH VIÊN BẢO VỆ.
```
