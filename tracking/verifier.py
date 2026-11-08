"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Temporal Reasoning & False Positive Elimination
TASK: 22 - Xây dựng Module tracking/verifier.py (Bộ lọc xác nhận theo thời gian)
Tích hợp:
  (2) Motion Filter (Bộ lọc chuyển động và vận tốc dịch chuyển)
  - Phân loại rõ ràng biển tĩnh với xe cộ/người đi bộ (TrackState.MOVING).
  - Perspective-Adaptive Scale theo đường chéo Bounding Box.
==============================================================================
"""

import time
from collections import deque
from .motion_filter import MotionFilter


class TrackState:
    """Các trạng thái vòng đời của một vật thể biển hiệu được theo dõi."""
    NORMAL = "NORMAL"          # Biển hợp lệ, không lấn chiếm vỉa hè
    SUSPECTED = "SUSPECTED"    # Nghi vấn vi phạm (< N giây liên tiếp, chưa phạt)
    CONFIRMED = "CONFIRMED"    # ĐÃ XÁC NHẬN VI PHẠM (>= N giây liên tiếp)
    MOVING = "MOVING"          # Đối tượng đang di chuyển (xe cộ, người bê biển - loại trừ)


class TemporalVerifier:
    """
    Bộ lọc xác nhận vi phạm theo chuỗi thời gian (Temporal Verification).

    Nguyên lý: Chỉ kết luận và phát cảnh báo vi phạm khi một đối tượng (track_id)
    duy trì hành vi lấn chiếm vỉa hè liên tục trong tối thiểu N GIÂY THỰC và ở trạng thái TĨNH.

    Cơ chế sàng lọc:
      - Loại bỏ phương tiện giao thông gắn quảng cáo và người bưng bê biển (Motion Filter).
      - Xe cộ vô tình che khuất chớp nhoáng (Flickering) với tolerance_frames.
      - Cảnh báo trùng lặp (Spam Alert) nhờ cơ chế Cooldown Timer & Spatial Radius.
    """

    def __init__(
        self,
        confirm_frames: int = 20,
        confirm_seconds: float = 3.0,
        cooldown_seconds: float = 60.0,
        max_missing_frames: int = 45,
        tolerance_frames: int = 4,
        source_fps: float = None,
        min_avg_confidence: float = 0.40,
        require_stationary: bool = True,
        max_displacement_pixels: float = 40.0,
        max_velocity_pixels_per_sec: float = 35.0,
        stationary_window_seconds: float = 1.0,
        spatial_cooldown_radius: float = 50.0,
        adaptive_perspective_scale: bool = True,
        min_stationary_seconds: float = None,
    ):
        """
        Args:
            confirm_frames:            Số frames liên tiếp vi phạm tối thiểu (fallback).
            confirm_seconds:           Thời gian vi phạm liên tiếp tối thiểu (giây).
            cooldown_seconds:          Thời gian chờ (giây) chống gửi cảnh báo trùng lặp.
            max_missing_frames:        Xóa track khỏi RAM nếu mất dấu quá số frame này.
            tolerance_frames:          Dung sai frame rung lắc/flicker trước khi reset bộ đếm.
            source_fps:                FPS của nguồn video (dùng để quy đổi giây <-> frame).
            min_avg_confidence:        Ngưỡng confidence TB tối thiểu để CONFIRMED.
            require_stationary:        Bật/tắt bộ lọc yêu cầu vật thể đứng yên.
            max_displacement_pixels:   Độ dời tối đa (trần) trong cửa sổ để coi là đứng yên.
            max_velocity_pixels_per_sec: Vận tốc di chuyển tối đa (px/s) để coi là đứng yên.
            stationary_window_seconds: Độ rộng cửa sổ trượt kiểm tra đứng yên (mặc định 1.0s).
            spatial_cooldown_radius:   Bán kính không gian (pixels) khử trùng lặp khi nhảy ID.
            adaptive_perspective_scale: Tự động co ngưỡng dịch chuyển theo kích thước BBox ở xa.
            min_stationary_seconds:    Thời gian đứng yên liên tục tối thiểu (giây) để CONFIRMED.
        """
        self.confirm_frames = confirm_frames
        self.confirm_seconds = confirm_seconds
        self.cooldown_seconds = cooldown_seconds
        self.max_missing_frames = max_missing_frames
        self.tolerance_frames = tolerance_frames
        self.source_fps = source_fps
        self.min_avg_confidence = min_avg_confidence

        # --- Motion Filter config ---
        self.require_stationary = require_stationary
        self.max_displacement_pixels = max_displacement_pixels
        self.max_velocity_pixels_per_sec = max_velocity_pixels_per_sec
        self.stationary_window_seconds = stationary_window_seconds
        self.adaptive_perspective_scale = adaptive_perspective_scale
        self.min_stationary_seconds = min_stationary_seconds if min_stationary_seconds is not None else min(2.0, self.confirm_seconds)

        # Khởi tạo bộ lọc chuyển động độc lập (MotionFilter)
        self.motion_filter = MotionFilter(
            max_displacement_pixels=self.max_displacement_pixels,
            max_velocity_pixels_per_sec=self.max_velocity_pixels_per_sec,
            window_seconds=self.stationary_window_seconds,
            min_stationary_seconds=self.min_stationary_seconds,
            adaptive_perspective_scale=self.adaptive_perspective_scale,
        )

        # Spatial deduplication khi track_id bị đổi
        self.spatial_cooldown_radius = spatial_cooldown_radius
        self.confirmed_locations: list = []     # [{cx, cy, time, track_id}, ...]

        self.track_records: dict = {}
        self.current_frame_index = 0

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _elapsed_viol_seconds(self, record: dict, now: float) -> float:
        """Trả về số giây vi phạm liên tiếp thực tế dựa trên mốc bắt đầu vi phạm."""
        if not record.get("viol_confs") or record.get("viol_start_time") is None:
            return 0.0
        return max(0.0, now - record["viol_start_time"])

    def _is_stationary(self, record: dict, now: float) -> bool:
        """Kiểm tra xem đối tượng có đang đứng yên không (tương thích ngược)."""
        if not self.require_stationary:
            return True
        track_id = record.get("track_id")
        if track_id is not None:
            res = self.motion_filter.estimate_motion(track_id, now)
            return not res["is_moving"]
        return True

    def _confirm_threshold_reached(self, record: dict, now: float) -> bool:
        """
        Kiểm tra đã đạt ngưỡng xác nhận chưa.
        Ưu tiên: giây thực nếu có thể tính được (viol_start_time tồn tại),
        fallback về số frame.
        """
        if record.get("viol_start_time") is not None and record.get("viol_confs"):
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
            tracked_objects:     Danh sách đối tượng từ ObjectTracker (box, conf, track_id)
            checker:             ViolationChecker để kiểm tra hình học không gian
            polygons:            Danh sách đa giác vỉa hè (Multi-ROI)
            current_timestamp:   Mốc thời gian thực (time.time()); mặc định lấy từ hệ thống
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

            # Tính tọa độ tâm và đường chéo hộp giới hạn
            cx = (box[0] + box[2]) / 2.0
            cy = (box[1] + box[3]) / 2.0

            # Cập nhật và đánh giá chuyển động qua MotionFilter
            if track_id > 0 and self.require_stationary:
                motion_res = self.motion_filter.update(track_id, box, current_timestamp)
                is_moving = motion_res["is_moving"]
                is_stationary_long_enough = motion_res["is_stationary"]
                velocity = motion_res["velocity_px_s"]
                stationary_dur = motion_res["stationary_duration"]
            else:
                is_moving = False
                is_stationary_long_enough = True
                velocity = 0.0
                stationary_dur = 0.0

            # Vật thể chưa có track_id hợp lệ (frame đầu tiên xuất hiện)
            if track_id <= 0:
                initial_status = TrackState.SUSPECTED if is_spatial_viol else TrackState.NORMAL
                enriched_results.append({
                    "track_id": track_id,
                    "box": box,
                    "conf": conf,
                    "spatial_res": spatial_res,
                    "temporal_status": initial_status,
                    "suspect_reason": "",
                    "violation_frames": 1 if is_spatial_viol else 0,
                    "violation_seconds": 0.0,
                    "velocity_px_s": 0.0,
                    "is_new_alert": False,
                })
                continue

            active_ids.add(track_id)

            # 2. Khởi tạo bản ghi nếu là ID mới
            if track_id not in self.track_records:
                self.track_records[track_id] = {
                    "track_id": track_id,
                    "count": 0,
                    "viol_start_time": None,
                    "last_viol_timestamp": None,
                    "status": TrackState.NORMAL,
                    "last_seen": self.current_frame_index,
                    "last_alert_time": None,
                    "alerted": False,
                    "non_viol_streak": 0,
                    "viol_confs": deque(maxlen=200),
                }

            record = self.track_records[track_id]
            record["last_seen"] = self.current_frame_index

            # 3. Cập nhật bộ đếm thời gian & phân tích trạng thái
            is_new_alert = False
            suspect_reason = ""

            if is_spatial_viol:
                if is_moving:
                    # KỸ THUẬT 2: ĐỐI TƯỢNG ĐANG DI CHUYỂN TRÊN VỈA HÈ (Xe buýt, người bê biển)
                    # Giữ ở diện nghi vấn SUSPECTED với lý do DI CHUYEN, loại trừ hoàn toàn khỏi CONFIRMED
                    record["status"] = TrackState.SUSPECTED
                    suspect_reason = f"DI CHUYEN ({velocity:.0f}px/s)"
                    record["viol_confs"].clear()
                    record["count"] = 0
                    record["viol_start_time"] = None
                    record["last_viol_timestamp"] = current_timestamp

                else:
                    # Đối tượng đang ở vị trí vi phạm và TĨNH (không di chuyển nhanh)
                    frame_interval = (1.0 / self.source_fps) if self.source_fps else 0.04
                    max_allowed_gap = max(0.6, (self.tolerance_frames + 2) * frame_interval)
                    if record["last_viol_timestamp"] is not None:
                        gap = current_timestamp - record["last_viol_timestamp"]
                        if gap > max_allowed_gap:
                            record["viol_confs"].clear()
                            record["viol_start_time"] = current_timestamp
                            record["count"] = 0
                            record["status"] = TrackState.SUSPECTED

                    if record["viol_start_time"] is None:
                        record["viol_start_time"] = current_timestamp

                    record["last_viol_timestamp"] = current_timestamp
                    record["viol_confs"].append((current_timestamp, conf))
                    record["count"] = len(record["viol_confs"])
                    record["non_viol_streak"] = 0

                    # Tính confidence trung bình trên chuỗi quan sát
                    confs = [c for t, c in record["viol_confs"]]
                    avg_conf = (sum(confs) / len(confs)) if confs else 0.0

                    # Kiểm tra đã đạt ngưỡng thời gian/frame chưa
                    if self._confirm_threshold_reached(record, current_timestamp):
                        if not is_stationary_long_enough and self.require_stationary:
                            # Vừa mới dừng lại, chưa đủ thời gian đứng yên tối thiểu
                            record["status"] = TrackState.SUSPECTED
                            suspect_reason = f"CHO TINH ({stationary_dur:.1f}s<{self.min_stationary_seconds:.1f}s)"
                        elif avg_conf < self.min_avg_confidence:
                            record["status"] = TrackState.SUSPECTED
                            suspect_reason = f"CONF {int(avg_conf * 100)}%<{int(self.min_avg_confidence * 100)}%"
                        else:
                            record["status"] = TrackState.CONFIRMED
                            suspect_reason = ""

                        # Khử trùng lặp cảnh báo (Deduplication)
                        if record["status"] == TrackState.CONFIRMED:
                            if not record.get("alerted", False):
                                is_spatially_cooldown = any(
                                    ((cx - c["cx"]) ** 2 + (cy - c["cy"]) ** 2) ** 0.5 <= self.spatial_cooldown_radius
                                    and (current_timestamp - c["time"]) < self.cooldown_seconds
                                    for c in self.confirmed_locations
                                )
                                if not is_spatially_cooldown:
                                    is_new_alert = True
                                    record["alerted"] = True
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
                        if record["status"] != TrackState.CONFIRMED:
                            record["status"] = TrackState.SUSPECTED
                        suspect_reason = ""

            else:
                # Không vi phạm ở khung hình này (hợp lệ hoặc nằm ngoài vỉa hè)
                record["non_viol_streak"] += 1
                tolerance_time = (self.tolerance_frames / self.source_fps) if (self.source_fps and self.source_fps > 0) else None
                if tolerance_time is not None and record["last_viol_timestamp"] is not None:
                    streak_exceeded = (current_timestamp - record["last_viol_timestamp"]) > tolerance_time
                else:
                    streak_exceeded = record["non_viol_streak"] > self.tolerance_frames

                if streak_exceeded:
                    record["count"] = 0
                    record["viol_confs"].clear()
                    record["viol_start_time"] = None
                    record["last_viol_timestamp"] = None
                    record["status"] = TrackState.NORMAL
                    record["alerted"] = False
                else:
                    if record["viol_confs"]:
                        record["viol_confs"].popleft()
                    record["count"] = len(record["viol_confs"])
                    if record["count"] == 0:
                        record["viol_start_time"] = None
                        record["last_viol_timestamp"] = None
                        record["status"] = TrackState.NORMAL
                        record["alerted"] = False
                    else:
                        record["viol_start_time"] = record["viol_confs"][0][0]

            enriched_results.append({
                "track_id": track_id,
                "box": box,
                "conf": conf,
                "spatial_res": spatial_res,
                "temporal_status": record["status"],
                "suspect_reason": suspect_reason,
                "is_moving": is_moving,
                "violation_frames": record["count"],
                "violation_seconds": round(self._elapsed_viol_seconds(record, current_timestamp), 2),
                "velocity_px_s": round(velocity, 1),
                "is_new_alert": is_new_alert,
            })

        # 4. Decay các track bị che khuất (Missing Occlusion Decay)
        for tid, r in self.track_records.items():
            if tid not in active_ids:
                missing_streak = self.current_frame_index - r["last_seen"]
                tolerance_time = (self.tolerance_frames / self.source_fps) if (self.source_fps and self.source_fps > 0) else None
                if tolerance_time is not None and r["last_viol_timestamp"] is not None:
                    missing_exceeded = (current_timestamp - r["last_viol_timestamp"]) > tolerance_time
                else:
                    missing_exceeded = missing_streak > self.tolerance_frames

                if missing_exceeded:
                    if missing_streak > (self.max_missing_frames // 2):
                        r["status"] = TrackState.NORMAL
                        r["alerted"] = False
                        r["viol_confs"].clear()
                        r["count"] = 0
                        r["viol_start_time"] = None
                        r["last_viol_timestamp"] = None
                    else:
                        if r["viol_confs"]:
                            r["viol_confs"].popleft()
                        r["count"] = len(r["viol_confs"])
                        if r["count"] == 0:
                            r["viol_start_time"] = None
                            r["last_viol_timestamp"] = None
                            r["status"] = TrackState.NORMAL
                        else:
                            r["viol_start_time"] = r["viol_confs"][0][0]
                            if r["status"] == TrackState.CONFIRMED and not self._confirm_threshold_reached(r, current_timestamp):
                                r["status"] = TrackState.SUSPECTED

        # 5. Garbage Collection – xóa track cũ khỏi RAM
        stale_ids = [
            tid for tid, r in self.track_records.items()
            if (self.current_frame_index - r["last_seen"]) > self.max_missing_frames
        ]
        for tid in stale_ids:
            del self.track_records[tid]
            self.motion_filter.reset(tid)

        return enriched_results

    def reset(self):
        """Xóa toàn bộ bản ghi trạng thái (khi tua video hoặc đổi camera)."""
        self.track_records.clear()
        self.confirmed_locations.clear()
        self.current_frame_index = 0
        if hasattr(self, 'motion_filter'):
            self.motion_filter.reset()
