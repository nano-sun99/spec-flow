#!/usr/bin/env python3
"""check-change.py 的正负例测试。

正例：仓库内真实 manifest 必须绿。
负例：空 rules、non_rule 盖规则文件、phantom 命中、短 old.text、缺 anchor、
head 不一致，必须红。
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
BASE = "06814b0"
HEAD = "HEAD"
_spec = importlib.util.spec_from_file_location("check_change", ROOT / "scripts/check-change.py")
check_change = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(check_change)


def run(manifest_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/check-change.py"),
            "--manifest",
            str(manifest_path),
            "--base",
            BASE,
            "--head",
            HEAD,
            "--root",
            str(ROOT),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def with_manifest(data: dict) -> Path:
    # 必须放在 repo 内：否则校验器会把「manifest 未覆盖」当成红，
    # 7 个负例就失去判别性（R2 A3）。
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

    results.append(expect(True, "真实 manifest 绿", run(MANIFEST)))

    data = copy.deepcopy(original)
    data["rules"] = []
    path = with_manifest(data)
    results.append(expect(False, "空 rules 红", run(path), "rules 为空"))
    path.unlink(missing_ok=True)

    data = copy.deepcopy(original)
    data.setdefault("non_rule_changes", []).append(
        {"file": "references/v2/10-stages.md", "reason": "试图用 non_rule 盖规则文件"}
    )
    path = with_manifest(data)
    results.append(expect(False, "non_rule 盖规则文件红", run(path), "non_rule_changes 不允许覆盖规则文件"))
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
    data["head"] = BASE
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
