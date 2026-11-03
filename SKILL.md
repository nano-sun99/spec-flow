---
name: spec-flow
description: "复杂活的两段流程：需求确认、spec、PR 过闸、合并后开 issue；认领 issue、实施、过闸合并回填。要设计、动多个端或值得留依据的需求，开工前调用；「请你做 #N」从实施期进，每份交付物合并前均由用户选审核档位，agent 不自派。也处理「把 spec-flow 应用到本项目」「更新本项目的 spec-flow 接入」及语义变体，可附带 ADR 等采用意图；未知描述问清。"
---

# 复杂活的两段流程

**主线**：需求 → 骨架 → 对照 → 实施版 spec → `SPEC_READY`（交接）→ 委托 → 实施。每份交付物合并前过同一道闸，用户点档。按顺序走，不跳步、不合并步骤。

开工读入口：新需求进段一、已有 issue 进段二、接入走〈应用到项目〉。已采用规则在相关动作执行；ADR 项目开工或压缩恢复时读 `references/adr-decision-records.md`；调查、旧 issue、免方案期首次实施前搜现行决定；长期影响就记录、收尾核；未采用不加动作（依据：rationale R25）。

改动前核工作区、范围、目标及 diff，以源码和测试核影响，不扩范围。**代码地图默认停用**，仅明确试用/恢复时读（依据：rationale R27）。

**段一·方案期**（新需求）

1. **用户描述需求**
2. **一起确认需求** —— 有岔路问清，不猜；能自己查判的先做；再判有没有页面，判不了摆页面卡
3. **点头后才动 spec** —— 先出骨架版：有页面开 Draft PR 等设计稿，无页面用样例
4. **对照 → 实施版 → DoR → 过闸** —— 同一 PR 补四列对照与实施版；过 DoR 转 Ready、摆闸卡
5. **按需修订 → 确认合并**
6. **开 issue** —— spec PR 合并后、实施前开，锚 spec 永久链接

**段二·实施期**（spec 已合并，不重走段一）

7. **认领 issue** —— 锁 = worktree 分支 `issue-<N>`；首次实施前读获批 spec
8. **在 worktree 里实施** —— 核当前影响及已采用约束
9. **过闸 → 确认合并 → 回填** —— 按完成标准和已采用收尾规则回填、决定关单、放锁

## 卡片总表

要用户拍板就摆卡，不打字问。

| 卡 | 何时摆 | 选项 | 没点 / 点了别的 |
|---|---|---|---|
| 页面卡 | 第 2 步判页面 | 出设计稿 / 不出，用样例，推荐在前 | 停住，等用户选 |
| 拆分卡 | 骨架版成形、结构实质变化（第 3/6 步） | 拆 / 不拆，推荐在前 | 不开执行单 |
| 机制卡 | 方案 / spec 有新增机制（第 2/3 步） | 全要 / 全砍 / 逐项挑 | 不出 spec |
| 闸卡 | 每份交付物合并前（第 4、9 步） | 不审 / 轻审 / 重审 / 重审 + 变异 | 按「不审」走 |
| 修订卡 | 审核有发现 | 改 / 不改 | 不合并 |
| 例外卡 | 验收项有观察式条目、属三类例外之一（第 2/3 步） | 纳入 / 不纳入 | 按「不纳入」走（默认禁） |
| 改旧 spec 卡 | 改已合并 spec 正文（含新需求、实施写错） | 新开一份 spec / 改旧的 | 不动笔 |
| 合并卡 | PR 合进目标分支 | 合并 / 先不合 | 不合并 |

- 定稿 spec 反复改会乱，新开还是改旧由用户定（依据：rationale R12）。

## 闸（两段共用）

- 每份各过一道、当场点档、不沿用；摆卡即算过完（不审也算），没摆卡不算；过闸不授权合并（依据：rationale R30）。
- **判断权全在用户**：agent 不自动派、不自行判「算不算核心」。
- 档位按每份算：

  | 档 | 派什么 | 大致代价 |
  |---|---|---|
  | 不审 | 无；agent 拿 diff 对 spec 改动面及已采用约束（受影响者核源码），范围外停下报告 | 0 |
  | 轻审 | 1 个：spec 期 = 规格符合性 + 两张清单；实施期 = 对抗找 bug + 范围外对账（依据：rationale R3） | 约 5 分钟 |
  | 重审 | 2 个：规格符合性（含清单 / 对账）+ 对抗找 bug | 约 10 分钟 |
  | 重审 + 变异 | 重审 + agent 自跑一次变异：判据换错、跑全量测试，全绿 = 没护栏 | 同重审 + 约 18 秒 |

- ⚠️ **多份叠加**：卡上算「N 份 × 该档 = 约 X 个 agent / Y 分钟」。
- 项目禁的档不摆，审核 prompt 也不要求跑。
- 摆卡前：含文档改动先跑目标仓检查，卡上固定一行「文档检查：绿 / 红+摘要 / 无入口」。
- 派审核、跑检查前读 `references/gate-details.md`；结论原样贴 PR 评论，有发现再摆修订卡，处置进 spec 末尾「审核修订记录」；不审不写免责声明。

