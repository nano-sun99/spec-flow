# Case: 2026-09-16 并发认领与 open 误判

- **情况**：同一 issue 号出现 5 个进程并发认领；另一仓 xhs-analysis #12 有两个 agent 都以「issue 是 open」判断没人做。
- **预期**：只有一个人做，另一个人另找活。
- **实际**：5 个进程里恰好 1 个 `git worktree add` 成功，其余全被 git 以 fatal 拒绝；xhs-analysis 的两个 agent 都做完了，浪费一份。
- **意外**：`open` 同时表示「待做」和「在做」，它从来不是锁；真正的锁由 git 保管——同一 `.git` 里分支名唯一，已被检出的分支不许再检出。
- **学到什么**：认领就是开 worktree：开得成 = 没人做，被拒 = 有人在做。想早知道可以看 `git worktree list`，但锁不靠它。跨机 / 跨 clone 不共享 `.git`，没有锁。
- **影响提议**：无。已进 [worktree playbook](../30-playbooks/worktree.md) 与 [10-stages](../10-stages.md) 交付前置条件。
- **用户是否批准偏离**：不适用。
- **被哪条规则覆盖 / superseded_by**：覆盖于 `30-playbooks/worktree.md` 撞锁与接管；superseded_by：无。
