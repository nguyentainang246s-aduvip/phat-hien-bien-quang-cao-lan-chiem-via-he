"""
Package evaluation: Đánh giá thực nghiệm và đo đạc chỉ số hệ thống phục vụ ĐATN.
"""
from .benchmark import SystemBenchmark
from .eval_system import SystemEvaluator

__all__ = ["SystemBenchmark", "SystemEvaluator"]