## 豁免总表

拿不准不自判：照摆卡，附问归属。

| 免什么 | 条件 | 照样不免 |
|---|---|---|
| 方案期（不出 spec、不开 issue） | 改一行、纯查事实、「直接干 / 别走流程」 | 闸、合并卡 |
| 开 worktree | 当场说「直接改 / 不开 wt」；agent 不自判、不建议 | 声明真并行的仓认领仍开锁 |
| 闸 | 无新内容机械变更（回填号、状态、索引、勾验收）；不进仓的草稿 / PR 底稿 | 无 PR 的交付前照摆卡，diff 随卡；免审核不免合并卡 |
| 改旧 spec 卡 | 同上机械变更；末尾「审核修订记录」追加 | — |

## 工作区与锁

- 凡文件变更先 `git fetch`，从 `origin/main`（或 `origin/master`）开 worktree，别改主仓。
- 进 worktree 先 `pwd` 重取基准：编辑工具不跟 cwd 走。
- 认领 = 开同名分支与 worktree `issue-<N>`：成功=没人做；被拒=有人做，停（依据：rationale R6）。⚠️ 不拿 issue `open` 当无人领，只信锁（依据：rationale R7）。
- 合并后删 worktree 与分支放锁；认领、撞锁、放锁前读 `references/worktree-lock.md`。

## 各步要点

**第 2/3 步·两张清单**

- **机制清单**：每新增机制 / 概念 / 抽象单列「解决什么 / 没有会怎样」；没有写「无新增机制」。新增机制先单摆机制卡，不混正文点头，获准才写 spec；需求确认不代替它，机制来自需求也不免卡。清单随方案、spec 入文件。
- **自定细节**：spec 未写死、agent 定的默认值、判定、命名、落点逐条列末尾「自定细节」；用户扫、不逐项问；该列不列违规。
- spec 期审核核两张清单都在、与正文对应；清单外机制 = 漏报。

**完成标准**（第 3、6、9 步）：**完成 = 有限承诺**——约定功能、相关测试通过、无未处理阻断、证据齐全；观察式收尾默认不进单；例外见 `references/done-criteria.md`（依据：rationale R18）。

**spec 体量与拆分**：骨架版成形后按 `references/split-large-spec.md` 评估体量、多阶段，用户选后定稿；编号、父子单照细则（依据：rationale R15、R28）。

**第 5 步·修订**：⛔ 改判据/定义/常量/术语必须全文同步；动笔前读 `references/spec-revision-sync.md`（依据：rationale R1）。

**第 6 步·开 issue**：结构确认、spec 合并后开；正文含 spec 永久链接、关系、改动面、未勾验收及交接区（父单除外）（依据：rationale R2、R28）。

**方案交接**：spec 合并后开执行 issue 写 `SPEC_READY` 交接区（见 `references/phase-handoff.md`）；报告后停，实施须用户明确委托；审核档位不继承（依据：rationale R29）。

**第 9 步·回填**：spec 头部 Issue、状态随 PR 改，不另开 PR；正文写「关联 issue：#N」而非 `Closes` / `Fixes` / `Resolves`（依据：rationale R22）。合并后勾验收、评论「代码已合」、按完成标准关单、放锁。

## 应用到项目

应用/更新/语义变体读 `references/apply-to-project.md`。只指向不放副本；未知描述问清，旧副本只报告不删改。显式升级共用接入检查；普通任务不补制度；项目写入核授权、机器安装另同意，可执行资产走 §十 升级闸（依据：rationale R21、R25）。

## 项目体例与参考

目录、标题、标签、节序依项目 `AGENTS.md` / `CLAUDE.md` 或记忆。

命中动作的细则必须读、执行；压缩丢失或版本变了，动作前重读。历史说明不增义务。表内「选修」默认关闭，不自动引入或推销；本次要求或项目声明已采用时才读，采用走行内修饰词。

| 文件 | 何时读 |
|---|---|
| `references/spec-maturity.md` | 第 2–4 步：三阶段与 DoR |
| `references/gate-details.md` | 派审核、检查、合并前 |
| `references/worktree-lock.md` | 认领、撞锁、放锁时 |
| `references/spec-revision-sync.md` | 第 5 步修订 spec 前 |
| `references/done-criteria.md` | 完成标准、观察收尾、例外 |
| `references/code-map.md` | 停用；明确试用/恢复时读 |
| `references/split-large-spec.md` | 骨架、定稿、开单前 |
| `references/phase-handoff.md` | 交接、委托、合并时 |
| `references/adr-decision-records.md` | 选修 `adr`——调查、实施前、拍板、收尾 |
| `references/documentation-lifecycle.md` | 选修 `doc-lifecycle`——读序与文档分工 |
| `references/issue-status-labels.md` | 选修 `issue-status`——阶段/卡点及收尾 |
| `references/issue-type-labels.md` | 选修 `issue-type`——开单挂类型与回填 |
| `references/release-discipline.md` | 选修 `release`——发布纪律 |
| `references/apply-to-project.md` | 应用、接入 |
| `references/adoption-model.md` | 按需了解采纳 |
| `references/rationale.md` | 按需查依据（R 号） |
