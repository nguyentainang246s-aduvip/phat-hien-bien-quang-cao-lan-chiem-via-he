"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Web Dashboard Giám Sát & Quản Lý Phạt Nguội Trực Quan (Version 1.4)
TASK: 25 & 26 - DASHBOARD ĐA NỀN TẢNG (CHẠY ĐỘC LẬP KHÔNG CẦN CÀI ĐẶT THÊM THƯ VIỆN)
==============================================================================
"""

import os
import sys
import json
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath("."))


from database import ViolationDatabase
from roi import ROIManager

PORT = 8501
DB_PATH = "data/surveillance.db"
db = ViolationDatabase(DB_PATH)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CCTV Sidewalk Surveillance Dashboard - ĐATN 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-dark: #0f172a;
            --card-bg: #1e293b;
            --border: #334155;
            --primary: #3b82f6;
            --danger: #ef4444;
            --warning: #f59e0b;
            --success: #10b981;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; }
        
        /* Navbar */
        .navbar {
            background-color: var(--card-bg);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .navbar .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
        }
        .navbar .brand i { font-size: 1.6rem; color: var(--danger); }
        .navbar .badge-status {
            background: rgba(16, 185, 129, 0.15);
            color: var(--success);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            border: 1px solid rgba(16, 185, 129, 0.3);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .navbar .badge-status::before {
            content: "";
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px var(--success);
        }

        /* Container */
        .container { max-width: 1400px; margin: 0 auto; padding: 2rem; width: 100%; flex: 1; }

        /* KPI Cards */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }
        .kpi-card {
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.3); }
        .kpi-icon {
            width: 56px;
            height: 56px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }
        .kpi-icon.blue { background: rgba(59, 130, 246, 0.15); color: var(--primary); }
        .kpi-icon.red { background: rgba(239, 68, 68, 0.15); color: var(--danger); }
        .kpi-icon.yellow { background: rgba(245, 158, 11, 0.15); color: var(--warning); }
        .kpi-icon.green { background: rgba(16, 185, 129, 0.15); color: var(--success); }
        .kpi-info .val { font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }
        .kpi-info .lbl { font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }

        /* Section Header */
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        .section-title {
            font-size: 1.3rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .btn-refresh {
            background: var(--primary);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            text-decoration: none;
            transition: background 0.2s;
        }
        .btn-refresh:hover { background: #2563eb; }

        /* Violations Grid */
        .violations-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        .violation-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: border-color 0.2s;
        }
        .violation-card:hover { border-color: var(--danger); }
        .card-img-container {
            position: relative;
            background: #000;
            height: 240px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        .card-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            cursor: pointer;
            transition: transform 0.3s;
        }
        .card-img:hover { transform: scale(1.03); }
        .card-crop-thumb {
            position: absolute;
            bottom: 10px;
            right: 10px;
            width: 90px;
            height: 90px;
            object-fit: cover;
            border-radius: 8px;
            border: 2px solid var(--danger);
            box-shadow: 0 4px 10px rgba(0,0,0,0.6);
            background: #111;
        }
        .card-badge {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(239, 68, 68, 0.9);
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            backdrop-filter: blur(4px);
        }
        .card-body { padding: 1.25rem; flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
        .card-meta { display: flex; justify-content: space-between; margin-bottom: 0.75rem; font-size: 0.85rem; color: var(--text-muted); }
        .card-meta span { display: flex; align-items: center; gap: 6px; }
        .card-title { font-size: 1.05rem; font-weight: 600; margin-bottom: 0.5rem; color: #fff; }
        
        /* Overlap Progress Bar */
        .progress-container { margin-top: 0.75rem; }
        .progress-label { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px; color: var(--text-muted); }
        .progress-bar { background: #334155; height: 8px; border-radius: 4px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #f59e0b, #ef4444); border-radius: 4px; }

        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 4rem 2rem;
            background: var(--card-bg);
            border: 1px dashed var(--border);
            border-radius: 12px;
            color: var(--text-muted);
        }
        .empty-state i { font-size: 3.5rem; margin-bottom: 1rem; color: var(--primary); }

        /* Modal Preview */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.85);
            align-items: center;
            justify-content: center;
        }
        .modal-content { max-width: 90%; max-height: 90%; border-radius: 8px; border: 2px solid var(--border); }
        .modal-close { position: absolute; top: 20px; right: 30px; color: white; font-size: 2rem; cursor: pointer; }

        /* Footer */
        footer {
            border-top: 1px solid var(--border);
            padding: 1.5rem;
            text-align: center;
            font-size: 0.85rem;
            color: var(--text-muted);
            background: var(--card-bg);
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="brand">
            <i class="fa-solid fa-video"></i>
            <span>CCTV SMART SURVEILLANCE &middot; LẤN CHIẾM VỈA HÈ</span>
        </div>
        <div class="badge-status">HỆ THỐNG ONLINE (CCTV ACTIVE)</div>
    </div>

    <div class="container">
        <!-- KPI Metrics -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-icon red"><i class="fa-solid fa-triangle-exclamation"></i></div>
                <div class="kpi-info">
                    <div class="val" id="total-val">0</div>
                    <div class="lbl">Tổng vụ vi phạm</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon yellow"><i class="fa-solid fa-calendar-day"></i></div>
                <div class="kpi-info">
                    <div class="val" id="today-val">0</div>
                    <div class="lbl">Vi phạm trong ngày</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon blue"><i class="fa-solid fa-camera"></i></div>
                <div class="kpi-info">
                    <div class="val" id="cam-val">0</div>
                    <div class="lbl">Camera đang giám sát</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon green"><i class="fa-solid fa-microchip"></i></div>
                <div class="kpi-info">
                    <div class="val">YOLOv8</div>
                    <div class="lbl">Bộ não AI + ByteTrack</div>
                </div>
            </div>
        </div>

        <!-- Section: Bằng chứng phạt nguội -->
        <div class="section-header">
            <div class="section-title">
                <i class="fa-solid fa-folder-open text-primary"></i>
                <span>Kho Bằng Chứng Vi Phạm Phạt Nguội</span>
            </div>
            <button class="btn-refresh" onclick="loadData()">
                <i class="fa-solid fa-rotate-right"></i> Làm Mới Dữ Liệu
            </button>
        </div>

        <!-- Cards Container -->
        <div class="violations-grid" id="violations-container">
            <!-- Render via JS -->
        </div>
    </div>

    <!-- Image Modal Preview -->
    <div class="modal" id="imageModal" onclick="closeModal()">
        <span class="modal-close">&times;</span>
        <img class="modal-content" id="modalImg">
    </div>

    <footer>
        Đồ Án Tốt Nghiệp: Phát hiện biển quảng cáo/biển hiệu lấn chiếm vỉa hè qua CCTV cố định &middot; 2026
    </footer>

    <script>
        async function loadData() {
            try {
                const [statsRes, violsRes] = await Promise.all([
                    fetch('/api/stats'),
                    fetch('/api/violations')
                ]);
                const stats = await statsRes.json();
                const viols = await violsRes.json();

                // Update KPIs
                document.getElementById('total-val').innerText = stats.total_violations || 0;
                document.getElementById('today-val').innerText = stats.today_violations || 0;
                document.getElementById('cam-val').innerText = Object.keys(stats.violations_by_camera || {}).length || 1;

                // Render Cards
                const container = document.getElementById('violations-container');
                if (!viols || viols.length === 0) {
                    container.innerHTML = `
                        <div class="empty-state" style="grid-column: 1/-1;">
                            <i class="fa-solid fa-shield-halved"></i>
                            <h3>Chưa ghi nhận vụ vi phạm nào</h3>
                            <p>Hãy chạy file <code>main_temporal.py</code> để giám sát và tự động lưu bằng chứng vào đây.</p>
                        </div>
                    `;
                    return;
                }

                container.innerHTML = viols.map(v => `
                    <div class="violation-card">
                        <div class="card-img-container">
                            <span class="card-badge"><i class="fa-solid fa-circle-exclamation"></i> VI PHẠM #${v.id}</span>
                            <img class="card-img" src="/${v.full_image_path}" alt="Bằng chứng toàn cảnh" onclick="openModal('/${v.full_image_path}')">
                            ${v.crop_image_path ? `<img class="card-crop-thumb" src="/${v.crop_image_path}" title="Ảnh cận cảnh biển hiệu" onclick="openModal('/${v.crop_image_path}')">` : ''}
                        </div>
                        <div class="card-body">
                            <div class="card-meta">
                                <span><i class="fa-solid fa-video"></i> ${v.camera_id}</span>
                                <span><i class="fa-solid fa-clock"></i> ${v.timestamp}</span>
                            </div>
                            <div class="card-title">Biển Hiệu ID: #${v.track_id} (Độ tin cậy: ${(v.confidence*100).toFixed(0)}%)</div>
                            <div style="margin-top:8px; display:flex; gap:6px;">
                                <button onclick="updateStatus(${v.id}, 'confirmed')" style="background:#10b981; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer; font-size:0.8rem; font-weight:600;">✓ Xác nhận</button>
                                <button onclick="updateStatus(${v.id}, 'dismissed')" style="background:#6b7280; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer; font-size:0.8rem; font-weight:600;">✗ Bỏ qua</button>
                                <button onclick="updateStatus(${v.id}, 'resolved')" style="background:#3b82f6; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer; font-size:0.8rem; font-weight:600;">☑ Đã xử lý</button>
                            </div>
                            <div class="progress-container">
                                <div class="progress-label">
                                    <span>Tỷ lệ lấn chiếm vỉa hè</span>
                                    <span style="color: var(--danger); font-weight: 700;">${v.overlap_pct}%</span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${Math.min(100, v.overlap_pct)}%;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                console.error("Lỗi tải dữ liệu:", err);
            }
        }

        function openModal(src) {
            document.getElementById('modalImg').src = src;
            document.getElementById('imageModal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('imageModal').style.display = 'none';
        }

        // ISSUE 15: Cập nhật trạng thái vi phạm
        async function updateStatus(id, status) {
            try {
                const res = await fetch(`/api/violations/${id}/status`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: status })
                });
                if (res.ok) {
                    alert(`Đã cập nhật vụ #${id} thành "${status}"`);
                    loadData();
                } else {
                    alert('Lỗi cập nhật trạng thái!');
                }
            } catch (err) {
                console.error('Lỗi:', err);
            }
        }

        // Tự động tải dữ liệu ban đầu
        loadData();
    </script>
</body>
</html>
"""


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Giảm thiểu log rác ra console
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))

        elif path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            stats = db.get_statistics()
            self.wfile.write(json.dumps(stats).encode("utf-8"))

        elif path == "/api/violations":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            records = db.get_violations(limit=100)
            self.wfile.write(json.dumps(records).encode("utf-8"))

        elif path.startswith("/evidence/") or path.startswith("/data/"):
            file_path = path.lstrip("/")
            if os.path.exists(file_path):
                self.send_response(200)
                mime, _ = mimetypes.guess_type(file_path)
                self.send_header("Content-Type", mime or "application/octet-stream")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """ISSUE 15: Xử lý cập nhật trạng thái vi phạm."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # POST /api/violations/{id}/status
        import re
        match = re.match(r'/api/violations/(\d+)/status', path)
        if match:
            violation_id = int(match.group(1))
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                new_status = data.get('status', '')
                success = db.update_violation_status(violation_id, new_status)
                self.send_response(200 if success else 400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": success}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def run_dashboard(port: int = PORT):
    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    print("=" * 75)
    print(f"🚀 DASHBOARD GIÁM SÁT CCTV & LỊCH SỬ PHẠT NGUỘI ĐÃ KHỞI ĐỘNG THÀNH CÔNG!")
    print(f"🌐 Truy cập ngay tại trình duyệt:")
    print(f"   👉 http://localhost:{port}")
    print(f"   👉 http://127.0.0.1:{port}")
    print("=" * 75)
    print("Nhấn 'Ctrl + C' trong Terminal để dừng máy chủ Dashboard.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[OK] Đã dừng máy chủ Web Dashboard an toàn.")
        server.server_close()


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_dashboard(p)
