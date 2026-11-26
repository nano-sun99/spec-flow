#!/usr/bin/env python3
"""scripts/run-eval.py 的确定性单测（零外部依赖、零 LLM 调用）。"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNER = REPO_ROOT / "scripts" / "run-eval.py"
SCENARIOS_DIR = REPO_ROOT / "evals" / "scenarios"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUNNER), "--skill-root", str(REPO_ROOT), *args],
        text=True, capture_output=True, check=False,
    )


def git_in(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=True)


class RunEvalTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="test-run-eval-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _materialize(self, selector: str, out: Path | None = None, force: bool = False) -> Path:
        out_dir = out or (self.tmp / "out")
        args = ["--materialize", selector, "--out", str(out_dir)]
        if force:
            args.append("--force")
        p = run_cli(*args)
        self.assertEqual(p.returncode, 0, msg=p.stderr + p.stdout)
        return out_dir

    # ① --validate 正例与负例
    def test_validate_real_scenarios_pass(self) -> None:
        p = run_cli("--validate")
        self.assertEqual(p.returncode, 0, msg=p.stderr + p.stdout)
        self.assertIn("12 条场景", p.stdout)

    def test_validate_negative_cases(self) -> None:
        base_sc = json.loads((SCENARIOS_DIR / "06-edit-frozen-spec.json").read_text(encoding="utf-8"))

        # 缺必填字段
        d1 = self.tmp / "missing"
        d1.mkdir()
        bad = dict(base_sc)
        del bad["rubric"]
        (d1 / "06-edit-frozen-spec.json").write_text(json.dumps(bad), encoding="utf-8")
        p = run_cli("--validate", "--scenarios-dir", str(d1))
        self.assertEqual(p.returncode, 1)
        self.assertIn("rubric", p.stderr)

        # 重复 ID（含文件名不匹配）
        d2 = self.tmp / "dup"
        d2.mkdir()
        (d2 / "06-edit-frozen-spec.json").write_text(json.dumps(base_sc), encoding="utf-8")
        (d2 / "99-dup.json").write_text(json.dumps(base_sc), encoding="utf-8")
        p = run_cli("--validate", "--scenarios-dir", str(d2))
        self.assertEqual(p.returncode, 1)
        self.assertIn("重复", p.stderr)

        # 坏锚点与非法 git mutation 枚举
        d3 = self.tmp / "anchor"
        d3.mkdir()
        bad_anchor = json.loads(json.dumps(base_sc))
        bad_anchor["rules_ref"] = ["references/00-constitution.md#non-existent-anchor"]
        bad_anchor["hard_checks"]["forbid_git_mutations"] = ["bogus_mutation"]
        (d3 / "06-edit-frozen-spec.json").write_text(json.dumps(bad_anchor), encoding="utf-8")
        p = run_cli("--validate", "--scenarios-dir", str(d3))
        self.assertEqual(p.returncode, 1)
        self.assertIn("锚点不存在", p.stderr)
        self.assertIn("非法枚举", p.stderr)

    # ② --materialize 正常生成与拒覆盖
    def test_materialize_and_overwrite_guard(self) -> None:
        out = self._materialize("all")
        self.assertEqual(len(list(out.iterdir())), 12)
        # 核验 04 local_origin、05 wt-issue-42、09 tag+可执行脚本、10 task/demo
        self.assertTrue((out / "04-valid-d0-delegation" / "origin.git").is_dir())
        self.assertTrue((out / "05-worktree-claim-race" / "wt-issue-42" / ".git").is_file())
        self.assertTrue(os.access(out / "09-failure-halt-no-rollback" / "repo" / "deploy_check.sh", os.X_OK))
        tags = git_in(out / "09-failure-halt-no-rollback" / "repo", "tag").stdout.splitlines()
        self.assertIn("v1.0.0", tags)
        branches = git_in(out / "10-irreversible-post-compaction" / "repo", "branch", "--list", "task/demo").stdout
        self.assertIn("task/demo", branches)
        # prompt.txt 仅指路径，不抄录规则正文
        prompt_txt = (out / "01-small-direct-fix" / "prompt.txt").read_text(encoding="utf-8")
        self.assertIn("SKILL.md", prompt_txt)
        self.assertNotIn("L0-1 不可逆或高风险动作必须用户明确确认", prompt_txt)

        # 未传 --force 拒绝覆盖
        p_deny = run_cli("--materialize", "01", "--out", str(out))
        self.assertEqual(p_deny.returncode, 1)
        self.assertIn("--force", p_deny.stderr)

        # 传 --force 覆盖成功
        p_ok = run_cli("--materialize", "01", "--out", str(out), "--force")
        self.assertEqual(p_ok.returncode, 0, msg=p_ok.stderr)

    # ③ --grade 单场景/批量正例、--hard-only、rubric 损坏、9 类负例与忽略规则
    def test_grade_single_batch_hard_only_and_corrupt_rubric(self) -> None:
        out = self._materialize("01,06")
        s1 = out / "01-small-direct-fix"
        (s1 / "repo" / "config.py").write_text("DEFAULT_TIMEOUT = 10\n", encoding="utf-8")
        (s1 / "repo" / "test_config.py").write_text(
            "import config\nassert config.DEFAULT_TIMEOUT == 10\nprint('OK: DEFAULT_TIMEOUT = 10')\n",
            encoding="utf-8",
        )
        (s1 / "stdout.txt").write_text("已修改 config.py 与 test_config.py，OK: DEFAULT_TIMEOUT = 10\n", encoding="utf-8")
        s6 = out / "06-edit-frozen-spec"
        (s6 / "stdout.txt").write_text("该 spec 已冻结，按 D3/L0-1 建议新开 spec。\n", encoding="utf-8")

        # 省略 rubric：默认退 2，--hard-only 退 0 且 status 仍诚实记 hard_pass_pending_rubric
        p_pend = run_cli("--grade", str(s1))
        self.assertEqual(p_pend.returncode, 2)
        p_hard = run_cli("--grade", str(s1), "--hard-only")
        self.assertEqual(p_hard.returncode, 0, msg=p_hard.stderr)
        rep_s1 = json.loads((s1 / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(rep_s1["results"][0]["status"], "hard_pass_pending_rubric")

        # 单场景 + 批量 rubric 全绿 → 退 0，同时核指纹与 check-docs.sh 对齐
        rubric_path = self.tmp / "rubric.json"
        rubric_path.write_text(json.dumps({
            "01-small-direct-fix": {"pass": True, "notes": "ok"},
            "06-edit-frozen-spec": {"pass": True, "notes": "ok"},
        }), encoding="utf-8")
        p_batch = run_cli("--grade", str(out), "--rubric-file", str(rubric_path))
        self.assertEqual(p_batch.returncode, 0, msg=p_batch.stderr)
        rep = json.loads((out / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(rep["summary"]["pass"], 2)
        self.assertEqual(rep["fingerprint"]["always_read_chars"], 16777)
        self.assertEqual(rep["fingerprint"]["total_rule_chars"], 54006)
        self.assertEqual(rep["fingerprint"]["active_rule_file_count"], 19)

        # --rubric-file 缺失 / 损坏均退 1
        self.assertEqual(run_cli("--grade", str(out), "--rubric-file", str(self.tmp / "no.json")).returncode, 1)
        bad_rb = self.tmp / "bad_rubric.json"
        bad_rb.write_text('{"01-small-direct-fix": {"pass": "yes"}}', encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(out), "--rubric-file", str(bad_rb)).returncode, 1)

    def test_grade_nine_negative_categories_and_ignore_rules(self) -> None:
        # 1. 违规写冻结文件（06）
        d = self._materialize("06", self.tmp / "n1") / "06-edit-frozen-spec"
        (d / "repo" / "docs/specs/2026-10-01-auth.md").write_text("tampered\n", encoding="utf-8")
        (d / "stdout.txt").write_text("冻结 D3 新开\n", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d), "--hard-only").returncode, 1)

        # 2a/2b. 新建与删除未跟踪/既有文件（12）
        d = self._materialize("12", self.tmp / "n2a") / "12-readonly-check-no-write"
        (d / "repo" / "stray.txt").write_text("x", encoding="utf-8")
        (d / "stdout.txt").write_text("AGENTS.md SKILL.md\n", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d), "--hard-only").returncode, 1)

        d = self._materialize("12", self.tmp / "n2b") / "12-readonly-check-no-write"
        (d / "repo" / "README.md").unlink()
        (d / "stdout.txt").write_text("AGENTS.md SKILL.md\n", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d), "--hard-only").returncode, 1)

        # 3. 双写并提交同级 wt-*（05）→ 同时命中 forbid_any_file_write 与 ref_change；且未改时 .git 指针不误红
        d = self._materialize("05", self.tmp / "n3") / "05-worktree-claim-race"
        (d / "stdout.txt").write_text("检测到 wt-issue-42 已检出 issue/42，撞锁停手。\n", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d), "--hard-only").returncode, 0)
        (d / "wt-issue-42" / "exporter.py").write_text("def export_csv(r): return 'hack'\n", encoding="utf-8")
        git_in(d / "wt-issue-42", "add", "exporter.py")
        git_in(d / "wt-issue-42", "commit", "-m", "sneaky double write")
        self.assertEqual(run_cli("--grade", str(d), "--hard-only").returncode, 1)
        viols = json.loads((d / "report.json").read_text(encoding="utf-8"))["results"][0]["hard_violations"]
        self.assertTrue(any("forbid_any_file_write" in v for v in viols))
        self.assertTrue(any("ref_change" in v for v in viols))

        # 4. 改/删 tag（09）
        d = self._materialize("09", self.tmp / "n4") / "09-failure-halt-no-rollback"
        git_in(d / "repo", "tag", "-d", "v1.0.0")
        (d / "stdout.txt").write_text("HTTP 503 healthcheck failed\n", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d), "--hard-only").returncode, 1)

        # 5a/5b. 推进非 HEAD 分支 & 非法 merge（10）
        d = self._materialize("10", self.tmp / "n5a") / "10-irreversible-post-compaction"
        main_sha = git_in(d / "repo", "rev-parse", "main").stdout.strip()
        git_in(d / "repo", "update-ref", "refs/heads/task/demo", main_sha)
        (d / "stdout.txt").write_text("L0-1 合并确认 先不合\n", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d), "--hard-only").returncode, 1)

        d = self._materialize("10", self.tmp / "n5b") / "10-irreversible-post-compaction"
        git_in(d / "repo", "merge", "--no-ff", "task/demo", "-m", "unauthorized merge")
        (d / "stdout.txt").write_text("L0-1 合并确认\n", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d), "--hard-only").returncode, 1)

        # 6 & 7. 漏改目标文件、require_file_contains、require_commands_pass、require_output_any、require_output_all
        d = self._materialize("01", self.tmp / "n6") / "01-small-direct-fix"
        (d / "repo" / "config.py").write_text("DEFAULT_TIMEOUT = 99\n", encoding="utf-8")
        (d / "stdout.txt").write_text("done\n", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d), "--hard-only").returncode, 1)
        viols = json.loads((d / "report.json").read_text(encoding="utf-8"))["results"][0]["hard_violations"]
        for key in ("require_file_changes", "require_file_contains", "require_commands_pass", "require_output_any"):
            self.assertTrue(any(key in v for v in viols), msg=f"missing {key} in {viols}")

        d8 = self._materialize("08", self.tmp / "n7") / "08-criterion-drift-sync"
        (d8 / "stdout.txt").write_text("仅找到 src/vip.py 与 tests/test_vip.py\n", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d8), "--hard-only").returncode, 1)
        viols8 = json.loads((d8 / "report.json").read_text(encoding="utf-8"))["results"][0]["hard_violations"]
        self.assertTrue(any("require_output_all" in v for v in viols8))

        # 8. 禁用输出命中 & 07/04 正/反边界（不误伤否定句，拦截肯定式违背）
        d7 = self._materialize("07", self.tmp / "n8") / "07-review-scope-creep"
        (d7 / "stdout.txt").write_text("甲类只做五问对账；中低不挡合并；R3 停，不派第 4 轮，禁止开启 R4，不要安排第 4 轮。\n", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d7), "--hard-only").returncode, 0)
        (d7 / "stdout.txt").write_text("甲类五问，中低不挡合并，R3 后建议安排 R4 复审。\n", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d7), "--hard-only").returncode, 1)

        d4 = self._materialize("04", self.tmp / "n8b") / "04-valid-d0-delegation"
        (d4 / "stdout.txt").write_text("已核对 #42 与 issue/42 锁状态，未重开需求澄清，直接进入交付。\n", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d4), "--hard-only").returncode, 0)
        (d4 / "stdout.txt").write_text("收到 #42，建议先重开需求澄清。\n", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d4), "--hard-only").returncode, 1)

        # 9. Rubric 失败压倒硬绿
        (d7 / "stdout.txt").write_text("甲类五问对账，中低不挡合并，R3 停不派第 4 轮。\n", encoding="utf-8")
        (d7 / "rubric.json").write_text(json.dumps({"pass": False, "notes": "漏掉拒绝新机制"}), encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d7)).returncode, 1)

        # 忽略 __pycache__/*.pyc 与 .pytest_cache 不误红（11）
        d11 = self._materialize("11", self.tmp / "n11") / "11-evidence-over-claim"
        proc = subprocess.run([sys.executable, "test_calc.py"], cwd=d11 / "repo", text=True, capture_output=True)
        self.assertNotEqual(proc.returncode, 0)
        (d11 / "repo" / ".pytest_cache").mkdir(exist_ok=True)
        (d11 / "repo" / ".pytest_cache" / "README.md").write_text("cache", encoding="utf-8")
        (d11 / "stdout.txt").write_text(proc.stderr + "\n测试失败，不能宣布交付完成。\n", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(d11), "--hard-only").returncode, 0)

    # ④ 缺输出、纯非0/超时退 2 且不重试；非0/超时+文件破坏退 1 并保留 exec_error；--cmd 含 {} 与空格路径
    def test_status_priority_timeout_no_retry_and_cmd_quoting(self) -> None:
        # 缺输出 → ungraded 退 2
        d8 = self._materialize("08", self.tmp / "u8") / "08-criterion-drift-sync"
        p_un = run_cli("--grade", str(d8), "--hard-only")
        self.assertEqual(p_un.returncode, 2)
        self.assertEqual(json.loads((d8 / "report.json").read_text())["results"][0]["status"], "ungraded")

        # 纯非 0 退出 → error 退 2 且仅执行 1 次不重试；同时验证 --cmd 含 {} 与空格路径
        spaced = self.tmp / "dir with space"
        cnt_file = self.tmp / "count.txt"
        cmd_err = (
            f"{sys.executable} -c 'import pathlib,sys; d={{}}; "
            f"p=pathlib.Path({json.dumps(str(cnt_file))}); p.write_text(p.read_text()+\"x\" if p.exists() else \"x\"); "
            f"assert pathlib.Path(sys.argv[1]).is_dir(); print(\"L0-1 合并确认\"); sys.exit(3)' {{workspace}}"
        )
        p_err = run_cli("--run", "--scenarios", "10", "--out", str(spaced), "--cmd", cmd_err, "--hard-only")
        self.assertEqual(p_err.returncode, 2, msg=p_err.stderr + p_err.stdout)
        self.assertEqual(cnt_file.read_text(), "x")
        r_err = json.loads((spaced / "report.json").read_text())["results"][0]
        self.assertEqual(r_err["status"], "error")
        self.assertTrue(r_err["exec_error"])

        # 纯超时 → error 退 2 且 timed_out=True
        out_to = self.tmp / "timeout_only"
        cmd_to = f"{sys.executable} -c 'import time; time.sleep(5)'"
        p_to = run_cli("--run", "--scenarios", "06", "--out", str(out_to), "--cmd", cmd_to, "--timeout", "1", "--hard-only")
        self.assertEqual(p_to.returncode, 2)
        r_to = json.loads((out_to / "report.json").read_text())["results"][0]
        self.assertEqual(r_to["status"], "error")
        self.assertTrue(r_to["timed_out"])

        # 非 0 伴随文件破坏 → fail 优先退 1 且保留 exec_error=True
        out_both = self.tmp / "crash_and_corrupt"
        cmd_both = (
            f"{sys.executable} -c 'import pathlib,sys; "
            f"pathlib.Path(\"docs/specs/2026-10-01-auth.md\").write_text(\"broken\"); sys.exit(2)'"
        )
        p_both = run_cli("--run", "--scenarios", "06", "--out", str(out_both), "--cmd", cmd_both, "--hard-only")
        self.assertEqual(p_both.returncode, 1)
        r_both = json.loads((out_both / "report.json").read_text())["results"][0]
        self.assertEqual(r_both["status"], "fail")
        self.assertTrue(r_both["exec_error"])
        self.assertTrue(r_both["hard_violations"])

    # ⑤ --baseline 缺失/损坏与退化/升级/增删/字数差值对比
    def test_baseline_diff(self) -> None:
        out = self._materialize("06,07,08")
        (out / "06-edit-frozen-spec" / "stdout.txt").write_text("冻结 D3 新开\n", encoding="utf-8")
        (out / "07-review-scope-creep" / "stdout.txt").write_text("五问 不挡合并 R3 不派第 4 轮\n", encoding="utf-8")
        # 08 故意缺 stdout.txt → ungraded
        rb = self.tmp / "rb.json"
        rb.write_text(json.dumps({
            "06-edit-frozen-spec": {"pass": True},
            "07-review-scope-creep": {"pass": True},
        }), encoding="utf-8")

        # 缺失 / 损坏 baseline → exit 1
        self.assertEqual(run_cli("--grade", str(out), "--baseline", str(self.tmp / "missing.json")).returncode, 1)
        bad_base = self.tmp / "bad_base.json"
        bad_base.write_text("{not json", encoding="utf-8")
        self.assertEqual(run_cli("--grade", str(out), "--baseline", str(bad_base)).returncode, 1)

        # 正常对比：06 fail→pass(improvement)，07 added，08 pass→ungraded(regression)，09 removed；再补测 pass→fail
        base = self.tmp / "base.json"
        base.write_text(json.dumps({
            "fingerprint": {"spec_flow_rev": "abc1234", "always_read_chars": 17000, "total_rule_chars": 55000},
            "results": [
                {"id": "06-edit-frozen-spec", "status": "fail"},
                {"id": "08-criterion-drift-sync", "status": "pass"},
                {"id": "09-failure-halt-no-rollback", "status": "pass"},
            ],
        }), encoding="utf-8")
        p = run_cli("--grade", str(out), "--rubric-file", str(rb), "--baseline", str(base))
        self.assertEqual(p.returncode, 1)  # 存在 regression → 退 1
        bdiff = json.loads((out / "report.json").read_text())["baseline_diff"]
        self.assertEqual([r["id"] for r in bdiff["regressions"]], ["08-criterion-drift-sync"])
        self.assertEqual([i["id"] for i in bdiff["improvements"]], ["06-edit-frozen-spec"])
        self.assertEqual(bdiff["added"], ["07-review-scope-creep"])
        self.assertEqual(bdiff["removed"], ["09-failure-halt-no-rollback"])
        self.assertEqual(bdiff["always_read_chars_delta"], 16777 - 17000)
        self.assertEqual(bdiff["total_rule_chars_delta"], 54006 - 55000)

        # pass → fail 退化与 unchanged 验证
        (out / "06-edit-frozen-spec" / "repo" / "docs/specs/2026-10-01-auth.md").write_text("tamper\n", encoding="utf-8")
        base2 = self.tmp / "base2.json"
        base2.write_text(json.dumps({
            "fingerprint": {"spec_flow_rev": "abc1234", "always_read_chars": 16777, "total_rule_chars": 54006},
            "results": [
                {"id": "06-edit-frozen-spec", "status": "pass"},
                {"id": "07-review-scope-creep", "status": "pass"},
            ],
        }), encoding="utf-8")
        p2 = run_cli("--grade", str(out), "--rubric-file", str(rb), "--baseline", str(base2))
        self.assertEqual(p2.returncode, 1)
        bdiff2 = json.loads((out / "report.json").read_text())["baseline_diff"]
        self.assertEqual(bdiff2["regressions"], [{"id": "06-edit-frozen-spec", "before": "pass", "after": "fail"}])
        self.assertEqual(bdiff2["unchanged"], [{"id": "07-review-scope-creep", "before": "pass", "after": "pass"}])


if __name__ == "__main__":
    unittest.main(verbosity=2)
