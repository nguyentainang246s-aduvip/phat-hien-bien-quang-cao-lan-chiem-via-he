import sys, os
sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import cv2
from tracking import ObjectTracker, TemporalVerifier, TrackState
from roi import ROIManager
from violation import ViolationChecker

tracker = ObjectTracker(model_path='models/best.pt', conf_threshold=0.25, imgsz=1280)
roi_mgr = ROIManager('configs/roi_video_test.json')
checker = ViolationChecker(threshold=0.30)
verifier = TemporalVerifier(confirm_frames=20, confirm_seconds=3.0, source_fps=24.0)

cap = cv2.VideoCapture('data/videos/video test.mp4')
confirmed_count = 0
frame_idx = 0
confirmed_tracks = set()

while cap.isOpened() and frame_idx < 150:
    ret, frame = cap.read()
    if not ret:
        break
    frame_idx += 1
    tracks = tracker.track(frame)
    for t in tracks:
        tid = t['track_id']
        box = t['box']
        conf = t['conf']
        sp = checker.check(box, roi_mgr.polygons[0])
        status = verifier.update(tid, box, sp, conf)
        if status == TrackState.CONFIRMED and tid not in confirmed_tracks:
            confirmed_tracks.add(tid)
            confirmed_count += 1
            print(f"Frame {frame_idx}: Confirmed Track #{tid}, Box: {box}, Overlap: {sp['overlap_pct']}%, Conf: {conf*100:.1f}%")

cap.release()
print(f"Tổng số track vi phạm đã xác nhận: {len(confirmed_tracks)}")
