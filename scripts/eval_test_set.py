import sys
import time
from pathlib import Path
from ultralytics import YOLO

def main():
    model_path = Path("models/best.pt")
    data_yaml = Path("datasets/v13_clean/data.yaml")
    
    if not model_path.exists():
        print(f"Error: {model_path} does not exist!")
        sys.exit(1)
        
    print(f"[*] Loading model: {model_path}...")
    model = YOLO(str(model_path))
    
    print(f"[*] Running independent test evaluation on {data_yaml} (split='test', imgsz=1280)...")
    t0 = time.time()
    
    metrics = model.val(
        data=str(data_yaml),
        split="test",
        imgsz=1280,
        batch=4,
        device="cpu",
        plots=True,
        project="reports/test_evaluation",
        name="test_v13_clean_local"
    )
    
    t_elapsed = time.time() - t0
    print("\n" + "=" * 70)
    print(f"TEST EVALUATION COMPLETED IN {t_elapsed:.1f}s")
    print("=" * 70)
    p = metrics.results_dict.get("metrics/precision(B)", 0)
    r = metrics.results_dict.get("metrics/recall(B)", 0)
    map50 = metrics.results_dict.get("metrics/mAP50(B)", 0)
    map5095 = metrics.results_dict.get("metrics/mAP50-95(B)", 0)
    
    print(f"  Precision (Độ chính xác) : {p:.4f} ({p*100:.2f}%)")
    print(f"  Recall (Độ bao phủ)      : {r:.4f} ({r*100:.2f}%)")
    print(f"  mAP@50                   : {map50:.4f} ({map50*100:.2f}%)")
    print(f"  mAP@50-95                : {map5095:.4f} ({map5095*100:.2f}%)")
    print("=" * 70)

if __name__ == "__main__":
    main()

