import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

root = Path('.')
model_refs = []

patterns = [
    re.compile(r"['\"]([^'\"]*\.(?:pt|onnx|engine))['\"]"),
    re.compile(r"model_path\s*[:=]\s*['\"]?([^'\"\s,)]+)['\"]?"),
    re.compile(r"DEFAULT_MODEL\s*=\s*['\"]?([^'\"\s,)]+)['\"]?")
]

ignore_dirs = {'.venv', '.git', '__pycache__', 'runs', '.agents', '.gemini', 'reports', 'evidence', 'data'}

for p in root.rglob('*'):
    if any(ig in p.parts for ig in ignore_dirs):
        continue
    if p.suffix in ('.py', '.yaml', '.yml', '.json'):
        try:
            content = p.read_text(encoding='utf-8', errors='ignore')
            for line_no, line in enumerate(content.splitlines(), 1):
                for pat in patterns:
                    m = pat.search(line)
                    if m:
                        val = m.group(1)
                        if any(ext in val for ext in ['.pt', '.onnx', '.engine']) or 'model' in val.lower():
                            model_refs.append((str(p), line_no, val, line.strip()))
        except Exception:
            pass

print(f"Tổng số vị trí tham chiếu model tìm thấy: {len(model_refs)}")
seen = set()
for path, line_no, val, full_line in model_refs:
    key = (path, line_no)
    if key not in seen:
        seen.add(key)
        print(f"[{path}:{line_no}] -> {val}\n   Code: {full_line[:100]}\n")

