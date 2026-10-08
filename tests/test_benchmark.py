"""
Unit test for SystemBenchmark (evaluation/benchmark.py)
"""
import os
import sys
import unittest

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath("."))
from evaluation.benchmark import SystemBenchmark


class TestSystemBenchmark(unittest.TestCase):
    def setUp(self):
        self.bench = SystemBenchmark(
            model_path="models/best.pt",
            num_frames=5
        )

    def test_hardware_info(self):
        hw = self.bench.get_hardware_info()
        self.assertIn("os", hw)
        self.assertIn("python_version", hw)
        self.assertIn("device_name", hw)

    def test_run_benchmark(self):
        results = self.bench.run_benchmark(verbose=False)
        self.assertIn("latency_breakdown_ms", results)
        self.assertIn("throughput_fps", results)
        self.assertIn("ablation_study", results)
        self.assertGreater(results["throughput_fps"]["fps_average"], 0)

    def test_export_report(self):
        results = self.bench.run_benchmark(verbose=False)
        report_path = "reports/test_report.md"
        out = self.bench.export_markdown_report(results, output_file=report_path)
        self.assertTrue(os.path.exists(out))
        with open(out, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("CHƯƠNG 7: THỰC NGHIỆM VÀ ĐÁNH GIÁ KẾT QUẢ HỆ THỐNG", content)
        self.assertIn("Bảng 7.1. Phân rã độ trễ từng thành phần", content)

        # Cleanup
        if os.path.exists(report_path):
            os.remove(report_path)


if __name__ == "__main__":
    unittest.main()
