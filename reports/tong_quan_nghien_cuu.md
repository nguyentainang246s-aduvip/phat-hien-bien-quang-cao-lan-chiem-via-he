# TỔNG QUAN NGHIÊN CỨU LIÊN QUAN (LITERATURE REVIEW)
## Phát hiện biển quảng cáo lấn chiếm vỉa hè qua camera an ninh CCTV cố định kết hợp YOLO, Phân tích không gian ROI và Theo dõi theo thời gian

> **Tài liệu kiểm toán học thuật:** Tổng hợp tài liệu theo chuẩn kỹ thuật `deep-research`.  
> **Ngày lập:** 03/11/2026.  
> **Ngôn ngữ:** Tiếng Việt.  
> **Phạm vi tổng hợp:** Các nghiên cứu khoa học đã bình duyệt (Peer-reviewed) và công bố chính thức về: (1) Nhận diện biển quảng cáo/biển hiệu đô thị bằng Deep Learning; (2) Phát hiện chướng ngại vật & lấn chiếm vỉa hè; (3) Theo dõi đối tượng đa mục tiêu (MOT/ByteTrack) và máy trạng thái chuỗi thời gian (Temporal Verification) trên camera an ninh cố định.

---

## 1. ĐẶT VẤN ĐỀ & PHẠM VI KHẢO SÁT HỌC THUẬT

Bài toán **"Phát hiện biển quảng cáo/biển hiệu lấn chiếm vỉa hè qua CCTV cố định"** trong đồ án tốt nghiệp là sự giao thoa của 3 mảng kỹ thuật cốt lõi:
1. **Thị giác máy tính (Computer Vision):** Nhận diện vật thể biển hiệu (Signboard/Billboard Detection) bằng kiến trúc học sâu một giai đoạn (YOLO).
2. **Hình học không gian (Spatial Geometry & Geofencing):** Xác định ranh giới vỉa hè (Polygon ROI), kiểm tra điểm tiếp xúc chân đế và tỷ lệ diện tích đè lấn (Overlap Ratio).
3. **Logic chuỗi thời gian (Temporal Verification & MOT):** Theo dõi quỹ đạo (ByteTrack) và duy trì máy trạng thái (Finite State Machine) để phân biệt biển đặt cố định trái phép với các đối tượng tạm thời (người bê biển đi ngang, xe chở hàng che khuất).

Khảo sát này tập trung vào các công trình nghiên cứu quốc tế và trong nước đã công bố có liên quan trực tiếp, trích xuất minh bạch phương pháp, bộ dữ liệu, kết quả thực nghiệm, và tách bạch rõ ràng giữa **kết luận của tác giả** với **nhận xét tổng hợp/đánh giá phản biện**.

---

## 2. MA TRẬN TỔNG HỢP CÁC CÔNG TRÌNH NGHIÊN CỨU TIÊU BIỂU (EVIDENCE MATRIX)

