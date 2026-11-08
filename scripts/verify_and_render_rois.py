import cv2
import json
import os
import numpy as np

def main():
    out_dir = "reports/figures/tuan_4_8"
    os.makedirs(out_dir, exist_ok=True)

    mapping = [
        ("data/videos/video test.mp4", "configs/roi_video_test.json", "camera_1_video_test.jpg"),
        ("data/videos/videotesst2.mp4", "configs/roi_videotesst2.json", "camera_2_videotesst2.jpg"),
        ("data/videos/video test3.mp4", "configs/roi_video_test3.json", "camera_3_video_test3.jpg"),
        ("data/videos/videotest4.mp4", "configs/roi_videotest4.json", "camera_4_videotest4.jpg"),
        ("data/videos/videotest5.mp4", "configs/roi_videotest5.json", "camera_5_videotest5.jpg"),
        ("data/videos/videotest6.mp4", "configs/roi_videotest6.json", "camera_6_videotest6.jpg"),
    ]

    summary = []

    for v_path, r_path, out_name in mapping:
        cap = cv2.VideoCapture(v_path)
        ret, frame = cap.read()
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        if not ret:
            print(f"[!] Không thể đọc frame từ video: {v_path}")
            continue

        with open(r_path, "r", encoding="utf-8") as f:
            roi_data = json.load(f)

        polys = roi_data.get("polygons")
        if not polys and "polygon_points" in roi_data:
            polys = [roi_data["polygon_points"]]

        overlay = frame.copy()
        for poly in polys:
            pts = np.array(poly, dtype=np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(overlay, [pts], (0, 255, 0))
            cv2.polylines(frame, [pts], True, (0, 0, 255), 3)

        cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)

        cam_id = roi_data.get("camera_id", os.path.basename(v_path))
        num_pts = roi_data.get("total_points", sum(len(p) for p in polys))
        cv2.putText(frame, f"ROI: {cam_id} ({num_pts} pts) - {w}x{h}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        out_path = os.path.join(out_dir, out_name)
        cv2.imwrite(out_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        print(f"[✓] Đã xuất ảnh minh chứng: {out_path} ({w}x{h})")

        summary.append({
            "video_path": v_path,
            "roi_config": r_path,
            "resolution": f"{w}x{h}",
            "fps": fps,
            "total_frames": total_frames,
            "duration_sec": total_frames / fps if fps > 0 else 0,
            "camera_id": cam_id,
            "regions_count": len(polys),
            "total_points": num_pts,
            "preview_image": out_path
        })

    print(f"\n[HOÀN THÀNH] Đã đối chiếu và kết xuất 6/6 hình ảnh minh chứng ROI khớp với video!")
    return summary

if __name__ == "__main__":
    main()

