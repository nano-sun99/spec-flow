#!/usr/bin/env python3
"""spec-flow 行为级 Eval 回归 Runner（纯 Python 3.9+ 标准库，CLI 无关）。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib, json, os, re, shlex, shutil, subprocess, sys, tempfile, time
from pathlib import Path
from urllib.parse import unquote

KINDS = {"guardrail", "anti-bloat"}
GIT_MUTATION_TYPES = {"branch_change", "head_change", "ref_change", "new_branch", "deleted_branch", "tag_change", "worktree_change"}
HARD_CHECK_KEYS = {
    "forbid_any_file_write", "forbid_file_writes", "require_file_changes", "require_file_contains",
    "forbid_git_mutations", "require_commands_pass", "forbid_output_patterns", "require_output_any", "require_output_all",
}
IGNORE_SEGMENTS = {".git", "__pycache__", ".pytest_cache"}
STATUS_RANK = {"pass": 5, "hard_pass_pending_rubric": 4, "ungraded": 3, "error": 2, "fail": 1}
ALWAYS_READ_REFS = ("references/00-constitution.md", "references/10-stages.md", "references/15-records.md", "references/20-decisions.md")
CMD_TOKENS = ("workspace", "prompt_file", "skill_dir", "scenario_id")

def read_utf8(p: Path) -> str:
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()

def write_utf8(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)

def load_json(p: Path):
    return json.loads(read_utf8(p))

def dump_json(p: Path, obj: object) -> None:
    write_utf8(p, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

def safe_rel(raw: object) -> str | None:
    if not isinstance(raw, str) or not raw or raw.startswith("/") or "\\" in raw:
        return None
    parts = Path(raw).parts
    return None if (not parts or any(p in ("", ".", "..") for p in parts)) else "/".join(parts)

def run_git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    if check and proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败：{proc.stderr.strip() or proc.stdout.strip()}")
    return proc

def heading_slugs(path: Path) -> set[str]:
    slugs, counts, fence = set(), {}, None
    for line in read_utf8(path).splitlines():
        st = line.lstrip()
        if fence:
            fence = None if st.startswith(fence) else fence
            continue
        if st.startswith(("```", "~~~")):
            fence = st[:3]
            continue
        if m := re.match(r"^#{1,6}\s+(.+?)\s*$", line):
            s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", re.sub(r"`([^`]*)`", r"\1", m.group(1).strip().lower()))
            base = re.sub(r"[^\w\s\u4e00-\u9fff-]", "", s).replace(" ", "-")
            n = counts.get(base, 0)
            counts[base] = n + 1
            slugs.add(base if n == 0 else f"{base}-{n}")
    return slugs

def compute_fingerprint(skill_root: Path) -> dict:
    lines = read_utf8(skill_root / "SKILL.md").splitlines(keepends=True)
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip("\r\n") == "---"), -1) if lines and lines[0].rstrip("\r\n") == "---" else -1
    always_chars = len("".join(lines[end + 1:] if end >= 0 else lines)) + sum(len(read_utf8(skill_root / r)) for r in ALWAYS_READ_REFS)
    active = sorted(["SKILL.md"] + [
        f"{Path(dp).relative_to(skill_root).as_posix()}/{f}"
        for dp, _, fs in os.walk(skill_root / "references")
        if not Path(dp).relative_to(skill_root).as_posix().startswith("references/40-cases")
        for f in fs if f.endswith(".md")
    ])
    hasher, total_chars = hashlib.sha256(), 0
    for rel in active:
        txt = read_utf8(skill_root / rel)
        total_chars += len(txt)
        hasher.update(rel.encode("utf-8") + b"\0" + txt.encode("utf-8") + b"\0")
    rev_p = run_git(skill_root, "rev-parse", "HEAD", check=False)
    rev = rev_p.stdout.strip() if rev_p.returncode == 0 else "unknown"
    if rev != "unknown" and run_git(skill_root, "status", "--porcelain", "--", "SKILL.md", "references/", check=False).stdout.strip():
        rev += "-dirty"
    return {"spec_flow_rev": rev, "rule_tree_sha256": hasher.hexdigest(), "always_read_chars": always_chars, "total_rule_chars": total_chars, "active_rule_file_count": len(active)}

def snapshot_tree(root: Path, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    if not root.is_dir():
        return out
    for dp, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in IGNORE_SEGMENTS)
        for name in sorted(files):
            if name in IGNORE_SEGMENTS or name.endswith(".pyc"):
                continue
            full = Path(dp) / name
            payload = b"symlink:" + os.readlink(full).encode("utf-8") if full.is_symlink() else full.read_bytes()
            rel = full.relative_to(root).as_posix()
            out[f"{prefix}/{rel}" if prefix else rel] = hashlib.sha256(payload).hexdigest()
    return out

def take_snapshot(run_dir: Path) -> dict:
    repo, wt_files = run_dir / "repo", {}
    for p in sorted(run_dir.glob("wt-*")):
        if p.is_dir():
            wt_files.update(snapshot_tree(p, p.name))
    refs = lambda pfx: dict(l.split(" ", 1) for l in run_git(repo, "for-each-ref", "--format=%(refname) %(objectname)", pfx).stdout.splitlines() if l.strip())
    wts, cur_p, cur_b = [], None, "detached"
    for line in run_git(repo, "worktree", "list", "--porcelain").stdout.splitlines() + [""]:
        if line.startswith("worktree "):
            cur_p, cur_b = os.path.realpath(line[9:].strip()), "detached"
        elif line.startswith("branch "):
            cur_b = line[7:].strip()
        elif not line.strip() and cur_p:
            wts.append([cur_p, cur_b])
            cur_p = None
    return {
        "files": snapshot_tree(repo), "worktree_files": wt_files,
        "git": {
            "branch": run_git(repo, "symbolic-ref", "--short", "-q", "HEAD", check=False).stdout.strip(),
            "head": run_git(repo, "rev-parse", "HEAD").stdout.strip(),
            "heads": refs("refs/heads"), "tags": refs("refs/tags"), "worktrees": sorted(wts),
        },
    }

def check_ref(ref: object, skill_root: Path, cache: dict[Path, set[str]]) -> str | None:
    if not isinstance(ref, str) or not ref.strip():
        return "引用必须是非空字符串"
    path_part, anchor = (ref.split("#", 1) + [""])[:2]
    norm = safe_rel(path_part)
    if not norm or not (skill_root / norm).is_file():
        return f"引用文件不存在或路径非法：{ref}"
    if anchor and unquote(anchor) not in cache.setdefault(skill_root / norm, heading_slugs(skill_root / norm)):
        return f"引用锚点不存在：{ref}"
    return None

def load_scenarios(sdir: Path, skill_root: Path) -> tuple[list[tuple[Path, dict]], list[str]]:
    if not sdir.is_dir() or not (files := sorted(sdir.glob("*.json"))):
        return [], [f"场景目录不存在或为空：{sdir}"]
    seen, cache, valid, errs = set(), {}, [], []
    req = ("id", "title", "kind", "rules_ref", "fixture", "user_prompt", "hard_checks", "rubric")
    for p in files:
        e: list[str] = []
        add = lambda cond, msg: None if cond else e.append(f"{p.name}: {msg}")
        try:
            d = load_json(p)
        except Exception as exc:
            errs.append(f"{p.name}: JSON 解析失败：{exc}")
            continue
        if not isinstance(d, dict) or any(k not in d for k in req):
            errs.append(f"{p.name}: 顶层非对象或缺少必填字段 {[k for k in req if not isinstance(d, dict) or k not in d]}")
            continue
        sid = d["id"]
        if isinstance(sid, str) and re.fullmatch(r"[0-9a-zA-Z_-]+", sid):
            add(sid == p.stem, f"文件名 stem ({p.stem}) 与 id ({sid}) 不一致")
            add(sid not in seen, f"id 重复 ({sid})")
            seen.add(sid)
        else:
            e.append(f"{p.name}: id 非法")
        add(d["kind"] in KINDS, f"kind 非法 ({d['kind']})")
        for k in ("title", "user_prompt"):
            add(isinstance(d[k], str) and d[k].strip(), f"{k} 必须是非空字符串")
        add(isinstance(d["rules_ref"], list) and bool(d["rules_ref"]), "rules_ref 必须是非空列表")
        for r in (d["rules_ref"] if isinstance(d["rules_ref"], list) else []):
            if msg := check_ref(r, skill_root, cache):
                e.append(f"{p.name}: rules_ref {msg}")
        if d.get("case_ref") is not None and (msg := check_ref(d["case_ref"], skill_root, cache)):
            e.append(f"{p.name}: case_ref {msg}")
        fx = d["fixture"]
        if isinstance(fx, dict) and isinstance(fx.get("files"), dict):
            for fp, val in fx["files"].items():
                add(safe_rel(fp) and isinstance(val, str), f"fixture.files 非法项 {fp!r}")
            for fp in fx.get("executable_files", []):
                add(safe_rel(fp), f"executable_files 非法路径 {fp!r}")
            gcfg = fx.get("git") or {}
            add(isinstance(gcfg, dict), "fixture.git 必须是对象")
            if isinstance(gcfg, dict):
                for wt in gcfg.get("worktrees", []):
                    wdir = wt.get("dir", "") if isinstance(wt, dict) else ""
                    add(isinstance(wdir, str) and re.fullmatch(r"wt-[0-9a-zA-Z._-]+", wdir), f"worktree dir 须匹配 wt-<name>：{wdir!r}")
                for fp in (gcfg.get("post_commit_files") or {}):
                    add(safe_rel(fp), f"post_commit_files 非法路径 {fp!r}")
        else:
            e.append(f"{p.name}: fixture.files 必须是对象")
        hc = d["hard_checks"]
        if isinstance(hc, dict):
            add(not (set(hc) - HARD_CHECK_KEYS), f"hard_checks 含未知键 {sorted(set(hc) - HARD_CHECK_KEYS)}")
            for mut in hc.get("forbid_git_mutations", []):
                add(mut in GIT_MUTATION_TYPES, f"forbid_git_mutations 非法枚举 {mut!r}")
            for k in ("forbid_output_patterns", "require_output_any", "require_output_all"):
                pats = hc.get(k, [])
                add(isinstance(pats, list), f"{k} 必须是列表")
                for pat in (pats if isinstance(pats, list) else []):
                    try:
                        re.compile(pat)
                    except re.error as exc:
                        e.append(f"{p.name}: {k} 正则无效 {pat!r} ({exc})")
        else:
            e.append(f"{p.name}: hard_checks 必须是对象")
        rb = d["rubric"]
        add(isinstance(rb, dict) and bool(rb.get("must_do")) and bool(rb.get("must_not_do")), "rubric 必须含非空 must_do 与 must_not_do")
        errs.extend(e)
        if not e:
            valid.append((p, d))
    return valid, errs

def select_scenarios(scenarios: list[tuple[Path, dict]], selector: str) -> list[tuple[Path, dict]]:
    if selector == "all":
        return scenarios
    picked, seen = [], set()
    for tok in [t.strip() for t in selector.split(",") if t.strip()]:
        matches = [x for x in scenarios if x[1]["id"] == tok] or [x for x in scenarios if x[1]["id"].startswith(tok)]
        if len(matches) != 1:
            raise ValueError(f"场景选择器 {tok!r} 无匹配或有歧义（命中 {len(matches)} 条）")
        if matches[0][1]["id"] not in seen:
            seen.add(matches[0][1]["id"])
            picked.append(matches[0])
    if not picked:
        raise ValueError("空的场景选择器")
    return picked

def commit_files(repo: Path, files: dict[str, str], execs: set[str], msg: str, allow_empty: bool = True) -> None:
    for rel, content in files.items():
        fp = repo / rel
        write_utf8(fp, content)
        if rel in execs:
            fp.chmod(fp.stat().st_mode | 0o111)
    run_git(repo, "add", "-A")
    run_git(repo, "commit", *(("--allow-empty",) if allow_empty else ()), "-m", msg)

def materialize_scenario(sc: dict, out_root: Path, skill_root: Path, force: bool, sp: Path | None = None) -> Path:
    run_dir = out_root / sc["id"]
    if run_dir.exists():
        if not force:
            raise FileExistsError(f"目标目录已存在（如需覆盖请传 --force）：{run_dir}")
        shutil.rmtree(run_dir)
    repo = run_dir / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    fx, gcfg = sc["fixture"], (sc["fixture"].get("git") or {})
    default_br, execs = gcfg.get("default_branch", "main"), set(fx.get("executable_files", []))
    run_git(repo, "init", "-b", default_br)
    for k, v in (("user.name", "Eval Fixture"), ("user.email", "eval@example.invalid"), ("commit.gpgsign", "false")):
        run_git(repo, "config", k, v)
    commit_files(repo, fx.get("files", {}), execs, "Initial fixture", allow_empty=not fx.get("files"))
    for cm in gcfg.get("initial_commits", []):
        commit_files(repo, cm.get("files", {}), execs, cm.get("message", "Fixture commit"))
    for br in gcfg.get("extra_branches", []):
        run_git(repo, "checkout", "-b", br["name"], br.get("from", default_br))
        for cm in br.get("commits", []):
            commit_files(repo, cm.get("files", {}), execs, cm.get("message", "Branch commit"))
        run_git(repo, "checkout", default_br)
    for tag in gcfg.get("tags", []):
        ref = tag.get("ref", "HEAD")
        run_git(repo, *(("tag", "-a", tag["name"], "-m", tag.get("message", tag["name"]), ref) if tag.get("annotated") else ("tag", tag["name"], ref)))
    for wt in gcfg.get("worktrees", []):
        has_br = run_git(repo, "show-ref", "--verify", "--quiet", f"refs/heads/{wt['branch']}", check=False).returncode == 0
        run_git(repo, "worktree", "add", *((str(run_dir / wt["dir"]), wt["branch"]) if has_br else ("-b", wt["branch"], str(run_dir / wt["dir"]))))
    if gcfg.get("local_origin"):
        origin = run_dir / "origin.git"
        run_git(run_dir, "init", "--bare", str(origin))
        run_git(repo, "remote", "add", "origin", str(origin))
        run_git(repo, "push", "--all", "origin")
        run_git(repo, "push", "--tags", "origin")
        run_git(repo, "fetch", "origin")
    for rel, content in (gcfg.get("post_commit_files") or {}).items():
        fp = repo / rel
        write_utf8(fp, content)
        if rel in execs:
            fp.chmod(fp.stat().st_mode | 0o111)
    write_utf8(run_dir / "prompt.txt", f"请先阅读并严格遵守 spec-flow 规则真身：{(skill_root / 'SKILL.md').resolve()}\n当前任务工作区：{repo.resolve()}\n\n用户请求：\n{sc['user_prompt']}\n")
    dump_json(run_dir / "snapshot.before.json", take_snapshot(run_dir))
    dump_json(run_dir / "meta.json", {
        "scenario_id": sc["id"], "scenario_path": str(sp.resolve()) if sp else None, "scenario": sc,
        "skill_root": str(skill_root.resolve()), "workspace": str(repo.resolve()),
        "prompt_file": str((run_dir / "prompt.txt").resolve()), "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return run_dir

def validate_rubric(obj: object, label: str) -> dict:
    if not isinstance(obj, dict) or not isinstance(obj.get("pass"), bool):
        raise ValueError(f"Rubric 格式无效（{label}）：必须含布尔字段 pass")
    return obj

def grade_one(run_dir: Path, out_ov: Path | None, rubric: dict | None) -> dict:
    meta, before = load_json(run_dir / "meta.json"), load_json(run_dir / "snapshot.before.json")
    sc, hc, repo, after, viols = meta["scenario"], meta["scenario"]["hard_checks"], run_dir / "repo", take_snapshot(run_dir), []
    exec_info = load_json(run_dir / "exec.json") if (run_dir / "exec.json").is_file() else None
    timed_out, exec_rc = bool(exec_info and exec_info.get("timed_out")), (exec_info.get("returncode") if exec_info else None)
    exec_err = bool(exec_info and (timed_out or exec_rc != 0))
    bf, af, bw, aw = before["files"], after["files"], before.get("worktree_files", {}), after.get("worktree_files", {})
    repo_chg = sorted(k for k in set(bf) | set(af) if bf.get(k) != af.get(k))
    wt_chg = sorted(k for k in set(bw) | set(aw) if bw.get(k) != aw.get(k))
    all_chg = repo_chg + wt_chg
    if hc.get("forbid_any_file_write") and all_chg:
        viols.append(f"forbid_any_file_write: 检测到文件变动 {all_chg}")
    for p in hc.get("forbid_file_writes", []):
        if hits := [k for k in repo_chg if k == p] + [k for k in wt_chg if k == p or k.endswith(f"/{p}")]:
            viols.append(f"forbid_file_writes: 禁止修改的路径被改 {hits}")
    bg, ag = before["git"], after["git"]
    muts = {
        "branch_change": bg["branch"] != ag["branch"], "head_change": bg["head"] != ag["head"],
        "ref_change": bg["heads"] != ag["heads"], "new_branch": bool(set(ag["heads"]) - set(bg["heads"])),
        "deleted_branch": bool(set(bg["heads"]) - set(ag["heads"])), "tag_change": bg["tags"] != ag["tags"],
        "worktree_change": bg["worktrees"] != ag["worktrees"],
    }
    viols.extend(f"forbid_git_mutations: 触发 {m}" for m in hc.get("forbid_git_mutations", []) if muts[m])
    out_p = out_ov or (run_dir / "stdout.txt")
    need_out = bool(hc.get("forbid_output_patterns") or hc.get("require_output_any") or hc.get("require_output_all"))
    missing_out = need_out and not out_p.is_file()
    out_txt = out_p.read_text(encoding="utf-8", errors="replace") if out_p.is_file() else None
    if out_txt is not None:
        viols.extend(f"forbid_output_patterns: 命中禁用模式 {pat!r}" for pat in hc.get("forbid_output_patterns", []) if re.search(pat, out_txt, re.M))
    if not exec_err:
        viols.extend(f"require_file_changes: 目标文件未修改 {p}" for p in hc.get("require_file_changes", []) if p not in repo_chg)
        for p, needles in (hc.get("require_file_contains") or {}).items():
            if not (repo / p).is_file():
                viols.append(f"require_file_contains: 文件缺失 {p}")
            else:
                txt = (repo / p).read_text(encoding="utf-8", errors="replace")
                viols.extend(f"require_file_contains: {p} 缺少 {nd!r}" for nd in ([needles] if isinstance(needles, str) else needles) if nd not in txt)
        for cmd in hc.get("require_commands_pass", []):
            if (proc := subprocess.run(cmd, cwd=repo, shell=True, text=True, capture_output=True, timeout=60)).returncode != 0:
                viols.append(f"require_commands_pass: `{cmd}` 退出码 {proc.returncode}")
        if out_txt is not None:
            if (req_any := hc.get("require_output_any", [])) and not any(re.search(pat, out_txt, re.M) for pat in req_any):
                viols.append(f"require_output_any: 未命中任一模式 {req_any}")
            viols.extend(f"require_output_all: 缺少必需模式 {pat!r}" for pat in hc.get("require_output_all", []) if not re.search(pat, out_txt, re.M))
    if rubric is None and (run_dir / "rubric.json").is_file():
        rubric = validate_rubric(load_json(run_dir / "rubric.json"), sc["id"])
    rb_st = "pending" if rubric is None else ("pass" if rubric["pass"] else "fail")
    hard_st = "fail" if viols else ("error" if exec_err else ("ungraded" if missing_out else "pass"))
    status = "fail" if (viols or rb_st == "fail") else ("error" if exec_err else ("ungraded" if missing_out else ("hard_pass_pending_rubric" if rb_st == "pending" else "pass")))
    return {
        "id": sc["id"], "title": sc["title"], "kind": sc["kind"], "status": status, "hard_status": hard_st,
        "rubric_status": rb_st, "hard_violations": viols, "changed_files": all_chg, "missing_output": missing_out,
        "exec_error": exec_err, "timed_out": timed_out, "exec_returncode": exec_rc, "rubric": rubric,
    }

def compare_baseline(results: list[dict], fp: dict, bpath: Path) -> dict:
    if not bpath.is_file():
        raise ValueError(f"Baseline 文件不存在：{bpath}")
    base = load_json(bpath)
    if not isinstance(base, dict) or not isinstance(base.get("results"), list) or not isinstance(base.get("fingerprint"), dict):
        raise ValueError(f"Baseline 格式无效：{bpath}")
    old = {r["id"]: r["status"] for r in base["results"] if isinstance(r, dict) and "id" in r and r.get("status") in STATUS_RANK}
    if len(old) != len(base["results"]):
        raise ValueError(f"Baseline results 含非法条目：{bpath}")
    cur, regs, imps, unch = {r["id"]: r["status"] for r in results}, [], [], []
    for sid in sorted(set(old) & set(cur)):
        o, c = old[sid], cur[sid]
        (regs if STATUS_RANK[c] < STATUS_RANK[o] else (imps if STATUS_RANK[c] > STATUS_RANK[o] else unch)).append({"id": sid, "before": o, "after": c})
    bfp = base["fingerprint"]
    return {
        "baseline_file": str(bpath), "baseline_rev": bfp.get("spec_flow_rev"),
        "always_read_chars_delta": fp["always_read_chars"] - int(bfp["always_read_chars"]),
        "total_rule_chars_delta": fp["total_rule_chars"] - int(bfp["total_rule_chars"]),
        "regressions": regs, "improvements": imps, "unchanged": unch,
        "added": sorted(set(cur) - set(old)), "removed": sorted(set(old) - set(cur)),
    }

def render_markdown(rep: dict) -> str:
    fp, sm = rep["fingerprint"], rep["summary"]
    lines = [
        "# spec-flow 行为级 Eval 报告", "", f"- 生成时间：{rep['generated_at']}", f"- 执行环境：{rep['execution_env']}",
        f"- `spec_flow_rev`：`{fp['spec_flow_rev']}`", f"- `rule_tree_sha256`：`{fp['rule_tree_sha256']}`",
        f"- 必读核字数（`always_read_chars`）：`{fp['always_read_chars']:,}`",
        f"- 现行规则总字数（`total_rule_chars`）：`{fp['total_rule_chars']:,}`（{fp['active_rule_file_count']} 份文件）",
        f"- 汇总：总计 `{sm['total']}` ｜ `pass={sm['pass']}` ｜ `hard_pass_pending_rubric={sm['hard_pass_pending_rubric']}` ｜ `ungraded={sm['ungraded']}` ｜ `error={sm['error']}` ｜ `fail={sm['fail']}`",
        "", "## 逐场景结果", "", "| ID | 类型 | 总状态 | 硬断言 | Rubric | 备注 / 违规 |", "|---|---|---|---|---|---|",
    ]
    for r in rep["results"]:
        note = "；".join(r["hard_violations"]) if r["hard_violations"] else ((r["rubric"] or {}).get("notes") or ("超时/非0退出" if r["exec_error"] else ("缺输出" if r["missing_output"] else "—")))
        lines.append(f"| `{r['id']}` | `{r['kind']}` | `{r['status']}` | `{r['hard_status']}` | `{r['rubric_status']}` | {note.replace('|', '/')} |")
    if b := rep.get("baseline_diff"):
        lines += [
            "", "## Baseline 对比", "", f"- 对比基线：`{b['baseline_file']}`（`{b['baseline_rev']}`）",
            f"- `always_read_chars_delta`：`{b['always_read_chars_delta']:+d}`；`total_rule_chars_delta`：`{b['total_rule_chars_delta']:+d}`",
            f"- 退化：`{len(b['regressions'])}` ｜ 改善：`{len(b['improvements'])}` ｜ 不变：`{len(b['unchanged'])}` ｜ 新增：`{len(b['added'])}` ｜ 缺跑：`{len(b['removed'])}`",
        ] + [f"  - 退化：`{x['id']}`（`{x['before']}` → `{x['after']}`）" for x in b["regressions"]]
    return "\n".join(lines) + "\n"

def run_grade(args: argparse.Namespace, target: Path, skill_root: Path) -> int:
    if not target.is_dir():
        return print(f"[错误] 评分目标目录不存在：{target}", file=sys.stderr) or 1
    single = (target / "snapshot.before.json").is_file()
    if not single and args.output_file:
        return print("[错误] 批量目录模式不支持 --output-file", file=sys.stderr) or 1
    run_dirs = [target] if single else sorted(p for p in target.iterdir() if p.is_dir() and (p / "snapshot.before.json").is_file())
    if not run_dirs:
        return print(f"[错误] 未找到含 snapshot.before.json 的场景：{target}", file=sys.stderr) or 1
    try:
        meta_ids = {d: load_json(d / "meta.json")["scenario_id"] for d in run_dirs}
        rb_map: dict[str, dict] = {}
        if args.rubric_file:
            rp = Path(args.rubric_file)
            if not rp.is_file() or not isinstance(raw_rb := load_json(rp), dict):
                raise ValueError(f"Rubric 文件缺失或顶层非对象：{rp}")
            rb_map = {meta_ids[run_dirs[0]]: validate_rubric(raw_rb, meta_ids[run_dirs[0]])} if (single and isinstance(raw_rb.get("pass"), bool)) else {k: validate_rubric(v, k) for k, v in raw_rb.items()}
        out_ov = Path(args.output_file) if args.output_file else None
        results = [grade_one(d, out_ov, rb_map.get(meta_ids[d])) for d in run_dirs]
        fp = compute_fingerprint(skill_root)
        bdiff = compare_baseline(results, fp, Path(args.baseline)) if args.baseline else None
    except Exception as exc:
        return print(f"[错误] 评分失败：{exc}", file=sys.stderr) or 1
    counts = {k: sum(1 for r in results if r["status"] == k) for k in STATUS_RANK}
    rep = {"generated_at": datetime.now(timezone.utc).isoformat(), "execution_env": args.execution_env, "mode": "single" if single else "batch", "fingerprint": fp, "summary": {"total": len(results), **counts}, "results": results, "baseline_diff": bdiff}
    rdir = Path(args.report_out) if args.report_out else target
    dump_json(rdir / "report.json", rep)
    write_utf8(rdir / "report.md", render_markdown(rep))
    print(f"报告已写入：{rdir / 'report.json'} 与 {rdir / 'report.md'}")
    print(f"结果：total={len(results)} pass={counts['pass']} pending={counts['hard_pass_pending_rubric']} ungraded={counts['ungraded']} error={counts['error']} fail={counts['fail']}")
    if counts["fail"] > 0 or (bdiff and bdiff["regressions"]):
        return 1
    return 2 if (counts["error"] > 0 or counts["ungraded"] > 0 or (not args.hard_only and counts["hard_pass_pending_rubric"] > 0)) else 0

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="spec-flow 行为级 Eval 回归 Runner")
    grp = ap.add_mutually_exclusive_group(required=True)
    for f, kw in (("--validate", {"action": "store_true"}), ("--materialize", {"metavar": "ID|PREFIX|all"}), ("--grade", {"metavar": "PATH"}), ("--run", {"action": "store_true"})):
        grp.add_argument(f, **kw)
    for f, kw in (
        ("--skill-root", {"default": "."}), ("--scenarios-dir", {"default": None}), ("--out", {"default": None}),
        ("--force", {"action": "store_true"}), ("--output-file", {"default": None}), ("--rubric-file", {"default": None}),
        ("--baseline", {"default": None}), ("--report-out", {"default": None}), ("--hard-only", {"action": "store_true"}),
        ("--cmd", {"default": None}), ("--scenarios", {"default": "all"}), ("--timeout", {"type": int, "default": 180}),
        ("--execution-env", {"default": "self-test (local runner, non-independent)"}),
    ):
        ap.add_argument(f, **kw)
    args = ap.parse_args(argv)
    skill_root = Path(args.skill_root).resolve()
    sdir = Path(args.scenarios_dir) if args.scenarios_dir else (skill_root / "evals" / "scenarios")
    if args.grade:
        return run_grade(args, Path(args.grade), skill_root)
    scenarios, errs = load_scenarios(sdir, skill_root)
    if args.validate and not errs:
        with tempfile.TemporaryDirectory(prefix="spec-flow-eval-validate-") as td:
            for sp, sc in scenarios:
                try:
                    materialize_scenario(sc, Path(td), skill_root, True, sp)
                except Exception as exc:
                    errs.append(f"{sp.name}: 临时物化失败：{exc}")
    if errs:
        return [print(f"[红] {e}", file=sys.stderr) for e in errs] and 1 or 1
    if args.validate:
        return print(f"[绿] 校验通过：{len(scenarios)} 条场景 schema、链接/锚点与临时物化均正常") or 0
    try:
        if args.materialize:
            if not args.out:
                raise ValueError("--materialize 必须提供 --out <dir>")
            for sp, sc in select_scenarios(scenarios, args.materialize):
                print(f"[物化] {sc['id']} -> {materialize_scenario(sc, Path(args.out), skill_root, args.force, sp)}")
            return 0
        if not args.cmd:
            raise ValueError("--run 必须提供 --cmd '<template>'")
        picked = select_scenarios(scenarios, args.scenarios)
        out_root = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix=f"spec-flow-eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}-"))
        out_root.mkdir(parents=True, exist_ok=True)
        print(f"[运行目录] {out_root}")
        for sp, sc in picked:
            run_dir = materialize_scenario(sc, out_root, skill_root, args.force, sp)
            tokens = {"workspace": str((run_dir / "repo").resolve()), "prompt_file": str((run_dir / "prompt.txt").resolve()), "skill_dir": str(skill_root), "scenario_id": sc["id"]}
            rendered = args.cmd
            for k in CMD_TOKENS:
                rendered = rendered.replace("{" + k + "}", shlex.quote(tokens[k]))
            env = {**os.environ, **{f"EVAL_{k.upper()}": v for k, v in tokens.items()}}
            t0, timed_out, rc = time.monotonic(), False, None
            try:
                proc = subprocess.run(rendered, cwd=run_dir / "repo", shell=True, text=True, capture_output=True, timeout=args.timeout, env=env)
                stdout, stderr, rc = proc.stdout, proc.stderr, proc.returncode
            except subprocess.TimeoutExpired as exc:
                timed_out = True
                stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            write_utf8(run_dir / "stdout.txt", stdout)
            write_utf8(run_dir / "stderr.txt", stderr)
            dump_json(run_dir / "exec.json", {"cmd": rendered, "returncode": rc, "timed_out": timed_out, "duration_sec": round(time.monotonic() - t0, 3)})
    except Exception as exc:
        return print(f"[错误] {exc}", file=sys.stderr) or 1
    return run_grade(args, out_root, skill_root)

if __name__ == "__main__":
    sys.exit(main())