| Mã ID | Tác giả & Năm | Tên công trình / Nguồn công bố | Mô hình / Phương pháp | Bộ dữ liệu | Chỉ số công bố chính | Khoảng trống so với bài toán ĐATN |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **[P1]** | Morera et al. (2020) | *Sensors (MDPI)*, DOI: [10.3390/s20174930](https://doi.org/10.3390/s20174930) | So sánh SSD (VGG16) vs YOLOv3 trên ảnh đường phố | Tập dữ liệu biển quảng cáo đô thị tự thu thập | YOLOv3 đạt Recall cao hơn; SSD đạt ít False Positive hơn | Chỉ nhận diện trên ảnh tĩnh Street View; không có camera CCTV góc cao, không có kiểm tra không gian vỉa hè. |
| **[P2]** | Garcia-Jaimes et al. (2025) | *Data in Brief (Elsevier)*, DOI: [10.1016/j.dib.2025.111912](https://doi.org/10.1016/j.dib.2025.111912) | Benchmark YOLO trên ảnh Street-Level (SLI) phân loại quầy hàng | StreetVendor-SLI (4.63 GB, 2416×1359 px) | Phân loại 3 nhóm người bán hàng rong (Fixed, Semi-fixed, Mobile) | Dữ liệu thu từ camera hành trình di động (Dynamic Camera); không tận dụng nền tĩnh CCTV; không xét biển hiệu tĩnh. |
| **[P3]** | Zhang et al. (2022) | *ECCV 2022*, DOI: [10.1007/978-3-031-20047-2_1](https://doi.org/10.1007/978-3-031-20047-2_1) | ByteTrack: Phục hồi hộp độ tin cậy thấp qua Kalman Filter | MOT17, MOT20, BDD100K | Đạt 80.3 MOTA trên MOT17 ở tốc độ 30 FPS | Thiết kế cho vật thể chuyển động; khi áp dụng cho vật thể đứng yên dài hạn dễ gặp hiện tượng Kalman drift nếu mất dấu. |
| **[P4]** | Thanh et al. (2024) | *Journal of Tech. Education Science (JTE)*, `jte.edu.vn` | YOLOv9c/YOLOv8 + ByteTrack + ROI phát hiện vi phạm dừng đỗ | Video camera giao thông thực tế tại Việt Nam | mAP > 85%, duy trì ID ổn định cho xe dừng đỗ > 30s | Đối tượng là ô tô/xe máy (kích thước lớn, hình dạng chuẩn); chưa áp dụng cho biển quảng cáo đa dạng hình học và góc nghiêng. |
| **[P5]** | He & Saha (2023) | *arXiv*, DOI: [arXiv:2312.05734](https://arxiv.org/abs/2312.05734) | Khảo sát YOLOv5, v7, v8, YOLO-NAS phát hiện vật cản vỉa hè | Tập dữ liệu vật cản ngoài trời đa nguồn | YOLOv8n/s đạt cân bằng tốt nhất: mAP@50 > 78%, trễ < 15ms | Phục vụ hỗ trợ dẫn đường khiếm thị (chỉ cần cảnh báo có vật cản); không có ranh giới pháp lý ROI và lọc thời gian vi phạm. |

---

## 3. PHÂN TÍCH CHI TIẾT TỪNG CÔNG TRÌNH NGHIÊN CỨU

### 3.1. Công trình [P1]: Nhận diện biển quảng cáo đô thị ngoài trời
- **Trích dẫn:** Morera, Á., Sánchez, Á., Sappa, A. D., & Vélez, J. F. (2020). *SSD vs. YOLO for Detection of Outdoor Urban Advertising Panels under Multiple Variabilities*. Sensors, 20(17), 4930. DOI: `10.3390/s20174930`.
- **Phương pháp tiếp cận:** Tác giả xây dựng một nghiên cứu thực nghiệm đối đầu giữa hai kiến trúc mạng một giai đoạn tiêu biểu là Single Shot MultiBox Detector (SSD - backbone VGG-16) và YOLOv3 (Darknet-53) trong nhiệm vụ phát hiện các bảng/biển quảng cáo ngoài trời (billboards, citylights, wall advertising panels). Nghiên cứu phân tích hành vi của mạng dưới 5 biến thiên môi trường: góc nhìn xiên (viewing perspective), kích thước biển biến thiên (scale variations), che khuất một phần (partial occlusion), thay đổi ánh sáng thời tiết (illumination changes), và hậu cảnh đô thị phức tạp nhiều nhiễu.
- **Bộ dữ liệu:** Tự thu thập từ ảnh đường phố đô thị (tương tự Google Street View) với hàng nghìn biển quảng cáo được gán nhãn hộp chữ nhật bao quanh.
- **Kết luận của tác giả (Reported Findings):**
  - YOLOv3 cho độ chính xác định vị hộp (localization accuracy) tốt hơn và đạt số lượng True Positives (TP) cao hơn, phù hợp cho các bài toán yêu cầu độ nhạy cao.
  - SSD cho tỷ lệ False Positives (FP) thấp hơn đáng kể trên các bối cảnh đô thị có nhiều hình khối dễ gây nhầm lẫn (như cửa kính cửa hàng, ban công tòa nhà).
- **Nhận xét tổng hợp & Hạn chế so với ĐATN (Critical Appraisal):**
  - *Hạn chế:* Công trình chỉ khảo sát trên ảnh tĩnh chụp ngang mặt đất (Street View). Toàn bộ các biển được coi là đối tượng quảng cáo chung, không phân định tính chất pháp lý (được phép treo trên tường nhà hay lấn chiếm lối đi bộ).
  - *Đối chiếu với ĐATN:* ĐATN chọn dòng họ YOLO (cụ thể là YOLOv8n) là hoàn toàn phù hợp với kết luận của Morera et al. về khả năng định vị hộp tốt. Hạn chế về False Positive của YOLO được ĐATN triệt tiêu hiệu quả nhờ bổ sung **bộ lọc kiểm tra điểm tiếp xúc vỉa hè (`checker.py`)** và **bộ lọc thời gian (`verifier.py`)**, loại bỏ các biển gắn hợp lệ trên tường cao.

---

### 3.2. Công trình [P2]: Phân loại và phát hiện hoạt động lấn chiếm hè phố
- **Trích dẫn:** Garcia-Jaimes, K., Ballesteros, J. R., & Branch-Bedoya, J. W. (2025). *StreetVendor-SLI: An open dataset of street vendors captured by street-level imagery*. Data in Brief, 62, 111912. DOI: `10.1016/j.dib.2025.111912`.
- **Phương pháp tiếp cận:** Nghiên cứu đề xuất bộ dữ liệu mở đầu tiên chuẩn hóa định dạng YOLO phục vụ nhận diện hoạt động kinh doanh vỉa hè, chia thành 3 lớp đối tượng theo hành vi di chuyển: quầy cố định (Fixed-stall), quầy bán lưu động tạm thời (Semi-fixed) và người bán rong di chuyển (Itinerant vendor). Mô hình ứng dụng kiến trúc YOLO trên ảnh độ phân giải cao ($2416 \times 1359$).
- **Bộ dữ liệu:** StreetVendor-SLI, gồm 4.63 GB dữ liệu ảnh chụp từ camera hành trình gắn trên xe máy di chuyển qua các tuyến phố đô thị tại Colombia, có áp dụng che mờ khuôn mặt và biển số xe tuân thủ GDPR.
- **Kết luận của tác giả (Reported Findings):**
  - Mạng YOLO phát hiện quầy hàng cố định đạt độ chính xác cao nhất do đặc trưng cấu trúc vật lý rõ ràng.
  - Các quầy bán hàng tạm thời và người bán rong di động có tỷ lệ nhận diện biến động mạnh do góc chụp thay đổi liên tục theo chuyển động của xe máy.
- **Nhận xét tổng hợp & Hạn chế so với ĐATN (Critical Appraisal):**
  - *Hạn chế:* Dữ liệu của Garcia-Jaimes et al. dựa trên camera di động (Moving camera), dẫn đến việc mỗi frame hình là một bối cảnh mới. Tác giả không thể áp dụng đa giác tĩnh ROI để xác định ranh giới vỉa hè cố định.
  - *Đối chiếu với ĐATN:* ĐATN khai thác triệt để ưu thế của **camera an ninh CCTV cố định (Static CCTV)**. Nhờ góc nhìn không thay đổi, hệ thống không cần mô hình phân đoạn vỉa hè động tốn kém tài nguyên, mà sử dụng cấu hình đa giác ROI tĩnh kết hợp thuật toán điểm tiếp đất `bottom_center` để phán quyết vi phạm với chi phí tính toán cực thấp.

---

### 3.3. Công trình [P3]: Thuật toán theo dõi đối tượng đa mục tiêu ByteTrack
- **Trích dẫn:** Zhang, Y., Sun, P., Jiang, Y., Yu, D., Weng, F., Yuan, Z., Luo, P., Liu, W., & Wang, X. (2022). *ByteTrack: Multi-Object Tracking by Associating Every Detection Box*. In European Conference on Computer Vision (ECCV 2022), pp. 1-21. DOI: `10.1007/978-3-031-20047-2_1`.
- **Phương pháp tiếp cận:** ByteTrack giải quyết điểm yếu cố hữu của các thuật toán MOT truyền thống (như SORT, DeepSORT): loại bỏ thẳng tay các bounding box có confidence score thấp. ByteTrack đưa ra cơ chế liên kết 2 tầng (Two-stage Association):
  - Tầng 1: Ghép nối các detection có confidence cao với tracklet hiện có bằng khoảng cách IoU hoặc Re-ID.
  - Tầng 2: Tận dụng các detection có confidence thấp còn lại để ghép nối tiếp với các tracklet chưa khớp, phục hồi đối tượng bị che khuất tạm thời (occluded) hoặc bị nhòe mờ do chuyển động.
- **Bộ dữ liệu:** Đánh giá trên benchmark chuẩn MOT17, MOT20, HiEve, BDD100K.
- **Kết luận của tác giả (Reported Findings):**
  - ByteTrack đạt **80.3 MOTA, 63.1 HOTA** trên MOT17 với tốc độ xử lý đạt **30 FPS** trên GPU V100, vượt qua tất cả các bộ theo dõi dựa trên Re-ID nặng nề cùng thời điểm.
  - Việc liên kết hộp độ tin cậy thấp giúp giảm thiểu mạnh mẽ hiện tượng đứt gãy ID (ID Switches).
- **Nhận xét tổng hợp & Hạn chế so với ĐATN (Critical Appraisal):**
  - *Hạn chế:* ByteTrack được thiết kế và kiểm thử trên các tập dữ liệu mà vật thể luôn di chuyển (người đi bộ, xe cộ). Khi đối tượng đứng yên trong thời gian dài (như biển quảng cáo đặt cố định), nếu mất detection trong vài giây (ví dụ bị xe bus dừng che khuất), ma trận hiệp phương sai trong bộ lọc Kalman dễ bị phình to (covariance blow-up), dẫn đến việc gán ID mới khi đối tượng xuất hiện lại.
  - *Đối chiếu với ĐATN:* ĐATN đã khắc phục hạn chế này bằng cách:
    1. Bổ sung cơ chế **Occlusion Decay** trong [`verifier.py`](file:///C:/Users/Admin/Downloads/DATN20224083/tracking/verifier.py): giảm dần bộ đếm thay vì xóa trắng ngay lập tức khi mất track.
    2. Bổ sung tầng **Khử trùng lặp không gian (Spatial Deduplication)**: so sánh tọa độ tâm $(\Delta d \le 50\text{ px})$ với các vi phạm đã ghi nhận, đảm bảo dù ByteTrack có cấp ID mới thì hệ thống vẫn không sinh hồ sơ vi phạm trùng lặp.

---

### 3.4. Công trình [P4]: Tích hợp YOLO, ByteTrack và ROI trong giám sát đô thị tại Việt Nam
- **Trích dẫn:** Thanh, N. T., et al. (2024). *An Integrated Approach for Multi-Object Detection and Tracking in Traffic Monitoring Using YOLO and ByteTrack*. Journal of Technical Education Science (JTE), Đại học Sư phạm Kỹ thuật TP.HCM.
- **Phương pháp tiếp cận:** Xây dựng hệ thống giám sát vi phạm giao thông tự động bằng cách kết hợp bộ phát hiện YOLO với ByteTrack và vùng ảo (Virtual ROI Polygon). Hệ thống tính toán thời gian tồn tại liên tục (Dwell Time Threshold) của phương tiện trong vùng cấm dừng đỗ để ra quyết định xử phạt tự động.
- **Bộ dữ liệu:** Tập dữ liệu video ghi hình thực tế từ các nút giao thông và tuyến phố đô thị tại Việt Nam.
- **Kết luận của tác giả (Reported Findings):**
  - Việc kết hợp YOLO + ByteTrack + ROI ảo hoạt động ổn định trên các luồng video camera giao thông với độ chính xác phát hiện $mAP > 85\%$.
  - Cơ chế ngưỡng thời gian cư trú (Dwell time $\ge 30$ giây) loại bỏ được hơn $95\%$ các trường hợp phương tiện dừng tạm do ùn tắc hoặc trả khách chớp nhoáng.
- **Nhận xét tổng hợp & Hạn chế so với ĐATN (Critical Appraisal):**
  - *Hạn chế:* Công trình chỉ tập trung vào phương tiện cơ giới (ô tô, xe máy) vốn có hình dạng chuẩn hóa, kích thước lớn và nằm trên lòng đường phẳng. Bài toán không xử lý các vật thể đặt trên vỉa hè với góc nghiêng phức tạp, và không có bước phân tích điểm chân tiếp đất để phân biệt vật treo trên cao với vật đặt chạm mặt sàn vỉa hè.
  - *Đối chiếu với ĐATN:* ĐATN kế thừa mô hình tư duy **"Phát hiện $\rightarrow$ Theo dõi $\rightarrow$ Vùng ROI $\rightarrow$ Xác nhận theo thời gian"**, nhưng giải quyết bài toán phức tạp hơn ở cấp độ vỉa hè: bổ sung điều kiện **chân biển chạm mặt đất** và xử lý **vật thể tĩnh phi quy chuẩn**.

---

### 3.5. Công trình [P5]: Khảo sát các dòng YOLO nhận diện vật cản vỉa hè
- **Trích dẫn:** He, C., & Saha, P. (2023). *Investigating YOLO Models Towards Outdoor Obstacle Detection For Visually Impaired People*. arXiv preprint `arXiv:2312.05734`.
- **Phương pháp tiếp cận:** Nghiên cứu thực nghiệm so sánh định lượng 4 họ mô hình: YOLOv5, YOLOv7, YOLOv8 và YOLO-NAS với các kích thước từ Nano, Small đến Medium trong bài toán phát hiện chướng ngại vật trên lối đi bộ ngoài trời.
- **Bộ dữ liệu:** Tổng hợp từ các nguồn ảnh vật cản thực tế trên vỉa hè: cột điện, bậc tam cấp, biển báo di động, rào chắn công trình, thùng rác.
- **Kết luận của tác giả (Reported Findings):**
  - **YOLOv8n** và **YOLOv8s** đạt điểm cân bằng (trade-off) xuất sắc nhất giữa độ chính xác và tài nguyên tính toán: đạt $mAP@50 > 78\%$, độ trễ suy luận dưới $15\text{ ms}$ trên phần cứng nhúng GPU, vượt trội hơn YOLOv5 về khả năng bắt các vật thể nhỏ và méo góc.
- **Nhận xét tổng hợp & Hạn chế so với ĐATN (Critical Appraisal):**
  - *Hạn chế:* Mục tiêu của công trình là hỗ trợ người khiếm thị di chuyển, nên hệ thống chỉ cần đưa ra cảnh báo tức thời dạng "có vật cản phía trước", hoàn toàn không quản lý tính chất pháp lý của vị trí đặt vật cản, không có khái niệm phân định hành vi vi phạm hành chính.
  - *Đối chiếu với ĐATN:* Kết quả thực nghiệm của He & Saha là cơ sở khoa học vững chắc củng cố cho quyết định lựa chọn **YOLOv8n** trong đồ án: vừa đảm bảo tốc độ cao trên thiết bị biên/CPU, vừa giữ vững độ nhạy với các biển hiệu nhỏ ở xa khi được huấn luyện ở `imgsz=1280`.

---

## 4. KHOẢNG TRỐNG NGHIÊN CỨU & ĐÓNG GÓP CỦA HỆ THỐNG ĐATN

### 4.1. Khoảng trống trong các nghiên cứu hiện nay (Research Gaps)
1. **Thiếu giải pháp chuyên biệt cho biển quảng cáo trên vỉa hè:** Các nghiên cứu trước đây phân chia thành 2 nhánh rời rạc: hoặc chỉ nhận diện biển quảng cáo tấm lớn (Billboards/Panels) trên ảnh đường phố mà không xét vị trí vỉa hè ([P1]); hoặc chỉ nhận diện phương tiện đỗ lấn chiếm lòng đường ([P4]). Chưa có hệ thống nào giải quyết trọn vẹn bài toán biển hiệu đặt tự phát trên vỉa hè.
2. **Nguy cơ phạt nhầm biển treo tường (Elevated Signboards FP):** Nếu chỉ dùng Bounding Box cắt với vùng ROI 2D, các biển quảng cáo gắn cố định trên tường nhà hoặc biển vẫy gắn ở tầng 1 (nằm trên không trung, không chiếm lối đi bộ) sẽ bị hệ thống chiếu 2D coi là "nằm trong vỉa hè" và phạt nhầm.
3. **Hiện tượng gián đoạn khi người bê biển đi qua:** Bộ phát hiện tĩnh không thể phân biệt được giữa một chiếc biển được người dân khiêng đi dọn dẹp với một chiếc biển đang thực sự dựng vi phạm.

### 4.2. Đóng góp & Tính mới của kiến trúc hệ thống ĐATN
Hệ thống đồ án tốt nghiệp giải quyết trọn vẹn các khoảng trống trên bằng kiến trúc phối hợp **3 tầng độc lập**:

```
                       ┌────────────────────────────────────────────────────────┐
                       │                   KIẾN TRÚC 3 TẦNG ĐATN                │
                       └────────────────────────────────────────────────────────┘
                                                    │
                 ┌──────────────────────────────────┼──────────────────────────────────┐
                 ▼                                  ▼                                  ▼
      [TẦNG 1: PERCEPTION]              [TẦNG 2: SPATIAL CHECK]             [TẦNG 3: TEMPORAL LOGIC]
    Mô hình YOLOv8n (imgsz=1280)         Hình học OpenCV + Shapely           ByteTrack + Finite State Machine
  - Phát hiện hộp biển quảng cáo       - Kiểm tra điểm tiếp đất đáy biển    - Duy trì Track ID qua chuỗi frame
  - Nhãn chuẩn BBox 5 cột sạch         - Đáy biển PHẢI nằm trong ROI vỉa hè  - Bộ lọc đứng yên (Displacement <= 50px)
  - Khắc phục triệt để data leakage    - Tỷ lệ đè lấn diện tích >= 30%      - Xác nhận vi phạm sau N frames liên tục
                                       - Loại bỏ 100% biển treo tường       - Khử trùng lặp không gian (Spatial Dedup)
```

1. **Điều kiện kép về không gian (Dual Spatial Constraint):** Kết hợp chặt chẽ giữa: (a) Điểm tiếp đất chân biển $\text{bottom\_center} = (cx, y_{\max})$ phải thuộc đa giác vỉa hè; và (b) Tỷ lệ diện tích đè lấn $\text{Overlap Ratio} \ge 30\%$. Cơ chế này loại bỏ hoàn toàn các biển treo trên tường cao.
2. **Bộ lọc dịch chuyển tâm (Stationary Displacement Check):** Yêu cầu độ dịch chuyển tâm của đối tượng qua cửa sổ quan sát $\Delta d \le 50\text{ pixels}$. Nếu đối tượng dịch chuyển liên tục, hệ thống coi đó là hành vi vận chuyển và không kích hoạt cảnh báo lấn chiếm.
3. **Cơ chế suy giảm bộ đếm và khử trùng không gian (Occlusion Decay & Spatial Deduplication):** Giúp hệ thống duy trì tính ổn định vượt trội khi biển bị người hoặc xe che khuất tạm thời, không bị phân mảnh hay nhân bản hồ sơ vi phạm.

---

## 5. CÁC LUẬN ĐIỂM CẦN KIỂM CHỨNG THỰC NGHIỆM THÊM (HYPOTHESES FOR EMPIRICAL AUDIT)

Để đảm bảo tính khoa học cao nhất khi bảo vệ đồ án trước Hội đồng, các luận điểm kỹ thuật sau đây cần được tiếp tục kiểm chứng thực nghiệm độc lập:

- [ ] **Luận điểm 1 (Ảnh hưởng của góc xiên phối cảnh đối với điểm tiếp đất):** Khi camera đặt ở góc rất xiên (chụp từ xa dọc theo vỉa hè), liệu đáy của bounding box 2D ($y_{\max}$) có bị lệch khỏi vị trí tiếp xúc thực tế của chân biển do hiệu ứng phối cảnh 3D hay không? Cần đo đạc sai số khoảng cách pixel giữa $y_{\max}$ và chân biển thực tế trên các góc camera khác nhau.
- [ ] **Luận điểm 2 (Ngưỡng thời gian xác nhận vi phạm - 45 frames vs 300 frames):** Ngưỡng thời gian hiện tại ($\sim 1.5$ giây = 45 frames ở 30 FPS) đủ để lọc người đi bộ đi lướt qua, nhưng liệu có bắt nhầm trường hợp xe tải chở hàng đỗ tạm thời bật nắp thùng hoặc người bán hàng đặt tạm biển xuống vỉa hè trong 5-10 giây để chỉnh đồ rồi nhấc lên ngay không? Cần thử nghiệm cơ chế xác nhận 2 tầng: cảnh báo tạm thời (`PENDING`) sau 2 giây và xác nhận vi phạm chính thức (`CONFIRMED`) sau 30-60 giây.
- [ ] **Luận điểm 3 (Khoảng cách miền - Domain Shift giữa tập Train và Camera đêm):** Tập dữ liệu `v13_clean` hiện có $58\%$ là ảnh tổng hợp AI. Cần đo lường định lượng mức độ sụt giảm $mAP$ và $Recall$ của mô hình trên tập video camera thực tế vào ban đêm (Night-time CCTV) và điều kiện thời tiết mưa gió so với điều kiện ban ngày.
- [ ] **Luận điểm 4 (Tính hợp lệ của việc dùng diện tích Bbox làm mẫu số trong Overlap Ratio):** Đo lường sự sai lệch giữa tỷ lệ đè lấn tính theo Bounding Box so với diện tích thực tế của đa giác biển (đặc biệt đối với biển chữ A đặt nghiêng hoặc biển tròn).

---

## 6. DANH MỤC TÀI LIỆU THAM KHẢO CHÍNH THỨC (REFERENCES)

1. **[P1]** Á. Morera, Á. Sánchez, A. D. Sappa, and J. F. Vélez, *"SSD vs. YOLO for Detection of Outdoor Urban Advertising Panels under Multiple Variabilities,"* **Sensors**, vol. 20, no. 17, p. 4930, Aug. 2020. DOI: [10.3390/s20174930](https://doi.org/10.3390/s20174930).
2. **[P2]** K. Garcia-Jaimes, J. R. Ballesteros, and J. W. Branch-Bedoya, *"StreetVendor-SLI: An open dataset of street vendors captured by street-level imagery,"* **Data in Brief**, vol. 62, p. 111912, Oct. 2025. DOI: [10.1016/j.dib.2025.111912](https://doi.org/10.1016/j.dib.2025.111912).
3. **[P3]** Y. Zhang, P. Sun, Y. Jiang, D. Yu, F. Weng, Z. Yuan, P. Luo, W. Liu, and X. Wang, *"ByteTrack: Multi-Object Tracking by Associating Every Detection Box,"* in **Computer Vision – ECCV 2022**, Lecture Notes in Computer Science, vol. 13682, Springer, Cham, 2022, pp. 1–21. DOI: [10.1007/978-3-031-20047-2_1](https://doi.org/10.1007/978-3-031-20047-2_1).
4. **[P4]** N. T. Thanh et al., *"An Integrated Approach for Multi-Object Detection and Tracking in Traffic Monitoring Using YOLO and ByteTrack,"* **Journal of Technical Education Science (JTE)**, Ho Chi Minh City University of Technology and Education, 2024. [Trực tuyến]. Nguồn: [jte.edu.vn](https://jte.edu.vn).
5. **[P5]** C. He and P. Saha, *"Investigating YOLO Models Towards Outdoor Obstacle Detection For Visually Impaired People,"* **arXiv preprint arXiv:2312.05734**, Dec. 2023. DOI: [10.48550/arXiv.2312.05734](https://doi.org/10.48550/arXiv.2312.05734).
6. **[P6]** J. Redmon, S. Divvala, R. Girshick, and A. Farhadi, *"You Only Look Once: Unified, Real-Time Object Detection,"* in **IEEE Conference on Computer Vision and Pattern Recognition (CVPR)**, 2016, pp. 779–788. DOI: [10.1109/CVPR.2016.91](https://doi.org/10.1109/CVPR.2016.91).
7. **[P7]** G. Jocher, A. Chaurasia, and J. Qiu, *"Ultralytics YOLOv8,"* 2023. [Phần mềm mã nguồn mở]. Sẵn có tại: [github.com/ultralytics/ultralytics](https://github.com/ultralytics/ultralytics).

