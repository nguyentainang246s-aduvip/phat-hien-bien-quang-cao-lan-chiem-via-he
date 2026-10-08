r"""
==============================================================================
CHƯƠNG TRÌNH NHẬN DIỆN BIỂN HIỆU / BIỂN QUẢNG CÁO (THUẦN YOLO, KHÔNG CẦN ROI)
==============================================================================
Sử dụng:
  # Chạy trên ảnh:
  python detect_only.py --source "data/images/Duck-ai-image-2026-09-14-09-20 (1).jpeg"

  # Chạy trên video:
  python detect_only.py --source data/videos/sample.mp4 --max-frames 100

  # Chạy trên toàn bộ thư mục ảnh:
  python detect_only.py --source data/images/
==============================================================================
"""

import os
import sys
import argparse
import cv2
from ultralytics import YOLO

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def detect_image(model, img_path, conf_thresh, out_dir):
    img = cv2.imread(img_path)
    if img is None:
        print(f"[!] Không thể đọc ảnh: {img_path}")
        return

    h, w = img.shape[:2]
    res = model.predict(img, conf=conf_thresh, imgsz=640, verbose=False)[0]
    boxes = res.boxes

    print("=" * 65)
    print(f"📷 Ảnh: {os.path.basename(img_path)} ({w}x{h})")
    print(f"-> Số biển quảng cáo phát hiện: {len(boxes)}")
    for idx, b in enumerate(boxes, 1):
        conf = float(b.conf[0])
        xyxy = [round(x, 1) for x in b.xyxy[0].tolist()]
        print(f"   [#{idx}] Độ tin cậy: {conf*100:.1f}% | Box: {xyxy}")

    # Vẽ kết quả chỉ với bounding box biển quảng cáo
    annotated = res.plot()

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"detected_{os.path.basename(img_path)}")
    cv2.imwrite(out_path, annotated)
    print(f"✅ Đã lưu kết quả tại: {out_path}")
    print("=" * 65)


def detect_video(model, video_path, conf_thresh, out_dir, max_frames=None):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[!] Không thể mở video: {video_path}")
        return

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    os.makedirs(out_dir, exist_ok=True)
    out_name = f"detected_{os.path.splitext(os.path.basename(video_path))[0]}.mp4"
    out_path = os.path.join(out_dir, out_name)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))

    print("=" * 65)
    print(f"🎬 Video: {os.path.basename(video_path)} ({w}x{h} @ {fps:.1f} FPS, Tổng {total_frames} frames)")
    print(f"Đang nhận diện biển quảng cáo...")

    frame_count = 0
    total_detections = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        res = model.predict(frame, conf=conf_thresh, imgsz=640, verbose=False)[0]
        n_box = len(res.boxes)
        total_detections += n_box

        annotated = res.plot()
        writer.write(annotated)

        if frame_count % 30 == 0 or frame_count == total_frames:
            print(f"   Frame {frame_count}/{total_frames or '?'} - Đang phát hiện {n_box} biển quảng cáo")

        if max_frames and frame_count >= max_frames:
            print(f"[INFO] Dừng tại giới hạn {max_frames} frames.")
            break

    cap.release()
    writer.release()

    print(f"\n✅ Hoàn thành! Đã xuất video kết quả tại: {out_path}")
    print(f"Tổng số lượt phát hiện qua {frame_count} frames: {total_detections}")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Nhận diện biển quảng cáo thuần YOLO (Không dùng ROI)")
    parser.add_argument("--source", type=str, default="data/images/Duck-ai-image-2026-09-14-09-20 (1).jpeg",
                        help="Đường dẫn file ảnh, thư mục ảnh hoặc file video")
    parser.add_argument("--model", type=str, default="models/best.pt",
                        help="Đường dẫn trọng số YOLO (mặc định: models/best.pt)")
    parser.add_argument("--conf", type=float, default=0.25,
                        help="Ngưỡng tin cậy (mặc định: 0.25)")
    parser.add_argument("--out-dir", type=str, default="reports/demo_results",
                        help="Thư mục lưu ảnh/video kết quả")
    parser.add_argument("--max-frames", type=int, default=150,
                        help="Giới hạn số frames khi xử lý video")

    args = parser.parse_args()

    if not os.path.exists(args.model):
        print(f"[LỖI] Không tìm thấy file model: {args.model}")
        return

    print(f"[*] Nạp mô hình: {args.model} | Ngưỡng tin cậy conf={args.conf}")
    model = YOLO(args.model)

    source = args.source
    if os.path.isdir(source):
        extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
        files = [os.path.join(source, f) for f in os.listdir(source) if f.lower().endswith(extensions)]
        print(f"[*] Quét thấy {len(files)} tệp ảnh trong thư mục: {source}")
        for f in files:
            detect_image(model, f, args.conf, args.out_dir)
    elif source.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        detect_video(model, source, args.conf, args.out_dir, max_frames=args.max_frames)
    elif source.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
        detect_image(model, source, args.conf, args.out_dir)
    else:
        print(f"[LỖI] Định dạng tệp không được hỗ trợ: {source}")


if __name__ == "__main__":
    main()
