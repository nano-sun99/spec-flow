#!/usr/bin/env python3
"""校验替换式变更的 v2 薄声明 manifest（schema: 2 + 自动扫 diff）。

用法：
    python3 scripts/check-change.py --manifest docs/changes/<slug>/manifest.json \
        --base <git-rev> [--head <git-rev>] [--root .] [--draft] [--from-disk]
"""
from __future__ import annotations

import argparse
import json
import posixpath
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

SCHEMA_VERSION = 2
TYPES = {"add", "replace", "retire"}
DISPOSITIONS = {"replace", "delete", "merge", "alias", "keep-history", "keep-scoped", "not-applicable"}
STATUSES = {"done", "whitelist", "unresolved"}
CONCLUSIONS = {"match", "changed", "whitelist", "unresolved"}
REVIEWERS = {"user", "review-agent"}
REQUIRED_TOP = {"schema", "change", "title", "base", "head", "classification", "rules", "scans", "semantic_checks", "approval", "rebuild"}
DEFAULT_RULE_PATHS = ["SKILL.md", "references/"]
DEFAULT_RULE_EXCLUDE = ["references/40-cases/", "references/README.md", "references/v2/SKILL.md"]
TEXT_SUFFIXES = (".md", ".tsv", ".txt")
HEX_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
SECTION_REF_RE = re.compile(r"§\s*(\d+(?:\.\d+)*|[一二三四五六七八九十百]+)")
HEADING_ID_RES = (
    re.compile(r"^#{1,6}\s+(\d+(?:\.\d+)*)(?=$|[\s、.．：:）)])"),
    re.compile(r"^#{1,6}\s+([一二三四五六七八九十百]+)(?=$|[\s、.．：:）)])"),
)
HUNK_NEW_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
ROOT_README_RE = re.compile(r"^README[^/]*\.md$")
REVIEW_REF_RE = re.compile(r"^(?:https?://\S+|PR #\d+.*|review:\S+.*)$")
MIN_SUMMARY, MIN_MATCH, MIN_SEMANTIC = 6, 4, 4


def get_str(obj: dict, key: str) -> str:
    val = obj.get(key)
    return val.strip() if isinstance(val, str) else ""


def in_set(val: object, allowed: set[str]) -> bool:
    return isinstance(val, str) and val in allowed


def is_pos_int(val: object) -> bool:
    return isinstance(val, int) and not isinstance(val, bool) and val >= 1


def valid_review_ref(ref: str) -> bool:
    return bool(REVIEW_REF_RE.fullmatch(ref))


def is_valid_rel_path(pat: str) -> bool:
    if not pat or pat.startswith("/") or "\\" in pat:
        return False
    body = pat[:-1] if pat.endswith("/") else pat
    return bool(body) and all(s not in ("", ".", "..") for s in body.split("/"))


def path_matches(path: str, pat: str) -> bool:
    return path.startswith(pat) if pat.endswith("/") else path == pat


def scope_covers(scope_item: str, rule_path: str) -> bool:
    return scope_item == rule_path or (scope_item.endswith("/") and rule_path.startswith(scope_item))


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=root, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败：{proc.stderr.strip()}")
    return proc.stdout


def resolve(root: Path, rev: str) -> str:
    return git(root, "rev-parse", "--verify", f"{rev}^{{commit}}").strip()


def is_hex_commit_sha(root: Path, rev: str) -> bool:
    if not HEX_SHA_RE.fullmatch(rev):
        return False
    return all(
        subprocess.run(["git", "show-ref", "--verify", "--quiet", p + rev], cwd=root, text=True, capture_output=True, check=False).returncode != 0
        for p in ("refs/heads/", "refs/tags/")
    )


def is_ancestor(root: Path, anc: str, desc: str) -> bool:
    return subprocess.run(["git", "merge-base", "--is-ancestor", anc, desc], cwd=root, text=True, capture_output=True, check=False).returncode == 0


def read_at(root: Path, rev: str, path: str) -> str:
    return git(root, "show", f"{rev}:{path}")


def list_tree(root: Path, rev: str) -> list[str]:
    return [p for p in git(root, "ls-tree", "-r", "-z", "--name-only", rev).split("\0") if p]


