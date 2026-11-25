---
name: spec-flow
description: "Use when 用户提出值得先设计的复杂需求、要求实施既有 issue（如请做 #N）、接续未完成规格或 PR，或要求应用、更新项目的 spec-flow 接入。"
---

# spec-flow

- **是什么**：决策环境，不是流程编译器。提供五层知识（铁律 → 阶段合同 → 决策目录 → 专项总纲 / Playbook → 案例），由 agent 按当前事实自选路径。
- **硬闸**：D0–D7 八类用户决定（[20-decisions](references/20-decisions.md)）；八类之外遇到 L0-1 不可逆动作或 L0-7 承重缺口同样停。
- **需求澄清自主完成**：不查找、读取、调用、推荐或提示安装 `grill-me`、`grilling`、`grilling-cards`、`brainstorming`、`writing-plans` 或同类外部技能；即使客户端列出它们也不调用。缺写文件等工具时只报告实际限制，不改其他文件充当交付。

## 运行循环

先核用户原话、项目事实、获批材料与适用的分支、issue、锁；指南里的举例不构成本项目决定。

| 本轮实际任务 | 下一步动作 |
|---|---|
| 核对既有结果 / 只读检查 / 设计对照 | 满足要求或核对完成后直接交付并结束，不顺手写入或安装 |
| 完善现有需求稿，只缺单个承重决定 | 用业务选项卡问这一项，答后写回原稿；选范围不授权取数或写入 |
| 明确的小改或按已有实施委托交付 | 一句话说明改动面后执行并验证；涉及替换式变更走 [change-protocol](references/30-playbooks/change-protocol.md) |
| 新需求且范围不平凡、将触不可逆或预计问超 3 次 | 按 [交互卡片契约](references/20-decisions.md#交互卡片契约) 发计划卡；确认计划不替代实施委托 |

执行前核对写入对象：改现有文件就改指定对象，要求导出时源文件只作输入；实际产生产物才报成功。需求已有明确实施委托时直接从交付段接手，不重开访谈。

## 导航（一跳）

阅读顺序：L0 → L1 → L2 每次先读；专项总纲与 L3 按任务形态按需读；L4 仅在 L0–L2 无落点或遇异常时查。

| 层 | 入口 | 唯一职责 |
|---|---|---|
| 目录地图 | [README](references/README.md) | 文件地图与按需阅读说明 |
| L0 铁律 | [00-constitution](references/00-constitution.md) | 8 条铁律（冲突时最高优先） |
| L1 阶段合同 | [10-stages](references/10-stages.md) | 4 段完成条件、核心术语与交付前置 |
| L1 记录 | [15-records](references/15-records.md) | 15 类记录、授权拍板、载体读序、关单与例外 |
| L2 决策目录 | [20-decisions](references/20-decisions.md) | D0–D7 硬闸、交互卡片契约与标签确认 |
| 专项总纲 | [25-spec-governance](references/25-spec-governance.md) · [26-review-contract](references/26-review-contract.md) | 规格文档治理（索引 / 盘点表 / 权威顺序）与审核契约（Lane A/B） |
| L3 Playbook | [new-spec](references/30-playbooks/new-spec.md) · [direct](references/30-playbooks/direct.md) · [issue](references/30-playbooks/issue.md) · [change-protocol](references/30-playbooks/change-protocol.md) · [release](references/30-playbooks/release.md) · [incident](references/30-playbooks/incident.md) · [labels](references/30-playbooks/labels.md) · [worktree](references/30-playbooks/worktree.md) · [adr](references/30-playbooks/adr.md) | 9 条按需走法（示例非必须） |
| L4 案例 | [40-cases/INDEX](references/40-cases/INDEX.md) | 15 条事故与演练案例（非授权依据） |
| 项目接入 | [50-adapters/README](references/50-adapters/README.md) | 5 个选修模块与只指向式接入契约 |

## 异常协议与重读

- 先查 L0–L2、专项总纲、L3 / L4 与实际事实（`file:line`、diff、锁、证据）。
- 仅不需用户决定的可逆做法可用安全默认并报告；遇不可逆、无安全默认、多 owner 或承重缺口按 L0-7 停，给 2–3 个选项与推荐。
- 卡片未答或取消的处理按 [交互卡片契约](references/20-decisions.md#交互卡片契约)；失败、崩溃、监控异常按 L0-4 停住上报。
- 任何不可逆动作前重读 L0-1 与当次决策卡；长会话压缩后重读铁律，不凭记忆假设。
- 收尾仅在改变行为或揭示新失败模式时写案例；发现铁律缺项只提议替换或合并（L0-8）。
