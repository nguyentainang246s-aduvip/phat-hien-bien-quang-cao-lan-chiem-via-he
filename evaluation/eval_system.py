"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: System-level Evaluation Framework (Phục vụ Chương 7 Báo cáo Đồ án)
Mục tiêu: Đánh giá độc lập chất lượng phán quyết vi phạm của TOÀN HỆ THỐNG
          (System Precision / Recall / F1) tách bạch với Model Detection mAP.
==============================================================================
"""

import os
import json
import numpy as np


class SystemEvaluator:
    """
    Bộ đánh giá cấp độ hệ thống (System-level Metrics).
    Phân biệt rõ:
      1. Model-level metrics: mAP50, Precision, Recall của mô hình YOLOv8 detect vật thể.
      2. System-level metrics: Precision, Recall, F1 của toàn bộ pipeline (YOLO + Geometry + Temporal)
         trong việc phán quyết sự kiện lấn chiếm vỉa hè.
    """

    def __init__(self, iou_threshold: float = 0.5):
        self.iou_threshold = iou_threshold

    @staticmethod
    def compute_box_iou(box1, box2):
        """Tính IoU giữa 2 bounding box (x1, y1, x2, y2)"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        inter_area = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = max(0, box1[2] - box1[0]) * max(0, box1[3] - box1[1])
        area2 = max(0, box2[2] - box2[0]) * max(0, box2[3] - box2[1])
        union_area = area1 + area2 - inter_area

        if union_area <= 0:
            return 0.0
        return float(inter_area / union_area)

    def evaluate(self, ground_truths: list, system_predictions: list) -> dict:
        """
        So khớp ground truth và phán quyết của hệ thống trên từng frame / event.
        
        Args:
            ground_truths: Danh sách nhãn thực tế [ {"box": [...], "is_violation": bool}, ... ]
            system_predictions: Danh sách kết quả hệ thống [ {"box": [...], "is_violation": bool}, ... ]
            
        Returns:
            dict chứa TP, FP, FN, Precision, Recall, F1-Score
        """
        tp = 0  # Thực tế vi phạm, hệ thống báo vi phạm
        fp = 0  # Thực tế không vi phạm (hoặc không có biển), hệ thống báo vi phạm
        fn = 0  # Thực tế vi phạm, hệ thống bỏ sót không báo

        matched_preds = set()

        for gt in ground_truths:
            gt_box = gt["box"]
            gt_viol = gt.get("is_violation", True)

            best_iou = 0.0
            best_p_idx = -1

            for p_idx, pred in enumerate(system_predictions):
                if p_idx in matched_preds:
                    continue
                iou = self.compute_box_iou(gt_box, pred["box"])
                if iou > best_iou:
                    best_iou = iou
                    best_p_idx = p_idx

            if best_iou >= self.iou_threshold and best_p_idx >= 0:
                matched_preds.add(best_p_idx)
                pred_viol = system_predictions[best_p_idx].get("is_violation", False)

                if gt_viol and pred_viol:
                    tp += 1
                elif gt_viol and not pred_viol:
                    fn += 1
                elif not gt_viol and pred_viol:
                    fp += 1
            else:
                # Không match được box nào
                if gt_viol:
                    fn += 1

        # Các dự đoán còn lại không match với bất kỳ GT nào
        for p_idx, pred in enumerate(system_predictions):
            if p_idx not in matched_preds:
                if pred.get("is_violation", False):
                    fp += 1

        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        return {
            "TP": tp,
            "FP": fp,
            "FN": fn,
            "system_precision": round(precision, 4),
            "system_recall": round(recall, 4),
            "system_f1": round(f1, 4),
            "total_ground_truth_violations": sum(1 for g in ground_truths if g.get("is_violation", True)),
            "total_system_alerts": sum(1 for p in system_predictions if p.get("is_violation", False))
        }

    def generate_markdown_report(self, results: dict, title: str = "ĐÁNH GIÁ CHẤT LƯỢNG TOÀN HỆ THỐNG (SYSTEM-LEVEL METRICS)") -> str:
        """Tạo bảng báo cáo kết quả đánh giá hệ thống dạng Markdown phục vụ báo cáo ĐATN."""
        md = []
        md.append(f"## {title}\n")
        md.append("> **Phương pháp:** Đánh giá độc lập phán quyết vi phạm của toàn pipeline (AI Detection + Spatial Rule + Temporal Verifier) so với Ground Truth thực tế.\n")
        md.append("| Chỉ số Đánh giá | Giá trị | Ý nghĩa thực nghiệm |")
        md.append("| :--- | :---: | :--- |")
        md.append(f"| **True Positives (TP)** | `{results['TP']}` | Số vụ vi phạm thực tế được hệ thống phát hiện chính xác |")
        md.append(f"| **False Positives (FP)** | `{results['FP']}` | Số vụ báo động giả (biển hợp lệ hoặc vật thể khác bị bắt nhầm) |")
        md.append(f"| **False Negatives (FN)** | `{results['FN']}` | Số vụ vi phạm thực tế mà hệ thống bỏ sót |")
        md.append(f"| **System Precision** | **{results['system_precision']*100:.2f}%** | Tỷ lệ cảnh báo của hệ thống là vi phạm thật |")
        md.append(f"| **System Recall** | **{results['system_recall']*100:.2f}%** | Tỷ lệ vi phạm ngoài thực tế được hệ thống ghi nhận |")
        md.append(f"| **System F1-Score** | **{results['system_f1']*100:.2f}%** | Điểm cân bằng điều hòa giữa Precision và Recall |")
        md.append("")
        return "\n".join(md)
