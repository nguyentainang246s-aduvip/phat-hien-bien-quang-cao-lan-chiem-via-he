import sys
import os
sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import cv2
from detection import YOLODetector
from roi import ROIManager
from violation import ViolationChecker
from test_on_image import process_and_annotate

detector = YOLODetector(model_path='models/best.pt', conf_threshold=0.25, imgsz=1280)
roi_mgr = ROIManager('configs/roi_ChatGPT_Image_Sep_30_2026_09_49_42_PM.json')
checker = ViolationChecker(threshold=0.30)

img = cv2.imread('data/images/ChatGPT Image Sep 30, 2026, 09_49_42 PM.png')
dets = detector.detect(img)
poly = roi_mgr.polygons[0]

print(f"Tổng số biển hiệu phát hiện bởi mô hình mới (v13_clean): {len(dets)}")
for i, d in enumerate(dets):
    box = d['bbox']
    conf = d['confidence']
    overlap = checker.calculate_overlap_ratio(box, poly)
    is_vio = overlap >= 0.30
    status = "VI PHẠM" if is_vio else "HỢP LỆ"
    print(f"Biển {i+1}: Conf={conf*100:.1f}%, Overlap={overlap*100:.1f}%, Trạng thái={status}, Box={box}")

# Render annotated image
vis, details = process_and_annotate(img, dets, checker, roi_mgr, show_roi=True)
out_path = 'data/images/output_v13_clean/v13_clean_detected_street1.png'
cv2.imwrite(out_path, vis)
print(f"[OK] Đã lưu ảnh kết quả nhận diện mới vào: {out_path}")
