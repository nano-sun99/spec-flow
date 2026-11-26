# Playbook: 直接干（无 spec / 无 issue）

> **示例非必须**：本页是参考走法；直接干免方案期与 D1，但**不免独立 worktree、验收与 D4 合并闸**。

- **适用**：改动边界清楚、无获批 spec / 执行 issue，用户选择直接干或 agent 判定落点报告后未被否决。

## 一、参考走法

1. **最小澄清与计划说明（L0-6）**：先核是否落在某个 open issue 范围内（落点表见 [issue playbook](issue.md)）；无批准基线时，一句话说明改哪里、怎么改、怎么验后再动文件（直接干免 D1 与反熵增三问）。
2. **替换式变更前置**：若本次改动修改 PR `base` 既有判据 / 术语 / 范围 / owner / 边界 / 分类，按 [change-protocol](change-protocol.md) 备 manifest 并跑校验器。
3. **开独立 worktree**：从项目映射开发基线切 `task/<slug>`（目录 `task-<slug>`），分支名唯一即锁；细则见 [worktree playbook](worktree.md)。
4. **实现与先测后合**：在 task 分支完成实现与测试；有测试环境时先部署 PR 分支跑验收，无则写不适用及事实理由。纯内部 bugfix / 重构零额外文书税；仅改变对外可见行为 / 命令 / 架构 / 接口 / README 时，于 `D4 ②` 前同步现状文档唯一 owner（见 [10-stages](../10-stages.md) 交付段）。
5. **提 PR 先不合**：PR 提到目标分支（staging 线为 staging），正文写清目标、范围、验收、无 issue 说明与验证证据，不直接合入。
6. **合并闸（D4）**：按 [26-review-contract](../26-review-contract.md) 先跑文档检查、走 D4 ① 选审核档位与修订范围，审核修订完成后走 D4 ② 独立确认合并。
7. **收尾**：已采用 `release` 时在发布记录**手工列入**该任务的分支、PR、commit 与验收证据，不靠 issue 标签查询；批次失败切 `fix/<slug>`，不回已合并分支。

## 二、常见坑

- 先合进候选再问「用候选测吗」，测试对象已不是待合版本。
- 以「只改一行」跳过计划说明、worktree 或 D4 合并闸。
- 发布分拣只查 issue 标签导致直接干任务漏列；或给 task PR 强套 issue 标签语义。
- PR 正文只写「修了个问题」，目标、验收与证据全靠会话记忆。
- 改动了对外可见命令 / 接口 / 架构或 README 却漏同步现状文档唯一 owner。

## 三、关联闸口（指针）

- 计划说明与否决点：L0-6（[00-constitution](../00-constitution.md)）。
- 交付完成条件：[10-stages](../10-stages.md) 交付段（无 issue 分支）。
- 审核与合并：D4 两时点（[20-decisions](../20-decisions.md)）、L0-5、[26-review-contract](../26-review-contract.md)。
