---
name: spec-flow
description: "复杂活的两段流程：需求确认、spec、PR 过闸、合并后开 issue；认领 issue、实施、过闸合并回填。要设计、动多个端或值得留依据的需求，开工前调用；「请你做 #N」从实施期进，每份交付物合并前均由用户选审核档位，agent 不自派。也处理「把 spec-flow 应用到本项目」「更新本项目的 spec-flow 接入」及语义变体，可附带 ADR 等采用意图；未知描述问清。"
---

# 复杂活的两段流程

**主线**：新需求选直接干，或方案 Yes/No → 页面 → 草稿 → 拆分 → 样例或用户设计/接口分析 → 终稿/DoR → 派审/合并 → 开单交接 → 明确委托 → 实施 → 派审/合并 → 回填。有发现点修订，不跳步。

入口：仅新需求写文件前选「直接干 / 开 spec」，选择入 PR；已有 issue 按有效委托进段二，未合并 spec / PR 续原阶段，有效确认不重问。接入走〈应用到项目〉。ADR 已采用者开工/压缩恢复读 `references/adr-decision-records.md`，调查、旧单、免方案首次实施前搜现行决定，长期影响留证；未采用不加动作（依据：rationale R25、R36）。

只读核 grill-me 及实际调用的 grilling 可加载；仅 PLAN / ANALYZE 缺依赖问安装 Yes / No，拒绝或失败暂停该路径、不换模板，不挡直接干/既有实施交付。见 `references/apply-to-project.md`〈方案梳理依赖〉（依据：rationale R36）。

改前核工作区/范围/目标/diff，以源码和测试核影响。**代码地图默认停用**，仅明确试用/恢复读（依据：rationale R27）。

**段一·方案期**（新需求）

1. **描述需求、选入口** —— 直接干不补 spec / 执行单，仍过交付闸
2. **PLAN / CONFIRM** —— 开 spec 立即加载 grill-me；事实先查，只问用户能定的事、给推荐。汇总改哪里/怎么改/问题与能力、目标/范围/验收；No 调整同一方案，首次 Yes 前不写 spec
3. **PAGE → 草稿 → 拆分** —— Yes 后立即摆有页面/无页面卡，未选停；写目标/验收草稿：有页面开同一 Draft PR，无页面配样例；草稿后单独选拆分
4. **对照 → 终稿 → DoR → 派审** —— 有页面暂停等用户设计，再借 grill-me 分析页面与接口；无页面用正常/边界/失败或重跑样例。完善同一终稿，DoR 通过且用户同意送审才转 Ready、摆派审卡
5. **按需修订 → 确认合并**
6. **开 issue** —— spec PR 合并后、实施前开；锚 spec 永久链接，附批次表

**段二·实施期**（spec 已合并，不重走段一）

7. **认领 issue** —— 锁 = worktree 分支 `issue-<N>`；实施前读获批 spec
8. **worktree 实施** —— 一次授权覆盖整份 spec，阶段间不问，只在预声明停止点停；核影响和已采用约束
9. **派审 → 修订 → 确认合并 → 回填** —— 按完成标准与已采用规则回填、关单、放锁

## 卡片总表

要拍板就摆卡。入口 → 同一方案 Yes / No → 页面 → 草稿后拆分，不另摆机制卡/固定三句；例外/改旧按条件触发。交付的派审/修订/合并每份独立点。选项与未答后果见 `references/one-path.md`（依据：rationale R36）。

- 改已合并 spec 先让用户选新开/改旧（依据：rationale R12）。

## 闸（两段共用）

- 每份当场选档、不沿用；摆卡才过闸（不审也算），不授权合并（依据：rationale R30）。
- **判断权全在用户**：agent 不自动派、不自行判核心。
- 档位按每份算：

  | 档 | 派什么 | 大致代价 |
  |---|---|---|
  | 不审 | 无；agent 拿 diff 对 spec 改动面及已采用约束（受影响者核源码），范围外停下报告 | 0 |
  | 轻审 | 1 个：spec 期 = 规格符合性 + 两张清单；实施期 = 对抗找 bug + 范围外对账（依据：rationale R3） | 约 5 分钟 |
  | 重审 | 2 个：规格符合性（含清单 / 对账）+ 对抗找 bug | 约 10 分钟 |
  | 重审 + 变异 | 重审 + agent 自跑一次变异：判据换错、跑全量测试，全绿 = 没护栏 | 同重审 + 约 18 秒 |

- 审核：R1 全量、R2 核上轮闭合、R3 停，由用户选重画/砍范围/停，不派第4轮；复审重摆派审卡（依据：rationale R35）。
- 有发现点全改/只改阻断+高/不改；阻断/高不合并，中/低列合并卡未处理项、不挡合并。
- ⚠️ 多份卡上算「N 份 × 该档 = X 个 agent / Y 分钟」。
- 项目禁的档不摆，也不派。
- 摆卡前：含文档改动先在交付工作区跑文档检查，卡上固定一行「文档检查：绿 / 红+摘要 / 无入口」。
- 派审/检查前读 `references/gate-details.md`；结论原样贴 PR 评论，处置进 spec 末尾「审核修订记录」；不审不写免责声明。

