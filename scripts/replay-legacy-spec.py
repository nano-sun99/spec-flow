#!/usr/bin/env python3
"""把旧格式 spec 映射成新一页 + AC 表，用临时副本跑 spec-check。

用法：python3 scripts/replay-legacy-spec.py <spec>...

只读历史 spec；临时副本写到系统临时目录，不修改仓库文件。
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def section(lines: list[str], key: str, exclude: str | None = None) -> list[str]:
    for i, line in enumerate(lines):
        if re.match(r"^#{2,3} ", line) and key in line and (not exclude or exclude not in line):
            j = i + 1
            while j < len(lines) and not re.match(r"^#{2,3} ", lines[j]):
                j += 1
            return lines[i + 1:j]
    return []


def first_bullet(sec: list[str]) -> str:
    for line in sec:
        m = re.match(r"^\s*[-*]\s*(?:\[[ xX]\]\s*)?(.+)$", line)
        if m:
            return m.group(1).strip()
    return ""


def verify_of(text: str) -> str:
    m = re.search(r"(验证|证据|命令|断言|截图)[：:]\s*(.+)$", text)
    if m:
        return m.group(2).strip()
    if any(k in text for k in ("`", "全绿", "≤", "exit", "grep", "pytest", "PR #")):
        return text
    return ""


def replay(path: Path) -> tuple[int, list[str], int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    goal = first_bullet(section(lines, "目标", "非目标"))
    notdo = first_bullet(section(lines, "非目标")) or first_bullet(section(lines, "不做"))
    acc = section(lines, "验收")
    items = []
    for line in acc:
        m = re.match(r"^\s*(?:\d+\.|[-*]\s*\[[ xX]\]|[-*]\s*\*\*[A-Z]\d+[a-z]?\*\*)\s*(.+)$", line)
        if m:
            items.append(m.group(1).strip())
    changed = []
    for line in section(lines, "改动面"):
        changed += re.findall(r"`([^`]+\.(?:md|py|sh))`", line)
    changed = sorted(set(changed)) or ["无"]

    out = ["# replay", "", f"- **目标**：{goal or '未取到'}", f"- **不做**：{notdo or '未取到'}",
           f"- **验收**：{items[0] if items else '未取到'}", "- **改**：" + "、".join(changed), "- **不改**：无", "",
           "| ID | 需求 | 验收 | 验证 | 结果 |", "|---|---|---|---|---|"]
    for i, text in enumerate(items, 1):
        out.append(f"| A{i} | {text[:80]} | {text[:80]} | {verify_of(text)} |  |")
    out += ["", "---", ""] + lines

    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "spec.md"
        p.write_text("\n".join(out), encoding="utf-8")
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "spec-check.py"), str(p)], capture_output=True, text=True)
    e2 = next((l for l in proc.stdout.splitlines() if l.startswith("E2 ")), "")
    flagged = len(re.findall(r"\d+:", e2))
    return len(items), [e2] if e2 else [], proc.returncode


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    print("| spec | AC | E2 点名 | exit |")
    print("|---|---|---|---|")
    for arg in sys.argv[1:]:
        path = Path(arg)
        n, e2, rc = replay(path)
        count = len(re.findall(r"\d+:", e2[0])) if e2 else 0
        print(f"| {path.name} | {n} | {count} | {rc} |")
        for line in e2:
            print(f"  {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
