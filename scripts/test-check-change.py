#!/usr/bin/env python3
"""check-change.py v2（薄声明 + 自动扫 diff）全套正负例测试。

覆盖：schema 门禁与旧 v1 快照拒绝、提交树一致与 manifest-only 尾钉扎（含尾提交重命名删文件绕过拦截）、
正式模式不可变 SHA 与 JSON null 守卫、--draft / --from-disk、自动 diff 覆盖率与 aux_files 分流、
外部项目 rule_paths=["docs/"] 豁免 manifest_rel 不死锁、R* 重命名 / C* 拷贝 3 字段解析、
scans[] 零命中自动绿 / 排除口径（docs/changes/README.md 保留、docs/changes/*/、未触及冻结 docs/specs/、
40-cases/、PR 改动草案与显式 scope 取消排除）、伪前缀 scope 拦截、allow[] span 包含 + 唯一覆盖 + count、
三道自动结构反扫（新增断链 § 跳代码块、删改章节跳代码块、已删/改名文本文件 ASCII 边界中文紧邻路径与
带 #anchor/?query/URL 解码相对链接及 {file, path} path_ref_whitelist 含过期拦截）、rebuild 与容器畸形防崩溃。
"""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check-change.py"
LEGACY_V1_MANIFEST = ROOT / "docs/changes/2026-11-25-replacement-manifest/manifest.json"

_spec = importlib.util.spec_from_file_location("check_change", SCRIPT)
check_change = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(check_change)


def sh(cwd: Path, *cmd: str) -> str:
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)
    if p.returncode != 0:
        raise RuntimeError(f"cmd failed {cmd}: {p.stderr}")
    return p.stdout.strip()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def commit_all(repo: Path, msg: str) -> str:
    sh(repo, "git", "add", "-A")
    sh(repo, "git", "commit", "-m", msg)
    return sh(repo, "git", "rev-parse", "HEAD")


def run_cli(
    repo: Path,
    manifest: str,
    base: str,
    head: str = "HEAD",
    *,
    draft: bool = False,
    from_disk: bool = False,
) -> subprocess.CompletedProcess:
    cmd = [
        sys.executable, str(SCRIPT),
        "--root", str(repo),
        "--manifest", manifest,
        "--base", base,
        "--head", head,
    ]
    if draft:
        cmd.append("--draft")
    if from_disk:
        cmd.append("--from-disk")
    return subprocess.run(cmd, cwd=repo, text=True, capture_output=True, check=False)


def lint_mem(
    repo: Path,
    manifest_path: Path,
    data: dict,
    *,
    base: str,
    head: str,
    draft: bool = False,
    from_disk: bool = True,
) -> tuple[list[str], str]:
    payload = json.dumps(data, ensure_ascii=False)
    real_read_text = Path.read_text

    def fake_read_text(self: Path, *args, **kwargs) -> str:
        if self.resolve() == manifest_path.resolve():
            return payload
        return real_read_text(self, *args, **kwargs)

    buf = io.StringIO()
    with mock.patch.object(Path, "read_text", fake_read_text), contextlib.redirect_stdout(buf):
        errs = check_change.lint(repo, manifest_path, base, head, draft=draft, from_disk=from_disk)
    return errs, buf.getvalue()


def make_base_manifest(base: str, head: str) -> dict:
    return {
        "schema": 2,
        "change": "2026-11-27-demo",
        "title": "演示替换式变更",
        "base": base,
        "head": head,
        "classification": "replace",
        "approval": {
            "user_quote": "确认按方案替换旧口径",
            "timestamp": "2026-11-27",
            "scope": "references/ 与配套文档",
            "base": base,
            "head": head,
            "link": "PR #200",
        },
        "rules": [
            {
                "id": "R-001",
                "type": "replace",
                "files": ["references/10-stages.md", "references/30-playbooks/new.md"],
                "summary": "重命名旧走法并同步 10-stages 链接与口径",
                "disposition": "replace",
                "status": "done",
            },
            {
                "id": "R-002",
                "type": "replace",
                "files": ["references/15-records.md"],
                "summary": "更新记录页与允许保留的历史说明",
                "disposition": "keep-scoped",
                "status": "whitelist",
                "reason": "保留一处带上下文的旧术语说明",
                "reviewer": "review-agent",
                "review_ref": "review:r1",
            },
        ],
        "scans": [
            {
                "query": "LEGACY_TOKEN",
                "allow": [
                    {
                        "file": "docs/changes/README.md",
                        "match": "历史旧版含 LEGACY_TOKEN 说明",
                        "reason": "历史快照说明保留",
                        "reviewer": "review-agent",
                        "review_ref": "review:r1",
                    }
                ],
            },
            {
                "query": "OBSOLETE_RULE",
            },
        ],
        "semantic_checks": [
            {
                "item": "旧口径与新口径无同触发冲突",
                "conclusion": "changed",
                "evidence": "references/10-stages.md 与 15-records.md 已同步",
            }
        ],
        "rebuild": {"triggered": False, "reason": "", "old_behaviors": []},
    }


