"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Database Management & Violation Records
TASK: 24 - Xây dựng Module database/db.py (Quản lý CSDL SQLite)
==============================================================================
"""

import logging
import os
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)


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
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
        except Exception as e:
            logger.warning("Không thể kích hoạt SQLite WAL mode (%s). Tiếp tục với chế độ mặc định.", e)
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
                    reviewed_by TEXT DEFAULT NULL,
                    dismiss_reason TEXT DEFAULT NULL,
                    reviewed_at DATETIME DEFAULT NULL,
                    full_image_path TEXT,
                    crop_image_path TEXT,
                    created_at DATETIME DEFAULT (datetime('now', 'localtime'))
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

    def is_duplicate_violation(self, camera_id: str, bbox: tuple, time_window_minutes: int = 60) -> bool:
        """
        Kiểm tra xem đã có bản ghi vi phạm tương tự trong DB chưa (khử trùng lặp theo vụ việc/incident):
        1. Cùng camera và tọa độ bbox tương đồng.
        2. Nếu đang có hồ sơ 'pending' hoặc 'confirmed' trong vòng time_window_minutes (mặc định 60 phút).
        3. Nếu hồ sơ tại vị trí này đã được cán bộ duyệt 'dismissed' (có giấy phép) trong 24 giờ qua thì không báo lại.
        """
        x1, y1, x2, y2 = bbox if bbox else (0, 0, 0, 0)
        # Tách riêng biên độ pixel theo trục X và trục Y để thích nghi với biển dạng đứng
        margin_x = max(30, int(abs(x2 - x1) * 0.15))
        margin_y = max(30, int(abs(y2 - y1) * 0.15))
        
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
                  AND (
                      (status IN ('pending', 'confirmed') AND timestamp >= datetime('now', 'localtime', ?))
                      OR (status = 'dismissed' AND COALESCE(reviewed_at, timestamp) >= datetime('now', 'localtime', '-24 hours'))
                  )
            """, (
                camera_id,
                x1, margin_x, y1, margin_y, x2, margin_x, y2, margin_y,
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

    def get_statistics(self, date_str: str = None) -> dict:
        """
        Thống kê tổng quan phục vụ Dashboard.
        Hỗ trợ lọc theo ngày cụ thể (YYYY-MM-DD) nếu truyền date_str.
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            date_filter = " WHERE DATE(timestamp) = DATE(?)" if date_str else ""
            params = (date_str,) if date_str else ()
            
            # Tổng số vụ
            cursor.execute(f"SELECT COUNT(*) FROM violations{date_filter}", params)
            total = cursor.fetchone()[0]

            # Số vụ hôm nay (hoặc ngày hiện tại)
            cursor.execute("SELECT COUNT(*) FROM violations WHERE DATE(timestamp) = DATE('now', 'localtime')")
            today = cursor.fetchone()[0]

            # Thống kê theo camera
            cursor.execute(f"SELECT camera_id, COUNT(*) as count FROM violations{date_filter} GROUP BY camera_id", params)
            by_cam = {row["camera_id"]: row["count"] for row in cursor.fetchall()}

            # Thống kê theo trạng thái (Pending, Confirmed, Dismissed, Resolved)
            cursor.execute(f"SELECT status, COUNT(*) as count FROM violations{date_filter} GROUP BY status", params)
            by_status = {row["status"]: row["count"] for row in cursor.fetchall()}

            return {
                "total_violations": total,
                "today_violations": today,
                "violations_by_camera": by_cam,
                "violations_by_status": by_status,
                "filter_date": date_str
            }
        finally:
            conn.close()

    def get_available_dates(self) -> list:
        """
        Lấy danh sách các ngày có ghi nhận vi phạm kèm số lượng hồ sơ.
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DATE(timestamp) as viol_date, COUNT(*) as count 
                FROM violations 
                WHERE timestamp IS NOT NULL 
                GROUP BY DATE(timestamp) 
                ORDER BY viol_date DESC
            """)
            rows = cursor.fetchall()
            return [{"date": row["viol_date"], "count": row["count"]} for row in rows if row["viol_date"]]
        finally:
            conn.close()

