import csv
import json
import yaml
from pathlib import Path

print("=" * 70)
print("AUDIT SCRIPT: VERIFYING ALL EXPERIMENTAL NUMBERS")
print("=" * 70)

# 1. Compare Old v13 vs New v13_clean
runs = [
    ("Old v13", Path("runs/detect/train_v13/results.csv")),
    ("Newest v13_clean", Path("reports/train_v13_clean/content/runs/detect/runs/detect/train_v13_clean/results.csv"))
]

for name, path in runs:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [k.strip() for k in reader.fieldnames]
            rows = list(reader)
        best_row = max(rows, key=lambda r: 0.1 * float(r["metrics/mAP50(B)"]) + 0.9 * float(r["metrics/mAP50-95(B)"]))
        print(f"Run [{name}]:")
        print(f"  Total epochs: {len(rows)}")
        print(f"  Best epoch  : {best_row['epoch']}")
        print(f"  Precision   : {float(best_row['metrics/precision(B)']):.5f}")
        print(f"  Recall      : {float(best_row['metrics/recall(B)']):.5f}")
        print(f"  mAP@50      : {float(best_row['metrics/mAP50(B)']):.5f}")
        print(f"  mAP@50-95   : {float(best_row['metrics/mAP50-95(B)']):.5f}")
        print("-" * 50)

# 2. Check test evaluation log
log_path = Path("reports/test_evaluation/test_v13_clean_local")
print("Local test eval directory exists:", log_path.exists())

# 3. Check system evaluation on video
sys_eval_path = Path("reports/system_eval_results.json")
if sys_eval_path.exists():
    with open(sys_eval_path, "r", encoding="utf-8") as f:
        sys_data = json.load(f)
    print("\nSystem Eval Video Results:")
    summary = sys_data.get("summary", {})
    for k, v in summary.items():
        print(f"  {k}: {v}")

print("=" * 70)