def setup_repo(tmp: Path) -> tuple[Path, str, str, str, str]:
    repo = tmp / "repo"
    repo.mkdir()
    sh(repo, "git", "init", "-b", "main")
    sh(repo, "git", "config", "user.email", "test@example.com")
    sh(repo, "git", "config", "user.name", "Test")

    write(repo / "SKILL.md", "# spec-flow\n\n## 1. 入口\n\n见 [10](references/10-stages.md)\n")
    write(repo / "README.md", "# Demo\n\nIntro\n")
    write(repo / "references/README.md", "# Map\n")
    write(repo / "references/10-stages.md", "# 阶段\n\n## 一、核心\n\n见 [旧走法](30-playbooks/old.md#一参考走法) 与 §二\n\n## 二、旧节\n\nOBSOLETE_RULE\n")
    write(repo / "references/15-records.md", "# 记录\n\n## 一、说明\n\n旧内容 LEGACY_TOKEN\n")
    write(repo / "references/30-playbooks/old.md", "# 旧走法\n\n## 一、参考走法\n\n旧步骤\n")
    write(repo / "references/40-cases/case1.md", "# 案例\n\n历史案例提及 LEGACY_TOKEN 与 references/30-playbooks/old.md\n")
    write(repo / "docs/archive/v1/old.md", "# 归档\n\nLEGACY_TOKEN references/30-playbooks/old.md\n")
    write(repo / "docs/changes/README.md", "# 清单\n\n历史旧版含 LEGACY_TOKEN 说明\n")
    write(repo / "docs/changes/2026-11-25-old/notes.md", "# 旧台账\n\nLEGACY_TOKEN\n")
    write(repo / "docs/specs/2026-10-01-frozen.md", "# 冻结规格\n\n历史规格提及 LEGACY_TOKEN 与 references/30-playbooks/old.md\n")
    write(repo / "docs/specs/2026-11-27-draft.md", "# 草案规格\n\n草稿初版\n")
    base_sha = commit_all(repo, "base")

    # 内容提交：重命名 old.md -> new.md、改 10-stages、15-records、README.md（配套）、草案 spec
    (repo / "references/30-playbooks/old.md").unlink()
    write(repo / "references/30-playbooks/new.md", "# 新走法\n\n## 一、参考走法\n\n新步骤\n")
    write(repo / "references/10-stages.md", "# 阶段\n\n## 一、核心\n\n见 [新走法](30-playbooks/new.md#一参考走法) 与 §一\n\n```text\n示例代码块 §9.9.9 与已删 §二 不误报\n```\n")
    write(repo / "references/15-records.md", "# 记录\n\n## 一、说明\n\n新内容无残留\n")
    write(repo / "README.md", "# Demo\n\nUpdated README\n")
    write(repo / "docs/specs/2026-11-27-draft.md", "# 草案规格\n\n更新后草案\n")
    content_sha = commit_all(repo, "content")

    # manifest-only 尾部钉扎提交
    manifest_rel = "docs/changes/2026-11-27-demo/manifest.json"
    mdata = make_base_manifest(base_sha, content_sha)
    write(repo / manifest_rel, json.dumps(mdata, ensure_ascii=False, indent=2) + "\n")
    pinned_head = commit_all(repo, "pin manifest")

    return repo, base_sha, content_sha, pinned_head, manifest_rel


