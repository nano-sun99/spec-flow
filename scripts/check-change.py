#!/usr/bin/env python3
"""校验一次替换式变更的 change manifest。

用法：
    python3 scripts/check-change.py --manifest docs/changes/<slug>/manifest.json \
        --base <git-rev> [--head <git-rev>] [--root .]

只做机器可判的结构/证据检查，不判断规则语义。退出码 0 = 全部通过；1 = 有违规。
"""
from __future__ import annotations

import argparse
import json
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
CONCLUSIONS = {"match", "changed", "whitelist", "unresolved"}
REVIEWERS = {"user", "review-agent"}
REQUIRED_TOP = {
    "change", "title", "base", "head", "classification", "rules", "scans",
    "semantic_checks", "approval", "rebuild",
}
# 只有这些视图文件可以用 non_rule_changes 覆盖；规则文件不能靠它躲开规则行。
NON_RULE_ALLOW = {
    "references/v2/README.md",
    "references/v2/40-cases/INDEX.md",
}
MIN_OLD_TEXT = 6
MIN_SEARCH = 6
MIN_SEMANTIC = 4
MIN_ANCHOR = 4
MIN_EVIDENCE = 6


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=False
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败：{proc.stderr.strip()}")
    return proc.stdout


def resolve(root: Path, rev: str) -> str:
    return git(root, "rev-parse", "--verify", rev).strip()


def read_at(root: Path, rev: str, path: str) -> str:
    return git(root, "show", f"{rev}:{path}")


def changed_files(root: Path, base: str, head: str) -> set[str]:
    return set(git(root, "diff", "--name-only", base, head).splitlines())


def head_md_files(root: Path, head: str, scope: list[str]) -> list[str]:
    names = git(root, "ls-tree", "-r", "--name-only", head).splitlines()
    out: list[str] = []
    for name in names:
        if not name.endswith(".md"):
            continue
        if any(name == s or name.startswith(s.rstrip("/") + "/") for s in scope):
            out.append(name)
    return sorted(set(out))


def find_lines(root: Path, head: str, path: str, needle: str) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    for no, line in enumerate(read_at(root, head, path).splitlines(), 1):
        if needle in line:
            hits.append((no, line))
    return hits


