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
AC_BULLET_RE = re.compile(r"^\s*[-*]\s*(AC[-_]?\d+|A\d+)\b(.*)$", re.IGNORECASE)
HEADER_KEYS = {"#", "ID", "编号", "序号", "AC", "R"}


def strip_fences(lines: list[str]) -> list[str]:
    out: list[str] = []
    fence: str | None = None
    for line in lines:
        s = line.lstrip()
        if fence is None and (s.startswith("```") or s.startswith("~~~")):
            fence = s[:3]
            out.append("")
            continue
        if fence is not None and s.startswith(fence):
            fence = None
            out.append("")
            continue
        out.append("" if fence else line)
    return out


def strip_inline(line: str) -> str:
    return re.sub(r"`[^`]*`", "", line)


def cells_of(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def is_sep(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{1,}:?", c) for c in cells)


def split_paths(value: str) -> list[str]:
    value = value.strip().strip("`")
    if not value or value in ("无", "—", "-"):
        return []
    value = re.sub(r"[（(][^）)]*[）)]\s*$", "", value).strip()
    parts = re.split(r"[,，、]", value)
    out = []
    for p in parts:
        p = p.strip().strip("`").lstrip("./").rstrip("。. ")
        if p and p not in ("无", "—", "-"):
            out.append(p)
    return out


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
    limit = min(len(lines), 40)
    for idx, line in enumerate(lines[:limit]):
        if re.match(r"^##\s+1[.、]", line):
            limit = idx
            break
    found: dict[str, tuple[int, str]] = {}
    for idx, line in enumerate(lines[:limit], 1):
        m = ANCHOR_RE.match(line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if not value:
            for nxt in lines[idx:idx + 3]:
                if nxt.strip() and not nxt.lstrip().startswith("#"):
                    value = nxt.strip().lstrip("-* ").strip()
                    break
        if value:
            found.setdefault(key, (idx, value))
    return found


def verify_of(text: str) -> str:
    m = re.search(r"验证\s*[：:]\s*(.+)$", text)
    if m:
        return m.group(1).strip()
    if "`" in text or any(k in text for k in ("全绿", "≤", "exit", "grep", "pytest", "PR #", "命令", "断言", "截图")):
        return text.strip()
    return ""


def parse_ac(lines: list[str]) -> tuple[int, list[str]]:
    problems: list[str] = []
    count = 0
    header: list[str] | None = None
    verify_idx = result_idx = disp_idx = None

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("- ") or stripped.startswith("* ") or "|" not in stripped:
            header = None
            verify_idx = result_idx = disp_idx = None
            bm = AC_BULLET_RE.match(line)
            if bm:
                count += 1
                if not verify_of(bm.group(2)):
                    problems.append(f"{idx}: {bm.group(1)} 没有验证方法")
            continue

        cells = cells_of(stripped)
        if is_sep(cells):
            continue
        if header is None:
            head = cells[0].upper() if cells else ""
            if (head in HEADER_KEYS or "需求" in head or "编号" in head) and any("验收" in c for c in cells) and any("验证" in c or "证据" in c for c in cells):
                header = cells
                verify_idx = next((i for i, c in enumerate(cells) if "验证" in c or "证据" in c), None)
                result_idx = next((i for i, c in enumerate(cells) if "结果" in c), None)
                disp_idx = next((i for i, c in enumerate(cells) if "处置" in c or "处理" in c), None)
            continue
        if verify_idx is None or len(cells) <= verify_idx:
            continue
        count += 1
        verify = cells[verify_idx].strip()
        if not verify or verify in ("…", "-", "—"):
            problems.append(f"{idx}: AC 行没有验证方法")
        result = cells[result_idx] if result_idx is not None and len(cells) > result_idx else ""
        disp = cells[disp_idx] if disp_idx is not None and len(cells) > disp_idx else ""
        if "❌" in result and not (disp.strip() or re.search(r"处置\s*[：:]|豁免\s*[：:]|已处置|不修", " ".join(cells))):
            problems.append(f"{idx}: ❌ 未写处置")
    return count, problems


def repo_root(spec: Path) -> Path | None:
    proc = subprocess.run(["git", "-C", str(spec.parent), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return Path(proc.stdout.strip())


def parse_diff(args: argparse.Namespace, spec: Path) -> tuple[list[str] | None, str | None]:
    """返回 (files, error)。None = 没给 base/diff；error 非空 = 检查失败。"""
    if args.diff:
        text = Path(args.diff).read_text(encoding="utf-8")
        lines = [l.rstrip("\n") for l in text.splitlines() if l.strip()]
        if any(l.startswith(("diff --git", "+++ ", "--- ")) for l in lines):
            files = set()
            for l in lines:
                m = re.match(r"^\+\+\+\s+b/(.+)$", l) or re.match(r"^---\s+a/(.+)$", l)
                if m and m.group(1) != "/dev/null":
                    files.add(m.group(1))
            return sorted(files), None
        return [l.strip().lstrip("./").rstrip("。. ") for l in lines], None
    if not args.base:
        return None, None
    root = repo_root(spec)
    if root is None:
        return None, "给了 --base，但 spec 不在 git 仓里"
    proc = subprocess.run(["git", "-C", str(root), "diff", "--name-only", args.base], capture_output=True, text=True)
    if proc.returncode != 0:
        return None, f"--base `{args.base}` 无效：{proc.stderr.strip().splitlines()[:1]}"
    files = {l.strip() for l in proc.stdout.splitlines() if l.strip()}
    status = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True)
    if status.returncode == 0:
        for line in status.stdout.splitlines():
            if len(line) > 3 and line[:2] == "??":
                files.add(line[3:].strip())
    return sorted(files), None


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

    changed, kept, _ = parse_scope(lines)
    kept_declared = bool(kept) or any(re.match(r"^\s*[-*]?\s*(?:\*\*)?不改(?:\*\*)?\s*[：:]\s*(无|—|-)\s*$", l) for l in lines)
    add("W2", kept_declared, "不改：" + ("、".join(kept) if kept else ("无" if kept_declared else "未声明")), level="warn")

    ac_count, ac_problems = parse_ac(lines)
    add("E2", ac_count > 0 and not ac_problems, f"AC {ac_count} 条" if not ac_problems else "；".join(ac_problems))

    body = "\n".join(strip_inline(l) for l in lines)
    holes = [p for p in PLACEHOLDERS if p in body]
    add("E3", not holes, "无占位符" if not holes else "发现：" + "、".join(holes))

    bad_bullets = [f"{i}: {l.strip()[:60]}" for i, l in enumerate(lines, 1)
                   if AC_BULLET_RE.match(l) and "❌" in l and not re.search(r"处置\s*[：:]|豁免\s*[：:]|已处置|不修", strip_inline(l))]
    add("E4", not bad_bullets, "无未处置 ❌" if not bad_bullets else "；".join(bad_bullets[:4]))

    fuzzy = sorted({w for w in FUZZY if w in body})
    add("W1", not fuzzy, "无模糊词" if not fuzzy else "发现：" + "、".join(fuzzy), level="warn")

    changed_files, diff_error = parse_diff(args, spec_path)
    if diff_error:
        add("E5", False, diff_error)
    elif changed_files is None:
        add("E5", False, "未提供 --base / --diff，跳过 diff 比对", level="warn")
    elif not changed:
        add("E5", False, "未声明「改」清单，跳过 diff 比对", level="warn")
    else:
        spec_rel = None
        root = repo_root(spec_path)
        if root is not None:
            try:
                spec_rel = spec_path.resolve().relative_to(root.resolve()).as_posix()
            except ValueError:
                spec_rel = None
        outside = [f for f in changed_files if f != spec_rel and not path_hit(f, changed)]
        if not changed_files:
            add("E5", True, "base 与工作区无差异")
        else:
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
