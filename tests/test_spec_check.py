#!/usr/bin/env python3
"""spec-check 的固定坏样本：10 份 fixture / 11 条用例，逐条断言 exit code 与对应检查行。

用法：python3 tests/test_spec_check.py
零依赖：只用标准库 unittest；不引 pytest，不依赖 CI。
Mutations 一组把解析分支故意改坏，断言对应用例的结果翻转——证明这些样本真守着代码。
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "spec-check.py"
FIX = Path(__file__).resolve().parent / "spec-check"
NOISE = (".idea", ".vscode", "__pycache__", "node_modules", ".worktrees")


def load():
    """把被测脚本当模块加载，用来核用例清单与脚本常量没漂。"""
    spec = importlib.util.spec_from_file_location("spec_check_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(spec: Path | str, *args: str, cwd: Path = ROOT, script: Path = SCRIPT) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, str(script), str(spec), *args],
                          capture_output=True, text=True, cwd=cwd)
    return proc.returncode, proc.stdout + proc.stderr


def line(out: str, cid: str) -> str:
    for row in out.splitlines():
        if row.startswith(cid + " | "):
            return row
    raise AssertionError(f"输出里没有 {cid} 这行：\n{out}")


class Fixtures(unittest.TestCase):
    """每条 fixture 只坏一处，断言就咬得住：exit code + 那一行的红/绿 + 证据片段。"""

    CASES = (
        # 用例, fixture, 额外参数, 期望 exit, (检查项, 期望, 证据片段)
        ("缺三行锚", "missing-anchors.md", (), 1, ("E1", "红", "缺：目标、不做、验收")),
        ("空验证", "empty-verify.md", (), 1, ("E2", "红", "AC 行没有验证方法")),
        ("占位符", "placeholder.md", (), 1, ("E3", "红", "TBD")),
        ("❌ 未处置", "cross-no-disposition.md", (), 1, ("E4", "红", "AC1 上传成功")),
        ("怎么验 表头", "clean.md", (), 0, ("E2", "绿", "AC 1 条")),
        ("不改：无", "no-change-none.md", (), 0, ("W2", "绿", "不改：无")),
        ("~~~ 围栏", "tilde-fence.md", (), 0, ("E3", "绿", "无占位符")),
        ("行内代码里的 ❌", "inline-cross.md", (), 0, ("E2", "绿", "AC 1 条")),
        ("patch", "clean.md", ("--diff", str(FIX / "patch-inside.patch")), 0,
         ("E5", "绿", "diff 全在「改」清单内")),
        ("无效 base", "clean.md", ("--base", "no-such-ref"), 1, ("E5", "红", "无效")),
    )

    def test_cases(self):
        for name, fixture, args, want_exit, (cid, want, text) in self.CASES:
            with self.subTest(name):
                code, out = run(FIX / fixture, *args)
                self.assertEqual(code, want_exit, f"{name}：\n{out}")
                row = line(out, cid)
                self.assertTrue(row.startswith(f"{cid} | {want} "), f"{name}：{row}")
                self.assertIn(text, row, f"{name}：{row}")


class Untracked(unittest.TestCase):
    """第 11 条：E5 只放过 untracked 一侧的噪声目录，真改动照样红。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "spec.md").write_text((FIX / "untracked.md").read_text(encoding="utf-8"), encoding="utf-8")
        (self.repo / "a.py").write_text("x = 1\n", encoding="utf-8")
        (self.repo / "other.py").write_text("y = 1\n", encoding="utf-8")
        self.git("init", "-q", "-b", "main")
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True, text=True)

    def check(self, script: Path = SCRIPT) -> tuple[int, str]:
        return run(self.repo / "spec.md", "--base", "HEAD", cwd=self.repo, script=script)

    def test_noise_dirs_all_ignored(self):
        """5 个噪声目录各一条用例；清单与脚本的 NOISE_DIRS 必须一致，漂了当场红。"""
        self.assertEqual(tuple(load().NOISE_DIRS), NOISE)
        for name in NOISE:
            with self.subTest(dir=name):
                (self.repo / name).mkdir()
                (self.repo / name / "x.txt").write_text("x", encoding="utf-8")
                code, out = self.check()
                self.assertEqual(code, 0, out)
                self.assertIn("E5 | 绿", out)
                shutil.rmtree(self.repo / name)

    def test_new_file_still_red(self):
        (self.repo / "src").mkdir()
        (self.repo / "src" / "new.py").write_text("z = 1\n", encoding="utf-8")
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("越界：src", out)   # 未跟踪目录会被 git 折叠成 src/，红就够了

    def test_tracked_change_still_red(self):
        (self.repo / "other.py").write_text("y = 2\n", encoding="utf-8")
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("越界：other.py", out)


class Mutations(unittest.TestCase):
    """解析分支被改坏，对应 fixture 的结果必须翻转；否则这些用例只是摆设。"""

    CASES = (
        # 名字, 改前, 改后, fixture, 变异后期望 exit, (检查项, 期望结果)
        ("行内剥离", "result = strip_inline(cells[result_idx]) if result_idx is not None",
         "result = cells[result_idx] if result_idx is not None", "inline-cross.md", 1, ("E2", "红")),
        ("三行锚", 'ANCHORS = ("目标", "不做", "验收")',
         'ANCHORS = ("目标", "不做", "验收", "锚四")', "clean.md", 1, ("E1", "红")),
        ("~~~ 围栏", 'if fence is None and (s.startswith("```") or s.startswith("~~~")):',
         'if fence is None and s.startswith("```"):', "tilde-fence.md", 1, ("E3", "红")),
        ("占位符", 'PLACEHOLDERS = ("{{", "TBD", "待补")', 'PLACEHOLDERS = ("{{", "待补")',
         "placeholder.md", 0, ("E3", "绿")),
        ("怎么验 表头", 'VERIFY_WORDS = ("验证", "证据", "怎么验", "如何验", "验法")',
         'VERIFY_WORDS = ("验证", "证据", "如何验", "验法")', "clean.md", 1, ("E2", "红")),
    )

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def mutate(self, old: str, new: str) -> Path:
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertIn(old, src, "变异点挪了——脚本改过，测试要跟着改")
        path = self.dir / "spec-check-mutated.py"
        path.write_text(src.replace(old, new, 1), encoding="utf-8")
        return path

    def test_branches(self):
        for name, old, new, fixture, want_exit, (cid, want) in self.CASES:
            with self.subTest(name):
                script = self.mutate(old, new)
                code, out = run(FIX / fixture, script=script)
                self.assertEqual(code, want_exit, f"{name}：\n{out}")
                self.assertTrue(line(out, cid).startswith(f"{cid} | {want} "), f"{name}：{out}")

    def test_noise_filter_mutation_goes_red(self):
        script = self.mutate("if not is_noise(path):", "if True:")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "spec.md").write_text((FIX / "untracked.md").read_text(encoding="utf-8"), encoding="utf-8")
            for args in (("init", "-q", "-b", "main"),
                         ("-c", "user.name=t", "-c", "user.email=t@t", "add", "-A"),
                         ("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")):
                subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)
            # 提交之后再放噪声目录：它必须是 untracked，否则守的不是这条分支
            (repo / ".idea").mkdir()
            (repo / ".idea" / "workspace.xml").write_text("<x/>", encoding="utf-8")
            code, out = run(repo / "spec.md", "--base", "HEAD", cwd=repo, script=script)
            self.assertEqual(code, 1, out)
            self.assertIn("越界：.idea/", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
