---
name: spec-flow
description: "Use when 用户提出值得先设计的复杂需求、要求实施既有 issue（如请做 #N）、接续未完成规格或 PR，或要求应用、更新项目的 spec-flow 接入。"
---

# 复杂活的两段流程

**对用户是方案期、实施期两段；必要闸口严格，闸内方法灵活。** 本文件只识别入口、当前阶段和已采用模块，不另定义流程、卡片、交付或完成判据。正文按职责各有唯一 owner（依据：rationale R37）。

## 从当前入口读

- **新需求**：第 1 步调用 `grilling-cards` 澄清（模型可调用；不得用普通提问代替，不可用才退回手动并记录原因），再选直接干 / 开 spec；然后读 `references/one-path.md` 的方案期与 `references/gate-details.md` 的入口与方案闸口。已有效的选择不重问（依据：rationale R38）。
- **既有 issue / 实施委托**（如“请做 #N”）：读 issue、当前获批 spec 和项目指令；按 `references/gate-details.md` 识别授权，按 `references/phase-handoff.md` 留痕，再按 `references/worktree-lock.md` 认领。不重走新需求访谈。
- **续接未合并 spec / PR 或暂停任务**：从 `references/one-path.md` 核当前阶段事实；确认的适用范围和恢复条件见 `references/gate-details.md`，交接记录见 `references/phase-handoff.md`。
- **应用 / 更新项目接入**：读 `references/apply-to-project.md`，只处理获准的采用意图、指针和项目落点；不因普通任务补制度或自动迁移采用项目。

文件变更与锁、审核和合并、交付与关单分别读取对应正文；压缩后不可见或版本变化，动作前重读。源码、实际 diff 和相关测试用来核事实与影响，不由历史规格的现状断言代替。

## 导航与正文归属

项目目录、命名和明确约束依项目 `AGENTS.md` / `CLAUDE.md`；承重冲突报告来源，不擅自用中央规则覆盖。指南可替换，不能据此替用户批准或省略必要交付。

选修**默认关闭**：仅用户本次明确要求，或项目规则**声明已采用**时读取。已采用 ADR、文档生命周期等按其实际触发时点执行，不因结构重组新增制度。代码地图仍停用，仅明确试用 / 恢复时读。

| 文件 | 何时读 |
|---|---|
| `references/one-path.md` | 流程唯一正文：两段主线、定稿图、阶段事实与衔接 |
| `references/gate-details.md` | 闸口唯一正文：选项交互、可实施/送审、授权、审核、修订、合并及停止 |
| `references/phase-handoff.md` | 交付唯一正文：spec / issue / PR / 候选字段、来源与更新责任；授权留痕 |
| `references/done-criteria.md` | 完成唯一判据：必要证据、关单、观察式收尾与已批准例外 |
| `references/worktree-lock.md` | 文件变更、认领、撞锁、接管和放锁；Git 工作区安全 |
| `references/spec-maturity.md` | 方案期工作指南：骨架、设计/规则对照、终稿表达 |
| `references/split-large-spec.md` | 拆分工作指南：交付物、依赖、并行与稳定身份 |
| `references/spec-revision-sync.md` | 修订工作指南：定位并同步真实现行落点 |
| `references/apply-to-project.md` | 项目采用、显式升级、指针与资产边界；梳理技能依赖 |
| `references/adr-decision-records.md` | 选修 `adr`：调查、明确长期决定、收尾 |
| `references/documentation-lifecycle.md` | 选修 `doc-lifecycle`：现状/规格读序、载体分工 |
| `references/issue-status-labels.md` | 选修 `issue-status`：阶段标签、分拣和下次看 |
| `references/issue-type-labels.md` | 选修 `issue-type`：开单类型及获准迁移 |
| `references/release-discipline.md` | 选修 `release`：Git 分支形态映射、完整候选与必要发布 |
| `references/code-map.md` | 停用；仅用户明确试用 / 恢复时读 |
| `references/adoption-model.md` | 采纳模型的历史解释，不增流程义务 |
| `references/rationale.md` | 按需追溯规则依据；历史不是第二套运行正文 |
