# BÀI HỌC NGÀY 01: VIDEO SỐ, KHUNG HÌNH (FRAME) VÀ VÒNG LẶP VIDEO VỚI OPENCV
## Đồ án Tốt nghiệp: Hệ thống Giám sát Biển quảng cáo Lấn chiếm Vỉa hè qua CCTV (DATN20224083)

---

### 1. Mục tiêu bài học
Sau khi hoàn thành bài học này, bạn sẽ:
- Hiểu được bản chất khoa học của **Video số** dưới góc nhìn của máy tính và AI: Một video thực chất chỉ là một cuộn phim gồm nhiều bức ảnh tĩnh (gọi là **Frame**) chạy lướt qua mắt người với tốc độ cao.
- Hiểu được cấu trúc dữ liệu của một bức ảnh trong Python: Đó là một **ma trận 3 chiều** (Height, Width, Kênh màu) được quản lý bởi thư viện **NumPy**.
- Nắm vững quy luật màu sắc trong OpenCV: Hệ màu **BGR** (Blue - Green - Red), khác với hệ RGB thông thường.
- Hiểu và tự tay giải thích được từng câu lệnh kinh điển của OpenCV: `cv2.VideoCapture()`, `cap.read()`, `cv2.imshow()`, `cv2.waitKey()`, `cap.release()`.
- Biết cách mã nguồn thật của dự án (`camera/video_reader.py` và `main.py`) đóng gói các lệnh này thành một đối tượng chuyên nghiệp để phục vụ hệ thống giám sát.

---

### 2. Tại sao cần học bài này?
Hãy hình dung hệ thống phát hiện biển quảng cáo lấn chiếm vỉa hè là một nhà máy chế biến. Muốn nhà máy hoạt động, việc đầu tiên là phải **đưa được nguyên liệu thô vào dây chuyền**. 
- Trong dự án này, **nguyên liệu thô chính là các luồng video hoặc camera CCTV ngoài thực địa**.
- Nếu bạn không biết máy tính lấy từng bức ảnh từ video ra bằng cách nào, bạn sẽ không thể hiểu được AI nhận ảnh ở đâu để phát hiện biển hiệu, và càng không thể tính toán được tọa độ lấn chiếm vỉa hè.
- Đây là bài học "vỡ lòng", đặt nền móng vững chắc cho toàn bộ 13 ngày học tiếp theo.

---

### 3. Kiến thức nền tảng (Giải thích từ con số 0)

#### Khái niệm 1: Khung hình (Frame) và Video số
1. **Khái niệm đó là gì?**  
   Một đoạn video không phải là một dải hình ảnh chuyển động liên tục ma thuật. Video là một chuỗi các bức ảnh tĩnh được chụp liên tiếp và chiếu lại thật nhanh (thường là 25 đến 30 bức ảnh trong 1 giây). Mỗi một bức ảnh tĩnh đơn lẻ đó được gọi là một **Khung hình (Frame)**.
2. **Nó dùng để làm gì?**  
   Giúp mắt người nhìn thấy chuyển động mượt mà nhờ hiện tượng lưu ảnh trên võng mạc.
3. **Tại sao dự án cần nó?**  
   Mô hình AI (YOLO) hay các thuật toán hình học **không thể xử lý cả một đoạn video cùng lúc**. Máy tính bắt buộc phải "xé lẻ" video thành từng Frame ảnh đơn lẻ để phân tích từng frame một.
4. **Nó hoạt động như thế nào?**  
   Camera ghi lại 30 frame trong 1 giây. Máy tính lấy frame thứ 1 $\to$ phân tích $\to$ lấy frame thứ 2 $\to$ phân tích $\to$ lặp lại liên tục.
5. **Ví dụ đời sống:**  
   Hãy nhớ lại trò chơi vẽ một nhân vật hoạt hình ở góc mép từng trang của một quyển vở, sau đó dùng ngón tay cái vuốt lật thật nhanh các trang giấy. Nhân vật hoạt hình như đang chuyển động và chạy nhảy. Mỗi trang vở chính là một **Frame**, và thao tác vuốt nhanh chính là **Video**.
