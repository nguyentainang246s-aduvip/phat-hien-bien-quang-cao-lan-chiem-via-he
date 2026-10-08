"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Temporal Reasoning & False Positive Elimination
TASK: 22 - Xây dựng Module tracking/verifier.py (Bộ lọc xác nhận theo thời gian)
==============================================================================
"""

import time


class TrackState:
    """Các trạng thái vòng đời của một vật thể biển hiệu được theo dõi."""
    NORMAL = "NORMAL"          # Biển hợp lệ, không lấn chiếm vỉa hè
    SUSPECTED = "SUSPECTED"    # Nghi vấn vi phạm (< N frames liên tiếp, chưa phạt)
    CONFIRMED = "CONFIRMED"    # ĐÃ XÁC NHẬN VI PHẠM (>= N frames liên tiếp)


class TemporalVerifier:
    """
    Bộ lọc xác nhận vi phạm theo chuỗi thời gian (Temporal Verification).
    Nguyên lý: Chỉ kết luận và phát cảnh báo vi phạm khi một đối tượng (track_id)
    duy trì hành vi lấn chiếm vỉa hè liên tục trong tối thiểu N khung hình.
    Loại bỏ triệt để:
      - Người đi bộ bê biển đi ngang qua vỉa hè.
      - Xe cộ vô tình che khuất chớp nhoáng (Flickering).
      - Cảnh báo trùng lặp (Spam Alert) nhờ cơ chế Cooldown Timer.
    """
    def __init__(
        self,
        confirm_frames: int = 15,
        cooldown_seconds: float = 60.0,
        max_missing_frames: int = 30,
        tolerance_frames: int = 2
    ):
        """
        Khởi tạo TemporalVerifier.
        
        Args:
            confirm_frames: Số frames vi phạm liên tiếp tối thiểu để CHÍNH THỨC XÁC NHẬN (vd: 15 frames ~ 0.5s)
            cooldown_seconds: Thời gian chờ (giây) trước khi cho phép kích hoạt cảnh báo lặp lại cho cùng 1 ID
            max_missing_frames: Số frames vắng mặt trước khi xóa ID khỏi bộ nhớ để chống tràn RAM
            tolerance_frames: Số frames không vi phạm tối đa cho phép dung sai (chống chập chờn/flicker) trước khi reset bộ đếm về 0
        """
        self.confirm_frames = confirm_frames
        self.cooldown_seconds = cooldown_seconds
        self.max_missing_frames = max_missing_frames
        self.tolerance_frames = tolerance_frames
        self.min_avg_confidence = 0.40  # ISSUE 19: Ngưỡng confidence trung bình tối thiểu để CONFIRMED
        
        # ISSUE 07: Bộ lọc kiểm tra vật thể đứng yên (loại bỏ người bê biển đi bộ ngang qua)
        self.require_stationary = True
        self.max_displacement_pixels = 50.0  # Độ dời tâm tối đa cho phép để coi là vật thể cố định
        
        # ISSUE 08: Khử trùng lặp cảnh báo theo vị trí không gian (Spatial Deduplication) khi track_id bị đổi
        self.spatial_cooldown_radius = 50.0  # Bán kính không gian (pixels)
        self.confirmed_locations = []  # Lưu [{cx, cy, time, track_id}, ...]

        # Lưu trữ trạng thái của từng track_id:
        # { track_id: { "count": int, "status": str, "last_seen": int, "last_alert_time": float, 
        #               "non_viol_streak": int, "conf_sum": float, "initial_center": tuple, "current_center": tuple } }
        self.track_records = {}
        self.current_frame_index = 0

    def process_frame(
        self,
        tracked_objects: list,
        checker,
        polygons: list,
        current_timestamp: float = None,
        precomputed_spatial: list = None
    ) -> list:
        """
        Phân tích chuỗi thời gian cho danh sách đối tượng trong khung hình hiện tại.
        
        Args:
            tracked_objects: Danh sách đối tượng từ ObjectTracker (chứa box, conf, track_id)
            checker: Đối tượng ViolationChecker để kiểm tra hình học
            polygons: Danh sách các đa giác vỉa hè (Multi-ROI)
            current_timestamp: Mốc thời gian thực (time.time()), mặc định lấy thời gian hệ thống
            precomputed_spatial: Danh sách kết quả spatial đã tính toán trước (tránh tính 2 lần trong benchmark)
        """
        if current_timestamp is None:
            current_timestamp = time.time()

        self.current_frame_index += 1
        active_ids = set()
        enriched_results = []

        for idx, obj in enumerate(tracked_objects):
            track_id = obj.get("track_id", -1)
            box = obj["box"]
            conf = obj["conf"]

            # 1. Kiểm tra hình học không gian (dùng kết quả tính trước nếu có)
            if precomputed_spatial is not None and idx < len(precomputed_spatial):
                spatial_res = precomputed_spatial[idx]
            else:
                spatial_res = checker.check_multi(box, polygons)
            is_spatial_viol = spatial_res["is_violation"]

            # Tính tọa độ tâm hiện tại của bounding box
            cx = (box[0] + box[2]) / 2.0
            cy = (box[1] + box[3]) / 2.0

            # Nếu chưa có track_id hợp lệ (vật thể mới xuất hiện frame đầu), khởi tạo tạm thời
            if track_id <= 0:
                enriched_results.append({
                    "track_id": track_id,
                    "box": box,
                    "conf": conf,
                    "spatial_res": spatial_res,
                    "temporal_status": TrackState.SUSPECTED if is_spatial_viol else TrackState.NORMAL,
                    "violation_frames": 1 if is_spatial_viol else 0,
                    "is_new_alert": False
                })
                continue

            active_ids.add(track_id)

            # 2. Khởi tạo bản ghi nếu là ID mới
            if track_id not in self.track_records:
                self.track_records[track_id] = {
                    "count": 0,
                    "status": TrackState.NORMAL,
                    "last_seen": self.current_frame_index,
                    "last_alert_time": 0.0,
                    "non_viol_streak": 0,
                    "conf_sum": 0.0,
                    "initial_center": (cx, cy),
                    "current_center": (cx, cy)
                }

            record = self.track_records[track_id]
            record["last_seen"] = self.current_frame_index
            record["current_center"] = (cx, cy)

            # Tính độ dời so với vị trí ban đầu (Displacement)
            init_cx, init_cy = record.get("initial_center", (cx, cy))
            displacement = ((cx - init_cx) ** 2 + (cy - init_cy) ** 2) ** 0.5

            # 3. Cập nhật bộ đếm thời gian (Temporal Counter Logic)
            is_new_alert = False

            if is_spatial_viol:
                record["count"] += 1
                record["non_viol_streak"] = 0
                record["conf_sum"] += conf

                # Đã xuất hiện đủ số frames quy định
                if record["count"] >= self.confirm_frames:
                    avg_conf = record["conf_sum"] / record["count"] if record["count"] > 0 else 0.0
                    
                    # ISSUE 07: Kiểm tra tính đứng yên (vật thể di chuyển > max_displacement là người/xe đi ngang)
                    is_stationary = True
                    if self.require_stationary and displacement > self.max_displacement_pixels:
                        is_stationary = False

                    if not is_stationary:
                        # Đang di chuyển liên tục -> coi là đối tượng di động, giữ SUSPECTED không báo vi phạm
                        record["status"] = TrackState.SUSPECTED
                    elif avg_conf < self.min_avg_confidence:
                        # Confidence trung bình quá thấp -> không tin tưởng, giữ SUSPECTED
                        record["status"] = TrackState.SUSPECTED
                    else:
                        record["status"] = TrackState.CONFIRMED

                    # ISSUE 08: Khử trùng cảnh báo theo ID và theo Vị trí không gian (Spatial Deduplication)
                    if record["status"] == TrackState.CONFIRMED:
                        is_spatially_cooldown = False
                        for c_item in self.confirmed_locations:
                            dist = ((cx - c_item["cx"]) ** 2 + (cy - c_item["cy"]) ** 2) ** 0.5
                            if dist <= self.spatial_cooldown_radius and (current_timestamp - c_item["time"]) < self.cooldown_seconds:
                                is_spatially_cooldown = True
                                break

                        if not is_spatially_cooldown and (current_timestamp - record["last_alert_time"]) >= self.cooldown_seconds:
                            is_new_alert = True
                            record["last_alert_time"] = current_timestamp
                            self.confirmed_locations.append({
                                "cx": cx,
                                "cy": cy,
                                "time": current_timestamp,
                                "track_id": track_id
                            })
                            # Dọn dẹp các mốc cũ
                            self.confirmed_locations = [
                                c for c in self.confirmed_locations
                                if (current_timestamp - c["time"]) <= self.cooldown_seconds * 2
                            ]
                else:
                    record["status"] = TrackState.SUSPECTED
            else:
                # Nếu không vi phạm ở frame này: tăng chuỗi không vi phạm
                record["non_viol_streak"] += 1
                if record["non_viol_streak"] > self.tolerance_frames:
                    # Vượt quá dung sai -> reset hoàn toàn bộ đếm về 0
                    record["count"] = 0
                    record["conf_sum"] = 0.0
                    record["status"] = TrackState.NORMAL
                    record["initial_center"] = (cx, cy)
                else:
                    # Trong ngưỡng dung sai (1-2 frame rung lắc): giảm dần
                    record["count"] = max(0, record["count"] - 1)
                    if record["count"] == 0:
                        record["status"] = TrackState.NORMAL

            enriched_results.append({
                "track_id": track_id,
                "box": box,
                "conf": conf,
                "spatial_res": spatial_res,
                "temporal_status": record["status"],
                "violation_frames": record["count"],
                "is_new_alert": is_new_alert
            })

        # 4. Xử lý các track_id bị che khuất (Missing / Occlusion Decay):
        for tid, r in self.track_records.items():
            if tid not in active_ids:
                missing_streak = self.current_frame_index - r["last_seen"]
                if missing_streak > self.tolerance_frames:
                    r["count"] = max(0, r["count"] - 1)
                    if r["count"] == 0:
                        r["status"] = TrackState.NORMAL

        # 5. Dọn dẹp bộ nhớ (Garbage Collection):
        stale_ids = [
            tid for tid, r in self.track_records.items()
            if (self.current_frame_index - r["last_seen"]) > self.max_missing_frames
        ]
        for tid in stale_ids:
            del self.track_records[tid]

        return enriched_results

    def reset(self):
        """Xóa toàn bộ bản ghi trạng thái (khi tua video hoặc đổi camera)"""
        self.track_records.clear()
        self.confirmed_locations.clear()
        self.current_frame_index = 0