def main() -> int:
    results: list[bool] = []

    def check(ok: bool, name: str, actual_ok: bool, out: str, needle: str = "") -> None:
        good = (actual_ok == ok) and (not needle or needle in out)
        print(("PASS " if good else "FAIL ") + name)
        if not good:
            print("  expected ok=", ok, "actual=", actual_ok, "needle=", needle)
            print("  output:\n" + out)
        results.append(good)

    # 1. 旧 v1 历史 manifest 被清晰拒绝并提示历史快照
    p_v1 = run_cli(ROOT, str(LEGACY_V1_MANIFEST.relative_to(ROOT)), "06814b0", "2daa47c", from_disk=True)
    check(False, "历史 v1 manifest 缺 schema=2 报红并提示历史快照", p_v1.returncode == 0, p_v1.stdout, "历史快照")

    with tempfile.TemporaryDirectory(prefix="spec-flow-cc-v2-") as td:
        tmp = Path(td)
        repo, base, content, head, mrel = setup_repo(tmp)
        mpath = repo / mrel
        base_manifest = json.loads(mpath.read_text(encoding="utf-8"))

        # 2. 正式模式提交树一致 + manifest-only 尾钉扎 + 0 命中 scan 自动绿 + aux_files=2(README+draft) 不含 manifest_rel
        p = run_cli(repo, mrel, base, head)
        check(
            True,
            "正式模式 manifest-only 尾钉扎绿 + 摘要含 schema=2/status/allow/rule_files=3/aux_files=2",
            p.returncode == 0,
            p.stdout,
            "schema=2",
        )
        check(True, "摘要含 content_pinned", True, p.stdout, f"content_pinned={content[:12]}")
        check(True, "摘要含 status done/whitelist/unresolved=1/1/0", True, p.stdout, "status done/whitelist/unresolved=1/1/0")
        check(True, "摘要含 rule_files=3 aux_files=2 allow=1", True, p.stdout, "rule_files=3 aux_files=2 scans=2 allow=1")

        # 3. --from-disk 显式输出 mode=from-disk 与非合并门禁提示
        p_fd = run_cli(repo, mrel, base, head, from_disk=True)
        check(True, "--from-disk 显式标记 mode=from-disk", p_fd.returncode == 0, p_fd.stdout, "mode=from-disk")

        # 4. 磁盘 manifest 与 --head 提交树不一致红
        p_mismatch = run_cli(repo, mrel, base, content)
        check(False, "磁盘 manifest 与 --head 提交树不一致红", p_mismatch.returncode == 0, p_mismatch.stdout, "不存在或无法解析")

        # 5. schema 边界：缺 schema / schema=1 / schema=True / schema=2.0
        for label, s_val in [("缺 schema 红", None), ("schema=1 红", 1), ("schema=True 红", True), ("schema=2.0 红", 2.0)]:
            d = copy.deepcopy(base_manifest)
            if s_val is None:
                d.pop("schema", None)
            else:
                d["schema"] = s_val
            errs, out = lint_mem(repo, mpath, d, base=base, head=head)
            check(False, label, not errs, out or "\n".join(errs), "manifest.schema 必须为整数 2")

        # 6. 正式模式禁止 HEAD / @ / HEAD~0 / 分支名；JSON null 拦截；裸 review_ref 拦截
        for bad_ref in ("HEAD", "@", "HEAD~0", "main"):
            d = copy.deepcopy(base_manifest)
            d["head"] = bad_ref
            errs, out = lint_mem(repo, mpath, d, base=base, head=head)
            check(False, f"正式模式 manifest.head={bad_ref!r} 红", not errs, out, "不可变十六进制提交 SHA")

            d = copy.deepcopy(base_manifest)
            d["approval"]["head"] = bad_ref
            errs, out = lint_mem(repo, mpath, d, base=base, head=head)
            check(False, f"正式模式 approval.head={bad_ref!r} 红", not errs, out, "不可变十六进制提交 SHA")

        d = copy.deepcopy(base_manifest)
        d["approval"]["user_quote"] = None
        errs, out = lint_mem(repo, mpath, d, base=base, head=head)
        check(False, "正式模式 JSON null approval.user_quote 红", not errs, out, "approval 缺 user_quote")

        for bare in ("http", "PR #", "review:"):
            d = copy.deepcopy(base_manifest)
            d["rules"][1]["review_ref"] = bare
            errs, out = lint_mem(repo, mpath, d, base=base, head=head)
            check(False, f"裸 review_ref={bare!r} 红", not errs, out, "review_ref 需为有效链接")

        # 7. --draft 正负例（缺 approval 与 head="HEAD" 绿；approval.head=null 绿；缺 rules 红）
        d_draft = copy.deepcopy(base_manifest)
        d_draft.pop("approval", None)
        d_draft["head"] = "HEAD"
        errs, out = lint_mem(repo, mpath, d_draft, base=base, head=head, draft=True)
        check(True, "--draft 缺 approval 且 head='HEAD' 绿", not errs, out, "mode=draft")

        d_draft_null = copy.deepcopy(base_manifest)
        d_draft_null["approval"] = {"base": None, "head": None}
        errs, out = lint_mem(repo, mpath, d_draft_null, base=base, head=head, draft=True)
        check(True, "--draft approval.base/head=null 绿", not errs, out, "mode=draft")

        errs, out = lint_mem(repo, mpath, d_draft, base=base, head=head, draft=False)
        check(False, "正式模式缺 approval 红", not errs, out, "顶层缺字段：approval")

        # 8. 未覆盖变更规则文件拦截 & rules[].files 声明未改动文件 / manifest_rel 拦截
        d_uncov = copy.deepcopy(base_manifest)
        d_uncov["rules"] = [d_uncov["rules"][0]]  # 漏掉 15-records.md
        errs, out = lint_mem(repo, mpath, d_uncov, base=base, head=head)
        check(False, "漏覆盖变更规则文件 15-records.md 红", not errs, out, "未覆盖变更规则文件")

        d_fake = copy.deepcopy(base_manifest)
        d_fake["rules"][0]["files"].append("SKILL.md")  # SKILL.md 未改动
        errs, out = lint_mem(repo, mpath, d_fake, base=base, head=head)
        check(False, "rules[].files 声明未改动文件 SKILL.md 红", not errs, out, "未出现在 base..head diff")

        d_self = copy.deepcopy(base_manifest)
        d_self["rules"][0]["files"].append(mrel)
        errs, out = lint_mem(repo, mpath, d_self, base=base, head=head)
        check(False, "rules[].files 填 manifest 自身红", not errs, out, "禁止填 manifest 自身")

        # 9. scans[].scope 伪前缀 ("ref") 绕过拦截 + 显式指向冻结 docs/specs/ 取消默认排除 (R3-L2)
        d_pseudo = copy.deepcopy(base_manifest)
        d_pseudo["scans"] = [{"query": "OBSOLETE_RULE", "scope": ["ref"]}]
        errs, out = lint_mem(repo, mpath, d_pseudo, base=base, head=head)
        check(False, "scans[].scope 伪前缀 'ref' 缺 scope_reason 拦截红", not errs, out, "未覆盖全部 rule_paths")

        d_exp_spec = copy.deepcopy(base_manifest)
        d_exp_spec["scans"] = [{"query": "LEGACY_TOKEN", "scope": ["SKILL.md", "references/", "docs/specs/"]}]
        errs, out = lint_mem(repo, mpath, d_exp_spec, base=base, head=head)
        check(False, "显式 scope 指向 docs/specs/ 取消默认排除并检出冻结规格命中红", not errs, out, "docs/specs/2026-10-01-frozen.md")

        d_exp_case = copy.deepcopy(base_manifest)
        d_exp_case["scans"] = [{"query": "LEGACY_TOKEN", "scope": ["SKILL.md", "references/", "references/40-cases/"]}]
        errs, out = lint_mem(repo, mpath, d_exp_case, base=base, head=head)
        check(False, "显式 scope 指向 references/40-cases/ 取消默认排除红", not errs, out, "references/40-cases/case1.md")

        # 10. PR 改动中的草案 spec 仍纳入默认扫描；未触及冻结 spec 与 40-cases 保持排除
        d_draft_hit = copy.deepcopy(base_manifest)
        d_draft_hit["scans"] = [{"query": "更新后草案"}]
        errs, out = lint_mem(repo, mpath, d_draft_hit, base=base, head=head)
        check(False, "本 PR 改动中的 docs/specs 草案纳入默认扫描红", not errs, out, "docs/specs/2026-11-27-draft.md")

        # 11. 容器畸形防崩溃（含 6 处不可哈希枚举）& rebuild.triggered=true 缺 old_behaviors 拦截
        for label, mut, needle in [
            ("rules 非数组红", lambda x: x.__setitem__("rules", "bad"), "rules 必须是数组"),
            ("rules 元素非对象红", lambda x: x.__setitem__("rules", [123]), "rules[1] 必须是对象"),
            ("classification=[] 不崩溃报红", lambda x: x.__setitem__("classification", []), "classification 不在"),
            ("rules[0].type={} 不崩溃报红", lambda x: x["rules"][0].__setitem__("type", {}), "type 不在"),
            ("rules[0].disposition=[] 不崩溃报红", lambda x: x["rules"][0].__setitem__("disposition", []), "disposition 不在"),
            ("rules[0].status=[] 不崩溃报红", lambda x: x["rules"][0].__setitem__("status", []), "status 不在"),
            ("allow.reviewer=[] 不崩溃报红", lambda x: x["scans"][0]["allow"][0].__setitem__("reviewer", []), "reviewer 不在"),
            ("semantic_checks.conclusion=[] 不崩溃报红", lambda x: x["semantic_checks"][0].__setitem__("conclusion", []), "conclusion 不合法"),
            ("rebuild 缺 old_behaviors 红", lambda x: x.__setitem__("rebuild", {"triggered": True, "reason": "重构", "old_behaviors": []}), "old_behaviors 为空"),
            ("allow.count=True 红", lambda x: x["scans"][0]["allow"][0].__setitem__("count", True), "count 必须是正整数"),
        ]:
            d = copy.deepcopy(base_manifest)
            mut(d)
            errs, out = lint_mem(repo, mpath, d, base=base, head=head)
            check(False, label, not errs, out, needle)

        # 11b. 带注释 tag 作 --base 剥离至提交 SHA 绿（B6）
        sh(repo, "git", "tag", "-a", "v1.0-test", "-m", "annotated base tag", base)
        errs, out = lint_mem(repo, mpath, base_manifest, base="v1.0-test", head=head, draft=True)
        check(True, "带注释 tag 作 --base 自动剥离至提交 SHA 绿", not errs, out)

        # 12. 对抗分支测试：tail-rename 绕过、C* 3 字段、allow span 攻击（同行双命中/搭便车/重叠/过期）、
        #     新增断链 §、删改章节残留、已删/改名中文紧邻路径 & #anchor/?query/URL 编码链接 & path_ref_whitelist
        # 12a. 尾提交将他文件重命名为 manifest_rel 绕过拦截
        sh(repo, "git", "checkout", "-b", "test-tail-rename", content)
        write(repo / "references/README.md", json.dumps(base_manifest, ensure_ascii=False, indent=2) + "\n")
        c_src = commit_all(repo, "put manifest content in README")
        # 改 manifest.head 指 c_src，再在下一提交把 references/README.md 移动为 manifest_rel（100% 重命名！）
        d_tr = copy.deepcopy(base_manifest)
        d_tr["head"] = c_src
        d_tr["approval"]["head"] = c_src
        (repo / "references/README.md").unlink()
        write(repo / mrel, json.dumps(d_tr, ensure_ascii=False, indent=2) + "\n")
        h_tr = commit_all(repo, "rename README to manifest")
        p_tr = run_cli(repo, mrel, base, h_tr)
        check(False, "尾提交将他文件重命名为 manifest_rel 绕过拦截红", p_tr.returncode == 0, p_tr.stdout, "references/README.md")

        # 12b. allow[] span 包含 + 唯一覆盖 + 搭便车 + 同行合法双命中 + 重叠 + 过期
        sh(repo, "git", "checkout", "-b", "test-allow-span", base)
        write(
            repo / "references/15-records.md",
            "# 记录\n\n历史格式 old.line（旧表1）与 old.line（旧表2）\n历史说明 old.line（保留），此处漏删 old 规则\n",
        )
        c_span = commit_all(repo, "span fixture")
        d_span = {
            "schema": 2,
            "change": "span-test",
            "title": "测试 allow span",
            "base": base,
            "head": "HEAD",
            "classification": "replace",
            "rules": [{"id": "R-1", "type": "replace", "files": ["references/15-records.md"], "summary": "更新记录页测试 span", "disposition": "replace", "status": "done"}],
            "scans": [{
                "query": "old\\.line",
                "scope": ["references/15-records.md"],
                "scope_reason": "仅测 span",
                "allow": [
                    {"file": "references/15-records.md", "match": "old.line（旧表1）", "reason": "旧表1", "reviewer": "user", "review_ref": "PR #1"},
                    {"file": "references/15-records.md", "match": "old.line（旧表2）", "reason": "旧表2", "reviewer": "user", "review_ref": "PR #1"},
                    {"file": "references/15-records.md", "match": "历史说明 old.line（保留）", "reason": "保留", "reviewer": "user", "review_ref": "PR #1"},
                ],
            }],
            "semantic_checks": [{"item": "无冲突核对", "conclusion": "changed", "evidence": "人工核对通过"}],
            "rebuild": {"triggered": False, "reason": "", "old_behaviors": []},
        }
        errs, out = lint_mem(repo, mpath, d_span, base=base, head=c_span, draft=True)
        check(True, "同行合法双命中（2 条上下文精准 allow）绿", not errs, out)

        # 搭便车攻击：query=old\.line|old，只用一条 count=2 的 allow 试图吞没行尾无关 old
        d_piggy = copy.deepcopy(d_span)
        d_piggy["scans"][0]["query"] = "old\\.line|old"
        d_piggy["scans"][0]["allow"][2]["count"] = 2
        errs, out = lint_mem(repo, mpath, d_piggy, base=base, head=c_span, draft=True)
        check(False, "同行第二命中搭便车绕过拦截红", not errs, out, "未登记的命中")

        # 重叠冗余 allow 拦截
        d_ov = copy.deepcopy(d_span)
        d_ov["scans"][0]["allow"].append(
            {"file": "references/15-records.md", "match": "old.line（保留）", "reason": "重叠", "reviewer": "user", "review_ref": "PR #1"}
        )
        errs, out = lint_mem(repo, mpath, d_ov, base=base, head=c_span, draft=True)
        check(False, "多条 allow 重叠覆盖同一命中拦截红", not errs, out, "重叠覆盖同一命中")

        # 过期无效 allow 拦截
        d_exp_al = copy.deepcopy(d_span)
        d_exp_al["scans"][0]["allow"].append(
            {"file": "references/15-records.md", "match": "不存在的 old.line 文本", "reason": "过期", "reviewer": "user", "review_ref": "PR #1"}
        )
        errs, out = lint_mem(repo, mpath, d_exp_al, base=base, head=c_span, draft=True)
        check(False, "过期无效 allow（0 命中）拦截红", not errs, out, "过期无效")

        # count=2 精准放行 & 默认 count=1 吞没 2 命中拦截（B3 / A-5）
        d_cnt_fail = copy.deepcopy(d_span)
        d_cnt_fail["scans"][0]["allow"] = [
            {"file": "references/15-records.md", "match": "old.line（旧表1）与 old.line（旧表2）", "reason": "双处", "reviewer": "user", "review_ref": "PR #1"},
            {"file": "references/15-records.md", "match": "历史说明 old.line（保留）", "reason": "保留", "reviewer": "user", "review_ref": "PR #1"},
        ]
        errs, out = lint_mem(repo, mpath, d_cnt_fail, base=base, head=c_span, draft=True)
        check(False, "单条 allow（count=1）吞没 2 处命中拦截红", not errs, out, "命中次数 2 != 声明 count=1")

        d_cnt_ok = copy.deepcopy(d_cnt_fail)
        d_cnt_ok["scans"][0]["allow"][0]["count"] = 2
        errs, out = lint_mem(repo, mpath, d_cnt_ok, base=base, head=c_span, draft=True)
        check(True, "单条 allow 显式 count=2 精准放行 2 处命中绿", not errs, out)

        # 12b-2. ++ 开头新增行不吞行号（B2）
        sh(repo, "git", "checkout", "-b", "test-plus-hunk", base)
        write(
            repo / "references/10-stages.md",
            "# 阶段\n\n## 一、核心\n\n原有内容\n++ 见 §999\n```text\ncode\n```\n真正正文断链 §888\n",
        )
        c_plus = commit_all(repo, "plus prefix line")
        d_plus = copy.deepcopy(d_span)
        d_plus["rules"] = [{"id": "R-1", "type": "replace", "files": ["references/10-stages.md"], "summary": "测试 ++ 开头行号不漂移", "disposition": "replace", "status": "done"}]
        d_plus["scans"] = [{"query": "OBSOLETE_RULE"}]
        errs, out = lint_mem(repo, mpath, d_plus, base=base, head=c_plus, draft=True)
        joined_plus = "\n".join(errs)
        check(False, "++ 开头新增行 §999 检出红", not errs, joined_plus, "§999")
        check(False, "++ 开头后不偏移行号并检出 §888 红", not errs, joined_plus, "§888")

        # 12c. 路径残留反扫（子目录相对链接 + [`scans[]`] 方括号与 (v1) 括号链接 + 中文紧邻裸路径 + {file, path} 重复/非法/过期）+ § 反扫
        sh(repo, "git", "checkout", "-b", "test-path-sec", base)
        write(repo / "references/30-playbooks/old(v1).md", "# 旧括号\n")
        base_v1 = commit_all(repo, "add old(v1)")
        (repo / "references/30-playbooks/old.md").unlink()
        (repo / "references/30-playbooks/old(v1).md").unlink()
        write(repo / "references/30-playbooks/new.md", "# 新走法\n\n## 一、参考走法\n\n见 §99\n")
        write(
            repo / "references/10-stages.md",
            "# 阶段\n\n## 一、核心\n\n"
            "请详见references/30-playbooks/old.md说明；另见 §二。\n"
            "相对链接 [`scans[]`](30-playbooks/old.md#一参考走法) 与 [旧括号](30-playbooks/old%28v1%29.md?x=1#sec \"t\")。\n",
        )
        write(
            repo / "README.md",
            "# Demo\n\n[带锚点](references/30-playbooks/old.md#%E4%B8%80%E5%8F%82%E8%80%83%E8%B5%B0%E6%B3%95?x=1 \"title\")\n",
        )
        c_ps = commit_all(repo, "path and section residue")
        d_ps = copy.deepcopy(d_span)
        d_ps["base"] = base_v1
        d_ps["rules"] = [
            {"id": "R-1", "type": "replace", "files": ["references/10-stages.md", "references/30-playbooks/new.md", "references/30-playbooks/old(v1).md"], "summary": "测试路径与章节残留反扫", "disposition": "replace", "status": "done"},
        ]
        d_ps["scans"] = [{"query": "OBSOLETE_RULE"}]
        errs, out = lint_mem(repo, mpath, d_ps, base=base_v1, head=c_ps, draft=True)
        joined = "\n".join(errs)
        check(False, "紧邻中文裸路径残留拦截红", not errs, joined, "references/10-stages.md:5 → references/30-playbooks/old.md")
        check(False, "子目录相对链接含 [`scans[]`] 与 URL 编码 old(v1).md 均拦截红", not errs, joined, "references/10-stages.md:6 → references/30-playbooks/old(v1).md")
        check(False, "README 带 #anchor/?query/URL 编码链接残留拦截红", not errs, joined, "README.md:3 → references/30-playbooks/old.md")
        check(False, "新增断链 §99 拦截红", not errs, joined, "references/30-playbooks/new.md §99")
        check(False, "删改章节 §二 残留拦截红", not errs, joined, "references/10-stages.md:5 §二")

        # 仅白名单 README.md 不致盲 10-stages.md；两者全白名单绿；重复/非法/过期白名单均拦截（B9）
        check(False, "子目录相对链接 [`scans[]`](30-playbooks/old.md) 精准拦截红", not errs, joined, "references/10-stages.md:6 → references/30-playbooks/old.md")
        d_ps["section_ref_whitelist"] = [
            {"ref": "§99", "reason": "外部章节", "reviewer": "user", "review_ref": "PR #2"},
            {"ref": "§二", "reason": "测试豁免", "reviewer": "user", "review_ref": "PR #2"},
        ]
        d_ps["path_ref_whitelist"] = [
            {"file": "README.md", "path": "references/30-playbooks/old.md", "reason": "迁移说明", "reviewer": "user", "review_ref": "PR #2"},
        ]
        errs, out = lint_mem(repo, mpath, d_ps, base=base_v1, head=c_ps, draft=True)
        check(False, "path_ref_whitelist 仅豁免 README 不致盲 10-stages.md 红", not errs, "\n".join(errs), "references/10-stages.md:5 → references/30-playbooks/old.md")

        d_ps["path_ref_whitelist"].extend([
            {"file": "references/10-stages.md", "path": "references/30-playbooks/old.md", "reason": "迁移说明", "reviewer": "user", "review_ref": "PR #2"},
            {"file": "references/10-stages.md", "path": "references/30-playbooks/old(v1).md", "reason": "括号路径说明", "reviewer": "user", "review_ref": "PR #2"},
        ])
        errs, out = lint_mem(repo, mpath, d_ps, base=base_v1, head=c_ps, draft=True)
        check(True, "绑定式 {file, path} path_ref_whitelist 全覆盖绿", not errs, out)

        d_ps_dup = copy.deepcopy(d_ps)
        d_ps_dup["path_ref_whitelist"].append(
            {"file": "README.md", "path": "references/30-playbooks/old.md", "reason": "重复", "reviewer": "user", "review_ref": "PR #2"}
        )
        errs, out = lint_mem(repo, mpath, d_ps_dup, base=base_v1, head=c_ps, draft=True)
        check(False, "重复 path_ref_whitelist 拦截红", not errs, "\n".join(errs), "重复登记")

        d_ps_bad = copy.deepcopy(d_ps)
        d_ps_bad["path_ref_whitelist"].append(
            {"file": "../bad.md", "path": "references/30-playbooks/old.md", "reason": "非法", "reviewer": "user", "review_ref": "PR #2"}
        )
        errs, out = lint_mem(repo, mpath, d_ps_bad, base=base_v1, head=c_ps, draft=True)
        check(True, "非法 path_ref_whitelist.file 仅报不合法不误报过期", bool(errs) and all("过期无效" not in e for e in errs), "\n".join(errs), "file 不合法")

        d_ps["path_ref_whitelist"].append(
            {"file": "SKILL.md", "path": "references/30-playbooks/old.md", "reason": "过期", "reviewer": "user", "review_ref": "PR #2"}
        )
        errs, out = lint_mem(repo, mpath, d_ps, base=base_v1, head=c_ps, draft=True)
        check(False, "过期无效 path_ref_whitelist 拦截红", not errs, "\n".join(errs), "path_ref_whitelist[4] 过期无效")

        # 12d-2. 阻断漏洞回归：R* 将规则文件重命名为 manifest_rel 不得绕过规则覆盖门禁（B1 / A-6）
        ext_r = tmp / "ext-rename-bypass"
        ext_r.mkdir()
        sh(ext_r, "git", "init", "-b", "main")
        sh(ext_r, "git", "config", "user.email", "t@e.com")
        sh(ext_r, "git", "config", "user.name", "T")
        seed_manifest = {
            "schema": 2,
            "change": "bypass",
            "title": "验证 R* 重命名到 manifest_rel 拦截",
            "base": "0" * 40,
            "head": "HEAD",
            "classification": "replace",
            "rule_paths": ["docs/"],
            "rule_exclude": [],
            "rules": [{"id": "R-1", "type": "replace", "files": ["docs/keep.md"], "summary": "仅声明修改 keep 漏报被删规则文件", "disposition": "replace", "status": "done"}],
            "scans": [{"query": "NEVER_MATCH_TOKEN"}],
            "semantic_checks": [{"item": "无冲突核对", "conclusion": "changed", "evidence": "核对完成"}],
            "rebuild": {"triggered": False, "reason": "", "old_behaviors": []},
        }
        write(ext_r / "docs/keep.md", "# Keep\n\nold\n")
        write(ext_r / "docs/secret-policy.md", json.dumps(seed_manifest, ensure_ascii=False, indent=2) + "\n")
        eb = commit_all(ext_r, "ext base")
        write(ext_r / "docs/keep.md", "# Keep\n\nnew\n")
        (ext_r / "docs/secret-policy.md").unlink()
        seed_manifest["base"] = eb
        bmrel = "docs/changes/2026-11-27-bypass/manifest.json"
        write(ext_r / bmrel, json.dumps(seed_manifest, ensure_ascii=False, indent=2) + "\n")
        ec1 = commit_all(ext_r, "delete secret-policy and add similar manifest")
        seed_manifest["head"] = ec1
        seed_manifest["approval"] = {"user_quote": "ok", "timestamp": "2026-11-27", "scope": "docs", "base": eb, "head": ec1, "link": "PR #9"}
        write(ext_r / bmrel, json.dumps(seed_manifest, ensure_ascii=False, indent=2) + "\n")
        eh1 = commit_all(ext_r, "pin manifest")
        p_b1 = run_cli(ext_r, bmrel, eb, eh1)
        check(False, "R* 将规则文件重命名为 manifest_rel 绕过门禁拦截红（B1）", p_b1.returncode == 0, p_b1.stdout, "docs/secret-policy.md")

        # 12d. 外部项目 rule_paths=["docs/"], rule_exclude=[] 豁免 manifest_rel 不死锁
        ext = tmp / "ext-repo"
        ext.mkdir()
        sh(ext, "git", "init", "-b", "main")
        sh(ext, "git", "config", "user.email", "t@e.com")
        sh(ext, "git", "config", "user.name", "T")
        write(ext / "docs/policy.md", "# Policy\n\nOLD_LIMIT = 10\n")
        ext_base = commit_all(ext, "ext base")
        write(ext / "docs/policy.md", "# Policy\n\nNEW_LIMIT = 20\n")
        ext_mrel = "docs/changes/2026-11-27-limit/manifest.json"
        ext_m = {
            "schema": 2,
            "change": "limit-bump",
            "title": "提高阈值",
            "base": ext_base,
            "head": "HEAD",
            "classification": "replace",
            "rule_paths": ["docs/"],
            "rule_exclude": [],
            "rules": [{"id": "R-1", "type": "replace", "files": ["docs/policy.md"], "summary": "阈值由 10 改为 20", "disposition": "replace", "status": "done"}],
            "scans": [{"query": "OLD_LIMIT"}],
            "semantic_checks": [{"item": "文档与代码一致", "conclusion": "changed", "evidence": "docs/policy.md 已同步"}],
            "rebuild": {"triggered": False, "reason": "", "old_behaviors": []},
        }
        write(ext / ext_mrel, json.dumps(ext_m, ensure_ascii=False, indent=2) + "\n")
        ext_head = commit_all(ext, "ext change with draft manifest")
        p_ext = run_cli(ext, ext_mrel, ext_base, ext_head, draft=True)
        check(True, "外部项目 rule_paths=['docs/'] 豁免 manifest_rel 不死锁绿", p_ext.returncode == 0, p_ext.stdout, "rule_files=1 aux_files=0")

        # 12e. parse_name_status_z 直接测试 C* 3 字段解析与未知状态码报错
        parsed = check_change.parse_name_status_z("C100\0a.md\0b.md\0R095\0old.md\0new.md\0M\0c.md\0D\0d.md\0")
        check(
            True,
            "parse_name_status_z 正确解析 C*/R* 3 字段与 M/D 2 字段",
            parsed == [("C100", "a.md", "b.md"), ("R095", "old.md", "new.md"), ("M", "", "c.md"), ("D", "d.md", "")],
            str(parsed),
        )
        try:
            check_change.parse_name_status_z("X\0weird.md\0")
            bad_st_caught = False
        except RuntimeError:
            bad_st_caught = True
        check(True, "parse_name_status_z 遇未知状态码显式报错", bad_st_caught, "RuntimeError expected")

    passed = sum(results)
    print(f"\n合计：{passed}/{len(results)} 通过")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
