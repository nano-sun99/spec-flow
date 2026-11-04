# spec：#135 审核建议池三件收尾

- 日期：2026-11-04
- Issue：#135
- 状态：实施版（小 PR 一次收完）
- 决策人：用户
- 决策来源：2026-11-04 对话。用户原话「干」。
- 结构：**不拆**（1 份 spec、1 个 PR）
- 基线：`main@75ff76f`（#134 已合并，R2 28/28 闭合）

目标：把 #134 审核剩下的三条建议（固定坏样本、1–9 步图、E5 忽略 untracked 噪声）在一个 PR 内收掉，三条验收全绿。
不做：不改 1–9 步语义；不动 17 份场景包规则；不加新流程、不新增章节；不接 CI。
验收：11 条用例（10 份 fixture）全绿，故意改坏任一支解析分支能红；中英 README 各一张 1–9 步图、节标记对齐；main 上 `spec-check --base HEAD~1` 转绿，新增普通文件仍红。

改：README.md、README.zh-CN.md、scripts/spec-check.py、tests/
不改：SKILL.md、references/、docs/specs 下既有 spec

| # | 验收 | 怎么验 |
|---|---|---|
| AC1 | 10 份 fixture / 11 条用例固化进仓，逐条断言 exit code 与 E2 / E5 输出 | `python3 tests/test_spec_check.py` exit 0 |
| AC2 | 解析分支被改坏时测试能红 | 临时删掉噪声判断与 `strip_inline`，测试 exit 1 |
| AC3 | E5 跳过 5 个噪声目录，只跳 untracked 一侧 | 5 个目录逐个绿；`src/new.py` 红；tracked 改动仍红 |
| AC4 | 图与 `SKILL.md` 的 1–9 步逐项对应，双语节标记一一对应 | 逐项点名 1–9；`bash scripts/check-docs.sh` 绿 |
| AC5 | 两项全局检查绿 | `check-docs.sh` 绿；`spec-check --base main` 绿 |

## 1. 背景

#134 把默认面瘦成 3 份常驻 + `spec-check`，R2 28/28 闭合。审核建议池剩三条，都不阻塞，单独收：

1. 这次审核用过的 11 个反例只在 /tmp 里跑过，没进仓——脚本被改坏没人发现。
2. 五步把两段压成一条直线是这次唯一的阻断，README 缺一张 1–9 步图。
3. 本仓 `.idea/` 未跟踪，`spec-check --base` 在 main 上恒红，是误报。

## 2. 实测现状（基线）

- 在 main 上跑 `python3 scripts/spec-check.py docs/specs/2026-11-04-slim-default-surface.md --base HEAD~1`：`E5 | 红 | 越界：.idea/`，exit 1——噪声目录让 E5 永远红，越界检查形同失效。
- 表格「结果」列写成行内代码 `` `❌` `` 时 `E2` 仍判红：`parse_ac` 对表格行没剥行内代码（bullet 那支已剥）。11 条 fixture 会把它抓出来，本次一并修。

## 3. 方案

| 改什么 | 改哪里 | 得到什么 / 没有会怎样 |
|---|---|---|
| 坏样本进仓 | 新增 `tests/spec-check/` 10 份 fixture / 11 条用例 + `tests/test_spec_check.py`（unittest，零依赖） | 解析分支被改坏当场红；没有它：回归靠人记得 /tmp 里跑过什么 |
| 两段看得见 | 中英 README 各一张路线图，图里点名 1–9（并入「两段怎么转」，见 §6） | 不再被读成单段直线；没有它：同一阻断会复发 |
| 噪声不冒充越界 | `scripts/spec-check.py` 的 `parse_diff` 收集 `??` 时跳过 `.idea/` `.vscode/` `__pycache__/` `node_modules/` `.worktrees/`；tracked diff 不动 | main 上 E5 转绿；没有它：E5 恒红 = 越界闸失效 |
| 行内代码不算内容 | `parse_ac` 对表格行先剥行内代码再判 `❌` 与处置 | 写法一致：bullet 与表格同一口径 |

## 4. 不做

- 不重开 #134 的 spec，不改 1–9 步语义，不动 `references/` 的 17 份规则。
- 不动常驻面（`SKILL.md` / `references/`），不新增章节——图并入既有节。
- 不加 CI、不把测试接进 `check-docs.sh`（文档检查只管文档）。
- 不清理 `.idea/` 本身，也不加进 `.gitignore`——脚本侧跳过就够，别人仓里的同名噪声一并受益。

## 5. 验收

- `python3 tests/test_spec_check.py` 全绿（10 份 fixture / 11 条用例）。
- 故意改坏解析分支时测试变红：噪声判断、`strip_inline`、锚常量、`~~~` 围栏、占位符、`怎么验` 表头共 6 支。
- `bash scripts/check-docs.sh` 绿（双语节标记 14 / 14）。
- `python3 scripts/spec-check.py docs/specs/2026-11-04-suggestion-pool.md --base main` 绿。
- 在 main 工作区复核：`--base HEAD~1` 不再因 `?? .idea/` 红，新增 `src/new.py` 仍红。

## 6. 审核与合并记录

- **轻审**（用户点档）：1 个审核员（agent 派出，非独立第三方），5 / 5 过、0 阻断、范围外 0 条；建议池 4 条见 PR #136 评论。
- **合并**：PR #136 → `824263b`。合并后发现 #137 重写的 README 已有同主题一节，PR #138 → `824b7f0` 把路线图并入「两段怎么转」并删掉重复节；**最终没有新增章节**，节标记 15 → 14。
- **建议池收尾**（本 PR）：4 条全收——5 个噪声目录逐个建用例并与脚本常量对表；变异从 2 支扩到 6 支；本 spec 措辞与计数按最终状态修正；「11 条 fixture」改为「10 份 fixture / 11 条用例」。
