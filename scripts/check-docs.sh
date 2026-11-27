#!/usr/bin/env bash
# spec-flow 文档检查入口（单轨现行体系）：
# 1. SKILL.md frontmatter、字数/行数/警示符预算；
# 2. 核心层（L0–L2、两份专项总纲）字数与行数预算，以及现行规则正文单行可见字数上限；
# 3. 相对链接与精确 GitHub #锚点可达性（拒绝对路径、不二次清洗锚点）；禁止现行规则外链 docs/archive；
# 4. 核心 owner 章节、5 个选修模块与全目录孤儿文件检查（含 40-cases/INDEX.md）；
# 5. README.md / README.zh-CN.md 双语节标记（含重复拦截）与 references 提及同步。
# 每项一行结果，末行「绿 / 红」；退出码 0 = 绿，1 = 红。

set -euo pipefail

CDPATH= cd -- "$(dirname -- "$0")/.." || { echo "[红] 进不了仓根目录"; echo "红"; exit 1; }

if ! command -v python3 >/dev/null 2>&1; then
  echo "[红] 找不到 python3，检查跑不起来"
  echo "红"
  exit 1
fi

PYTHONIOENCODING=utf-8 python3 - <<'PY'
import json, os, re, sys
from urllib.parse import unquote

red = False

def report(ok: bool, msg: str) -> None:
    global red
    red = red or not ok
    print(("[绿] " if ok else "[红] ") + msg)

def unfenced(text: str) -> list[str]:
    out, fence = [], None
    for line in text.splitlines():
        st = line.lstrip()
        if fence:
            if st.startswith(fence):
                fence = None
            continue
        if st.startswith("```") or st.startswith("~~~"):
            fence = st[:3]
            out.append("")
            continue
        out.append(line)
    return out

def visible_len(line: str) -> int:
    return len(re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line))

def github_slug(heading: str) -> str:
    # 对齐 GitHub github-slugger：转小写、去内联代码/链接语法、去标点（保留字母/数字/汉字/空格/连字符）、
    # 每个空格逐一替换为 '-'（不折叠连续空格，保持与 GitHub 渲染一致）。
    s = heading.strip().lower()
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"[^\w\s\u4e00-\u9fff-]", "", s)
    s = s.replace(" ", "-")
    return s

def heading_slugs(path: str) -> set[str]:
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    text = open(path, encoding="utf-8", newline="").read()
    for line in unfenced(text):
        m = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if not m:
            continue
        base = github_slug(m.group(1))
        n = counts.get(base, 0)
        counts[base] = n + 1
        slugs.add(base if n == 0 else f"{base}-{n}")
    return slugs

def exists_exact(path: str) -> bool:
    if not path or path.startswith("/"):
        return False
    norm = os.path.normpath(path)
    if norm.startswith("/") or norm.startswith(".."):
        return False
    if norm == ".":
        return False
    cur = "."
    for part in norm.split("/"):
        if not os.path.isdir(cur) or part not in os.listdir(cur):
            return False
        cur = os.path.join(cur, part)
    return os.path.exists(cur)

