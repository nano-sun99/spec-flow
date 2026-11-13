# Playbook: 工作区与锁

> **示例非必须**：本页的走法是一条走通过的路，不是必须顺序；按实际情况调整。
> **规范性**：只有标「（规范性）」的章节；它们引用 L0-L2，不新增、不放宽闸口。

- **适用**：任何文件变更；认领 issue、撞锁、接管、放锁；直接干 / 批次修复 / hotfix 的分支起点。
- **一条走通过的路**：`git fetch` → 开 worktree → 先 `pwd` 取基准 → 干活 → 核完成事实 → 放锁。
- **失败模式**：在共享主仓直接改；拿 issue `open` 当没人认领；`--force` 强拆；改另一个 worktree 已检出的引用；不放锁导致重开撞锁。
- **证据**：`git worktree list`、分支名、基线提交、授权记录、放锁后的残留检查。
- **注意**：这是示例，不是必须顺序；闸口相关章节是规范性的，不能自行放宽；改动闸口证据须用户批准。

## 一条走通过的路（示例非必须）

1. **对表远端**：`git fetch origin --prune`；看当前分支、工作区是否干净、是否落后。
2. **选基线**：按项目映射取远端开发基线（未采用 release 默认 `origin/main` 或 `origin/master`；采用 staging 线为 `origin/staging`；已采用以项目映射为准）；不用可能落后的本地分支。
3. **认领**：`git worktree add <wt根>/issue-<N> -b issue/<N> <远端基线>`；开得成 = 没人做，被拒 = 有人在做。锁键 = 精确分支名 `issue/<N>`，worktree 目录 `issue-<N>`。
4. **进 worktree 第一件事 `pwd`**：编辑工具的绝对路径不跟 cwd 走；照会话前半段记下的主仓路径写，改的是主仓、还没报错。快信号：新写的测试报 `no tests to run`、新符号 grep 不到、worktree 里 `git status` 是空的。
5. **干活**：实现、测试、文档检查都在这个工作区完成；不直改另一个 worktree 已检出的引用。
6. **放锁**：按完成 / 交付事实收尾；先 fetch 并核本任务实际目标，再 `git worktree remove <wt根>/issue-<N>` + `git branch -d issue/<N>`；保留未提交工作时不强删。

## 撞锁与接管（示例非必须）

- `fatal: a branch named 'issue/<N>' already exists` = 有人领过；`git worktree list` 找到对方工作区路径。
- 目录还在 → 人在做；去读该 issue 的评论定等 / 让，不双写同一工作区。
- 目录没了 → 对方已不在；`git worktree prune` 清掉残留登记后，`git worktree add <wt根>/issue-<N> issue/<N>`（不带 `-b` 复用旧分支 = 接着既有提交干）。
- 推倒重来涉及危险删除，须用户明确要求；不因本页描述自行 `git branch -D`。

## 放锁细节（示例非必须）

- `git branch -d` 认的是 fetch 后的远端分支；先 `git fetch origin`。
- 远端 squash 合并时 `-d` 照样以 not fully merged 拒删；换 `-D` 属危险操作，须用户明确要求。
- 不放锁 = issue 重开时撞锁；不能用提前放锁冒充完成。
- 目录失效时才 `prune` 并按获准范围复用分支；不把撤销伪装成完成。

## 其它任务形态（示例非必须）

| 任务 | 分支 | worktree 目录 |
|---|---|---|
| issue 实施 | `issue/<N>` | `issue-<N>` |
| 直接干 | `task/<slug>` | `task-<slug>` |
| 批次修复 | `fix/<N>-<slug>`（直接干 `fix/<slug>`） | 同名 |
| hotfix | `hotfix/<tag>-<slug>` | 同名 |

无 issue 的任务没有锁可领，但 worktree 照开；分支名唯一即锁。

## 失败模式（示例非必须）

- 在共享主仓改文件；提交混进别人的分支，或改到主仓却无报错。
- 拿 issue `open` 当「没人认领」：2026-09-16 实测两个 agent 双双做完，浪费一份。
- `git worktree add --force` 强拆别人的工作区；本机制只防守规矩的人犯错，不防故意绕过。
- 跨机 / 跨 clone 把锁当全局；不同 `.git` 不共享锁。
- 放锁时直接 `-D`；把未推送 / 未合并的分支删掉。
- 以为锁能挡不同 issue 改同一堆文件；那是拆分时「独占文件」要解决的问题。

## 证据（示例非必须）

| 时点 | 证据 |
|---|---|
| 认领前 | 授权记录（D0 8 字段）或直接干的范围说明 |
| 认领 | `git worktree list`、分支名、基线提交 |
| 干活中 | 工作区路径（`pwd`）、提交记录 |
| 放锁 | fetch 结果、目标分支核对、`worktree remove` / `branch -d` 输出、残留项 |

## 闸口（规范性）

- **交付前置条件**（[10-stages](../10-stages.md) §三）：文件变更在独立 worktree；同一 issue 的分支锁名唯一（`issue/<N>`）；撞锁停，不双写同一工作区；分支命名可以自由，但锁键不能自由。
- **先授权后认领**：D0 授权与记录按 [20-decisions](../20-decisions.md) D0 与 [15-records](../15-records.md) §二；没有授权记录就开 = 跳过交接协议。接管需新的用户明确委托并留接管记录。
- **危险操作**：`git branch -D`、`git worktree add --force`、删除仍保留未提交工作的工作区、force push 等，只在用户明确要求时执行（L0-1）。
- **不直改他人引用**：不直改另一个 worktree 已检出的引用；不在共享主仓切分支或做快照。
- **不放锁冒充完成**：放锁按完成 / 交付事实收尾（[15-records](../15-records.md) §五）。
- **不新增闸**：本页不新增决定类型或完成条件；与 L0-L2 冲突时以 L0-L2 为准。
