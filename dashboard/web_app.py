"""
==============================================================================
ĐỒ ÁN TỐT NGHIỆP: PHÁT HIỆN BIỂN HIỆU/BIỂN QUẢNG CÁO LẤN CHIẾM VỈA HÈ QUA CCTV
Chủ đề: Web Dashboard Giám Sát & Quản Lý Phạt Nguội (Human-in-the-Loop Workflow)
Hỗ trợ Cán bộ Đội Quản lý Trật tự Đô thị duyệt/bác bỏ hồ sơ vi phạm theo quy trình
==============================================================================
"""

import os
import sys
import json
import re
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
    <title>Hệ Thống Giám Sát & Quản Lý Phạt Nguội Vỉa Hè - ĐATN 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-dark: #0b1120;
            --card-bg: #1e293b;
            --card-hover: #243248;
            --border: #334155;
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --danger: #ef4444;
            --danger-bg: rgba(239, 68, 68, 0.15);
            --warning: #f59e0b;
            --warning-bg: rgba(245, 158, 11, 0.15);
            --success: #10b981;
            --success-bg: rgba(16, 185, 129, 0.15);
            --purple: #8b5cf6;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; }
        
        /* Navbar */
        .navbar {
            background-color: #111827;
            border-bottom: 1px solid var(--border);
            padding: 0.9rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .navbar .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.15rem;
            font-weight: 700;
            color: #fff;
        }
        .navbar .brand i { font-size: 1.4rem; color: #ef4444; }
        .navbar .brand-subtitle { font-size: 0.78rem; color: var(--text-muted); font-weight: 400; }
        .navbar .badge-status {
            background: var(--success-bg);
            color: var(--success);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
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
        .container { max-width: 1440px; margin: 0 auto; padding: 1.8rem; width: 100%; flex: 1; }

        /* Banner thông tin quy trình */
        .workflow-banner {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
            border: 1px solid var(--border);
            border-left: 4px solid var(--primary);
            border-radius: 10px;
            padding: 1rem 1.4rem;
            margin-bottom: 1.8rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
        }
        .workflow-banner-text {
            font-size: 0.88rem;
            color: var(--text-muted);
            line-height: 1.4;
        }
        .workflow-banner-text strong { color: #fff; }
        .workflow-steps {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.8rem;
            color: var(--text-muted);
        }
        .step-pill {
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 600;
            background: #0f172a;
            border: 1px solid var(--border);
        }
        .step-pill.active { background: rgba(59, 130, 246, 0.2); color: var(--primary); border-color: var(--primary); }

        /* KPI Cards */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.2rem;
            margin-bottom: 2rem;
        }
        .kpi-card {
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.25rem;
            display: flex;
            align-items: center;
            gap: 1.1rem;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }
        .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.3); }
        .kpi-icon {
            width: 50px;
            height: 50px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
        }
        .kpi-icon.blue { background: rgba(59, 130, 246, 0.15); color: var(--primary); }
        .kpi-icon.yellow { background: var(--warning-bg); color: var(--warning); }
        .kpi-icon.green { background: var(--success-bg); color: var(--success); }
        .kpi-icon.gray { background: rgba(148, 163, 184, 0.15); color: #94a3b8; }
        .kpi-icon.purple { background: rgba(139, 92, 246, 0.15); color: var(--purple); }
        .kpi-info .val { font-size: 1.65rem; font-weight: 700; margin-bottom: 2px; }
        .kpi-info .lbl { font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }

        /* Filter Tabs */
        .filter-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.5rem;
            background: var(--card-bg);
            padding: 0.75rem 1rem;
            border-radius: 10px;
            border: 1px solid var(--border);
        }
        .filter-tabs {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .filter-btn {
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-muted);
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
        }
        .filter-btn:hover { color: #fff; background: rgba(255,255,255,0.05); }
        .filter-btn.active {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }
        .filter-count {
            background: rgba(0,0,0,0.3);
            padding: 2px 7px;
            border-radius: 10px;
            font-size: 0.75rem;
        }
        .filter-btn.active .filter-count {
            background: rgba(255,255,255,0.25);
        }
        .btn-refresh {
            background: #334155;
            color: white;
            border: none;
            padding: 7px 15px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.85rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: background 0.2s;
        }
        .btn-refresh:hover { background: #475569; }

        /* Violations Grid */
        .violations-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
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
            transition: border-color 0.2s, transform 0.2s;
        }
        .violation-card:hover { transform: translateY(-2px); border-color: #475569; }
        .violation-card.status-pending { border-left: 4px solid var(--warning); }
        .violation-card.status-confirmed { border-left: 4px solid var(--success); }
        .violation-card.status-dismissed { border-left: 4px solid var(--text-dim); opacity: 0.85; }
        .violation-card.status-resolved { border-left: 4px solid var(--primary); }

        .card-img-container {
            position: relative;
            background: #000;
            height: 230px;
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
            cursor: pointer;
        }
        
        /* Status Badges */
        .card-status-badge {
            position: absolute;
            top: 10px;
            left: 10px;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            backdrop-filter: blur(6px);
            display: flex;
            align-items: center;
            gap: 6px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }
        .badge-pending { background: rgba(245, 158, 11, 0.9); color: #000; }
        .badge-confirmed { background: rgba(16, 185, 129, 0.9); color: #fff; }
        .badge-dismissed { background: rgba(100, 116, 139, 0.9); color: #fff; }
        .badge-resolved { background: rgba(59, 130, 246, 0.9); color: #fff; }

        .card-privacy-tag {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(15, 23, 42, 0.85);
            color: #cbd5e1;
            font-size: 0.7rem;
            padding: 3px 8px;
            border-radius: 4px;
            border: 1px solid rgba(255,255,255,0.1);
        }

        .card-body { padding: 1.2rem; flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
        .card-meta { display: flex; justify-content: space-between; margin-bottom: 0.6rem; font-size: 0.82rem; color: var(--text-muted); }
        .card-meta span { display: flex; align-items: center; gap: 6px; }
        .card-title { font-size: 1.05rem; font-weight: 700; margin-bottom: 0.4rem; color: #fff; }
        
        /* Review Audit Box */
        .review-audit-box {
            background: rgba(15, 23, 42, 0.7);
            border: 1px dashed var(--border);
            border-radius: 8px;
            padding: 0.65rem 0.85rem;
            margin: 0.7rem 0;
            font-size: 0.8rem;
            line-height: 1.4;
        }
        .review-audit-box.confirmed-box { border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.05); }
        .review-audit-box.dismissed-box { border-color: rgba(239, 68, 68, 0.4); background: rgba(239, 68, 68, 0.05); }
        .review-audit-box.pending-box { border-color: rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.05); }

        /* Overlap Progress Bar */
        .progress-container { margin: 0.6rem 0; }
        .progress-label { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px; color: var(--text-muted); }
        .progress-bar { background: #334155; height: 7px; border-radius: 4px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #f59e0b, #ef4444); border-radius: 4px; }

        /* Action Buttons */
        .card-actions {
            margin-top: 1rem;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            border-top: 1px solid rgba(255,255,255,0.07);
            padding-top: 0.8rem;
        }
        .btn-action {
            flex: 1;
            padding: 7px 12px;
            border-radius: 6px;
            border: none;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.15s;
        }
        .btn-confirm { background: #10b981; color: white; }
        .btn-confirm:hover { background: #059669; }
        .btn-dismiss { background: #475569; color: white; }
        .btn-dismiss:hover { background: #334155; }
        .btn-resolve { background: #3b82f6; color: white; }
        .btn-resolve:hover { background: #2563eb; }
        .btn-reopen { background: #64748b; color: white; }
        .btn-reopen:hover { background: #475569; }

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
            background: rgba(0,0,0,0.88);
            align-items: center;
            justify-content: center;
        }
        .modal-content { max-width: 90%; max-height: 90%; border-radius: 8px; border: 2px solid var(--border); }
        .modal-close { position: absolute; top: 20px; right: 30px; color: white; font-size: 2rem; cursor: pointer; }

        /* Modal Dismiss / Reject Dialog */
        .dialog-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 1100;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(4px);
        }
        .dialog-box {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            width: 90%;
            max-width: 520px;
            padding: 1.8rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6);
        }
        .dialog-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #fff;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .dialog-desc {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 1.2rem;
            line-height: 1.4;
        }
        .dialog-group {
            margin-bottom: 1rem;
        }
        .dialog-label {
            display: block;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .dialog-input, .dialog-select {
            width: 100%;
            background: #0f172a;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 9px 12px;
            color: #fff;
            font-size: 0.9rem;
            outline: none;
        }
        .dialog-input:focus, .dialog-select:focus { border-color: var(--primary); }
        .dialog-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 1.5rem;
        }
        .btn-cancel {
            background: #334155;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
        }
        .btn-confirm-action {
            background: var(--danger);
            color: white;
            border: none;
            padding: 8px 18px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
        }

        /* Footer */
        footer {
            border-top: 1px solid var(--border);
            padding: 1.2rem;
            text-align: center;
            font-size: 0.82rem;
            color: var(--text-muted);
            background: #111827;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="brand">
            <i class="fa-solid fa-shield-halved"></i>
            <div>
                <div>CCTV SMART SURVEILLANCE &middot; LẤN CHIẾM VỈA HÈ</div>
                <div class="brand-subtitle">Hệ Thống Giám Sát & Hỗ Trợ Ra Quyết Định Xử Phạt (Human-in-the-Loop)</div>
            </div>
        </div>
        <div class="badge-status">HỆ THỐNG ONLINE &middot; CCTV ACTIVE</div>
    </div>

    <div class="container">
        <!-- Quy trình Banner -->
        <div class="workflow-banner">
            <div class="workflow-banner-text">
                <i class="fa-solid fa-circle-info" style="color: var(--primary); margin-right: 6px;"></i>
                <strong>Quy trình xử lý chuẩn:</strong> AI phát hiện & lưu cảnh báo vào hàng chờ <strong>Pending</strong> ➔ 
                Cán bộ Đội TTĐT đối chiếu ảnh toàn cảnh/cận cảnh ➔ <strong>Xác nhận phạt</strong> hoặc <strong>Bác bỏ</strong> (kèm lý do) ➔ <strong>Thi hành xử phạt</strong>.
            </div>
            <div class="workflow-steps">
                <span class="step-pill active">1. AI Phát hiện</span>
                <i class="fa-solid fa-arrow-right"></i>
                <span class="step-pill">2. Cán bộ duyệt</span>
                <i class="fa-solid fa-arrow-right"></i>
                <span class="step-pill">3. Lập biên bản</span>
            </div>
        </div>

        <!-- KPI Metrics -->
        <div class="kpi-grid">
            <div class="kpi-card" onclick="filterByStatus('all')">
                <div class="kpi-icon blue"><i class="fa-solid fa-folder-open"></i></div>
                <div class="kpi-info">
                    <div class="val" id="total-val">0</div>
                    <div class="lbl">Tổng hồ sơ ghi nhận</div>
                </div>
            </div>
            <div class="kpi-card" onclick="filterByStatus('pending')">
                <div class="kpi-icon yellow"><i class="fa-solid fa-clock"></i></div>
                <div class="kpi-info">
                    <div class="val" id="pending-val" style="color: var(--warning);">0</div>
                    <div class="lbl">Chờ cán bộ duyệt (Pending)</div>
                </div>
            </div>
            <div class="kpi-card" onclick="filterByStatus('confirmed')">
                <div class="kpi-icon green"><i class="fa-solid fa-circle-check"></i></div>
                <div class="kpi-info">
                    <div class="val" id="confirmed-val" style="color: var(--success);">0</div>
                    <div class="lbl">Đã xác nhận vi phạm</div>
                </div>
            </div>
            <div class="kpi-card" onclick="filterByStatus('dismissed')">
                <div class="kpi-icon gray"><i class="fa-solid fa-ban"></i></div>
                <div class="kpi-info">
                    <div class="val" id="dismissed-val" style="color: #94a3b8;">0</div>
                    <div class="lbl">Đã bác bỏ / Miễn trừ</div>
                </div>
            </div>
            <div class="kpi-card" onclick="filterByStatus('resolved')">
                <div class="kpi-icon purple"><i class="fa-solid fa-gavel"></i></div>
                <div class="kpi-info">
                    <div class="val" id="resolved-val" style="color: var(--purple);">0</div>
                    <div class="lbl">Đã hoàn thành xử lý</div>
                </div>
            </div>
        </div>

        <!-- Filter Bar -->
        <div class="filter-bar">
            <div class="filter-tabs">
                <button class="filter-btn active" id="tab-all" onclick="filterByStatus('all')">
                    Tất cả <span class="filter-count" id="count-all">0</span>
                </button>
                <button class="filter-btn" id="tab-pending" onclick="filterByStatus('pending')">
                    <i class="fa-solid fa-hourglass-half"></i> Chờ duyệt (Pending) <span class="filter-count" id="count-pending">0</span>
                </button>
                <button class="filter-btn" id="tab-confirmed" onclick="filterByStatus('confirmed')">
                    <i class="fa-solid fa-check"></i> Đã xác nhận <span class="filter-count" id="count-confirmed">0</span>
                </button>
                <button class="filter-btn" id="tab-dismissed" onclick="filterByStatus('dismissed')">
                    <i class="fa-solid fa-xmark"></i> Đã bác bỏ <span class="filter-count" id="count-dismissed">0</span>
                </button>
                <button class="filter-btn" id="tab-resolved" onclick="filterByStatus('resolved')">
                    <i class="fa-solid fa-flag-checkered"></i> Đã xử lý <span class="filter-count" id="count-resolved">0</span>
                </button>
            </div>
            <button class="btn-refresh" onclick="loadData()">
                <i class="fa-solid fa-rotate-right"></i> Làm mới
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

    <!-- Dialog Bác bỏ vi phạm (Dismiss Modal) -->
    <div class="dialog-overlay" id="dismissDialog">
        <div class="dialog-box">
            <div class="dialog-title">
                <i class="fa-solid fa-triangle-exclamation" style="color: var(--warning);"></i>
                Bác Bỏ Hồ Sơ Vi Phạm #<span id="dialog-viol-id">0</span>
            </div>
            <div class="dialog-desc">
                Cán bộ vui lòng chọn lý do bác bỏ cảnh báo này. Dữ liệu này sẽ được lưu trữ làm bằng chứng kiểm toán và dùng để tối ưu mô hình AI sau này.
            </div>

            <div class="dialog-group">
                <label class="dialog-label">Họ tên / Mã Cán bộ duyệt:</label>
                <input type="text" class="dialog-input" id="dismiss-reviewer" value="Cán bộ Đội TTĐT">
            </div>

            <div class="dialog-group">
                <label class="dialog-label">Lý do bác bỏ:</label>
                <select class="dialog-select" id="dismiss-reason-select" onchange="toggleCustomReason()">
                    <option value="Biển có giấy phép sử dụng tạm thời vỉa hè hợp lệ">Biển có giấy phép sử dụng tạm thời vỉa hè hợp lệ</option>
                    <option value="Người dân đang bốc dỡ hàng / chuyển đồ đi ngang (tạm thời)">Người dân đang bốc dỡ hàng / chuyển đồ đi ngang (tạm thời)</option>
                    <option value="Nhận diện nhầm vật thể khác (cửa cuốn, cây cối, xe cộ, mái hiên)">Nhận diện nhầm vật thể khác (cửa cuốn, cây cối, xe cộ, mái hiên)</option>
                    <option value="Biển đặt lùi vào trong chỉ giới đỏ (không chiếm lòng hè)">Biển đặt lùi vào trong chỉ giới đỏ (không chiếm lòng hè)</option>
                    <option value="other">Lý do khác (Nhập thủ công)...</option>
                </select>
            </div>

            <div class="dialog-group" id="custom-reason-group" style="display: none;">
                <label class="dialog-label">Chi tiết lý do khác:</label>
                <input type="text" class="dialog-input" id="dismiss-reason-custom" placeholder="Nhập lý do chi tiết...">
            </div>

            <div class="dialog-actions">
                <button class="btn-cancel" onclick="closeDismissDialog()">Hủy bỏ</button>
                <button class="btn-confirm-action" onclick="submitDismiss()">Xác Nhận Bác Bỏ</button>
            </div>
        </div>
    </div>

    <!-- Dialog Phê duyệt vi phạm (Confirm Modal) -->
    <div class="dialog-overlay" id="confirmDialog">
        <div class="dialog-box">
            <div class="dialog-title">
                <i class="fa-solid fa-shield-check" style="color: var(--success);"></i>
                Xác Nhận Lập Biên Bản Vi Phạm #<span id="dialog-confirm-id">0</span>
            </div>
            <div class="dialog-desc">
                Xác nhận biển hiệu này lấn chiếm vỉa hè trái phép. Hồ sơ sẽ được chuyển sang trạng thái <strong>Đã xác nhận</strong> để in biên bản hoặc xử phạt nguội.
            </div>

            <div class="dialog-group">
                <label class="dialog-label">Họ tên / Mã Cán bộ ký duyệt:</label>
                <input type="text" class="dialog-input" id="confirm-reviewer" value="Cán bộ Đội TTĐT">
            </div>

            <div class="dialog-actions">
                <button class="btn-cancel" onclick="closeConfirmDialog()">Hủy bỏ</button>
                <button class="btn-confirm-action" style="background: var(--success);" onclick="submitConfirm()">Xác Nhận Vi Phạm</button>
            </div>
        </div>
    </div>

    <footer>
        Đồ Án Tốt Nghiệp: Phát hiện biển quảng cáo/biển hiệu lấn chiếm vỉa hè qua CCTV cố định &middot; 2026<br>
        <span style="font-size:0.75rem; color:#64748b;">Decision Support System (Hệ thống Hỗ trợ ra quyết định & lưu bằng chứng bảo vệ quyền riêng tư)</span>
    </footer>

    <script>
        let currentStatusFilter = 'all';
        let activeViolIdForDismiss = null;
        let activeViolIdForConfirm = null;

        async function loadData() {
            try {
                const statsRes = await fetch('/api/stats');
                const stats = await statsRes.json();

                // Update KPIs
                const byStatus = stats.violations_by_status || {};
                const total = stats.total_violations || 0;
                const pending = byStatus.pending || 0;
                const confirmed = byStatus.confirmed || 0;
                const dismissed = byStatus.dismissed || 0;
                const resolved = byStatus.resolved || 0;

                document.getElementById('total-val').innerText = total;
                document.getElementById('pending-val').innerText = pending;
                document.getElementById('confirmed-val').innerText = confirmed;
                document.getElementById('dismissed-val').innerText = dismissed;
                document.getElementById('resolved-val').innerText = resolved;

                document.getElementById('count-all').innerText = total;
                document.getElementById('count-pending').innerText = pending;
                document.getElementById('count-confirmed').innerText = confirmed;
                document.getElementById('count-dismissed').innerText = dismissed;
                document.getElementById('count-resolved').innerText = resolved;

                // Load violations with filter
                const url = currentStatusFilter === 'all' ? '/api/violations' : `/api/violations?status=${currentStatusFilter}`;
                const violsRes = await fetch(url);
                const viols = await violsRes.json();

                const container = document.getElementById('violations-container');
                if (!viols || viols.length === 0) {
                    container.innerHTML = `
                        <div class="empty-state" style="grid-column: 1/-1;">
                            <i class="fa-solid fa-clipboard-check"></i>
                            <h3>Không có hồ sơ nào trong mục này</h3>
                            <p>Tất cả bằng chứng ghi nhận sẽ xuất hiện tại đây khi camera phát hiện vi phạm.</p>
                        </div>
                    `;
                    return;
                }

                container.innerHTML = viols.map(v => {
                    const status = v.status || 'pending';
                    let statusBadge = '';
                    let actionButtons = '';
                    let auditBox = '';

                    if (status === 'pending') {
                        statusBadge = `<span class="card-status-badge badge-pending"><i class="fa-solid fa-hourglass-start"></i> Chờ duyệt</span>`;
                        actionButtons = `
                            <button class="btn-action btn-confirm" onclick="openConfirmDialog(${v.id})">
                                <i class="fa-solid fa-check"></i> Duyệt vi phạm
                            </button>
                            <button class="btn-action btn-dismiss" onclick="openDismissDialog(${v.id})">
                                <i class="fa-solid fa-ban"></i> Bác bỏ
                            </button>
                        `;
                        auditBox = `
                            <div class="review-audit-box pending-box">
                                <i class="fa-solid fa-circle-exclamation" style="color: var(--warning);"></i> 
                                Cần Cán bộ Đội TTĐT xem xét ảnh toàn cảnh và xác nhận trước khi lập biên bản.
                            </div>
                        `;
                    } else if (status === 'confirmed') {
                        statusBadge = `<span class="card-status-badge badge-confirmed"><i class="fa-solid fa-circle-check"></i> Đã xác nhận</span>`;
                        actionButtons = `
                            <button class="btn-action btn-resolve" onclick="updateStatusDirect(${v.id}, 'resolved', '${v.reviewed_by || 'Cán bộ'}')">
                                <i class="fa-solid fa-gavel"></i> Đã nộp phạt / Xử lý
                            </button>
                            <button class="btn-action btn-dismiss" onclick="openDismissDialog(${v.id})">
                                <i class="fa-solid fa-ban"></i> Bác bỏ lại
                            </button>
                        `;
                        auditBox = `
                            <div class="review-audit-box confirmed-box">
                                <strong>👤 Người duyệt:</strong> ${v.reviewed_by || 'Cán bộ TTĐT'}<br>
                                <span style="color: var(--text-muted); font-size: 0.75rem;">Thời gian duyệt: ${v.reviewed_at || v.timestamp}</span>
                            </div>
                        `;
                    } else if (status === 'dismissed') {
                        statusBadge = `<span class="card-status-badge badge-dismissed"><i class="fa-solid fa-ban"></i> Đã bác bỏ</span>`;
                        actionButtons = `
                            <button class="btn-action btn-reopen" onclick="updateStatusDirect(${v.id}, 'pending', null, null)">
                                <i class="fa-solid fa-rotate-left"></i> Phục hồi về chờ duyệt
                            </button>
                        `;
                        auditBox = `
                            <div class="review-audit-box dismissed-box">
                                <strong>🚫 Lý do bác bỏ:</strong> ${v.dismiss_reason || 'Không có lý do chi tiết'}<br>
                                <span style="color: var(--text-muted); font-size: 0.75rem;">Cán bộ: ${v.reviewed_by || 'Chưa rõ'} &bull; ${v.reviewed_at || ''}</span>
                            </div>
                        `;
                    } else if (status === 'resolved') {
                        statusBadge = `<span class="card-status-badge badge-resolved"><i class="fa-solid fa-circle-check"></i> Đã hoàn thành</span>`;
                        actionButtons = `
                            <button class="btn-action btn-reopen" onclick="updateStatusDirect(${v.id}, 'confirmed', '${v.reviewed_by || 'Cán bộ'}')">
                                <i class="fa-solid fa-arrow-rotate-left"></i> Đưa về Đã duyệt
                            </button>
                        `;
                        auditBox = `
                            <div class="review-audit-box">
                                <span style="color: var(--success); font-weight:600;"><i class="fa-solid fa-check-double"></i> Vụ việc đã được chấp hành/nộp phạt.</span>
                            </div>
                        `;
                    }

                    return `
                        <div class="violation-card status-${status}">
                            <div class="card-img-container">
                                ${statusBadge}
                                <span class="card-privacy-tag"><i class="fa-solid fa-eye-slash"></i> Face Blurred</span>
                                <img class="card-img" src="/${v.full_image_path}" alt="Bằng chứng toàn cảnh" onclick="openModal('/${v.full_image_path}')">
                                ${v.crop_image_path ? `<img class="card-crop-thumb" src="/${v.crop_image_path}" title="Ảnh cận cảnh biển hiệu" onclick="openModal('/${v.crop_image_path}')">` : ''}
                            </div>
                            <div class="card-body">
                                <div class="card-meta">
                                    <span><i class="fa-solid fa-video"></i> ${v.camera_id}</span>
                                    <span><i class="fa-solid fa-clock"></i> ${v.timestamp}</span>
                                </div>
                                <div class="card-title">Hồ sơ #${v.id} &bull; Biển hiệu Track #${v.track_id}</div>
                                
                                <div class="progress-container">
                                    <div class="progress-label">
                                        <span>Độ tin cậy: <strong>${(v.confidence*100).toFixed(0)}%</strong></span>
                                        <span>Lấn chiếm vỉa hè: <strong style="color: var(--danger);">${v.overlap_pct}%</strong></span>
                                    </div>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: ${Math.min(100, v.overlap_pct)}%;"></div>
                                    </div>
                                </div>

                                ${auditBox}

                                <div class="card-actions">
                                    ${actionButtons}
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
            } catch (err) {
                console.error("Lỗi tải dữ liệu:", err);
            }
        }

        function filterByStatus(status) {
            currentStatusFilter = status;
            ['all', 'pending', 'confirmed', 'dismissed', 'resolved'].forEach(s => {
                const el = document.getElementById(`tab-${s}`);
                if (el) {
                    if (s === status) el.classList.add('active');
                    else el.classList.remove('active');
                }
            });
            loadData();
        }

        function openModal(src) {
            document.getElementById('modalImg').src = src;
            document.getElementById('imageModal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('imageModal').style.display = 'none';
        }

        /* Confirm Dialog */
        function openConfirmDialog(id) {
            activeViolIdForConfirm = id;
            document.getElementById('dialog-confirm-id').innerText = id;
            document.getElementById('confirmDialog').style.display = 'flex';
        }

        function closeConfirmDialog() {
            document.getElementById('confirmDialog').style.display = 'none';
            activeViolIdForConfirm = null;
        }

        async function submitConfirm() {
            const reviewer = document.getElementById('confirm-reviewer').value.trim() || 'Cán bộ Đội TTĐT';
            await updateStatusDirect(activeViolIdForConfirm, 'confirmed', reviewer, null);
            closeConfirmDialog();
        }

        /* Dismiss Dialog */
        function openDismissDialog(id) {
            activeViolIdForDismiss = id;
            document.getElementById('dialog-viol-id').innerText = id;
            document.getElementById('dismissDialog').style.display = 'flex';
        }

        function closeDismissDialog() {
            document.getElementById('dismissDialog').style.display = 'none';
            activeViolIdForDismiss = null;
        }

        function toggleCustomReason() {
            const sel = document.getElementById('dismiss-reason-select').value;
            const customGroup = document.getElementById('custom-reason-group');
            if (sel === 'other') {
                customGroup.style.display = 'block';
            } else {
                customGroup.style.display = 'none';
            }
        }

        async function submitDismiss() {
            const reviewer = document.getElementById('dismiss-reviewer').value.trim() || 'Cán bộ Đội TTĐT';
            const sel = document.getElementById('dismiss-reason-select').value;
            let reason = sel;
            if (sel === 'other') {
                reason = document.getElementById('dismiss-reason-custom').value.trim();
                if (!reason) {
                    alert('Vui lòng nhập lý do bác bỏ chi tiết!');
                    return;
                }
            }

            await updateStatusDirect(activeViolIdForDismiss, 'dismissed', reviewer, reason);
            closeDismissDialog();
        }

        /* API Call */
        async function updateStatusDirect(id, status, reviewer, reason) {
            try {
                const res = await fetch(`/api/violations/${id}/status`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        status: status,
                        reviewed_by: reviewer,
                        dismiss_reason: reason
                    })
                });
                if (res.ok) {
                    loadData();
                } else {
                    alert('Lỗi cập nhật trạng thái vi phạm!');
                }
            } catch (err) {
                console.error('Lỗi API:', err);
                alert('Không thể kết nối đến máy chủ.');
            }
        }

        // Tự động tải ban đầu
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
            query_params = urllib.parse.parse_qs(parsed.query)
            status_param = query_params.get("status", [None])[0]
            records = db.get_violations(limit=100, status=status_param)
            self.wfile.write(json.dumps(records).encode("utf-8"))

        elif path.startswith("/evidence/") or path.startswith("/data/"):
            # Chặn path traversal (../) bằng cách resolve đường dẫn tuyệt đối
            base_dir = os.path.abspath(".")
            allowed_prefixes = (
                os.path.abspath("evidence"),
                os.path.abspath(os.path.join("data", "surveillance.db")).rstrip("surveillance.db"),
            )
            raw_path = path.lstrip("/")
            file_path = os.path.normpath(os.path.join(base_dir, raw_path))
            is_allowed = any(file_path.startswith(prefix) for prefix in allowed_prefixes)

            if not is_allowed:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"403 Forbidden: Access outside allowed directories")
            elif os.path.isfile(file_path):
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
        """Xử lý cập nhật trạng thái vi phạm (Human-in-the-Loop)."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # POST /api/violations/{id}/status
        match = re.match(r'/api/violations/(\d+)/status', path)
        if match:
            # Kiểm tra bảo mật: chỉ chấp nhận từ localhost
            client_host = self.client_address[0] if self.client_address else ""
            if client_host not in ("127.0.0.1", "::1", "localhost"):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"403 Forbidden: Status updates require local access")
                return

            violation_id = int(match.group(1))
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                new_status = data.get('status', '')
                reviewed_by = data.get('reviewed_by', None)
                dismiss_reason = data.get('dismiss_reason', None)

                success = db.update_violation_status(
                    violation_id=violation_id,
                    new_status=new_status,
                    reviewed_by=reviewed_by,
                    dismiss_reason=dismiss_reason
                )
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
