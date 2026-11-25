#!/usr/bin/env python3
"""校验一次替换式变更的 change manifest。

用法：
    python3 scripts/check-change.py --manifest docs/changes/<slug>/manifest.json \
        --base <git-rev> [--head HEAD] [--root .]

只做机器可判的结构/证据检查，不判断规则语义。退出码 0 = 全部通过；1 = 有违规。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

TYPES = {"add", "replace", "retire"}
DISPOSITIONS = {
    "replace", "delete", "merge", "alias", "keep-history", "keep-scoped",
    "not-applicable",
}
STATUSES = {"done", "whitelist", "unresolved"}
SCAN_CONCLUSIONS = {"match", "changed", "whitelist", "unresolved"}
REQUIRED_TOP = {"change", "base", "head", "classification", "rules", "scans", "semantic_checks", "approval"}


def run_git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=False
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败：{proc.stderr.strip()}")
    return proc.stdout


def changed_files(root: Path, base: str) -> set[str]:
    tracked = set(run_git(root, "diff", "--name-only", base).splitlines())
    untracked = set(run_git(root, "ls-files", "--others", "--exclude-standard").splitlines())
    return {p for p in tracked | untracked if p}


def base_lines(root: Path, base: str, path: str) -> list[str]:
    try:
        return run_git(root, "show", f"{base}:{path}").splitlines()
    except RuntimeError:
        return []


def read_md_files(root: Path, scope: list[str]) -> list[Path]:
    files: list[Path] = []
    for entry in scope:
        target = root / entry
        if target.is_dir():
            files.extend(p for p in target.rglob("*.md") if p.is_file())
        elif target.is_file() and target.suffix == ".md":
            files.append(target)
    return sorted(set(files))


def lint(root: Path, manifest_path: Path, base: str, head: str) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"manifest 读不了 / 不是合法 JSON：{exc}"]

    missing = REQUIRED_TOP - set(data)
    if missing:
        errors.append(f"顶层缺字段：{', '.join(sorted(missing))}")
    mbase = str(data.get("base", ""))
    if not (mbase == base or mbase.startswith(base) or base.startswith(mbase)):
        errors.append(f"manifest.base={mbase!r} 与 --base={base!r} 不一致")
    if data.get("head") not in {head, "HEAD"}:
        errors.append(f"manifest.head={data.get('head')!r} 与 --head={head!r} 不一致")
    if data.get("classification") not in TYPES:
        errors.append(f"classification 不在 {sorted(TYPES)}：{data.get('classification')!r}")

    rules = data.get("rules") or []
    ids: set[str] = set()
    for i, rule in enumerate(rules, 1):
        where = f"rules[{i}]"
        rid = rule.get("id")
        if not rid:
            errors.append(f"{where} 缺 id")
        elif rid in ids:
            errors.append(f"{where} id 重复：{rid}")
        else:
            ids.add(rid)
        rtype = rule.get("type")
        if rtype not in TYPES:
            errors.append(f"{where} type 不在 {sorted(TYPES)}：{rtype!r}")
        if rule.get("disposition") not in DISPOSITIONS:
            errors.append(f"{where} disposition 不在允许集合：{rule.get('disposition')!r}")
        if rule.get("status") not in STATUSES:
            errors.append(f"{where} status 不在 {sorted(STATUSES)}：{rule.get('status')!r}")
        if not str(rule.get("evidence", "")).strip():
            errors.append(f"{where} 缺 evidence")
        new = rule.get("new") or {}
        if not new.get("file"):
            errors.append(f"{where} 缺 new.file")
        elif not (root / new["file"]).exists():
            errors.append(f"{where} new.file 不存在：{new['file']}")
        if not str(new.get("section", "")).strip():
            errors.append(f"{where} 缺 new.section")
        if rtype == "add":
            if rule.get("old"):
                errors.append(f"{where} type=add 却给了 old")
            if not str(rule.get("same_trigger_search", "")).strip():
                errors.append(f"{where} type=add 缺 same_trigger_search")
            if rule.get("disposition") != "not-applicable":
                errors.append(f"{where} type=add 的 disposition 必须是 not-applicable")
        else:
            old = rule.get("old") or {}
            if not old.get("file"):
                errors.append(f"{where} type={rtype} 缺 old.file")
                continue
            line = old.get("line")
            text = str(old.get("text", "")).strip()
            if not text:
                errors.append(f"{where} type={rtype} 缺 old.text")
            if not isinstance(line, int):
                errors.append(f"{where} type={rtype} 缺 old.line（整数）")
                continue
            lines = base_lines(root, base, old["file"])
            if not lines:
                errors.append(f"{where} base:{old['file']} 读不到")
            elif line < 1 or line > len(lines):
                errors.append(f"{where} old.line={line} 超出 base:{old['file']} 行数 {len(lines)}")
            elif text and text not in lines[line - 1]:
                errors.append(
                    f"{where} base:{old['file']}:{line} 不含 old.text；实际：{lines[line - 1][:120]!r}"
                )

    whitelist = data.get("whitelist") or []
    white_ids = {w.get("rule_id") for w in whitelist}
    for i, w in enumerate(whitelist, 1):
        where = f"whitelist[{i}]"
        if not w.get("rule_id") or w["rule_id"] not in ids:
            errors.append(f"{where} rule_id 不存在：{w.get('rule_id')!r}")
        if not str(w.get("reason", "")).strip():
            errors.append(f"{where} 缺 reason")
        if not str(w.get("reviewer", "")).strip():
            errors.append(f"{where} 缺 reviewer")
    for rule in rules:
        if rule.get("status") == "whitelist" and rule.get("id") not in white_ids:
            errors.append(f"{rule.get('id')} 状态=whitelist 但 whitelist 表无对应条目")

    scans = data.get("scans") or []
    for i, scan in enumerate(scans, 1):
        where = f"scans[{i}]"
        query = scan.get("query")
        scope = scan.get("scope") or []
        if not query:
            errors.append(f"{where} 缺 query")
            continue
        if not scope:
            errors.append(f"{where} 缺 scope")
            continue
        if scan.get("conclusion") not in SCAN_CONCLUSIONS:
            errors.append(f"{where} conclusion 不在 {sorted(SCAN_CONCLUSIONS)}：{scan.get('conclusion')!r}")
        try:
            pattern = re.compile(query)
        except re.error as exc:
            errors.append(f"{where} query 不是合法正则：{exc}")
            continue
        listed = scan.get("hits") or []
        found: list[tuple[str, int, str]] = []
        for path in read_md_files(root, scope):
            rel = path.relative_to(root).as_posix()
            for no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                for m in pattern.finditer(line):
                    found.append((rel, no, m.group(0)))
        for rel, no, hit in found:
            match = any(
                h.get("file") == rel and hit in str(h.get("text", ""))
                for h in listed
            )
            if not match:
                errors.append(f"{where} 未登记的命中：{rel}:{no} {hit!r}")
        for h in listed:
            if h.get("conclusion") not in SCAN_CONCLUSIONS:
                errors.append(f"{where} hit 的 conclusion 不合法：{h.get('conclusion')!r}")

    semantic = data.get("semantic_checks") or []
    if not semantic:
        errors.append("semantic_checks 为空：反向冲突扫描至少给一条")
    for i, item in enumerate(semantic, 1):
        where = f"semantic_checks[{i}]"
        if not str(item.get("item", "")).strip():
            errors.append(f"{where} 缺 item")
        if item.get("conclusion") not in SCAN_CONCLUSIONS:
            errors.append(f"{where} conclusion 不合法：{item.get('conclusion')!r}")
        if not str(item.get("evidence", "")).strip():
            errors.append(f"{where} 缺 evidence")

    approval = data.get("approval") or {}
    for key in ("user_quote", "timestamp", "scope", "base", "head"):
        if not str(approval.get(key, "")).strip():
            errors.append(f"approval 缺 {key}")
    abase = str(approval.get("base", ""))
    if abase and not (abase == base or abase.startswith(base) or base.startswith(abase)):
        errors.append("approval.base 与 --base 不一致")
    if approval.get("head") and approval.get("head") not in {head, "HEAD"}:
        errors.append("approval.head 与 --head 不一致")

    rebuild = data.get("rebuild") or {}
    if not isinstance(rebuild, dict):
        errors.append("rebuild 必须是对象")
    elif rebuild.get("triggered"):
        if not str(rebuild.get("reason", "")).strip():
            errors.append("rebuild.triggered=true 但缺 reason")
        if not (rebuild.get("old_behaviors") or []):
            errors.append("rebuild.triggered=true 但 old_behaviors 为空")

    covered: set[str] = set()
    for rule in rules:
        if rule.get("old"):
            covered.add(rule["old"].get("file", ""))
        if rule.get("new"):
            covered.add(rule["new"].get("file", ""))
    for item in data.get("non_rule_changes") or []:
        if not item.get("file") or not str(item.get("reason", "")).strip():
            errors.append("non_rule_changes 条目缺 file 或 reason")
            continue
        covered.add(item["file"])
    covered.add(manifest_path.relative_to(root).as_posix())
    changed = changed_files(root, base)
    uncovered = sorted(changed - covered)
    if uncovered:
        errors.append("有改动文件未被 manifest 覆盖：" + "、".join(uncovered))

    if any(r.get("status") == "unresolved" for r in rules):
        errors.append("存在 status=unresolved 的规则")
    if any(s.get("conclusion") == "unresolved" for s in scans):
        errors.append("存在 conclusion=unresolved 的扫描")
    if any(i.get("conclusion") == "unresolved" for i in semantic):
        errors.append("存在 conclusion=unresolved 的语义检查")

    # 摘要
    by_type = {t: sum(1 for r in rules if r.get("type") == t) for t in sorted(TYPES)}
    by_status = {s: sum(1 for r in rules if r.get("status") == s) for s in sorted(STATUSES)}
    print(
        f"rules={len(rules)} add/replace/retire={by_type['add']}/{by_type['replace']}/{by_type['retire']} "
        f"status done/whitelist/unresolved={by_status['done']}/{by_status['whitelist']}/{by_status['unresolved']} "
        f"whitelist_entries={len(whitelist)} scans={len(scans)} semantic_checks={len(semantic)} changed_files={len(changed)}"
    )
    if errors:
        print("违规：")
        for err in errors:
            print(" - " + err)
        return errors
    print("绿：manifest 结构与证据检查通过")
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    manifest = (root / args.manifest).resolve()
    if not manifest.exists():
        print(f"红：manifest 不存在：{manifest}")
        return 1
    try:
        errors = lint(root, manifest, args.base, args.head)
    except Exception as exc:  # noqa: BLE001
        print(f"红：校验器自身报错：{exc}")
        return 1
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
