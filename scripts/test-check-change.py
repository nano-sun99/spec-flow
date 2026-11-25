#!/usr/bin/env python3
"""check-change.py 的正负例测试。

覆盖：真实历史 manifest 提交树一致性校验、manifest-only 尾部钉扎、非 manifest 尾改拦截、
正式模式禁字面 HEAD、祖先下界、--draft 正负例、NON_RULE_ALLOW 收紧与 review_ref 格式统一。
"""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

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
    # B-01：正式模式禁止字面 HEAD
    data = copy.deepcopy(original)
    data["head"] = "HEAD"
    path = with_manifest(data)
    results.append(expect(False, "正式模式 manifest.head='HEAD' 红", run(path), "正式模式禁止 manifest.head"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["approval"]["head"] = "HEAD"
    path = with_manifest(data)
    results.append(expect(False, "正式模式 approval.head='HEAD' 红", run(path), "正式模式禁止 approval.head"))
    path.unlink(missing_ok=True)

    # B-02 场景 2：pinned == base 必须拦红
    data = copy.deepcopy(original)
    data["base"] = "be0f6f7"
    data["head"] = "be0f6f7"
    data["approval"]["base"] = "be0f6f7"
    data["approval"]["head"] = "be0f6f7"
    path = with_manifest(data)
    results.append(
        expect(
            False,
            "manifest.head 等于 base 红",
            run(path, base="be0f6f7", head="d06ae65"),
            "严格后代提交",
        )
    )
    path.unlink(missing_ok=True)

    # B-09：tail_pinned 下 approval.head 指错提交红
    data = copy.deepcopy(original)
    data["approval"]["head"] = "aaac33c"
    path = with_manifest(data)
    results.append(
        expect(
            False,
            "tail_pinned 下 approval.head 不一致红",
            run(path, base=BASE, head="2daa47c"),
            "approval.head 解析后与 --head 不一致",
        )
    )
    path.unlink(missing_ok=True)

    # --draft 正负例 + 正式模式缺 approval 红
    draft_data = copy.deepcopy(original)
    draft_data.pop("approval", None)
    draft_data.setdefault("view_files", []).append(
        {
            "file": "docs/changes/2026-11-25-replacement-manifest/manifest.json",
            "reason": "单测临时副本替代原 manifest 路径",
            "reviewer": "review-agent",
            "review_ref": "review:test-draft",
        }
    )
    path = with_manifest(draft_data)
    results.append(expect(True, "--draft 缺 approval 绿", run(path, draft=True), "mode=draft"))
    results.append(expect(False, "正式模式缺 approval 红", run(path, draft=False), "顶层缺字段"))
    path.unlink(missing_ok=True)

    draft_bad = copy.deepcopy(draft_data)
    draft_bad["rules"] = []
    path = with_manifest(draft_bad)
    results.append(expect(False, "--draft 空 rules 仍红", run(path, draft=True), "rules 为空"))
    path.unlink(missing_ok=True)

    draft_malformed = copy.deepcopy(draft_data)
    draft_malformed["approval"] = "not-an-object"
    path = with_manifest(draft_malformed)
    results.append(expect(False, "--draft 畸形 approval 红", run(path, draft=True), "approval 必须是对象"))
    path.unlink(missing_ok=True)

    # B-08：坏 base 报结构化错误而非崩溃
    data = copy.deepcopy(original)
    data["base"] = "<base commit>"
    path = with_manifest(data)
    results.append(expect(False, "坏 manifest.base 结构化报红", run(path), "manifest.base 解析不了"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["rules"] = []
    path = with_manifest(data)
    results.append(expect(False, "空 rules 红", run(path), "rules 为空"))
    path.unlink(missing_ok=True)

    # B-06 & B-09：收紧 NON_RULE_ALLOW，禁止盖规则文件 / SKILL / README
    for bad_file in ("references/v2/10-stages.md", "references/10-stages.md", "SKILL.md", "references/v2/SKILL.md", "README.md"):
        data = copy.deepcopy(original)
        data.setdefault("non_rule_changes", []).append({"file": bad_file, "reason": "试图免审覆盖"})
        path = with_manifest(data)
        results.append(expect(False, f"non_rule 盖 {bad_file} 红", run(path), "non_rule_changes 不允许覆盖规则文件"))
        path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["scans"][0]["hits"].append(
        {"file": data["scans"][0]["hits"][0]["file"], "text": "根本不存在的命中", "conclusion": "whitelist"}
    )
    path = with_manifest(data)
    results.append(expect(False, "phantom 命中红", run(path), "登记的命中"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["rules"][0]["old"]["text"] = "x"
    path = with_manifest(data)
    results.append(expect(False, "短 old.text 红", run(path), "old.text 太短"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["rules"][0]["new"].pop("anchor", None)
    path = with_manifest(data)
    results.append(expect(False, "缺 anchor 红", run(path), "缺 new.anchor"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["scans"] = []
    path = with_manifest(data)
    results.append(expect(False, "空 scans 红", run(path), "scans 为空"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["rules"][0]["new"]["anchor"] = "审核档位"
    path = with_manifest(data)
    results.append(expect(False, "重复 anchor 红", run(path), "new.anchor 不唯一"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["rules"][0]["evidence"] = "x"
    path = with_manifest(data)
    results.append(expect(False, "短 evidence 红", run(path), "evidence 太短"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["whitelist"][0]["review_ref"] = ""
    path = with_manifest(data)
    results.append(expect(False, "缺 review_ref 红", run(path), "缺 review_ref"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["scans"][0]["hits"][0]["reason"] = ""
    path = with_manifest(data)
    results.append(expect(False, "scan whitelist 缺 reason 红", run(path), "whitelist hit 缺 reason"))
    path.unlink(missing_ok=True)

    # B-06：scans[].hits[] 统一校验 review_ref 格式
    data = copy.deepcopy(original)
    data["scans"][0]["hits"][0]["review_ref"] = "x"
    path = with_manifest(data)
    results.append(expect(False, "scan whitelist review_ref 格式红", run(path), "whitelist hit review_ref 需为链接"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["rules"][12]["new"]["anchor"] = "change manifest 与校验输出（rules"
    path = with_manifest(data)
    results.append(expect(False, "跨规则重复 anchor 红", run(path), "anchor 跨规则重复"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["scans"][0]["scope"] = ["references/v2/README.md"]
    path = with_manifest(data)
    results.append(expect(False, "窄 scope 红", run(path), "scope 未覆盖默认"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["scans"][0]["query"] = "根本不存在的正则"
    data["scans"][0]["hits"] = []
    data["scans"][0]["conclusion"] = "match"
    path = with_manifest(data)
    results.append(expect(False, "零命中 scan 红", run(path), "零命中 scan"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["whitelist"][0]["review_ref"] = "x"
    path = with_manifest(data)
    results.append(expect(False, "review_ref 格式红", run(path), "review_ref 需为链接"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["scans"][0]["hits"] = [h for h in data["scans"][0]["hits"] if "2026-09-11" not in h["file"]]
    path = with_manifest(data)
    results.append(expect(False, "命中登记数不足红", run(path), "命中登记数"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data.pop("title", None)
    path = with_manifest(data)
    results.append(expect(False, "缺 title 红", run(path), "顶层缺字段"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["head"] = "aaac33c"
    path = with_manifest(data)
    results.append(expect(False, "head 与 --head 不一致红", run(path), "manifest.head 解析后与 --head 不一致"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["view_files"] = [{"file": "docs/changes/README.md", "reason": "测试视图"}]
    path = with_manifest(data)
    results.append(expect(False, "view_files 缺 reviewer 红", run(path), "view_files[1] reviewer"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["count_checks"] = [
        {"name": "测试计数", "value": 1, "source": "docs/changes/README.md"}
    ]
    path = with_manifest(data)
    results.append(expect(False, "count_checks 缺 command 红", run(path), "count_checks[1] command 太短"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data["section_ref_whitelist"] = [{"ref": "§9.9.9", "reason": "测试外部引用"}]
    path = with_manifest(data)
    results.append(expect(False, "section_ref_whitelist 缺 reviewer 红", run(path), "section_ref_whitelist[1] reviewer"))
    path.unlink(missing_ok=True)

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
