---
name: spec-flow-v2
description: "v2 草案入口（默认不启用）。用户明确说「按 v2 走」或指定读 references/v2/SKILL.md 时才使用。"
---

# spec-flow v2（草案）

- **是什么**：一个决策环境，不是流程编译器。给出五层知识（铁律 → 阶段合同 → 决策目录 → playbook → 案例），由 agent 按当前事实自选路径。
- **何时用**：只有用户显式点名 v2 才加载。P0-P6 期间 v1（根 `SKILL.md` + 旧 `references/`）仍是默认运行权威；两个入口若拿到不同权威，停，报告，由用户指定。
- **硬闸**：D0-D7 八类用户决定（实施委托、范围与结构、设计确认、spec 合并、每份 PR 的两个时点〔审核档位 / 合并〕、整条 issue 合入 staging、生产发布、回滚）。这八类必须停；八类之外遇到 L0-7 承重缺口，走异常协议停。
- **需求澄清由 v2 自己完成**：`grill-me`、`grilling`、`grilling-cards`、Superpowers 的 `brainstorming`、`writing-plans` 及同类技能都不是本流程的依赖。即使客户端列出了它们，也不去查找、读取、调用、推荐或提示安装。缺写文件等项目工具时只报告实际限制，不去读技能找替代路径，不改其他文件充当交付。
- **v1/v2 冲突**：v2 任务内同时读 v1 与 v2 时，**v2 铁律与入口优先**；v1 保留三类用途——项目采用只按 [v2 接入边界](50-adapters/README.md) 借用 v1 说明；v2 playbook 明确指向的 v1 操作细则（如 issue-type 迁移、release 历史操作）按该处引用；历史档案按需查。两处对同一动作给出不同要求，按 v2，并报告「v1 与 v2 不一致：<一句>」。不静默二选一。

## 运行循环

```
读事实 → 定阶段 → 出计划（按触发）→ 执行
   ↑                                    ↓
   └── 异常协议 ←── 硬闸摆证据 ←────────┘
```

1. **读事实**：核项目指令、用户原话、获批材料、issue、分支、标签、证据与锁。已定项只引用来源，不出澄清卡。规则里的例子不是本项目的决定：项目材料写「范围待定」就仍是待定；明确写了范围、已过滤的输入或表头，就照用，不要求用户重新选。
2. **定阶段**：这一单从哪段进、到哪段出；直接干可跳过澄清/设计。
3. **出计划（按触发）**：新任务且范围不平凡、即将不可逆、预计问用户超过 3 次，任一成立就在执行前摆原生计划卡。卡上陈述改动面与验收，选项只涉及「确认计划 / 调整计划」，不提供「确认并实施」或用委托卡顶替。按已批准口径同步多个交付物也适用；没有实施委托，确认后只记录计划，不改实现。未触发时一句说明即可，不另编实施计划。
4. **执行**：只执行已有授权的动作。需要用户决定时按下方「异常协议」交互；范围选择、送审、合并、实施与数据访问各自有效，不能捆绑。
5. **异常**：按下方协议区分能自定的做法与须由用户回答的缺口。
6. **收尾**：只有发生了「改变了什么行为」或「教了什么失败」才写案例；普通任务不写。只有发现铁律缺一条才提议替换/合并一条，否则只记案例。

## 五层导航（一跳）

| 层 | 入口 | 内容 |
|---|---|---|
| L0 铁律（≤60 行） | [00-constitution.md](00-constitution.md) | 8 条铁律 |
| L1 阶段合同（≤200 行） | [10-stages.md](10-stages.md) | 4 段完成条件 + 证据 + 出口 |
| L1 记录 | [15-records.md](15-records.md) | 15 类记录 + 关单收尾 + 观察式例外 |
| L2 决策目录（≤100 行） | [20-decisions.md](20-decisions.md) | D0-D7、标签规则、观察式例外 |
| L3 playbook（示例非必须） | [new-spec](30-playbooks/new-spec.md) · [spec](30-playbooks/spec.md) · [direct](30-playbooks/direct.md) · [issue](30-playbooks/issue.md) · [review](30-playbooks/review.md) · [release](30-playbooks/release.md) · [hotfix](30-playbooks/hotfix.md) · [rollback](30-playbooks/rollback.md) · [batch-fix](30-playbooks/batch-fix.md) · [main-snapshot](30-playbooks/main-snapshot.md) · [labels](30-playbooks/labels.md) · [worktree](30-playbooks/worktree.md) · [adr](30-playbooks/adr.md) | 9 核心 + 4 支撑 |
| L4 案例（≤15 条） | [INDEX](40-cases/INDEX.md) · [09-11](40-cases/2026-09-11-criterion-sync.md) · [09-16](40-cases/2026-09-16-claim-race.md) · [09-22 拆](40-cases/2026-09-22-split-semantic-deps.md) · [09-22 副本](40-cases/2026-09-22-copy-drift.md) · [09-26](40-cases/2026-09-26-rule-bloat.md) · [10-04](40-cases/2026-10-04-merged-spec-edit.md) · [10-06](40-cases/2026-10-06-long-tail-close.md) · [10-15](40-cases/2026-10-15-adoption-contract.md) · [10-17 地图](40-cases/2026-10-17-code-map.md) · [10-17 假绿](40-cases/2026-10-17-false-green.md) · [10-24](40-cases/2026-10-24-no-delegation.md) · [11-03 发布](40-cases/2026-11-03-release-unclear.md) · [11-03 顺序](40-cases/2026-11-03-spec-order.md) · [11-07](40-cases/2026-11-07-review-scope-explosion.md) · [11-11](40-cases/2026-11-11-staging-drill.md) | 叙述 + 提议，不是法条 |
| 项目接入 | [50-adapters/README.md](50-adapters/README.md) | 5 个选修模块与只指向式契约 |

阅读顺序见 [README.md](README.md)：L0 → L1 → L2 → L3 → L4。

## 异常协议

- 先查 L0-L2 落点，再查 L3 playbook、L4 案例，并核实际事实（`file:line`、diff、锁、证据）。
- 只有不需用户决定的可逆做法才可用安全默认。遇到不可逆、无安全默认、多 owner 或承重缺口，按 L0-7 停；只问影响本次任务的问题，不把假设的新功能列为选项。
- **需要答案时**（含计划卡）：客户端有选项卡工具，就实际调用它（如 `ask_user_question`）；没有该工具才在正文列等价选项。给 2–3 个可行选项与推荐，说明差别并允许自填。例如范围未定就问「仅本人 / 全组」，不同时索要取数授权。
- **卡片未答或取消**：记待定，结束本次提问，停住依赖该答案的动作；不再用文字重问或按推荐项执行。已有答复只记录实际选择或补充，不产生其他授权。没有实际工具结果或产物，不报告已执行。
- 失败、崩溃、监控异常：停住上报，不自动回滚、不静默重试（L0-4）。

## 重读触发

任何不可逆动作前，重读 L0-1 与当次决策卡；长任务被压缩后，不假设自己还记得铁律。

## 边界

- P8 前根 `SKILL.md` 不动；v2 只在用户显式点名时使用。
- 本文件只做入口与导航，不写步骤、不新增规则；各层各有唯一 owner。
- 需求已有明确实施委托时从交付段接手，不重开访谈或另写规格。