6. **Ví dụ code minh họa:**  
   ```python
   # Đọc 1 frame ra khỏi video
   ret, frame = cap.read()
   ```
7. **Nó được sử dụng ở đâu trong dự án thực tế?**  
   Xuất hiện ở dòng 121 tệp `scripts/demos/read_video.py` và dòng 282 tệp `main.py`.

---

#### Khái niệm 2: Ma trận ảnh và Hệ màu BGR trong OpenCV
1. **Khái niệm đó là gì?**  
   Với máy tính, một bức ảnh không phải là bức tranh nghệ thuật, mà là một **bảng số liệu (ma trận số)**. Mỗi điểm trên ảnh gọi là một **Pixel (điểm ảnh)**. Mỗi pixel được pha trộn từ 3 màu cơ bản: Xanh lam (Blue), Xanh lục (Green), Đỏ (Red).
2. **Nó dùng để làm gì?**  
   Dùng để lưu trữ giá trị độ sáng và màu sắc của từng điểm ảnh (giá trị từ 0 đến 255).
3. **Tại sao dự án cần nó?**  
   Để AI và các phép toán hình học biết được kích thước khung hình (chiều cao bao nhiêu pixel, chiều rộng bao nhiêu pixel) nhằm xác định tọa độ của biển hiệu và vỉa hè.
4. **Nó hoạt động như thế nào?**  
   Một ảnh có độ phân giải $1280 \times 720$ sẽ là một mảng NumPy 3 chiều: `(720, 1280, 3)`.  
   *Đặc biệt lưu ý:* OpenCV sắp xếp thứ tự 3 kênh màu là **BGR (Blue - Green - Red)** chứ không phải RGB như thông thường.
5. **Ví dụ đời sống:**  
   Một bức tranh ghép hình (puzzle) làm từ 1.000.000 mảnh ghép nhỏ li ti. Mỗi mảnh ghép có một màu cố định. Nhìn xa thì ra bức tranh hoàn chỉnh, nhìn sát vào kính lúp thì chỉ là từng mảnh ghép riêng biệt.
6. **Ví dụ code minh họa:**  
   ```python
   # Lấy kích thước ảnh
   chieu_cao, chieu_rong, so_kenh_mau = frame.shape
   print(f"Ảnh cao: {chieu_cao}px, Rộng: {chieu_rong}px")
   ```
7. **Nó được sử dụng ở đâu trong dự án thực tế?**  
   `main.py` dòng 290: `fh, fw = frame.shape[:2]` để kiểm tra độ phân giải video phục vụ việc co giãn tọa độ vỉa hè.

---

#### Khái niệm 3: Đối tượng điều khiển Video `cv2.VideoCapture`
1. **Khái niệm đó là gì?**  
   Là một công cụ (Class) được thư viện OpenCV xây dựng sẵn, chuyên dùng để kết nối, mở và giải mã các luồng video (tệp file `.mp4`, webcam máy tính hoặc camera an ninh RTSP).
2. **Nó dùng để làm gì?**  
   Đóng vai trò như một "đầu đĩa/đầu phát" kết nối trực tiếp tới video.
3. **Tại sao dự án cần nó?**  
   Hệ thống giám sát vỉa hè phải nhận video từ file hoặc camera ngoài đường. `cv2.VideoCapture` chính là cổng nhận dữ liệu đầu vào.
4. **Nó hoạt động như thế nào?**  
   Bạn truyền đường dẫn file vào `cv2.VideoCapture("data/videos/test.mp4")`. Nó sẽ nạp codec phần cứng, mở file và đứng chờ lệnh lấy từng frame.
5. **Ví dụ đời sống:**  
   Như một chiếc đầu đọc đĩa DVD. Khi bạn nhét đĩa vào khay, đầu đọc nhận đĩa, kiểm tra xem đĩa có trầy xước không (`isOpened()`), rồi sẵn sàng bấm nút Play để chiếu.
6. **Ví dụ code minh họa:**  
   ```python
   import cv2
   cap = cv2.VideoCapture("data/videos/sample_cctv.mp4")
   if not cap.isOpened():
       print("Lỗi: Không mở được video!")
   ```
