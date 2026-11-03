"""
Module bảo mật và xử lý an toàn chuỗi kết nối / URL cho toàn hệ thống.
"""

import re
from urllib.parse import urlsplit, urlunsplit


def mask_source_url(url) -> str:
    """
    Che giấu mật khẩu trong URL luồng RTSP / HTTP / HTTPS để chống lộ thông tin xác thực trong log.
    Hỗ trợ cả trường hợp mật khẩu có chứa ký tự đặc biệt hoặc ký tự '@' chưa qua mã hóa.
    
    Ví dụ:
        rtsp://admin:secret123@192.168.1.1:554/live -> rtsp://admin:***@192.168.1.1:554/live
        rtsp://user:p@ss@192.168.1.1/live -> rtsp://user:***@192.168.1.1/live
        data/videos/test.mp4 -> data/videos/test.mp4
        0 -> "0"
    """
    if not isinstance(url, str):
        return str(url)

    if "://" not in url or "@" not in url:
        return url

    try:
        parsed = urlsplit(url)
        if parsed.password is not None:
            user = parsed.username or ""
            port_str = f":{parsed.port}" if parsed.port else ""
            host = parsed.hostname or ""
            masked_netloc = f"{user}:***@{host}{port_str}"
            return urlunsplit((parsed.scheme, masked_netloc, parsed.path, parsed.query, parsed.fragment))
    except Exception:
        pass

    # Fallback bằng regex tham lam (greedy match tới ký tự '@' cuối cùng trước host/path)
    return re.sub(r'(://[^:/@]+):.*@', r'\1:***@', url)
