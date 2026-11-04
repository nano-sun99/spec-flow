---
name: spec-flow
description: "复杂活的两段流程：开工一页（目标 / 不做 / 验收），过 3 道闸（规格 / 范围 / 完成），审核四进三出；场景包触发才读。要设计、动多个端或值得留依据的需求，开工前调用；「请你做 #N」从实施期进；也处理「应用到本项目」「更新接入」，未知描述问清。"
---

# 复杂活的两段流程

**默认面 3 份**：开工读 `one-page.md`，过闸读 `gates.md`，PR / issue 读 `project-integration.md`。其余参考是场景包，触发才读。

## 段一·方案期（1–6）

1. **需求** —— 用户描述；有岔路问清，不猜；能自己查判的先做。
2. **确认** —— 方案页四格（页面 / 机制 / 例外 / 改旧 spec）各自独立点；判页面，判不了停。
3. **骨架** —— 起点 / 终点 / 主路表；有页面开 Draft PR，无页面用样例。
4. **拆分 / 对照 / 实施版** —— 骨架后评估拆分；同一 PR 补对照与实施版；机制清单 + 自定细节齐备，过 DoR 且用户点头才转 Ready。
5. **修订 / 合并** —— 派审卡由用户点档，agent 不自派；最多 2 轮；修订后单独确认合并。
6. **开 issue** —— spec PR 合并后开执行 issue（spec 链接 + 批次表 + 交接区）；报告后停，实施须用户明确委托。

## 段二·实施期（7–9）

7. **认领** —— worktree `issue-<N>`；首次实施前读获批 spec。
8. **实施** —— 一次授权覆盖整份 spec；每轮跑 `spec-check --base`；E5 越界 = 停 / 变更单；新东西先写「不做 / 待定」，用户点头才做。
9. **过闸 / 合并 / 回填** —— 派审 / 修订 / 合并每份单独点；回填、关单、放锁。

**开工一页**：三行锚（目标 / 不做 / 验收）+ 范围（改 / 不改）+ AC 表；跑 `scripts/spec-check.py`，E1–E4 绿才往下。三行写不出可验证句 = 停。

脚本在 skill 根下；安装后是 `~/.claude/skills/spec-flow/scripts/spec-check.py`，在目标仓里用 `python3` 跑。

**每轮第一行**：复杂活回复第一行写「目标 / 本轮推进 / 还差」；写不出「还差」= 这轮不该开工。

**宪法**：只准加检查，不准加规矩。新翻车只能进 `spec-check`，或替换一条旧规矩；不准新增章节 / 卡片 / reference；默认面 3 份是白名单，新增需用户点头。预算：SKILL ≤ 60 行 / 正文 ≤ 2,800 字符；3 份常驻 ≤ 180 行。

**豁免**：改一行、纯查事实、「直接干 / 别走流程」免方案期；当场说「直接改 / 不开 wt」免开 worktree；无新内容机械变更（回填号、状态、索引、勾验收）免闸；闸、合并卡不免。

## 参考

下表 3 份常驻默认读；场景包触发才读；标「选修」的默认关闭，项目规则声明已采用才读。

| 文件 | 何时读 |
|---|---|
| `references/one-page.md` | 常驻——开工写一页 |
| `references/gates.md` | 常驻——过闸、派审、完成 |
| `references/project-integration.md` | 常驻——PR / issue / worktree / 回填 |
| `references/one-path.md` | 场景包——要 8 卡默认值 / 骨架主路表 / 多份叠加 |
| `references/gate-details.md` | 场景包——要四档差异 / 多份叠加 / 文档检查红绿 |
| `references/spec-maturity.md` | 场景包——要三阶段 / DoR 细则 |
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
