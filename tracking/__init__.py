"""
Package tracking: Quản lý bám vết vật thể (Object Tracking) và bộ lọc thời gian (Temporal Verification)
Bao gồm:
  - ObjectTracker: ByteTrack kết hợp Hysteresis & Spatial Adaptive Thresholding
  - TemporalVerifier & TrackState: Xác thực thời gian vi phạm & cooldown chống spam
  - MotionFilter: Bộ lọc vận tốc & phân loại đối tượng di chuyển
"""
from .tracker import ObjectTracker
from .verifier import TemporalVerifier, TrackState
from .motion_filter import MotionFilter

__all__ = ["ObjectTracker", "TemporalVerifier", "TrackState", "MotionFilter"]
