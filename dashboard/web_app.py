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
import time
import urllib.parse
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
import cv2
import threading

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

        /* Navigation Tabs */
        .nav-tabs-wrapper {
            display: flex;
            align-items: center;
            gap: 6px;
            background: #0f172a;
            padding: 4px;
            border-radius: 10px;
            border: 1px solid var(--border);
        }
        .nav-tab-btn {
            background: transparent;
            color: var(--text-muted);
            border: none;
            padding: 8px 18px;
            border-radius: 7px;
            font-size: 0.88rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
        }
        .nav-tab-btn:hover {
            color: #fff;
            background: rgba(255, 255, 255, 0.05);
        }
        .nav-tab-btn.active {
            background: var(--primary);
            color: #fff;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.35);
        }

        /* ROI Studio Layout */
        .roi-header-stats {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .badge-pill-stat {
            background: #0f172a;
            border: 1px solid var(--border);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .roi-studio-grid {
            display: grid;
            grid-template-columns: 360px 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
            align-items: start;
        }
        @media (max-width: 1024px) {
            .roi-studio-grid { grid-template-columns: 1fr; }
        }
        .roi-sidebar {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.2rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .roi-sidebar-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 700;
            font-size: 0.95rem;
            color: #fff;
        }
        .sidebar-title {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .sidebar-title i { color: var(--primary); }
        .btn-sidebar-refresh {
            background: #0f172a;
            border: 1px solid var(--border);
            color: var(--text-muted);
            border-radius: 6px;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-sidebar-refresh:hover { color: #fff; border-color: var(--primary); }
        .roi-search-box {
            position: relative;
            display: flex;
            align-items: center;
        }
        .roi-search-box i {
            position: absolute;
            left: 12px;
            color: var(--text-dim);
            font-size: 0.85rem;
        }
        .roi-search-box input {
            width: 100%;
            background: #0f172a;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 8px 12px 8px 34px;
            color: #fff;
            font-size: 0.85rem;
            outline: none;
            transition: border-color 0.2s;
        }
        .roi-search-box input:focus { border-color: var(--primary); }
        .roi-video-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-height: calc(100vh - 360px);
            overflow-y: auto;
            padding-right: 4px;
        }
        .roi-video-list::-webkit-scrollbar { width: 5px; }
        .roi-video-list::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        .roi-video-card {
            background: #0f172a;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px 14px;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .roi-video-card:hover {
            border-color: var(--primary);
            background: #152238;
            transform: translateX(3px);
        }
        .roi-video-card.active {
            border-color: var(--primary);
            background: rgba(59, 130, 246, 0.12);
            box-shadow: 0 0 0 1px var(--primary);
        }
        .roi-video-card-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 8px;
        }
        .roi-video-filename {
            font-weight: 600;
            font-size: 0.88rem;
            color: #fff;
            word-break: break-all;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .roi-video-filename i { color: #60a5fa; }
        .badge-roi-status {
            font-size: 0.72rem;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 12px;
            white-space: nowrap;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        .badge-roi-status.configured {
            background: var(--success-bg);
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .badge-roi-status.missing {
            background: var(--warning-bg);
            color: var(--warning);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .roi-video-meta {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.76rem;
            color: var(--text-muted);
        }
        .roi-video-meta span { display: flex; align-items: center; gap: 4px; }

        /* Workspace / Canvas Area */
        .roi-workspace {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.2rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .roi-toolbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            background: #0f172a;
            padding: 10px 14px;
            border-radius: 10px;
            border: 1px solid var(--border);
        }
        .roi-toolbar-left {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        .active-video-badge {
            font-size: 0.9rem;
            font-weight: 700;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 7px;
        }
        .active-video-badge i { color: var(--primary); }
        .roi-meta-badge {
            background: #1e293b;
            color: var(--text-muted);
            border: 1px solid var(--border);
            padding: 3px 9px;
            border-radius: 6px;
            font-size: 0.76rem;
            font-family: monospace;
        }
        .roi-cursor-coord {
            color: #38bdf8;
            font-family: monospace;
            font-size: 0.8rem;
            background: rgba(56, 189, 248, 0.1);
            padding: 3px 9px;
            border-radius: 6px;
            border: 1px solid rgba(56, 189, 248, 0.25);
        }
        .roi-toolbar-actions {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        .roi-btn {
            border: none;
            padding: 7px 14px;
            border-radius: 7px;
            font-weight: 600;
            font-size: 0.82rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }
        .roi-btn-primary {
            background: rgba(59, 130, 246, 0.2);
            color: #60a5fa;
            border: 1px solid var(--primary);
        }
        .roi-btn-primary:hover {
            background: var(--primary);
            color: #fff;
        }
        .roi-btn-secondary {
            background: #334155;
            color: #e2e8f0;
        }
        .roi-btn-secondary:hover { background: #475569; color: #fff; }
        .roi-btn-danger {
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.4);
        }
        .roi-btn-danger:hover { background: var(--danger); color: #fff; }
        .roi-btn-success {
            background: var(--success);
            color: #fff;
            box-shadow: 0 2px 10px rgba(16, 185, 129, 0.35);
        }
        .roi-btn-success:hover {
            background: #059669;
            transform: translateY(-1px);
        }

        .roi-canvas-container {
            background: #020617;
            border: 1px solid var(--border);
            border-radius: 10px;
            position: relative;
            min-height: 520px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.6);
        }
        #roiCanvas {
            max-width: 100%;
            max-height: calc(100vh - 340px);
            width: auto;
            height: auto;
            object-fit: contain;
            cursor: crosshair;
            display: none;
            box-shadow: 0 4px 20px rgba(0,0,0,0.6);
        }
        .roi-canvas-placeholder {
            text-align: center;
            color: var(--text-dim);
            padding: 3rem;
        }
        .roi-canvas-placeholder i {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            color: #334155;
        }
        .roi-canvas-placeholder h3 {
            color: var(--text-muted);
            margin-bottom: 6px;
            font-size: 1.1rem;
        }
        .roi-canvas-placeholder p {
            font-size: 0.85rem;
            max-width: 400px;
            margin: 0 auto;
        }
        .roi-canvas-loader {
            position: absolute;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
            color: #fff;
            font-size: 0.9rem;
            font-weight: 500;
            background: rgba(11, 17, 32, 0.85);
            padding: 24px 32px;
            border-radius: 12px;
            border: 1px solid var(--border);
            z-index: 10;
        }
        .roi-canvas-loader i {
            font-size: 2rem;
            color: var(--primary);
        }

        .roi-hud-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            background: #0f172a;
            padding: 10px 14px;
            border-radius: 10px;
            border: 1px solid var(--border);
        }
        .roi-hud-tips {
            display: flex;
            align-items: center;
            gap: 14px;
            flex-wrap: wrap;
            font-size: 0.78rem;
            color: var(--text-muted);
        }
        .hud-tip { display: flex; align-items: center; gap: 5px; }
        .hud-tip kbd {
            background: #1e293b;
            border: 1px solid var(--border);
            color: #fff;
            padding: 1px 6px;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 700;
        }
        .roi-regions-summary {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        .region-badge-pill {
            background: #1e293b;
            border: 1px solid var(--border);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.76rem;
            display: flex;
            align-items: center;
            gap: 8px;
            color: #fff;
        }
        .region-badge-pill .color-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }
        .region-delete-btn {
            background: none;
            border: none;
            color: var(--text-dim);
            cursor: pointer;
            padding: 0;
            font-size: 0.8rem;
            transition: color 0.2s;
        }
        .region-delete-btn:hover { color: var(--danger); }

        /* Toast notification */
        .roi-toast {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #10b981;
            color: #fff;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            display: none;
            align-items: center;
            gap: 10px;
            z-index: 1000;
            animation: slideInToast 0.3s ease;
        }
        @keyframes slideInToast {
            from { transform: translateY(100%); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        /* ====================================================================
           LIVE AI VIDEO PLAYER & TESTING STUDIO (PHÁT & KIỂM THỬ VIDEO TRỰC TIẾP)
           ==================================================================== */
        .player-studio-grid {
            display: grid;
            grid-template-columns: 340px 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
            align-items: start;
        }
        @media (max-width: 1024px) {
            .player-studio-grid { grid-template-columns: 1fr; }
        }

        /* Sidebar Playlist */
        .player-sidebar {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.2rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .player-sidebar-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 700;
            font-size: 0.95rem;
            color: #fff;
        }
        .player-video-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-height: 620px;
            overflow-y: auto;
            padding-right: 4px;
        }
        .player-video-card {
            background: #0f172a;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px;
            display: flex;
            gap: 12px;
            align-items: center;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
        }
        .player-video-card:hover {
            border-color: #475569;
            transform: translateX(4px);
            background: #1e293b;
        }
        .player-video-card.active {
            border-color: var(--primary);
            background: rgba(59, 130, 246, 0.14);
            box-shadow: 0 4px 14px rgba(59, 130, 246, 0.25);
        }
        .pvc-thumb-box {
            position: relative;
            width: 84px;
            height: 54px;
            border-radius: 6px;
            overflow: hidden;
            background: #000;
            flex-shrink: 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .pvc-thumb-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }
        .pvc-play-overlay {
            position: absolute;
            inset: 0;
            background: rgba(0, 0, 0, 0.35);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 0.9rem;
            opacity: 0.7;
            transition: opacity 0.2s;
        }
        .player-video-card:hover .pvc-play-overlay { opacity: 1; color: var(--primary); }
        .player-video-card.active .pvc-play-overlay {
            background: rgba(59, 130, 246, 0.45);
            opacity: 1;
            color: #fff;
        }
        .pvc-info {
            flex: 1;
            min-width: 0;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .pvc-title {
            font-size: 0.88rem;
            font-weight: 700;
            color: #fff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .pvc-meta-row {
            display: flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
        }
        .pvc-badge-roi {
            font-size: 0.68rem;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 600;
        }
        .pvc-badge-roi.has-roi { background: rgba(16, 185, 129, 0.2); color: #34d399; }
        .pvc-badge-roi.no-roi { background: rgba(148, 163, 184, 0.15); color: #94a3b8; }
        .pvc-playing-tag {
            font-size: 0.72rem;
            color: #38bdf8;
            font-weight: 700;
            display: none;
            align-items: center;
            gap: 4px;
        }
        .player-video-card.active .pvc-playing-tag { display: flex; }

        /* Cinema Player Workspace */
        .player-cinema-box {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        }
        .player-screen-frame {
            position: relative;
            background: #020617;
            width: 100%;
            height: 520px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        @media (max-width: 768px) {
            .player-screen-frame { height: 320px; }
        }
        #ai-live-stream-player {
            width: 100%;
            height: 100%;
            object-fit: contain;
            display: block;
            background: #000;
        }
        #raw-video-player {
            width: 100%;
            height: 100%;
            object-fit: contain;
            display: none;
            background: #000;
        }
        .player-screen-placeholder {
            position: absolute;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: var(--text-dim);
            gap: 12px;
            background: #070b14;
            z-index: 2;
        }
        .player-screen-placeholder i { font-size: 4rem; color: #334155; }
        .player-screen-placeholder h3 { color: #94a3b8; font-size: 1.15rem; font-weight: 700; }
        .player-screen-placeholder p { font-size: 0.85rem; max-width: 440px; text-align: center; color: var(--text-muted); }

        /* HUD Overlay on Screen */
        .player-hud-top {
            position: absolute;
            top: 14px;
            left: 14px;
            right: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;
            pointer-events: none;
        }
        .player-hud-title-badge {
            background: rgba(15, 23, 42, 0.88);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 700;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        }
        .hud-live-tag {
            background: #ef4444;
            color: #fff;
            font-size: 0.65rem;
            font-weight: 800;
            padding: 2px 7px;
            border-radius: 4px;
            letter-spacing: 0.6px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            animation: pulseLive 1.5s infinite;
        }
        @keyframes pulseLive {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .player-hud-stats-group {
            display: flex;
            gap: 8px;
        }
        .hud-stat-chip {
            background: rgba(15, 23, 42, 0.88);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 700;
            color: #38bdf8;
            font-family: 'Consolas', monospace;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Player Control Toolbar */
        .player-controls-bar {
            background: #0f172a;
            border-top: 1px solid var(--border);
            padding: 12px 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }
        .player-btn-group {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        .btn-pctrl {
            background: #1e293b;
            color: #f8fafc;
            border: 1px solid var(--border);
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.84rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 7px;
            transition: all 0.18s;
        }
        .btn-pctrl:hover { background: #334155; color: #fff; border-color: #64748b; }
        .btn-pctrl-primary {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            border-color: #2563eb;
            color: #fff;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35);
        }
        .btn-pctrl-primary:hover {
            background: linear-gradient(135deg, #60a5fa, #3b82f6);
        }
        .player-options-group {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }
        .player-mode-switch {
            display: flex;
            background: #020617;
            padding: 3px;
            border-radius: 8px;
            border: 1px solid var(--border);
        }
        .mode-btn {
            background: transparent;
            color: var(--text-muted);
            border: none;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .mode-btn.active {
            background: var(--purple);
            color: #fff;
        }

        /* Live Detection Feed Bar */
        .player-live-feed {
            background: #090e1a;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            padding: 12px 18px;
        }
        .player-live-feed-header {
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .player-live-feed-chips {
            display: flex;
            gap: 8px;
            overflow-x: auto;
            padding-bottom: 4px;
        }
        .live-obj-chip {
            background: #0f172a;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 0.8rem;
            display: flex;
            align-items: center;
            gap: 8px;
            flex-shrink: 0;
            font-weight: 600;
        }
        .live-obj-chip.chip-confirmed {
            border-color: rgba(239, 68, 68, 0.5);
            background: rgba(239, 68, 68, 0.12);
            color: #fca5a5;
        }
        .live-obj-chip.chip-suspected {
            border-color: rgba(245, 158, 11, 0.5);
            background: rgba(245, 158, 11, 0.12);
            color: #fde68a;
        }
        .live-obj-chip.chip-normal {
            border-color: rgba(16, 185, 129, 0.5);
            background: rgba(16, 185, 129, 0.12);
            color: #a7f3d0;
        }

        /* ====================================================================
           EVALUATION STUDIO (KIỂM THỬ & ĐÁNH GIÁ VIDEO)
           ==================================================================== */
        .eval-dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }
        @media (max-width: 900px) {
            .eval-dashboard-grid {
                grid-template-columns: 1fr;
            }
        }
        .eval-control-card, .eval-telemetry-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
            display: flex;
            flex-direction: column;
        }
        .eval-card-header {
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 12px;
            margin-bottom: 16px;
        }
        .eval-card-header i {
            color: var(--purple);
        }
        .eval-card-body {
            display: flex;
            flex-direction: column;
            gap: 14px;
            flex: 1;
        }
        .eval-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 6px;
            display: block;
        }
        .eval-select {
            width: 100%;
            background: #0f172a;
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 0.88rem;
            outline: none;
            transition: border-color 0.2s;
        }
        .eval-select:focus {
            border-color: var(--primary);
        }
        .eval-action-buttons {
            display: flex;
            gap: 10px;
            margin-top: auto;
            padding-top: 8px;
            flex-wrap: wrap;
        }
        .btn-eval-primary {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 10px 18px;
            font-weight: 600;
            font-size: 0.88rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
        }
        .btn-eval-primary:hover:not(:disabled) {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.5);
            background: linear-gradient(135deg, #60a5fa, #3b82f6);
        }
        .btn-eval-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .btn-eval-secondary {
            background: #334155;
            color: #f8fafc;
            border: 1px solid #475569;
            border-radius: 8px;
            padding: 10px 16px;
            font-weight: 600;
            font-size: 0.88rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
        }
        .btn-eval-secondary:hover {
            background: #475569;
        }
        .btn-eval-danger {
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            font-weight: 600;
            font-size: 0.88rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
        }
        .eval-progress-meta {
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 500;
        }
        .eval-progress-bar-bg {
            background: #0f172a;
            border-radius: 999px;
            height: 12px;
            overflow: hidden;
            border: 1px solid #334155;
            position: relative;
        }
        .eval-progress-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6, #10b981);
            width: 0%;
            border-radius: 999px;
            transition: width 0.25s ease-out;
            box-shadow: 0 0 12px rgba(59, 130, 246, 0.6);
        }
        .eval-telemetry-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 6px;
        }
        .telemetry-box {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 10px 8px;
            text-align: center;
        }
        .telemetry-val {
            font-size: 1.15rem;
            font-weight: 700;
            color: #38bdf8;
            font-family: 'Consolas', monospace;
        }
        .telemetry-lbl {
            font-size: 0.72rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.3px;
            margin-top: 2px;
        }
        .eval-console-wrapper {
            background: #070b14;
            border: 1px solid #1e293b;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
            margin-bottom: 24px;
        }
        .eval-console-header {
            background: #0f172a;
            padding: 10px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #1e293b;
        }
        .console-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #94a3b8;
            font-family: 'Consolas', monospace;
        }
        .live-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
            display: inline-block;
            box-shadow: 0 0 8px #10b981;
        }
        .console-actions {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .console-autoscroll-toggle {
            font-size: 0.78rem;
            color: var(--text-muted);
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            user-select: none;
        }
        .btn-console-clear {
            background: transparent;
            border: 1px solid #334155;
            color: var(--text-muted);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-console-clear:hover {
            color: var(--text-main);
            border-color: #64748b;
        }
        .eval-console-screen {
            padding: 14px 16px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 0.82rem;
            line-height: 1.55;
            color: #38bdf8;
            max-height: 260px;
            min-height: 150px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-break: break-all;
            margin: 0;
            background: #070b14;
        }
        .results-section-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 16px;
        }
        .results-section-title i {
            color: var(--primary);
        }
        .results-timestamp {
            font-size: 0.8rem;
            color: var(--text-muted);
            font-weight: 400;
            margin-left: auto;
        }
        .eval-crop-thumb {
            width: 60px;
            height: 60px;
            object-fit: cover;
            border-radius: 6px;
            border: 1px solid var(--border);
            cursor: pointer;
            transition: transform 0.2s, border-color 0.2s;
            background: #000;
        }
        .eval-crop-thumb:hover {
            transform: scale(1.08);
            border-color: var(--primary);
        }
        .eval-tag-tp {
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.4);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            display: inline-block;
        }
        .eval-tag-fp {
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.4);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            display: inline-block;
        }
        .eval-tag-fn {
            background: rgba(245, 158, 11, 0.2);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.4);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            display: inline-block;
        }
        .eval-tag-tn {
            background: rgba(59, 130, 246, 0.2);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.4);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            display: inline-block;
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
        <div class="nav-tabs-wrapper">
            <button id="btn-tab-violations" class="nav-tab-btn active" onclick="switchMainTab('violations')">
                <i class="fa-solid fa-clipboard-list"></i> Hồ Sơ Vi Phạm
            </button>
            <button id="btn-tab-roi" class="nav-tab-btn" onclick="switchMainTab('roi')">
                <i class="fa-solid fa-draw-polygon"></i> Studio Vẽ ROI Vỉa Hè
            </button>
            <button id="btn-tab-eval" class="nav-tab-btn" onclick="switchMainTab('eval')">
                <i class="fa-solid fa-play-circle"></i> Phát & Kiểm Thử Video AI
            </button>
        </div>
        <div class="badge-status">HỆ THỐNG ONLINE &middot; CCTV ACTIVE</div>
    </div>

    <div class="container">
        <!-- TAB 1: QUẢN LÝ VI PHẠM & PHẠT NGUỘI -->
        <div id="tab-view-violations">
            <!-- Quy trình Banner -->
        <div class="workflow-banner">
            <div class="workflow-banner-text">
                <i class="fa-solid fa-circle-info" style="color: var(--primary); margin-right: 6px;"></i>
                <strong>Quy trình xử lý chuẩn:</strong> AI phát hiện & lưu cảnh báo vào hàng chờ <strong>Pending</strong>  
                Cán bộ Đội TTĐT đối chiếu ảnh toàn cảnh/cận cảnh  <strong>Xác nhận phạt</strong> hoặc <strong>Bác bỏ</strong> (kèm lý do)  <strong>Thi hành xử phạt</strong>.
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
        </div> <!-- /#tab-view-violations -->

        <!-- TAB 2: STUDIO CẤU HÌNH VỈA HÈ (MULTI-ROI) CHO TẤT CẢ VIDEO -->
        <div id="tab-view-roi" style="display: none;">
            <!-- Banner hướng dẫn Studio -->
            <div class="workflow-banner" style="border-left-color: #10b981;">
                <div class="workflow-banner-text">
                    <i class="fa-solid fa-compass-drafting" style="color: var(--success); margin-right: 6px;"></i>
                    <strong>Studio Cấu Hình Vỉa Hè (Multi-ROI):</strong> Chọn bất kỳ video nào trong danh sách bên trái để xem và vẽ vùng vỉa hè.
                    Hỗ trợ vẽ nhiều vùng riêng biệt (vỉa hè trái, vỉa hè phải). Nhấp chuyển video ngay lập tức mà không cần chạy lại terminal!
                </div>
                <div class="roi-header-stats">
                    <span class="badge-pill-stat"><i class="fa-solid fa-video"></i> <span id="roi-video-count-badge">0</span> Video</span>
                    <span class="badge-pill-stat" style="background: rgba(16, 185, 129, 0.15); color: var(--success); border-color: rgba(16, 185, 129, 0.3);">
                        <i class="fa-solid fa-check"></i> <span id="roi-configured-count-badge">0</span> Đã có ROI
                    </span>
                </div>
            </div>

            <!-- Layout 2 cột: Danh sách Video & Canvas Workspace -->
            <div class="roi-studio-grid">
                <!-- Sidebar: Danh sách video -->
                <div class="roi-sidebar">
                    <div class="roi-sidebar-header">
                        <div class="sidebar-title">
                            <i class="fa-solid fa-film"></i>
                            <span>Tất Cả Video (data/videos)</span>
                        </div>
                        <button class="btn-sidebar-refresh" onclick="loadRoiVideos()" title="Quét lại thư mục">
                            <i class="fa-solid fa-rotate-right"></i>
                        </button>
                    </div>

                    <div class="roi-search-box">
                        <i class="fa-solid fa-magnifying-glass"></i>
                        <input type="text" id="roi-video-search" placeholder="Tìm kiếm video..." oninput="filterRoiVideoList()">
                    </div>

                    <div class="roi-video-list" id="roi-video-list">
                        <!-- Render qua JS -->
                    </div>
                </div>

                <!-- Workspace: Canvas & Công cụ vẽ -->
                <div class="roi-workspace">
                    <!-- Toolbar điều khiển -->
                    <div class="roi-toolbar">
                        <div class="roi-toolbar-left">
                            <div class="active-video-badge" id="roi-current-video-title">
                                <i class="fa-solid fa-video"></i> Chưa chọn video
                            </div>
                            <div class="roi-meta-badge" id="roi-current-meta">
                                1280 &times; 720 px
                            </div>
                            <div class="roi-cursor-coord" id="roi-cursor-coord">
                                X: 0 | Y: 0
                            </div>
                        </div>

                        <div class="roi-toolbar-actions">
                            <button class="roi-btn roi-btn-primary" onclick="finishCurrentPolygon()" title="Chốt vùng hiện tại và bắt đầu vẽ vùng tiếp theo (Phím N)">
                                <i class="fa-solid fa-plus"></i> Chốt Vùng (+ Vùng Mới)
                            </button>
                            <button class="roi-btn roi-btn-secondary" onclick="undoVertex()" title="Xóa đỉnh vừa chấm gần nhất (Chuột phải / Phím Backspace)">
                                <i class="fa-solid fa-rotate-left"></i> Hoàn Tác (Undo)
                            </button>
                            <button class="roi-btn roi-btn-secondary" onclick="clearCurrentPolygon()" title="Xóa vùng đang vẽ dở (Phím C)">
                                <i class="fa-solid fa-eraser"></i> Xóa Đang Vẽ
                            </button>
                            <button class="roi-btn roi-btn-danger" onclick="clearAllPolygons()" title="Xóa tất cả các vùng">
                                <i class="fa-solid fa-trash-can"></i> Xóa Hết
                            </button>
                            <button class="roi-btn roi-btn-success" onclick="saveRoiConfigToServer()" title="Lưu cấu hình ra file JSON (Phím S)">
                                <i class="fa-solid fa-floppy-disk"></i> Lưu Cấu Hình ROI
                            </button>
                            <button class="roi-btn" style="background: rgba(139, 92, 246, 0.22); border: 1px solid rgba(139, 92, 246, 0.5); color: #c4b5fd;" onclick="testCurrentVideoFromRoi()" title="Chuyển sang tab Đánh giá và kiểm thử ngay video này">
                                <i class="fa-solid fa-play"></i> Test Video Này
                            </button>
                        </div>
                    </div>

                    <!-- Khung Canvas -->
                    <div class="roi-canvas-container" id="roi-canvas-container">
                        <canvas id="roiCanvas"></canvas>
                        <div class="roi-canvas-placeholder" id="roi-canvas-placeholder">
                            <i class="fa-solid fa-photo-film"></i>
                            <h3>Chưa chọn video để vẽ ROI</h3>
                            <p>Nhấp vào bất kỳ video nào trong danh sách bên trái để tải khung hình và cấu hình tọa độ vỉa hè.</p>
                        </div>
                        <div class="roi-canvas-loader" id="roi-canvas-loader" style="display: none;">
                            <i class="fa-solid fa-circle-notch fa-spin"></i>
                            <span>Đang trích xuất khung hình video...</span>
                        </div>
                    </div>

                    <!-- HUD hướng dẫn & Tóm tắt vùng đã vẽ -->
                    <div class="roi-hud-bar">
                        <div class="roi-hud-tips">
                            <span class="hud-tip"><i class="fa-solid fa-mouse"></i> <strong>Chuột trái:</strong> Chấm đỉnh</span>
                            <span class="hud-tip"><i class="fa-solid fa-mouse-pointer"></i> <strong>Chuột phải:</strong> Undo đỉnh</span>
                            <span class="hud-tip"><kbd>N</kbd> Chốt vùng mới</span>
                            <span class="hud-tip"><kbd>S</kbd> Lưu JSON</span>
                            <span class="hud-tip"><kbd>C</kbd> Xóa điểm dở</span>
                        </div>
                        <div class="roi-regions-summary" id="roi-regions-summary">
                            <!-- Các badge vùng vỉa hè được render qua JS -->
                        </div>
                    </div>
                </div>
            </div>
        </div> <!-- /#tab-view-roi -->

        <!-- TAB 3: PHÁT & KIỂM THỬ VIDEO AI TRỰC TIẾP (LIVE AI VIDEO PLAYER) -->
        <div id="tab-view-eval" style="display: none;">
            <!-- Workflow Banner -->
            <div class="workflow-banner" style="border-left-color: #8b5cf6;">
                <div class="workflow-banner-text">
                    <i class="fa-solid fa-play-circle" style="color: var(--purple); margin-right: 6px;"></i>
                    <strong>Phát & Kiểm Thử Video AI Trực Tiếp (Live Video Player & Testing):</strong>
                    Chọn bất kỳ video nào trong danh sách bên trái để phát trực tiếp kèm thuật toán YOLOv8 nhận diện, ByteTrack bám vết và phán quyết lấn chiếm vỉa hè theo thời gian thực!
                </div>
                <div class="roi-header-stats">
                    <span class="badge-pill-stat" id="player-active-video-pill">
                        <i class="fa-solid fa-film"></i> <span id="player-active-video-name">Chưa chọn video</span>
                    </span>
                    <span class="badge-pill-stat" style="background: rgba(16, 185, 129, 0.15); color: var(--success); border-color: rgba(16, 185, 129, 0.3);">
                        <i class="fa-solid fa-circle" id="player-status-dot" style="font-size: 8px;"></i>
                        <span id="player-status-text">Sẵn Sàng</span>
                    </span>
                </div>
            </div>

            <!-- Two-column Grid: Danh sách Video (Trái) & Khung Chiếu Video (Phải) -->
            <div class="player-studio-grid">
                <!-- Cột trái: Playlist tất cả video -->
                <div class="player-sidebar">
                    <div class="player-sidebar-header">
                        <div class="sidebar-title">
                            <i class="fa-solid fa-film" style="color: var(--primary);"></i>
                            <span>Danh Sách Video (data/videos)</span>
                        </div>
                        <button class="btn-sidebar-refresh" onclick="loadPlayerVideos()" title="Quét lại thư mục video">
                            <i class="fa-solid fa-rotate-right"></i>
                        </button>
                    </div>

                    <div class="roi-search-box">
                        <i class="fa-solid fa-magnifying-glass"></i>
                        <input type="text" id="player-video-search" placeholder="Tìm video..." oninput="filterPlayerVideoList()">
                    </div>

                    <div class="player-video-list" id="player-video-list">
                        <!-- Rendered by JS -->
                    </div>
                </div>

                <!-- Cột phải: Khung Chiếu Cinema Player & Điều Khiển -->
                <div class="player-cinema-box">
                    <!-- Khung Màn Hình Video 16:9 -->
                    <div class="player-screen-frame">
                        <!-- HUD nổi trên video -->
                        <div class="player-hud-top" id="player-hud-top">
                            <div class="player-hud-title-badge">
                                <span class="hud-live-tag">LIVE AI</span>
                                <span id="player-hud-title">Chưa chọn video</span>
                            </div>
                            <div class="player-hud-stats-group">
                                <div class="hud-stat-chip"><i class="fa-solid fa-gauge"></i> <span id="player-stat-fps">0.0 FPS</span></div>
                                <div class="hud-stat-chip"><i class="fa-solid fa-clock"></i> <span id="player-stat-frame">Khung 0/0</span></div>
                                <div class="hud-stat-chip" style="color: #f87171;"><i class="fa-solid fa-triangle-exclamation"></i> <span id="player-stat-viol">0 Vi Phạm</span></div>
                            </div>
                        </div>

                        <!-- 1. Trình phát luồng AI (MJPEG Stream) -->
                        <img id="ai-live-stream-player" src="" alt="Luồng Video AI">

                        <!-- 2. Trình phát Video Gốc (HTML5 MP4) -->
                        <video id="raw-video-player" controls playsinline></video>

                        <!-- Màn hình chờ khi chưa chọn video -->
                        <div class="player-screen-placeholder" id="player-screen-placeholder">
                            <i class="fa-solid fa-circle-play"></i>
                            <h3>Chưa chọn video để phát</h3>
                            <p>Nhấp vào bất kỳ video nào trong danh sách bên trái để phát trực tiếp kèm nhận diện AI và phán quyết vi phạm.</p>
                        </div>
                    </div>

                    <!-- Thanh Điều Khiển Phát Video -->
                    <div class="player-controls-bar">
                        <div class="player-btn-group">
                            <button id="btn-player-play" class="btn-pctrl btn-pctrl-primary" onclick="resumeLiveStream()" title="Tiếp tục phát">
                                <i class="fa-solid fa-play"></i> Phát Video
                            </button>
                            <button id="btn-player-pause" class="btn-pctrl" onclick="pauseLiveStream()" title="Tạm dừng phát">
                                <i class="fa-solid fa-pause"></i> Tạm Dừng
                            </button>
                            <button class="btn-pctrl" onclick="restartLiveStream()" title="Phát lại từ đầu">
                                <i class="fa-solid fa-rotate-left"></i> Phát Lại
                            </button>
                            <button class="btn-pctrl" onclick="stopLiveStream()" title="Dừng phát">
                                <i class="fa-solid fa-stop"></i> Dừng
                            </button>
                        </div>

                        <div class="player-options-group">
                            <!-- Chuyển đổi chế độ: AI vs Video Gốc -->
                            <div class="player-mode-switch">
                                <button id="mode-btn-ai" class="mode-btn active" onclick="setPlayerMode('ai')">
                                    <i class="fa-solid fa-robot"></i> Lớp Phủ AI
                                </button>
                                <button id="mode-btn-raw" class="mode-btn" onclick="setPlayerMode('raw')">
                                    <i class="fa-solid fa-film"></i> Video Gốc (MP4)
                                </button>
                            </div>

                            <!-- Độ nhạy (Confidence) -->
                            <select id="player-conf-select" class="eval-select" style="width: auto; padding: 6px 10px; font-size: 0.8rem;" onchange="onPlayerSettingChange()" title="Độ nhạy AI (Confidence Threshold)">
                                <option value="0.10">Độ nhạy: Rất cao (10% - Bắt tối đa)</option>
                                <option value="0.15" selected>Độ nhạy: Cao (15% - Bắt biển nhỏ)</option>
                                <option value="0.20">Độ nhạy: Trung bình (20%)</option>
                                <option value="0.30">Độ nhạy: Khắt khe (30%)</option>
                            </select>

                            <!-- Độ phân giải AI (Imgsz) -->
                            <select id="player-imgsz-select" class="eval-select" style="width: auto; padding: 6px 10px; font-size: 0.8rem;" onchange="onPlayerSettingChange()" title="Độ phân giải nạp vào AI">
                                <option value="1280">Độ nét: 1280px (Cực nét - Bắt xa)</option>
                                <option value="960" selected>Độ nét: 960px (Cân bằng Tốc độ/Nét)</option>
                                <option value="640">Độ nét: 640px (Tốc độ cao nhất)</option>
                            </select>

                            <!-- Lựa chọn Frame Skip -->
                            <select id="player-skip-select" class="eval-select" style="width: auto; padding: 6px 10px; font-size: 0.8rem;" onchange="onPlayerSkipChange()" title="Bỏ qua khung hình">
                                <option value="1">Tần suất: Chuẩn (Skip 1 - Mượt)</option>
                                <option value="0">Tất cả khung hình (Skip 0)</option>
                                <option value="2">Siêu tốc độ (Skip 2 - Edge AI)</option>
                            </select>
                        </div>
                    </div>

                    <!-- Dòng Sự Kiện Vi Phạm Thời Gian Thực -->
                    <div class="player-live-feed">
                        <div class="player-live-feed-header">
                            <i class="fa-solid fa-bullseye" style="color: var(--primary);"></i>
                            <span>Đối tượng nhận diện & phán quyết trong video</span>
                        </div>
                        <div class="player-live-feed-chips" id="player-live-chips">
                            <span style="font-size: 0.8rem; color: var(--text-dim); padding: 4px 0;">Đang kết nối luồng AI...</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Bảng Mở Rộng: Chỉ Số Đánh Giá Học Thuật & Ground Truth -->
            <div style="background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; margin-bottom: 24px; overflow: hidden;">
                <div onclick="toggleEvalAcademicMetrics()" style="cursor: pointer; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; background: #0f172a; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
                    <div style="font-weight: 700; font-size: 0.95rem; display: flex; align-items: center; gap: 10px; color: #fff;">
                        <i class="fa-solid fa-chart-pie" style="color: var(--primary);"></i>
                        <span>Chỉ Số Đánh Giá Học Thuật Toàn Hệ Thống & Bảng Đối Chiếu Ground Truth (16 Mẫu)</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <button class="btn-eval-primary" style="padding: 6px 12px; font-size: 0.78rem;" onclick="event.stopPropagation(); startEvaluation();" title="Chạy đánh giá toàn diện ngầm">
                            <i class="fa-solid fa-flask"></i> Chạy Full Đánh Giá
                        </button>
                        <i id="eval-metrics-chevron" class="fa-solid fa-chevron-down" style="color: var(--text-muted); transition: transform 0.2s;"></i>
                    </div>
                </div>

                <div id="eval-academic-body" style="padding: 20px; display: none;">
                    <div class="stats-grid" id="eval-kpi-grid">
                        <!-- Rendered by JS -->
                    </div>

                    <div class="table-container" style="margin-top: 20px;">
                        <div class="table-header-title" style="padding: 16px 20px 8px; font-weight: 700; color: var(--text-main); display: flex; align-items: center; gap: 8px;">
                            <i class="fa-solid fa-table-list" style="color: var(--primary);"></i>
                            Bảng Đối Sánh Chi Tiết Từng Đối Tượng Với Ground Truth (16 Mẫu Thực Địa)
                        </div>
                        <table class="data-table" id="eval-gt-table">
                            <thead>
                                <tr>
                                    <th style="width: 75px;">Video</th>
                                    <th style="width: 65px; text-align: center;">Track ID</th>
                                    <th style="width: 75px; text-align: center;">Ảnh Crop</th>
                                    <th>Tên Biển Hiệu / Đối Tượng</th>
                                    <th style="width: 75px; text-align: center;">Số Khung</th>
                                    <th style="width: 80px; text-align: center;">Độ Tin Cậy</th>
                                    <th style="width: 85px; text-align: center;">% Lấn Chiếm</th>
                                    <th style="width: 125px; text-align: center;">Kết Luận AI</th>
                                    <th>Cơ Sở Thực Tế (Ground Truth)</th>
                                    <th style="width: 110px; text-align: center;">Phân Loại</th>
                                </tr>
                            </thead>
                            <tbody id="eval-gt-tbody">
                                <!-- Rendered by JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div> <!-- /#tab-view-eval -->
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

    <!-- Toast Notification for ROI Studio -->
    <div class="roi-toast" id="roi-toast"></div>

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
                                <strong> Người duyệt:</strong> ${v.reviewed_by || 'Cán bộ TTĐT'}<br>
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
                                <strong> Lý do bác bỏ:</strong> ${v.dismiss_reason || 'Không có lý do chi tiết'}<br>
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

        /* ====================================================================
           CHUYỂN ĐỔI TAB CHÍNH: HỒ SƠ VI PHẠM <-> STUDIO ROI <-> KIỂM THỬ VIDEO
           ==================================================================== */
        function switchMainTab(tabName) {
            const tabViol = document.getElementById('tab-view-violations');
            const tabRoi = document.getElementById('tab-view-roi');
            const tabEval = document.getElementById('tab-view-eval');
            const btnViol = document.getElementById('btn-tab-violations');
            const btnRoi = document.getElementById('btn-tab-roi');
            const btnEval = document.getElementById('btn-tab-eval');

            // Ẩn tất cả tab và bỏ active class
            if (tabViol) tabViol.style.display = 'none';
            if (tabRoi) tabRoi.style.display = 'none';
            if (tabEval) tabEval.style.display = 'none';
            if (btnViol) btnViol.classList.remove('active');
            if (btnRoi) btnRoi.classList.remove('active');
            if (btnEval) btnEval.classList.remove('active');

            if (tabName === 'roi') {
                if (tabRoi) tabRoi.style.display = 'block';
                if (btnRoi) btnRoi.classList.add('active');
                if (allVideosList.length === 0) {
                    loadRoiVideos();
                }
            } else if (tabName === 'eval') {
                if (tabEval) tabEval.style.display = 'block';
                if (btnEval) btnEval.classList.add('active');
                initEvalTab();
            } else {
                if (tabViol) tabViol.style.display = 'block';
                if (btnViol) btnViol.classList.add('active');
                loadData();
            }
        }

        /* ====================================================================
           STUDIO VẼ & CẤU HÌNH VỈA HÈ TƯƠNG TÁC (MULTI-ROI STUDIO)
           ==================================================================== */
        let allVideosList = [];
        let currentVideo = null;
        let currentImage = null;
        let completedPolygons = [];
        let activePolygon = [];
        let mousePos = null;

        const canvas = document.getElementById('roiCanvas');
        const ctx = canvas ? canvas.getContext('2d') : null;

        const REGION_PALETTE = [
            { fill: 'rgba(0, 200, 255, 0.28)', stroke: '#00e5ff', text: '#00e5ff', dot: '#00e5ff' },
            { fill: 'rgba(16, 185, 129, 0.28)', stroke: '#10b981', text: '#10b981', dot: '#10b981' },
            { fill: 'rgba(139, 92, 246, 0.28)', stroke: '#a855f7', text: '#c084fc', dot: '#a855f7' },
            { fill: 'rgba(245, 158, 11, 0.28)', stroke: '#f59e0b', text: '#fbbf24', dot: '#f59e0b' }
        ];

        async function loadRoiVideos() {
            try {
                const res = await fetch('/api/roi/videos');
                if (!res.ok) throw new Error('Không thể tải danh sách video');
                allVideosList = await res.json();

                renderRoiVideoList(allVideosList);

                // Cập nhật thống kê
                const total = allVideosList.length;
                const configured = allVideosList.filter(v => v.has_roi).length;
                document.getElementById('roi-video-count-badge').innerText = total;
                document.getElementById('roi-configured-count-badge').innerText = configured;

                // Tự động nạp video đầu tiên nếu chưa chọn
                if (!currentVideo && allVideosList.length > 0) {
                    selectVideoByIndex(0);
                }
            } catch (err) {
                console.error('Lỗi loadRoiVideos:', err);
            }
        }

        function renderRoiVideoList(videos) {
            const listEl = document.getElementById('roi-video-list');
            if (!videos || videos.length === 0) {
                listEl.innerHTML = `
                    <div style="text-align: center; color: var(--text-dim); padding: 2rem 1rem; font-size: 0.85rem;">
                        <i class="fa-solid fa-folder-open" style="font-size: 2rem; margin-bottom: 8px; color: #334155;"></i>
                        <p>Không tìm thấy video nào trong thư mục data/videos/</p>
                    </div>
                `;
                return;
            }

            listEl.innerHTML = videos.map((v, idx) => {
                const isActive = currentVideo && currentVideo.filename === v.filename ? 'active' : '';
                const statusBadge = v.has_roi
                    ? `<span class="badge-roi-status configured"><i class="fa-solid fa-circle-check"></i> Đã có ROI (${v.regions_count} vùng / ${v.points_count} đỉnh)</span>`
                    : `<span class="badge-roi-status missing"><i class="fa-solid fa-circle-exclamation"></i> Chưa có ROI</span>`;

                return `
                    <div class="roi-video-card ${isActive}" id="vid-card-${idx}" onclick="selectVideoByIndex(${idx})">
                        <div class="roi-video-card-top">
                            <div class="roi-video-filename">
                                <i class="fa-solid fa-video"></i> ${v.filename}
                            </div>
                        </div>
                        <div>${statusBadge}</div>
                        <div class="roi-video-meta">
                            <span><i class="fa-solid fa-expand"></i> ${v.width}&times;${v.height}</span>
                            <span><i class="fa-solid fa-gauge"></i> ${v.fps} FPS</span>
                            <span><i class="fa-solid fa-hard-drive"></i> ${v.size_mb} MB</span>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function filterRoiVideoList() {
            const q = (document.getElementById('roi-video-search').value || '').toLowerCase().trim();
            const filtered = allVideosList.filter(v => v.filename.toLowerCase().includes(q));
            renderRoiVideoList(filtered);
        }

        function selectVideoByIndex(idx) {
            if (idx >= 0 && idx < allVideosList.length) {
                selectVideo(allVideosList[idx].filename);
            }
        }

        async function selectVideo(fname) {
            const vid = allVideosList.find(v => v.filename === fname);
            if (!vid) return;

            currentVideo = vid;

            // Highlight card
            document.querySelectorAll('.roi-video-card').forEach(c => c.classList.remove('active'));
            const idx = allVideosList.findIndex(v => v.filename === fname);
            const activeEl = document.getElementById(`vid-card-${idx}`);
            if (activeEl) activeEl.classList.add('active');

            // Show loader
            const loader = document.getElementById('roi-canvas-loader');
            if (loader) loader.style.display = 'flex';

            activePolygon = [];
            completedPolygons = [];

            try {
                const [configRes, imgRes] = await Promise.all([
                    fetch(`/api/roi/config?video=${encodeURIComponent(fname)}`).then(r => r.json()),
                    fetch(`/api/roi/frame?video=${encodeURIComponent(fname)}`)
                ]);

                if (!imgRes.ok) throw new Error("Không thể trích xuất khung hình từ video");

                const blob = await imgRes.blob();
                const imgUrl = URL.createObjectURL(blob);
                const img = new Image();

                img.onload = () => {
                    currentImage = img;
                    canvas.width = img.naturalWidth || vid.width || 1280;
                    canvas.height = img.naturalHeight || vid.height || 720;

                    if (configRes && configRes.polygons && configRes.polygons.length > 0) {
                        completedPolygons = JSON.parse(JSON.stringify(configRes.polygons));
                    }

                    // Cập nhật toolbar
                    document.getElementById('roi-current-video-title').innerHTML = `<i class="fa-solid fa-video"></i> ${vid.filename}`;
                    document.getElementById('roi-current-meta').innerText = `${canvas.width} × ${canvas.height} px (${vid.fps} FPS)`;

                    document.getElementById('roi-canvas-placeholder').style.display = 'none';
                    canvas.style.display = 'block';
                    if (loader) loader.style.display = 'none';

                    updateRegionsSummary();
                    redrawCanvas();
                };
                img.src = imgUrl;
            } catch (err) {
                console.error('Lỗi selectVideo:', err);
                if (loader) loader.style.display = 'none';
                alert('Không thể mở video: ' + err.message);
            }
        }

        function getCanvasCoords(e) {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            let x = Math.round((e.clientX - rect.left) * scaleX);
            let y = Math.round((e.clientY - rect.top) * scaleY);
            x = Math.max(0, Math.min(canvas.width, x));
            y = Math.max(0, Math.min(canvas.height, y));
            return { x, y };
        }

        function redrawCanvas() {
            if (!ctx || !currentImage) return;

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(currentImage, 0, 0, canvas.width, canvas.height);

            // 1. Vẽ các polygon đã chốt
            completedPolygons.forEach((poly, polyIdx) => {
                if (!poly || poly.length < 3) return;
                const color = REGION_PALETTE[polyIdx % REGION_PALETTE.length];

                ctx.beginPath();
                ctx.moveTo(poly[0][0], poly[0][1]);
                for (let i = 1; i < poly.length; i++) {
                    ctx.lineTo(poly[i][0], poly[i][1]);
                }
                ctx.closePath();
                ctx.fillStyle = color.fill;
                ctx.fill();
                ctx.strokeStyle = color.stroke;
                ctx.lineWidth = 3;
                ctx.stroke();

                // Vẽ các đỉnh
                poly.forEach((pt, ptIdx) => {
                    ctx.beginPath();
                    ctx.arc(pt[0], pt[1], 5, 0, Math.PI * 2);
                    ctx.fillStyle = '#ffffff';
                    ctx.fill();
                    ctx.strokeStyle = color.stroke;
                    ctx.lineWidth = 2;
                    ctx.stroke();
                });

                // Vẽ nhãn vùng
                const firstPt = poly[0];
                const labelText = `[VỈA HÈ #${polyIdx + 1}] (${poly.length} đỉnh)`;
                ctx.font = 'bold 15px Inter, sans-serif';
                const tw = ctx.measureText(labelText).width;
                const lx = firstPt[0] + 8;
                const ly = Math.max(22, firstPt[1] - 12);

                ctx.fillStyle = 'rgba(15, 23, 42, 0.88)';
                ctx.fillRect(lx, ly - 18, tw + 14, 24);
                ctx.strokeStyle = color.stroke;
                ctx.lineWidth = 1;
                ctx.strokeRect(lx, ly - 18, tw + 14, 24);
                ctx.fillStyle = color.text;
                ctx.fillText(labelText, lx + 7, ly);
            });

            // 2. Vẽ polygon đang chấm dở
            if (activePolygon.length > 0) {
                ctx.beginPath();
                ctx.moveTo(activePolygon[0][0], activePolygon[0][1]);
                for (let i = 1; i < activePolygon.length; i++) {
                    ctx.lineTo(activePolygon[i][0], activePolygon[i][1]);
                }
                if (mousePos) {
                    ctx.lineTo(mousePos.x, mousePos.y);
                }
                ctx.strokeStyle = '#f59e0b';
                ctx.lineWidth = 2.5;
                ctx.setLineDash([6, 4]);
                ctx.stroke();
                ctx.setLineDash([]);

                if (activePolygon.length >= 3) {
                    ctx.closePath();
                    ctx.fillStyle = 'rgba(245, 158, 11, 0.18)';
                    ctx.fill();
                }

                activePolygon.forEach((pt, ptIdx) => {
                    ctx.beginPath();
                    ctx.arc(pt[0], pt[1], 6, 0, Math.PI * 2);
                    ctx.fillStyle = '#ef4444';
                    ctx.fill();
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 2;
                    ctx.stroke();

                    ctx.font = 'bold 13px Inter, sans-serif';
                    ctx.fillStyle = '#f59e0b';
                    ctx.fillText(`P${ptIdx + 1}`, pt[0] + 8, pt[1] - 5);
                });
            }
        }

        function finishCurrentPolygon() {
            if (activePolygon.length < 3) {
                showToast('Một vùng vỉa hè cần tối thiểu 3 đỉnh!', true);
                return;
            }
            completedPolygons.push([...activePolygon]);
            activePolygon = [];
            updateRegionsSummary();
            redrawCanvas();
            showToast(`Đã chốt Vỉa hè #${completedPolygons.length}! Bạn có thể vẽ tiếp vùng khác.`);
        }

        function undoVertex() {
            if (activePolygon.length > 0) {
                activePolygon.pop();
                redrawCanvas();
            } else if (completedPolygons.length > 0) {
                activePolygon = completedPolygons.pop();
                updateRegionsSummary();
                redrawCanvas();
                showToast('Đã mở lại vùng trước để chỉnh sửa tiếp.');
            }
        }

        function clearCurrentPolygon() {
            if (activePolygon.length > 0) {
                activePolygon = [];
                redrawCanvas();
                showToast('Đã xóa vùng đang vẽ dở.');
            }
        }

        function clearAllPolygons() {
            if (completedPolygons.length === 0 && activePolygon.length === 0) return;
            if (confirm('Bạn có chắc chắn muốn xóa TẤT CẢ các vùng vỉa hè của video này?')) {
                completedPolygons = [];
                activePolygon = [];
                updateRegionsSummary();
                redrawCanvas();
                showToast('Đã xóa tất cả các vùng.');
            }
        }

        function deleteRegion(idx) {
            if (idx >= 0 && idx < completedPolygons.length) {
                completedPolygons.splice(idx, 1);
                updateRegionsSummary();
                redrawCanvas();
                showToast(`Đã xóa vùng vỉa hè #${idx + 1}.`);
            }
        }

        function updateRegionsSummary() {
            const container = document.getElementById('roi-regions-summary');
            if (!container) return;

            if (completedPolygons.length === 0) {
                container.innerHTML = `<span style="font-size: 0.78rem; color: var(--text-dim);">Chưa chốt vùng nào</span>`;
                return;
            }

            container.innerHTML = completedPolygons.map((poly, idx) => {
                const color = REGION_PALETTE[idx % REGION_PALETTE.length];
                return `
                    <div class="region-badge-pill">
                        <span class="color-dot" style="background: ${color.dot};"></span>
                        <span>Vỉa hè #${idx + 1} (${poly.length} đỉnh)</span>
                        <button class="region-delete-btn" onclick="deleteRegion(${idx})" title="Xóa vùng này">
                            <i class="fa-solid fa-xmark"></i>
                        </button>
                    </div>
                `;
            }).join('');
        }

        async function saveRoiConfigToServer() {
            if (!currentVideo) {
                alert('Vui lòng chọn 1 video trước khi lưu!');
                return;
            }

            if (activePolygon.length >= 3) {
                completedPolygons.push([...activePolygon]);
                activePolygon = [];
            }

            if (completedPolygons.length === 0) {
                alert('Chưa có vùng vỉa hè nào được vẽ! Hãy chấm ít nhất 3 điểm trên khung hình.');
                return;
            }

            try {
                const payload = {
                    video: currentVideo.filename,
                    polygons: completedPolygons,
                    resolution: {
                        width: canvas.width,
                        height: canvas.height
                    }
                };

                const res = await fetch('/api/roi/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await res.json();
                if (res.ok && data.ok) {
                    showToast(`Đã lưu thành công ${data.total_regions} vùng vào ${data.config_filename}!`);

                    // Cập nhật trạng thái trong video list
                    currentVideo.has_roi = true;
                    currentVideo.regions_count = data.total_regions;
                    currentVideo.points_count = data.total_points;

                    renderRoiVideoList(allVideosList);
                    const configured = allVideosList.filter(v => v.has_roi).length;
                    document.getElementById('roi-configured-count-badge').innerText = configured;

                    updateRegionsSummary();
                    redrawCanvas();
                } else {
                    alert('Lỗi lưu cấu hình: ' + (data.error || 'Không xác định'));
                }
            } catch (err) {
                console.error('Lỗi lưu cấu hình:', err);
                alert('Lỗi kết nối máy chủ khi lưu cấu hình.');
            }
        }

        function showToast(msg, isWarn = false) {
            const toast = document.getElementById('roi-toast');
            if (!toast) return;
            toast.style.background = isWarn ? '#f59e0b' : '#10b981';
            toast.innerHTML = `<i class="fa-solid ${isWarn ? 'fa-triangle-exclamation' : 'fa-circle-check'}"></i> ${msg}`;
            toast.style.display = 'flex';
            clearTimeout(toast._timer);
            toast._timer = setTimeout(() => {
                toast.style.display = 'none';
            }, 3500);
        }

        // Lắng nghe sự kiện Canvas
        if (canvas) {
            canvas.addEventListener('mousedown', (e) => {
                if (!currentImage) return;
                const coords = getCanvasCoords(e);

                if (e.button === 0) { // Chuột trái: Thêm đỉnh
                    activePolygon.push([coords.x, coords.y]);
                    redrawCanvas();
                } else if (e.button === 2) { // Chuột phải: Undo đỉnh
                    e.preventDefault();
                    undoVertex();
                }
            });

            canvas.addEventListener('mousemove', (e) => {
                if (!currentImage) return;
                const coords = getCanvasCoords(e);
                mousePos = coords;
                document.getElementById('roi-cursor-coord').innerText = `X: ${coords.x} | Y: ${coords.y}`;
                if (activePolygon.length > 0) {
                    redrawCanvas();
                }
            });

            canvas.addEventListener('mouseleave', () => {
                mousePos = null;
                if (activePolygon.length > 0) redrawCanvas();
            });

            canvas.addEventListener('contextmenu', (e) => {
                e.preventDefault();
            });
        }

        // Lắng nghe phím tắt bàn phím
        window.addEventListener('keydown', (e) => {
            const tabRoi = document.getElementById('tab-view-roi');
            if (!tabRoi || tabRoi.style.display === 'none') return;

            if (e.key === 'n' || e.key === 'N') {
                finishCurrentPolygon();
            } else if (e.key === 's' || e.key === 'S') {
                if (e.ctrlKey) e.preventDefault();
                saveRoiConfigToServer();
            } else if (e.key === 'c' || e.key === 'C') {
                clearCurrentPolygon();
            } else if (e.key === 'Escape') {
                clearCurrentPolygon();
            } else if ((e.ctrlKey && (e.key === 'z' || e.key === 'Z')) || e.key === 'Backspace') {
                if (e.target.tagName !== 'INPUT') {
                    e.preventDefault();
                    undoVertex();
                }
            }
        });

        /* ====================================================================
           LIVE AI VIDEO PLAYER & EVALUATION STUDIO
           ==================================================================== */
        let currentStreamVideo = null;
        let currentStreamToken = null;
        let streamTelemetryInterval = null;
        let currentFrameSkip = 1;
        let currentConfidence = 0.15;
        let currentImgsz = 960;
        let currentPlayerMode = 'ai'; // 'ai' or 'raw'
        let allPlayerVideos = [];

        let evalPollInterval = null;
        let evalLogOffset = 0;
        let evalRunning = false;

        function initEvalTab() {
            initPlayerStudio();
            checkInitialEvalStatus();
            loadEvaluationResults();
        }

        async function initPlayerStudio() {
            await loadPlayerVideos();
        }

        async function loadPlayerVideos() {
            try {
                const res = await fetch('/api/roi/videos');
                allPlayerVideos = await res.json();
                renderPlayerVideoList(allPlayerVideos);

                // Nếu chưa có video nào được chọn, phát video đầu tiên
                if (!currentStreamVideo && allPlayerVideos.length > 0) {
                    selectAndPlayVideo(allPlayerVideos[0].filename);
                }
            } catch (e) {
                console.error('Lỗi tải danh sách video:', e);
            }
        }

        function renderPlayerVideoList(videos) {
            const container = document.getElementById('player-video-list');
            if (!container) return;

            if (!videos || videos.length === 0) {
                container.innerHTML = `<div style="text-align: center; color: var(--text-dim); padding: 2rem 1rem;">Không có video nào trong data/videos/</div>`;
                return;
            }

            container.innerHTML = videos.map(v => {
                const isActive = (currentStreamVideo === v.filename);
                const roiBadge = v.has_roi
                    ? `<span class="pvc-badge-roi has-roi"><i class="fa-solid fa-check"></i> Đã có ROI</span>`
                    : `<span class="pvc-badge-roi no-roi"><i class="fa-solid fa-circle-question"></i> Chưa có ROI</span>`;

                return `
                    <div class="player-video-card ${isActive ? 'active' : ''}" data-video="${v.filename}" onclick="selectAndPlayVideo('${v.filename}')">
                        <div class="pvc-thumb-box">
                            <img src="/api/roi/frame?video=${encodeURIComponent(v.filename)}" class="pvc-thumb-img" alt="${v.filename}">
                            <div class="pvc-play-overlay">
                                <i class="fa-solid fa-play"></i>
                            </div>
                        </div>
                        <div class="pvc-info">
                            <div class="pvc-title" title="${v.filename}">${v.filename}</div>
                            <div class="pvc-meta-row">
                                ${roiBadge}
                                <span style="font-size: 0.72rem; color: var(--text-muted);">${v.resolution ? v.resolution.width + 'x' + v.resolution.height : '720p'}</span>
                            </div>
                            <div class="pvc-playing-tag">
                                <i class="fa-solid fa-circle-play"></i> Đang phát
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function filterPlayerVideoList() {
            const q = (document.getElementById('player-video-search').value || '').toLowerCase().trim();
            const filtered = allPlayerVideos.filter(v => v.filename.toLowerCase().includes(q));
            renderPlayerVideoList(filtered);
        }

        function selectAndPlayVideo(videoName) {
            currentStreamVideo = videoName;
            currentStreamToken = Date.now();

            // Cập nhật giao diện thẻ được chọn
            document.querySelectorAll('.player-video-card').forEach(c => {
                if (c.getAttribute('data-video') === videoName) {
                    c.classList.add('active');
                } else {
                    c.classList.remove('active');
                }
            });

            // Ẩn placeholder
            const placeholder = document.getElementById('player-screen-placeholder');
            if (placeholder) placeholder.style.display = 'none';

            // Cập nhật tiêu đề HUD
            const titleElem = document.getElementById('player-hud-title');
            if (titleElem) titleElem.textContent = videoName;
            const activePill = document.getElementById('player-active-video-name');
            if (activePill) activePill.textContent = videoName;
            const statusText = document.getElementById('player-status-text');
            if (statusText) statusText.textContent = 'Đang Phát Trực Tiếp';

            updatePlayerSource();

            // Bắt đầu telemetry polling
            if (streamTelemetryInterval) clearInterval(streamTelemetryInterval);
            streamTelemetryInterval = setInterval(pollStreamTelemetry, 500);
        }

        function updatePlayerSource() {
            if (!currentStreamVideo) return;
            const imgPlayer = document.getElementById('ai-live-stream-player');
            const rawPlayer = document.getElementById('raw-video-player');

            if (currentPlayerMode === 'ai') {
                if (rawPlayer) {
                    rawPlayer.pause();
                    rawPlayer.style.display = 'none';
                }
                if (imgPlayer) {
                    imgPlayer.style.display = 'block';
                    imgPlayer.src = `/api/stream/video?name=${encodeURIComponent(currentStreamVideo)}&token=${currentStreamToken}&skip=${currentFrameSkip}&overlay=1&conf=${currentConfidence}&imgsz=${currentImgsz}`;
                }
            } else {
                if (imgPlayer) {
                    imgPlayer.style.display = 'none';
                    imgPlayer.src = '';
                }
                if (rawPlayer) {
                    rawPlayer.style.display = 'block';
                    rawPlayer.src = `/videos/${encodeURIComponent(currentStreamVideo)}`;
                    rawPlayer.play().catch(e => console.log('Autoplay:', e));
                }
            }
        }

        function pauseLiveStream() {
            const rawPlayer = document.getElementById('raw-video-player');
            if (currentPlayerMode === 'raw' && rawPlayer) {
                rawPlayer.pause();
            } else {
                currentStreamToken = 0;
            }
            const statusText = document.getElementById('player-status-text');
            if (statusText) statusText.textContent = 'Tạm Dừng';
        }

        function resumeLiveStream() {
            if (!currentStreamVideo) {
                if (allPlayerVideos.length > 0) selectAndPlayVideo(allPlayerVideos[0].filename);
                return;
            }
            currentStreamToken = Date.now();
            updatePlayerSource();
            const statusText = document.getElementById('player-status-text');
            if (statusText) statusText.textContent = 'Đang Phát Trực Tiếp';
        }

        function restartLiveStream() {
            if (!currentStreamVideo) return;
            currentStreamToken = Date.now();
            const rawPlayer = document.getElementById('raw-video-player');
            if (currentPlayerMode === 'raw' && rawPlayer) {
                rawPlayer.currentTime = 0;
                rawPlayer.play().catch(e => {});
            } else {
                updatePlayerSource();
            }
        }

        function stopLiveStream() {
            currentStreamToken = 0;
            const imgPlayer = document.getElementById('ai-live-stream-player');
            if (imgPlayer) {
                imgPlayer.src = '';
                imgPlayer.style.display = 'none';
            }
            const rawPlayer = document.getElementById('raw-video-player');
            if (rawPlayer) {
                rawPlayer.pause();
                rawPlayer.style.display = 'none';
            }
            const placeholder = document.getElementById('player-screen-placeholder');
            if (placeholder) placeholder.style.display = 'flex';
            if (streamTelemetryInterval) {
                clearInterval(streamTelemetryInterval);
                streamTelemetryInterval = null;
            }
            const statusText = document.getElementById('player-status-text');
            if (statusText) statusText.textContent = 'Đã Dừng';
        }

        function setPlayerMode(mode) {
            currentPlayerMode = mode;
            const btnAi = document.getElementById('mode-btn-ai');
            const btnRaw = document.getElementById('mode-btn-raw');
            if (btnAi) btnAi.classList.toggle('active', mode === 'ai');
            if (btnRaw) btnRaw.classList.toggle('active', mode === 'raw');
            updatePlayerSource();
        }

        function onPlayerSkipChange() {
            const select = document.getElementById('player-skip-select');
            if (select) {
                currentFrameSkip = parseInt(select.value) || 1;
                if (currentStreamVideo && currentPlayerMode === 'ai') {
                    currentStreamToken = Date.now();
                    updatePlayerSource();
                }
            }
        }

        function onPlayerSettingChange() {
            const confSelect = document.getElementById('player-conf-select');
            const imgszSelect = document.getElementById('player-imgsz-select');
            if (confSelect) currentConfidence = parseFloat(confSelect.value) || 0.15;
            if (imgszSelect) currentImgsz = parseInt(imgszSelect.value) || 960;
            if (currentStreamVideo && currentPlayerMode === 'ai') {
                currentStreamToken = Date.now();
                updatePlayerSource();
            }
        }

        async function pollStreamTelemetry() {
            if (!currentStreamVideo || currentPlayerMode !== 'ai') return;
            try {
                const res = await fetch(`/api/stream/telemetry?video=${encodeURIComponent(currentStreamVideo)}`);
                if (!res.ok) return;
                const data = await res.json();
                if (!data || data.status !== 'streaming') return;

                const fpsStat = document.getElementById('player-stat-fps');
                if (fpsStat) fpsStat.textContent = `${data.fps || 0.0} FPS`;

                const frameStat = document.getElementById('player-stat-frame');
                if (frameStat) frameStat.textContent = `Khung ${data.current_frame || 0}/${data.total_frames || 0}`;

                const violStat = document.getElementById('player-stat-viol');
                if (violStat) violStat.textContent = `${data.violations_count || 0} Vi Phạm`;

                const chipsContainer = document.getElementById('player-live-chips');
                if (chipsContainer && data.events && data.events.length > 0) {
                    chipsContainer.innerHTML = data.events.map(ev => {
                        let badgeClass = 'chip-normal';
                        let icon = 'fa-check';
                        let statusLabel = 'Hợp lệ';
                        if (ev.status === 'CONFIRMED') {
                            badgeClass = 'chip-confirmed';
                            icon = 'fa-triangle-exclamation';
                            statusLabel = 'VI PHẠM';
                        } else if (ev.status === 'SUSPECTED') {
                            badgeClass = 'chip-suspected';
                            icon = 'fa-clock';
                            statusLabel = 'Nghi vấn';
                        }
                        return `
                            <div class="live-obj-chip ${badgeClass}">
                                <i class="fa-solid ${icon}"></i>
                                <span>Track #${ev.track_id}</span>
                                <span style="font-weight: 700;">${statusLabel}</span>
                                <span style="opacity: 0.8; font-size: 0.72rem;">(${Math.round(ev.overlap)}% đè vỉa hè)</span>
                            </div>
                        `;
                    }).join('');
                }
            } catch (e) {}
        }

        function toggleEvalAcademicMetrics() {
            const body = document.getElementById('eval-academic-body');
            const icon = document.getElementById('eval-metrics-chevron');
            if (!body) return;
            const isHidden = (body.style.display === 'none');
            body.style.display = isHidden ? 'block' : 'none';
            if (icon) {
                icon.style.transform = isHidden ? 'rotate(180deg)' : 'rotate(0deg)';
            }
            if (isHidden) {
                loadEvaluationResults();
            }
        }

        function testCurrentVideoFromRoi() {
            if (!currentVideo) {
                showToast('Chưa chọn video nào trong ROI Studio để test!', true);
                return;
            }
            switchMainTab('eval');
            selectAndPlayVideo(currentVideo.filename);
            showToast(`Đang phát video: ${currentVideo.filename} với cấu hình ROI hiện tại!`);
        }

        async function startEvaluation(explicitMode = null, explicitVideo = null) {
            if (evalRunning) return;

            const modeSelect = document.getElementById('eval-mode-select');
            const videoSelect = document.getElementById('eval-video-select');
            
            let mode = explicitMode || (modeSelect ? modeSelect.value : 'batch');
            let videoName = explicitVideo || (videoSelect && mode === 'single' ? videoSelect.value : '');

            if (mode === 'single' && !videoName) {
                alert('Vui lòng chọn video để kiểm thử!');
                return;
            }

            setEvalRunningUI(true);
            evalLogOffset = 0;
            const consoleScreen = document.getElementById('eval-console-screen');
            if (consoleScreen) consoleScreen.textContent = `[${new Date().toLocaleTimeString()}] Bắt đầu tiến trình kiểm thử (${mode.toUpperCase()})...\n`;

            try {
                const res = await fetch('/api/eval/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mode: mode, video: videoName })
                });
                const data = await res.json();
                if (!res.ok || !data.ok) {
                    alert('Lỗi: ' + (data.error || 'Không thể bắt đầu kiểm thử.'));
                    setEvalRunningUI(false);
                    return;
                }

                if (evalPollInterval) clearInterval(evalPollInterval);
                evalPollInterval = setInterval(pollEvalStatus, 600);
            } catch (e) {
                console.error('Lỗi gọi API /api/eval/run:', e);
                alert('Không thể kết nối đến máy chủ.');
                setEvalRunningUI(false);
            }
        }

        async function checkInitialEvalStatus() {
            try {
                const res = await fetch('/api/eval/status?since=0');
                if (!res.ok) return;
                const data = await res.json();
                if (data.status === 'running') {
                    setEvalRunningUI(true);
                    if (evalPollInterval) clearInterval(evalPollInterval);
                    evalPollInterval = setInterval(pollEvalStatus, 600);
                } else if (data.status === 'completed' && data.has_results) {
                    loadEvaluationResults();
                }
            } catch (e) {}
        }

        async function pollEvalStatus() {
            try {
                const res = await fetch(`/api/eval/status?since=${evalLogOffset}`);
                if (!res.ok) return;
                const data = await res.json();

                if (data.new_logs && data.new_logs.length > 0) {
                    const screen = document.getElementById('eval-console-screen');
                    if (screen) {
                        data.new_logs.forEach(l => {
                            screen.textContent += l + String.fromCharCode(10);
                        });
                        evalLogOffset = data.total_logs;
                        const autoscroll = document.getElementById('eval-autoscroll');
                        if (autoscroll && autoscroll.checked) {
                            screen.scrollTop = screen.scrollHeight;
                        }
                    }
                }

                const pct = Math.min(100, Math.max(0, data.percent || 0));
                const fill = document.getElementById('eval-progress-fill');
                if (fill) fill.style.width = pct + '%';
                const pctLabel = document.getElementById('eval-progress-pct');
                if (pctLabel) pctLabel.textContent = Math.round(pct) + '%';

                const metaLabel = document.getElementById('eval-progress-label');
                if (metaLabel) metaLabel.textContent = data.message || 'Đang thực thi...';

                const frameStat = document.getElementById('eval-stat-frame');
                if (frameStat) frameStat.textContent = `${data.current_frame} / ${data.total_frames}`;

                const fpsStat = document.getElementById('eval-stat-fps');
                if (fpsStat) fpsStat.textContent = `${data.fps || 0.0} FPS`;

                const timeStat = document.getElementById('eval-stat-time');
                if (timeStat) timeStat.textContent = `${data.elapsed_sec || 0.0}s`;

                if (data.status === 'completed') {
                    if (evalPollInterval) clearInterval(evalPollInterval);
                    evalPollInterval = null;
                    setEvalRunningUI(false);
                    updateStatusPill('completed');
                    showToast('Đã hoàn thành kiểm thử video thành công!', 'success');
                    loadEvaluationResults();
                } else if (data.status === 'error') {
                    if (evalPollInterval) clearInterval(evalPollInterval);
                    evalPollInterval = null;
                    setEvalRunningUI(false);
                    updateStatusPill('error');
                    alert('Lỗi kiểm thử: ' + (data.error || data.message));
                }
            } catch (e) {
                console.error('Lỗi polling:', e);
            }
        }

        function setEvalRunningUI(isRunning) {
            evalRunning = isRunning;
            const btnStart = document.getElementById('btn-start-eval');
            const iconStart = document.getElementById('btn-start-icon');
            const textStart = document.getElementById('btn-start-text');
            const dot = document.getElementById('console-live-dot');

            if (isRunning) {
                if (btnStart) btnStart.disabled = true;
                if (iconStart) iconStart.className = 'fa-solid fa-circle-notch fa-spin';
                if (textStart) textStart.textContent = 'Đang Chạy Kiểm Thử...';
                if (dot) dot.style.opacity = '1';
                updateStatusPill('running');
            } else {
                if (btnStart) btnStart.disabled = false;
                if (iconStart) iconStart.className = 'fa-solid fa-play';
                if (textStart) textStart.textContent = 'Bắt Đầu Chạy Kiểm Thử';
                if (dot) dot.style.opacity = '0.4';
            }
        }

        function updateStatusPill(status) {
            const pill = document.getElementById('eval-status-pill');
            const dot = document.getElementById('eval-status-dot');
            const text = document.getElementById('eval-status-text');
            if (!pill || !dot || !text) return;

            if (status === 'running') {
                dot.style.color = '#38bdf8';
                text.textContent = 'Đang Thực Thi';
                pill.style.borderColor = 'rgba(56, 189, 248, 0.4)';
            } else if (status === 'completed') {
                dot.style.color = '#10b981';
                text.textContent = 'Đã Hoàn Thành';
                pill.style.borderColor = 'rgba(16, 185, 129, 0.4)';
            } else if (status === 'error') {
                dot.style.color = '#ef4444';
                text.textContent = 'Có Lỗi Xảy Ra';
                pill.style.borderColor = 'rgba(239, 68, 68, 0.4)';
            } else {
                dot.style.color = 'var(--text-dim)';
                text.textContent = 'Sẵn Sàng';
                pill.style.borderColor = 'var(--border)';
            }
        }

        function clearConsoleLog() {
            const screen = document.getElementById('eval-console-screen');
            if (screen) screen.textContent = '';
        }

        async function loadEvaluationResults() {
            try {
                const res = await fetch('/api/eval/results');
                if (!res.ok) return;
                const data = await res.json();
                if (data && (data.metrics_version_b_official || data.results || data.gt_eval)) {
                    renderEvaluationResults(data);
                }
            } catch (e) {
                console.error('Lỗi nạp kết quả kiểm thử:', e);
            }
        }

        function renderEvaluationResults(data) {
            const container = document.getElementById('eval-results-container');
            if (!container) return;
            container.style.display = 'block';

            const isBatch = !!data.metrics_version_b_official;
            const meta = data.metadata || {};
            const tsLabel = document.getElementById('results-timestamp');
            if (tsLabel) {
                tsLabel.textContent = `Cập nhật lúc: ${meta.generated_at || new Date().toLocaleString()}`;
            }

            const kpiGrid = document.getElementById('eval-kpi-grid');
            const tbody = document.getElementById('eval-gt-tbody');

            if (isBatch) {
                const mb = data.metrics_version_b_official;
                const precPct = (mb.precision * 100).toFixed(1);
                const recPct = (mb.recall * 100).toFixed(1);
                const f1Pct = (mb.f1_score * 100).toFixed(1);
                const pCi0 = (mb.precision_wilson_95_ci[0] * 100).toFixed(1);
                const pCi1 = (mb.precision_wilson_95_ci[1] * 100).toFixed(1);
                const rCi0 = (mb.recall_wilson_95_ci[0] * 100).toFixed(1);
                const rCi1 = (mb.recall_wilson_95_ci[1] * 100).toFixed(1);
                const fpsRange = `${mb.pipeline_throughput_fps_min} – ${mb.pipeline_throughput_fps_max} FPS`;

                if (kpiGrid) {
                    kpiGrid.innerHTML = `
                        <div class="stat-card">
                            <div class="stat-icon" style="background: rgba(16, 185, 129, 0.15); color: var(--success);"><i class="fa-solid fa-bullseye"></i></div>
                            <div class="stat-label">System Precision</div>
                            <div class="stat-value" style="color: var(--success);">${precPct}%</div>
                            <div class="stat-sub">Wilson 95% CI: [${pCi0}% – ${pCi1}%]</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon" style="background: rgba(59, 130, 246, 0.15); color: var(--primary);"><i class="fa-solid fa-magnifying-glass-chart"></i></div>
                            <div class="stat-label">System Recall</div>
                            <div class="stat-value" style="color: var(--primary);">${recPct}%</div>
                            <div class="stat-sub">Wilson 95% CI: [${rCi0}% – ${rCi1}%]</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon" style="background: rgba(139, 92, 246, 0.15); color: var(--purple);"><i class="fa-solid fa-scale-balanced"></i></div>
                            <div class="stat-label">System F1-Score</div>
                            <div class="stat-value" style="color: var(--purple);">${f1Pct}%</div>
                            <div class="stat-sub">Điều hòa cân bằng tối ưu</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon" style="background: rgba(245, 158, 11, 0.15); color: var(--warning);"><i class="fa-solid fa-bolt"></i></div>
                            <div class="stat-label">Throughput Pipeline</div>
                            <div class="stat-value" style="color: var(--warning); font-size: 1.55rem;">${fpsRange}</div>
                            <div class="stat-sub">Tần suất AI: ${mb.estimated_inference_rate_hz || '~11 - 13 Hz'}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon" style="background: rgba(148, 163, 184, 0.15); color: var(--text-muted);"><i class="fa-solid fa-table-cells"></i></div>
                            <div class="stat-label">Ma Trận Nhầm Lẫn</div>
                            <div class="stat-value" style="font-size: 1.35rem; color: #38bdf8;">TP:${mb.true_positives} | FP:${mb.false_positives}</div>
                            <div class="stat-sub">FN:${mb.false_negatives} (Nghi vấn) | TN:${mb.true_negatives}</div>
                        </div>
                    `;
                }

                if (tbody && mb.item_evaluations) {
                    tbody.innerHTML = '';
                    mb.item_evaluations.forEach(item => {
                        const tr = document.createElement('tr');
                        const vName = (item.video_id === 'video_test') ? 'Video 1' : ((item.video_id === 'videotesst2') ? 'Video 2' : 'Video 3');
                        
                        let evalBadge = '';
                        if (item.eval_result === 'TP') {
                            evalBadge = '<span class="eval-tag-tp"><i class="fa-solid fa-check"></i> TP (Bắt đúng)</span>';
                        } else if (item.eval_result === 'TN') {
                            evalBadge = '<span class="eval-tag-tn"><i class="fa-solid fa-shield"></i> TN (Đúng chuẩn)</span>';
                        } else if (item.eval_result === 'FN') {
                            evalBadge = '<span class="eval-tag-fn"><i class="fa-solid fa-clock"></i> FN (Nghi vấn)</span>';
                        } else {
                            evalBadge = '<span class="eval-tag-fp"><i class="fa-solid fa-triangle-exclamation"></i> FP (Báo sai)</span>';
                        }

                        let statusBadge = '';
                        if (item.system_status === 'CONFIRMED') {
                            statusBadge = '<span class="badge badge-confirmed">VI PHẠM (CONFIRMED)</span>';
                        } else if (item.system_status === 'SUSPECTED') {
                            statusBadge = '<span class="badge badge-suspected">NGHI VẤN (SUSPECTED)</span>';
                        } else {
                            statusBadge = '<span class="badge badge-dismissed">HỢP LỆ (NORMAL)</span>';
                        }

                        let cropHtml = '<span style="color: var(--text-dim); font-size: 0.75rem;">N/A</span>';
                        if (item.best_crop_path) {
                            const cleanP = item.best_crop_path.replaceAll(String.fromCharCode(92), '/');
                            const cropUrl = '/' + (cleanP.startsWith('/') ? cleanP.slice(1) : cleanP);
                            cropHtml = `<img src="${cropUrl}" class="eval-crop-thumb" alt="Crop #${item.expected_track_id}" onclick="openModal('${cropUrl}')" title="Nhấp để phóng to ảnh vi phạm">`;
                        }

                        tr.innerHTML = `
                            <td><span style="font-weight: 600; color: #38bdf8;">${vName}</span></td>
                            <td style="text-align: center; font-weight: 700;">#${item.expected_track_id}</td>
                            <td style="text-align: center;">${cropHtml}</td>
                            <td>
                                <div style="font-weight: 600; color: var(--text-main);">${item.description}</div>
                                <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 2px;">Mã mẫu: ${item.object_id}</div>
                            </td>
                            <td style="text-align: center; font-family: monospace;">${item.total_detections}</td>
                            <td style="text-align: center; font-family: monospace; font-weight: 600; color: #34d399;">${(item.avg_conf * 100).toFixed(1)}%</td>
                            <td style="text-align: center; font-family: monospace; font-weight: 600;">${item.avg_overlap.toFixed(1)}%</td>
                            <td style="text-align: center;">${statusBadge}</td>
                            <td style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.4;">${item.justification}</td>
                            <td style="text-align: center;">${evalBadge}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                }
            } else {
                const r = data.results || {};
                const gt = data.gt_eval || {};
                const fps = r.avg_fps ? r.avg_fps.toFixed(1) : 'N/A';
                const lat = r.latency_stats ? r.latency_stats.tracker_p50_ms : 'N/A';

                if (kpiGrid) {
                    kpiGrid.innerHTML = `
                        <div class="stat-card">
                            <div class="stat-icon" style="background: rgba(59, 130, 246, 0.15); color: var(--primary);"><i class="fa-solid fa-video"></i></div>
                            <div class="stat-label">Video Kiểm Thử</div>
                            <div class="stat-value" style="font-size: 1.25rem; color: #38bdf8;">${data.video || 'Single'}</div>
                            <div class="stat-sub">${r.total_frames || 0} frames (${(r.duration_sec || 0).toFixed(1)}s)</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon" style="background: rgba(239, 68, 68, 0.15); color: var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i></div>
                            <div class="stat-label">Số Vi Phạm Bắt Được</div>
                            <div class="stat-value" style="color: var(--danger);">${r.confirmed_count || 0}</div>
                            <div class="stat-sub">Nghi vấn: ${r.suspected_count || 0} | Hợp lệ: ${r.normal_count || 0}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon" style="background: rgba(245, 158, 11, 0.15); color: var(--warning);"><i class="fa-solid fa-bolt"></i></div>
                            <div class="stat-label">Tốc Độ Thông Lượng</div>
                            <div class="stat-value" style="color: var(--warning);">${fps} FPS</div>
                            <div class="stat-sub">Độ trễ p50: ${lat} ms</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon" style="background: rgba(16, 185, 129, 0.15); color: var(--success);"><i class="fa-solid fa-chart-line"></i></div>
                            <div class="stat-label">Đối Chiếu Ground Truth</div>
                            <div class="stat-value" style="font-size: 1.25rem; color: var(--success);">TP: ${gt.tp || 0} | FP: ${gt.fp || 0}</div>
                            <div class="stat-sub">FN: ${gt.fn || 0} | TN: ${gt.tn || 0}</div>
                        </div>
                    `;
                }

                if (tbody && gt.items && gt.items.length > 0) {
                    tbody.innerHTML = '';
                    gt.items.forEach(item => {
                        const tr = document.createElement('tr');
                        let evalBadge = (item.eval_result === 'TP') ? '<span class="eval-tag-tp">TP</span>' :
                            ((item.eval_result === 'TN') ? '<span class="eval-tag-tn">TN</span>' :
                            ((item.eval_result === 'FN') ? '<span class="eval-tag-fn">FN</span>' : '<span class="eval-tag-fp">FP</span>'));
                        
                        let statusBadge = (item.system_status === 'CONFIRMED') ? '<span class="badge badge-confirmed">CONFIRMED</span>' :
                            ((item.system_status === 'SUSPECTED') ? '<span class="badge badge-suspected">SUSPECTED</span>' : '<span class="badge badge-dismissed">NORMAL</span>');

                        let cropHtml = '<span style="color: var(--text-dim);">N/A</span>';
                        if (item.best_crop_path) {
                            const cleanP = item.best_crop_path.replaceAll(String.fromCharCode(92), '/');
                            const cropUrl = '/' + (cleanP.startsWith('/') ? cleanP.slice(1) : cleanP);
                            cropHtml = `<img src="${cropUrl}" class="eval-crop-thumb" alt="Crop" onclick="openModal('${cropUrl}')">`;
                        }

                        tr.innerHTML = `
                            <td><span style="font-weight: 600; color: #38bdf8;">${data.video}</span></td>
                            <td style="text-align: center; font-weight: 700;">#${item.expected_track_id}</td>
                            <td style="text-align: center;">${cropHtml}</td>
                            <td><div style="font-weight: 600;">${item.description}</div></td>
                            <td style="text-align: center; font-family: monospace;">${item.total_detections}</td>
                            <td style="text-align: center; font-family: monospace; color: #34d399;">${(item.avg_conf * 100).toFixed(1)}%</td>
                            <td style="text-align: center; font-family: monospace;">${item.avg_overlap.toFixed(1)}%</td>
                            <td style="text-align: center;">${statusBadge}</td>
                            <td style="font-size: 0.8rem; color: var(--text-muted);">${item.justification}</td>
                            <td style="text-align: center;">${evalBadge}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                }
            }
        }

        // Khởi động trang web dựa theo tham số URL (?tab=roi hoặc ?tab=eval)
        function initAppOnLoad() {
            const urlParams = new URLSearchParams(window.location.search);
            const tabParam = urlParams.get('tab');
            if (tabParam === 'roi') {
                switchMainTab('roi');
            } else if (tabParam === 'eval') {
                switchMainTab('eval');
            } else {
                loadData();
            }
        }

        if (document.readyState === 'loading') {
            window.addEventListener('DOMContentLoaded', initAppOnLoad);
        } else {
            initAppOnLoad();
        }
    </script>
</body>
</html>
"""


# ==============================================================================
# BỘ TRỢ GIÚP QUẢN LÝ & XỬ LÝ KHUNG HÌNH CHO STUDIO CẤU HÌNH VỈA HÈ (ROI STUDIO)
# ==============================================================================
_FRAME_CACHE = {}


def get_roi_videos_list():
    """Quét và trả về danh sách tất cả các tệp video kèm trạng thái cấu hình ROI."""
    video_dir = os.path.abspath("data/videos")
    config_dir = os.path.abspath("configs")
    if not os.path.exists(video_dir):
        return []

    videos = []
    valid_exts = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
    for fname in sorted(os.listdir(video_dir)):
        if fname.lower().endswith(valid_exts) and not fname.startswith('.'):
            fpath = os.path.join(video_dir, fname)
            try:
                size_mb = round(os.path.getsize(fpath) / (1024 * 1024), 2)
            except Exception:
                size_mb = 0

            w, h, fps, total_frames = 1280, 720, 24.0, 0
            try:
                cap = cv2.VideoCapture(fpath)
                vw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                vh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                vfps = round(cap.get(cv2.CAP_PROP_FPS), 1)
                vframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.release()
                if vw > 0 and vh > 0:
                    w, h, fps, total_frames = vw, vh, vfps, vframes
            except Exception:
                pass

            base_name = os.path.splitext(fname)[0]
            clean_name = base_name.replace(" ", "_").replace(",", "").replace("-", "_")

            candidate_files = [
                f"roi_{clean_name}.json",
                f"roi_{base_name}.json"
            ]
            cfg_file = None
            for c in candidate_files:
                p = os.path.join(config_dir, c)
                if os.path.exists(p):
                    cfg_file = c
                    break

            has_roi = False
            regions_count = 0
            points_count = 0
            created_at = ""
            if cfg_file:
                try:
                    with open(os.path.join(config_dir, cfg_file), "r", encoding="utf-8") as cf:
                        cdata = json.load(cf)
                        polys = cdata.get("polygons", [])
                        if not polys and "polygon_points" in cdata and len(cdata["polygon_points"]) >= 3:
                            polys = [cdata["polygon_points"]]
                        regions_count = len(polys)
                        points_count = sum(len(p) for p in polys)
                        has_roi = regions_count > 0
                        created_at = cdata.get("created_at", "")
                except Exception:
                    pass

            videos.append({
                "filename": fname,
                "clean_id": clean_name,
                "size_mb": size_mb,
                "width": w,
                "height": h,
                "fps": fps,
                "total_frames": total_frames,
                "has_roi": has_roi,
                "config_filename": cfg_file or f"roi_{clean_name}.json",
                "regions_count": regions_count,
                "points_count": points_count,
                "created_at": created_at
            })

    return videos


def extract_video_frame(video_name: str) -> bytes:
    """Trích xuất khung hình đầu tiên (frame 0) của video và trả về bytes JPEG."""
    video_name = os.path.basename(video_name)
    video_path = os.path.abspath(os.path.join("data", "videos", video_name))

    data_dir = os.path.abspath("data/videos")
    if os.path.commonpath([data_dir, video_path]) != data_dir or not os.path.exists(video_path):
        return None

    if video_path in _FRAME_CACHE:
        return _FRAME_CACHE[video_path]

    try:
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            return None

        success, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if success:
            jpeg_bytes = buf.tobytes()
            _FRAME_CACHE[video_path] = jpeg_bytes
            return jpeg_bytes
    except Exception as e:
        print(f"[ERROR] Không thể đọc frame từ video {video_name}: {e}")

    return None


def get_roi_config(video_name: str) -> dict:
    """Lấy dữ liệu cấu hình ROI JSON hiện có của video nếu tồn tại."""
    video_name = os.path.basename(video_name)
    base_name = os.path.splitext(video_name)[0]
    clean_name = base_name.replace(" ", "_").replace(",", "").replace("-", "_")
    config_dir = os.path.abspath("configs")

    candidate_paths = [
        os.path.join(config_dir, f"roi_{clean_name}.json"),
        os.path.join(config_dir, f"roi_{base_name}.json")
    ]

    for cpath in candidate_paths:
        if os.path.exists(cpath):
            try:
                with open(cpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["has_existing"] = True
                    data["config_path"] = os.path.basename(cpath)
                    if "polygons" not in data or not data["polygons"]:
                        if "polygon_points" in data and len(data["polygon_points"]) >= 3:
                            data["polygons"] = [data["polygon_points"]]
                        else:
                            data["polygons"] = []
                    return data
            except Exception as e:
                print(f"[WARN] Lỗi đọc cấu hình {cpath}: {e}")

    return {
        "camera_id": base_name,
        "description": "Vung via he co dinh (Ho tro Multi-ROI: Via he trai, phai)",
        "resolution": {"width": 1280, "height": 720},
        "total_regions": 0,
        "total_points": 0,
        "polygons": [],
        "polygon_points": [],
        "has_existing": False,
        "config_path": f"roi_{clean_name}.json"
    }


def save_roi_config(data: dict) -> dict:
    """Lưu danh sách đa giác vỉa hè ra tệp JSON chuẩn ROIManager."""
    video_name = os.path.basename(data.get("video", ""))
    if not video_name:
        return {"ok": False, "error": "Tên video không hợp lệ"}

    base_name = os.path.splitext(video_name)[0]
    clean_name = base_name.replace(" ", "_").replace(",", "").replace("-", "_")
    config_dir = os.path.abspath("configs")
    os.makedirs(config_dir, exist_ok=True)

    raw_polygons = data.get("polygons", [])
    valid_polygons = []
    for poly in raw_polygons:
        if isinstance(poly, list) and len(poly) >= 3:
            valid_polygons.append([[int(pt[0]), int(pt[1])] for pt in poly if len(pt) >= 2])

    res = data.get("resolution", {})
    width = int(res.get("width", 1280)) if isinstance(res, dict) else 1280
    height = int(res.get("height", 720)) if isinstance(res, dict) else 720

    out_filename = f"roi_{clean_name}.json"
    out_path = os.path.join(config_dir, out_filename)

    total_pts = sum(len(p) for p in valid_polygons)
    save_data = {
        "camera_id": base_name,
        "description": "Vung via he co dinh (Ho tro Multi-ROI: Via he trai, phai)",
        "resolution": {"width": width, "height": height},
        "total_regions": len(valid_polygons),
        "total_points": total_pts,
        "polygons": valid_polygons,
        "polygon_points": valid_polygons[0] if valid_polygons else [],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, indent=4, ensure_ascii=False)

    print(f"[WEB ROI STUDIO] Đã lưu cấu hình {len(valid_polygons)} vùng ({total_pts} đỉnh) vào {out_filename}")

    return {
        "ok": True,
        "config_filename": out_filename,
        "total_regions": len(valid_polygons),
        "total_points": total_pts,
        "video": video_name
    }


# ==============================================================================
# HỆ THỐNG QUẢN LÝ TIẾN TRÌNH KIỂM THỬ VIDEO TRỰC TUYẾN (EVALUATION RUNNER)
# ==============================================================================
_EVAL_LOCK = threading.Lock()
_EVAL_STATE = {
    "status": "idle",       # "idle", "running", "completed", "error"
    "mode": "batch",        # "batch" or "single"
    "video_name": "",
    "current_frame": 0,
    "total_frames": 0,
    "fps": 0.0,
    "percent": 0.0,
    "elapsed_sec": 0.0,
    "message": "Sẵn sàng",
    "logs": [],
    "results": None,
    "error": None
}


class WebEvalLogger:
    """Thu thập dòng log streaming từ pipeline đánh giá đưa vào bộ nhớ đệm web."""
    def write(self, msg):
        if not msg:
            return
        try:
            sys.stdout.write(msg)
            sys.stdout.flush()
        except Exception:
            pass
        
        lines = msg.splitlines(keepends=False)
        with _EVAL_LOCK:
            for l in lines:
                if l.strip():
                    _EVAL_STATE["logs"].append(l)
            if len(_EVAL_STATE["logs"]) > 2500:
                _EVAL_STATE["logs"] = _EVAL_STATE["logs"][-2000:]

    def flush(self):
        try:
            sys.stdout.flush()
        except Exception:
            pass


def _eval_worker_func(mode: str, video_name: str):
    """Hàm chạy ngầm đánh giá video trên thread riêng biệt, không block web server."""
    from evaluation import evaluate_videos as ev
    logger = WebEvalLogger()
    t_start = time.time()

    def _batch_cb(pct, vid_label, f_idx, f_total, fps_val):
        with _EVAL_LOCK:
            _EVAL_STATE["percent"] = pct
            _EVAL_STATE["current_frame"] = f_idx
            _EVAL_STATE["total_frames"] = f_total
            _EVAL_STATE["fps"] = fps_val
            _EVAL_STATE["elapsed_sec"] = time.time() - t_start
            _EVAL_STATE["message"] = f"Đang đánh giá {vid_label}: {f_idx}/{f_total} frames ({fps_val} FPS)"

    def _single_cb(f_idx, f_total, fps_val):
        with _EVAL_LOCK:
            pct = int((f_idx / max(1, f_total)) * 100)
            _EVAL_STATE["percent"] = pct
            _EVAL_STATE["current_frame"] = f_idx
            _EVAL_STATE["total_frames"] = f_total
            _EVAL_STATE["fps"] = fps_val
            _EVAL_STATE["elapsed_sec"] = time.time() - t_start
            _EVAL_STATE["message"] = f"Đang xử lý {video_name}: {f_idx}/{f_total} frames ({fps_val} FPS)"

    try:
        if mode == "batch":
            with _EVAL_LOCK:
                _EVAL_STATE["message"] = "Đang chạy đánh giá toàn diện 3 video nghiên cứu..."
            res = ev.run_full_evaluation(progress_callback=_batch_cb, custom_logger=logger)
            with _EVAL_LOCK:
                _EVAL_STATE["results"] = res
                _EVAL_STATE["status"] = "completed"
                _EVAL_STATE["percent"] = 100.0
                _EVAL_STATE["elapsed_sec"] = time.time() - t_start
                _EVAL_STATE["message"] = "Đã hoàn thành đánh giá toàn diện 3 video thành công!"
                _EVAL_STATE["logs"].append(f"[{time.strftime('%H:%M:%S')}] HOÀN THÀNH ĐÁNH GIÁ TOÀN DIỆN 3 VIDEO.")
        else:
            with _EVAL_LOCK:
                _EVAL_STATE["message"] = f"Đang chạy kiểm thử video {video_name}..."
            res = ev.run_single_video_eval_named(video_name, progress_callback=_single_cb, custom_logger=logger)
            with _EVAL_LOCK:
                if "error" in res:
                    _EVAL_STATE["status"] = "error"
                    _EVAL_STATE["error"] = res["error"]
                    _EVAL_STATE["message"] = res["error"]
                    _EVAL_STATE["logs"].append(f"[ERROR] {res['error']}")
                else:
                    _EVAL_STATE["results"] = res
                    _EVAL_STATE["status"] = "completed"
                    _EVAL_STATE["percent"] = 100.0
                    _EVAL_STATE["elapsed_sec"] = time.time() - t_start
                    _EVAL_STATE["message"] = f"Đã hoàn thành kiểm thử video {video_name}!"
                    _EVAL_STATE["logs"].append(f"[{time.strftime('%H:%M:%S')}] HOÀN THÀNH KIỂM THỬ VIDEO: {video_name}.")
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        with _EVAL_LOCK:
            _EVAL_STATE["status"] = "error"
            _EVAL_STATE["error"] = str(e)
            _EVAL_STATE["message"] = f"Lỗi thực thi: {e}"
            _EVAL_STATE["logs"].append(f"[EXCEPTION] {e}\n{tb}")


# ==============================================================================
# HỆ THỐNG TRUYỀN PHÁT LUỒNG VIDEO AI TRỰC TIẾP (LIVE AI STREAMING SERVER)
# ==============================================================================
_STREAM_LOCK = threading.Lock()
_ACTIVE_STREAM_TOKENS = {}
_STREAM_TELEMETRY = {}
_CACHED_TRACKER = None


def get_shared_tracker(conf_threshold: float = 0.15, imgsz: int = 960):
    global _CACHED_TRACKER
    if _CACHED_TRACKER is None:
        from tracking import ObjectTracker
        _CACHED_TRACKER = ObjectTracker(model_path="models/best.onnx", conf_threshold=conf_threshold, imgsz=imgsz)
    return _CACHED_TRACKER


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Giảm thiểu log rác ra console
        pass

    def serve_video_file(self, file_path):
        """Phục vụ file video mp4 hỗ trợ HTTP 206 Partial Content (Range header) cho HTML5 player."""
        if not os.path.isfile(file_path):
            self.send_response(404)
            self.end_headers()
            return

        file_size = os.path.getsize(file_path)
        range_header = self.headers.get("Range")
        if range_header:
            range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
                length = end - start + 1
                self.send_response(206)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                self.send_header("Content-Length", str(length))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                try:
                    with open(file_path, "rb") as f:
                        f.seek(start)
                        self.wfile.write(f.read(length))
                except (BrokenPipeError, ConnectionResetError, OSError):
                    pass
                return

        self.send_response(200)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Content-Length", str(file_size))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(65536):
                    self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def stream_ai_video(self, video_name, token, frame_skip=1, overlay=True, conf=0.15, imgsz=960):
        """Truyền phát trực tiếp luồng video AI (MJPEG Stream) kèm nhận diện YOLO & bám vết ByteTrack."""
        video_name = os.path.basename(video_name)
        video_path = os.path.abspath(os.path.join("data", "videos", video_name))
        data_dir = os.path.abspath("data/videos")

        if os.path.commonpath([data_dir, video_path]) != data_dir or not os.path.exists(video_path):
            self.send_response(404)
            self.end_headers()
            return

        with _STREAM_LOCK:
            _ACTIVE_STREAM_TOKENS[video_name] = token
            _STREAM_TELEMETRY[video_name] = {
                "status": "streaming",
                "video": video_name,
                "current_frame": 0,
                "total_frames": 0,
                "fps": 0.0,
                "objects_count": 0,
                "violations_count": 0,
                "events": []
            }

        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Connection", "close")
        self.end_headers()

        cap = cv2.VideoCapture(video_path)
        fps_source = cap.get(cv2.CAP_PROP_FPS) or 24.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
        frame_delay = 1.0 / max(10.0, fps_source)

        from tracking import ObjectTracker, TemporalVerifier, TrackState
        from roi import ROIManager
        from violation import ViolationChecker
        from utils import FPSTracker, draw_fps_badge, draw_detection

        roi_info = get_roi_config(video_name)
        config_path = os.path.join("configs", roi_info.get("config_path", ""))
        roi_manager = ROIManager(config_path if os.path.exists(config_path) else "configs/roi_camera1.json")
        checker = ViolationChecker(threshold=0.30)
        min_avg_c = max(0.20, min(0.35, conf * 1.5))
        verifier = TemporalVerifier(confirm_frames=15, confirm_seconds=0.5, source_fps=fps_source, min_avg_confidence=min_avg_c)
        fps_tracker = FPSTracker(alpha=0.15)
        tracker = get_shared_tracker(conf_threshold=conf, imgsz=imgsz)

        frame_idx = 0
        roi_validated = False
        last_results = []
        confirmed_ids = set()

        try:
            while True:
                with _STREAM_LOCK:
                    if _ACTIVE_STREAM_TOKENS.get(video_name) != token:
                        break

                t_start = time.perf_counter()
                ret, frame = cap.read()
                if not ret or frame is None:
                    # Tua lại video từ đầu để tiếp tục phát mượt mà
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    frame_idx = 0
                    verifier.reset()
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        break

                frame_idx += 1
                fh, fw = frame.shape[:2]
                if not roi_validated:
                    roi_manager.validate_resolution(fw, fh)
                    roi_validated = True

                curr_fps = fps_tracker.update()
                is_infer = (frame_skip <= 0) or (frame_idx % (frame_skip + 1) == 1)

                if is_infer:
                    tracked_objs = tracker.track(frame, conf=conf, imgsz=imgsz)
                    last_results = verifier.process_frame(tracked_objs, checker, roi_manager.polygons)

                    events = []
                    viol_count = 0
                    for obj in last_results:
                        tid = obj["track_id"]
                        stat = obj["temporal_status"]
                        sp = obj["spatial_res"]
                        if stat == TrackState.CONFIRMED:
                            viol_count += 1
                            confirmed_ids.add(tid)
                            events.append({"track_id": tid, "status": "CONFIRMED", "overlap": sp["overlap_pct"]})
                        elif stat == TrackState.SUSPECTED:
                            events.append({"track_id": tid, "status": "SUSPECTED", "overlap": sp["overlap_pct"]})
                        else:
                            events.append({"track_id": tid, "status": "NORMAL", "overlap": sp["overlap_pct"]})

                    with _STREAM_LOCK:
                        _STREAM_TELEMETRY[video_name] = {
                            "status": "streaming",
                            "video": video_name,
                            "current_frame": frame_idx,
                            "total_frames": total_frames,
                            "fps": round(curr_fps, 1),
                            "objects_count": len(last_results),
                            "violations_count": len(confirmed_ids),
                            "events": events[:8]
                        }

                if overlay:
                    roi_manager.draw_overlay(frame, alpha=0.25)
                    for obj in last_results:
                        box = obj["box"]
                        tid = obj["track_id"]
                        stat = obj["temporal_status"]
                        sp = obj["spatial_res"]
                        ov_pct = sp["overlap_pct"]
                        if stat == TrackState.CONFIRMED:
                            lbl = f"ID #{tid} VI PHAM {ov_pct:.0f}%"
                        elif stat == TrackState.SUSPECTED:
                            lbl = f"ID #{tid} NGHI VAN {ov_pct:.0f}%"
                        else:
                            lbl = f"ID #{tid} HOP LE {ov_pct:.0f}%"
                        draw_detection(frame, box, lbl, is_violation=(stat == TrackState.CONFIRMED), track_id=tid, status=stat)

                    draw_fps_badge(frame, curr_fps)
                    hud_title = f"{video_name} | Khung {frame_idx}/{total_frames} | Vi pham: {len(confirmed_ids)}"
                    cv2.putText(frame, hud_title, (20, fh - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 4)
                    cv2.putText(frame, hud_title, (20, fh - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (56, 189, 248), 2)

                if fw > 960:
                    scale = 960 / fw
                    render_frame = cv2.resize(frame, (960, int(fh * scale)), interpolation=cv2.INTER_LINEAR)
                else:
                    render_frame = frame

                _, jpeg = cv2.imencode('.jpg', render_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                frame_bytes = jpeg.tobytes()

                chunk = (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: " + str(len(frame_bytes)).encode() + b"\r\n\r\n"
                    + frame_bytes + b"\r\n"
                )
                self.wfile.write(chunk)
                self.wfile.flush()

                elapsed = time.perf_counter() - t_start
                sleep_time = max(0.002, frame_delay - elapsed)
                time.sleep(sleep_time)

        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass
        except Exception as e:
            import traceback
            print(f"[STREAM ERROR] {e}\n{traceback.format_exc()}")
        finally:
            cap.release()
            with _STREAM_LOCK:
                if _ACTIVE_STREAM_TOKENS.get(video_name) == token:
                    _STREAM_TELEMETRY[video_name]["status"] = "stopped"

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

        elif path == "/api/roi/videos":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            vids = get_roi_videos_list()
            self.wfile.write(json.dumps(vids, ensure_ascii=False).encode("utf-8"))

        elif path == "/api/roi/frame":
            query_params = urllib.parse.parse_qs(parsed.query)
            video_name = query_params.get("video", [None])[0]
            if not video_name:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing video parameter")
                return
            jpeg_bytes = extract_video_frame(video_name)
            if jpeg_bytes:
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                self.wfile.write(jpeg_bytes)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Video frame not found or cannot be read")

        elif path == "/api/roi/config":
            query_params = urllib.parse.parse_qs(parsed.query)
            video_name = query_params.get("video", [None])[0]
            if not video_name:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing video parameter")
                return
            cfg_data = get_roi_config(video_name)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(cfg_data, ensure_ascii=False).encode("utf-8"))

        elif path == "/api/stream/video":
            query_params = urllib.parse.parse_qs(parsed.query)
            video_name = query_params.get("name", [None])[0]
            try:
                token = int(query_params.get("token", [0])[0])
            except Exception:
                token = 0
            try:
                frame_skip = int(query_params.get("skip", [1])[0])
            except Exception:
                frame_skip = 1
            overlay = query_params.get("overlay", ["1"])[0] == "1"
            try:
                conf = float(query_params.get("conf", [0.15])[0])
            except Exception:
                conf = 0.15
            try:
                imgsz = int(query_params.get("imgsz", [960])[0])
            except Exception:
                imgsz = 960
            if not video_name:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing name parameter")
                return
            self.stream_ai_video(video_name, token, frame_skip=frame_skip, overlay=overlay, conf=conf, imgsz=imgsz)

        elif path == "/api/stream/telemetry":
            query_params = urllib.parse.parse_qs(parsed.query)
            video_name = query_params.get("video", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            with _STREAM_LOCK:
                tdata = _STREAM_TELEMETRY.get(video_name, {
                    "status": "idle",
                    "video": video_name or "",
                    "current_frame": 0,
                    "total_frames": 0,
                    "fps": 0.0,
                    "objects_count": 0,
                    "violations_count": 0,
                    "events": []
                })
            self.wfile.write(json.dumps(tdata, ensure_ascii=False).encode("utf-8"))

        elif path.startswith("/videos/"):
            raw_name = path[len("/videos/"):]
            video_name = urllib.parse.unquote(raw_name)
            video_path = os.path.abspath(os.path.join("data", "videos", os.path.basename(video_name)))
            data_dir = os.path.abspath("data/videos")
            if os.path.commonpath([data_dir, video_path]) == data_dir and os.path.isfile(video_path):
                self.serve_video_file(video_path)
            else:
                self.send_response(404)
                self.end_headers()

        elif path.startswith("/evidence/") or path.startswith("/reports/video_eval_crops/"):
            # Kiểm tra an toàn path traversal và chỉ cho phép phục vụ ảnh bằng chứng hợp lệ
            base_dir = os.path.abspath(".")
            allowed_dirs = [
                os.path.abspath("evidence"),
                os.path.abspath(os.path.join("data", "evidence")),
                os.path.abspath(os.path.join("reports", "video_eval_crops")),
            ]
            raw_path = path.lstrip("/")
            file_path = os.path.abspath(os.path.normpath(os.path.join(base_dir, raw_path)))

            # 1. Kiểm tra phần mở rộng: CHỈ cho phép file ảnh (.jpg, .jpeg, .png, .webp)
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"403 Forbidden: Only evidence images are allowed")
                return

            # 2. Kiểm tra an toàn thư mục (sử dụng commonpath chuẩn xác thay vì startswith/rstrip)
            is_inside_allowed = any(
                os.path.commonpath([d, file_path]) == d
                for d in allowed_dirs
                if os.path.exists(d)
            )

            if not is_inside_allowed:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"403 Forbidden: Access outside allowed evidence directories")
            elif os.path.isfile(file_path):
                self.send_response(200)
                mime, _ = mimetypes.guess_type(file_path)
                self.send_header("Content-Type", mime or "image/jpeg")
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        elif path == "/api/eval/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            query_params = urllib.parse.parse_qs(parsed.query)
            try:
                since_idx = int(query_params.get("since", [0])[0])
            except Exception:
                since_idx = 0
            with _EVAL_LOCK:
                new_logs = _EVAL_STATE["logs"][since_idx:]
                resp_data = {
                    "status": _EVAL_STATE["status"],
                    "mode": _EVAL_STATE["mode"],
                    "video_name": _EVAL_STATE["video_name"],
                    "current_frame": _EVAL_STATE["current_frame"],
                    "total_frames": _EVAL_STATE["total_frames"],
                    "fps": _EVAL_STATE["fps"],
                    "percent": _EVAL_STATE["percent"],
                    "elapsed_sec": round(_EVAL_STATE["elapsed_sec"], 1),
                    "message": _EVAL_STATE["message"],
                    "error": _EVAL_STATE["error"],
                    "total_logs": len(_EVAL_STATE["logs"]),
                    "new_logs": new_logs,
                    "has_results": _EVAL_STATE["results"] is not None
                }
            self.wfile.write(json.dumps(resp_data, ensure_ascii=False).encode("utf-8"))

        elif path == "/api/eval/results":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            res_data = None
            with _EVAL_LOCK:
                if _EVAL_STATE.get("results"):
                    res_data = _EVAL_STATE["results"]
            if not res_data and os.path.exists("reports/system_eval_results.json"):
                try:
                    with open("reports/system_eval_results.json", "r", encoding="utf-8") as f:
                        res_data = json.load(f)
                except Exception:
                    res_data = None
            self.wfile.write(json.dumps(res_data or {}, ensure_ascii=False).encode("utf-8"))
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

        elif path == "/api/roi/save":
            client_host = self.client_address[0] if self.client_address else ""
            if client_host not in ("127.0.0.1", "::1", "localhost"):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"403 Forbidden: Saving ROI requires local access")
                return

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                res = save_roi_config(data)
                self.send_response(200 if res.get("ok") else 400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
        elif path == "/api/eval/run":
            client_host = self.client_address[0] if self.client_address else ""
            if client_host not in ("127.0.0.1", "::1", "localhost"):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"403 Forbidden: Evaluation requires local access")
                return

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body) if body else {}
                mode = data.get("mode", "batch")
                video_name = data.get("video", "")

                with _EVAL_LOCK:
                    if _EVAL_STATE["status"] == "running":
                        self.send_response(409)
                        self.send_header("Content-Type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(json.dumps({"ok": False, "error": "Tiến trình kiểm thử đang chạy dở. Vui lòng đợi!"}, ensure_ascii=False).encode("utf-8"))
                        return
                    _EVAL_STATE["status"] = "running"
                    _EVAL_STATE["mode"] = mode
                    _EVAL_STATE["video_name"] = video_name
                    _EVAL_STATE["current_frame"] = 0
                    _EVAL_STATE["total_frames"] = 0
                    _EVAL_STATE["fps"] = 0.0
                    _EVAL_STATE["percent"] = 0.0
                    _EVAL_STATE["elapsed_sec"] = 0.0
                    _EVAL_STATE["message"] = f"Khởi động kiểm thử ({mode.upper()})..."
                    _EVAL_STATE["logs"] = [f"[{time.strftime('%H:%M:%S')}] Khởi động kiểm thử video (Chế độ: {mode.upper()})..."]
                    _EVAL_STATE["error"] = None

                th = threading.Thread(target=_eval_worker_func, args=(mode, video_name), daemon=True)
                th.start()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "status": "started"}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def run_dashboard(port: int = PORT, host: str = "127.0.0.1", initial_tab: str = None):
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    print("=" * 75)
    print(" DASHBOARD GIÁM SÁT CCTV, STUDIO VẼ ROI & PHÁT VIDEO AI ĐÃ KHỞI ĐỘNG THÀNH CÔNG!")
    print(" Truy cập an toàn tại trình duyệt:")
    if initial_tab == "roi":
        print(f"    http://127.0.0.1:{port}/?tab=roi   (Studio Cấu Hình ROI Vỉa Hè)")
    elif initial_tab == "eval":
        print(f"    http://127.0.0.1:{port}/?tab=eval  (Phát & Kiểm Thử Video AI Trực Tiếp)")
    else:
        print(f"    http://127.0.0.1:{port}            (Hồ Sơ Vi Phạm & Phạt Nguội)")
        print(f"    http://127.0.0.1:{port}/?tab=roi   (Studio Cấu Hình ROI Vỉa Hè)")
        print(f"    http://127.0.0.1:{port}/?tab=eval  (Phát & Kiểm Thử Video AI Trực Tiếp)")
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
