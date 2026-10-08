"""
Module đo đạc FPS thời gian thực
"""
import time

class FPSTracker:
    def __init__(self, alpha: float = 0.15):
        self.alpha = alpha
        self.prev_time = None
        self.smoothed_fps = 0.0

    def update(self) -> float:
        curr_time = time.perf_counter()
        if self.prev_time is None:
            self.prev_time = curr_time
            return 0.0
            
        delta_t = curr_time - self.prev_time
        self.prev_time = curr_time
        
        if delta_t > 0:
            instant_fps = 1.0 / delta_t
            if self.smoothed_fps == 0.0:
                self.smoothed_fps = instant_fps
            else:
                self.smoothed_fps = self.alpha * instant_fps + (1.0 - self.alpha) * self.smoothed_fps
        return self.smoothed_fps
