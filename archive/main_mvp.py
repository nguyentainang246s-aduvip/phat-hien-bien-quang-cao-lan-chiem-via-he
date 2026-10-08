"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
TASK: 19 & 20 - PIPELINE MVP HOÀN CHỈNH (CỘT MỐC SỐNG CÒN - MILESTONE M7)
Luồng tích hợp: Camera -> ROI Vỉa hè -> AI YOLO -> Logic Phán quyết Vi phạm
==============================================================================
"""

import os
import sys
import time
import cv2

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from camera import VideoReader
from roi import ROIManager
from detection import YOLODetector
from violation import ViolationChecker
from utils import FPSTracker, draw_fps_badge, draw_detection


def run_mvp_pipeline(video_path: str = None, model_path: str = "models/best.pt", config_path: str = None):
    print("=" * 70)
    print("KHỞI ĐỘNG HỆ THỐNG GIÁM SÁT LẤN CHIẾM VỈA HÈ - PHIÊN BẢN MVP (TASK 19)")
    print("=" * 70)

    # 1. KẾT NỐI NGUỒN ĐẦU VÀO (VIDEO HOẶC ẢNH)
    if video_path is None or not os.path.exists(video_path):
        video_dir = "data/videos"
        files = [f for f in os.listdir(video_dir) if f.lower().endswith(('.mp4', '.avi', '.mov'))] if os.path.exists(video_dir) else []
        video_path = os.path.join(video_dir, files[0]) if files else "data/videos/sample_cctv.mp4"

    is_image = video_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))

    # TỰ ĐỘNG CHỌN CONFIG PHÙ HỢP NẾU NGƯỜI DÙNG KHÔNG CHỈ ĐỊNH
    if config_path is None:
        if os.path.exists("configs/roi_moi.json"):
            config_path = "configs/roi_moi.json"
        elif "Duck-ai-image" in video_path and os.path.exists("configs/roi_duck_image.json"):
            config_path = "configs/roi_duck_image.json"
        else:
            config_path = "configs/roi_camera1.json"


    # 2. NẠP CẤU HÌNH VÙNG VỈA HÈ (ROI)
    roi_manager = ROIManager(config_path)
    if not roi_manager.polygons:
        print(f"[CẢNH BÁO] Không tìm thấy hoặc cấu hình ROI chưa đủ 3 điểm: {config_path}")
        print("Hệ thống sẽ chạy ở chế độ AI thuần túy (chưa có vỉa hè).")
    else:
        print(f"[+] File cấu hình ROI  : {config_path}")
        total_pts = sum(len(p) for p in roi_manager.polygons)
        print(f"[+] Vùng vỉa hè camera : {roi_manager.camera_id} ({len(roi_manager.polygons)} vùng vỉa hè, tổng {total_pts} đỉnh)")


    # 3. NẠP BỘ NÃO AI (YOLO)
    if not os.path.exists(model_path):
        print(f"[CẢNH BÁO] Chưa có '{model_path}', tạm thời dùng 'yolov8n.pt' mặc định.")
        model_path = "yolov8n.pt"

    detector = YOLODetector(model_path=model_path, conf_threshold=0.20)
    print(f"[+] Mô hình AI nạp     : {model_path}")

    # 4. NẠP BỘ PHÁN QUYẾT VI PHẠM (VIOLATION CHECKER)
    checker = ViolationChecker(threshold=0.30)
    print(f"[+] Ngưỡng lấn chiếm   : >= {checker.threshold*100:.0f}% diện tích & chân đế trên vỉa hè")

    fps_tracker = FPSTracker(alpha=0.15)
    window_name = "CCTV Sidewalk Surveillance - MVP Pipeline"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    if is_image:
        print(f"[+] Nguồn ảnh kiểm thử : {video_path}")
        print("-" * 70)
        print(">> ĐANG HIỂN THỊ KẾT QUẢ PHÂN TÍCH... Nhấn phím bất kỳ hoặc 'q' để đóng.")

        frame = cv2.imread(video_path)
        if frame is None:
            print(f"[LỖI] Không thể đọc ảnh: {video_path}")
            return False

        h, w = frame.shape[:2]
        cv2.resizeWindow(window_name, min(w, 960), min(h, 720))

        # BƯỚC A: AI PHÁT HIỆN TRÊN KHUNG HÌNH GỐC NGUYÊN BẢN (CHƯA VẼ)
        t0 = time.perf_counter()
        detections = detector.detect(frame)
        infer_time = (time.perf_counter() - t0) * 1000

        # BƯỚC B: VẼ LỚP PHỦ VỈA HÈ BÁN TRONG SUỐT (ROI OVERLAY) SAU KHI AI ĐÃ QUÉT
        roi_manager.draw_overlay(frame, alpha=0.25)


        violations_count = 0
        for det in detections:
            box = det["box"]
            conf = det["conf"]
            v_res = checker.check_multi(box, roi_manager.polygons)
            is_viol = v_res["is_violation"]

            if is_viol:
                violations_count += 1
                sw_idx = v_res.get("sidewalk_index", 1)
                label_text = f"VI PHAM VH#{sw_idx}: {v_res['overlap_pct']}% (Conf: {conf*100:.0f}%)"
            else:
                label_text = f"HOP LE: {v_res['overlap_pct']}% (Conf: {conf*100:.0f}%)"


            draw_detection(frame, box, label_text, is_violation=is_viol)

        # HUD
        hud_text = f"Tong bien: {len(detections)} | Vi pham: {violations_count} | Infer: {infer_time:.1f}ms"
        hud_color = (0, 0, 255) if violations_count > 0 else (0, 255, 0)
        cv2.putText(frame, hud_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, hud_color, 2, cv2.LINE_AA)

        cv2.imshow(window_name, frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        print("-" * 70)
        print("KẾT QUẢ PHÂN TÍCH ẢNH:")
        print(f"  • Số biển hiệu phát hiện        : {len(detections)}")
        print(f"  • Số biển hiệu lấn chiếm vỉa hè : {violations_count}")
        print(f"  • Thời gian xử lý AI            : {infer_time:.1f} ms")
        print("=" * 70)
        return True

    # CHẾ ĐỘ VIDEO STREAM
    reader = VideoReader(video_path)
    cv2.resizeWindow(window_name, min(reader.width, 960), min(reader.height, 720))
    print(f"[+] Nguồn video CCTV   : {video_path} ({reader.width}x{reader.height}, {reader.fps:.1f} FPS)")
    print("-" * 70)
    print(">> ĐANG GIÁM SÁT TRỰC TIẾP... Nhấn phím 'q' hoặc 'ESC' để dừng.")

    frame_count = 0
    total_violations_detected = 0

    try:
        while True:
            ret, frame = reader.read()
            if not ret:
                # Tua lại đầu video để chạy vòng lặp liên tục như camera CCTV thật
                reader.reset()
                continue

            frame_count += 1

            # BƯỚC A: AI PHÁT HIỆN TRÊN KHUNG HÌNH GỐC NGUYÊN BẢN (CHƯA VẼ)
            detections = detector.detect(frame)

            # BƯỚC B: VẼ LỚP PHỦ VỈA HÈ BÁN TRONG SUỐT (ROI OVERLAY) SAU KHI AI ĐÃ QUÉT
            roi_manager.draw_overlay(frame, alpha=0.25)


            current_frame_violations = 0

            # BƯỚC C: PHÂN TÍCH HÌNH HỌC LẤN CHIẾM TỪNG VẬT THỂ
            for det in detections:
                box = det["box"]
                conf = det["conf"]

                # Chạy qua bộ phán quyết vi phạm lai (Hỗ trợ nhiều vỉa hè)
                v_res = checker.check_multi(box, roi_manager.polygons)
                is_viol = v_res["is_violation"]

                if is_viol:
                    current_frame_violations += 1
                    total_violations_detected += 1
                    sw_idx = v_res.get("sidewalk_index", 1)
                    label_text = f"VI PHAM VH#{sw_idx}: {v_res['overlap_pct']}% (Conf: {conf*100:.0f}%)"
                else:
                    label_text = f"HOP LE: {v_res['overlap_pct']}%"


                # BƯỚC D: VẼ BOUNDING BOX + NHÃN MÀU (Đỏ = Vi phạm, Xanh = Hợp lệ)
                draw_detection(frame, box, label_text, is_violation=is_viol)

            # BƯỚC E: VẼ BẢNG ĐIỀU KHIỂN THÔNG SỐ (HUD OVERLAY)
            # Đo và vẽ FPS
            current_fps = fps_tracker.update()
            draw_fps_badge(frame, current_fps, reader.fps)

            # Vẽ thanh trạng thái cảnh báo trên cùng bên phải
            hud_text = f"Tong bien: {len(detections)} | Vi pham: {current_frame_violations}"
            hud_color = (0, 0, 255) if current_frame_violations > 0 else (0, 255, 0)
            cv2.putText(frame, hud_text, (reader.width - 400, 32),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, hud_color, 2, cv2.LINE_AA)

            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break

    finally:
        reader.release()
        cv2.destroyAllWindows()
        print("-" * 70)
        print("TỔNG KẾT PHIÊN GIÁM SÁT MVP:")
        print(f"  • Tổng số frames đã xử lý        : {frame_count}")
        print(f"  • Tốc độ xử lý trung bình (FPS) : {fps_tracker.smoothed_fps:.1f} FPS")
        print(f"  • Tổng số lượt phát hiện vi phạm : {total_violations_detected}")
        print("[OK] Đã giải phóng tài nguyên hệ thống an toàn.")
        print("=" * 70)

    return True


if __name__ == "__main__":
    target_media = sys.argv[1] if len(sys.argv) > 1 else None
    target_config = sys.argv[2] if len(sys.argv) > 2 else None
    run_mvp_pipeline(target_media, config_path=target_config)

