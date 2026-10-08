"""
Package tracking: Quản lý bám vết vật thể (Object Tracking) và bộ lọc thời gian (Temporal Verification)
"""
from .tracker import ObjectTracker
from .verifier import TemporalVerifier, TrackState

__all__ = ["ObjectTracker", "TemporalVerifier", "TrackState"]

