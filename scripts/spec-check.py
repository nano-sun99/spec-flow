#!/usr/bin/env python3
"""spec-check：三行锚 / 范围 / AC / 占位符 / 模糊词 / ❌ 处置 / diff 越界。

用法：
  python3 scripts/spec-check.py <spec> [--base <ref>] [--diff <file>] [--json]

退出码：有 error = 1；只有 warn 或全绿 = 0。
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

FUZZY = ("顺便", "以后", "尽量", "可能", "应该", "等等")
PLACEHOLDERS = ("{{", "TBD", "待补")
ANCHORS = ("目标", "不做", "验收")
SCOPE_RE = re.compile(r"^\s*[-*]?\s*(?:\*\*)?(改|不改)(?:\*\*)?\s*[：:]\s*(.*)$")
ANCHOR_RE = re.compile(r"^\s*[-*]?\s*(?:\*\*)?(目标|不做|验收)(?:\*\*)?\s*[：:]\s*(.*)$")
AC_ID_RE = re.compile(r"^(?:R|AC|A)[-_]?\d+", re.IGNORECASE)


def strip_fences(lines: list[str]) -> list[str]:
    out: list[str] = []
    inside = False
    for line in lines:
        if line.lstrip().startswith("```"):
            inside = not inside
            out.append("")
            continue
        out.append("" if inside else line)
    return out


def split_paths(value: str) -> list[str]:
    value = value.strip().strip("`")
    if not value or value in ("无", "—", "-"):
        return []
    parts = re.split(r"[,，、]", value)
    return [p.strip().strip("`") for p in parts if p.strip().strip("`")]


def parse_scope(lines: list[str]) -> tuple[list[str], list[str], list[int]]:
    changed: list[str] = []
    kept: list[str] = []
    evidence: list[int] = []
    i = 0
    while i < len(lines):
        m = SCOPE_RE.match(lines[i])
        if not m:
            i += 1
            continue
        key, value = m.group(1), m.group(2).strip()
        bucket = changed if key == "改" else kept
        evidence.append(i + 1)
        bucket.extend(split_paths(value))
        if not value:
            j = i + 1
            while j < len(lines):
                line = lines[j]
                if not line.strip() or line.lstrip().startswith("#"):
                    break
                bm = re.match(r"^\s*[-*]\s*(.+)$", line)
                if not bm:
                    break
                bucket.extend(split_paths(bm.group(1)))
                j += 1
            i = j
        else:
            i += 1
    return changed, kept, evidence


def parse_anchors(lines: list[str]) -> dict[str, tuple[int, str]]:
    found: dict[str, tuple[int, str]] = {}
    for idx, line in enumerate(lines, 1):
        m = ANCHOR_RE.match(line)
        if m and m.group(2).strip():
            found.setdefault(m.group(1), (idx, m.group(2).strip()))
    return found


def parse_ac(lines: list[str]) -> tuple[int, list[str]]:
    """返回 (AC 条数, 问题列表)。支持表格与 bullet。"""
    problems: list[str] = []
    count = 0
    header: list[str] | None = None
    verify_idx = result_idx = None

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            header = None
            verify_idx = result_idx = None
            bm = re.match(r"^\s*[-*]\s*((?:R|AC|A)[-_]?\d+.*)$", line, re.IGNORECASE)
            if bm:
                count += 1
                if not re.search(r"验证|证据|命令|断言|截图", bm.group(1)):
                    problems.append(f"{idx}: {bm.group(1)[:40]} 没有验证方法")
            continue

        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue
        if header is None:
            head = cells[0].upper()
            if (head in ("ID", "编号", "序号", "AC", "R") or "需求" in cells[0]) and any("验证" in c for c in cells):
                header = cells
                verify_idx = next((i for i, c in enumerate(cells) if "验证" in c), None)
                result_idx = next((i for i, c in enumerate(cells) if "结果" in c), None)
            continue
        if verify_idx is None:
            continue
        count += 1
        verify = cells[verify_idx] if verify_idx is not None and len(cells) > verify_idx else ""
        if not verify or verify in ("…", "-", "—"):
            problems.append(f"{idx}: AC 行没有验证方法")
        result = cells[result_idx] if result_idx is not None and len(cells) > result_idx else ""
        if "❌" in result and not re.search(r"处置|豁免|修复|已修|不修", " ".join(cells)):
            problems.append(f"{idx}: ❌ 未写处置")
    return count, problems


def parse_diff(args: argparse.Namespace, root: Path) -> list[str]:
    if args.diff:
        text = Path(args.diff).read_text(encoding="utf-8")
        return [l.strip() for l in text.splitlines() if l.strip()]
    if args.base:
        proc = subprocess.run(
            ["git", "-C", str(root), "diff", "--name-only", args.base],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return []
        return [l.strip() for l in proc.stdout.splitlines() if l.strip()]
    return []


def path_hit(path: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if path == pat or path.startswith(pat.rstrip("/") + "/"):
            return True
        if fnmatch.fnmatch(path, pat):
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--base")
    ap.add_argument("--diff")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.is_file():
        print(f"红 | 找不到 spec：{args.spec}", file=sys.stderr)
        return 2
    raw = spec_path.read_text(encoding="utf-8").splitlines()
    lines = strip_fences(raw)
    checks: list[tuple[str, str, str, bool]] = []

    def add(cid: str, ok: bool, evidence: str, level: str = "error") -> None:
        checks.append((cid, "绿" if ok else ("红" if level == "error" else "黄"), evidence, ok or level != "error"))

    anchors = parse_anchors(lines)
    missing = [a for a in ANCHORS if a not in anchors]
    add("E1", not missing, "三行锚齐全" if not missing else "缺：" + "、".join(missing))

    changed, kept, scope_lines = parse_scope(lines)
    add("W2", bool(kept), "不改：" + ("、".join(kept) if kept else "未声明"), level="warn")

    ac_count, ac_problems = parse_ac(lines)
    add("E2", ac_count > 0 and not ac_problems, f"AC {ac_count} 条" if not ac_problems else "；".join(ac_problems[:4]))

    body = "\n".join(re.sub(r"`[^`]*`", "", l) for l in lines)
    holes = [p for p in PLACEHOLDERS if p in body]
    add("E3", not holes, "无占位符" if not holes else "发现：" + "、".join(holes))

    bad_rows = [f"{i}: {l.strip()[:60]}" for i, l in enumerate(lines, 1) if re.match(r"^\s*[-*]\s*(?:R|AC|A)[-_]?\d+", l) and "❌" in l and not re.search(r"处置|豁免|修复|已修|不修", l)]
    add("E4", not bad_rows, "无未处置 ❌" if not bad_rows else "；".join(bad_rows[:4]))

    fuzzy = sorted({w for w in FUZZY if w in body})
    add("W1", not fuzzy, "无模糊词" if not fuzzy else "发现：" + "、".join(fuzzy), level="warn")

    diff_files = parse_diff(args, Path.cwd())
    if not changed:
        add("E5", False, "未声明「改」清单，跳过 diff 比对", level="warn")
    elif not diff_files:
        add("E5", False, "未提供 --base / --diff，跳过 diff 比对", level="warn")
    else:
        outside = [f for f in diff_files if not path_hit(f, changed)]
        add("E5", not outside, "diff 全在「改」清单内" if not outside else "越界：" + "、".join(outside[:6]))

    errors = [c for c in checks if not c[3]]
    if args.json:
        print(json.dumps({
            "spec": str(spec_path),
            "checks": [{"id": c[0], "result": c[1], "evidence": c[2]} for c in checks],
            "errors": len(errors),
            "result": "red" if errors else "green",
        }, ensure_ascii=False, indent=2))
    else:
        for cid, result, evidence, _ in checks:
            print(f"{cid} | {result} | {evidence}")
        print("红" if errors else "绿")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
