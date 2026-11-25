# Playbook: 工作区与锁

> **示例非必须**：本页是 Git worktree 与锁的操作方法；独立 worktree 与锁键规则以 [10-stages](../10-stages.md) §三 及 L0-1 为准。

- **适用**：任何文件变更；issue 认领、撞锁、接管与放锁；直接干 / 批次修复 / hotfix 的分支建立。

## 一、参考走法

1. **对表远端**：`git fetch origin --prune`，核当前分支、工作区状态与是否落后。
2. **选远端基线**：按项目映射取开发基线（未采用 release 默认 `origin/main` 或 `origin/master`；staging 线取 `origin/staging`），不用可能落后的本地分支。
3. **认领建 worktree**：`git worktree add <wt根>/issue-<N> -b issue/<N> <远端基线>`；开成 = 无人做，被拒 = 已有锁。
4. **进 worktree 先跑 `pwd`**：编辑工具的绝对路径不跟 shell cwd 走；核路径防误改主仓（快信号：新符号 grep 不到或 worktree `git status` 为空）。
5. **干活与验证**：实现、测试、文档检查均在该 worktree 完成；不直改另一 worktree 已检出的引用。
6. **按事实放锁**：完成收尾并 `git fetch origin` 核目标分支已合入后，执行 `git worktree remove` + `git branch -d`；保留未提交工作时不强删。

## 二、撞锁、接管与分支命名

- **撞锁判定**：`branch 'issue/<N>' already exists` 即有人领过，用 `git worktree list` 找目录：
  - 目录仍在 → 有人在做，读 issue 评论沟通等 / 让，**不双写同一工作区**。
  - 目录已删 → `git worktree prune` 清残留后，在取得新用户接管委托（D0 `takeover`）下用 `git worktree add <wt根>/issue-<N> issue/<N>`（不带 `-b`）续做。
- **危险删除须用户明确要求（L0-1）**：`git branch -D`（含远端 squash 合并导致 `-d` 拒删时）、`git worktree add --force`、删未提交工作区、force push 均不自行执行。

| 任务形态 | 分支名（锁键） | worktree 目录 |
|---|---|---|
| issue 实施 | `issue/<N>` | `issue-<N>` |
| 直接干 | `task/<slug>` | `task-<slug>` |
| 批次修复 | `fix/<N>-<slug>`（直接干 `fix/<slug>`） | 同名 |
| hotfix | `hotfix/<tag>-<slug>` | 同名 |

## 三、常见坑

- 拿 issue `open` 当无人认领导致双双做完浪费一份；或在共享主仓直接改文件。
- 误以为不同 clone / 机器共享本地 worktree 锁；或以为锁能防不同 issue 改同一文件（那是拆分独占范围的事）。
- 提前放锁冒充完成，或不放锁导致重开时撞锁。

## 四、关联闸口（指针）

- 交付前置与锁键：[10-stages](../10-stages.md) §三；先授权后认领：[20-decisions](../20-decisions.md) D0、[15-records](../15-records.md) §二。
- 危险操作确认：L0-1（[00-constitution](../00-constitution.md)）；收尾放锁：[15-records](../15-records.md) §五。