## 豁免总表

拿不准不自判：照摆卡，附问归属。

| 免什么 | 条件 | 照样不免 |
|---|---|---|
| 方案期（不出 spec、不开 issue） | 用户选「直接干 / 别走流程」；纯查事实 | 闸、合并卡；新需求不因改动小自动免 |
| 开 worktree | 当场说「直接改 / 不开 wt」；agent 不自判、不建议 | 声明真并行的仓认领仍开锁 |
| 闸 | 无新内容机械变更（回填号、状态、索引、勾验收）；不进仓的草稿 / PR 底稿 | 无 PR 的交付前照摆卡，diff 随卡 |
| 改旧 spec 卡 | 同上机械变更；末尾「审核修订记录」追加 | — |

## 工作区与锁

文件变更先 `git fetch`，从 `origin/main` 或 `origin/master` 开 worktree，不改主仓。认领用 `issue-<N>`；非认领（含 spec 期/占位 issue）命名随意，惯例 `<type>/<slug>`。认领、撞锁、放锁及进 worktree 重取基准见 `references/worktree-lock.md`（依据：rationale R6、R7）。

## 各步要点

**第 2–4 步·方案说明与自定细节**

- 原机制清单由同一已确认方案承接，新做法及解决什么/没有会怎样入 spec，不另造汇总或卡。
- **自定细节**：agent 定的默认值、判定、命名、落点列末尾，用户扫；遗漏违规。
- 审核核两者齐备且对应正文；目标/范围/能力实质变化回同一 CONFIRM，补齐既定决定不重问，有效设计复用（依据：rationale R36）。

**完成标准**：功能与相关测试通过、无未处理阻断、证据齐全；观察式收尾默认不进单，例外见 `references/done-criteria.md`（依据：rationale R18）。

**spec 体量与拆分**：所选分支草稿后按 `references/split-large-spec.md` 评估体量/多阶段、编号和父子单；选后推进，结构不变不重问（依据：rationale R15、R28、R36）。

**第 5 步·修订**：⛔ 改判据/定义/常量/术语必须全文同步；动笔前读 `references/spec-revision-sync.md`（依据：rationale R1）。

**第 6 步·开 issue**：结构确认、spec 合并后开；正文含 spec 永久链接、关系、改动面、未勾验收及交接区（父单除外）；开单报告附批次表（依据：rationale R2、R28、R35）。

**方案交接**：spec 合并后开执行 issue 写 `SPEC_READY` 交接区（见 `references/phase-handoff.md`）；报告后停，实施须用户明确委托；审核档位不继承（依据：rationale R29）。

**第 9 步·回填**：spec 头部 Issue、状态随 PR 改，不另开 PR；正文写「关联 issue：#N」而非 `Closes` / `Fixes` / `Resolves`（依据：rationale R22）。合并后勾已满足项、评论「代码已合」、按完成标准关单、放锁。

## 应用到项目

应用/更新/语义变体读 `references/apply-to-project.md`。只指向不复制；未知问清，旧副本只报告。显式升级共用接入检查，普通任务不补制度；项目写入核授权、机器安装另同意，可执行资产走 §十 升级闸（依据：rationale R21、R25）。

## 项目体例与参考

目录/标题/标签/节序依项目 `AGENTS.md` / `CLAUDE.md`。

细则命中必读、执行；压缩丢失/变更重读。历史不增义务；「选修」默认关闭，仅本次要求或项目声明已采用才读，采用走行内修饰词。

| 文件 | 何时读 |
|---|---|
| `references/spec-maturity.md` | 第 2–4 步：三阶段与 DoR |
| `references/one-path.md` | 方案确认、页面两路、走路审核、批次表、卡片默认值 |
| `references/gate-details.md` | 派审核、合并前 |
| `references/worktree-lock.md` | 文件变更、认领、撞锁、放锁时 |
| `references/spec-revision-sync.md` | 第 5 步修订前 |
| `references/done-criteria.md` | 完成标准、观察收尾、例外 |
| `references/code-map.md` | 停用；明确试用/恢复时读 |
| `references/split-large-spec.md` | 骨架、定稿、开单前 |
| `references/phase-handoff.md` | 交接、委托、合并时 |
| `references/adr-decision-records.md` | 选修 `adr`——拍板、收尾 |
| `references/documentation-lifecycle.md` | 选修 `doc-lifecycle`——读序、分工 |
| `references/issue-status-labels.md` | 选修 `issue-status`——阶段、收尾 |
| `references/issue-type-labels.md` | 选修 `issue-type`——开单、回填 |
| `references/release-discipline.md` | 选修 `release`——发布纪律 |
| `references/apply-to-project.md` | 应用、接入 |
| `references/adoption-model.md` | 按需了解采纳 |
| `references/rationale.md` | 按需查依据（R 号） |