7. **Nó được sử dụng ở đâu trong dự án thực tế?**  
   Dòng 59 trong `scripts/demos/read_video.py` và dòng 10 trong `camera/video_reader.py`.

---

#### Khái niệm 4: Hàm `cv2.waitKey(delay_ms)` — Nhịp tim của vòng lặp video
1. **Khái niệm đó là gì?**  
   Là hàm tạm dừng chương trình trong một số mili-giây nhất định, vừa để hệ điều hành kịp vẽ bức ảnh lên màn hình, vừa để "lắng nghe" xem người dùng có bấm phím nào trên bàn phím hay không.
2. **Nó dùng để làm gì?**  
   Kiểm soát tốc độ phát video đúng với đời thực và bắt sự kiện bàn phím (ví dụ: bấm phím `q` để tắt).
3. **Tại sao dự án cần nó?**  
   Nếu không có `waitKey()`, máy tính sẽ đọc hàng trăm frame với tốc độ tối đa của CPU (nhanh như tua gấp), hình ảnh chưa kịp hiển thị lên cửa sổ thì đã vụt qua, hoặc cửa sổ OpenCV sẽ bị treo đơ (Not Responding).
4. **Nó hoạt động như thế nào?**  
   Nếu video có tốc độ 30 FPS, mỗi frame nên cách nhau: $\frac{1000\text{ms}}{30} \approx 33\text{ms}$. Lệnh `cv2.waitKey(33)` sẽ cho chương trình nghỉ 33 mili-giây trước khi sang frame kế tiếp.
5. **Ví dụ đời sống:**  
   Giống như người chiếu phim phải quay tay máy chiếu với tốc độ đều đặn 1 giây được 30 hình. Nếu quay quá nhanh thì phim bị tua tít mù, nếu không quay thì phim đứng im.
6. **Ví dụ code minh họa:**  
   ```python
   # Dừng 33ms và kiểm tra nếu nhấn phím 'q' (ASCII của 'q' là ord('q'))
   if cv2.waitKey(33) & 0xFF == ord('q'):
       break
   ```
7. **Nó được sử dụng ở đâu trong dự án thực tế?**  
   Dòng 142 trong `scripts/demos/read_video.py` và dòng 382 trong `main.py`.

---

### 4. Thực hành kiến thức cơ bản (Ví dụ độc lập dễ chạy)

Dưới đây là một đoạn code Python hoàn chỉnh ngắn gọn nhất giúp bạn hiểu trọn vẹn luồng đọc một video:

```python
import cv2

# 1. Mở file video
video_path = "data/videos/sample_cctv.mp4"
cap = cv2.VideoCapture(video_path)

# Kiểm tra xem OpenCV có đọc được video không
if not cap.isOpened():
    print(f"Không thể mở video tại: {video_path}")
    exit()

print("Bắt đầu phát video... Bấm phím 'q' để dừng.")

# 2. Vòng lặp lấy từng bức ảnh
while True:
    # Lấy 1 frame
    ret, frame = cap.read()
    
    # Nếu ret == False nghĩa là đã hết video
    if not ret:
        print("Đã phát hết video.")
        break
        
    # 3. Hiển thị frame lên cửa sổ
    cv2.imshow("Cua So Phat Video", frame)
    
    # 4. Chờ 30 mili-giây và lắng nghe phím 'q' để thoát
    if cv2.waitKey(30) & 0xFF == ord('q'):
        print("Người dùng đã bấm dừng.")
        break

# 5. Giải phóng bộ nhớ khi kết thúc
cap.release()
cv2.destroyAllWindows()
print("Đã dọn dẹp bộ nhớ xong.")
```

---

### 5. Áp dụng vào dự án thật

