"""
Script kiểm thử các kịch bản thực tế của Module violation.ViolationChecker (Task 18)
"""
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath("."))

from violation import ViolationChecker
from roi import ROIManager

def test_scenarios():
    print("=" * 65)
    print("KIỂM THỬ THUẬT TOÁN QUYẾT ĐỊNH VI PHẠM (TASK 18)")
    print("=" * 65)
    
    # Nạp vùng vỉa hè mẫu
    roi = ROIManager("configs/roi_camera1.json")
    print(f"[+] Vùng vỉa hè: {roi.camera_id} ({len(roi.points)} đỉnh)")
    checker = ViolationChecker(threshold=0.30)
    
    # Kịch bản 1: Biển đặt chình ình giữa vỉa hè (Tọa độ y: 760 -> 920)
    box_violation = (150, 760, 450, 920)
    res1 = checker.check(box_violation, roi.points)
    print("\n[KỊCH BẢN 1] Biển đặt giữa vỉa hè:")
    print(f"  Chân đế: {res1['base_point']} | Lấn chiếm: {res1['overlap_pct']}% | Vi phạm: {res1['is_violation']}")
    assert res1['is_violation'] == True, "Lỗi: Kịch bản 1 phải là VI PHẠM!"
    print("  -> ĐÁNH GIÁ: ĐẠT CHUẨN [VI PHẠM]")
    
    # Kịch bản 2: Biển đặt trong nhà, chỉ liếm nhẹ 5% vào vỉa hè do góc nhìn
    box_edge = (150, 680, 450, 755)
    res2 = checker.check(box_edge, roi.points)
    print("\n[KỊCH BẢN 2] Biển đặt trong nhà chạm mép nhẹ:")
    print(f"  Chân đế: {res2['base_point']} | Lấn chiếm: {res2['overlap_pct']}% | Vi phạm: {res2['is_violation']}")
    assert res2['is_violation'] == False, "Lỗi: Kịch bản 2 phải là HỢP LỆ (dưới ngưỡng)!"
    print("  -> ĐÁNH GIÁ: ĐẠT CHUẨN [HỢP LỆ]")

    # Kịch bản 3: Biển đặt hoàn toàn ngoài vỉa hè (Dưới lòng đường hoặc trên ban công)
    box_outside = (200, 200, 400, 400)
    res3 = checker.check(box_outside, roi.points)
    print("\n[KỊCH BẢN 3] Biển trên cao / ngoài vỉa hè:")
    print(f"  Chân đế: {res3['base_point']} | Lấn chiếm: {res3['overlap_pct']}% | Vi phạm: {res3['is_violation']}")
    assert res3['is_violation'] == False, "Lỗi: Kịch bản 3 phải là HỢP LỆ!"
    print("  -> ĐÁNH GIÁ: ĐẠT CHUẨN [HỢP LỆ]")
    
    # Kịch bản 4: Xử lý ngoại lệ hình học Shapely (Error Path Resilience - N2)
    from unittest.mock import patch
    print("\n[KỊCH BẢN 4] Kiểm thử đường lỗi ngoại lệ hình học Shapely:")
    with patch("shapely.geometry.Polygon", side_effect=RuntimeError("Lỗi cấu trúc đa giác Shapely mô phỏng")):
        res4 = checker.check(box_violation, roi.points)
        print(f"  Kết quả khi Shapely ném lỗi: Overlap = {res4['overlap_pct']}% | Vi phạm = {res4['is_violation']}")
        assert res4['overlap_ratio'] == 0.0, "Khi hình học lỗi, overlap_ratio phải là 0.0"
        assert res4['is_violation'] is False, "Khi hình học lỗi, không được kết luận vi phạm bừa bãi"
    print("  -> ĐÁNH GIÁ: ĐẠT CHUẨN [BẮT NGOẠI LỆ AN TOÀN - KHÔNG SẬP CHƯƠNG TRÌNH]")

    print("=" * 65)
    print(">> KẾT QUẢ: TẤT CẢ 4 KỊCH BẢN ĐỀU VƯỢT QUA 100%!")
    print(">> MODULE VIOLATION CHECKER HOẠT ĐỘNG HOÀN TOÀN CHÍNH XÁC.")
    print("=" * 65)
    return True

if __name__ == "__main__":
    success = test_scenarios()
    sys.exit(0 if success else 1)
