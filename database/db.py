"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Database Management & Violation Records
TASK: 24 - Xây dựng Module database/db.py (Quản lý CSDL SQLite)
==============================================================================
"""

import os
import sqlite3
from datetime import datetime


class ViolationDatabase:
    """
    Quản lý cơ sở dữ liệu SQLite lưu trữ lịch sử các vụ vi phạm lấn chiếm vỉa hè.
    Hỗ trợ truy vấn nhanh theo Camera, Thời gian và phục vụ hiển thị lên Web Dashboard.
    """
    def __init__(self, db_path: str = "data/surveillance.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self.init_tables()

    def get_connection(self):
        """Tạo kết nối SQLite với Row Factory để truy vấn dạng dict và kích hoạt WAL Mode."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
        except Exception:
            pass
        return conn

    def init_tables(self):
        """Khởi tạo bảng violations và index nếu chưa tồn tại."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    camera_id TEXT NOT NULL,
                    track_id INTEGER NOT NULL,
                    timestamp DATETIME NOT NULL,
                    violation_type TEXT DEFAULT 'lan_chiem_via_he',
                    confidence REAL,
                    overlap_pct REAL,
                    bbox_x1 INTEGER,
                    bbox_y1 INTEGER,
                    bbox_x2 INTEGER,
                    bbox_y2 INTEGER,
                    sidewalk_index INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'pending',
                    full_image_path TEXT,
                    crop_image_path TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_camera ON violations(camera_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON violations(timestamp)")
            
            # Tự động kiểm tra và thêm từng cột mới nếu bảng đã tồn tại từ phiên bản cũ
            cursor.execute("PRAGMA table_info(violations)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            new_columns = [
                ("bbox_x1", "INTEGER"),
                ("bbox_y1", "INTEGER"),
                ("bbox_x2", "INTEGER"),
                ("bbox_y2", "INTEGER"),
                ("sidewalk_index", "INTEGER DEFAULT 1"),
                ("status", "TEXT DEFAULT 'pending'"),
                ("reviewed_by", "TEXT DEFAULT NULL"),
                ("dismiss_reason", "TEXT DEFAULT NULL"),
                ("reviewed_at", "DATETIME DEFAULT NULL")
            ]
            
            for col_name, col_type in new_columns:
                if col_name not in existing_columns:
                    cursor.execute(f"ALTER TABLE violations ADD COLUMN {col_name} {col_type}")

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON violations(status)")
                
            conn.commit()
        finally:
            conn.close()

    def insert_violation(self, camera_id: str, track_id: int, timestamp: str, 
                         confidence: float, overlap_pct: float, 
                         full_image_path: str, crop_image_path: str = "",
                         violation_type: str = "lan_chiem_via_he",
                         bbox: tuple = None, sidewalk_index: int = 1) -> int:
        """
        Ghi một bản ghi vi phạm mới vào CSDL.
        
        Args:
            bbox: Tọa độ bounding box (x1, y1, x2, y2) tại thời điểm vi phạm
            sidewalk_index: Chỉ số vỉa hè bị lấn chiếm (1, 2, ...)
            
        Returns:
            int: ID của bản ghi vừa thêm
        """
        x1, y1, x2, y2 = bbox if bbox else (0, 0, 0, 0)
        sql = """
            INSERT INTO violations (
                camera_id, track_id, timestamp, violation_type, 
                confidence, overlap_pct, full_image_path, crop_image_path,
                bbox_x1, bbox_y1, bbox_x2, bbox_y2, sidewalk_index
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (
                camera_id, track_id, timestamp, violation_type,
                round(confidence, 2), round(overlap_pct, 1),
                full_image_path, crop_image_path,
                x1, y1, x2, y2, sidewalk_index
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def is_duplicate_violation(self, camera_id: str, bbox: tuple, time_window_minutes: int = 5) -> bool:
        """
        ISSUE 09 FIX: Kiểm tra xem đã có bản ghi vi phạm tương tự trong DB chưa
        (để tránh ghi trùng khi hệ thống restart).
        So sánh: cùng camera + bbox gần giống + trong vòng N phút.
        """
        x1, y1, x2, y2 = bbox if bbox else (0, 0, 0, 0)
        # Khoảng mở rộng pixel cho phép coi là "cùng vị trí"
        margin = max(30, int((x2 - x1) * 0.15))  # 15% chiều rộng box hoặc tối thiểu 30px
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM violations
                WHERE camera_id = ?
                  AND ABS(bbox_x1 - ?) <= ?
                  AND ABS(bbox_y1 - ?) <= ?
                  AND ABS(bbox_x2 - ?) <= ?
                  AND ABS(bbox_y2 - ?) <= ?
                  AND timestamp >= datetime('now', 'localtime', ?)
            """, (
                camera_id,
                x1, margin, y1, margin, x2, margin, y2, margin,
                f'-{time_window_minutes} minutes'
            ))
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            conn.close()

    def update_violation_status(self, violation_id: int, new_status: str, reviewed_by: str = None, dismiss_reason: str = None) -> bool:
        """
        Cập nhật trạng thái xử lý vi phạm kèm thông tin cán bộ duyệt và lý do bác bỏ (Human-in-the-Loop).
        Trạng thái hợp lệ: 'pending', 'confirmed', 'dismissed', 'resolved'
        """
        valid_statuses = {'pending', 'confirmed', 'dismissed', 'resolved'}
        if new_status not in valid_statuses:
            print(f"[LỖI] Trạng thái '{new_status}' không hợp lệ. Chọn: {valid_statuses}")
            return False
            
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            reviewed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """
                UPDATE violations 
                SET status = ?, 
                    reviewed_by = COALESCE(?, reviewed_by), 
                    dismiss_reason = ?, 
                    reviewed_at = ?
                WHERE id = ?
                """,
                (new_status, reviewed_by, dismiss_reason, reviewed_at, violation_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_violations(self, camera_id: str = None, date_str: str = None, status: str = None, limit: int = 100) -> list:
        """
        Truy vấn danh sách vi phạm có lọc theo camera, ngày hoặc trạng thái.
        """
        query = "SELECT * FROM violations WHERE 1=1"
        params = []

        if camera_id:
            query += " AND camera_id = ?"
            params.append(camera_id)

        if date_str:
            query += " AND DATE(timestamp) = DATE(?)"
            params.append(date_str)

        if status and status != "all":
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_statistics(self) -> dict:
        """
        Thống kê tổng quan phục vụ Dashboard.
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Tổng số vụ
            cursor.execute("SELECT COUNT(*) FROM violations")
            total = cursor.fetchone()[0]

            # Số vụ hôm nay
            cursor.execute("SELECT COUNT(*) FROM violations WHERE DATE(timestamp) = DATE('now', 'localtime')")
            today = cursor.fetchone()[0]

            # Thống kê theo camera
            cursor.execute("SELECT camera_id, COUNT(*) as count FROM violations GROUP BY camera_id")
            by_cam = {row["camera_id"]: row["count"] for row in cursor.fetchall()}

            # Thống kê theo trạng thái (Pending, Confirmed, Dismissed, Resolved)
            cursor.execute("SELECT status, COUNT(*) as count FROM violations GROUP BY status")
            by_status = {row["status"]: row["count"] for row in cursor.fetchall()}

            return {
                "total_violations": total,
                "today_violations": today,
                "violations_by_camera": by_cam,
                "violations_by_status": by_status
            }
        finally:
            conn.close()

