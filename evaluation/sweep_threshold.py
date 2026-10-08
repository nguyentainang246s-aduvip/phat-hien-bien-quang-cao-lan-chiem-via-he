"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Thực nghiệm quét ngưỡng diện tích (Threshold Sweep Experiment)
Mục tiêu: Giải trình khoa học cho việc lựa chọn ngưỡng overlap 30% (Chương 7)
Công thức: Overlap Ratio = Intersection Area / Bounding Box Area (Không phải IoU)
ISSUE 04 FIX: Tích hợp Ground Truth để tính F1 thực sự thay vì chỉ đếm violation
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


def run_threshold_sweep(
    gt_path: str = "evaluation/ground_truth.json",
    model_path: str = "models/best.pt",
    thresholds: list = None,
    output_report: str = "reports/threshold_sweep_report.md"
):
    if thresholds is None:
        thresholds = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60]

    # 1. Đọc Ground Truth
    if not os.path.exists(gt_path):
        print(f"[LỖI] Không tìm thấy file ground truth: {gt_path}")
        return []

    with open(gt_path, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    # 2. Detect tất cả vật thể một lần (reuse cho mọi threshold)
    detector = YOLODetector(model_path=model_path, conf_threshold=0.20)
    evaluator = SystemEvaluator(iou_threshold=0.5)

    all_detections = []  # [(frame_dets, roi_polygons, gt_annotations)]

    for entry in gt_data:
        image_path = entry["image_path"]
        config_path = entry.get("config_path", "configs/roi_moi.json")
        annotations = entry["annotations"]

        if not os.path.exists(image_path):
            continue

        frame = cv2.imread(image_path)
        if frame is None:
            continue

        roi_mgr = ROIManager(config_path)
        fh, fw = frame.shape[:2]
        roi_mgr.validate_resolution(fw, fh)

        dets = detector.detect(frame)
        all_detections.append((dets, roi_mgr.polygons, annotations))

    if not all_detections:
        print("[LỖI] Không có dữ liệu nào để quét ngưỡng!")
        return []

    # 3. Quét qua các ngưỡng overlap ratio
    print("=" * 70)
    print("🔬 THỰC NGHIỆM QUÉT NGƯỠNG DIỆN TÍCH (THRESHOLD SWEEP)")
    print("=" * 70)

    sweep_results = []
    best_f1 = -1.0
    best_threshold = 0.30

    for th in thresholds:
        checker = ViolationChecker(threshold=th)
        total_boxes = 0
        total_violations = 0
        all_gt = []
        all_pred = []
        avg_overlap = []

        for dets, polys, annotations in all_detections:
            for d in dets:
                total_boxes += 1
                sp = checker.check_multi(d["box"], polys)
                avg_overlap.append(sp["overlap_pct"])
                if sp["is_violation"]:
                    total_violations += 1
                all_pred.append({
                    "box": list(d["box"]),
                    "is_violation": sp["is_violation"]
                })

            for ann in annotations:
                all_gt.append({
                    "box": ann["box"],
                    "is_violation": ann["is_violation"]
                })

        # Tính System Metrics
        if all_gt:
            metrics = evaluator.evaluate(all_gt, all_pred)
            precision = metrics["system_precision"]
            recall = metrics["system_recall"]
            f1 = metrics["system_f1"]
        else:
            precision = recall = f1 = 0.0

        mean_ov = sum(avg_overlap) / len(avg_overlap) if avg_overlap else 0.0

        if f1 > best_f1:
            best_f1 = f1
            best_threshold = th

        # Đánh giá dựa trên F1 thực tế thay vì hard-code
        sweep_results.append({
            "threshold": th,
            "threshold_pct": f"{int(th*100)}%",
            "total_boxes": total_boxes,
            "violations": total_violations,
            "legal": total_boxes - total_violations,
            "violation_rate": f"{total_violations/total_boxes*100:.1f}%" if total_boxes > 0 else "0%",
            "mean_overlap": f"{mean_ov:.1f}%",
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tp": metrics["TP"] if all_gt else 0,
            "fp": metrics["FP"] if all_gt else 0,
            "fn": metrics["FN"] if all_gt else 0
        })

        print(f"  Threshold {int(th*100):>3}% | Violations: {total_violations:>3} | "
              f"P={precision*100:5.1f}% R={recall*100:5.1f}% F1={f1*100:5.1f}%"
              f"{' ← BEST' if th == best_threshold and f1 == best_f1 else ''}")

    print(f"\n  🏆 Ngưỡng tối ưu (F1 cao nhất): {int(best_threshold*100)}% (F1 = {best_f1*100:.1f}%)")
    print("=" * 70)

    # 4. Xuất báo cáo Markdown
    os.makedirs(os.path.dirname(output_report), exist_ok=True)
    with open(output_report, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO THỰC NGHIỆM QUÉT NGƯỠNG DIỆN TÍCH (THRESHOLD SWEEP EXPERIMENT)\n\n")
        f.write("> **Định nghĩa chỉ số:** `Overlap Ratio = Diện tích giao (Bbox ∩ ROI) / Diện tích Bounding Box`.\n")
        f.write("> **Mục đích:** Chứng minh bằng số liệu thực nghiệm lý do lựa chọn ngưỡng mặc định thông qua điểm F1-Score cao nhất trên bộ Ground Truth.\n\n")

        f.write("## Bảng kết quả quét ngưỡng\n\n")
        f.write("| Ngưỡng | Số biển | Vi phạm | Hợp lệ | Tỷ lệ VP | Overlap TB | Precision | Recall | **F1-Score** | Ghi chú |\n")
        f.write("| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |\n")

        for r in sweep_results:
            is_best = (r["threshold"] == best_threshold)
            note = "**🏆 Tối ưu (F1 cao nhất)**" if is_best else (
                "Quá nhạy (nhiều FP)" if r["threshold"] <= 0.15 else (
                    "Quá khắt khe (bỏ sót FN)" if r["threshold"] >= 0.50 else "Chấp nhận được"
                )
            )
            f1_str = f"**{r['f1']*100:.1f}%**" if is_best else f"{r['f1']*100:.1f}%"
            f.write(f"| {r['threshold_pct']} | {r['total_boxes']} | {r['violations']} | {r['legal']} "
                    f"| {r['violation_rate']} | {r['mean_overlap']} "
                    f"| {r['precision']*100:.1f}% | {r['recall']*100:.1f}% | {f1_str} | {note} |\n")

        f.write(f"\n### Kết luận khoa học\n\n")
        f.write(f"Dựa trên thực nghiệm quét {len(thresholds)} giá trị ngưỡng từ {int(thresholds[0]*100)}% đến {int(thresholds[-1]*100)}%, "
                f"ngưỡng **{int(best_threshold*100)}%** đạt điểm F1-Score cao nhất **({best_f1*100:.1f}%)**, "
                f"cân bằng tối ưu giữa:\n\n")
        f.write(f"1. **Precision** (tỷ lệ cảnh báo đúng): tránh báo động giả cho các biển chỉ nhô nhẹ mép.\n")
        f.write(f"2. **Recall** (tỷ lệ phát hiện): không bỏ sót các trường hợp lấn chiếm thực sự.\n\n")
        f.write(f"Do đó, ngưỡng `{int(best_threshold*100)}%` được chọn làm giá trị mặc định của hệ thống.\n")

    print(f"\n[+] Đã hoàn thành thực nghiệm Threshold Sweep! Báo cáo: {output_report}")
    return sweep_results


if __name__ == "__main__":
    run_threshold_sweep()
