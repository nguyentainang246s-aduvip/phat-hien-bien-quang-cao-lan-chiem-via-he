"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Computer Vision & Fixed Camera Surveillance
TASK: 06 - Công cụ thiết lập và lưu Đa giác Vỉa hè (Multi-ROI) ra file JSON
==============================================================================
Cách sử dụng:
  1. Vẽ ROI tuần tự cho TẤT CẢ các ảnh trong thư mục data/images:
     python roi_drawer.py --all
     python roi_drawer.py --dir data/images

  2. Vẽ ROI cho 1 ảnh cụ thể:
     python roi_drawer.py "data/images/ChatGPT Image Sep 30, 2026, 09_49_42 PM.png"
     python roi_drawer.py "data/images/ChatGPT Image Sep 30, 2026, 09_51_43 PM.png"
     python roi_drawer.py "data/images/Screenshot 2026-09-30 214856.png"

Thao tác chuột & bàn phím:
  • Click CHUỘT TRÁI : Chấm các đỉnh của vỉa hè (tối thiểu 3 điểm)
  • Click CHUỘT PHẢI : Xóa điểm vừa chấm (Undo)
  • Nhấn phím 'n'    : Chốt vỉa hè hiện tại, vẽ tiếp vỉa hè khác (Multi-ROI hai bên đường)
  • Nhấn phím 's'    : LƯU TẤT CẢ VÙNG VỈA HÈ RA FILE JSON
  • Nhấn phím 'c'    : Xóa làm lại
  • Nhấn phím 'q'    : Thoát / Chuyển sang ảnh tiếp theo
