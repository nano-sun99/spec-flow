# Playbook: 续已有 issue（实施委托与整条交付）

> **示例非必须**：本页是参考走法；硬闸与记录以 L0–L2 为准。

- **适用**：点名执行 issue（「请做 `#N`」）、请求落入某 open issue 获批范围且未合入候选，或接管已认领工作。

## 一、落点判定

先查分支名、PR「关联 issue：#N」、commit `(#N)`、交接区、worktree 锁与发布记录再推荐：

| 事实 | 归属 |
|---|---|
| 落入某 open issue 获批范围且分支未合候选 | 续该 issue 分支 |
| 命中多单 | 列候选交用户选 |
| 无命中且边界清楚 | 直接干，开 `task/<slug>` |
| 无命中且需独立验收 / 设计 | 开新 issue，必要时先开 spec |
| 已合入候选或已关单 | 不续；走 `fix/<N>-<slug>` / `fix/<slug>` 或新单 |

## 二、参考走法

1. **对表远端**：`git fetch`、`git status -sb`、`gh issue view N`；核 `open`、获批 spec 版本、范围、标签与锁。
2. **核 D0 并留痕**：按 [20-decisions](../20-decisions.md) D0 核授权，将 [15-records](../15-records.md) §二 的 8 字段只追加写入原 issue。
3. **认领 worktree**：按 [worktree playbook](worktree.md) 开 `issue/<N>` 与 `issue-<N>`；开成 = 无人做，撞锁即停。
4. **影响分析**：用业务词 / 符号查源码、diff 与测试核调用方与分母；代码地图默认停用，自报 `complete` 不证全覆盖。
5. **分步实现与 D4**：实现 PR 只回 `issue/<N>`，每份独立走 D4 与 [26-review-contract](../26-review-contract.md)；PR 正文只写「关联 issue：#N」，**禁写** `Closes`/`Fixes`/`Resolves`；多 PR 中间子 PR 在 `D4 ②` 仅核本 PR 变更并标明剩余现状回写 / 减法归属整单出口。
6. **验收、四类与竣工回写**：在 `issue/<N>` 按获批 spec 验收贴证，核四类与竣工回写（[10-stages](../10-stages.md)、[15-records](../15-records.md) §五：现状同步 + 减法核销或用户确认转遗留）；有冻结盘点表仅交付表内行。
7. **预演与 D5（仅 staging 线）**：合当前 staging 入 issue 或临时预演分支并在真实 merge 树构建验收；通过后摆 D5 卡，确认后**真 merge（不 squash）**，经确认换「待上线」，分支冻结。采用 `release` 后续走 [release playbook](release.md)。

## 三、常见坑与关联闸口

- **坑**：拿 `open` 当无人认领双写；spec 合并未获 D0 就开工；把父单 / PR / 锁 / 审核通过当委托；实现 PR 合进 issue 就报完成漏四类 / 竣工回写 / 预演 / D5；整条合入用 squash 丢来源；把标签当状态机掩盖交接区冲突。
- **指针**：D0 / D4 / D5（[20-decisions](../20-decisions.md)）、[10-stages](../10-stages.md) §三、[15-records](../15-records.md) §一–§五、[release playbook](release.md#一发布安全不变式)。
