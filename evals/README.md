# spec-flow 行为级 Eval 回归套件

本目录是 `spec-flow` 行为级回归评测的唯一现状文档与夹具落点（设计规格见 [2026-11-26-behavioral-eval-harness.md](../docs/specs/2026-11-26-behavioral-eval-harness.md)）。本文件只记录 Eval 用法、指标口径与 A/B 对比流程，不复述 `SKILL.md` 或 `references/` 规则正文。

## 目录结构

| 路径 | 职责 |
|---|---|
| `evals/scenarios/01..12.json` | 12 条单文件自足场景（9 条 `guardrail` + 3 条 `anti-bloat`），运行时物化到临时目录 |
| `evals/baselines/` | 脱敏基线报告（JSON + Markdown），用于规则修改前后的行为退化与字数对比 |
| `scripts/run-eval.py` | 纯 Python 3（≥ 3.9）标准库、CLI 无关 Runner |
| `scripts/test-run-eval.py` | 确定性单测（零模型调用），验证校验、物化、硬断言判别性与基线对比 |

## 常用命令

```bash
# 1. 静态校验全部场景 schema、规则/案例锚点可达性与临时物化自检
python3 scripts/run-eval.py --validate

# 2. 物化全部或单条场景到临时目录（支持完整 ID、唯一数字前缀或 all）
python3 scripts/run-eval.py --materialize all --out /tmp/spec-flow-eval-run --force
python3 scripts/run-eval.py --materialize 01 --out /tmp/spec-flow-eval-01 --force

# 3. 批量调用任意外部 agent CLI 并自动评分（占位符自动 shlex.quote，勿外包引号）
python3 scripts/run-eval.py --run \
  --cmd 'my-agent-cli --cwd {workspace} --prompt-file {prompt_file}' \
  --out /tmp/spec-flow-eval-run --timeout 180 \
  --baseline evals/baselines/2026-11-26-v2-baseline.json

# 4. 手工或子 agent 执行后，对目录做双层评分与基线对比
python3 scripts/run-eval.py --grade /tmp/spec-flow-eval-run \
  --rubric-file /tmp/spec-flow-eval-run/rubric.json \
  --baseline evals/baselines/2026-11-26-v2-baseline.json

# 5. 仅按确定性硬断言验绿（无 rubric 时退出码 0 需显式传 --hard-only）
python3 scripts/run-eval.py --grade /tmp/spec-flow-eval-run --hard-only

# 6. 跑确定性单测
python3 scripts/test-run-eval.py
```

`--run --cmd` 支持 4 个固定字面占位符：`{workspace}`、`{prompt_file}`、`{skill_dir}`、`{scenario_id}`（Runner 对每个替换值自动执行 `shlex.quote`，同时注入同名 `EVAL_*` 环境变量）。

## 指标、状态与退出码口径

- **规则树指纹**（与 `scripts/check-docs.sh` 同口径）：
  - `always_read_chars`：`SKILL.md` 去 frontmatter 正文 + `references/{00,10,15,20}` 字符数。
  - `total_rule_chars` 与 `rule_tree_sha256`：`SKILL.md` 全文 + 排序后的 `references/**/*.md`（排除 `references/40-cases/**`）。
  - `spec_flow_rev`：当前 `git HEAD` 提交 SHA（有未提交变更时附 `-dirty`）。
- **双层判定状态优先级（高 → 低）**：`fail > error > ungraded > hard_pass_pending_rubric > pass`。
  - 任一硬断言违规或 Rubric 失败记 `fail`（即使伴随子进程超时或非 0 退出，仍保留 `exec_error`/`timed_out` 事实）。
  - 未提供 Rubric 时记 `hard_pass_pending_rubric`，绝不标注为完整 `pass`。
- **退出码优先级**：`1`（任一 `fail`、基线存在 `regressions`、参数/schema/文件损坏） > `2`（`error`、`ungraded`，或未传 `--hard-only` 时存在 `hard_pass_pending_rubric`） > `0`（全部双层 `pass` 且零退化，或 `--hard-only` 全硬绿且零退化）。

## A/B 改动对照流程（用于后续规则瘦身 / 迭代）

1. 改规则前确认已有干净基线（如 `evals/baselines/2026-11-26-v2-baseline.json`）。
2. 在独立分支 / worktree 改完规则后，跑 `bash scripts/check-docs.sh` 与 `python3 scripts/run-eval.py --validate`。
3. 物化全部 12 场景，在相同执行环境下跑完并产出每条场景的 `stdout.txt` 与人工/结构化 `rubric.json`。
4. 执行 `python3 scripts/run-eval.py --grade <out> --rubric-file <rubric.json> --baseline evals/baselines/2026-11-26-v2-baseline.json`。
5. 核对 `regressions == []` 以及 `always_read_chars_delta` / `total_rule_chars_delta`；任何 `guardrail` 或 `anti-bloat` 退化即停止合并并查原因。
