# Playbook: 工作区与锁

> **示例非必须**：独立 worktree 与锁键规则以 [10-stages](../10-stages.md) §三 与 L0-1 为准。

- **适用**：任何文件变更；issue 认领、撞锁、接管与放锁；直接干 / 批次修复 / hotfix 分支建立。

## 一、参考走法

1. **对表远端与基线**：`git fetch origin --prune`，核状态与落后；按项目映射取远端基线（未采用 release 默认 `origin/main`/`origin/master`；staging 线 `origin/staging`），不用可能落后的本地分支。
2. **认领建 worktree**：`git worktree add <wt根>/issue-<N> -b issue/<N> <远端基线>`；开成 = 无人做，被拒 = 已有锁。
3. **进区先跑 `pwd`**：编辑工具路径不跟 shell cwd 走，防误改主仓（快信号：新符号 grep 不到或 worktree `git status` 空）。
4. **干活与按事实放锁**：实现 / 测试 / 文档检查均在 worktree 内完成，不改他区检出引用；收尾并 `git fetch` 核已合入后执行 `git worktree remove` + `git branch -d`（有未提交不强删）。

## 二、撞锁、接管与命名

- **撞锁**：`branch 'issue/<N>' already exists` 用 `git worktree list` 查目录——仍在则有人在做，沟通等 / 让，**不双写**；目录已删则 `git worktree prune` 清残留，在获新 D0 `takeover` 后 `git worktree add <wt根>/issue-<N> issue/<N>`（无 `-b`）续做。
- **危险删除须用户明示（L0-1）**：`git branch -D`（含远端 squash 合并 `-d` 拒删时）、`git worktree add --force`、删未提交区、force push 均不自行执行。
- **命名**：issue `issue/<N>`（`issue-<N>`）｜直接干 `task/<slug>`（`task-<slug>`）｜批次修 `fix/<N>-<slug>` 或 `fix/<slug>`｜hotfix `hotfix/<tag>-<slug>`。

## 三、常见坑与指针

- **坑**：拿 `open` 当无人认领双写；在共享主仓直改；误以为不同机器共享本地 worktree 锁或锁能替拆分；提前放锁或不放锁致重开撞锁。
- **指针**：[10-stages](../10-stages.md) §三、D0（[20-decisions](../20-decisions.md)）、[15-records](../15-records.md) §二 / §五、L0-1（[00-constitution](../00-constitution.md)）。
