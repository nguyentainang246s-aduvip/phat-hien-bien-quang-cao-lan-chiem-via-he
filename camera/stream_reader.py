"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Camera Ingestion & RTSP Stream Handling (Version 1.3)
TASK: 27 - Xây dựng Module camera/stream_reader.py tự động kết nối lại (Auto-Reconnect)
==============================================================================
"""

import os
import time
import threading
import cv2


class StreamReader:
    """
    Bộ quản lý đọc luồng video và camera CCTV thông minh.
    Hỗ trợ 3 nguồn dữ liệu:
      1. Luồng mạng RTSP CCTV trực tiếp (rtsp://...)
      2. Webcam cổng USB (0, 1, ...)
      3. File video giả lập camera 24/7 (.mp4, .avi)
      
    Tính năng chuyên nghiệp phục vụ đồ án:
      - Tự động kết nối lại (Auto-reconnect) khi camera bị mất mạng / rút nguồn.
      - Chạy luồng đọc nền (Background Thread) để làm rỗng bộ đệm (Buffer Flush),
        đảm bảo frame đưa vào AI luôn là khung hình mới nhất (Zero Latency).
    """
    def __init__(self, source, reconnect_delay: float = 2.0, max_retries: int = 10, loop: bool = False):
        """
        Args:
            source: Nguồn dữ liệu (int nếu là webcam, str nếu là video/RTSP)
            reconnect_delay: Thời gian chờ (giây) trước khi thử kết nối lại
            max_retries: Số lần thử kết nối lại tối đa
            loop: Tự động tua lại khi đọc hết tệp video (mặc định False: dừng khi hết file)
        """
        # Xử lý nếu source là chuỗi số ("0", "1")
        if isinstance(source, str) and source.isdigit():
            self.source = int(source)
            self.is_live_stream = True
        elif isinstance(source, str) and source.lower().startswith(("rtsp://", "http://", "https://")):
            self.source = source
            self.is_live_stream = True
        else:
            self.source = source
            self.is_live_stream = False

        self.reconnect_delay = reconnect_delay
        self.max_retries = max_retries
        self.loop = loop

        self.cap = None
        self.width = 1280
        self.height = 720
        self.fps = 30.0
        self.is_running = False
        self.looped = False
        self._frame_seq = 0
        self._last_consumed_seq = -1
        
        # Thiết lập timeout TCP cho FFmpeg để chống treo luồng C++ khi mất mạng
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|timeout;3000000"
        
        # Luồng nền cho RTSP/Live Stream chống trễ hình (Zero Latency Buffer Flush)
        self._lock = threading.Lock()
        self._cap_lock = threading.Lock()
        self._latest_frame = None
        self._latest_ret = False
        self._latest_ts = 0.0
        self._thread = None
        self._stop_event = threading.Event()

        # Khởi động kết nối ban đầu
        self._connect()

    def _stop_worker_thread(self):
        """Dừng an toàn luồng đọc nền trước khi giải phóng VideoCapture."""
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            if threading.current_thread() != self._thread:
                self._thread.join(timeout=2.5)
        self._thread = None

    def _connect(self) -> bool:
        """Tạo kết nối tới nguồn camera an toàn đa luồng."""
        self._stop_worker_thread()

        with self._cap_lock:
            if self.cap is not None:
                try:
                    self.cap.release()
                except Exception:
                    pass
                self.cap = None

            if not self.is_live_stream and isinstance(self.source, str) and not os.path.exists(self.source):
                print(f"[LỖI] Tệp video không tồn tại trên đĩa: {self.source}")
                return False

            print(f"[CAMERA STREAM] Đang kết nối nguồn: {self.source}...")
            self.cap = cv2.VideoCapture(self.source)

            if not self.cap.isOpened():
                print(f"[CẢNH BÁO] Không thể mở nguồn camera: {self.source}")
                return False

            # Lấy thông số luồng
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
            print(f"[+] Kết nối camera thành công ({self.width}x{self.height}, {self.fps:.1f} FPS)")
        
        # Nếu là live stream / RTSP: Kích hoạt background thread để flush buffer liên tục
        if self.is_live_stream:
            with self._lock:
                self._latest_frame = None
                self._latest_ret = False
                self._latest_ts = 0.0
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._capture_worker, daemon=True)
            self._thread.start()
            # Chờ frame đầu tiên sẵn sàng (tối đa 3.0s cho RTSP I-frame)
            for _ in range(60):
                with self._lock:
                    if self._latest_frame is not None:
                        break
                time.sleep(0.05)
            with self._lock:
                if self._latest_frame is None:
                    print("[CẢNH BÁO] Đã mở kết nối nhưng chưa nhận được frame đầu tiên sau 3.0s.")
                    self._stop_worker_thread()
                    with self._cap_lock:
                        if self.cap is not None:
                            try:
                                self.cap.release()
                            except Exception:
                                pass
                            self.cap = None
                    return False
                
        return True

    def _capture_worker(self):
        """Worker chạy ngầm đọc frame liên tục cho live stream để tránh nghẽn buffer OpenCV."""
        while not self._stop_event.is_set():
            with self._cap_lock:
                cap = self.cap
                if cap is None or not cap.isOpened():
                    time.sleep(0.05)
                    continue
            
            # Đọc frame ngoài _cap_lock để tránh deadlock khi luồng chính gọi release() / _reconnect()
            ret, frame = cap.read()
            if self._stop_event.is_set():
                break

            with self._lock:
                self._latest_ret = ret
                if ret and frame is not None:
                    self._latest_frame = frame
                    self._latest_ts = time.monotonic()
                    self._frame_seq += 1
            if not ret:
                time.sleep(0.05)

    def read(self):
        """
        Đọc 1 frame tiếp theo.
        Tự động xử lý:
          - Video file: Tự động tua lại đầu video nếu bật loop, hoặc dừng an toàn.
          - RTSP/Live stream: Chờ frame mới (Zero Latency Buffer Flush & Duplicate Prevention).
          
        Returns:
            (ret: bool, frame: np.ndarray)
            
        Note: Thuộc tính self.looped được đặt True khi video file tua lại đầu.
        """
        self.looped = False
        
        # 1. Đối với Live Stream / RTSP: Lấy frame mới nhất từ background thread
        if self.is_live_stream:
            start_wait = time.monotonic()
            while not self._stop_event.is_set():
                with self._lock:
                    is_new = (self._frame_seq != self._last_consumed_seq)
                    has_frame = self._latest_frame is not None and self._latest_ret
                    ts_fresh = (time.monotonic() - self._latest_ts) < 5.0
                    if has_frame and ts_fresh and (is_new or (time.monotonic() - start_wait) > 0.05):
                        self._last_consumed_seq = self._frame_seq
                        return True, self._latest_frame.copy()
                if (time.monotonic() - start_wait) > 0.5:
                    break
                time.sleep(0.005)
            
            with self._lock:
                ret = self._latest_ret and (time.monotonic() - self._latest_ts) < 5.0
                frame = self._latest_frame.copy() if (ret and self._latest_frame is not None) else None
            
            if ret and frame is not None:
                return True, frame
                
            # Nếu mất tín hiệu, thử reconnect
            print("[CẢNH BÁO MẤT LUỒNG] Tín hiệu camera bị gián đoạn! Kích hoạt Auto-Reconnect...")
            self._stop_event.set()
            if self._reconnect():
                with self._lock:
                    ret = self._latest_ret
                    frame = self._latest_frame.copy() if (ret and self._latest_frame is not None) else None
                return ret, frame
            return False, None

        # 2. Đối với Video File: Đọc tuần tự từng frame
        if self.cap is None or not self.cap.isOpened():
            if not self._reconnect():
                return False, None

        ret, frame = self.cap.read()

        if not ret or frame is None:
            if not self.loop:
                return False, None
            # Hết video file -> Tua lại đầu nếu bật chế độ lặp
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.looped = True
            ret, frame = self.cap.read()
            return ret, frame

        return ret, frame

    def _reconnect(self) -> bool:
        """Cơ chế tự động kết nối lại khi mất mạng (Fault Tolerance)."""
        if not self.is_live_stream and isinstance(self.source, str) and not os.path.exists(self.source):
            return False
        retries = 0
        while retries < self.max_retries:
            retries += 1
            print(f"[RECONNECT #{retries}/{self.max_retries}] Thử kết nối lại sau {self.reconnect_delay}s...")
            time.sleep(self.reconnect_delay)

            if self._connect():
                print("[THÀNH CÔNG] Đã phục hồi luồng camera CCTV an toàn!")
                return True

        print(f"[LỖI NGHIÊM TRỌNG] Camera không phản hồi sau {self.max_retries} lần thử lại.")
        return False

    def release(self):
        """Giải phóng bộ nhớ phần cứng camera và dừng background thread."""
        self._stop_worker_thread()
        with self._cap_lock:
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
                print("[OK] Đã giải phóng tài nguyên camera.")