==============================================================================
"""

import os
import sys
import json
import time
import argparse
import cv2
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Danh sách tất cả các đa giác vỉa hè đã chốt: [ [[x, y], ...], [[x, y], ...] ]
all_polygons = []
# Đa giác hiện tại đang chấm dở
current_polygon = []
CONFIG_DIR = "configs"
CONFIG_FILE = os.path.join(CONFIG_DIR, "roi_camera1.json")


def get_default_config_for_source(source_path: str) -> str:
    """Tự động sinh đường dẫn file JSON ROI chuẩn tương ứng với tên file nguồn."""
    base_name = os.path.splitext(os.path.basename(source_path))[0]
    clean_name = base_name.replace(" ", "_").replace(",", "").replace("-", "_")
    return os.path.join(CONFIG_DIR, f"roi_{clean_name}.json")


def mouse_handler(event, x, y, flags, param):
    """Bắt sự kiện click chuột để thêm đỉnh hoặc xóa đỉnh của đa giác."""
    global current_polygon
    
    # Click chuột trái: Thêm 1 đỉnh mới cho đa giác đang vẽ
    if event == cv2.EVENT_LBUTTONDOWN:
        current_polygon.append([x, y])
        print(f"[ĐỈNH MỚI] Vỉa hè #{len(all_polygons)+1} - Đỉnh #{len(current_polygon)}: ({x}, {y})")
        
    # Click chuột phải: Xóa đỉnh gần nhất (Undo)
    elif event == cv2.EVENT_RBUTTONDOWN:
        if current_polygon:
            removed = current_polygon.pop()
            print(f"[UNDO] Đã xóa đỉnh: {removed}. Còn lại: {len(current_polygon)} đỉnh.")
        elif all_polygons:
            current_polygon = all_polygons.pop()
            print(f"[UNDO] Mở lại Vỉa hè #{len(all_polygons)+1} để sửa tiếp.")


def draw_multi_roi_overlay(frame, completed_polys, active_pts):
    """
    Vẽ tất cả các đa giác vỉa hè (đã chốt và đang vẽ) với lớp phủ bán trong suốt.
    """
    vis_frame = frame.copy()
    overlay = vis_frame.copy()

    # 1. Vẽ các vỉa hè ĐÃ CHỐT trước đó (Xanh cyan / Vàng)
    for idx, poly in enumerate(completed_polys):
        if len(poly) >= 3:
            pts_arr = np.array(poly, np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(overlay, [pts_arr], (0, 200, 255))
            cv2.polylines(vis_frame, [pts_arr], isClosed=True, color=(0, 255, 255), thickness=2)
            first_pt = tuple(poly[0])
            cv2.putText(vis_frame, f"[VIA HE #{idx+1}]", (first_pt[0] + 5, max(25, first_pt[1] - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2, cv2.LINE_AA)

    # 2. Vẽ vỉa hè ĐANG CHẤM DỞ
    if len(active_pts) > 0:
        for idx, (px, py) in enumerate(active_pts):
            cv2.circle(vis_frame, (px, py), 6, (0, 0, 255), -1)      # Chấm đỏ
            cv2.circle(vis_frame, (px, py), 7, (255, 255, 255), 2)  # Viền trắng
            cv2.putText(vis_frame, f"P{idx+1}", (px + 8, py - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

        if len(active_pts) >= 3:
            pts_arr = np.array(active_pts, np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(overlay, [pts_arr], (255, 180, 0))
            cv2.polylines(vis_frame, [pts_arr], isClosed=True, color=(0, 200, 255), thickness=2)
        elif len(active_pts) == 2:
            cv2.line(vis_frame, tuple(active_pts[0]), tuple(active_pts[1]), (0, 200, 255), 2)

    cv2.addWeighted(overlay, 0.35, vis_frame, 0.65, 0, vis_frame)
    return vis_frame


def save_roi_config(polygons_list, width, height, camera_id="camera_01", target_path=None):
    """Lưu danh sách tất cả các đa giác vỉa hè ra file JSON chuẩn."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    out_file = target_path if target_path else CONFIG_FILE
    
    total_pts = sum(len(p) for p in polygons_list)
    data = {
        "camera_id": camera_id,
        "description": "Vung via he co dinh (Ho tro Multi-ROI: Via he trai, phai)",
        "resolution": {"width": width, "height": height},
        "total_regions": len(polygons_list),
        "total_points": total_pts,
        "polygons": polygons_list,
        "polygon_points": polygons_list[0] if polygons_list else [],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print("=" * 65)
    print(f"[THÀNH CÔNG] ĐÃ LƯU CẤU HÌNH {len(polygons_list)} VÙNG VỈA HÈ VÀO: {out_file}")
    for i, p in enumerate(polygons_list):
        print(f"  • Vỉa hè #{i+1} : {len(p)} đỉnh -> {p}")
    print("=" * 65)
    return out_file


def run_roi_tool(source_path: str = None, output_config: str = None):
    """Khởi chạy công cụ vẽ ROI tương tác bằng chuột cho 1 ảnh hoặc 1 video."""
    global all_polygons, current_polygon, CONFIG_FILE

    all_polygons.clear()
    current_polygon.clear()

    if source_path is None or not os.path.exists(source_path):
        video_dir = "data/videos"
        files = [f for f in os.listdir(video_dir) if f.lower().endswith(('.mp4', '.avi', '.mov'))] if os.path.exists(video_dir) else []
        source_path = os.path.join(video_dir, files[0]) if files else "data/videos/sample_cctv.mp4"

    if output_config:
        CONFIG_FILE = output_config
    else:
        CONFIG_FILE = get_default_config_for_source(source_path)

    os.makedirs(os.path.dirname(CONFIG_FILE) or ".", exist_ok=True)

    # Nạp cấu hình ROI đã có trước đó nếu file tồn tại
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
                if "polygons" in saved_data and isinstance(saved_data["polygons"], list):
                    all_polygons = [p for p in saved_data["polygons"] if len(p) >= 3]
                elif "polygon_points" in saved_data and len(saved_data["polygon_points"]) >= 3:
                    all_polygons = [saved_data["polygon_points"]]
            if all_polygons:
                print(f"[TẢI LẠI] Đã nạp {len(all_polygons)} vùng vỉa hè đã lưu từ trước tại: {CONFIG_FILE}")
        except Exception:
            pass

    is_image = source_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))

    if is_image:
        base_frame = cv2.imread(source_path)
        if base_frame is None:
            print(f"[LỖI] Không thể đọc ảnh: {source_path}")
            return False
        height, width = base_frame.shape[:2]
    else:
        cap = cv2.VideoCapture(source_path)
        if not cap.isOpened():
            print(f"[LỖI] Không thể mở video: {source_path}")
            return False
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ret, base_frame = cap.read()
        cap.release()
        if not ret or base_frame is None:
            print("[LỖI] Không thể đọc frame từ video.")
            return False

    window_name = f"ROI Tool - {os.path.basename(source_path)} (Nhan 's' de luu, 'q' de thoat)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, min(width, 1050), min(height, 750))
    cv2.setMouseCallback(window_name, mouse_handler)

    print("=" * 70)
    print("CÔNG CỤ THIẾT LẬP ĐA VÙNG VỈA HÈ (MULTI-ROI TOOL)")
    print(f"  Nguồn dữ liệu : {source_path} ({width}x{height})")
    print(f"  File cấu hình : {CONFIG_FILE}")
    print("=" * 70)
    print("HƯỚNG DẪN SỬ DỤNG:")
    print(" 1. Click CHUỘT TRÁI : Chấm các đỉnh của vỉa hè (tối thiểu 3 điểm)")
    print(" 2. Click CHUỘT PHẢI : Xóa điểm vừa bấm (Undo)")
    print(" 3. Nhấn phím 'n'    : CHỐT VỈA HÈ HIỆN TẠI VÀ CHUYỂN SANG VẼ VỈA HÈ TIẾP THEO")
    print(" 4. Nhấn phím 's'    : LƯU TẤT CẢ CÁC VÙNG VỈA HÈ VÀO FILE CONFIG JSON")
    print(" 5. Nhấn phím 'c'    : Xóa đa giác hiện tại để vẽ lại")
    print(" 6. Nhấn phím 'q'    : Thoát công cụ (hoặc chuyển sang ảnh tiếp theo)")
    print("-" * 70)

    has_saved = False

    while True:
        display_frame = draw_multi_roi_overlay(base_frame, all_polygons, current_polygon)
        
        info_text = f"Da chot: {len(all_polygons)} via he | Dang ve: {len(current_polygon)} pts | [N] Them via he | [S] Luu | [Q] Thoat"
        cv2.rectangle(display_frame, (0, 0), (width, 40), (20, 20, 20), -1)
        cv2.putText(display_frame, info_text, (15, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow(window_name, display_frame)
        key = cv2.waitKey(30) & 0xFF

        # Phím 'n' hoặc 'N': Chốt vỉa hè hiện tại, chuyển sang vẽ vỉa hè mới
        if key == ord('n') or key == ord('N'):
            if len(current_polygon) < 3:
                print("[CẢNH BÁO] Vỉa hè hiện tại chưa đủ 3 điểm để chốt!")
            else:
                all_polygons.append(list(current_polygon))
                current_polygon.clear()
                print(f"[+] ĐÃ CHỐT VỈA HÈ #{len(all_polygons)}! Hãy tiếp tục chấm chuột để vẽ vỉa hè tiếp theo.")

        # Phím 's' hoặc 'S': Lưu cấu hình JSON
        elif key == ord('s') or key == ord('S'):
            to_save = list(all_polygons)
            if len(current_polygon) >= 3:
                to_save.append(list(current_polygon))

            if not to_save:
                print("[CẢNH BÁO] Chưa có vỉa hè nào có từ 3 điểm trở lên để lưu!")
            else:
                cam_name = os.path.splitext(os.path.basename(source_path))[0]
                save_roi_config(to_save, width, height, camera_id=cam_name, target_path=CONFIG_FILE)
                has_saved = True
                print("[THÔNG BÁO] Đã lưu thành công. Bạn có thể nhấn 'q' để tiếp tục.")

        # Phím 'c' hoặc 'C': Xóa
        elif key == ord('c') or key == ord('C'):
            if current_polygon:
                current_polygon.clear()
                print("[THÔNG BÁO] Đã xóa điểm của vỉa hè đang vẽ dở.")
            elif all_polygons:
                all_polygons.clear()
                print("[THÔNG BÁO] Đã xóa toàn bộ tất cả các vỉa hè.")

        # Phím 'q' hoặc ESC: Thoát
        elif key == ord('q') or key == 27:
            # Tự động lưu nếu người dùng đã vẽ xong mà chưa bấm 's'
            if not has_saved and len(current_polygon) >= 3:
                all_polygons.append(list(current_polygon))
                cam_name = os.path.splitext(os.path.basename(source_path))[0]
                save_roi_config(all_polygons, width, height, camera_id=cam_name, target_path=CONFIG_FILE)
            break

    cv2.destroyAllWindows()
    return True


def run_batch_roi_drawer(img_dir: str = "data/images"):
    """Duyệt lần lượt tất cả các ảnh trong thư mục để người dùng vẽ ROI liên tục."""
    if not os.path.exists(img_dir):
        print(f"[LỖI] Không tìm thấy thư mục: {img_dir}")
        return

    images = [f for f in sorted(os.listdir(img_dir)) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    if not images:
        print(f"[!] Không có ảnh trong {img_dir}")
        return

    print("=" * 70)
    print(f"BẮT ĐẦU VẼ ROI TUẦN TỰ CHO {len(images)} ẢNH TRONG '{img_dir}'")
    print("  • Mỗi ảnh sẽ được mở lên lần lượt.")
    print("  • Bạn chấm chuột vẽ vỉa hè -> Nhấn 's' để lưu -> Nhấn 'q' để sang ảnh kế tiếp!")
    print("=" * 70)

    for idx, img_name in enumerate(images, start=1):
        img_path = os.path.join(img_dir, img_name)
        cfg_path = get_default_config_for_source(img_path)
        print(f"\n👉 [ẢNH {idx}/{len(images)}]: {img_name}")
        print(f"   Lưu file cấu hình tại: {cfg_path}")
        run_roi_tool(img_path, cfg_path)

    print("\n" + "=" * 70)
    print("✅ ĐÃ HOÀN TẤT VẼ ROI CHO TẤT CẢ CÁC ẢNH!")
    print("Bây giờ bạn có thể chạy: python test_on_image.py --gui để xem kết quả kiểm tra vi phạm!")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Công cụ vẽ đa giác ROI vỉa hè bằng chuột")
    parser.add_argument("source", nargs="?", default=None, help="Ảnh hoặc video cụ thể cần vẽ ROI")
    parser.add_argument("output", nargs="?", default=None, help="Đường dẫn file JSON cấu hình đích")
    parser.add_argument("--all", action="store_true", help="Duyệt lần lượt tất cả các ảnh trong data/images")
    parser.add_argument("--dir", type=str, default="data/images", help="Thư mục chứa các ảnh cần vẽ ROI tuần tự")

    args = parser.parse_args()

    if args.all or (args.source is None and len(sys.argv) == 1):
        run_batch_roi_drawer(args.dir)
    elif args.source and os.path.isdir(args.source):
        run_batch_roi_drawer(args.source)
    else:
        run_roi_tool(args.source, args.output)