try:
    # ── 1. SKILL.md frontmatter 与预算 ───────────────────────────────────
    skill_text = open("SKILL.md", encoding="utf-8", newline="").read()
    lines = skill_text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise ValueError("SKILL.md 开头没有 frontmatter")
    end = None
    for i in range(1, len(lines)):
        s = lines[i].rstrip("\r\n")
        if s == "---":
            end = i
            break
        if not (s.strip() == "" or re.match(r"[A-Za-z0-9_-]+\s*:", s) or s[:1] in " \t"):
            break
    if end is None:
        raise ValueError("SKILL.md frontmatter 缺少结束行 ---")
    front = "".join(lines[:end + 1])
    body = "".join(lines[end + 1:])
    meta = {}
    for line in lines[1:end]:
        m = re.fullmatch(r"(name|description): ([^\r\n]+)[\r\n]*", line)
        if not m or m.group(1) in meta:
            raise ValueError("frontmatter 仅允许不重复的 name 与单行 description")
        meta[m.group(1)] = m.group(2)
    if meta.get("name") != "spec-flow":
        raise ValueError("frontmatter name 必须为 spec-flow")
    desc = json.loads(meta.get("description", ""))
    if not isinstance(desc, str) or not desc.strip() or "\n" in desc or "\r" in desc:
        raise ValueError("frontmatter description 必须为非空单行字符串")

    report(len(front) <= 500, f"SKILL.md frontmatter {len(front)} / 500 字")
    report(len(body) <= 2600 and len(lines) <= 60,
           f"SKILL.md 正文 {len(body):,} / 2,600 字，{len(lines)} / 60 行")
    alerts = body.count("⚠") + body.count("⛔")
    report(alerts <= 3, f"SKILL.md 警示符 {alerts} / 3")

    # ── 2. 核心层预算、必读核 / 全仓现行规则硬上限与单行长度上限 ────────────
    CORE_BUDGETS = {
        "references/00-constitution.md": (62, 2800),
        "references/10-stages.md": (95, 4200),
        "references/15-records.md": (95, 3800),
        "references/20-decisions.md": (85, 3400),
        "references/25-spec-governance.md": (100, 4500),
        "references/26-review-contract.md": (110, 4800),
    }
    ALWAYS_READ_MAX = 15500
    TOTAL_RULE_MAX = 46000
    budget_err = []
    always_read_chars = len(body)
    for path, (max_l, max_c) in CORE_BUDGETS.items():
        if not exists_exact(path):
            budget_err.append(f"缺失 {path}")
            continue
        t = open(path, encoding="utf-8", newline="").read()
        lc, cc = len(t.splitlines()), len(t)
        if path in ("references/00-constitution.md", "references/10-stages.md",
                    "references/15-records.md", "references/20-decisions.md"):
            always_read_chars += cc
        if lc > max_l or cc > max_c:
            budget_err.append(f"{path}({lc}/{max_l}行, {cc}/{max_c}字)")
    report(not budget_err,
           "核心层单文件预算全部达标"
           if not budget_err else "核心层超预算：" + "；".join(budget_err))
    report(always_read_chars <= ALWAYS_READ_MAX,
           f"必读核字数（SKILL正文+L0-L2）{always_read_chars:,} / {ALWAYS_READ_MAX:,} 字")

    MAX_VISIBLE_LINE = 220
    active_rule_files = ["SKILL.md"] + sorted(
        os.path.join(dp, f)
        for dp, _, fs in os.walk("references")
        for f in fs
        if f.endswith(".md") and not dp.startswith("references/40-cases")
    )
    total_rule_chars = sum(
        len(open(path, encoding="utf-8", newline="").read())
        for path in active_rule_files
    )
    report(total_rule_chars <= TOTAL_RULE_MAX,
           f"全仓现行规则总字数 {total_rule_chars:,} / {TOTAL_RULE_MAX:,} 字（覆盖 {len(active_rule_files)} 份文件）")
    long_lines = []
    for path in active_rule_files:
        raw_lines = open(path, encoding="utf-8", newline="").read().splitlines()
        start_idx = 0
        if path == "SKILL.md" and raw_lines and raw_lines[0].strip() == "---":
            for j in range(1, len(raw_lines)):
                if raw_lines[j].strip() == "---":
                    start_idx = j + 1
                    break
        for i in range(start_idx, len(raw_lines)):
            vlen = visible_len(raw_lines[i])
            if vlen > MAX_VISIBLE_LINE:
                long_lines.append(f"{path}:{i + 1}({vlen}字)")
    report(not long_lines,
           f"现行规则正文单行可见字数均 ≤ {MAX_VISIBLE_LINE}（覆盖 {len(active_rule_files)} 份文件）"
           if not long_lines else "单行超长：" + "、".join(long_lines[:10]))

    # ── 3. 相对链接、精确 GitHub #锚点可达性与零归档外链 ─────────────────
    extra_docs = [p for p in ("AGENTS.md", "docs/changes/README.md", "docs/archive/v1/README.md") if os.path.isfile(p)]
    all_check_files = ["SKILL.md", "README.md", "README.zh-CN.md"] + extra_docs + sorted(
        os.path.join(dp, f)
        for dp, _, fs in os.walk("references")
        for f in fs
        if f.endswith(".md")
    )
    slug_cache: dict[str, set[str]] = {}
    link_err, archive_err = [], []
    for rel in all_check_files:
        if not os.path.isfile(rel):
            continue
        text = "\n".join(unfenced(open(rel, encoding="utf-8", newline="").read()))
        for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", text):
            raw = m.group(1)
            if raw.startswith(("http://", "https://", "mailto:")):
                continue
            target_part, anchor = (raw.split("#", 1) + [""])[:2]
            if target_part.startswith("/"):
                link_err.append(f"{rel} → {raw}（禁止以 / 开头绝对路径）")
                continue
            if not target_part:
                target_path = rel
            else:
                target_path = os.path.normpath(os.path.join(os.path.dirname(rel), target_part))
            if not exists_exact(target_path):
                link_err.append(f"{rel} → {raw}")
                continue
            if rel in active_rule_files and (target_path == "docs/archive" or target_path.startswith("docs/archive/")):
                archive_err.append(f"{rel} → {target_path}")
            if anchor and os.path.isfile(target_path) and target_path.endswith(".md"):
                if target_path not in slug_cache:
                    slug_cache[target_path] = heading_slugs(target_path)
                decoded_anchor = unquote(anchor)
                if decoded_anchor not in slug_cache[target_path]:
                    link_err.append(f"{rel} → {raw}（锚点不存在）")
    report(not link_err, f"全部相对链接与精确 #锚点可达（核查 {len(all_check_files)} 份文件）"
           if not link_err else "断链 / 坏锚点：" + "、".join(link_err))
    report(not archive_err, "现行规则无指向 docs/archive 的遗留依赖"
           if not archive_err else "仍依赖归档文件：" + "、".join(archive_err))

    # ── 4. 核心 owner 章节、5 选修与全目录孤儿文件 ────────────────────────
    owner_err = []
    checks = {
        "references/00-constitution.md": [f"## L0-{i} " for i in range(1, 9)],
        "references/10-stages.md": ["### 澄清", "### 设计", "### 交付", "### 发布"],
        "references/15-records.md": ["获批依据", "预期交付", "全部实际来源", "必要依赖", "就绪证据", "候选结果", "替换式变更载体处置表"],
        "references/20-decisions.md": [f"## D{i} " for i in range(0, 8)] + ["## 交互卡片契约"],
        "references/25-spec-governance.md": ["唯一权威顺序", "决定 owner 对账"],
        "references/26-review-contract.md": ["文档检查", "Lane A", "Lane B"],
        "references/50-adapters/README.md": ["`adr`", "`doc-lifecycle`", "`issue-status`", "`issue-type`", "`release`"],
    }
    for path, tokens in checks.items():
        if not exists_exact(path):
            owner_err.append(f"缺失核心文件 {path}")
            continue
        body_txt = open(path, encoding="utf-8", newline="").read()
        for tok in tokens:
            if tok not in body_txt:
                owner_err.append(f"{path} 缺「{tok}」")
    # 全目录孤儿检查（os.walk）：40-cases/ 须登记在 40-cases/INDEX.md；过渡页显式白名单；其余全部须由 SKILL.md 链接。
    TRANSITION_STUBS = {"references/v2/SKILL.md"}
    skill_links = set(re.findall(r"\]\((references/[^)#\s]+\.md)(?:#[^)\s]*)?\)", "\n".join(unfenced(skill_text))))
    all_ref_mds = sorted(
        os.path.join(dp, f)
        for dp, _, fs in os.walk("references")
        for f in fs
        if f.endswith(".md")
    )
    case_mds = [p for p in all_ref_mds if p.startswith("references/40-cases/") and p != "references/40-cases/INDEX.md"]
    nav_targets = [
        p for p in all_ref_mds
        if p not in TRANSITION_STUBS and not p.startswith("references/40-cases/")
    ] + (["references/40-cases/INDEX.md"] if exists_exact("references/40-cases/INDEX.md") else [])
    orphans = [p for p in nav_targets if p not in skill_links]
    if orphans:
        owner_err.append("SKILL.md 未链接：" + "、".join(orphans))
    if not exists_exact("references/40-cases/INDEX.md"):
        owner_err.append("缺失 references/40-cases/INDEX.md")
    else:
        idx_text = "\n".join(unfenced(open("references/40-cases/INDEX.md", encoding="utf-8", newline="").read()))
        idx_links = set(re.findall(r"\]\(([^)#\s]+\.md)(?:#[^)\s]*)?\)", idx_text))
        orphan_cases = [os.path.basename(p) for p in case_mds if os.path.basename(p) not in idx_links]
        if orphan_cases:
            owner_err.append("40-cases/INDEX.md 未登记：" + "、".join(orphan_cases))
    report(not owner_err, f"核心 owner 章节、5 选修、{len(nav_targets)} 份导航与 {len(case_mds)} 份案例索引齐全"
           if not owner_err else "结构缺失：" + "；".join(owner_err))

    # ── 5. 双语 README 同步 ──────────────────────────────────────────────
    def sections(text: str):
        out, fence, pending, pend_line = [], None, None, 0
        for i, line in enumerate(text.splitlines(), 1):
            st = line.lstrip()
            if fence:
                if st.startswith(fence):
                    fence = None
                continue
            if st.startswith("```") or st.startswith("~~~"):
                fence = st[:3]
                continue
            m = re.fullmatch(r"<!--\s*s:([a-z0-9-]+)\s*-->", line.strip())
            if m:
                if pending is not None:
                    out.append((pending, None, pend_line))
                pending, pend_line = m.group(1), i
                continue
            if re.match(r"##\s+\S", line):
                out.append((pending, line, i))
                pending = None
            elif st:
                if pending is not None:
                    out.append((pending, None, pend_line))
                    pending = None
        if pending is not None:
            out.append((pending, None, pend_line))
        return out

    readmes = {n: open(n, encoding="utf-8", newline="").read() for n in ("README.md", "README.zh-CN.md")}
    secs = {n: sections(t) for n, t in readmes.items()}
    ma = [m or "（无标记）" for m, _, _ in secs["README.md"]]
    mb = [m or "（无标记）" for m, _, _ in secs["README.zh-CN.md"]]
    diff = []
    for name, arr in (("README.md", ma), ("README.zh-CN.md", mb)):
        dups = sorted({x for x in arr if x != "（无标记）" and arr.count(x) > 1})
        if dups:
            diff.append(f"{name} 节标记重复：" + "、".join(dups))
    if [x for x in ma if x not in mb]:
        diff.append("仅 README.md 有：" + "、".join(x for x in ma if x not in mb))
    if [x for x in mb if x not in ma]:
        diff.append("仅 README.zh-CN.md 有：" + "、".join(x for x in mb if x not in ma))
    if not diff and ma != mb:
        diff.append("顺序不一致")
    report(not diff, f"双语 README 节标记 {len(ma)} / {len(mb)} 一一对应且无重复"
           if not diff else "双语节标记不一致：" + "；".join(diff))

    loose = [f"{n}:{ln} 标记 s:{m} 未贴 ## 标题" for n in secs for m, h, ln in secs[n] if m and not h]
    loose += [f"{n}:{ln} 标题「{h.strip()}」无标记" for n in secs for m, h, ln in secs[n] if h and not m]
    report(not loose, "每个节标记均贴着 ## 标题" if not loose else "；".join(loose))

    top_refs = sorted(
        [f"references/{f}" for f in os.listdir("references") if f.endswith(".md")]
        + ["references/30-playbooks/", "references/40-cases/", "references/50-adapters/"]
    )
    unlisted = [p for p in top_refs if not all(p in readmes[n] for n in readmes)]
    report(not unlisted, f"双语 README 均点到全部 {len(top_refs)} 项核心参考入口"
           if not unlisted else "双语 README 漏列：" + "、".join(unlisted))

    bogus = sorted({
        p for n in readmes
        for p in re.findall(r"(?<![/\w.-])references/[^\s`'\"()<>\[\]|，。；：、）]+?\.md", "\n".join(unfenced(readmes[n])))
        if not exists_exact(p)
    })
    report(not bogus, "README 内点到的 references 路径均存在"
           if not bogus else "README 指向不存在路径：" + "、".join(bogus))

except Exception as exc:
    report(False, f"文档检查异常：{exc}")

print("红" if red else "绿")
sys.exit(1 if red else 0)
PY
