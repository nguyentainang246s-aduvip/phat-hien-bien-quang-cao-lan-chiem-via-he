import os
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

items = {
    'NHOM_0': {
        'title': 'NHÓM 0: TỔNG QUAN ĐỀ TÀI, CẤU HÌNH HỆ THỐNG & ĐIỂM VÀO ĐIỀU HÀNH',
        'description': 'Tóm tắt bài toán, căn cứ pháp lý Nghị định 168/2024/NĐ-CP, kiến trúc 5 tầng, cấu hình chuẩn settings.yaml, điểm vào điều hành main.py và module suy luận YOLO ONNX detector.py.',
        'files': [
            ('PROJECT_ESSENTIALS_FOR_AI.txt', 'Hồ sơ bản chất kỹ thuật, cơ sở toán học, kiến trúc 5 tầng và ground truth chuẩn 16 đối tượng'),
            ('configs/settings.yaml', 'Tệp cấu hình hệ thống trung tâm (ngưỡng tin cậy, model path, frame skip, camera, vỉa hè)'),
            ('main.py', 'Điểm vào điều hành trung tâm (Unified Entry Point) hỗ trợ cả 4 chế độ: Monitor, Dashboard, ROI, Benchmark'),
            ('detection/detector.py', 'Tầng suy luận mô hình phát hiện vật thể YOLOv8 ONNX Runtime CPU')
        ]
    },
    'NHOM_1': {
        'title': 'NHÓM 1: BẮT BUỘC (ĐỂ CHỐT ĐIỂM TIÊU CHÍ 2 VÀ 4)',
        'description': 'Kiểm tra logic check_multi, chân đế tiếp đất, dung sai 15px, đa giác ROI, kịch bản đánh giá video, ground truth và ByteTrack wrapper.',
        'files': [
            ('violation/checker.py', 'Logic check_multi: overlap, 3 điểm chân đế, dung sai 15 px, xử lý nhiều ROI'),
            ('evaluation/evaluate_videos.py', 'Cách chạy pipeline trên clip, truyền timestamp video (thay vì time.time), tracks_summary, tính FP, Bipartite Hungarian Matching'),
            ('configs/video_ground_truth.json', 'Cấu trúc GT, expected_track_id, 16 đối tượng (14 dương tính, 2 âm tính)'),
            ('evaluation/sweep_threshold.py', 'Thực nghiệm sweep tìm ngưỡng overlap tối ưu (30%)'),
            ('tracking/tracker.py', 'Wrapper YOLO + ByteTrack, tiền xử lý, hậu xử lý, xử lý track_id = -1'),
            ('tracking/verifier.py', 'Bộ xác minh chuỗi thời gian, Perspective-Adaptive Stationary Check, Cooldown')
        ]
    },
    'NHOM_2': {
        'title': 'NHÓM 2: QUAN TRỌNG (ĐỘ ỔN ĐỊNH, TRIỂN KHAI THỰC TẾ)',
        'description': 'Kiểm tra độ tin cậy kết nối RTSP, auto-scale ROI, lưu ảnh bằng chứng (watermark & face blur), cơ sở dữ liệu SQLite, requirements và benchmark.',
        'files': [
            ('camera/stream_reader.py', 'RTSP reconnect, flush buffer đa luồng, xử lý read() thất bại, giải phóng tài nguyên'),
            ('camera/video_reader.py', 'Đọc video offline mô phỏng khung hình'),
            ('roi/roi_manager.py', 'validate_resolution, auto-scale tọa độ ROI theo độ phân giải, lưu/đọc JSON, draw_overlay'),
            ('evidence/saver.py', 'Lưu ảnh vi phạm, gắn watermark tem pháp lý, làm mờ khuôn mặt (Face Blurring) bằng Haar Cascade'),
            ('database/db.py', 'Schema SQLite, SQL tham số hóa chống SQL Injection, is_duplicate_violation, lọc theo ngày'),
            ('requirements.txt', 'Pin cứng phiên bản thư viện đảm bảo 100% tái hiện môi trường'),
            ('evaluation/benchmark.py', 'Đo FPS, End-to-end Latency, tự động đọc cấu hình phần cứng CPU/RAM/OS')
        ]
    },
    'NHOM_3': {
        'title': 'NHÓM 3: BỔ SUNG & HOÀN THIỆN HỆ THỐNG (NẾU CÒN DƯ SỨC)',
        'description': 'Kiểm tra Web Dashboard Human-in-the-Loop, 10 bài unit test tự động, công cụ ROI Drawer, cấu hình huấn luyện và báo cáo ngưỡng.',
        'files': [
            ('dashboard/web_app.py', 'Web Dashboard giám sát, duyệt hồ sơ Human-in-the-Loop, lọc vi phạm theo ngày, bind host an toàn'),
            ('tests/test_violation_checker.py', 'Unit test thuật toán kiểm tra vi phạm đa giác & chân đế'),
            ('tests/test_temporal_verifier.py', 'Unit test bộ xác minh chuỗi thời gian & thích ứng phối cảnh'),
            ('tests/test_stream_reader.py', 'Unit test StreamReader xử lý lỗi RTSP'),
            ('tests/test_tracker.py', 'Unit test tracker bám vết đối tượng'),
            ('tests/test_evidence_saver.py', 'Unit test lưu bằng chứng & watermark'),
            ('tests/test_database.py', 'Unit test thao tác cơ sở dữ liệu SQLite'),
            ('tests/test_benchmark.py', 'Unit test bộ đo benchmark'),
            ('tests/test_modules.py', 'Unit test tích hợp các module'),
            ('tests/test_detector.py', 'Unit test tầng phát hiện YOLO ONNX'),
            ('tests/test_main_cli.py', 'Unit test CLI và argument parsing'),
            ('roi_drawer.py', 'Công cụ GUI OpenCV vẽ và hiệu chỉnh đa giác vỉa hè'),
            ('test_on_image.py', 'Script kiểm thử mô hình và thuật toán trên ảnh tĩnh'),
            ('utils/fps_tracker.py', 'Bộ tính toán FPS làm mượt thời gian thực'),
            ('utils/visualizer.py', 'Bộ vẽ bounding box, trạng thái và tem vi phạm'),
            ('scripts/train_colab.py', 'Script huấn luyện mô hình YOLOv8 trên Google Colab'),
            ('datasets/v8/data.yaml', 'Cấu hình tập dữ liệu YOLOv8 (train/val/test, 1 class billboard)'),
            ('reports/threshold_sweep_report.md', 'Báo cáo khoa học phân tích số liệu thực nghiệm chọn ngưỡng 30%')
        ]
    }
}

