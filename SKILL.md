---
name: spec-flow
description: "Use when 用户提出值得先设计的复杂需求、要求实施既有 issue（如请做 #N）、接续未完成规格或 PR，或要求应用、更新项目的 spec-flow 接入。"
---

# spec-flow

- **定位**：决策环境，非流程编译器。五层知识（铁律 → 阶段合同 → 决策目录 → 专项总纲 / Playbook → 案例）按事实自选路径。
- **硬闸**：D0–D7（[20-decisions](references/20-decisions.md)）+ L0-1 不可逆 + L0-7 承重缺口。
- **澄清自主完成**：禁查、读、调用、推荐或提示安装 `grill-me`、`grilling`、`grilling-cards`、`brainstorming`、`writing-plans` 等外部技能（客户端列出亦不调）。缺工具只报限制，不改他文件充数。

## 运行循环

先核用户原话、项目事实、获批材料与分支 / issue / 锁；示例不构成本项目决定。

| 本轮任务 | 下一步 |
|---|---|
| 只读检查 / 核既有结果 / 设计对照 | 核完直接交付结束，不写入或安装 |
| 完善现稿，仅缺单个承重决定 | 发业务选项卡问该项，答后回写；选范围不授权写入 |
| 明确小改或已有实施委托 | 一句说明改动面后执行验证；替换式变更走 [change-protocol](references/30-playbooks/change-protocol.md) |
| 新需求不平凡、触不可逆或问超 3 次 | 按 [交互卡片契约](references/20-decisions.md#交互卡片契约) 发计划卡；确认不代实施委托 |

执行前核写入对象（导出时源只读），实际产出才报成功；已有实施委托直入交付段，不重开访谈。

## 导航（一跳）

读序：L0 → L1 → L2 每次必读；专项总纲与 L3 按需读；L4 缺落点或遇异常时查。

| 层 | 入口 | 职责 |
|---|---|---|
| 地图 | [README](references/README.md) | 文件地图与读序 |
| L0 | [00-constitution](references/00-constitution.md) | 8 条铁律（冲突最高优先） |
| L1 | [10-stages](references/10-stages.md) | 4 段完成条件、术语与交付前置 |
| L1 | [15-records](references/15-records.md) | 15 类记录、留痕、载体、关单与例外 |
| L2 | [20-decisions](references/20-decisions.md) | D0–D7 硬闸、卡片契约与标签确认 |
| 总纲 | [25-spec-governance](references/25-spec-governance.md) · [26-review-contract](references/26-review-contract.md) | 规格治理（底座 / 3 组件 / 平滑升级）与审核契约（Lane A/B） |
| L3 | [new-spec](references/30-playbooks/new-spec.md) · [direct](references/30-playbooks/direct.md) · [issue](references/30-playbooks/issue.md) · [change-protocol](references/30-playbooks/change-protocol.md) · [release](references/30-playbooks/release.md) · [incident](references/30-playbooks/incident.md) · [labels](references/30-playbooks/labels.md) · [worktree](references/30-playbooks/worktree.md) · [adr](references/30-playbooks/adr.md) | 9 条按需走法（标「规范性」为该领域唯一正文） |
| L4 | [40-cases/INDEX](references/40-cases/INDEX.md) | 15 条案例（非授权依据） |
| 接入 | [50-adapters/README](references/50-adapters/README.md) | 5 选修与只指向式接入契约 |

## 异常协议与重读

- 先查 L0–L2、总纲、L3/L4 与事实（`file:line`、diff、锁、证据）；可逆无决策做法用安全默认并报告；遇不可逆 / 无安全默认 / 多 owner / 承重缺口按 L0-7 停并给 2–3 选项与推荐。
- 未答 / 取消见 [交互卡片契约](references/20-decisions.md#交互卡片契约)；失败 / 崩溃 / 异常按 L0-4 停报。不可逆前重读 L0-1 与当次卡；长会话压缩后重读铁律。改行为或现新失败模式才写案例；铁律缺项只提议替换或合并（L0-8）。
