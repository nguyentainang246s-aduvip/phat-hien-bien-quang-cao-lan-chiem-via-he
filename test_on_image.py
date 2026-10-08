"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
TASK: Kiểm thử mô hình AI & Quản lý/Vẽ ROI Vỉa hè trên Album ảnh tĩnh
==============================================================================
Hướng dẫn sử dụng:
  1. Duyệt ảnh tương tác & VẼ ROI VỈA HÈ TRỰC TIẾP BẰNG CHUỘT:
     python test_on_image.py --gui
     --> Trong cửa sổ xem ảnh:
         • Nhấn phím 'r' : MỞ CÔNG CỤ VẼ ROI BẰNG CHUỘT CHO ẢNH ĐANG XEM!
         • Nhấn phím 'v' : Bật / Tắt hiển thị lớp phủ ROI vỉa hè
         • Nhấn 'd'/SPACE: Xem ảnh tiếp theo (Next)
         • Nhấn 'a'     : Quay lại ảnh trước (Previous)
         • Nhấn 'q'/ESC : Thoát

  2. Chạy công cụ vẽ ROI độc lập cho 1 ảnh bất kỳ:
     python roi_drawer.py "data/images/Screenshot 2026-09-30 214856.png" "configs/roi_screenshot.json"

  3. Chạy kiểm tra tự động xuất toàn bộ ảnh (Batch Mode kèm ROI):
     python test_on_image.py --roi configs/roi_pho_bang.json