out_all = 'MA_NGUON_TONG_HOP_GUI_REVIEW.txt'
out_n1 = 'MA_NGUON_NHOM_1_BAT_BUOC.txt'
out_n2 = 'MA_NGUON_NHOM_2_QUAN_TRONG.txt'
out_n3 = 'MA_NGUON_NHOM_3_BO_SUNG.txt'

def generate_header():
    return '''# ==============================================================================
# HỒ SƠ TỔNG HỢP TOÀN BỘ MÃ NGUỒN PHỤC VỤ ĐÁNH GIÁ & CHẤM ĐIỂM ĐỒ ÁN TỐT NGHIỆP
# Đề tài: Hệ thống giám sát và phát hiện biển quảng cáo/biển hiệu lấn chiếm vỉa hè
# Sinh viên: Nguyễn Đức Tài Năng — MSSV: 20224083
# Ngành: Công nghệ Thông tin / Khoa học Máy tính (Đại học Bách Khoa Hà Nội)
#
# DANH MỤC CÁC PHẦN:
# - NHÓM 0: TỔNG QUAN ĐỀ TÀI, CẤU HÌNH TOÀN CỤC & ĐIỂM VÀO ĐIỀU HÀNH (main.py, settings.yaml, detector.py, essentials)
# - NHÓM 1: BẮT BUỘC (Logic Overlap, Chân đế tiếp đất, Temporal Verifier, Hungarian Evaluation, GT)
# - NHÓM 2: QUAN TRỌNG (RTSP StreamReader, ROIManager, Evidence Saver, SQLite DB, Benchmark)
# - NHÓM 3: BỔ SUNG (Web Dashboard Human-in-the-Loop, 10 Bộ Unit Tests, Training config, Reports)
# ==============================================================================

'''

def dump_group(group_key):
    grp = items[group_key]
    lines = []
    lines.append('=' * 80 + '\n')
    lines.append(f">>> {grp['title']}\n")
    lines.append(f">>> Ý nghĩa: {grp['description']}\n")
    lines.append('=' * 80 + '\n\n')
    
    for fpath, note in grp['files']:
        if not os.path.exists(fpath):
            lines.append(f'[WARNING: FILE {fpath} KHONG TON TAI]\n\n')
            continue
        lines.append('=' * 80 + '\n')
        lines.append(f'FILE: {fpath}\n')
        lines.append(f'MỤC ĐÍCH KIỂM TRA: {note}\n')
        lines.append('=' * 80 + '\n\n')
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            lines.append(content)
        except Exception as e:
            lines.append(f'Error reading file: {e}')
        lines.append('\n\n')
    return ''.join(lines)

def main():
    print('[*] Đang xuất mã nguồn ra các tệp phục vụ kiểm tra...')
    c0 = dump_group('NHOM_0')
    c1 = dump_group('NHOM_1')
    c2 = dump_group('NHOM_2')
    c3 = dump_group('NHOM_3')

    # 1. Ghi tệp riêng Nhóm 1
    with open(out_n1, 'w', encoding='utf-8') as f:
        f.write(generate_header() + c1)

    # 2. Ghi tệp riêng Nhóm 2
    with open(out_n2, 'w', encoding='utf-8') as f:
        f.write(generate_header() + c2)

    # 3. Ghi tệp riêng Nhóm 3
    with open(out_n3, 'w', encoding='utf-8') as f:
        f.write(generate_header() + c3)

    # 4. Ghi tệp gộp tất cả (Bao gồm cả Nhóm 0 + Nhóm 1 + Nhóm 2 + Nhóm 3)
    with open(out_all, 'w', encoding='utf-8') as f:
        f.write(generate_header() + c0 + '\n\n' + c1 + '\n\n' + c2 + '\n\n' + c3)

    print('[OK] Đã hoàn thành xuất tất cả các tệp!')
    for p in [out_n1, out_n2, out_n3, out_all]:
        sz = os.path.getsize(p)
        ln = len(open(p, 'r', encoding='utf-8').readlines())
        print(f'  + {p:35} | {ln:5} lines | {sz/1024:6.1f} KB')

if __name__ == '__main__':
    main()
