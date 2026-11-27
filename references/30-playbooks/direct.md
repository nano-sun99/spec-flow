# Playbook: 直接干（无 spec / 无 issue）

> **示例非必须**：直接干免方案期、D1 与反熵增三问，但**不免独立 worktree、验收与 D4 合并闸**。

- **适用**：改动边界清楚、无获批 spec / 执行 issue，用户选直接干或 agent 判定报告后未被否决。

## 一、参考走法

1. **计划说明（L0-6）**：先核是否落入 open issue（落点表见 [issue playbook](issue.md)）；无基线时一句话说明改哪里、怎么改、怎么验后再动文件。
2. **替换式变更**：若改 PR `base` 既有判据 / 术语 / 范围 / owner / 边界 / 分类，按 [change-protocol](change-protocol.md) 备 v2 manifest 校验。
3. **开独立 worktree**：从项目开发基线切 `task/<slug>`（目录 `task-<slug>`），分支名即锁（[worktree playbook](worktree.md)）。
4. **实现与先测后合**：在 task 分支实现并验收（有测试环境先部署 PR 分支验收，无写理由）。纯内部 bugfix / 重构零额外文书税；仅改对外行为 / 命令 / 架构 / 接口 / README 时于 `D4 ②` 前同步现状文档唯一 owner（[10-stages](../10-stages.md) 交付段）。
5. **提 PR 与 D4**：PR 写清目标 / 范围 / 验收 / 无 issue 说明与证据，不直接合入；按 [26-review-contract](../26-review-contract.md) 先跑文档检查，再走 D4 ① 选档与 D4 ② 独立确认合并。
6. **收尾**：采用 `release` 时在发布记录**手工列入**分支 / PR / commit / 验收；批次失败切 `fix/<slug>`，不回已合分支。

## 二、常见坑

- 先合入再测；以「只改一行」跳过计划说明、worktree 或 D4；发布只查 issue 标签漏掉直接干；PR 正文靠会话记忆；改对外行为 / 命令 / 接口 / README 漏同步现状 owner。

## 三、关联闸口（指针）

- L0-6（[00-constitution](../00-constitution.md)）、[10-stages](../10-stages.md) 交付段（无 issue）、D4 两时点（[20-decisions](../20-decisions.md)）、L0-5、[26-review-contract](../26-review-contract.md)。
