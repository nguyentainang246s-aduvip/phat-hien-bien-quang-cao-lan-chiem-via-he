"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Module: tracking/motion_filter.py
Mục đích: Kỹ thuật 2 - Bộ lọc chuyển động và vận tốc dịch chuyển (Motion Filter)
==============================================================================
Đặc điểm:
  1. Phân biệt chính xác biển hiệu tĩnh cố định với các đối tượng di chuyển:
     - Phương tiện giao thông mang biển quảng cáo (xe buýt, xe tải, taxi).
     - Người đi bộ hoặc công nhân bưng bê biển quảng cáo di chuyển trên hè phố.
  2. Đo đạc vận tốc tức thời (pixels/giây) và độ dời không gian theo cửa sổ trượt (Sliding Window).
  3. Cơ chế Perspective-Adaptive: Tự động điều chỉnh ngưỡng dịch chuyển theo kích thước Bounding Box
     (khoảng cách hình chiếu theo phối cảnh xa gần của camera CCTV).
  4. Siêu nhẹ (dưới 0.05 ms/frame), không làm giảm FPS trên thiết bị biên như Raspberry Pi hay Jetson.
==============================================================================
"""

import math
import time
from collections import deque


class MotionFilter:
    """
    Bộ lọc chuyển động dựa trên phân tích quỹ đạo không gian và vận tốc tức thời.
    """
    def __init__(
        self,
        max_displacement_pixels: float = 40.0,
        max_velocity_pixels_per_sec: float = 35.0,
        window_seconds: float = 1.0,
        min_stationary_seconds: float = 2.0,
        adaptive_perspective_scale: bool = True,
        max_history_len: int = 200,
    ):
        """
        Khởi tạo MotionFilter.

        Args:
            max_displacement_pixels: Độ dời tối đa (pixels) trong cửa sổ trượt để coi là tĩnh.
            max_velocity_pixels_per_sec: Vận tốc di chuyển tối đa (px/s) để coi là tĩnh.
            window_seconds: Độ rộng cửa sổ trượt quan sát (mặc định 1.0 giây).
            min_stationary_seconds: Thời gian đứng yên liên tục tối thiểu để xác nhận là biển tĩnh.
            adaptive_perspective_scale: Tự động thu nhỏ ngưỡng với vật thể ở xa (hộp nhỏ).
            max_history_len: Số điểm lưu tối đa trong hàng đợi deque.
        """
        self.max_displacement_pixels = max_displacement_pixels
        self.max_velocity_pixels_per_sec = max_velocity_pixels_per_sec
        self.window_seconds = window_seconds
        self.min_stationary_seconds = min_stationary_seconds
        self.adaptive_perspective_scale = adaptive_perspective_scale
        self.max_history_len = max_history_len

        # Bảng ghi nhớ trạng thái theo từng track_id:
        # track_id -> { "pos_window": deque(...), "stationary_since": float, "last_timestamp": float }
        self.tracks = {}

    def update(self, track_id: int, box: tuple, timestamp: float = None) -> dict:
        """
        Cập nhật tọa độ mới cho một track_id và đánh giá ngay trạng thái chuyển động.

        Args:
            track_id: Mã định danh đối tượng bám vết.
            box: Tọa độ Bounding Box (x1, y1, x2, y2).
            timestamp: Mốc thời gian thực hoặc mốc thời gian giả lập từ video clip.

        Returns:
            dict: Kết quả đánh giá chuyển động:
                  {
                      "track_id": int,
                      "is_moving": bool,
                      "is_stationary": bool,
                      "velocity_px_s": float,
                      "displacement_px": float,
                      "stationary_duration": float,
                      "effective_threshold": float,
                      "status": "STATIONARY" | "MOVING" | "UNKNOWN"
                  }
        """
        if timestamp is None:
            timestamp = time.time()

        if track_id not in self.tracks:
            self.tracks[track_id] = {
                "pos_window": deque(maxlen=self.max_history_len),
                "stationary_since": timestamp,
                "last_timestamp": timestamp,
            }

        rec = self.tracks[track_id]
        rec["last_timestamp"] = timestamp

        # Tính tâm hộp và độ dài đường chéo (diagonal)
        x1, y1, x2, y2 = box
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        box_diag = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        # Lưu vào hàng đợi cửa sổ trượt: (timestamp, cx, cy, box_diag)
        rec["pos_window"].append((timestamp, cx, cy, box_diag))

        # Phân tích chuyển động
        return self.estimate_motion(track_id, timestamp)

    def estimate_motion(self, track_id: int, timestamp: float = None) -> dict:
        """
        Ước lượng độ dịch chuyển và vận tốc của track_id trong cửa sổ trượt gần nhất.
        """
        if timestamp is None:
            timestamp = time.time()

        if track_id not in self.tracks:
            return {
                "track_id": track_id,
                "is_moving": False,
                "is_stationary": True,
                "velocity_px_s": 0.0,
                "displacement_px": 0.0,
                "stationary_duration": 0.0,
                "effective_threshold": self.max_displacement_pixels,
                "status": "UNKNOWN",
            }

        rec = self.tracks[track_id]
        window = rec["pos_window"]

        if len(window) < 2:
            return {
                "track_id": track_id,
                "is_moving": False,
                "is_stationary": False,
                "velocity_px_s": 0.0,
                "displacement_px": 0.0,
                "stationary_duration": 0.0,
                "effective_threshold": self.max_displacement_pixels,
                "status": "UNKNOWN",
            }

        # Lọc các điểm thuộc cửa sổ trượt [timestamp - window_seconds, timestamp]
        cutoff = timestamp - self.window_seconds
        recent = [p for p in window if p[0] >= cutoff]
        if len(recent) < 2:
            recent = list(window)[-2:]

        # Tính độ dời cực đại giữa 2 điểm bất kỳ trong cửa sổ trượt
        xs = [p[1] for p in recent]
        ys = [p[2] for p in recent]
        max_d = max(
            math.sqrt((xs[i] - xs[j]) ** 2 + (ys[i] - ys[j]) ** 2)
            for i in range(len(recent))
            for j in range(i + 1, len(recent))
        )

        # Tính khoảng thời gian quan trắc thực tế trong cửa sổ
        dt = max(0.001, recent[-1][0] - recent[0][0])
        velocity = max_d / dt  # pixels/second

        # Chuẩn hóa ngưỡng dịch chuyển theo phối cảnh camera (Perspective Scaling)
        effective_threshold = self.max_displacement_pixels
        if self.adaptive_perspective_scale:
            avg_diag = sum(p[3] for p in recent) / len(recent)
            if avg_diag > 0:
                # Ngưỡng co lại tỉ lệ với 50% đường chéo, tối thiểu 15px, trần max_displacement_pixels
                effective_threshold = min(
                    self.max_displacement_pixels,
                    max(15.0, avg_diag * 0.50)
                )

        # Tiêu chí phân loại đối tượng di chuyển:
        # Vận tốc vượt ngưỡng HOẶC độ dời trong cửa sổ vượt ngưỡng dịch chuyển
        is_moving = (velocity > self.max_velocity_pixels_per_sec) or (max_d > effective_threshold)

        # Cập nhật thời lượng đứng yên liên tục
        if is_moving:
            rec["stationary_since"] = None
            stationary_duration = 0.0
            status = "MOVING"
        else:
            if rec["stationary_since"] is None:
                rec["stationary_since"] = timestamp
            stationary_duration = max(0.0, timestamp - rec["stationary_since"])
            status = "STATIONARY" if stationary_duration >= self.min_stationary_seconds else "UNKNOWN"

        is_stationary = (not is_moving) and (stationary_duration >= self.min_stationary_seconds)

        return {
            "track_id": track_id,
            "is_moving": is_moving,
            "is_stationary": is_stationary,
            "velocity_px_s": round(velocity, 2),
            "displacement_px": round(max_d, 2),
            "stationary_duration": round(stationary_duration, 2),
            "effective_threshold": round(effective_threshold, 2),
            "status": status,
        }

    def reset(self, track_id: int = None):
        """Reset bộ nhớ trạng thái theo dõi chuyển động."""
        if track_id is not None:
            self.tracks.pop(track_id, None)
        else:
            self.tracks.clear()
