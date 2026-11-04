# 项目接入（一页）

> 默认面 3 份之一。只写主路；接入新项目读 `apply-to-project.md`，标签读 `issue-status-labels.md` / `issue-type-labels.md`，ADR / 发布 / 文档生命周期按项目声明读。

## 工作区与锁

- 文件变更先 `git fetch`，从 `origin/main` 或 `origin/master` 开 worktree；认领用 `issue-<N>`，不认领用 `<type>/<slug>`。
- 撞锁 = 停；放锁 = PR 合并后 `worktree remove` + `branch -d`（squash 用 `-D`）。

## 段一：spec PR

- 一页 → 实施版；要三阶段 / DoR 细则读 `spec-maturity.md`，不强制每份 spec 走三阶段。
- 合并前摆卡：派审 / 修订 / 合并，每份单独点；过闸不授权合并。
- DoR 过了且用户点头才转 Ready；不自动转。
- 合并后开执行 issue：spec 永久链接、关系、改动面、未勾验收、交接区。
- 写完交接区报告后停；实施须用户明确委托，不自动开工。

## 段二：实施

- 认领 issue → worktree `issue-<N>` → 实施 → 派审 / 修订 / 合并 → 回填。
- 回填：spec 头 Issue、状态随 PR 改；正文写「关联 issue：#N」，不用 `Closes`。
- 关单：AC 全勾、证据齐、锁已放。

## 标签（项目声明才用）

- 类型：`feat` / `fix` / `docs` / `chore`；状态按项目；没声明不猜。
- 项目禁的审核档不摆，也不派。
