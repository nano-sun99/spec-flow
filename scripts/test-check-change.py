#!/usr/bin/env python3
"""check-change.py 的正负例测试。

正例：仓库内真实 manifest 必须绿。
负例：空 rules、non_rule 盖规则文件、phantom 命中、短 old.text、缺 anchor、
head 不一致，必须红。
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/changes/2026-11-25-replacement-manifest/manifest.json"
BASE = "06814b0"


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

    print(f"{sum(results)}/{len(results)} 通过")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