==============================================================================
"""

import os
import sys
import time
import argparse
import cv2
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from detection import YOLODetector
from utils import draw_detection
from roi import ROIManager
from violation import ViolationChecker
from roi_drawer import run_roi_tool


def get_default_roi_path_for_image(img_path: str) -> str:
    """Xác định đường dẫn file JSON ROI mặc định cho một tệp ảnh."""
    base_name = os.path.splitext(os.path.basename(img_path))[0]
    clean_name = base_name.replace(" ", "_").replace(",", "").replace("-", "_")
    candidates = [
        os.path.join("configs", f"roi_{clean_name}.json"),
        os.path.join("configs", f"roi_{base_name.lower().replace(' ', '_')}.json"),
    ]
    if "screenshot" in base_name.lower():
        candidates.append(os.path.join("configs", "roi_screenshot.json"))
        candidates.append(os.path.join("configs", "roi_Screenshot_2026_09_30_214856.json"))
    if "09_49" in base_name or "09-49" in base_name:
        candidates.append(os.path.join("configs", "roi_chatgpt_09_49.json"))
    if "09_51" in base_name or "09-51" in base_name:
        candidates.append(os.path.join("configs", "roi_chatgpt_09_51.json"))
        
    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[0]


def process_and_annotate(img, detections, checker=None, roi_manager=None, show_roi: bool = True):
    """
    Vẽ kết quả phát hiện và phán quyết vi phạm (nếu có ROI) lên ảnh.
    Trả về ảnh đã vẽ nhãn và danh sách chi tiết các biển.
    """
    vis = img.copy()
    h, w = img.shape[:2]
    
    # 1. Vẽ lớp phủ ROI vỉa hè nếu có cấu hình
    has_roi = False
    if roi_manager and len(roi_manager.polygons) > 0:
        has_roi = True
        if show_roi:
            vis = roi_manager.draw_overlay(vis, alpha=0.30)
        
    details = []
    
    for idx, det in enumerate(detections, 1):
        box = det["box"]
        conf = det["conf"]
        x1, y1, x2, y2 = box
        base_x = int((x1 + x2) / 2)
        base_y = int(y2)
        
        is_violation = False
        status_text = "BIEN QUANG CAO"
        overlap_pct = 0.0
        
        if checker and has_roi:
            # Kiểm tra vi phạm trên toàn bộ các đa giác vỉa hè (Multi-ROI)
            res = checker.check_multi(box, roi_manager.polygons)
            is_violation = res["is_violation"]
            overlap_pct = res["overlap_pct"]
            if is_violation:
                status_text = f"VI PHAM ({overlap_pct:.0f}%)"
            elif res.get("is_base_inside", False):
                status_text = f"MEP VIA HE ({overlap_pct:.0f}%)"
            else:
                status_text = f"HOP LE ({conf*100:.0f}%)"
        else:
            status_text = f"bienquangcao {conf*100:.0f}%"
            
        details.append({
            "idx": idx,
            "box": box,
            "conf": conf,
            "base_pt": (base_x, base_y),
            "is_violation": is_violation,
            "overlap_pct": overlap_pct,
            "status_text": status_text
        })
        
        # Vẽ box bằng hàm chuẩn trong utils/visualizer.py
        draw_detection(vis, box, status_text, is_violation=is_violation)
        
    return vis, details


def test_images_batch(
    img_dir: str = "data/images",
    model_path: str = "models/best.pt",
    conf_thresh: float = 0.25,
    imgsz: int = 1280,
    output_dir: str = "data/images/output_test_v8",
    roi_path: str = None
):
    """Chạy kiểm thử hàng loạt trên toàn bộ ảnh trong thư mục và lưu ảnh kết quả."""
    if not os.path.exists(img_dir):
        print(f"[LỖI] Thư mục không tồn tại: {img_dir}")
        return False

    os.makedirs(output_dir, exist_ok=True)
    images = [f for f in sorted(os.listdir(img_dir)) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

    if not images:
        print(f"[CẢNH BÁO] Không tìm thấy ảnh nào trong thư mục: {img_dir}")
        return False

    print("=" * 75)
    print("      KIỂM THỬ MÔ HÌNH NHẬN DIỆN BIỂN QUẢNG CÁO (YOLOv8n v8)")
    print("=" * 75)
    print(f"[+] Trọng số mô hình : {model_path}")
    print(f"[+] Thư mục ảnh      : {os.path.abspath(img_dir)} ({len(images)} ảnh)")
    print(f"[+] Ngưỡng Conf / Size: conf={conf_thresh:.2f}, imgsz={imgsz}")
    print(f"[+] Thư mục lưu kết quả: {os.path.abspath(output_dir)}")
    
    checker = None
    default_roi_mgr = None
    if roi_path and os.path.exists(roi_path):
        print(f"[+] Nạp cấu hình ROI : {roi_path}")
        default_roi_mgr = ROIManager(roi_path)
        checker = ViolationChecker(threshold=0.30)
    print("-" * 75)

    detector = YOLODetector(model_path=model_path, conf_threshold=conf_thresh, imgsz=imgsz)
    
    total_detections = 0
    total_violations = 0
    total_time_ms = 0.0

    for idx, img_name in enumerate(images, start=1):
        img_path = os.path.join(img_dir, img_name)
        img = cv2.imread(img_path)
        if img is None:
            print(f"[!] Không thể đọc ảnh: {img_name}")
            continue

        h, w = img.shape[:2]
        
        # Tìm ROI riêng cho ảnh nếu không có roi_path cố định
        cur_roi_mgr = default_roi_mgr
        if cur_roi_mgr is None:
            custom_roi = get_default_roi_path_for_image(img_path)
            if os.path.exists(custom_roi):
                cur_roi_mgr = ROIManager(custom_roi)
                checker = ViolationChecker(threshold=0.30)

        # Đo thời gian suy luận
        t_start = time.perf_counter()
        detections = detector.detect(img)
        t_infer_ms = (time.perf_counter() - t_start) * 1000.0
        total_time_ms += t_infer_ms
        total_detections += len(detections)

        # Xử lý vẽ nhãn và ROI
        vis, details = process_and_annotate(img, detections, checker, cur_roi_mgr, show_roi=True)

        n_viol = sum(1 for d in details if d["is_violation"])
        total_violations += n_viol

        print(f"\n📸 [ẢNH {idx}/{len(images)}] {img_name} ({w}x{h})")
        print(f"   ⏱️  Thời gian suy luận: {t_infer_ms:.1f} ms | Số biển: {len(detections)} | Vi phạm vỉa hè: {n_viol}")
        
        for d in details:
            print(f"      • Biển #{d['idx']}: Box={d['box']} | Chân={d['base_pt']} | Conf={d['conf']*100:.1f}% | Nhãn: {d['status_text']}")

        # Lưu ảnh kết quả
        clean_name = f"v8_result_{idx}_{img_name.replace(' ', '_')}"
        out_path = os.path.join(output_dir, clean_name)
        cv2.imwrite(out_path, vis)
        print(f"   💾 Đã lưu kết quả tại: {out_path}")

    # Báo cáo tổng kết
    avg_time = total_time_ms / len(images) if images else 0
    print("\n" + "=" * 75)
    print("                    TỔNG KẾT THỰC NGHIỆM")
    print("=" * 75)
    print(f"  • Tổng số ảnh đã kiểm thử    : {len(images)} ảnh")
    print(f"  • Tổng số biển phát hiện     : {total_detections} biển")
    if checker:
        print(f"  • Tổng số biển vi phạm vỉa hè: {total_violations} biển")
    print(f"  • Thời gian xử lý trung bình : {avg_time:.1f} ms/ảnh (~{1000.0/max(avg_time, 1):.1f} FPS)")
    print(f"  • Toàn bộ ảnh đã được lưu tại: {os.path.abspath(output_dir)}")
    print("=" * 75)
    return True


def test_single_image(
    image_path: str,
    model_path: str = "models/best.pt",
    conf_thresh: float = 0.25,
    imgsz: int = 1280,
    output_dir: str = "data/images/output_test_v8",
    roi_path: str = None,
    show_gui: bool = False
):
    """Kiểm thử một ảnh đơn lẻ."""
    if not os.path.exists(image_path):
        print(f"[LỖI] Không tìm thấy file ảnh: {image_path}")
        return False

    detector = YOLODetector(model_path=model_path, conf_threshold=conf_thresh, imgsz=imgsz)
    img = cv2.imread(image_path)
    if img is None:
        print(f"[LỖI] Không thể đọc ảnh: {image_path}")
        return False

    h, w = img.shape[:2]

    # Nạp ROI
    roi_mgr = None
    checker = None
    effective_roi = roi_path if roi_path and os.path.exists(roi_path) else get_default_roi_path_for_image(image_path)
    if os.path.exists(effective_roi):
        print(f"[+] Áp dụng ROI: {effective_roi}")
        roi_mgr = ROIManager(effective_roi)
        checker = ViolationChecker(threshold=0.30)

    t0 = time.perf_counter()
    detections = detector.detect(img)
    infer_ms = (time.perf_counter() - t0) * 1000.0

    print("=" * 70)
    print(f"[+] Ảnh kiểm thử : {image_path} ({w}x{h})")
    print(f"[+] Thời gian AI : {infer_ms:.1f} ms")
    print(f"[+] Phát hiện    : {len(detections)} biển hiệu!")
    
    vis, details = process_and_annotate(img, detections, checker, roi_mgr, show_roi=True)
    for d in details:
        print(f"   • Biển #{d['idx']}: Box={d['box']} | Conf={d['conf']*100:.1f}% | Nhãn: {d['status_text']}")

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "result_" + os.path.basename(image_path).replace(' ', '_'))
    cv2.imwrite(out_path, vis)
    print(f"[OK] Đã lưu ảnh kết quả tại: {out_path}")
    print("=" * 70)

    if show_gui:
        try:
            window_name = f"Ket Qua AI - {os.path.basename(image_path)}"
            scale = min(1000.0 / w, 750.0 / h, 1.0)
            disp = cv2.resize(vis, (int(w * scale), int(h * scale)))
            print("Đang mở cửa sổ... Nhấn phím bất kỳ hoặc 'q' để đóng.")
            cv2.imshow(window_name, disp)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except cv2.error as e:
            print(f"[!] Không thể mở cửa sổ hiển thị: {e}")
            print(f">> Ảnh kết quả đã được lưu đầy đủ tại: {out_path}")
    return True


def browse_images_interactively(
    img_dir: str = "data/images",
    model_path: str = "models/best.pt",
    conf_thresh: float = 0.25,
    imgsz: int = 1280,
    roi_path: str = None
):
    """
    Mở cửa sổ đồ họa xem từng ảnh tương tác với bàn phím.
    Hỗ trợ nhấn 'r' để VẼ ROI VỈA HÈ TRỰC TIẾP BẰNG CHUỘT cho ảnh đang xem!
    """
    if not os.path.exists(img_dir):
        os.makedirs(img_dir, exist_ok=True)

    images = [f for f in sorted(os.listdir(img_dir)) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    if not images:
        print(f"[!] Thư mục {img_dir} chưa có ảnh.")
        return

    detector = YOLODetector(model_path=model_path, conf_threshold=conf_thresh, imgsz=imgsz)
    current_idx = 0
    total = len(images)
    show_roi = True

    print("=" * 75)
    print(f"DUYỆT ẢNH TƯƠNG TÁC & VẼ ROI: {img_dir} ({total} ảnh)")
    print("  • Phím 'r' hoặc 'R'   : MỞ CÔNG CỤ VẼ ROI BẰNG CHUỘT CHO ẢNH NÀY!")
    print("  • Phím 'v' hoặc 'V'   : BẬT / TẮT HIỂN THỊ LỚP PHỦ ROI VỈA HÈ")
    print("  • Phím 'd' hoặc SPACE : Xem ảnh tiếp theo (Next)")
    print("  • Phím 'a'           : Quay lại ảnh trước (Previous)")
    print("  • Phím 'q' hoặc ESC  : Thoát chương trình")
    print("=" * 75)

    window_name = "AI Signboard Inspector (Nhan 'r' de ve ROI, 'q' de thoat)"
    try:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    except cv2.error as e:
        print(f"[!] Không thể khởi tạo cửa sổ GUI: {e}")
        return

    checker = ViolationChecker(threshold=0.30)

    while True:
        img_name = images[current_idx]
        img_path = os.path.join(img_dir, img_name)
        img = cv2.imread(img_path)

        if img is not None:
            h, w = img.shape[:2]

            # Xác định file ROI cho ảnh này
            custom_roi_file = roi_path if roi_path and os.path.exists(roi_path) else get_default_roi_path_for_image(img_path)
            
            roi_mgr = None
            if os.path.exists(custom_roi_file):
                roi_mgr = ROIManager(custom_roi_file)

            detections = detector.detect(img)
            vis, details = process_and_annotate(img, detections, checker, roi_mgr, show_roi=show_roi)

            # Thống kê vi phạm
            n_viol = sum(1 for d in details if d["is_violation"])
            roi_status_str = f"ROI: {len(roi_mgr.polygons)} vung (Hien thi: {'BAT' if show_roi else 'TAT'})" if roi_mgr and len(roi_mgr.polygons) > 0 else "CHUA CO ROI (Nhan 'r' de ve chuot)"

            # Vẽ thanh trạng thái menu trên đầu ảnh
            cv2.rectangle(vis, (0, 0), (w, 55), (20, 20, 20), -1)
            cv2.line(vis, (0, 55), (w, 55), (0, 255, 255), 2)
            
            info_line1 = f"[{current_idx + 1}/{total}] {img_name[:28]} | Phat hien: {len(detections)} bien | Vi pham: {n_viol} | {roi_status_str}"
            info_line2 = "[r]: VE ROI CHUOT | [v]: Bat/Tat ROI | [d]/SPACE: Tiep | [a]: Lui | [q]: Thoat"
            cv2.putText(vis, info_line1, (15, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(vis, info_line2, (15, 46), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (180, 180, 180), 1, cv2.LINE_AA)

            scale = min(1100.0 / w, 780.0 / h, 1.0)
            disp = cv2.resize(vis, (int(w * scale), int(h * scale)))
            try:
                cv2.imshow(window_name, disp)
            except cv2.error:
                break

        key = cv2.waitKey(0) & 0xFF
        
        # Thoát
        if key == ord('q') or key == 27:
            break
            
        # Sang ảnh tiếp
        elif key == ord('d') or key == 32:
            current_idx = (current_idx + 1) % total
            
        # Lùi ảnh
        elif key == ord('a'):
            current_idx = (current_idx - 1 + total) % total
            
        # Bật/Tắt hiển thị ROI
        elif key == ord('v') or key == ord('V'):
            show_roi = not show_roi
            print(f"[*] Trạng thái hiển thị ROI: {'BẬT' if show_roi else 'TẮT'}")

        # VẼ ROI TRỰC TIẾP BẰNG CHUỘT CHO ẢNH NÀY
        elif key == ord('r') or key == ord('R'):
            target_roi_path = roi_path if roi_path else get_default_roi_path_for_image(img_path)
            print("\n" + "=" * 65)
            print(f"[ROI DRAWER] Đang mở công cụ vẽ đa giác vỉa hè cho: {img_name}")
            print(f"[ROI DRAWER] File cấu hình sẽ lưu tại: {target_roi_path}")
            print("  • Click CHUỘT TRÁI để chấm các đỉnh vỉa hè")
            print("  • Click CHUỘT PHẢI để xóa điểm (Undo)")
            print("  • Nhấn 'n' để thêm vỉa hè bên kia đường (Multi-ROI)")
            print("  • Nhấn 's' để LƯU và 'q' để quay lại")
            print("=" * 65)
            
            # Đóng tạm cửa sổ inspector
            cv2.destroyAllWindows()
            
            # Mở công cụ vẽ ROI
            run_roi_tool(img_path, target_roi_path)
            
            # Mở lại cửa sổ inspector
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            print("[*] Đã cập nhật xong ROI! Đang tải lại khung hình với vùng vỉa hè mới...")

    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kiểm thử mô hình YOLOv8n v8 & Quản lý ROI vỉa hè trên ảnh")
    parser.add_argument("--dir", type=str, default="data/images", help="Thư mục chứa ảnh cần kiểm thử")
    parser.add_argument("--image", type=str, default=None, help="Đường dẫn đến một ảnh cụ thể")
    parser.add_argument("--model", type=str, default="models/best.pt", help="Đường dẫn trọng số mô hình")
    parser.add_argument("--conf", type=float, default=0.25, help="Ngưỡng độ tin cậy Confidence (0.0 - 1.0)")
    parser.add_argument("--imgsz", type=int, default=1280, help="Kích thước cạnh ảnh suy luận (mặc định 1280)")
    parser.add_argument("--output-dir", type=str, default="data/images/output_test_v8", help="Thư mục lưu ảnh kết quả")
    parser.add_argument("--roi", type=str, default=None, help="Tùy chọn file JSON cấu hình ROI vỉa hè để kiểm tra vi phạm")
    parser.add_argument("--gui", action="store_true", help="Bật giao diện xem tương tác bằng phím bấm")

    args = parser.parse_args()

    if args.gui:
        if args.image:
            test_single_image(
                image_path=args.image,
                model_path=args.model,
                conf_thresh=args.conf,
                imgsz=args.imgsz,
                output_dir=args.output_dir,
                roi_path=args.roi,
                show_gui=True
            )
        else:
            browse_images_interactively(
                img_dir=args.dir,
                model_path=args.model,
                conf_thresh=args.conf,
                imgsz=args.imgsz,
                roi_path=args.roi
            )
    else:
        if args.image:
            test_single_image(
                image_path=args.image,
                model_path=args.model,
                conf_thresh=args.conf,
                imgsz=args.imgsz,
                output_dir=args.output_dir,
                roi_path=args.roi,
                show_gui=False
            )
        else:
            test_images_batch(
                img_dir=args.dir,
                model_path=args.model,
                conf_thresh=args.conf,
                imgsz=args.imgsz,
                output_dir=args.output_dir,
                roi_path=args.roi
            )
