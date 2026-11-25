#!/usr/bin/env python3
"""校验一次替换式变更的 change manifest。

用法：
    python3 scripts/check-change.py --manifest docs/changes/<slug>/manifest.json \
        --base <git-rev> [--head <git-rev>] [--root .] [--draft] [--from-disk]

只做机器可判的结构/证据检查，不判断规则语义。退出码 0 = 全部通过；1 = 有违规。
"""
from __future__ import annotations

import argparse
from collections import Counter
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
# 仅纯索引 / 模板 / 单测文件允许用 non_rule_changes 免审覆盖；
# 规则文件、SKILL 入口与项目 README 必须落入 rules[] 或经审核的 view_files[]。
NON_RULE_ALLOW = {
    "references/README.md",
    "references/40-cases/INDEX.md",
    "docs/changes/README.md",
    "scripts/test-check-change.py",
    # 保留旧路径以兼容历史 manifest 回归测试
    "references/v2/README.md",
    "references/v2/40-cases/INDEX.md",
}
TEXT_SUFFIXES = (".md", ".tsv", ".txt")
HEX_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
SECTION_REF_RE = re.compile(r"§\s*(\d+(?:\.\d+)*|[一二三四五六七八九十百]+)")
HEADING_ID_RES = (
    re.compile(r"^#{1,6}\s+(\d+(?:\.\d+)*)(?=$|[\s、.．：:）)])"),
    re.compile(r"^#{1,6}\s+([一二三四五六七八九十百]+)(?=$|[\s、.．：:）)])"),
)
MIN_OLD_TEXT = 6
MIN_SEARCH = 6
MIN_SEMANTIC = 4
MIN_ANCHOR = 4
MIN_EVIDENCE = 6
DEFAULT_SCOPES = {"references/", "docs/"}


def get_str(obj: dict, key: str) -> str:
    """只接受真正的字符串；JSON null / 数值 / 布尔等一律返回空串，避免 str(None)=='None' 绕过。"""
    val = obj.get(key)
    return val.strip() if isinstance(val, str) else ""


def valid_review_ref(ref: str) -> bool:
    return bool(
        re.fullmatch(r"https?://\S+", ref)
        or re.fullmatch(r"PR #\d+.*", ref)
        or re.fullmatch(r"review:\S+.*", ref)
    )


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=False
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败：{proc.stderr.strip()}")
    return proc.stdout


def resolve(root: Path, rev: str) -> str:
    return git(root, "rev-parse", "--verify", rev).strip()


def is_hex_commit_sha(root: Path, rev: str) -> bool:
    """正式模式仅接受 7–40 位十六进制提交 SHA，排除 HEAD / @ / HEAD~0 / 分支与 tag 符号引用。"""
    if not HEX_SHA_RE.fullmatch(rev):
        return False
    for prefix in ("refs/heads/", "refs/tags/"):
        proc = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", prefix + rev],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode == 0:
            return False
    return True


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    proc = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.returncode == 0


def read_at(root: Path, rev: str, path: str) -> str:
    return git(root, "show", f"{rev}:{path}")


def changed_files(root: Path, base: str, head: str) -> set[str]:
    return set(git(root, "diff", "--name-only", base, head).splitlines())


def head_text_files(root: Path, head: str, scope: list[str]) -> list[str]:
    names = git(root, "ls-tree", "-r", "--name-only", head).splitlines()
    out: list[str] = []
    for name in names:
        if not name.endswith(TEXT_SUFFIXES):
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


def added_text(root: Path, base: str, head: str, path: str) -> str:
    """head 相对 base 的新增行；只查新引入的引用，不追旧账。"""
    diff = git(root, "diff", "--unified=0", base, head, "--", path)
    return "\n".join(
        line[1:]
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )


def defined_section_ids(texts: dict[str, str]) -> set[str]:
    """从 Markdown 标题提取章节号（数字或中文序号）。"""
    ids: set[str] = set()
    for text in texts.values():
        for line in text.splitlines():
            for pattern in HEADING_ID_RES:
                match = pattern.match(line)
                if match:
                    ids.add(match.group(1))
    return ids


def dangling_section_refs(
    added_texts: dict[str, str], corpus_texts: dict[str, str]
) -> list[tuple[str, str]]:
    """新增 / 改动的 §ref 必须解析到语料里现存的章节标题。"""
    defined = defined_section_ids(corpus_texts)
    out: list[tuple[str, str]] = []
    for path, text in added_texts.items():
        for token in sorted(set(SECTION_REF_RE.findall(text))):
            if token not in defined:
                out.append((path, token))
    return out


