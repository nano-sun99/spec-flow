#!/usr/bin/env python3
"""check-change.py 的正负例测试。

覆盖：真实历史 manifest 提交树一致性校验、manifest-only 尾部钉扎、非 manifest 尾改拦截、
正式模式严禁符号引用与 JSON null 绕过、--from-disk 输出标识、--draft 正负例、
容器类型守卫、NON_RULE_ALLOW 收紧与 review_ref 格式统一。
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
MANIFEST = ROOT / "docs/changes/2026-11-25-replacement-manifest/manifest.json"
MANIFEST_193 = ROOT / "docs/changes/2026-11-25-change-protocol-portability/manifest.json"
BASE = "06814b0"
HEAD = "HEAD"
_spec = importlib.util.spec_from_file_location("check_change", ROOT / "scripts/check-change.py")
check_change = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(check_change)


def run(
    manifest_path: Path,
    *,
    base: str | None = None,
    head: str | None = None,
    draft: bool = False,
    from_disk: bool = True,
) -> subprocess.CompletedProcess:
    cmd = [
        sys.executable,
        str(ROOT / "scripts/check-change.py"),
        "--manifest",
        str(manifest_path),
        "--base",
        base or BASE,
        "--head",
        head or HEAD,
        "--root",
        str(ROOT),
    ]
    if draft:
        cmd.append("--draft")
    if from_disk and not draft:
        cmd.append("--from-disk")
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)


def lint_in_memory(
    manifest_path: Path,
    data: dict,
    *,
    base: str,
    head: str,
    draft: bool = False,
    from_disk: bool = True,
) -> tuple[list[str], str]:
    """针对真实 manifest 路径做内存替换（零写盘），精确测试 tail_pinned 等分支。"""
    payload = json.dumps(data, ensure_ascii=False)
    real_read_text = Path.read_text

    def fake_read_text(self: Path, *args, **kwargs) -> str:
        if self.resolve() == manifest_path.resolve():
            return payload
        return real_read_text(self, *args, **kwargs)

    buf = io.StringIO()
    with mock.patch.object(Path, "read_text", fake_read_text), contextlib.redirect_stdout(buf):
        errs = check_change.lint(ROOT, manifest_path, base, head, draft=draft, from_disk=from_disk)
    return errs, buf.getvalue()


def with_manifest(data: dict) -> Path:
    fd, name = tempfile.mkstemp(
        suffix=".json",
        prefix="manifest.test.",
        dir=ROOT / "docs/changes/2026-11-25-replacement-manifest",
    )
    Path(name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return Path(name)


def expect(ok: bool, name: str, proc: subprocess.CompletedProcess, needle: str = "") -> bool:
    good = (proc.returncode == 0) == ok and (not needle or needle in proc.stdout)
    print(("PASS " if good else "FAIL ") + name)
    if not good:
        print(proc.stdout)
        print(proc.stderr)
    return good


def expect_mem(ok: bool, name: str, errs: list[str], out: str, needle: str = "") -> bool:
    good = (not errs) == ok and (not needle or needle in out)
    print(("PASS " if good else "FAIL ") + name)
    if not good:
        print("errors:", errs)
        print(out)
    return good


def main() -> int:
    global HEAD
    original = json.loads(MANIFEST.read_text(encoding="utf-8"))
    HEAD = str(original.get("head", "HEAD"))
    results: list[bool] = []

    # 正式提交树一致性校验（不传 --from-disk）：PR #192 与 PR #193 真实合并顶提交均绿
    results.append(
        expect(
            True,
            "真实 manifest（PR #192 顶提交 2daa47c 提交树一致）绿",
            run(MANIFEST, base=BASE, head="2daa47c", from_disk=False),
            "content_pinned=07c8665",
        )
    )
    results.append(
        expect(
            True,
            "manifest-only 尾部钉扎提交（PR #193 顶提交 d06ae65）绿",
            run(MANIFEST_193, base="d5e2842", head="d06ae65", from_disk=False),
            "content_pinned=be0f6f7",
        )
    )
    # R2-B-03：--from-disk 显式输出 mode=from-disk 与非合并门禁提示
    results.append(
        expect(
            True,
            "--from-disk 输出显式标记 mode=from-disk",
            run(MANIFEST_193, base="d5e2842", head="d06ae65", from_disk=True),
            "mode=from-disk",
        )
    )
    # B-02 场景 1：磁盘已钉扎 manifest 对着旧提交 be0f6f7（提交树内仍为 HEAD）必须拦红
    results.append(
        expect(
            False,
            "磁盘 manifest 与 --head 提交树不一致红",
            run(MANIFEST_193, base="d5e2842", head="be0f6f7", from_disk=False),
            "提交内",
        )
    )
    # 钉扎后若改动非 manifest 文件仍须拦红
    results.append(
        expect(
            False,
            "钉扎提交后有非 manifest 改动红",
            run(MANIFEST, base=BASE, head="8c4edbe"),
            "钉扎提交之后存在非 manifest 文件改动",
        )
    )
    # R2-B-01：正式模式禁止字面 HEAD 与全部符号引用（@ / HEAD~0 / 分支名）
    for bad_ref in ("HEAD", "@", "HEAD~0", "refactor/v2-streamline"):
        data = copy.deepcopy(original)
        data["head"] = bad_ref
        errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
        results.append(expect_mem(False, f"正式模式 manifest.head={bad_ref!r} 红", errs, out, "不可变十六进制提交 SHA"))

        data = copy.deepcopy(original)
        data["approval"]["head"] = bad_ref
        errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
        results.append(expect_mem(False, f"正式模式 approval.head={bad_ref!r} 红", errs, out, "不可变十六进制提交 SHA"))

    # R2-B-02：正式模式 JSON null 不得转为 "None" 绕过；review_ref 裸前缀不得放行
    data = copy.deepcopy(original)
    data["approval"]["user_quote"] = None
    data["approval"]["link"] = None
    data["semantic_checks"][0]["item"] = None
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(
        expect_mem(
            False,
            "JSON null 必填审批与语义检查拦截红",
            errs,
            out,
            "approval 缺 user_quote",
        )
    )

    for bare_ref in ("http", "PR #", "review:"):
        data = copy.deepcopy(original)
        data["whitelist"][0]["review_ref"] = bare_ref
        errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
        results.append(expect_mem(False, f"裸 review_ref={bare_ref!r} 红", errs, out, "review_ref 需为有效链接"))

    # R2-B-02 场景 2：--draft 下 approval.head=null / approval.base=null 不误报红
    data = copy.deepcopy(original)
    data["approval"] = {"head": None, "base": None}
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c", draft=True)
    results.append(expect_mem(True, "--draft 下 approval.head=null 绿", errs, out, "mode=draft"))

    # B-02 场景 2：pinned == base 必须拦红
    data = copy.deepcopy(original)
    data["base"] = "be0f6f7"
    data["head"] = "be0f6f7"
    data["approval"]["base"] = "be0f6f7"
    data["approval"]["head"] = "be0f6f7"
    errs, out = lint_in_memory(MANIFEST_193, data, base="be0f6f7", head="d06ae65")
    results.append(expect_mem(False, "manifest.head 等于 base 红", errs, out, "严格后代提交"))

    # R2-B-06：真正进入 tail_pinned=True 分支，仅报 approval.head 不一致（精确断言）
    data = copy.deepcopy(original)
    data["approval"]["head"] = "aaac33c"
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    exact_tail = (
        "content_pinned=07c8665" in out
        and errs == ["approval.head 解析后与 --head 不一致"]
    )
    print(("PASS " if exact_tail else "FAIL ") + "tail_pinned 真进入且仅报 approval.head 不一致红")
    if not exact_tail:
        print("errors:", errs)
        print(out)
    results.append(exact_tail)

    # --draft 正负例 + 正式模式缺 approval 红
    draft_data = copy.deepcopy(original)
    draft_data.pop("approval", None)
    errs, out = lint_in_memory(MANIFEST, draft_data, base=BASE, head="2daa47c", draft=True)
    results.append(expect_mem(True, "--draft 缺 approval 绿", errs, out, "mode=draft"))
    errs, out = lint_in_memory(MANIFEST, draft_data, base=BASE, head="2daa47c", draft=False)
    results.append(expect_mem(False, "正式模式缺 approval 红", errs, out, "顶层缺字段"))

    draft_bad = copy.deepcopy(draft_data)
    draft_bad["rules"] = []
    errs, out = lint_in_memory(MANIFEST, draft_bad, base=BASE, head="2daa47c", draft=True)
    results.append(expect_mem(False, "--draft 空 rules 仍红", errs, out, "rules 为空"))

    draft_malformed = copy.deepcopy(draft_data)
    draft_malformed["approval"] = "not-an-object"
    errs, out = lint_in_memory(MANIFEST, draft_malformed, base=BASE, head="2daa47c", draft=True)
    results.append(expect_mem(False, "--draft 畸形 approval 红", errs, out, "approval 必须是对象"))

    # R2-B-08：畸形容器类型与 old.line=True 不崩溃、结构化报红
    for label, mutator, needle in [
        ("rules 非数组红", lambda d: d.__setitem__("rules", "bad"), "rules 必须是数组"),
        ("rules 元素非对象红", lambda d: d.__setitem__("rules", [123]), "rules[1] 必须是对象"),
        ("old.line=True 红", lambda d: d["rules"][0]["old"].__setitem__("line", True), "缺 old.line（整数）"),
    ]:
        data = copy.deepcopy(original)
        mutator(data)
        errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
        results.append(expect_mem(False, label, errs, out, needle))

    # B-08：坏 base 报结构化错误而非崩溃
    data = copy.deepcopy(original)
    data["base"] = "<base commit>"
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c", draft=True)
    results.append(expect_mem(False, "坏 manifest.base 结构化报红", errs, out, "manifest.base 解析不了"))

    data = copy.deepcopy(original)
    data["rules"] = []
    path = with_manifest(data)
    results.append(expect(False, "空 rules 红", run(path), "rules 为空"))
    path.unlink(missing_ok=True)

    # B-06 & B-09：收紧 NON_RULE_ALLOW，禁止盖规则文件 / SKILL / README
    for bad_file in ("references/v2/10-stages.md", "references/10-stages.md", "SKILL.md", "references/v2/SKILL.md", "README.md"):
        data = copy.deepcopy(original)
        data.setdefault("non_rule_changes", []).append({"file": bad_file, "reason": "试图免审覆盖"})
        errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
        results.append(expect_mem(False, f"non_rule 盖 {bad_file} 红", errs, out, "non_rule_changes 不允许覆盖规则文件"))

    data = copy.deepcopy(original)
    data["scans"][0]["hits"].append(
        {"file": data["scans"][0]["hits"][0]["file"], "text": "根本不存在的命中", "conclusion": "whitelist"}
    )
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "phantom 命中红", errs, out, "登记的命中"))

    data = copy.deepcopy(original)
    data["rules"][0]["old"]["text"] = "x"
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "短 old.text 红", errs, out, "old.text 太短"))

    data = copy.deepcopy(original)
    data["rules"][0]["new"].pop("anchor", None)
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "缺 anchor 红", errs, out, "缺 new.anchor"))

    data = copy.deepcopy(original)
    data["scans"] = []
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "空 scans 红", errs, out, "scans 为空"))

    data = copy.deepcopy(original)
    data["rules"][0]["new"]["anchor"] = "审核档位"
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "重复 anchor 红", errs, out, "new.anchor 不唯一"))

    data = copy.deepcopy(original)
    data["rules"][0]["evidence"] = "x"
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "短 evidence 红", errs, out, "evidence 太短"))

    data = copy.deepcopy(original)
    data["whitelist"][0]["review_ref"] = ""
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "缺 review_ref 红", errs, out, "缺 review_ref"))

    data = copy.deepcopy(original)
    data["scans"][0]["hits"][0]["reason"] = ""
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "scan whitelist 缺 reason 红", errs, out, "whitelist hit 缺 reason"))

    data = copy.deepcopy(original)
    data["scans"][0]["hits"][0]["review_ref"] = "x"
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "scan whitelist review_ref 格式红", errs, out, "whitelist hit review_ref 需为有效链接"))

    data = copy.deepcopy(original)
    data["rules"][12]["new"]["anchor"] = "change manifest 与校验输出（rules"
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "跨规则重复 anchor 红", errs, out, "anchor 跨规则重复"))

    data = copy.deepcopy(original)
    data["scans"][0]["scope"] = ["references/v2/README.md"]
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "窄 scope 红", errs, out, "scope 未覆盖默认"))

    data = copy.deepcopy(original)
    data["scans"][0]["query"] = "根本不存在的正则"
    data["scans"][0]["hits"] = []
    data["scans"][0]["conclusion"] = "match"
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "零命中 scan 红", errs, out, "零命中 scan"))

    data = copy.deepcopy(original)
    data["whitelist"][0]["review_ref"] = "x"
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "review_ref 格式红", errs, out, "review_ref 需为有效链接"))

    data = copy.deepcopy(original)
    data["scans"][0]["hits"] = [h for h in data["scans"][0]["hits"] if "2026-09-11" not in h["file"]]
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "命中登记数不足红", errs, out, "命中登记数"))

    data = copy.deepcopy(original)
    data.pop("title", None)
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "缺 title 红", errs, out, "顶层缺字段"))

    data = copy.deepcopy(original)
    data["head"] = "aaac33c"
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "head 与 --head 不一致红", errs, out, "manifest.head 解析后与 --head 不一致"))

    data = copy.deepcopy(original)
    data["view_files"] = [{"file": "docs/changes/README.md", "reason": "测试视图"}]
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "view_files 缺 reviewer 红", errs, out, "view_files[1] reviewer"))

    data = copy.deepcopy(original)
    data["count_checks"] = [
        {"name": "测试计数", "value": 1, "source": "docs/changes/README.md"}
    ]
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "count_checks 缺 command 红", errs, out, "count_checks[1] command 太短"))

    data = copy.deepcopy(original)
    data["section_ref_whitelist"] = [{"ref": "§9.9.9", "reason": "测试外部引用"}]
    errs, out = lint_in_memory(MANIFEST, data, base=BASE, head="2daa47c")
    results.append(expect_mem(False, "section_ref_whitelist 缺 reviewer 红", errs, out, "section_ref_whitelist[1] reviewer"))

    dangling = check_change.dangling_section_refs(
        {"a.md": "见 §9.9.9"}, {"a.md": "见 §9.9.9"}
    )
    results.append(dangling == [("a.md", "9.9.9")])
    print(("PASS " if results[-1] else "FAIL ") + "章节引用无落点红")

    dangling = check_change.dangling_section_refs(
        {"a.md": "见 §9.9.9"}, {"a.md": "见 §9.9.9\n### 9.9.9 标题"}
    )
    results.append(not dangling)
    print(("PASS " if results[-1] else "FAIL ") + "章节引用有落点绿")

    dangling = check_change.dangling_section_refs(
        {"a.md": "见 §3.7"}, {"b.md": "### 3.7.1 Foo"}
    )
    results.append(dangling == [("a.md", "3.7")])
    print(("PASS " if results[-1] else "FAIL ") + "章节号前缀不算落点红")

    dangling = check_change.dangling_section_refs(
        {"a.md": "见 §9.9.9"}, {"b.md": "历史版本 9.9.9 说明"}
    )
    results.append(dangling == [("a.md", "9.9.9")])
    print(("PASS " if results[-1] else "FAIL ") + "正文数字不算标题红")

    dangling = check_change.dangling_section_refs(
        {"a.md": "见 §三"}, {"b.md": "## 三、双扫描"}
    )
    results.append(not dangling)
    print(("PASS " if results[-1] else "FAIL ") + "中文序号标题绿")

    removed = check_change.removed_section_ids(
        {"a.md": "### 3.7.1 Foo\n## 三、Bar"}, {"a.md": "## 三、Bar"}
    )
    results.append(removed == {"3.7.1"})
    print(("PASS " if results[-1] else "FAIL ") + "删章节识别")

    stale = check_change.stale_section_refs(
        {"3.7.1"}, {"docs/reg.tsv": "ep-1\tspec.md#3.7.1", "docs/a.md": "见 §3.7.1"}
    )
    results.append(
        stale == [("docs/reg.tsv", 1, "3.7.1"), ("docs/a.md", 1, "3.7.1")]
    )
    print(("PASS " if results[-1] else "FAIL ") + "反扫仍引用旧章节红")

    stale = check_change.stale_section_refs({"3.7.1"}, {"docs/a.md": "见 §3.8"})
    results.append(not stale)
    print(("PASS " if results[-1] else "FAIL ") + "反扫无旧引用绿")

    print(f"{sum(results)}/{len(results)} 通过")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