def lint(root: Path, manifest_path: Path, base_arg: str, head_arg: str) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"manifest 读不了 / 不是合法 JSON：{exc}"]

    try:
        base = resolve(root, base_arg)
        head = resolve(root, head_arg)
    except RuntimeError as exc:
        return [f"base/head 解析失败：{exc}"]

    missing = REQUIRED_TOP - set(data)
    if missing:
        errors.append(f"顶层缺字段：{', '.join(sorted(missing))}")
    for key in ("change", "title", "base", "head", "classification"):
        if not str(data.get(key, "")).strip():
            errors.append(f"{key} 为空")
    if data.get("base") and resolve(root, str(data["base"])) != base:
        errors.append(f"manifest.base 解析后与 --base 不一致：{data.get('base')!r}")
    if data.get("head") and str(data["head"]) != "HEAD":
        try:
            if resolve(root, str(data["head"])) != head:
                errors.append(f"manifest.head 解析后与 --head 不一致：{data.get('head')!r}")
        except RuntimeError:
            errors.append(f"manifest.head 解析不了：{data.get('head')!r}")
    if data.get("classification") not in TYPES:
        errors.append(f"classification 不在 {sorted(TYPES)}：{data.get('classification')!r}")

    rules = data.get("rules") or []
    if not rules:
        errors.append("rules 为空：至少一条规则")
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
        evidence = str(rule.get("evidence", "")).strip()
        if len(evidence) < MIN_EVIDENCE:
            errors.append(f"{where} evidence 太短（<{MIN_EVIDENCE}）：{evidence!r}")

        new = rule.get("new") or {}
        new_file = new.get("file")
        anchor = str(new.get("anchor", "")).strip()
        if not new_file:
            errors.append(f"{where} 缺 new.file")
        else:
            try:
                content = read_at(root, head, new_file)
            except RuntimeError:
                errors.append(f"{where} head 中不存在 new.file：{new_file}")
                content = ""
            if len(anchor) < MIN_ANCHOR:
                errors.append(f"{where} new.anchor 太短（<{MIN_ANCHOR}）：{anchor!r}")
            if anchor and content and anchor not in content:
                errors.append(f"{where} new.anchor 在 head:{new_file} 中找不到：{anchor!r}")
            if anchor and content and content.count(anchor) != 1:
                errors.append(f"{where} new.anchor 不唯一（出现 {content.count(anchor)} 次）：{anchor!r}")
        if not anchor:
            errors.append(f"{where} 缺 new.anchor（head 文件中可反查的字面片段）")
        if not str(new.get("section", "")).strip():
            errors.append(f"{where} 缺 new.section")

        if rtype == "add":
            if rule.get("old"):
                errors.append(f"{where} type=add 却给了 old")
            search = str(rule.get("same_trigger_search", "")).strip()
            if len(search) < MIN_SEARCH:
                errors.append(f"{where} same_trigger_search 太短（<{MIN_SEARCH}）：{search!r}")
            if rule.get("disposition") != "not-applicable":
                errors.append(f"{where} type=add 的 disposition 必须是 not-applicable")
        else:
            old = rule.get("old") or {}
            if not old.get("file"):
                errors.append(f"{where} type={rtype} 缺 old.file")
                continue
            line = old.get("line")
            text = str(old.get("text", "")).strip()
            if len(text) < MIN_OLD_TEXT:
                errors.append(f"{where} old.text 太短（<{MIN_OLD_TEXT}）：{text!r}")
            if not isinstance(line, int):
                errors.append(f"{where} type={rtype} 缺 old.line（整数）")
                continue
            try:
                lines = read_at(root, base, old["file"]).splitlines()
            except RuntimeError:
                errors.append(f"{where} base 中读不到 old.file：{old['file']}")
                continue
            if line < 1 or line > len(lines):
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
        if w.get("reviewer") not in REVIEWERS:
            errors.append(f"{where} reviewer 不在 {sorted(REVIEWERS)}：{w.get('reviewer')!r}")
        if not str(w.get("review_ref", "")).strip():
            errors.append(f"{where} 缺 review_ref")
    for rule in rules:
        if rule.get("status") == "whitelist" and rule.get("id") not in white_ids:
            errors.append(f"{rule.get('id')} 状态=whitelist 但 whitelist 表无对应条目")

    scans = data.get("scans") or []
    if not scans:
        errors.append("scans 为空：至少一条扫描")
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
        if scan.get("conclusion") not in CONCLUSIONS:
            errors.append(f"{where} conclusion 不在 {sorted(CONCLUSIONS)}：{scan.get('conclusion')!r}")
        if scan.get("conclusion") == "unresolved":
            errors.append(f"{where} conclusion=unresolved")
        try:
            pattern = re.compile(query)
        except re.error as exc:
            errors.append(f"{where} query 不是合法正则：{exc}")
            continue
        files = head_md_files(root, head, scope)
        if not files:
            errors.append(f"{where} scope 在 head 中没有 .md 文件：{scope}")
            continue
        found: list[tuple[str, int, str]] = []
        for path in files:
            for no, line in enumerate(read_at(root, head, path).splitlines(), 1):
                for m in pattern.finditer(line):
                    found.append((path, no, m.group(0)))
        listed = scan.get("hits") or []
        for rel, no, hit in found:
            match = any(
                h.get("file") == rel and hit in str(h.get("text", ""))
                for h in listed
            )
            if not match:
                errors.append(f"{where} 未登记的命中：{rel}:{no} {hit!r}")
        for h in listed:
            if h.get("conclusion") not in CONCLUSIONS:
                errors.append(f"{where} hit 的 conclusion 不合法：{h.get('conclusion')!r}")
            if h.get("conclusion") == "unresolved":
                errors.append(f"{where} hit conclusion=unresolved：{h.get('file')!r}")
            if h.get("conclusion") == "whitelist":
                if not str(h.get("reason", "")).strip():
                    errors.append(f"{where} whitelist hit 缺 reason：{h.get('file')!r}")
                if h.get("reviewer") not in REVIEWERS:
                    errors.append(f"{where} whitelist hit reviewer 不合法：{h.get('reviewer')!r}")
                if not str(h.get("review_ref", "")).strip():
                    errors.append(f"{where} whitelist hit 缺 review_ref：{h.get('file')!r}")
            file = h.get("file")
            text = str(h.get("text", ""))
            if not file or not text:
                errors.append(f"{where} hit 缺 file 或 text")
                continue
            if file not in files:
                errors.append(f"{where} hit 文件不在 scope：{file}")
            elif not find_lines(root, head, file, text):
                errors.append(f"{where} 登记的命中在 head:{file} 中不存在：{text!r}")

    semantic = data.get("semantic_checks") or []
    if not semantic:
        errors.append("semantic_checks 为空：反向冲突至少一条")
    for i, item in enumerate(semantic, 1):
        where = f"semantic_checks[{i}]"
        if len(str(item.get("item", "")).strip()) < MIN_SEMANTIC:
            errors.append(f"{where} item 太短（<{MIN_SEMANTIC}）")
        if item.get("conclusion") not in CONCLUSIONS:
            errors.append(f"{where} conclusion 不合法：{item.get('conclusion')!r}")
        if item.get("conclusion") == "unresolved":
            errors.append(f"{where} conclusion=unresolved")
        if len(str(item.get("evidence", "")).strip()) < MIN_SEMANTIC:
            errors.append(f"{where} evidence 太短（<{MIN_SEMANTIC}）")

    approval = data.get("approval") or {}
    for key in ("user_quote", "timestamp", "scope", "base", "head", "link"):
        if not str(approval.get(key, "")).strip():
            errors.append(f"approval 缺 {key}")
    if approval.get("base") and resolve(root, str(approval["base"])) != base:
        errors.append("approval.base 解析后与 --base 不一致")
    if approval.get("head") and str(approval["head"]) != "HEAD":
        try:
            if resolve(root, str(approval["head"])) != head:
                errors.append("approval.head 解析后与 --head 不一致")
        except RuntimeError:
            errors.append("approval.head 解析不了")

    rebuild = data.get("rebuild")
    if not isinstance(rebuild, dict):
        errors.append("rebuild 必须是对象")
    elif not isinstance(rebuild.get("triggered"), bool):
        errors.append("rebuild.triggered 必须是布尔")
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
        file = item.get("file")
        if not file or not str(item.get("reason", "")).strip():
            errors.append("non_rule_changes 条目缺 file 或 reason")
            continue
        if file not in NON_RULE_ALLOW:
            errors.append(f"non_rule_changes 不允许覆盖规则文件：{file}")
        covered.add(file)
    try:
        covered.add(manifest_path.relative_to(root).as_posix())
    except ValueError:
        pass
    changed = changed_files(root, base, head)
    uncovered = sorted(changed - covered)
    if uncovered:
        errors.append("有改动文件未被 manifest 覆盖：" + "、".join(uncovered))

    if any(r.get("status") == "unresolved" for r in rules):
        errors.append("存在 status=unresolved 的规则")

    by_type = {t: sum(1 for r in rules if r.get("type") == t) for t in sorted(TYPES)}
    by_status = {s: sum(1 for r in rules if r.get("status") == s) for s in sorted(STATUSES)}
    print(
        f"base={base[:12]} head={head[:12]} rules={len(rules)} "
        f"add/replace/retire={by_type['add']}/{by_type['replace']}/{by_type['retire']} "
        f"status done/whitelist/unresolved={by_status['done']}/{by_status['whitelist']}/{by_status['unresolved']} "
        f"whitelist_entries={len(whitelist)} scans={len(scans)} "
        f"semantic_checks={len(semantic)} changed_files={len(changed)}"
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
