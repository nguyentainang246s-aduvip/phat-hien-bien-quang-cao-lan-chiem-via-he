import csv
import sys
from pathlib import Path

csv_path = Path("reports/train_v13_clean/content/runs/detect/runs/detect/train_v13_clean/results.csv")
if not csv_path.exists():
    print(f"Error: {csv_path} not found")
    sys.exit(1)

with open(csv_path, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    reader.fieldnames = [k.strip() for k in reader.fieldnames]
    rows = list(reader)

print(f"Total epochs recorded in results.csv: {len(rows)}")
print("=" * 70)

for ep in [1, 42, 47, 62]:
    r = rows[ep - 1]
    p = float(r["metrics/precision(B)"])
    rc = float(r["metrics/recall(B)"])
    m50 = float(r["metrics/mAP50(B)"])
    m5095 = float(r["metrics/mAP50-95(B)"])
    fitness = 0.1 * m50 + 0.9 * m5095
    print(f"Epoch {ep:2d}:")
    print(f"  Train Loss: box={float(r['train/box_loss']):.4f}, cls={float(r['train/cls_loss']):.4f}, dfl={float(r['train/dfl_loss']):.4f}")
    print(f"  Val Loss  : box={float(r['val/box_loss']):.4f}, cls={float(r['val/cls_loss']):.4f}, dfl={float(r['val/dfl_loss']):.4f}")
    print(f"  Precision : {p:.4f}")
    print(f"  Recall    : {rc:.4f}")
    print(f"  mAP@50    : {m50:.4f}")
    print(f"  mAP@50-95 : {m5095:.4f}")
    print(f"  Fitness   : {fitness:.5f}")
    print("-" * 70)

best_by_fitness = max(rows, key=lambda r: 0.1 * float(r["metrics/mAP50(B)"]) + 0.9 * float(r["metrics/mAP50-95(B)"]))
print(f"BEST EPOCH BY ULTRALYTICS FITNESS (0.1*mAP50 + 0.9*mAP50-95) -> Epoch {best_by_fitness['epoch']}:")
print(f"  Precision : {float(best_by_fitness['metrics/precision(B)']):.4f}")
print(f"  Recall    : {float(best_by_fitness['metrics/recall(B)']):.4f}")
print(f"  mAP@50    : {float(best_by_fitness['metrics/mAP50(B)']):.4f}")
print(f"  mAP@50-95 : {float(best_by_fitness['metrics/mAP50-95(B)']):.4f}")
fitness_best = 0.1 * float(best_by_fitness['metrics/mAP50(B)']) + 0.9 * float(best_by_fitness['metrics/mAP50-95(B)'])
print(f"  Fitness   : {fitness_best:.5f}")
print("=" * 70)