def diff_no_renames_paths(root: Path, rev1: str, rev2: str) -> set[str]:
    return {p for p in git(root, "diff", "--no-renames", "--name-only", "-z", rev1, rev2).split("\0") if p}


def parse_name_status_z(raw: str) -> list[tuple[str, str, str]]:
    tokens = raw.split("\0")
    if tokens and tokens[-1] == "":
        tokens.pop()
    entries: list[tuple[str, str, str]] = []
    i = 0
    while i < len(tokens):
        st = tokens[i]
        if st in ("A", "M", "T", "D"):
            if i + 1 >= len(tokens):
                raise RuntimeError(f"git diff --name-status 令牌截断：{st!r}")
            entries.append((st, tokens[i + 1], "") if st == "D" else (st, "", tokens[i + 1]))
            i += 2
        elif (st.startswith("R") or st.startswith("C")) and st[1:].isdigit():
            if i + 2 >= len(tokens):
                raise RuntimeError(f"git diff --name-status 令牌截断：{st!r}")
            entries.append((st, tokens[i + 1], tokens[i + 2]))
            i += 3
        else:
            raise RuntimeError(f"git diff --name-status 未知状态码：{st!r}")
    return entries


def split_fence_state(text: str) -> tuple[list[tuple[int, str]], set[int]]:
    kept, fenced, fence = [], set(), None
    for no, line in enumerate(text.splitlines(), 1):
        st = line.lstrip()
        if fence:
            fenced.add(no)
            if st.startswith(fence):
                fence = None
        elif st.startswith("```") or st.startswith("~~~"):
            fence = st[:3]
            fenced.add(no)
        else:
            kept.append((no, line))
    return kept, fenced


def scan_lines(path: str, text: str) -> list[tuple[int, str]]:
    return split_fence_state(text)[0] if path.endswith(".md") else list(enumerate(text.splitlines(), 1))


def is_default_excluded(path: str, manifest_rel: str | None, touched_specs: set[str], explicit_scopes: list[str] | None = None) -> bool:
    if manifest_rel and path == manifest_rel:
        return True
    scopes = explicit_scopes or []
    cancelled = lambda pre: any(s.startswith(pre) and path_matches(path, s) for s in scopes)
    if path.startswith("docs/archive/"):
        return not cancelled("docs/archive/")
    if path.startswith("docs/changes/") and "/" in path[len("docs/changes/"):]:
        return not cancelled("docs/changes/")
    if path.startswith("references/40-cases/"):
        return not cancelled("references/40-cases/")
    if path.startswith("docs/specs/") and path not in touched_specs:
        return not cancelled("docs/specs/")
    return False


def filter_text_files(all_files: list[str], scopes: list[str], manifest_rel: str | None, touched_specs: set[str], explicit_scopes: list[str] | None = None) -> list[str]:
    return sorted({
        p for p in all_files
        if p.endswith(TEXT_SUFFIXES)
        and any(path_matches(p, s) for s in scopes)
        and not is_default_excluded(p, manifest_rel, touched_specs, explicit_scopes)
    })


def added_lines_for_entry(root: Path, base: str, head: str, st: str, old_p: str, new_p: str, head_text: str) -> list[tuple[int, str]]:
    if st == "A" or st.startswith("C"):
        lines = list(enumerate(head_text.splitlines(), 1))
    else:
        diff = git(root, "diff", "--unified=0", f"{base}:{old_p}", f"{head}:{new_p}") if st.startswith("R") else git(root, "diff", "--unified=0", base, head, "--", new_p)
        lines, cur, in_hunk = [], 0, False
        for raw in diff.splitlines():
            if raw.startswith("diff --git "):
                in_hunk = False
                continue
            m = HUNK_NEW_RE.match(raw)
            if m:
                cur, in_hunk = int(m.group(1)), True
                continue
            if in_hunk and raw.startswith("+"):
                lines.append((cur, raw[1:]))
                cur += 1
    if new_p.endswith(".md"):
        fenced = split_fence_state(head_text)[1]
        lines = [(no, ln) for no, ln in lines if no not in fenced]
    return lines


def defined_section_ids(texts: dict[str, str]) -> set[str]:
    return {m.group(1) for p, t in texts.items() for _, ln in scan_lines(p, t) for pat in HEADING_ID_RES if (m := pat.match(ln))}


