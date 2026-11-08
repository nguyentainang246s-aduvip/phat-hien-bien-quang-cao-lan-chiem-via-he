"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Object Tracking & Multi-Object Association
TASK: 21 - Module tracking/tracker.py tích hợp ByteTrack & Bộ giải pháp chống chớp tắt:
  (1) Hysteresis Thresholding (Ngưỡng trễ kép kích hoạt & duy trì bám vết).
  (2) Track Coasting / Visual Persistence (Duy trì hiển thị box khi bị che khuất ngắn, chống chớp tắt).
  (3) Spatial Static Stitching (Khóa vị trí biển tĩnh, hàn gắn lại ID cũ khi xuất hiện lại).
  (4) Spatial Adaptive Thresholding (Ngưỡng tự thích ứng không gian theo ROI).
==============================================================================
"""

import os
import cv2
import math
import numpy as np
from ultralytics import YOLO


class ObjectTracker:
    """
    Bộ bám vết vật thể (Multi-Object Tracker) tích hợp ByteTrack chuyên dụng cho CCTV vỉa hè:
      1. Hysteresis Thresholding: Ngưỡng kích hoạt cao (activation_conf), ngưỡng duy trì thấp (retention_conf).
      2. Visual Coasting: Duy trì bounding box trên màn hình trong K frames khi bị người/xe che khuất chớp nhoáng.
      3. Spatial Static Stitching: Hàn gắn lại ID cũ cho biển hiệu tĩnh khi xuất hiện lại sau che khuất dài.
      4. Spatial Adaptive Thresholding: Nhạy hơn trong vỉa hè (tối đa Recall), khắt khe ngoài vỉa hè (tối đa Precision).
    """
    def __init__(
        self,
        model_path: str = "models/best.pt",
        conf_threshold: float = 0.20,
        tracker_type: str = None,
        imgsz: int = 640,
        allowed_classes: list = None,
        iou: float = 0.50,
        device: str = None,
        track_low_thresh: float = 0.08,
        activation_conf: float = None,
        retention_conf: float = None,
        spatial_adaptive: bool = True,
        conf_inside_roi: float = 0.20,
        conf_outside_roi: float = 0.45,
        roi_polygons: list = None,
        enable_coasting: bool = True,
        max_coast_frames: int = 16,
        enable_stitching: bool = True,
        stitch_memory_frames: int = 180,
    ):
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.track_low_thresh = track_low_thresh
        self.activation_conf = activation_conf if activation_conf is not None else conf_threshold
        self.retention_conf = retention_conf if retention_conf is not None else track_low_thresh
        self.spatial_adaptive = spatial_adaptive
        self.conf_inside_roi = conf_inside_roi
        self.conf_outside_roi = conf_outside_roi
        self.roi_polygons = roi_polygons or []

        # Cơ chế chống chớp tắt & hàn gắn ID
        self.enable_coasting = enable_coasting
        self.max_coast_frames = max_coast_frames
        self.enable_stitching = enable_stitching
        self.stitch_memory_frames = stitch_memory_frames

        # Bộ nhớ theo dõi biển hiệu tĩnh:
        # canonical_id -> { "box": tuple, "conf": float, "class_id": int, "class_name": str, "hits": int, "miss": int, "in_roi": bool, "last_seen": int }
        self.track_memory = {}
        # Ánh xạ ID tạm thời từ ByteTrack sang ID chuẩn hóa: byte_id -> canonical_id
        self.id_mapping = {}
        self.frame_idx = 0

        if tracker_type is None:
            custom_cfg = "configs/bytetrack_custom.yaml"
            self.tracker_type = custom_cfg if os.path.exists(custom_cfg) else "bytetrack.yaml"
        else:
            self.tracker_type = tracker_type

        self.imgsz = imgsz
        self.allowed_classes = allowed_classes
        self.iou = iou
        self.device = device
        
        if not os.path.exists(model_path) and not model_path.endswith("yolov8n.pt"):
            raise FileNotFoundError(f"Không tìm thấy file trọng số mô hình: {model_path}")
            
        print(f"[OBJECT TRACKER] Nạp mô hình: {model_path} | Thuật toán: {self.tracker_type}")
        print(f"  • Hysteresis: Activation={self.activation_conf:.2f} | Retention={self.retention_conf:.2f}")
        print(f"  • Anti-Flicker: Coasting={self.enable_coasting} ({self.max_coast_frames}f) | Stitching={self.enable_stitching} ({self.stitch_memory_frames}f)")
        if self.spatial_adaptive:
            print(f"  • Spatial Adaptive: Inside={self.conf_inside_roi:.2f} | Outside={self.conf_outside_roi:.2f}")
        self.model = YOLO(model_path)
        self.class_names = self.model.names

    def set_roi_polygons(self, polygons: list):
        """Cập nhật danh sách đa giác ROI vỉa hè phục vụ Spatial Adaptive Thresholding."""
        self.roi_polygons = polygons or []

    @staticmethod
    def is_box_in_roi(box: tuple, polygons: list, margin: float = 15.0) -> bool:
        """Kiểm tra nhanh xem tọa độ chân đế (đáy bbox) có tiếp đất trên vỉa hè không (<0.02ms)."""
        if not polygons:
            return False
        x1, y1, x2, y2 = box
        pt_center = (int((x1 + x2) / 2), int(y2))
        pt_left = (int(x1), int(y2))
        pt_right = (int(x2), int(y2))
        for poly in polygons:
            if len(poly) < 3:
                continue
            pts_arr = np.array(poly, dtype=np.int32)
            if (cv2.pointPolygonTest(pts_arr, pt_center, measureDist=True) >= -margin or
                cv2.pointPolygonTest(pts_arr, pt_left, measureDist=True) >= -margin or
                cv2.pointPolygonTest(pts_arr, pt_right, measureDist=True) >= -margin):
                return True
        return False

    @staticmethod
    def calc_iou(b1: tuple, b2: tuple) -> float:
        """Tính chỉ số Intersection over Union (IoU) giữa 2 bounding box."""
        x1 = max(b1[0], b2[0])
        y1 = max(b1[1], b2[1])
        x2 = min(b1[2], b2[2])
        y2 = min(b1[3], b2[3])
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        a1 = (b1[2] - b1[0]) * (b1[3] - b1[1])
        a2 = (b2[2] - b2[0]) * (b2[3] - b2[1])
        union = a1 + a2 - inter
        return (inter / union) if union > 0 else 0.0

    @staticmethod
    def calc_ios(b1: tuple, b2: tuple) -> float:
        """Tính tỷ lệ phần trăm diện tích hộp nhỏ hơn bị bao phủ bởi hộp lớn hơn (Intersection over Smaller)."""
        x1 = max(b1[0], b2[0])
        y1 = max(b1[1], b2[1])
        x2 = min(b1[2], b2[2])
        y2 = min(b1[3], b2[3])
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        a1 = (b1[2] - b1[0]) * (b1[3] - b1[1])
        a2 = (b2[2] - b2[0]) * (b2[3] - b2[1])
        min_area = min(a1, a2)
        return (inter / min_area) if min_area > 0 else 0.0

    def track(self, frame, conf: float = None, imgsz: int = None, roi_polygons: list = None) -> list:
        """
        Thực hiện phát hiện và bám vết đối tượng kết hợp đầy đủ:
          - Hysteresis Thresholding
          - Spatial Adaptive Thresholding
          - Spatial Static Stitching (Hàn gắn ID)
          - Visual Coasting (Duy trì box chống chớp tắt)
        """
        self.frame_idx += 1
        target_conf = conf if conf is not None else self.activation_conf
        target_imgsz = imgsz if imgsz is not None else self.imgsz
        effective_polygons = roi_polygons if roi_polygons is not None else self.roi_polygons

        # Hạ infer_conf xuống mức thấp nhất để ByteTrack nhận đủ box vòng 2
        lowest_thresh = min(target_conf, self.retention_conf)
        if self.spatial_adaptive and effective_polygons:
            lowest_thresh = min(lowest_thresh, self.conf_inside_roi)

        track_kwargs = {
            "source": frame,
            "persist": True,
            "tracker": self.tracker_type,
            "conf": lowest_thresh,
            "imgsz": target_imgsz,
            "iou": self.iou,
            "verbose": False
        }
        if self.device:
            track_kwargs["device"] = self.device
        if self.allowed_classes is not None and all(isinstance(c, int) for c in self.allowed_classes):
            track_kwargs["classes"] = self.allowed_classes

        results = self.model.track(**track_kwargs)

        current_active_ids = set()
        current_frame_detections = []

        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            for box in boxes:
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = self.class_names.get(cls_id, f"class_{cls_id}")
                if self.allowed_classes is not None:
                    if cls_id not in self.allowed_classes and cls_name not in self.allowed_classes:
                        continue

                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                conf_val = float(box.conf[0].cpu().numpy())
                box_tuple = (int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3]))

                raw_tid = int(box.id[0].cpu().numpy()) if box.id is not None else -1

                # 1. Kỹ thuật Spatial Adaptive Thresholding
                in_roi = False
                if self.spatial_adaptive and effective_polygons:
                    in_roi = self.is_box_in_roi(box_tuple, effective_polygons)
                    required_activation = self.conf_inside_roi if in_roi else self.conf_outside_roi
                else:
                    required_activation = target_conf

                # 2. Kỹ thuật Hysteresis Thresholding
                # Kiểm tra nhanh xem box có khớp không gian với biển hiệu tĩnh trong bộ nhớ không
                is_known_stationary = any(
                    (self.calc_iou(box_tuple, rec["box"]) >= 0.25 or 
                     math.hypot((box_tuple[0] + box_tuple[2]) / 2 - (rec["box"][0] + rec["box"][2]) / 2, 
                                (box_tuple[1] + box_tuple[3]) / 2 - (rec["box"][1] + rec["box"][3]) / 2) <= 35.0)
                    for rec in self.track_memory.values() if rec["hits"] >= 2 and rec["miss"] <= self.stitch_memory_frames
                )

                if raw_tid > 0 or is_known_stationary:
                    if (self.spatial_adaptive and effective_polygons and not in_roi) and conf_val < required_activation:
                        continue
                    if conf_val < self.retention_conf:
                        continue
                else:
                    if conf_val < required_activation:
                        continue

                current_frame_detections.append({
                    "raw_id": raw_tid,
                    "box": box_tuple,
                    "conf": conf_val,
                    "class_id": cls_id,
                    "class_name": cls_name,
                    "in_roi": in_roi
                })

        # Lọc bỏ hộp lồng nhau / phát hiện trùng trên cùng 1 biển hiệu (Containment De-duplication)
        current_frame_detections.sort(key=lambda d: d["conf"], reverse=True)
        unique_detections = []
        for det in current_frame_detections:
            b1 = det["box"]
            is_dup = False
            for kept in unique_detections:
                b2 = kept["box"]
                if self.calc_iou(b1, b2) >= 0.50 or self.calc_ios(b1, b2) >= 0.75:
                    is_dup = True
                    break
            if not is_dup:
                unique_detections.append(det)
        current_frame_detections = unique_detections

        # 3. Kỹ thuật Spatial Static Stitching (Hàn gắn lại ID cũ khi vật thể tĩnh tái xuất hiện)
        final_tracked = []
        claimed_ids_this_frame = set()

        for det in current_frame_detections:
            raw_tid = det["raw_id"]
            box_tuple = det["box"]

            canonical_id = -1
            if raw_tid > 0:
                mapped = self.id_mapping.get(raw_tid, raw_tid)
                if mapped not in claimed_ids_this_frame:
                    canonical_id = mapped
                else:
                    canonical_id = raw_tid if raw_tid not in claimed_ids_this_frame else -1

            if self.enable_stitching and (canonical_id <= 0 or canonical_id not in self.track_memory or self.track_memory[canonical_id]["miss"] > 0):
                best_old_id = None
                best_iou = 0.28
                for old_id, rec in self.track_memory.items():
                    if old_id not in claimed_ids_this_frame and rec["miss"] > 0 and rec["miss"] <= self.stitch_memory_frames:
                        iou_val = self.calc_iou(box_tuple, rec["box"])
                        c1 = ((box_tuple[0] + box_tuple[2]) / 2, (box_tuple[1] + box_tuple[3]) / 2)
                        c2 = ((rec["box"][0] + rec["box"][2]) / 2, (rec["box"][1] + rec["box"][3]) / 2)
                        dist = math.hypot(c1[0] - c2[0], c1[1] - c2[1])
                        if iou_val > best_iou or (dist < 35.0 and iou_val > 0.15):
                            best_old_id = old_id
                            best_iou = max(best_iou, iou_val)

                if best_old_id is not None:
                    canonical_id = best_old_id
                    if raw_tid > 0:
                        self.id_mapping[raw_tid] = canonical_id

            if canonical_id > 0:
                claimed_ids_this_frame.add(canonical_id)
                current_active_ids.add(canonical_id)
                if canonical_id not in self.track_memory:
                    self.track_memory[canonical_id] = {
                        "box": box_tuple,
                        "conf": det["conf"],
                        "class_id": det["class_id"],
                        "class_name": det["class_name"],
                        "hits": 1,
                        "miss": 0,
                        "in_roi": det["in_roi"],
                        "last_seen": self.frame_idx
                    }
                else:
                    rec = self.track_memory[canonical_id]
                    rec["box"] = box_tuple
                    rec["conf"] = det["conf"]
                    rec["hits"] += 1
                    rec["miss"] = 0
                    rec["in_roi"] = det["in_roi"]
                    rec["last_seen"] = self.frame_idx

            final_tracked.append({
                "track_id": canonical_id,
                "box": box_tuple,
                "conf": round(det["conf"], 4),
                "class_id": det["class_id"],
                "class_name": det["class_name"],
                "in_roi": det["in_roi"],
                "is_coasted": False
            })

        # 4. Kỹ thuật Visual Coasting (Duy trì hiển thị box khi bị che khuất ngắn, chống chớp tắt)
        if self.enable_coasting:
            for old_id, rec in self.track_memory.items():
                if old_id not in current_active_ids and old_id > 0:
                    rec["miss"] += 1
                    # Chỉ coast các biển hiệu đã xuất hiện ổn định (hits >= 2) và mất dấu <= max_coast_frames
                    if rec["hits"] >= 2 and rec["miss"] <= self.max_coast_frames:
                        # Tránh vẽ box coast đè lên một đối tượng active đang hiện diện tại vị trí đó
                        is_occupied = any(
                            self.calc_iou(rec["box"], d["box"]) >= 0.40 or self.calc_ios(rec["box"], d["box"]) >= 0.65
                            for d in final_tracked
                        )
                        if not is_occupied:
                            final_tracked.append({
                                "track_id": old_id,
                                "box": rec["box"],
                                "conf": round(rec["conf"] * 0.98, 4),
                                "class_id": rec["class_id"],
                                "class_name": rec["class_name"],
                                "in_roi": rec["in_roi"],
                                "is_coasted": True
                            })

        return final_tracked

    def reset(self):
        """Reset toàn bộ bộ nhớ trạng thái tracker."""
        self.track_memory.clear()
        self.id_mapping.clear()
        self.frame_idx = 0
        try:
            from ultralytics.trackers.basetrack import BaseTrack
            BaseTrack._count = 0
        except Exception:
            pass
        if hasattr(self.model, 'predictor') and self.model.predictor is not None:
            pred = self.model.predictor
            if hasattr(pred, 'trackers') and pred.trackers is not None:
                for trk in pred.trackers:
                    if hasattr(trk, 'reset'):
                        try:
                            trk.reset()
                        except Exception:
                            pass
            else:
                if hasattr(pred, 'trackers'):
                    try:
                        del pred.trackers
                    except Exception:
                        pass