def removed_section_ids(
    base_texts: dict[str, str], head_texts: dict[str, str]
) -> set[str]:
    """base 有、head 语料里没有的章节号：删标题或改号。"""
    return defined_section_ids(base_texts) - defined_section_ids(head_texts)


def stale_section_refs(
    removed: set[str], corpus_texts: dict[str, str]
) -> list[tuple[str, int, str]]:
    """全语料反扫仍指向被删 / 改号章节的引用；TSV / TXT 兼查裸章号。"""
    out: list[tuple[str, int, str]] = []
    bare = {token: re.compile(rf"(?<![\d.]){re.escape(token)}(?![\d.])") for token in removed}
    for path, text in corpus_texts.items():
        check_bare = not path.endswith(".md")
        for no, line in enumerate(text.splitlines(), 1):
            hits = set(SECTION_REF_RE.findall(line)) & removed
            if check_bare:
                hits |= {token for token, pattern in bare.items() if pattern.search(line)}
            for token in sorted(hits):
                out.append((path, no, token))
    return out


def get_list(data: dict, key: str, errors: list[str]) -> list:
    raw = data.get(key)
    if raw is None:
        return []
    if not isinstance(raw, list):
        errors.append(f"{key} 必须是数组")
        return []
    return raw


def lint(
    root: Path,
    manifest_path: Path,
    base_arg: str,
    head_arg: str,
    draft: bool = False,
    from_disk: bool = False,
) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"manifest 读不了 / 不是合法 JSON：{exc}"]
    if not isinstance(data, dict):
        return ["manifest 顶层必须是 JSON 对象"]

    try:
        base = resolve(root, base_arg)
        head = resolve(root, head_arg)
    except RuntimeError as exc:
        return [f"base/head 解析失败：{exc}"]

    try:
        manifest_rel: str | None = manifest_path.relative_to(root).as_posix()
    except ValueError:
        manifest_rel = None

    # 正式模式默认核对 --head 提交树中的 manifest 与被检文件完全一致，防止磁盘假绿绕过；
    # 仅 --draft 或显式 --from-disk（本地预检 / 单测）跳过提交树一致性比对。
    if not draft and not from_disk:
        if not manifest_rel:
            errors.append("正式模式要求 manifest 位于仓库根目录内并已提交到 --head")
        else:
            try:
                committed_data = json.loads(read_at(root, head, manifest_rel))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"--head 提交中不存在或无法解析 manifest（{manifest_rel}）：{exc}")
            else:
                if committed_data != data:
                    errors.append(
                        f"磁盘 manifest 与 --head({head[:12]}) 提交内 {manifest_rel} 不一致（请先提交或加 --draft）"
                    )

    required_top = REQUIRED_TOP - ({"approval"} if draft else set())
    missing = required_top - set(data)
    if missing:
        errors.append(f"顶层缺字段：{', '.join(sorted(missing))}")
    for key in ("change", "title", "base", "head", "classification"):
        if not get_str(data, key):
            errors.append(f"{key} 为空或非字符串")

    raw_base = get_str(data, "base")
    if raw_base:
        if not draft and not is_hex_commit_sha(root, raw_base):
            errors.append(f"正式模式要求 manifest.base 为不可变十六进制提交 SHA：{raw_base!r}")
        else:
            try:
                if resolve(root, raw_base) != base:
                    errors.append(f"manifest.base 解析后与 --base 不一致：{raw_base!r}")
            except RuntimeError:
                errors.append(f"manifest.base 解析不了：{raw_base!r}")

    # 正式模式强制 manifest.head 为不可变十六进制提交 SHA（拦截 HEAD / @ / HEAD~0 / 分支名）；
    # 支持 manifest-only 尾部钉扎提交，且强制 pinned 严格晚于 base。
    content_head = head
    tail_pinned = False
    raw_head = get_str(data, "head")
    if raw_head:
        if raw_head == "HEAD":
            if not draft:
                errors.append("正式模式禁止 manifest.head 使用字面 'HEAD'（须为不可变十六进制提交 SHA，开发期加 --draft）")
        elif not draft and not is_hex_commit_sha(root, raw_head):
            errors.append(f"正式模式要求 manifest.head 为不可变十六进制提交 SHA（禁止符号引用）：{raw_head!r}")
        else:
            try:
                pinned = resolve(root, raw_head)
            except RuntimeError:
                errors.append(f"manifest.head 解析不了：{raw_head!r}")
            else:
                if pinned == base or not is_ancestor(root, base, pinned):
                    errors.append(
                        f"manifest.head 必须是 --base 的严格后代提交：{raw_head!r}"
                    )
                elif pinned != head:
                    if manifest_rel and is_ancestor(root, pinned, head):
                        tail_diff = changed_files(root, pinned, head) - {manifest_rel}
                        if not tail_diff:
                            content_head = pinned
                            tail_pinned = True
                        else:
                            errors.append(
                                f"manifest.head 解析后与 --head 不一致：{raw_head!r}"
                                "（钉扎提交之后存在非 manifest 文件改动："
                                + "、".join(sorted(tail_diff))
                                + "）"
                            )
                    else:
                        errors.append(f"manifest.head 解析后与 --head 不一致：{raw_head!r}")

    if data.get("classification") not in TYPES:
        errors.append(f"classification 不在 {sorted(TYPES)}：{data.get('classification')!r}")

    rules_raw = get_list(data, "rules", errors)
    rules: list[dict] = []
    if not rules_raw and "rules 必须是数组" not in errors:
        errors.append("rules 为空：至少一条规则")
    ids: set[str] = set()
    for i, rule in enumerate(rules_raw, 1):
        where = f"rules[{i}]"
        if not isinstance(rule, dict):
            errors.append(f"{where} 必须是对象")
            continue
        rules.append(rule)
        rid = get_str(rule, "id")
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
        evidence = get_str(rule, "evidence")
        if len(evidence) < MIN_EVIDENCE:
            errors.append(f"{where} evidence 太短（<{MIN_EVIDENCE}）：{evidence!r}")

        new_raw = rule.get("new")
        if not isinstance(new_raw, dict):
            errors.append(f"{where} new 必须是对象")
            new = {}
        else:
            new = new_raw
        new_file = get_str(new, "file")
        anchor = get_str(new, "anchor")
        if not new_file:
            errors.append(f"{where} 缺 new.file")
        else:
            try:
                content = read_at(root, content_head, new_file)
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
        if not get_str(new, "section"):
            errors.append(f"{where} 缺 new.section")

        if rtype == "add":
            if rule.get("old") is not None:
                errors.append(f"{where} type=add 却给了 old")
            search = get_str(rule, "same_trigger_search")
            if len(search) < MIN_SEARCH:
                errors.append(f"{where} same_trigger_search 太短（<{MIN_SEARCH}）：{search!r}")
            if rule.get("disposition") != "not-applicable":
                errors.append(f"{where} type=add 的 disposition 必须是 not-applicable")
        else:
            old_raw = rule.get("old")
            if not isinstance(old_raw, dict):
                errors.append(f"{where} type={rtype} old 必须是对象")
                continue
            old_file = get_str(old_raw, "file")
            if not old_file:
                errors.append(f"{where} type={rtype} 缺 old.file")
                continue
            line = old_raw.get("line")
            text = get_str(old_raw, "text")
            if len(text) < MIN_OLD_TEXT:
                errors.append(f"{where} old.text 太短（<{MIN_OLD_TEXT}）：{text!r}")
            if not isinstance(line, int) or isinstance(line, bool):
                errors.append(f"{where} type={rtype} 缺 old.line（整数）")
                continue
            try:
                lines = read_at(root, base, old_file).splitlines()
            except RuntimeError:
                errors.append(f"{where} base 中读不到 old.file：{old_file}")
                continue
            if line < 1 or line > len(lines):
                errors.append(f"{where} old.line={line} 超出 base:{old_file} 行数 {len(lines)}")
            elif text and text not in lines[line - 1]:
                errors.append(
                    f"{where} base:{old_file}:{line} 不含 old.text；实际：{lines[line - 1][:120]!r}"
                )

    anchor_map: dict[tuple[str, str], str] = {}
    for rule in rules:
        new = rule.get("new") if isinstance(rule.get("new"), dict) else {}
        key = (get_str(new, "file"), get_str(new, "anchor"))
        section = get_str(new, "section")
        if key[0] and key[1] and key in anchor_map and anchor_map[key] != section:
            errors.append(f"{rule.get('id')} anchor 跨规则重复且 section 不同：{key}")
        if key[0] and key[1]:
            anchor_map.setdefault(key, section)

    whitelist_raw = get_list(data, "whitelist", errors)
    whitelist: list[dict] = []
    white_ids: set[str] = set()
    for i, w in enumerate(whitelist_raw, 1):
        where = f"whitelist[{i}]"
        if not isinstance(w, dict):
            errors.append(f"{where} 必须是对象")
            continue
        whitelist.append(w)
        wid = get_str(w, "rule_id")
        if not wid or wid not in ids:
            errors.append(f"{where} rule_id 不存在：{w.get('rule_id')!r}")
        else:
            white_ids.add(wid)
        if not get_str(w, "reason"):
            errors.append(f"{where} 缺 reason")
        if w.get("reviewer") not in REVIEWERS:
            errors.append(f"{where} reviewer 不在 {sorted(REVIEWERS)}：{w.get('reviewer')!r}")
        ref = get_str(w, "review_ref")
        if not ref:
            errors.append(f"{where} 缺 review_ref")
        elif not valid_review_ref(ref):
            errors.append(f"{where} review_ref 需为有效链接 / PR #<N> / review:<id>：{ref!r}")
    for rule in rules:
        if rule.get("status") == "whitelist" and get_str(rule, "id") not in white_ids:
            errors.append(f"{rule.get('id')} 状态=whitelist 但 whitelist 表无对应条目")

    scans_raw = get_list(data, "scans", errors)
    scans: list[dict] = []
    if not scans_raw and "scans 必须是数组" not in errors:
        errors.append("scans 为空：至少一条扫描")
    for i, scan in enumerate(scans_raw, 1):
        where = f"scans[{i}]"
        if not isinstance(scan, dict):
            errors.append(f"{where} 必须是对象")
            continue
        scans.append(scan)
        query = get_str(scan, "query")
        scope_raw = scan.get("scope")
        if not isinstance(scope_raw, list) or not all(isinstance(s, str) and s.strip() for s in scope_raw):
            errors.append(f"{where} scope 必须是非空字符串数组")
            continue
        scope = [s.strip() for s in scope_raw]
        if not query:
            errors.append(f"{where} 缺 query")
            continue
        if not scope:
            errors.append(f"{where} 缺 scope")
            continue
        if not DEFAULT_SCOPES.issubset(set(scope)) and not get_str(scan, "scope_reason"):
            errors.append(f"{where} scope 未覆盖默认 {sorted(DEFAULT_SCOPES)} 且缺 scope_reason")
        if scan.get("conclusion") not in CONCLUSIONS:
            errors.append(f"{where} conclusion 不在 {sorted(CONCLUSIONS)}：{scan.get('conclusion')!r}")
        if scan.get("conclusion") == "unresolved":
            errors.append(f"{where} conclusion=unresolved")
        try:
            pattern = re.compile(query)
        except re.error as exc:
            errors.append(f"{where} query 不是合法正则：{exc}")
            continue
        files = head_text_files(root, content_head, scope)
        if not files:
            errors.append(f"{where} scope 在 head 中没有 .md / .tsv / .txt 文件：{scope}")
            continue
        found: list[tuple[str, int, str]] = []
        for path in files:
            for no, line in enumerate(read_at(root, content_head, path).splitlines(), 1):
                for m in pattern.finditer(line):
                    found.append((path, no, m.group(0)))
        listed_raw = scan.get("hits")
        if listed_raw is None:
            listed_raw = []
        if not isinstance(listed_raw, list):
            errors.append(f"{where} hits 必须是数组")
            continue
        listed = [h for h in listed_raw if isinstance(h, dict)]
        if len(listed) != len(listed_raw):
            errors.append(f"{where} hits 元素必须是对象")
        if not listed and scan.get("conclusion") == "match":
            errors.append(f"{where} 零命中 scan 不能 conclusion=match；给 note 或改 conclusion")
        for rel, no, hit in found:
            match = any(
                get_str(h, "file") == rel and hit in get_str(h, "text")
                for h in listed
            )
            if not match:
                errors.append(f"{where} 未登记的命中：{rel}:{no} {hit!r}")
        for h in listed:
            if h.get("conclusion") not in CONCLUSIONS:
                errors.append(f"{where} hit 的 conclusion 不合法：{h.get('conclusion')!r}")
            if h.get("conclusion") == "unresolved":
                errors.append(f"{where} hit conclusion=unresolved：{h.get('file')!r}")
            if h.get("conclusion") == "match" and not get_str(h, "evidence"):
                errors.append(f"{where} hit conclusion=match 缺 evidence：{h.get('file')!r}")
            if h.get("conclusion") == "whitelist":
                if not get_str(h, "reason"):
                    errors.append(f"{where} whitelist hit 缺 reason：{h.get('file')!r}")
                if h.get("reviewer") not in REVIEWERS:
                    errors.append(f"{where} whitelist hit reviewer 不合法：{h.get('reviewer')!r}")
                href = get_str(h, "review_ref")
                if not href:
                    errors.append(f"{where} whitelist hit 缺 review_ref：{h.get('file')!r}")
                elif not valid_review_ref(href):
                    errors.append(f"{where} whitelist hit review_ref 需为有效链接 / PR #<N> / review:<id>：{href!r}")
            file = get_str(h, "file")
            text = get_str(h, "text")
            if not file or not text:
                errors.append(f"{where} hit 缺 file 或 text")
                continue
            if file not in files:
                errors.append(f"{where} hit 文件不在 scope：{file}")
            elif not find_lines(root, content_head, file, text):
                errors.append(f"{where} 登记的命中在 head:{file} 中不存在：{text!r}")
        found_by_file = Counter(rel for rel, _, _ in found)
        listed_by_file = Counter(get_str(h, "file") for h in listed if get_str(h, "file"))
        for file, n in found_by_file.items():
            if listed_by_file[file] < n:
                errors.append(f"{where} {file} 命中登记数 {listed_by_file[file]} < 实际 {n}")

    changed = changed_files(root, base, head)
    added_texts: dict[str, str] = {}
    base_texts: dict[str, str] = {}
    for path in sorted(changed):
        if not path.endswith(TEXT_SUFFIXES):
            continue
        try:
            base_texts[path] = read_at(root, base, path)
        except RuntimeError:
            pass
        try:
            added_texts[path] = added_text(root, base, content_head, path)
        except RuntimeError:
            continue
    corpus_scope = sorted(
        {
            scope
            for scan in scans
            for scope in (scan.get("scope") if isinstance(scan.get("scope"), list) else [])
            if isinstance(scope, str) and scope.strip()
        }
    ) or sorted(DEFAULT_SCOPES)
    corpus_files = head_text_files(root, content_head, corpus_scope)
    corpus_texts = {p: read_at(root, content_head, p) for p in corpus_files}
    section_whitelist_raw = get_list(data, "section_ref_whitelist", errors)
    white_refs: set[str] = set()
    for i, item in enumerate(section_whitelist_raw, 1):
        where = f"section_ref_whitelist[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where} 必须是对象")
            continue
        ref = get_str(item, "ref")
        if not ref:
            errors.append(f"{where} 缺 ref")
        else:
            white_refs.add(ref.lstrip("§"))
        if not get_str(item, "reason"):
            errors.append(f"{where} 缺 reason")
        if item.get("reviewer") not in REVIEWERS:
            errors.append(f"{where} reviewer 不在 {sorted(REVIEWERS)}：{item.get('reviewer')!r}")
        review_ref = get_str(item, "review_ref")
        if not review_ref:
            errors.append(f"{where} 缺 review_ref")
        elif not valid_review_ref(review_ref):
            errors.append(f"{where} review_ref 需为有效链接 / PR #<N> / review:<id>：{review_ref!r}")
    for path, token in dangling_section_refs(added_texts, corpus_texts):
        if token in white_refs:
            continue
        errors.append(
            f"章节引用解析不到：{path} §{token}"
            "（语料里没有对应标题；外部引用加 section_ref_whitelist）"
        )
    removed = removed_section_ids(base_texts, corpus_texts)
    for path, no, token in stale_section_refs(removed, corpus_texts):
        if token in white_refs:
            continue
        errors.append(
            f"章节已删 / 改号但仍被引用：{path}:{no} §{token}"
            "（同步改引用，或加 section_ref_whitelist 说明保留原因）"
        )

    semantic_raw = get_list(data, "semantic_checks", errors)
    semantic: list[dict] = []
    if not semantic_raw and "semantic_checks 必须是数组" not in errors:
        errors.append("semantic_checks 为空：反向冲突至少一条")
    for i, item in enumerate(semantic_raw, 1):
        where = f"semantic_checks[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where} 必须是对象")
            continue
        semantic.append(item)
        if len(get_str(item, "item")) < MIN_SEMANTIC:
            errors.append(f"{where} item 太短（<{MIN_SEMANTIC}）")
        if item.get("conclusion") not in CONCLUSIONS:
            errors.append(f"{where} conclusion 不合法：{item.get('conclusion')!r}")
        if item.get("conclusion") == "unresolved":
            errors.append(f"{where} conclusion=unresolved")
        if len(get_str(item, "evidence")) < MIN_SEMANTIC:
            errors.append(f"{where} evidence 太短（<{MIN_SEMANTIC}）")

    raw_approval = data.get("approval")
    if raw_approval is not None and not isinstance(raw_approval, dict):
        errors.append("approval 必须是对象")
    elif not draft:
        approval = raw_approval or {}
        for key in ("user_quote", "timestamp", "scope", "base", "head", "link"):
            if not get_str(approval, key):
                errors.append(f"approval 缺 {key}")
        app_base_raw = get_str(approval, "base")
        if app_base_raw:
            if not is_hex_commit_sha(root, app_base_raw):
                errors.append(f"正式模式要求 approval.base 为不可变十六进制提交 SHA：{app_base_raw!r}")
            else:
                try:
                    if resolve(root, app_base_raw) != base:
                        errors.append("approval.base 解析后与 --base 不一致")
                except RuntimeError:
                    errors.append(f"approval.base 解析不了：{app_base_raw!r}")
        app_head_raw = get_str(approval, "head")
        if app_head_raw == "HEAD":
            errors.append("正式模式禁止 approval.head 使用字面 'HEAD'（须为不可变十六进制提交 SHA）")
        elif app_head_raw:
            if not is_hex_commit_sha(root, app_head_raw):
                errors.append(f"正式模式要求 approval.head 为不可变十六进制提交 SHA（禁止符号引用）：{app_head_raw!r}")
            else:
                try:
                    app_head = resolve(root, app_head_raw)
                    if app_head not in {head, content_head}:
                        errors.append("approval.head 解析后与 --head 不一致")
                except RuntimeError:
                    errors.append("approval.head 解析不了")
    elif isinstance(raw_approval, dict):
        # draft 模式下允许字段缺省或为 null；仅当已填非空字符串时校验其可解析且一致
        if raw_approval.get("base") is not None and not isinstance(raw_approval.get("base"), str):
            errors.append("approval.base 必须是字符串或 null")
        else:
            app_base_raw = get_str(raw_approval, "base")
            if app_base_raw:
                try:
                    if resolve(root, app_base_raw) != base:
                        errors.append("approval.base 解析后与 --base 不一致")
                except RuntimeError:
                    errors.append(f"approval.base 解析不了：{app_base_raw!r}")
        if raw_approval.get("head") is not None and not isinstance(raw_approval.get("head"), str):
            errors.append("approval.head 必须是字符串或 null")
        else:
            app_head_raw = get_str(raw_approval, "head")
            if app_head_raw and app_head_raw != "HEAD":
                try:
                    app_head = resolve(root, app_head_raw)
                    if app_head not in {head, content_head}:
                        errors.append("approval.head 解析后与 --head 不一致")
                except RuntimeError:
                    errors.append("approval.head 解析不了")

    rebuild = data.get("rebuild")
    if not isinstance(rebuild, dict):
        errors.append("rebuild 必须是对象")
    elif not isinstance(rebuild.get("triggered"), bool):
        errors.append("rebuild.triggered 必须是布尔")
    elif rebuild.get("triggered"):
        if not get_str(rebuild, "reason"):
            errors.append("rebuild.triggered=true 但缺 reason")
        old_behaviors = rebuild.get("old_behaviors")
        if not isinstance(old_behaviors, list) or not old_behaviors or not all(
            isinstance(x, str) and x.strip() for x in old_behaviors
        ):
            errors.append("rebuild.triggered=true 但 old_behaviors 为空或含非法项")

    covered: set[str] = set()
    for rule in rules:
        old = rule.get("old")
        if isinstance(old, dict) and get_str(old, "file"):
            covered.add(get_str(old, "file"))
        new = rule.get("new")
        if isinstance(new, dict) and get_str(new, "file"):
            covered.add(get_str(new, "file"))
    for i, item in enumerate(get_list(data, "non_rule_changes", errors), 1):
        if not isinstance(item, dict):
            errors.append(f"non_rule_changes[{i}] 必须是对象")
            continue
        file = get_str(item, "file")
        if not file or not get_str(item, "reason"):
            errors.append("non_rule_changes 条目缺 file 或 reason")
            continue
        if file not in NON_RULE_ALLOW:
            errors.append(f"non_rule_changes 不允许覆盖规则文件：{file}")
        covered.add(file)
    view_files_list = get_list(data, "view_files", errors)
    for i, item in enumerate(view_files_list, 1):
        where = f"view_files[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where} 必须是对象")
            continue
        file = get_str(item, "file")
        if not file or not get_str(item, "reason"):
            errors.append(f"{where} 缺 file 或 reason")
            continue
        if item.get("reviewer") not in REVIEWERS:
            errors.append(f"{where} reviewer 不在 {sorted(REVIEWERS)}：{item.get('reviewer')!r}")
        review_ref = get_str(item, "review_ref")
        if not review_ref:
            errors.append(f"{where} 缺 review_ref")
        elif not valid_review_ref(review_ref):
            errors.append(f"{where} review_ref 需为有效链接 / PR #<N> / review:<id>：{review_ref!r}")
        try:
            read_at(root, content_head, file)
        except RuntimeError:
            errors.append(f"{where} head 中不存在 file：{file}")
            continue
        covered.add(file)
    count_checks_list = get_list(data, "count_checks", errors)
    for i, item in enumerate(count_checks_list, 1):
        where = f"count_checks[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where} 必须是对象")
            continue
        if not get_str(item, "name"):
            errors.append(f"{where} 缺 name")
        if "value" not in item or item.get("value") is None:
            errors.append(f"{where} 缺 value")
        source = get_str(item, "source")
        command = get_str(item, "command")
        if not source:
            errors.append(f"{where} 缺 source")
        else:
            try:
                read_at(root, content_head, source)
            except RuntimeError:
                errors.append(f"{where} head 中不存在 source：{source}")
        if len(command) < MIN_SEARCH:
            errors.append(f"{where} command 太短（<{MIN_SEARCH}）：{command!r}")
    if manifest_rel:
        covered.add(manifest_rel)
    uncovered = sorted(changed - covered)
    if uncovered:
        errors.append("有改动文件未被 manifest 覆盖：" + "、".join(uncovered))

    if any(r.get("status") == "unresolved" for r in rules):
        errors.append("存在 status=unresolved 的规则")

    by_type = {t: sum(1 for r in rules if r.get("type") == t) for t in sorted(TYPES)}
    by_status = {s: sum(1 for r in rules if r.get("status") == s) for s in sorted(STATUSES)}
    tail_note = f" (content_pinned={content_head[:12]})" if tail_pinned else ""
    modes = ([("draft")] if draft else []) + ([("from-disk")] if from_disk else [])
    mode_note = f" mode={','.join(modes)}" if modes else ""
    print(
        f"base={base[:12]} head={head[:12]}{tail_note}{mode_note} rules={len(rules)} "
        f"add/replace/retire={by_type['add']}/{by_type['replace']}/{by_type['retire']} "
        f"status done/whitelist/unresolved={by_status['done']}/{by_status['whitelist']}/{by_status['unresolved']} "
        f"whitelist_entries={len(whitelist)} scans={len(scans)} "
        f"semantic_checks={len(semantic)} view_files={len(view_files_list)} "
        f"count_checks={len(count_checks_list)} changed_files={len(changed)}"
    )
    if errors:
        print("违规：")
        for err in errors:
            print(" - " + err)
        return errors
    suffix = "（仅本地预检，非正式合并门禁）" if (from_disk and not draft) else ""
    print(f"绿：manifest 结构与证据检查通过{suffix}")
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--draft",
        action="store_true",
        help="开发 / 审核期模式：允许本地未提交 manifest 与字面 HEAD，跳过 approval 完整性校验",
    )
    parser.add_argument(
        "--from-disk",
        action="store_true",
        help="本地预检 / 单测模式：从磁盘读取未提交 manifest，不要求与 --head 提交树一致（正式合并门禁不得使用）",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve()
    manifest = (root / args.manifest).resolve()
    if not manifest.exists():
        print(f"红：manifest 不存在：{manifest}")
        return 1
    try:
        errors = lint(
            root, manifest, args.base, args.head, draft=args.draft, from_disk=args.from_disk
        )
    except Exception as exc:  # noqa: BLE001
        print(f"红：校验器自身报错：{exc}")
        return 1
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
