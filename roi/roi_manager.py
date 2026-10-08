"""
Module quản lý Vùng quan tâm Vỉa hè (Sidewalk ROI)
"""
import os
import json
import cv2
import numpy as np

class ROIManager:
    def __init__(self, config_path: str = "configs/roi_camera1.json"):
        self.config_path = config_path
        self.polygons = []  # Danh sách các đa giác: [ [[x,y],...], [[x,y],...] ]
        self.camera_id = "unknown"
        self.orig_width = None
        self.orig_height = None
        self.current_width = None
        self.current_height = None
        self.base_polygons = []  # Lưu polygon gốc để có thể scale nhiều lần chính xác
        self.load_config()

    @property
    def points(self):
        """Tương thích ngược: trả về đa giác đầu tiên nếu có"""
        return self.polygons[0] if self.polygons else []

    def load_config(self) -> bool:
        if not os.path.exists(self.config_path):
            return False
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.camera_id = data.get("camera_id", "cam_01")
        
        # Đọc resolution gốc từ cấu hình
        res = data.get("resolution", {})
        if isinstance(res, dict):
            self.orig_width = res.get("width")
            self.orig_height = res.get("height")
        elif isinstance(res, (list, tuple)) and len(res) >= 2:
            self.orig_width = res[0]
            self.orig_height = res[1]

        # 1. Hỗ trợ định dạng Multi-ROI mới: "polygons": [ [[...]], [[...]] ] hoặc [{"points": [...]}]
        if "polygons" in data and isinstance(data["polygons"], list):
            self.polygons = []
            for item in data["polygons"]:
                pts = item.get("points", item) if isinstance(item, dict) else item
                if len(pts) >= 3:
                    self.polygons.append([[int(p[0]), int(p[1])] for p in pts])

        # 2. Tương thích ngược với định dạng cũ: "polygon_points": [...]
        elif "polygon_points" in data and len(data["polygon_points"]) >= 3:
            self.polygons = [[[int(p[0]), int(p[1])] for p in data["polygon_points"]]]

        # Sao lưu polygons gốc để tái co giãn khi cần
        import copy
        self.base_polygons = copy.deepcopy(self.polygons)
        self.current_width = self.orig_width
        self.current_height = self.orig_height

        return len(self.polygons) > 0

    def validate_resolution(self, frame_width: int, frame_height: int) -> bool:
        """
        Kiểm tra và tự động co giãn ROI nếu độ phân giải frame thực tế
        khác với độ phân giải gốc lúc vẽ ROI.
        
        PHẢI được gọi ngay khi có frame đầu tiên, TRƯỚC bất kỳ phép tính
        spatial nào (check_multi, is_point_inside...).
        
        Returns:
            True nếu ROI đã sẵn sàng sử dụng (khớp hoặc đã scale thành công).
            False nếu không thể validate (thiếu thông tin resolution trong config).
        """
        if not self.orig_width or not self.orig_height:
            print(f"[ROI WARNING] Config '{self.config_path}' KHONG CO truong 'resolution'. "
                  f"Khong the xac minh polygon co khop frame {frame_width}x{frame_height}. "
                  f"Su dung toa do goc — KET QUA CO THE SAI neu resolution lech!")
            return False

        if frame_width == self.orig_width and frame_height == self.orig_height:
            print(f"[ROI OK] Resolution frame ({frame_width}x{frame_height}) "
                  f"khop chinh xac voi config. Khong can co gian.")
            return True

        # Resolution lech -> auto-scale
        print(f"[ROI RESOLUTION MISMATCH] Frame thuc te: {frame_width}x{frame_height} "
              f"!= Config goc: {self.orig_width}x{self.orig_height}. Dang tu dong co gian...")
        return self.adapt_to_resolution(frame_width, frame_height)

    def adapt_to_resolution(self, target_width: int, target_height: int) -> bool:
        """
        Tự động co giãn (scale) tọa độ các đỉnh ROI khi độ phân giải khung hình
        thực tế khác với độ phân giải lúc vẽ ROI.
        """
        if not self.orig_width or not self.orig_height:
            return False

        if target_width == self.current_width and target_height == self.current_height:
            return True

        scale_x = target_width / float(self.orig_width)
        scale_y = target_height / float(self.orig_height)

        scaled_polys = []
        for poly in self.base_polygons:
            scaled_poly = [
                [int(round(pt[0] * scale_x)), int(round(pt[1] * scale_y))]
                for pt in poly
            ]
            scaled_polys.append(scaled_poly)

        self.polygons = scaled_polys
        self.current_width = target_width
        self.current_height = target_height
        print(f"[ROI AUTO-SCALE] Da co gian ROI tu {self.orig_width}x{self.orig_height} sang {target_width}x{target_height} (Scale: {scale_x:.3f}x, {scale_y:.3f}y)")
        return True

    def is_point_inside(self, point: tuple) -> bool:
        """Kiểm tra điểm (x, y) có nằm trong BẤT KỲ vùng vỉa hè nào không"""
        for pts in self.polygons:
            pts_arr = np.array(pts, dtype=np.int32)
            if cv2.pointPolygonTest(pts_arr, point, measureDist=False) >= 0:
                return True
        return False

    def draw_overlay(self, frame, alpha: float = 0.35):
        """Vẽ lớp phủ bán trong suốt cho TẤT CẢ các vùng vỉa hè (trái, phải,...)"""
        if not self.polygons or frame is None:
            return frame

        # Tự động co giãn nếu frame có độ phân giải khác ROI hiện tại
        if len(frame.shape) >= 2:
            fh, fw = frame.shape[:2]
            if self.orig_width and (fw != self.current_width or fh != self.current_height):
                self.adapt_to_resolution(fw, fh)

        overlay = frame.copy()
        for idx, pts in enumerate(self.polygons):
            pts_arr = np.array(pts, dtype=np.int32).reshape((-1, 1, 2))
            # Đổ màu bán trong suốt
            cv2.fillPoly(overlay, [pts_arr], (0, 200, 255))

        cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)

        # Vẽ viền và nhãn cho từng vỉa hè
        for idx, pts in enumerate(self.polygons):
            pts_arr = np.array(pts, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [pts_arr], isClosed=True, color=(0, 255, 255), thickness=3)
            
            first_pt = tuple(pts[0])
            label = f"[VIA HE #{idx+1}]"
            cv2.putText(frame, label, (first_pt[0] + 5, max(25, first_pt[1] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2, cv2.LINE_AA)
                        
        return frame