def iter_md_link_targets(line: str) -> list[str]:
    """扫描 Markdown 链接目标，支持链接文字内配对 [...] / 反引号以及目标内配对 (...) / <...>。"""
    targets: list[str] = []
    i, n = 0, len(line)
    while i < n:
        if line[i] != "[":
            i += 1
            continue
        # 匹配配对 [...]（含内联反引号）
        j, depth, in_code = i + 1, 1, False
        while j < n and depth > 0:
            ch = line[j]
            if ch == "`":
                in_code = not in_code
            elif not in_code:
                if ch == "[":
                    depth += 1
                elif ch == "]":
                    depth -= 1
            j += 1
        if depth != 0 or j >= n or line[j] != "(":
            i += 1
            continue
        # 匹配配对 (...)（支持 <...> 包裹）
        k, pdepth, in_angle = j + 1, 1, False
        while k < n and pdepth > 0:
            ch = line[k]
            if ch == "<" and k == j + 1:
                in_angle = True
            elif ch == ">" and in_angle:
                in_angle = False
            elif not in_angle:
                if ch == "(":
                    pdepth += 1
                elif ch == ")":
                    pdepth -= 1
            k += 1
        if pdepth == 0:
            targets.append(line[j + 1 : k - 1])
            i = k
        else:
            i += 1
    return targets


def parse_md_link_target(cur_file: str, raw_target: str) -> str | None:
    t = raw_target.strip()
    if not t:
        return None
    t = t[1:t.index(">")].strip() if (t.startswith("<") and ">" in t) else t.split()[0]
    if t.startswith(("http://", "https://", "mailto:")):
        return None
    t = unquote(t.split("#", 1)[0].split("?", 1)[0])
    if not t or t.startswith("/"):
        return None
    base_dir = posixpath.dirname(cur_file)
    norm = posixpath.normpath(posixpath.join(base_dir, t) if base_dir else t)
    return None if (norm in ("", ".") or norm.startswith("..")) else norm


def allow_covers_hit(a_file: str, a_match: str, rel: str, line: str, m_start: int, m_end: int) -> bool:
    if a_file != rel:
        return False
    mlen, pos = len(a_match), line.find(a_match, 0)
    while pos != -1:
        if pos <= m_start and m_end <= pos + mlen:
            return True
        pos = line.find(a_match, pos + 1)
    return False


def get_list(data: dict, key: str, errors: list[str]) -> list:
    raw = data.get(key)
    if raw is None:
        return []
    if not isinstance(raw, list):
        errors.append(f"{key} 必须是数组")
        return []
    return raw


def parse_path_list(data: dict, key: str, default: list[str], allow_empty: bool, errors: list[str]) -> list[str]:
    if key not in data or data.get(key) is None:
        return list(default)
    raw = data.get(key)
    if not isinstance(raw, list):
        errors.append(f"{key} 必须是字符串数组")
        return list(default)
    out = []
    for idx, item in enumerate(raw, 1):
        if not isinstance(item, str) or not is_valid_rel_path(item.strip()):
            errors.append(f"{key}[{idx}] 不是合法相对路径：{item!r}")
        else:
            out.append(item.strip())
    if not allow_empty and not out:
        errors.append(f"{key} 不能为空")
    return out


def validate_wl_meta(obj: dict, where: str, errors: list[str]) -> None:
    if not get_str(obj, "reason"):
        errors.append(f"{where} 缺 reason")
    if not in_set(obj.get("reviewer"), REVIEWERS):
        errors.append(f"{where} reviewer 不在 {sorted(REVIEWERS)}：{obj.get('reviewer')!r}")
    ref = get_str(obj, "review_ref")
    if not ref:
        errors.append(f"{where} 缺 review_ref")
    elif not valid_review_ref(ref):
        errors.append(f"{where} review_ref 需为有效链接 / PR #<N> / review:<id>：{ref!r}")


def check_sha_ref(root: Path, raw: str, label: str, expected: set[str], draft: bool, allow_head_literal: bool, errors: list[str]) -> None:
    if not raw:
        return
    if allow_head_literal and raw == "HEAD":
        if not draft:
            errors.append(f"正式模式禁止 {label} 使用字面 'HEAD'（须为不可变十六进制提交 SHA）")
        return
    if not draft and not is_hex_commit_sha(root, raw):
        errors.append(f"正式模式要求 {label} 为不可变十六进制提交 SHA（禁止符号引用）：{raw!r}")
        return
    try:
        if resolve(root, raw) not in expected:
            errors.append(f"{label} 解析后与目标提交不一致：{raw!r}")
    except RuntimeError:
        errors.append(f"{label} 解析不了：{raw!r}")


