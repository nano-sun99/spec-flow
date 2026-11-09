# 工作区、认领与锁（文件变更、认领、撞锁、放锁时读）

> 本文件是文件变更、认领、撞锁和放锁时必须读取的执行细则；不可见或版本变了时动作前重读。锁判据不变（依据：rationale R25）。

锁由 git 保管，不靠登记、不靠吱声。

- **改文件先开 worktree**：凡文件变更先 `git fetch`，别改主仓。未采用 release 时默认从 `origin/main`（或 `origin/master`）；已采用时先读 `references/release-discipline.md` 的已选单主线/三层映射，普通任务起点和 PR 目标跟随实际开发分支，不并存冲突默认。hotfix 继续原生产 tag 例外（依据：rationale R37）。
- **命名 = 锁**：分支和 worktree 目录同名 `issue-<N>`，纯号、无 slug、无前缀。同一 `.git` 里分支名唯一、已被检出的分支不许再检出——git 强制（依据：rationale R6）。认领就是开 worktree：开得成 = 没人做；被拒 = 有人在做。
- **认领**：`git fetch origin --prune` 后 `git worktree add <wt根>/issue-<N> -b issue-<N> <远端开发基线>`（未采用 release 的默认例为 origin/main；已采用以其映射为准；wt 根项目自定，如 `.claude/worktrees/`，不用可能落后的本地分支作基线）。想早知道可先 `git worktree list | grep issue-<N>`——可选，锁不靠它。⚠️ 别拿 issue `open` 当「没人认领」：open 同时表示待做和在做（依据：rationale R7）——只信锁。
- **先授权后认领**：授权识别只读 `references/gate-details.md`，授权记录信息只读 `references/phase-handoff.md`〈二〉；留痕后认领。无交接区旧单不补造规格/阶段，按同一交付正文留适用记录。没有授权记录就开 = 跳过交接协议（依据：rationale R29）。
- **接管 / 撤销**：先按 gate-details 核明确接管/撤销权限，按 phase-handoff 追加记录；状态衔接只读 `references/one-path.md`。目录失效时才 `prune` 并按获准范围复用分支，不把撤销伪装成完成。
- **撞锁 = 停**：`fatal: a branch named 'issue-<N>' already exists` = 有人领过。`git worktree list` 找到对方工作区路径：目录还在 → 人在做，去读该 issue 的评论定等 / 让；目录没了 → 对方已不在，`git worktree prune` 清掉残留登记后接手：`git worktree add <wt根>/issue-<N> issue-<N>`（不带 -b 复用旧分支 = 接着既有提交干；推倒重来涉及危险删除，须用户明确要求，不能因本页描述自行 `git branch -D`）。
- **放锁**：按完成/交付事实收尾，先 fetch 并核本任务实际目标，再 `git worktree remove <wt根>/issue-<N>` + `git branch -d issue-<N>`；保留未提交工作时不强删。squash 等情形 `-d` 可能拒绝，报告残留锁/分支，危险 `-D` 仍须用户明确要求，不从收尾指令外推（历史原因见 rationale R8）。不放 = issue 重开时会撞锁；不能用提前放锁冒充完成。
- **进 worktree 第一件事重新取基准**（`pwd`）：编辑工具用的绝对路径不跟 cwd 走，照会话前半段记下的主仓路径写，改的是主仓、还没报错。快信号：新写的测试报 `no tests to run`、新符号 grep 不到、worktree 里 `git status` 是空的。
- **边界**：锁只挡同号认领——不同 issue 改同一堆文件拦不住（那是拆 spec 时「独占文件」规矩管的，见 `references/split-large-spec.md`）；跨机 / 跨 clone 不共享 `.git`，无锁；`git worktree add --force` 能强拆——本机制只防守规矩的人犯错，不防故意绕过。不认领的活（如 spec 期，含占位 issue）：wt 照开（见本页的文件变更规则）但无锁可领，命名随意（惯例 `<type>/<slug>`）。
