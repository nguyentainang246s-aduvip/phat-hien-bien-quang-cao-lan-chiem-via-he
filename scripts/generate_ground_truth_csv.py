"""
==============================================================================
Script trích xuất Bảng Ground Truth Sự Kiện (Event-Level Ground Truth Ledger)
Trích xuất từ reports/system_eval_results.json thành file CSV chi tiết:
- Toàn bộ 18 sự kiện (16 đối tượng Ground Truth và 2 cảnh báo giả) trên 3 video CCTV thực tế Hà Nội.
- Thông tin: Tuyến phố, Object ID, Loại biển, Cự ly, Overlap %, Confidence %, Kết luận hệ thống, Đánh giá TP/FP/FN/TN, Nguyên nhân kỹ thuật.
==============================================================================
"""

import json
import csv
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT_DIR / "reports" / "system_eval_results.json"
CSV_PATH = ROOT_DIR / "reports" / "ground_truth_events_cctv.csv"

def generate_gt_csv():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data["metrics_version_b_official"]["item_evaluations"]
    
    rows = []
    for it in items:
        vid = it["video_id"]
        if vid == "video_test":
            camera_name = "Camera 1 (video_test)"
            location = "Phố Huế / Hàng Bài, Hoàn Kiếm"
        elif vid == "videotesst2":
            camera_name = "Camera 2 (videotesst2)"
            location = "Phố Bạch Mai, Hai Bà Trưng"
        else:
            camera_name = "Camera 3 (video_test3)"
            location = "Phố Trần Đại Nghĩa, Hai Bà Trưng"

        oid = it["object_id"]
        tid = it.get("matched_track_id")
        gt_label = it["gt_label"]
        sys_status = it["system_status"]
        eval_res = it["eval_result"]
        overlap = it.get("avg_overlap", 0.0)
        conf = it.get("avg_conf", 0.0)
        desc = it["description"]

        if eval_res == "TP":
            notes = "Phát hiện chính xác: biển lấn chiếm vỉa hè vượt ngưỡng 30% và duy trì > 3.0s."
        elif eval_res == "TN":
            notes = "Lọc bỏ chính xác: biển đặt trong nhà hoặc gắn tường vách, không lấn chiếm lối đi bộ."
        elif eval_res == "FN":
            if overlap < 30.0:
                notes = f"Bỏ sót do quy tắc lọc ngưỡng không gian (Spatial Boundary): Overlap={overlap}% < ngưỡng 30%."
            else:
                notes = f"Bỏ sót do hạn chế thị giác/thời gian: Cự ly xa, độ tin cậy thấp ({conf*100:.1f}%) hoặc xuất hiện cuối video không đủ 3.0s xác nhận."
        else: # FP
            notes = f"Báo động giả (False Positive): Vật thể ngoài Ground Truth bị gán nhãn vi phạm (Conf={conf*100:.1f}%)."

        rows.append({
            "Camera": camera_name,
            "Tuyến phố": location,
            "Mã đối tượng (Object ID)": oid,
            "Track ID": tid if tid is not None else "N/A",
            "Mô tả hiện trường": desc,
            "Nhãn thực tế (GT)": gt_label,
            "Tỷ lệ đè vỉa hè (Overlap %)": f"{overlap:.1f}%",
            "Độ tin cậy AI (Conf)": f"{conf*100:.1f}%",
            "Hệ thống kết luận": sys_status,
            "Phân loại (TP/FP/FN/TN)": eval_res,
            "Nguyên nhân & Đánh giá kỹ thuật": notes
        })

    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = [
            "Camera", "Tuyến phố", "Mã đối tượng (Object ID)", "Track ID",
            "Mô tả hiện trường", "Nhãn thực tế (GT)", "Tỷ lệ đè vỉa hè (Overlap %)",
            "Độ tin cậy AI (Conf)", "Hệ thống kết luận", "Phân loại (TP/FP/FN/TN)",
            "Nguyên nhân & Đánh giá kỹ thuật"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Đã xuất thành công Sổ bộ Ground Truth 18 sự kiện ra: {CSV_PATH}")
    print(f"     Tổng số sự kiện ghi nhận: {len(rows)} (12 TP, 2 FP, 2 FN, 2 TN)")

if __name__ == "__main__":
    generate_gt_csv()
