# Archive — Phiên bản lịch sử (Historical Versions)

Thư mục này chứa các file entry point **ĐÃ BỊ THAY THẾ** bởi `main.py` (Version 2.0).

**KHÔNG SỬ DỤNG** các file trong thư mục này để demo hoặc chạy hệ thống.

| File | Mô tả | Lý do archive |
| :--- | :--- | :--- |
| `main_mvp.py` | Phiên bản MVP đầu tiên (V1.0) | Thiếu Temporal Verification, thiếu evidence saving |
| `main_temporal.py` | Phiên bản thêm Temporal Verifier (V1.5) | Đã được gộp vào `main.py` V2.0 thống nhất |

## Entry point chính thức: `main.py` (gốc thư mục dự án)

```powershell
python main.py --mode monitor --source data/videos/sample.mp4
```
