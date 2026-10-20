# BẢNG TRA CỨU KIẾN THỨC ĐÃ HỌC
## SỔ TAY ĐỐI CHIẾU KIẾN THỨC - VỊ TRÍ CODE - TÁC DỤNG

Bảng này được cập nhật liên tục qua từng ngày học để bạn có thể tra cứu nhanh bất cứ lúc nào.

| Kiến thức / Thuật ngữ | Đã học ở đâu? | Được sử dụng ở đâu trong dự án? | Tác dụng kỹ thuật trong code |
| :--- | :--- | :--- | :--- |
| **Bản chất Video số** | Ngày 01 - Bài 1 | `scripts/demos/read_video.py`<br>`camera/video_reader.py` | Hiểu rằng video là một tập hợp các ảnh tĩnh (frames) chạy nối tiếp nhau |
| **Mảng 3D NumPy (BGR)** | Ngày 01 - Bài 1 | `scripts/demos/read_video.py` (dòng 121)<br>`camera/video_reader.py` (dòng 21) | Biến `frame` chứa dữ liệu màu sắc (Height, Width, 3 channels B-G-R) |
| **`cv2.VideoCapture`** | Ngày 01 - Bài 1 | `scripts/demos/read_video.py` (dòng 59)<br>`camera/video_reader.py` (dòng 10) | "Đầu đọc" kết nối tới tệp MP4 hoặc camera RTSP |
| **`cap.read()` -> `(ret, frame)`** | Ngày 01 - Bài 1 | `scripts/demos/read_video.py` (dòng 121)<br>`main.py` (dòng 282) | Rút 1 bức ảnh tiếp theo ra xử lý; `ret=False` báo hết video |
| **`cv2.waitKey(delay_ms)`** | Ngày 01 - Bài 1 | `scripts/demos/read_video.py` (dòng 142) | Điều khiển tốc độ phát video tự nhiên và lắng nghe phím bấm dừng |
| **`cap.release()` & `destroyAllWindows()`** | Ngày 01 - Bài 1 | `scripts/demos/read_video.py` (dòng 168-170)<br>`camera/video_reader.py` (dòng 30) | Thu hồi bộ nhớ RAM, đóng camera và tắt cửa sổ an toàn |
