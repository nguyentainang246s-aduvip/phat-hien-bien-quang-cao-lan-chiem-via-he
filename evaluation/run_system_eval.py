"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: System-level Evaluation Runner
Mục tiêu: Chạy toàn bộ pipeline (Detect → Spatial Check) trên ảnh có Ground Truth,
          so khớp kết quả, tính System Precision/Recall/F1 (ISSUE 03 fix).
==============================================================================
"""

import os
import sys
import json
import cv2

sys.path.insert(0, os.path.abspath("."))

from detection.detector import YOLODetector
from violation.checker import ViolationChecker
from roi.roi_manager import ROIManager
from evaluation.eval_system import SystemEvaluator


def run_system_evaluation(
    gt_path: str = "evaluation/ground_truth.json",
    model_path: str = "models/best.pt",
    default_config: str = "configs/roi_moi.json",
    overlap_threshold: float = 0.30,
    output_report: str = "reports/system_eval_report.md"
):
    """
    Chạy pipeline phát hiện + phán quyết vi phạm trên bộ ảnh Ground Truth,
    sau đó tính System-level Precision / Recall / F1.
    """
    # 1. Đọc Ground Truth
    if not os.path.exists(gt_path):
        print(f"[LỖI] Không tìm thấy file ground truth: {gt_path}")
        return None

    with open(gt_path, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    # 2. Khởi tạo các module
    detector = YOLODetector(model_path=model_path, conf_threshold=0.20)
    checker = ViolationChecker(threshold=overlap_threshold)
    evaluator = SystemEvaluator(iou_threshold=0.5)

    all_gt = []
    all_pred = []

    print("=" * 70)
    print("🔬 ĐÁNH GIÁ CHẤT LƯỢNG TOÀN HỆ THỐNG (SYSTEM-LEVEL EVALUATION)")
    print("=" * 70)

    for entry in gt_data:
        image_path = entry["image_path"]
        config_path = entry.get("config_path", default_config)
        annotations = entry["annotations"]

        if not os.path.exists(image_path):
            print(f"[CẢNH BÁO] Bỏ qua ảnh không tồn tại: {image_path}")
            continue

        print(f"\n[*] Đang xử lý: {image_path}")

        # Đọc ảnh & ROI
        frame = cv2.imread(image_path)
        if frame is None:
            continue

        roi_mgr = ROIManager(config_path)
        fh, fw = frame.shape[:2]
        roi_mgr.validate_resolution(fw, fh)

        # Detect
        detections = detector.detect(frame)
        print(f"    → Phát hiện {len(detections)} vật thể | Ground Truth: {len(annotations)} annotations")

        # Spatial check trên mỗi detection
        for det in detections:
            sp = checker.check_multi(det["box"], roi_mgr.polygons)
            all_pred.append({
                "box": list(det["box"]),
                "is_violation": sp["is_violation"],
                "overlap_pct": sp["overlap_pct"],
                "conf": det["conf"]
            })

        # Thêm GT
        for ann in annotations:
            all_gt.append({
                "box": ann["box"],
                "is_violation": ann["is_violation"]
            })

    # 3. Đánh giá
    if not all_gt:
        print("\n[LỖI] Không có ground truth nào để đánh giá!")
        return None

    results = evaluator.evaluate(all_gt, all_pred)

    print("\n" + "=" * 70)
    print("📊 KẾT QUẢ ĐÁNH GIÁ SYSTEM-LEVEL")
    print("=" * 70)
    print(f"  • True Positives (TP)  : {results['TP']}")
    print(f"  • False Positives (FP) : {results['FP']}")
    print(f"  • False Negatives (FN) : {results['FN']}")
    print(f"  • System Precision     : {results['system_precision']*100:.2f}%")
    print(f"  • System Recall        : {results['system_recall']*100:.2f}%")
    print(f"  • System F1-Score      : {results['system_f1']*100:.2f}%")
    print("=" * 70)

    # 4. Xuất báo cáo Markdown
    os.makedirs(os.path.dirname(output_report), exist_ok=True)
    md_report = evaluator.generate_markdown_report(results)

    # Thêm chi tiết cấu hình thực nghiệm
    md_header = f"""# BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG TOÀN HỆ THỐNG (SYSTEM-LEVEL METRICS)

> **Phương pháp:** Chạy toàn bộ pipeline (AI Detection + Spatial Rule Engine) trên bộ ảnh có gán nhãn Ground Truth thủ công, sau đó so khớp kết quả phán quyết vi phạm với nhãn thực tế.

> **Phân biệt với Model-level Metrics:** mAP/Precision/Recall từ Ultralytics chỉ đo khả năng **phát hiện vật thể "biển hiệu"** trong ảnh. Các chỉ số dưới đây đo khả năng **phán quyết đúng "LẤN CHIẾM VỈA HÈ"** — bao gồm cả logic hình học (Spatial) và ngưỡng overlap.

### Cấu hình thực nghiệm

| Thông số | Giá trị |
| :--- | :--- |
| **Số ảnh test** | {len(gt_data)} |
| **Tổng annotations GT** | {len(all_gt)} |
| **Tổng predictions hệ thống** | {len(all_pred)} |
| **Ngưỡng overlap (Threshold)** | {overlap_threshold*100:.0f}% |
| **Model** | {model_path} |
| **Ngưỡng confidence AI** | 20% |

---

"""
    with open(output_report, "w", encoding="utf-8") as f:
        f.write(md_header + md_report)

    print(f"\n[+] Đã xuất báo cáo: {output_report}")
    return results


if __name__ == "__main__":
    run_system_evaluation()
