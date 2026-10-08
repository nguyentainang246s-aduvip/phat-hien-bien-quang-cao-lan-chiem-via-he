"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Đánh Giá Thực Nghiệm Toàn Diện Hệ Thống Trên Luồng Video Thực Tế
Mục tiêu: Chạy 100% video thực địa (1 pass từ đầu đến cuối), trích xuất từng track_id,
          lưu ảnh bằng chứng crop cho từng biển, xuất bảng đánh giá System Metrics.
==============================================================================
"""

import os
import sys
import json
import time
import cv2
import numpy as np

sys.path.insert(0, os.path.abspath("."))

from tracking.tracker import ObjectTracker
from tracking.verifier import TemporalVerifier, TrackState
from violation.checker import ViolationChecker
from roi.roi_manager import ROIManager

OUTPUT_DIR = "reports/video_eval_crops"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def evaluate_single_video(
    video_path: str,
    roi_config_path: str,
    model_path: str = "models/best.onnx",
    conf_threshold: float = 0.20,
    overlap_threshold: float = 0.30,
    confirm_frames: int = 15,
    confirm_seconds: float = 3.0,
    frame_skip: int = 2,
    output_crops_dir: str = OUTPUT_DIR
):
    print("=" * 75)
    print(f"🎬 BẮT ĐẦU ĐÁNH GIÁ VIDEO: {video_path}")
    print(f"   • ROI Config: {roi_config_path}")
    print(f"   • Model     : {model_path} (Conf: {conf_threshold*100:.0f}%, Overlap: {overlap_threshold*100:.0f}%)")
    print(f"   • Temporal  : {confirm_frames} frames / {confirm_seconds}s")
    print("=" * 75)

    if not os.path.exists(video_path):
        print(f"[LỖI] Không tìm thấy video: {video_path}")
        return None

    if not os.path.exists(roi_config_path):
        print(f"[LỖI] Không tìm thấy ROI config: {roi_config_path}")
        return None

    roi_manager = ROIManager(roi_config_path)
    tracker = ObjectTracker(model_path=model_path, conf_threshold=conf_threshold, imgsz=640)
    checker = ViolationChecker(threshold=overlap_threshold)
    verifier = TemporalVerifier(
        confirm_frames=confirm_frames,
        confirm_seconds=confirm_seconds,
        cooldown_seconds=60.0,
        min_avg_confidence=0.35,
        require_stationary=True,
        max_displacement_pixels=80.0
    )

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    verifier.source_fps = fps
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    roi_manager.validate_resolution(width, height)

    video_basename = os.path.splitext(os.path.basename(video_path))[0].replace(" ", "_")
    video_crop_dir = os.path.join(output_crops_dir, video_basename)
    os.makedirs(video_crop_dir, exist_ok=True)

    tracks_summary = {}  # track_id -> dict metrics
    frame_idx = 0
    t_start = time.perf_counter()

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            break

        frame_idx += 1
        is_infer = (frame_skip <= 0) or (frame_idx % (frame_skip + 1) == 1)

        if is_infer:
            clean_frame = frame.copy()
            tracked_objs = tracker.track(frame)
            simulated_ts = frame_idx / fps
            verified_objs = verifier.process_frame(
                tracked_objs, checker, roi_manager.polygons, current_timestamp=simulated_ts
            )

            for vo in verified_objs:
                tid = vo["track_id"]
                if tid <= 0:
                    continue

                box = vo["box"]
                conf = vo["conf"]
                spatial = vo["spatial_res"]
                t_status = vo["temporal_status"]
                is_alert = vo["is_new_alert"]

                if tid not in tracks_summary:
                    tracks_summary[tid] = {
                        "track_id": tid,
                        "first_frame": frame_idx,
                        "last_frame": frame_idx,
                        "total_detections": 0,
                        "conf_list": [],
                        "overlap_list": [],
                        "is_spatial_viol_count": 0,
                        "final_status": t_status,
                        "best_conf": conf,
                        "best_crop_path": None,
                        "is_new_alert": False
                    }

                t_info = tracks_summary[tid]
                t_info["last_frame"] = frame_idx
                t_info["total_detections"] += 1
                t_info["conf_list"].append(conf)
                t_info["overlap_list"].append(spatial["overlap_ratio"] * 100)
                if spatial["is_violation"]:
                    t_info["is_spatial_viol_count"] += 1

                # Cập nhật trạng thái cao nhất
                if t_status == TrackState.CONFIRMED:
                    t_info["final_status"] = TrackState.CONFIRMED
                elif t_status == TrackState.SUSPECTED and t_info["final_status"] != TrackState.CONFIRMED:
                    t_info["final_status"] = TrackState.SUSPECTED

                if is_alert:
                    t_info["is_new_alert"] = True

                # Lưu ảnh crop tốt nhất (ảnh có độ tin cậy cao nhất)
                if conf >= t_info["best_conf"] or t_info["best_crop_path"] is None:
                    t_info["best_conf"] = conf
                    x1, y1, x2, y2 = [int(v) for v in box]
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(width, x2), min(height, y2)
                    if (x2 - x1) > 10 and (y2 - y1) > 10:
                        crop = clean_frame[y1:y2, x1:x2]
                        crop_fname = f"track_{tid}_conf{int(conf*100)}.jpg"
                        crop_path = os.path.join(video_crop_dir, crop_fname)
                        cv2.imwrite(crop_path, crop)
                        t_info["best_crop_path"] = crop_path

    cap.release()
    total_time = time.perf_counter() - t_start
    avg_fps = frame_idx / total_time if total_time > 0 else 0

    # Tổng kết bảng kết quả cho video
    print(f"\n✅ ĐÃ XỬ LÝ XONG {frame_idx}/{total_frames} FRAMES ({frame_idx/fps:.1f}s)")
    print(f"⏱️ Tốc độ xử lý trung bình: {avg_fps:.1f} FPS")
    print(f"🔍 Tổng số Track ID theo dõi được: {len(tracks_summary)}")
    print("-" * 75)
    print(f"{'Track ID':<10} | {'Frames':<8} | {'Avg Conf':<10} | {'Avg Overlap':<12} | {'Trạng thái phán quyết'}")
    print("-" * 75)

    confirmed_count = 0
    suspected_count = 0
    normal_count = 0

    for tid, info in sorted(tracks_summary.items()):
        avg_c = np.mean(info["conf_list"]) if info["conf_list"] else 0
        avg_ov = np.mean(info["overlap_list"]) if info["overlap_list"] else 0
        status_str = info["final_status"]

        if status_str == TrackState.CONFIRMED:
            confirmed_count += 1
            status_display = "🔴 VI PHAM (CONFIRMED)"
        elif status_str == TrackState.SUSPECTED:
            suspected_count += 1
            status_display = "🟡 NGHI VAN (SUSPECTED)"
        else:
            normal_count += 1
            status_display = "🟢 HOP LE / KHONG VI PHAM"

        print(f"#{tid:<9} | {info['total_detections']:<8} | {avg_c*100:>5.1f}%    | {avg_ov:>6.1f}%      | {status_display}")

    print("-" * 75)
    print(f"📌 TỔNG KẾT: {confirmed_count} VI PHẠM XÁC NHẬN | {suspected_count} NGHI VẤN | {normal_count} BÌNH THƯỜNG")
    print(f"🖼️ Ảnh crop bằng chứng từng biển đã lưu tại: {video_crop_dir}\n")

    return {
        "video_path": video_path,
        "video_basename": video_basename,
        "total_frames": frame_idx,
        "duration_sec": frame_idx / fps,
        "avg_fps": avg_fps,
        "tracks": tracks_summary,
        "confirmed_count": confirmed_count,
        "suspected_count": suspected_count,
        "normal_count": normal_count,
        "crop_dir": video_crop_dir
    }


def main():
    videos_to_eval = [
        ("data/videos/video test.mp4", "configs/roi_video_test.json"),
        ("data/videos/videotesst2.mp4", "configs/roi_videotesst2.json"),
        ("data/videos/video test3.mp4", "configs/roi_video_test3.json"),
    ]

    results = []
    for vid, roi in videos_to_eval:
        res = evaluate_single_video(vid, roi)
        if res:
            results.append(res)

    # Xuất báo cáo Markdown tổng hợp
    report_file = "reports/BAO_CAO_THUC_NGHIEM_VIDEO_THAT.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO KẾT QUẢ ĐÁNH GIÁ HỆ THỐNG TRÊN VIDEO GIÁM SÁT THỰC TẾ\n\n")
        f.write("> **Mục tiêu:** Kiểm chứng chất lượng toàn diện của pipeline AI + ByteTrack + Temporal Verifier ")
        f.write("trên các đoạn video camera giám sát thực địa (thay thế bộ test 2 ảnh tĩnh cũ).\n\n")

        for r in results:
            f.write(f"## 1. Video: `{r['video_path']}`\n")
            f.write(f"- **Độ dài:** {r['total_frames']} frames ({r['duration_sec']:.1f} giây)\n")
            f.write(f"- **Tốc độ xử lý:** {r['avg_fps']:.1f} FPS (ONNX Runtime CPU AVX2)\n")
            f.write(f"- **Tổng số biển theo dõi:** {len(r['tracks'])} biển hiệu\n")
            f.write(f"- **Kết quả phán quyết:** **{r['confirmed_count']} Vi phạm (Confirmed)** | ")
            f.write(f"**{r['suspected_count']} Nghi vấn (Suspected)** | **{r['normal_count']} Hợp lệ**\n\n")

            f.write("| Track ID | Số frames xuất hiện | Độ tin cậy TB | Tỷ lệ lấn chiếm TB | Kết luận Hệ thống | File ảnh Crop |\n")
            f.write("| :---: | :---: | :---: | :---: | :---: | :--- |\n")
            for tid, t in sorted(r["tracks"].items()):
                avg_c = np.mean(t["conf_list"]) if t["conf_list"] else 0
                avg_ov = np.mean(t["overlap_list"]) if t["overlap_list"] else 0
                st = t["final_status"]
                crop_name = os.path.basename(t["best_crop_path"]) if t["best_crop_path"] else "N/A"
                f.write(f"| **#{tid}** | {t['total_detections']} | {avg_c*100:.1f}% | {avg_ov:.1f}% | `{st}` | `{crop_name}` |\n")
            f.write("\n---\n\n")

        f.write("## 2. Bảng Đánh giá System-level Metrics đối sánh Ground Truth\n")
        f.write("*(Cần đối chiếu số lượng biển vi phạm thực tế bằng mắt thường với các Track ID được hệ thống ghi nhận ở trên)*\n\n")

    print(f"📝 ĐÃ XUẤT BÁO CÁO ĐÁNH GIÁ VIDEO: {report_file}")


if __name__ == "__main__":
    main()
