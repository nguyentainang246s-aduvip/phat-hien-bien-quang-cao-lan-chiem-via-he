"""
Module quản lý đọc video / camera
"""
import os
import cv2

class VideoReader:
    def __init__(self, source_path: str):
        self.source_path = source_path
        self.cap = cv2.VideoCapture(source_path)
        if not self.cap.isOpened():
            raise ValueError(f"Không thể mở nguồn video: {source_path}")
            
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def read(self):
        """Đọc 1 frame tiếp theo (ret, frame)"""
        return self.cap.read()

    def reset(self):
        """Tua lại đầu video"""
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def release(self):
        """Giải phóng bộ nhớ camera"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
