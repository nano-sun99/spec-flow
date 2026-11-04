---
name: spec-flow
description: "复杂活的两段流程：开工一页（目标 / 不做 / 验收），过 3 道闸（规格 / 范围 / 完成），审核四进三出；场景包触发才读。要设计、动多个端或值得留依据的需求，开工前调用；「请你做 #N」从实施期进；也处理「应用到本项目」「更新接入」，未知描述问清。"
---

# 复杂活的两段流程

**默认面 3 份**：开工读 `one-page.md`，过闸读 `gates.md`，PR / issue 读 `project-integration.md`。其余参考是场景包，触发才读。

## 五步

1. **开工** —— 写一页：目标 / 不做 / 验收；范围（改 / 不改）；R / AC / 验证。跑 `scripts/spec-check.py`，E1–E4 绿才往下；三行写不出可验证句 = 停，先问清。
2. **判页面 / 拆分** —— 无页面用样例；跨端或大 spec 读 `split-large-spec.md`；判不了摆页面卡，停。
3. **实施** —— worktree 里改；每轮跑 `spec-check --base`；E5 越界 = 停 / 变更单；新东西先写「不做 / 待定」，用户点头才做。
4. **审核** —— 每份 PR 由用户点档，agent 不自派。四进三出：输入 AC、diff + 证据、上轮 findings、已拍板决定；输出 AC / 证据 / 过不过 + 建议池；最多 2 轮，第 3 次只做重画 / 砍 / 停。
5. **合并 / 关单** —— spec PR 合并后开执行 issue（spec 链接 + 批次表）；实施 PR 合并后回填、关单、放锁。完成 = AC 无 ❌、证据齐、文档检查绿；❌ 未处置不能关。

**每轮第一行**：复杂活回复第一行写「目标 / 本轮推进 / 还差」；写不出「还差」= 这轮不该开工。

**方案页四格**：页面 / 机制 / 例外 / 改旧 spec，各自独立点，不合并。拆分 / 派审 / 修订 / 合并各一张卡。

**宪法**：只准加检查，不准加规矩。新翻车只能进 `spec-check`，或替换一条旧规矩；不准新增章节 / 卡片 / reference；默认面 3 份是白名单，新增需用户点头。

**豁免**：改一行、纯查事实、「直接干 / 别走流程」免方案期；闸、合并卡不免。

## 参考

下表 3 份常驻默认读；场景包触发才读；标「选修」的默认关闭，项目规则声明已采用才读。

| 文件 | 何时读 |
|---|---|
| `references/one-page.md` | 常驻——开工写一页 |
| `references/gates.md` | 常驻——过闸、派审、完成 |
| `references/project-integration.md` | 常驻——PR / issue / worktree / 回填 |
| `references/one-path.md` | 场景包——要 8 卡默认值 / 骨架主路表 / 多份叠加 |
| `references/gate-details.md` | 场景包——要四档差异 / R1–R3 逐轮职责 / 文档检查红绿 |
| `references/spec-maturity.md` | 场景包——新需求起手、判骨架 / 对照 / 实施版 |
| `references/split-large-spec.md` | 场景包——跨端 / AC 超阈值 / 评估拆分 |
| `references/phase-handoff.md` | 场景包——spec 合并后开 issue / 交接 |
| `references/done-criteria.md` | 场景包——观察式收尾 / 长尾验收 |
| `references/spec-revision-sync.md` | 场景包——改判据 / 定义 / 常量 / 术语 |
| `references/worktree-lock.md` | 场景包——撞锁 / 放锁 / squash 换 `-D` |
| `references/apply-to-project.md` | 场景包——接入 / 更新项目 |
| `references/adr-decision-records.md` | 选修 `adr`——拍板、收尾 |
| `references/documentation-lifecycle.md` | 选修 `doc-lifecycle`——读序、分工 |
| `references/issue-status-labels.md` | 选修 `issue-status`——阶段、收尾 |
| `references/issue-type-labels.md` | 选修 `issue-type`——开单、回填 |
| `references/release-discipline.md` | 选修 `release`——发布纪律 |
| `references/adoption-model.md` | 场景包——采用 / 接入契约 |
| `references/code-map.md` | 归档——已停用；明确试用 / 恢复才读 |
| `references/rationale.md` | 按需——查依据（R 号） |