def early_fail(msg: str) -> list[str]:
    print(f"红：{msg}")
    return [msg]


def lint(root: Path, manifest_path: Path, base_arg: str, head_arg: str, draft: bool = False, from_disk: bool = False) -> list[str]:
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return early_fail(f"manifest 读不了 / 不是合法 JSON：{exc}")
    if not isinstance(data, dict):
        return early_fail("manifest 顶层必须是 JSON 对象")
    sv = data.get("schema")
    if not isinstance(sv, int) or isinstance(sv, bool) or sv != SCHEMA_VERSION:
        return early_fail(f"manifest.schema 必须为整数 {SCHEMA_VERSION}，实际：{sv!r}（2026-11-26 及以前的 v1 manifest 为历史快照，请按 v2 薄声明编写）")
    try:
        base, head = resolve(root, base_arg), resolve(root, head_arg)
    except RuntimeError as exc:
        return early_fail(f"base/head 解析失败：{exc}")

    errors: list[str] = []
    try:
        manifest_rel: str | None = manifest_path.relative_to(root).as_posix()
    except ValueError:
        manifest_rel = None

    if not draft and not from_disk:
        if not manifest_rel:
            errors.append("正式模式要求 manifest 位于仓库根目录内并已提交到 --head")
        else:
            try:
                if json.loads(read_at(root, head, manifest_rel)) != data:
                    errors.append(f"磁盘 manifest 与 --head({head[:12]}) 提交内 {manifest_rel} 不一致（请先提交或加 --draft）")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"--head 提交中不存在或无法解析 manifest（{manifest_rel}）：{exc}")

    missing = (REQUIRED_TOP - ({"approval"} if draft else set())) - set(data)
    if missing:
        errors.append(f"顶层缺字段：{', '.join(sorted(missing))}")
    for key in ("change", "title", "base", "head", "classification"):
        if not get_str(data, key):
            errors.append(f"{key} 为空或非字符串")
    check_sha_ref(root, get_str(data, "base"), "manifest.base", {base}, draft, False, errors)

    content_head, tail_pinned = head, False
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
                    errors.append(f"manifest.head 必须是 --base 的严格后代提交：{raw_head!r}")
                elif pinned != head:
                    if manifest_rel and is_ancestor(root, pinned, head):
                        tail_diff = diff_no_renames_paths(root, pinned, head) - {manifest_rel}
                        if not tail_diff:
                            content_head, tail_pinned = pinned, True
                        else:
                            errors.append(f"manifest.head 解析后与 --head 不一致：{raw_head!r}（钉扎提交之后存在非 manifest 文件改动：{'、'.join(sorted(tail_diff))}）")
                    else:
                        errors.append(f"manifest.head 解析后与 --head 不一致：{raw_head!r}")

    if not in_set(data.get("classification"), TYPES):
        errors.append(f"classification 不在 {sorted(TYPES)}：{data.get('classification')!r}")

    rule_paths = parse_path_list(data, "rule_paths", DEFAULT_RULE_PATHS, False, errors)
    rule_exclude = parse_path_list(data, "rule_exclude", DEFAULT_RULE_EXCLUDE, True, errors)
    is_rule = lambda p: bool(p) and not (manifest_rel and p == manifest_rel) and any(path_matches(p, rp) for rp in rule_paths) and not any(path_matches(p, ex) for ex in rule_exclude)

    try:
        diff_entries = parse_name_status_z(git(root, "-c", "diff.renames=true", "diff", "--name-status", "-M", "-z", base, content_head))
    except RuntimeError as exc:
        return early_fail(str(exc))

    all_diff_paths = {p for _, op, np in diff_entries for p in (op, np) if p}
    touched_specs_head = {np for _, _, np in diff_entries if np.startswith("docs/specs/")}
    touched_specs_any = {p for p in all_diff_paths if p.startswith("docs/specs/")}

    # ── rules[] 薄声明 + diff 覆盖与反向真实性 ─────────────────────────────
    rules_raw = get_list(data, "rules", errors)
    rules: list[dict] = []
    if not rules_raw and "rules 必须是数组" not in errors:
        errors.append("rules 为空：至少一条规则")
    ids, declared_files = set(), set()
    for i, rule in enumerate(rules_raw, 1):
        w = f"rules[{i}]"
        if not isinstance(rule, dict):
            errors.append(f"{w} 必须是对象")
            continue
        rules.append(rule)
        rid = get_str(rule, "id")
        if not rid:
            errors.append(f"{w} 缺 id")
        elif rid in ids:
            errors.append(f"{w} id 重复：{rid}")
        else:
            ids.add(rid)
        rtype, status = rule.get("type"), rule.get("status")
        if not in_set(rtype, TYPES):
            errors.append(f"{w} type 不在 {sorted(TYPES)}：{rtype!r}")
        if not in_set(rule.get("disposition"), DISPOSITIONS):
            errors.append(f"{w} disposition 不在允许集合：{rule.get('disposition')!r}")
        if rtype == "add" and rule.get("disposition") != "not-applicable":
            errors.append(f"{w} type=add 的 disposition 必须是 not-applicable")
        if not in_set(status, STATUSES):
            errors.append(f"{w} status 不在 {sorted(STATUSES)}：{status!r}")
        elif status == "whitelist":
            validate_wl_meta(rule, w, errors)
        if len(get_str(rule, "summary")) < MIN_SUMMARY:
            errors.append(f"{w} summary 太短（<{MIN_SUMMARY}）")
        files_raw = rule.get("files")
        if not isinstance(files_raw, list) or not files_raw:
            errors.append(f"{w} files 必须是非空字符串数组")
            continue
        for j, fp in enumerate(files_raw, 1):
            if not isinstance(fp, str) or not is_valid_rel_path(fp.strip()):
                errors.append(f"{w}.files[{j}] 不是合法相对路径：{fp!r}")
                continue
            fpath = fp.strip()
            if manifest_rel and fpath == manifest_rel:
                errors.append(f"{w}.files[{j}] 禁止填 manifest 自身：{fpath}")
            elif fpath not in all_diff_paths:
                errors.append(f"{w}.files[{j}] 未出现在 base..head diff 中：{fpath}")
            else:
                declared_files.add(fpath)

    rule_file_count = aux_file_count = 0
    for st, old_p, new_p in diff_entries:
        if manifest_rel and ((st == "D" and old_p == manifest_rel) or (not st.startswith("R") and new_p == manifest_rel)):
            continue
        if st == "D":
            paths_check, hit_rule, label = (old_p,), is_rule(old_p), old_p
        elif st.startswith("R"):
            if manifest_rel and new_p == manifest_rel:
                paths_check, hit_rule, label = (old_p,), is_rule(old_p), f"{old_p} -> {new_p}"
            elif manifest_rel and old_p == manifest_rel:
                paths_check, hit_rule, label = (new_p,), is_rule(new_p), f"{old_p} -> {new_p}"
            else:
                paths_check, hit_rule, label = (old_p, new_p), (is_rule(old_p) or is_rule(new_p)), f"{old_p} -> {new_p}"
        else:
            paths_check, hit_rule, label = (new_p,), is_rule(new_p), new_p
        covered = any(p in declared_files for p in paths_check)
        if hit_rule:
            rule_file_count += 1
            if not covered:
                errors.append(f"未覆盖变更规则文件（{st}）：{label}")
        elif not covered:
            aux_file_count += 1
    if any(r.get("status") == "unresolved" for r in rules):
        errors.append("存在 status=unresolved 的规则")

    # ── scans[] 活跃残留复扫（span 包含 + 唯一覆盖 + 严格 count）────────────
    head_all_files = list_tree(root, content_head)
    head_cache: dict[str, str] = {}
    get_head = lambda p: head_cache.setdefault(p, read_at(root, content_head, p))

    scans_raw = get_list(data, "scans", errors)
    scans: list[dict] = []
    if not scans_raw and "scans 必须是数组" not in errors:
        errors.append("scans 为空：至少一条扫描")
    default_scope = list(dict.fromkeys([*rule_paths, "docs/"]))
    valid_scan_scopes: list[str] = []
    total_allows = 0

    for i, scan in enumerate(scans_raw, 1):
        w = f"scans[{i}]"
        if not isinstance(scan, dict):
            errors.append(f"{w} 必须是对象")
            continue
        scans.append(scan)
        query = get_str(scan, "query")
        if not query:
            errors.append(f"{w} 缺 query")
            continue
        try:
            pattern = re.compile(query)
        except re.error as exc:
            errors.append(f"{w} query 不是合法正则：{exc}")
            continue
        if "scope" in scan and scan.get("scope") is not None:
            sc_raw = scan.get("scope")
            if not isinstance(sc_raw, list) or not sc_raw:
                errors.append(f"{w} scope 必须是非空字符串数组")
                continue
            scope, bad = [], False
            for idx, item in enumerate(sc_raw, 1):
                if not isinstance(item, str) or not is_valid_rel_path(item.strip()):
                    errors.append(f"{w}.scope[{idx}] 不是合法相对路径：{item!r}")
                    bad = True
                else:
                    scope.append(item.strip())
            if bad:
                continue
            explicit_scopes = scope
            if not all(any(scope_covers(s, rp) for s in scope) for rp in rule_paths) and not get_str(scan, "scope_reason"):
                errors.append(f"{w} scope 未覆盖全部 rule_paths 且缺 scope_reason")
        else:
            scope, explicit_scopes = default_scope, []

        valid_scan_scopes.extend(scope)
        files = filter_text_files(head_all_files, scope, manifest_rel, touched_specs_head, explicit_scopes)
        if not files:
            errors.append(f"{w} scope 在 head 中没有可扫描文本文件：{scope}")
            continue
        allow_raw = scan.get("allow") if scan.get("allow") is not None else []
        if not isinstance(allow_raw, list):
            errors.append(f"{w} allow 必须是数组")
            continue
        valid_allows: list[dict] = []
        for j, al in enumerate(allow_raw, 1):
            aw = f"{w}.allow[{j}]"
            if not isinstance(al, dict):
                errors.append(f"{aw} 必须是对象")
                continue
            af, am, ac, ok = get_str(al, "file"), get_str(al, "match"), al.get("count", 1), True
            if not af or af not in files:
                errors.append(f"{aw} file 缺失或不在扫描范围内：{af!r}")
                ok = False
            if len(am) < MIN_MATCH:
                errors.append(f"{aw} match 太短（<{MIN_MATCH}）：{am!r}")
                ok = False
            if not is_pos_int(ac):
                errors.append(f"{aw} count 必须是正整数：{ac!r}")
                ok = False
            validate_wl_meta(al, aw, errors)
            if ok:
                valid_allows.append({"idx": j, "file": af, "match": am, "count": ac})
        total_allows += len(valid_allows)

        counts = [0] * len(valid_allows)
        for rel in files:
            for line_no, line in enumerate(get_head(rel).splitlines(), 1):
                for m in pattern.finditer(line):
                    cov = [idx for idx, al in enumerate(valid_allows) if allow_covers_hit(al["file"], al["match"], rel, line, m.start(), m.end())]
                    if not cov:
                        errors.append(f"{w} 未登记的命中：{rel}:{line_no} {m.group(0)!r}")
                    elif len(cov) > 1:
                        errors.append(f"{w} 多条 allow 重叠覆盖同一命中：{rel}:{line_no} {m.group(0)!r}（allow[{','.join(str(valid_allows[c]['idx']) for c in cov)}]）")
                    else:
                        counts[cov[0]] += 1
        for idx, al in enumerate(valid_allows):
            if counts[idx] != al["count"]:
                msg = "过期无效（0 命中" if counts[idx] == 0 else f"命中次数 {counts[idx]} != 声明"
                errors.append(f"{w}.allow[{al['idx']}] {msg} count={al['count']}：{al['file']} {al['match']!r}")

    # ── 三道自动结构反扫 ──────────────────────────────────────────────────
    corpus_scope = list(dict.fromkeys([*valid_scan_scopes, *rule_paths])) or default_scope
    corpus_files = filter_text_files(head_all_files, corpus_scope, manifest_rel, touched_specs_head, None)
    corpus_texts = {p: get_head(p) for p in corpus_files}

    white_refs: set[str] = set()
    for i, item in enumerate(get_list(data, "section_ref_whitelist", errors), 1):
        w = f"section_ref_whitelist[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{w} 必须是对象")
            continue
        ref = get_str(item, "ref")
        if not ref:
            errors.append(f"{w} 缺 ref")
        else:
            white_refs.add(ref.lstrip("§"))
        validate_wl_meta(item, w, errors)

    defined_head = defined_section_ids(corpus_texts)
    for st, old_p, new_p in diff_entries:
        if st == "D" or new_p not in corpus_texts:
            continue
        added = added_lines_for_entry(root, base, content_head, st, old_p, new_p, corpus_texts[new_p])
        for tok in sorted({t for _, ln in added for t in SECTION_REF_RE.findall(ln)}):
            if tok not in defined_head and tok not in white_refs:
                errors.append(f"章节引用解析不到：{new_p} §{tok}（语料无对应标题；外部引用加 section_ref_whitelist）")

    base_corpus_files = filter_text_files(list_tree(root, base), corpus_scope, manifest_rel, touched_specs_any, None)
    removed_secs = defined_section_ids({p: read_at(root, base, p) for p in base_corpus_files}) - defined_head
    if removed_secs:
        bare_res = {tok: re.compile(rf"(?<![\d.]){re.escape(tok)}(?![\d.])") for tok in removed_secs}
        for path, text in corpus_texts.items():
            check_bare = not path.endswith(".md")
            for no, line in scan_lines(path, text):
                hits = (set(SECTION_REF_RE.findall(line)) & removed_secs) | ({t for t, p in bare_res.items() if p.search(line)} if check_bare else set())
                for tok in sorted(hits - white_refs):
                    errors.append(f"章节已删 / 改号但仍被引用：{path}:{no} §{tok}（同步改引用或加 section_ref_whitelist）")

    path_wl: dict[tuple[str, str], int] = {}
    for i, item in enumerate(get_list(data, "path_ref_whitelist", errors), 1):
        w = f"path_ref_whitelist[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{w} 必须是对象")
            continue
        pf, pp = get_str(item, "file"), get_str(item, "path")
        pf_ok, pp_ok = bool(pf) and is_valid_rel_path(pf), bool(pp) and is_valid_rel_path(pp)
        if not pf_ok:
            errors.append(f"{w} file 不合法：{item.get('file')!r}")
        if not pp_ok:
            errors.append(f"{w} path 不合法：{item.get('path')!r}")
        validate_wl_meta(item, w, errors)
        if pf_ok and pp_ok:
            if (pf, pp) in path_wl:
                errors.append(f"{w} 重复登记：{pf} → {pp}")
            else:
                path_wl[(pf, pp)] = i

    retired_paths = sorted({op for st, op, _ in diff_entries if (st == "D" or st.startswith("R")) and op.endswith(TEXT_SUFFIXES)})
    path_wl_used: set[tuple[str, str]] = set()
    if retired_paths:
        retired_set = set(retired_paths)
        boundary_res = {rp: re.compile(r"(?<![/A-Za-z0-9_.-])" + re.escape(rp) + r"(?![/A-Za-z0-9_.-])") for rp in retired_paths}
        p3_files = sorted(set(corpus_files) | {p for p in head_all_files if ROOT_README_RE.fullmatch(p) and not (manifest_rel and p == manifest_rel)})
        for cur in p3_files:
            for no, line in scan_lines(cur, get_head(cur)):
                found_old = {rp for rp, pat in boundary_res.items() if pat.search(line)}
                found_old |= {t for raw_t in iter_md_link_targets(line) if (t := parse_md_link_target(cur, raw_t)) and t in retired_set}
                for old_p in sorted(found_old):
                    if (cur, old_p) in path_wl:
                        path_wl_used.add((cur, old_p))
                    else:
                        errors.append(f"已删 / 改名路径仍被引用：{cur}:{no} → {old_p}（同步更新或加 path_ref_whitelist）")
    for (wf, wp), idx in sorted(path_wl.items(), key=lambda kv: kv[1]):
        if (wf, wp) not in path_wl_used:
            errors.append(f"path_ref_whitelist[{idx}] 过期无效（未在活跃语料检出引用）：{wf} → {wp}")

    # ── semantic_checks[] / approval / rebuild ─────────────────────────────
    semantic_raw = get_list(data, "semantic_checks", errors)
    semantic: list[dict] = []
    if not semantic_raw and "semantic_checks 必须是数组" not in errors:
        errors.append("semantic_checks 为空：反向冲突至少一条")
    for i, item in enumerate(semantic_raw, 1):
        w = f"semantic_checks[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{w} 必须是对象")
            continue
        semantic.append(item)
        if len(get_str(item, "item")) < MIN_SEMANTIC:
            errors.append(f"{w} item 太短（<{MIN_SEMANTIC}）")
        if not in_set(item.get("conclusion"), CONCLUSIONS) or item.get("conclusion") == "unresolved":
            errors.append(f"{w} conclusion 不合法或为 unresolved：{item.get('conclusion')!r}")
        if len(get_str(item, "evidence")) < MIN_SEMANTIC:
            errors.append(f"{w} evidence 太短（<{MIN_SEMANTIC}）")

    raw_approval = data.get("approval")
    if raw_approval is not None and not isinstance(raw_approval, dict):
        errors.append("approval 必须是对象")
    elif not draft:
        app = raw_approval or {}
        for key in ("user_quote", "timestamp", "scope", "base", "head", "link"):
            if not get_str(app, key):
                errors.append(f"approval 缺 {key}")
        check_sha_ref(root, get_str(app, "base"), "approval.base", {base}, False, False, errors)
        check_sha_ref(root, get_str(app, "head"), "approval.head", {head, content_head}, False, True, errors)
    elif isinstance(raw_approval, dict):
        for k, exp in (("base", {base}), ("head", {head, content_head})):
            v = raw_approval.get(k)
            if v is not None and not isinstance(v, str):
                errors.append(f"approval.{k} 必须是字符串或 null")
            elif isinstance(v, str) and v.strip():
                check_sha_ref(root, v.strip(), f"approval.{k}", exp, True, k == "head", errors)

    rebuild = data.get("rebuild")
    if not isinstance(rebuild, dict):
        errors.append("rebuild 必须是对象")
    elif not isinstance(rebuild.get("triggered"), bool):
        errors.append("rebuild.triggered 必须是布尔")
    elif rebuild.get("triggered"):
        if not get_str(rebuild, "reason"):
            errors.append("rebuild.triggered=true 但缺 reason")
        ob = rebuild.get("old_behaviors")
        if not isinstance(ob, list) or not ob or not all(isinstance(x, str) and x.strip() for x in ob):
            errors.append("rebuild.triggered=true 但 old_behaviors 为空或含非法项")

    by_type = {t: sum(1 for r in rules if r.get("type") == t) for t in sorted(TYPES)}
    by_status = {s: sum(1 for r in rules if r.get("status") == s) for s in sorted(STATUSES)}
    tail_note = f" (content_pinned={content_head[:12]})" if tail_pinned else ""
    modes = (["draft"] if draft else []) + (["from-disk"] if from_disk else [])
    mode_note = f" mode={','.join(modes)}" if modes else ""
    print(
        f"schema={SCHEMA_VERSION} base={base[:12]} head={head[:12]}{tail_note}{mode_note} "
        f"rules={len(rules)} add/replace/retire={by_type['add']}/{by_type['replace']}/{by_type['retire']} "
        f"status done/whitelist/unresolved={by_status['done']}/{by_status['whitelist']}/{by_status['unresolved']} "
        f"rule_files={rule_file_count} aux_files={aux_file_count} scans={len(scans)} allow={total_allows} semantic_checks={len(semantic)}"
    )
    if errors:
        print("违规：\n" + "\n".join(" - " + e for e in errors))
        return errors
    print("绿：manifest 结构与证据检查通过" + ("（仅本地预检，非正式合并门禁）" if (from_disk and not draft) else ""))
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--root", default=".")
    parser.add_argument("--draft", action="store_true", help="开发 / 审核期模式")
    parser.add_argument("--from-disk", action="store_true", help="本地预检 / 单测模式（非正式合并门禁）")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    manifest = (root / args.manifest).resolve()
    if not manifest.exists():
        print(f"红：manifest 不存在：{manifest}")
        return 1
    try:
        return 1 if lint(root, manifest, args.base, args.head, draft=args.draft, from_disk=args.from_disk) else 0
    except Exception as exc:  # noqa: BLE001
        print(f"红：校验异常：{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
