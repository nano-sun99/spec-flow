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
验收：11 条 fixture 全绿且故意改坏一支能红；中英 README 各一张 1–9 步图、节标记对齐；main 上 `spec-check --base HEAD~1` 转绿，新增普通文件仍红。

改：README.md、README.zh-CN.md、scripts/spec-check.py、tests/
不改：SKILL.md、references/、docs/specs 下既有 spec

| # | 验收 | 怎么验 |
|---|---|---|
| AC1 | 11 条坏样本固化进仓，逐条断言 exit code 与 E2 / E5 输出 | `python3 tests/test_spec_check.py` exit 0 |
| AC2 | 解析分支被改坏时测试能红 | 临时删掉噪声判断与 `strip_inline`，测试 exit 1 |
| AC3 | E5 跳过 5 个噪声目录，只跳 untracked 一侧 | 用例三条：`.idea/` 绿、`src/new.py` 红、tracked 改动仍红 |
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
| 坏样本进仓 | 新增 `tests/spec-check/` 11 条 fixture + `tests/test_spec_check.py`（unittest，零依赖） | 解析分支被改坏当场红；没有它：回归靠人记得 /tmp 里跑过什么 |
| 两段看得见 | 中英 README 各加一节「两段怎么走」，带 `s:route` 标记，图里点名 1–9 | 不再被读成单段直线；没有它：同一阻断会复发 |
| 噪声不冒充越界 | `scripts/spec-check.py` 的 `parse_diff` 收集 `??` 时跳过 `.idea/` `.vscode/` `__pycache__/` `node_modules/` `.worktrees/`；tracked diff 不动 | main 上 E5 转绿；没有它：E5 恒红 = 越界闸失效 |
| 行内代码不算内容 | `parse_ac` 对表格行先剥行内代码再判 `❌` 与处置 | 写法一致：bullet 与表格同一口径 |

## 4. 不做

- 不重开 #134 的 spec，不改 1–9 步语义，不动 `references/` 的 17 份规则。
- 不加 CI、不加新章节、不把测试接进 `check-docs.sh`（文档检查只管文档）。
- 不清理 `.idea/` 本身，也不加进 `.gitignore`——脚本侧跳过就够，别人仓里的同名噪声一并受益。

## 5. 验收

- `python3 tests/test_spec_check.py` 全绿（11 条）。
- 故意改坏解析分支（去掉噪声判断 / 去掉 `strip_inline`）时测试变红。
- `bash scripts/check-docs.sh` 绿（双语节标记 15 / 15）。
- `python3 scripts/spec-check.py docs/specs/2026-11-04-suggestion-pool.md --base main` 绿。
- 在 main 工作区复核：`--base HEAD~1` 不再因 `?? .idea/` 红，新增 `src/new.py` 仍红。