Bây giờ chúng ta sẽ soi chiếu vào code thật của dự án:
- **File cần mở:** [`scripts/demos/read_video.py`](file:///C:/Users/Admin/Downloads/DATN20224083/scripts/demos/read_video.py) và [`camera/video_reader.py`](file:///C:/Users/Admin/Downloads/DATN20224083/camera/video_reader.py).

#### Đoạn code cốt lõi cần mổ xẻ (Trích từ `scripts/demos/read_video.py` dòng 116–150):
```python
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print(f"[KẾT THÚC] Đã đọc xong toàn bộ video ({frame_count} frames).")
                break
                
            frame_count += 1
            
            if display:
                cv2.imshow(window_title, frame)
                key = cv2.waitKey(delay_ms) & 0xFF
                if key == ord('q') or key == 27:
                    print(f"[THÔNG BÁO] Người dùng nhấn phím dừng tại frame {frame_count}.")
                    break
```

#### Phân tích chuyên sâu 9 tiêu chí bắt buộc:
1. **Vị trí:** Trong file `scripts/demos/read_video.py`, nằm bên trong hàm `play_video()`, từ dòng 116 đến 150.
2. **Mục đích:** Tạo ra một "trục quay thời gian" liên tục rút từng khung hình từ file video ra để hiển thị lên màn hình máy tính và cho phép người vận hành can thiệp phím bấm.
3. **Kiến thức cần có:** Vòng lặp `while True`, câu lệnh điều kiện `if`, hàm `cap.read()` và `cv2.waitKey()`.
4. **Giải thích cú pháp chi tiết:**
   - `while True:`: Vòng lặp vô tận. Video có bao nhiêu frame thì vòng lặp sẽ chạy bấy nhiêu lần.
   - `ret, frame = cap.read()`: Rút 1 frame. Trả về bộ đôi (Tuple):
     - `ret` (viết tắt của *return status* - kiểu `bool`): Mang giá trị `True` nếu đọc thành công, `False` nếu video bị lỗi hoặc đã hết.
     - `frame`: Mảng đa chiều NumPy chứa toàn bộ điểm ảnh của bức ảnh đó.
   - `if not ret: break`: Nếu `ret` là `False`, lập tức bẻ gãy vòng lặp (`break`) để kết thúc chương trình an toàn, tránh lỗi văng phần mềm.
   - `cv2.imshow(window_title, frame)`: Lệnh vẽ bức ảnh `frame` lên cửa sổ có tên `window_title`.
   - `key = cv2.waitKey(delay_ms) & 0xFF`: Tạm dừng `delay_ms` mili-giây. Phép toán `& 0xFF` (AND với 255) dùng để lấy đúng 8-bit cuối của mã phím trên hệ điều hành Windows, giúp nhận diện chính xác phím bấm bất kể phím NumLock hay CapsLock đang bật hay tắt.
   - `key == ord('q') or key == 27`: `ord('q')` trả về mã số ASCII của phím chữ `q` (mã 113); số `27` là mã ASCII của phím `ESC`.
5. **Cách hoạt động từng bước khi chạy:**
   - Bước 1: Máy tính gọi `cap.read()`, đọc bức ảnh đầu tiên vào biến `frame`. Biến `ret` nhận giá trị `True`.
   - Bước 2: Tăng biến đếm `frame_count` từ 0 lên 1.
   - Bước 3: `cv2.imshow()` dựng bức ảnh lên màn hình.
   - Bước 4: Chương trình tạm dừng 33ms. Nếu bạn không bấm gì, nó quay lại Bước 1 đọc bức ảnh thứ 2.
   - Bước 5: Cứ thế tiếp diễn cho đến khi hết video (`ret == False`) hoặc bạn ấn `q`.
6. **Ví dụ cụ thể về dữ liệu đầu vào và đầu ra:**
   - *Đầu vào:* File video `data/videos/sample_cctv.mp4` kích thước $640 \times 360$, thời lượng 5 giây, 25 FPS (tổng 125 frames).
   - *Đầu ra:* Biến `frame` là một mảng số có kích thước `(360, 640, 3)`. Màn hình xuất hiện cửa sổ phát video mượt mà, sau 125 vòng lặp màn hình console in dòng: `[KẾT THÚC] Đã đọc xong toàn bộ video (125 frames).`
7. **Liên hệ thực tế trong toàn bộ dự án:**
   Trong hệ thống giám sát hoàn chỉnh (`main.py` dòng 282), biến `frame` này sau khi được đọc ra sẽ **không chỉ để hiển thị**, mà ngay lập tức được ném vào:
   - Module `detection/detector.py`: để YOLO quét tìm biển hiệu.
   - Module `roi/roi_manager.py`: để vẽ lớp phủ đa giác vỉa hè lên trên.
   - Module `evidence/saver.py`: để cắt thành ảnh bằng chứng vi phạm.
8. **Nếu bỏ đoạn code này thì sao?**
   - Nếu bỏ `if not ret: break`: Khi video chạy đến frame cuối cùng, `cap.read()` sẽ trả về `frame = None`. Ở dòng tiếp theo, lệnh `cv2.imshow()` gặp `None` sẽ lập tức gây sập chương trình với lỗi nghiêm trọng: `cv2.error: OpenCV(4.x) ... (-215:Assertion failed) size.width>0 && size.height>0 in function 'cv::imshow'`.
   - Nếu bỏ `cv2.waitKey(delay_ms)`: Cửa sổ video sẽ trắng xóa hoặc đóng băng (treo cửa sổ) vì hệ điều hành Windows không được cấp thời gian để render giao diện đồ họa.
9. **Kiểm tra hiểu bài:**
   *Hãy tự trả lời:* Tại sao biến `ret` lại quan trọng đến mức phải kiểm tra ngay sau khi gọi `cap.read()`?

---

#### Cách dự án đóng gói thành Lập trình hướng đối tượng (OOP)
Sau khi bạn đã hiểu hàm thủ tục trong `scripts/demos/read_video.py`, hãy mở tệp [`camera/video_reader.py`](file:///C:/Users/Admin/Downloads/DATN20224083/camera/video_reader.py):

```python
class VideoReader:
    def __init__(self, source_path: str):
        self.source_path = source_path
        self.cap = cv2.VideoCapture(source_path)
        if not self.cap.isOpened():
            raise ValueError(f"Không thể mở nguồn video: {source_path}")
            
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def read(self):
        """Đọc 1 frame tiếp theo (ret, frame)"""
        return self.cap.read()

    def release(self):
        """Giải phóng bộ nhớ camera"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
```
*Nhận xét của Giảng viên:* Bạn có thấy không? Tất cả những dòng lệnh bạn vừa học (`VideoCapture`, `isOpened`, `get`, `read`, `release`) đã được gom gọn vào một **Class** tên là `VideoReader`. Nhờ vậy, trong chương trình chính `main.py`, lập trình viên chỉ cần viết đúng 2 dòng:
```python
reader = VideoReader("data/videos/test.mp4")
ret, frame = reader.read()
```
Code trở nên vô cùng gọn gàng, sáng sủa và chuẩn kỹ sư chuyên nghiệp!

---

### 6. Nhắc lại kiến thức liên quan từ ngày trước
> **Ghi chú:** Đây là bài học mở đầu (Ngày 01), bắt đầu từ con số 0 nên chưa có kiến thức cũ cần ôn tập. Các bài học từ Ngày 02 trở đi sẽ luôn có bảng đối chiếu nhắc lại cụ thể kiến thức của ngày hôm nay.

---

### 7. Bài thực hành dành cho bạn

Bạn hãy mở terminal trong VS Code (hoặc Command Prompt) và thực hiện 2 bài tập sau:

#### Bài tập 1: Chạy thử script demo có sẵn
Chạy lệnh sau trong thư mục dự án để trực tiếp quan sát video mẫu hoạt động:
```bash
python scripts/demos/read_video.py
```
- Quan sát cửa sổ phát video.
- Thử nhấn phím `q` trên cửa sổ video xem chương trình có dừng lại mượt mà hay không.

#### Bài tập 2: Thử nghiệm sửa đổi nhỏ để cảm nhận code
Mở file `scripts/demos/read_video.py`:
- Tại dòng 97, tìm dòng tính `delay_ms`. Thử đổi giá trị thành `delay_ms = 100` (nghỉ 100ms thay vì 33ms).
- Chạy lại lệnh `python scripts/demos/read_video.py`.
- *Hiện tượng gì xảy ra? Tốc độ video nhanh hơn hay chậm lại? Vì sao?*

---

### 8. Câu hỏi kiểm tra hiểu bài (3 Câu hỏi cốt lõi)

1. **Câu hỏi 1 (Bản chất):** Trong OpenCV, khi một bức ảnh được nạp vào biến `frame`, máy tính lưu trữ nó dưới dạng cấu trúc dữ liệu gì? Thứ tự 3 kênh màu của nó là gì?
2. **Câu hỏi 2 (Cơ chế hoạt động):** Hàm `cap.read()` trả về 2 biến `ret` và `frame`. Ý nghĩa của từng biến là gì? Điều gì sẽ xảy ra nếu bạn gọi `cv2.imshow()` khi `ret` mang giá trị `False`?
3. **Câu hỏi 3 (Kỹ thuật):** Vai trò của hàm `cv2.waitKey(delay_ms)` là gì? Nếu trong vòng lặp phát video mà bạn xóa bỏ hoàn toàn dòng lệnh `cv2.waitKey()`, cửa sổ video hiển thị sẽ gặp phải hiện tượng gì?

---

### 9. Đáp án và Hướng dẫn tự kiểm tra

*(Bạn hãy suy nghĩ và trả lời trước khi đọc phần đáp án bên dưới!)*

::: details Bấm vào đây để xem đáp án tham khảo
- **Đáp án Câu 1:**  
  Biến `frame` được lưu trữ dưới dạng một **Mảng đa chiều (ndarray) của thư viện NumPy**. Thứ tự 3 kênh màu trong OpenCV là **BGR (Blue - Green - Red)**, không phải RGB.
- **Đáp án Câu 2:**  
  - `ret` (boolean): Báo trạng thái đọc ảnh (`True` là thành công, `False` là thất bại hoặc hết video).
  - `frame`: Ma trận số chứa dữ liệu pixel của bức ảnh.
  - Nếu `ret == False` mà vẫn gọi `cv2.imshow()`, biến `frame` lúc này là `None`, OpenCV sẽ lập tức báo lỗi rỗng ma trận `(-215:Assertion failed)` và làm chương trình bị sập.
- **Đáp án Câu 3:**  
  Hàm `cv2.waitKey(delay_ms)` có 2 nhiệm vụ: (1) Cung cấp một khoảng thời gian trễ cần thiết để hệ điều hành Windows vẽ bức ảnh lên màn hình; (2) Lắng nghe tín hiệu phím bấm từ bàn phím.  
  Nếu xóa bỏ `cv2.waitKey()`, cửa sổ video sẽ bị **treo đơ, trắng xóa hoặc hiện trạng thái "Not Responding"** vì giao diện đồ họa không có thời gian xử lý sự kiện vẽ hình.
:::

---

### 10. Tổng kết cuối ngày
- Hôm nay bạn đã làm chủ viên gạch đầu tiên quan trọng nhất: **Cách lấy từng bức ảnh từ một luồng video vào bộ nhớ RAM của máy tính.**
- Bạn đã hiểu được biến `frame` chính là "nguyên liệu thô" xuyên suốt mọi ngóc ngách của dự án.
- **Bước tiếp theo (Ngày 02):** Sau khi đã lấy được frame ảnh, làm thế nào để biết hệ thống của chúng ta đang chạy nhanh hay chậm? Chúng ta sẽ học cách **Đo lường tốc độ xử lý FPS thực tế** và giải thuật làm mượt **EMA (Exponential Moving Average)** để hiển thị số FPS mượt mà trên camera giám sát.

---

### 11. Tiêu chí hoàn thành Ngày 01
Bạn được xem là đã hoàn thành xuất sắc Ngày 01 khi:
- [x] Chạy thành công file `scripts/demos/read_video.py` trên máy tính của bạn.
- [x] Hiểu và giải thích được bằng lời của mình câu hỏi: *"Biến `frame` là gì và tại sao cần `cv2.waitKey()`?"*
- [x] Mở được file `camera/video_reader.py` và nhận ra các câu lệnh quen thuộc nằm bên trong Class `VideoReader`.
