# BÀI HỌC NGÀY 02: ĐO TỐC ĐỘ XỬ LÝ (FPS) VÀ GIẢI THUẬT LÀM MƯỢT EMA
## Đồ án Tốt nghiệp: Hệ thống Giám sát Biển quảng cáo Lấn chiếm Vỉa hè qua CCTV (DATN20224083)

---

### 1. Mục tiêu bài học
Sau bài học này, bạn sẽ:
- Hiểu chính xác **FPS (Frames Per Second)** là gì và tại sao trong camera an ninh bắt buộc phải đo FPS.
- Hiểu được "bệnh kinh điển" khi đo FPS: Tại sao số FPS đo tức thời lại nhảy giật liên tục khiến người xem nhức mắt?
- Nắm vững giải thuật làm mượt **EMA (Exponential Moving Average)** — một công thức toán học cực ngắn nhưng giúp số FPS hiển thị êm ái, ổn định.
- Mổ xẻ từng dòng code của Class `FPSTracker` trong file [`utils/fps_tracker.py`](file:///C:/Users/Admin/Downloads/DATN20224083/utils/fps_tracker.py) và demo [`scripts/demos/read_video_fps.py`](file:///C:/Users/Admin/Downloads/DATN20224083/scripts/demos/read_video_fps.py).
- Biết cách vẽ khung thông tin (Badge) chuyên nghiệp màu xanh dạ quang lên góc màn hình video bằng `cv2.putText()` và `cv2.rectangle()`.

---

### 2. Tại sao cần học bài này?
Hãy nhớ lại mục tiêu lớn của Đồ án tốt nghiệp này:
> **"Hệ thống phải chạy thời gian thực (Real-time >= 25 FPS) trực tiếp trên CPU thiết bị biên, không đòi hỏi GPU đắt tiền."**

Khi bạn đứng trước Hội đồng chấm thi:
- Thầy cô sẽ hỏi ngay câu đầu tiên: *"Hệ thống của em chạy được bao nhiêu khung hình một giây? Có bị giật lag không?"*
- Nếu bạn không biết đo FPS, bạn không thể chứng minh hệ thống của mình đủ tiêu chuẩn triển khai thực tế.
- Đo FPS chính là chiếc "đồng hồ công-tơ-mét" trên xe máy của bạn, báo cho bạn biết cỗ máy AI đang chạy nhanh hay chậm.

---

### 3. Kiến thức nền tảng (Bản chất từ con số 0)

#### Khái niệm 1: FPS là gì và tính như thế nào?
1. **Khái niệm:** FPS viết tắt của **Frames Per Second** (Số khung hình xử lý được trong 1 giây).
2. **Công thức tính đơn giản nhất:**  
   Nếu máy tính mất $\Delta t = 0.04$ giây để xử lý xong 1 bức ảnh, thì trong 1 giây nó sẽ xử lý được:
   $$\text{FPS} = \frac{1}{\Delta t} = \frac{1}{0.04} = 25\text{ FPS}$$
3. **Bệnh giật số FPS:**  
   Trong thực tế, máy tính lúc thì bận xử lý tác vụ nền của Windows, lúc thì rảnh rỗi. Do đó:
   - Frame 1 mất 0.03s $\to$ FPS = 33.3
   - Frame 2 mất 0.06s $\to$ FPS = 16.6
   - Frame 3 mất 0.02s $\to$ FPS = 50.0  
   Nếu bạn in thẳng con số này lên màn hình, mắt người sẽ thấy con số nhảy liên tục như đèn vũ trường, không thể đọc nổi!

---

#### Khái niệm 2: Giải thuật làm mượt EMA (Exponential Moving Average)
1. **EMA là gì?**  
   Là công thức lấy trung bình có trọng số giữa **kết quả mới đo được** và **kết quả cũ trước đó**.
2. **Công thức EMA trong code:**
   $$\text{FPS}_{\text{mới}} = \alpha \times \text{FPS}_{\text{tức thời}} + (1 - \alpha) \times \text{FPS}_{\text{cũ}}$$
   Trong đó: $\alpha$ (alpha) là hệ số làm mượt, thường chọn từ $0.1$ đến $0.15$.
3. **Ví dụ đời thường:**  
   Tưởng tượng bạn đang đo nhiệt độ phòng. Nếu bạn mở cửa sổ gió lùa 1 giây làm nhiệt kế tụt đột ngột, bạn không thể vội kết luận cả căn phòng đã bị lạnh buốt. Bạn phải kết hợp nhiệt độ hiện tại với nhiệt độ trung bình từ nãy đến giờ. Đó chính là EMA!

---

### 4. Mổ xẻ Code Thật của Dự án

Toàn bộ giải thuật nằm gói gọn trong Class `FPSTracker` tại file [`utils/fps_tracker.py`](file:///C:/Users/Admin/Downloads/DATN20224083/utils/fps_tracker.py):

```python
import time

class FPSTracker:
    def __init__(self, alpha: float = 0.15):
        self.alpha = alpha
        self.prev_time = None
        self.smoothed_fps = 0.0

    def update(self) -> float:
        curr_time = time.perf_counter()
        
        # 1. Khung hình đầu tiên: Chưa có mốc quá khứ để so sánh
        if self.prev_time is None:
            self.prev_time = curr_time
            return 0.0
            
        # 2. Tính khoảng thời gian trôi qua (giây)
        delta_t = curr_time - self.prev_time
        self.prev_time = curr_time
        
        # 3. Tính FPS và làm mượt bằng EMA
        if delta_t > 0:
            instant_fps = 1.0 / delta_t
            if self.smoothed_fps == 0.0:
                self.smoothed_fps = instant_fps
            else:
                self.smoothed_fps = self.alpha * instant_fps + (1.0 - self.alpha) * self.smoothed_fps
                
        return self.smoothed_fps
```

#### Giải thích chi tiết từng dòng:
1. `time.perf_counter()`: Là chiếc đồng hồ bấm giờ chính xác nhất của Python (đo tới phần triệu của giây - microsecond). Ta không dùng `time.time()` vì `perf_counter()` không bị ảnh hưởng khi người dùng chỉnh lại giờ hệ thống.
2. `delta_t = curr_time - self.prev_time`: Lấy giờ hiện tại trừ giờ bức ảnh trước = thời gian xử lý xong 1 bức ảnh.
3. `instant_fps = 1.0 / delta_t`: Tốc độ tức thời của riêng bức ảnh vừa xong.
4. `self.smoothed_fps = self.alpha * instant_fps + (1.0 - self.alpha) * self.smoothed_fps`:  
   - Giả sử $\alpha = 0.15$: Ta chỉ lấy $15\%$ độ biến động của bức ảnh mới, còn giữ lại $85\%$ độ ổn định của các bức ảnh trước.  
   - Kết quả: Con số FPS hiển thị sẽ trôi nhẹ nhàng, êm ái, mắt người đọc rất dễ chịu!

---

### 5. Cách vẽ huy hiệu FPS lên góc Video (`draw_fps_badge`)

Trong file [`scripts/demos/read_video_fps.py`](file:///C:/Users/Admin/Downloads/DATN20224083/scripts/demos/read_video_fps.py) (dòng 75–100):

```python
# 1. Vẽ hộp nền màu xám đen phía sau chữ
cv2.rectangle(frame, (x - 8, y - 5), (x + text_w + 12, y + text_h + 12), (30, 30, 30), -1)

# 2. Vẽ viền hộp màu xanh
cv2.rectangle(frame, (x - 8, y - 5), (x + text_w + 12, y + text_h + 12), (0, 255, 0), 1)

# 3. Vẽ chữ FPS màu xanh neon
cv2.putText(frame, fps_text, (x, y + text_h + 2), font, font_scale, (0, 255, 0), font_thickness, cv2.LINE_AA)
```

- **Tại sao phải vẽ cái hộp màu đen phía sau chữ?**  
  Vì camera ngoài đường có lúc quay cảnh vỉa hè màu trắng, nắng chói chang. Nếu vẽ chữ trực tiếp lên ảnh mà không có nền đen, chữ màu sáng sẽ bị "chìm" vào nền và người xem không đọc được!

---

### 6. Bài tập thực hành
Mở Terminal và chạy lệnh:
```bash
.\.venv\Scripts\python.exe scripts/demos/read_video_fps.py
```
- Quan sát góc trên bên trái: Bạn sẽ thấy khung `Processing FPS: xx.x | Native: 24.0`.
- Nhận xét xem con số FPS có bị giật loạn xạ không, hay chạy rất êm?
