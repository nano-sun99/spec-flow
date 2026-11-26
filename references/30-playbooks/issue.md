# Playbook: 续已有 issue（实施委托与整条交付）

> **示例非必须**：本页是参考走法；硬闸与记录要求以 L0–L2 为准。

- **适用**：用户点名执行 issue（如「请做 `#N`」）、新请求落在某 open issue 获批范围内且分支未合入，或接管已认领工作。

## 一、落点判定

先查事实再推荐（分支名、PR「关联 issue：#N」、commit `(#N)`、交接区、worktree 锁、发布记录）：

| 事实 | 归属 |
|---|---|
| 落在某 open issue 获批范围内且分支未合入候选 | 续该 issue 分支 |
| 命中多个 issue | 列候选交用户选 |
| 无命中且改动边界清楚 | 直接干，开 `task/<slug>` |
| 无命中且需独立验收或设计 | 开新 issue，必要时先开 spec |
| issue 已合入候选或已关单 | 不续；走 `fix/<N>-<slug>` / `fix/<slug>` 或新 issue |

## 二、参考走法

1. **对表远端**：`git fetch`、`git status -sb`、`gh issue view N`；核 issue 仍 `open`、获批 spec 版本、范围、标签与锁状态。
2. **核 D0 授权并留痕**：按 [20-decisions](../20-decisions.md) D0 核定向入口、同窗口入口闭集或接管授权，将 [15-records](../15-records.md) §二 的 8 字段追加进原 issue（只追加不篡改）。
3. **认领 worktree**：按 [worktree playbook](worktree.md) 开 `issue/<N>` 与 `issue-<N>`；开成 = 无人做，撞锁即停。
4. **影响分析**：实现前用业务词 / 符号检索源码、读真实 diff 与相关测试，核调用方与分母。代码地图工具默认停用，仅用户明确要求试用 / 恢复时才用；工具自报 `complete` 不证明全仓覆盖，未验部分回落源码。
5. **分步实现与 D4**：实现 PR 只回 `issue/<N>`，不直接合候选；每份 PR 独立走 D4 两时点与 [26-review-contract](../26-review-contract.md)。PR 正文只写「关联 issue：#N」，不写 `Closes` / `Fixes` / `Resolves`。多 PR 分步合回时，中间子 PR 在 `D4 ②` 仅核本 PR 对应变更并注明剩余现状回写 / 减法项归属整单交付出口。
6. **分支验收、四类核对与竣工回写**：在 `issue/<N>` 按获批 spec 验收并贴证据；逐项核对四类（spec、实现 / 测试、文档、依赖）并完成竣工回写硬核对（[10-stages](../10-stages.md) 交付段、[15-records](../15-records.md) §五：现状文档按最终实现同步，减法清单已落实或经用户确认登记遗留）。有冻结范围盘点表时只交付表内行。
7. **合入预演与 D5（仅 staging 线）**：把当前 staging 合入 issue 分支或临时预演分支，在真实 merge 树上构建并跑本 issue 验收（rebase / CI 须证结果树等于真实 merge 树）；通过后摆 D5 卡，确认后**真 merge（不 squash）**，经用户确认换「待上线」，分支冻结。
8. **后续发布**：已采用 `release` 按 [release playbook](release.md) 走批次、rc 与生产。

## 三、常见坑

- 拿 issue `open` 当无人认领导致双写撞车；或 spec 合并、开单后未获 D0 就开工。
- 把父单、PR 号、已有锁或审核通过当成实施委托。
- 实现 PR 合进 issue 分支就报 issue 完成，漏掉四类、竣工回写（现状同步与减法核销）、预演与 D5。
- 整条合入用 squash 丢掉各 PR 来源；或把标签当状态机静默覆盖交接区冲突。

## 四、关联闸口（指针）

- 硬闸：D0 / D4 / D5（[20-decisions](../20-decisions.md)）、L0-5、L0-6。
- 前置与记录：[10-stages](../10-stages.md) §三 交付前置、[15-records](../15-records.md) §一–§五。
- 发布不变式与审核：[release playbook](release.md#一发布安全不变式)、[26-review-contract](../26-review-contract.md)。
