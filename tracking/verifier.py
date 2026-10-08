"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Temporal Reasoning & False Positive Elimination
TASK: 22 - Xây dựng Module tracking/verifier.py (Bộ lọc xác nhận theo thời gian)

v2.1 – Sửa lỗi stationary logic:
  - Chuyển từ displacement-from-origin sang cửa sổ trượt (sliding window)
    để không từ chối biển được đặt xuống rồi đứng yên.
  - Tính thời gian vi phạm bằng giây thực (time.time()) thay vì số frame,
    tránh sai lệch khi FPS thay đổi (RTSP trả cùng frame nhiều lần).
  - confirm_seconds là ngưỡng chính; confirm_frames chỉ còn tác dụng fallback
    nếu không lấy được FPS nguồn.
==============================================================================
"""

import time
from collections import deque


class TrackState:
    """Các trạng thái vòng đời của một vật thể biển hiệu được theo dõi."""
    NORMAL = "NORMAL"          # Biển hợp lệ, không lấn chiếm vỉa hè
    SUSPECTED = "SUSPECTED"    # Nghi vấn vi phạm (< N giây liên tiếp, chưa phạt)
    CONFIRMED = "CONFIRMED"    # ĐÃ XÁC NHẬN VI PHẠM (>= N giây liên tiếp)


class TemporalVerifier:
    """
    Bộ lọc xác nhận vi phạm theo chuỗi thời gian (Temporal Verification).

    Nguyên lý: Chỉ kết luận và phát cảnh báo vi phạm khi một đối tượng (track_id)
    duy trì hành vi lấn chiếm vỉa hè liên tục trong tối thiểu N GIÂY THỰC.

    Loại bỏ triệt để:
      - Người đi bộ bê biển đi ngang qua vỉa hè (sliding window displacement).
      - Xe cộ vô tình che khuất chớp nhoáng (Flickering) với tolerance_seconds.
      - Cảnh báo trùng lặp (Spam Alert) nhờ cơ chế Cooldown Timer.

    v2.1 – Sliding window stationary check:
      Thay vì so sánh tâm hiện tại với tâm lúc XUẤT HIỆN (lỗi cũ: biển đặt
      xuống rồi đứng yên 60 frame không bao giờ CONFIRMED), bộ kiểm tra
      nay so sánh độ dời trong cửa sổ trượt 1 giây gần nhất.
      Biển thực sự cố định → doire < max_displacement; người bê biển đi →
      dời liên tục nên ít nhất một lần vượt ngưỡng.
    """

    def __init__(
        self,
        confirm_frames: int = 15,
        confirm_seconds: float = 0.5,
        cooldown_seconds: float = 60.0,
        max_missing_frames: int = 30,
        tolerance_frames: int = 2,
        source_fps: float = None,
    ):
        """
        Args:
            confirm_frames:   Số frames liên tiếp vi phạm tối thiểu (fallback khi
                              không rõ FPS; với 30 FPS → 15 frame ≈ 0.5 giây).
            confirm_seconds:  Thời gian vi phạm liên tiếp tối thiểu (giây) — ưu tiên
                              hơn confirm_frames khi source_fps được cung cấp.
            cooldown_seconds: Thời gian chờ (giây) chống gửi cảnh báo trùng lặp.
            max_missing_frames: Xóa track khỏi RAM nếu mất dấu quá số frame này.
            tolerance_frames: Dung sai frame rung lắc/flicker trước khi reset bộ đếm.
            source_fps:       FPS của nguồn video (dùng để quy đổi giây↔frame).
                              Nếu None → dùng thời gian thực (time.time()).
        """
        self.confirm_frames = confirm_frames
        self.confirm_seconds = confirm_seconds
        self.cooldown_seconds = cooldown_seconds
        self.max_missing_frames = max_missing_frames
        self.tolerance_frames = tolerance_frames
        self.source_fps = source_fps  # Có thể cập nhật sau khi StreamReader khởi xong

        self.min_avg_confidence = 0.40  # Ngưỡng confidence TB tối thiểu để CONFIRMED

        # --- Stationary check (sliding window) ---
        self.require_stationary = True
        self.max_displacement_pixels = 50.0     # Độ dời tối đa trong cửa sổ để coi là đứng yên
        self.stationary_window_seconds = 1.0    # Kích thước cửa sổ trượt kiểm tra đứng yên (giây)

        # Spatial deduplication khi track_id bị đổi
        self.spatial_cooldown_radius = 50.0
        self.confirmed_locations: list = []     # [{cx, cy, time, track_id}, ...]

        # Lưu trạng thái mỗi track_id:
        # {
        #   "count":            int   – số frames vi phạm liên tiếp (fallback)
        #   "viol_start_time":  float – thời điểm bắt đầu chuỗi vi phạm (time.time())
        #   "status":           str   – NORMAL / SUSPECTED / CONFIRMED
        #   "last_seen":        int   – frame index lần cuối nhìn thấy
        #   "last_alert_time":  float – thời điểm gửi cảnh báo lần cuối
        #   "non_viol_streak":  int   – số frames liên tiếp không vi phạm
        #   "conf_sum":         float – tổng confidence để tính trung bình
        #   "pos_window":       deque – hàng đợi [(timestamp, cx, cy), ...] (sliding window)
        # }
        self.track_records: dict = {}
        self.current_frame_index = 0

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _elapsed_viol_seconds(self, record: dict, now: float) -> float:
        """Trả về số giây vi phạm liên tiếp kể từ lần đầu bắt đầu."""
        start = record.get("viol_start_time")
        if start is None:
            return 0.0
        return max(0.0, now - start)

    def _is_stationary(self, record: dict, now: float) -> bool:
        """
        Kiểm tra cửa sổ trượt: lấy tất cả vị trí trong `stationary_window_seconds`
        gần nhất, tính khoảng cách giữa vị trí sớm nhất và muộn nhất trong cửa sổ.
        Nếu khoảng cách < max_displacement_pixels → đứng yên.
        """
        if not self.require_stationary:
            return True

        window = record.get("pos_window")
        if window is None or len(window) < 2:
            return True  # Không đủ dữ liệu → giả định đứng yên

        cutoff = now - self.stationary_window_seconds
        recent = [(t, cx, cy) for (t, cx, cy) in window if t >= cutoff]
        if len(recent) < 2:
            return True

        xs = [p[1] for p in recent]
        ys = [p[2] for p in recent]
        max_d = max(
            ((xs[i] - xs[j]) ** 2 + (ys[i] - ys[j]) ** 2) ** 0.5
            for i in range(len(recent))
            for j in range(i + 1, len(recent))
        )
        return max_d <= self.max_displacement_pixels

    def _confirm_threshold_reached(self, record: dict, now: float) -> bool:
        """
        Kiểm tra đã đạt ngưỡng xác nhận chưa.
        Ưu tiên: giây thực nếu có thể tính được (viol_start_time tồn tại),
        fallback về số frame.
        """
        if record.get("viol_start_time") is not None:
            return self._elapsed_viol_seconds(record, now) >= self.confirm_seconds
        return record["count"] >= self.confirm_frames

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def process_frame(
        self,
        tracked_objects: list,
        checker,
        polygons: list,
        current_timestamp: float = None,
        precomputed_spatial: list = None,
    ) -> list:
        """
        Phân tích chuỗi thời gian cho danh sách đối tượng trong khung hình hiện tại.

        Args:
            tracked_objects:    Danh sách đối tượng từ ObjectTracker (box, conf, track_id)
            checker:            ViolationChecker để kiểm tra hình học không gian
            polygons:           Danh sách đa giác vỉa hè (Multi-ROI)
            current_timestamp:  Mốc thời gian thực (time.time()); mặc định lấy từ hệ thống
            precomputed_spatial: Kết quả spatial đã tính trước (tránh tính 2 lần trong benchmark)
        """
        if current_timestamp is None:
            current_timestamp = time.time()

        self.current_frame_index += 1
        active_ids: set = set()
        enriched_results: list = []

        for idx, obj in enumerate(tracked_objects):
            track_id = obj.get("track_id", -1)
            box = obj["box"]
            conf = obj["conf"]

            # 1. Kiểm tra hình học không gian
            if precomputed_spatial is not None and idx < len(precomputed_spatial):
                spatial_res = precomputed_spatial[idx]
            else:
                spatial_res = checker.check_multi(box, polygons)
            is_spatial_viol = spatial_res["is_violation"]

            # Tính tọa độ tâm
            cx = (box[0] + box[2]) / 2.0
            cy = (box[1] + box[3]) / 2.0

            # Vật thể chưa có track_id hợp lệ (frame đầu tiên xuất hiện)
            if track_id <= 0:
                enriched_results.append({
                    "track_id": track_id,
                    "box": box,
                    "conf": conf,
                    "spatial_res": spatial_res,
                    "temporal_status": TrackState.SUSPECTED if is_spatial_viol else TrackState.NORMAL,
                    "violation_frames": 1 if is_spatial_viol else 0,
                    "is_new_alert": False,
                })
                continue

            active_ids.add(track_id)

            # 2. Khởi tạo bản ghi nếu là ID mới
            if track_id not in self.track_records:
                self.track_records[track_id] = {
                    "count": 0,
                    "viol_start_time": None,
                    "status": TrackState.NORMAL,
                    "last_seen": self.current_frame_index,
                    "last_alert_time": 0.0,
                    "non_viol_streak": 0,
                    "conf_sum": 0.0,
                    "pos_window": deque(maxlen=200),   # ~6.7 giây ở 30 FPS
                }

            record = self.track_records[track_id]
            record["last_seen"] = self.current_frame_index

            # Cập nhật sliding window vị trí
            record["pos_window"].append((current_timestamp, cx, cy))

            # 3. Cập nhật bộ đếm thời gian
            is_new_alert = False

            if is_spatial_viol:
                record["count"] += 1
                record["non_viol_streak"] = 0
                record["conf_sum"] += conf

                # Ghi nhận thời điểm bắt đầu chuỗi vi phạm (chỉ lần đầu)
                if record["viol_start_time"] is None:
                    record["viol_start_time"] = current_timestamp

                # Kiểm tra đã đạt ngưỡng thời gian/frame chưa
                if self._confirm_threshold_reached(record, current_timestamp):
                    avg_conf = record["conf_sum"] / record["count"] if record["count"] > 0 else 0.0

                    # Stationary check (sliding window – sửa lỗi cũ)
                    is_stationary = self._is_stationary(record, current_timestamp)

                    if not is_stationary:
                        # Đang di chuyển → người bê biển đi ngang, giữ SUSPECTED
                        record["status"] = TrackState.SUSPECTED
                    elif avg_conf < self.min_avg_confidence:
                        # Confidence TB quá thấp → giữ SUSPECTED
                        record["status"] = TrackState.SUSPECTED
                    else:
                        record["status"] = TrackState.CONFIRMED

                    # Spatial & temporal deduplication
                    if record["status"] == TrackState.CONFIRMED:
                        is_spatially_cooldown = any(
                            ((cx - c["cx"]) ** 2 + (cy - c["cy"]) ** 2) ** 0.5 <= self.spatial_cooldown_radius
                            and (current_timestamp - c["time"]) < self.cooldown_seconds
                            for c in self.confirmed_locations
                        )
                        time_ok = (current_timestamp - record["last_alert_time"]) >= self.cooldown_seconds

                        if not is_spatially_cooldown and time_ok:
                            is_new_alert = True
                            record["last_alert_time"] = current_timestamp
                            self.confirmed_locations.append({
                                "cx": cx,
                                "cy": cy,
                                "time": current_timestamp,
                                "track_id": track_id,
                            })
                            # Dọn dẹp mốc cũ
                            self.confirmed_locations = [
                                c for c in self.confirmed_locations
                                if (current_timestamp - c["time"]) <= self.cooldown_seconds * 2
                            ]
                else:
                    record["status"] = TrackState.SUSPECTED

            else:
                # Không vi phạm ở frame này
                record["non_viol_streak"] += 1
                if record["non_viol_streak"] > self.tolerance_frames:
                    # Vượt ngưỡng dung sai → reset hoàn toàn
                    record["count"] = 0
                    record["conf_sum"] = 0.0
                    record["viol_start_time"] = None
                    record["status"] = TrackState.NORMAL
                else:
                    # Trong ngưỡng dung sai (1–2 frame flicker)
                    record["count"] = max(0, record["count"] - 1)
                    if record["count"] == 0:
                        record["viol_start_time"] = None
                        record["status"] = TrackState.NORMAL

            enriched_results.append({
                "track_id": track_id,
                "box": box,
                "conf": conf,
                "spatial_res": spatial_res,
                "temporal_status": record["status"],
                "violation_frames": record["count"],
                "violation_seconds": round(self._elapsed_viol_seconds(record, current_timestamp), 2),
                "is_new_alert": is_new_alert,
            })

        # 4. Decay các track bị che khuất (Missing Occlusion Decay)
        for tid, r in self.track_records.items():
            if tid not in active_ids:
                missing_streak = self.current_frame_index - r["last_seen"]
                if missing_streak > self.tolerance_frames:
                    r["count"] = max(0, r["count"] - 1)
                    if r["count"] == 0:
                        r["viol_start_time"] = None
                        r["status"] = TrackState.NORMAL

        # 5. Garbage Collection – xóa track cũ khỏi RAM
        stale_ids = [
            tid for tid, r in self.track_records.items()
            if (self.current_frame_index - r["last_seen"]) > self.max_missing_frames
        ]
        for tid in stale_ids:
            del self.track_records[tid]

        return enriched_results

    def reset(self):
        """Xóa toàn bộ bản ghi trạng thái (khi tua video hoặc đổi camera)."""
        self.track_records.clear()
        self.confirmed_locations.clear()
        self.current_frame_index = 0
