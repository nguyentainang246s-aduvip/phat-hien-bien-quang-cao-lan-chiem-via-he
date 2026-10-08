"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Spatial Reasoning & Violation Decision Engine
TASK: 18 - Xây dựng Module Quyết định Vi phạm Lai (Hybrid Violation Checker)
==============================================================================
"""

import cv2
import numpy as np
import shapely.geometry as sg


class ViolationChecker:
    """
    Bộ phán quyết vi phạm hành vi lấn chiếm vỉa hè.
    Áp dụng thuật toán lai kép (Dual-Condition Logic):
      1. Tọa độ chân đế tiếp xúc mặt đất (Ground Contact Point) nằm trong vỉa hè.
      2. Tỷ lệ diện tích giao nhau 2D (Overlap Ratio) >= Ngưỡng Threshold (mặc định 30%).
    """
    def __init__(self, threshold: float = 0.30):
        """
        Args:
            threshold (float): Tỷ lệ diện tích lấn chiếm tối thiểu để cảnh báo (0.30 = 30%).
        """
        self.threshold = threshold

    def check(self, box: tuple, polygon_points: list) -> dict:
        """
        Kiểm tra trạng thái vi phạm của một vật thể biển hiệu.
        
        Args:
            box: Tọa độ Bounding Box (x1, y1, x2, y2)
            polygon_points: Danh sách các đỉnh của đa giác vỉa hè [[x, y], ...]
            
        Returns:
            dict: Kết quả phân tích chi tiết:
                  {
                      "is_violation": bool,
                      "overlap_ratio": float (0.0 -> 1.0),
                      "overlap_pct": float (0.0% -> 100.0%),
                      "base_point": (x, y),
                      "is_base_inside": bool,
                      "status_text": str
                  }
        """
        if len(polygon_points) < 3:
            return {
                "is_violation": False,
                "overlap_ratio": 0.0,
                "overlap_pct": 0.0,
                "base_point": (0, 0),
                "is_base_inside": False,
                "status_text": "CHƯA CÓ VÙNG VỈA HÈ"
            }

        x1, y1, x2, y2 = box
        
        # ---------------------------------------------------------------------
        # ĐIỀU KIỆN 1: TỌA ĐỘ CHÂN TIẾP ĐẤT (3-POINT GROUND CONTACT POINT)
        # ---------------------------------------------------------------------
        # Kiểm tra 3 điểm tiếp xúc mặt đất: Chân trái (x1, y2), Giữa, Chân phải (x2, y2)
        pt_left = (int(x1), int(y2))
        pt_center = (int((x1 + x2) / 2), int(y2))
        pt_right = (int(x2), int(y2))
        base_point = pt_center

        pts_array = np.array(polygon_points, dtype=np.int32)
        # cv2.pointPolygonTest: >= 0 là nằm trong hoặc trên mép vỉa hè
        left_inside = cv2.pointPolygonTest(pts_array, pt_left, measureDist=False) >= 0
        center_inside = cv2.pointPolygonTest(pts_array, pt_center, measureDist=False) >= 0
        right_inside = cv2.pointPolygonTest(pts_array, pt_right, measureDist=False) >= 0

        # Thỏa mãn nếu BẤT KỲ điểm nào trong 3 điểm (Chân trái / Giữa / Chân phải) tiếp đất trên vỉa hè
        is_base_inside = left_inside or center_inside or right_inside

        # ---------------------------------------------------------------------
        # ĐIỀU KIỆN 2: TỶ LỆ DIỆN TÍCH GIAO NHAU (OVERLAP RATIO VỚI SHAPELY)
        # ---------------------------------------------------------------------
        box_poly = sg.box(x1, y1, x2, y2)
        sidewalk_poly = sg.Polygon(polygon_points)
        
        # Sửa lỗi đa giác tự cắt nếu có
        if not sidewalk_poly.is_valid:
            sidewalk_poly = sidewalk_poly.buffer(0)

        overlap_ratio = 0.0
        if box_poly.area > 0:
            intersection = sidewalk_poly.intersection(box_poly)
            # ISSUE 07: Mẫu số là diện tích BOUNDING BOX (không phải IoU, không phải ROI area).
            # Lý do khoa học:
            #   - Phản ánh đúng câu hỏi pháp lý: "Bao nhiêu % CỦA BIỂN nằm trên vỉa hè?"
            #   - Nếu dùng IoU: biển nhỏ nằm gọn ROI lớn → IoU rất thấp → bỏ sót vi phạm rõ ràng
            #   - Nếu dùng ROI area: kết quả phụ thuộc kích thước vỉa hè, không phản ánh mức độ lấn chiếm
            overlap_ratio = float(intersection.area / box_poly.area)

        # ---------------------------------------------------------------------
        # RA QUYẾT ĐỊNH (DECISION RULE)
        # ---------------------------------------------------------------------
        # Vi phạm khi CẢ HAI điều kiện đồng thời thỏa mãn:
        #   1. Chân đế (Ground Contact Point) nằm trong vùng vỉa hè
        #   2. Tỷ lệ diện tích bounding box giao vỉa hè >= ngưỡng threshold
        # Lý do: Chỉ dùng overlap sẽ báo sai cho biển treo cao trên tầng 2/3
        #         có bounding box trùm xuống ROI nhưng không thực sự chạm đất.
        is_violation = (is_base_inside and overlap_ratio >= self.threshold)

        
        overlap_pct = round(overlap_ratio * 100, 1)
        if is_violation:
            status_text = f"VI PHAM LAN CHIEM ({overlap_pct}%)"
        elif is_base_inside and overlap_ratio < self.threshold:
            status_text = f"CHAM MEP VIA HE ({overlap_pct}%)"
        else:
            status_text = f"HOP LE (NGOAI VIA HE)"

        return {
            "is_violation": is_violation,
            "overlap_ratio": round(overlap_ratio, 3),
            "overlap_pct": overlap_pct,
            "base_point": base_point,
            "base_points": {
                "left": pt_left,
                "center": pt_center,
                "right": pt_right
            },
            "points_inside": {
                "left": left_inside,
                "center": center_inside,
                "right": right_inside
            },
            "is_base_inside": is_base_inside,
            "status_text": status_text
        }

    def check_multi(self, box: tuple, list_of_polygons: list) -> dict:
        """
        Kiểm tra vi phạm trên danh sách nhiều đa giác vỉa hè (Multi-ROI).
        Chỉ cần lấn chiếm BẤT KỲ vỉa hè nào (vỉa hè trái hoặc vỉa hè phải) -> KẾT LUẬN VI PHẠM.
        """
        if not list_of_polygons:
            return self.check(box, [])

        best_result = None
        max_overlap = -1.0

        for idx, pts in enumerate(list_of_polygons):
            res = self.check(box, pts)
            if res["is_violation"]:
                res["sidewalk_index"] = idx + 1
                return res  # Lấn chiếm ít nhất 1 vỉa hè là đủ kết luận vi phạm
            if res["overlap_ratio"] > max_overlap:
                max_overlap = res["overlap_ratio"]
                best_result = res
                best_result["sidewalk_index"] = idx + 1

        return best_result or self.check(box, [])

