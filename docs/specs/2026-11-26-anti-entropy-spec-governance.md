# spec-flow 反熵增规格治理与竣工回写（迭代 2）

- 状态：Draft（待 D2 审核与确认）
- 日期：2026-11-26
- 基线：`rebuild/v2`（`c352037`）
- 形态：无页面；不拆（单份 spec + 单条实现分支）；无观察式例外；非跨切面需求（不建范围盘点表：本迭代不涉及多入口/权限维度枚举，受影响文件清单在 §二.1 完整枚举，实施期由 `change-protocol` manifest 逐条旧→新对账）

## 一、决定节（唯一正文）

本仓未对一般规格启用独立 ADR，本节是迭代 2 全部承重决定的唯一正文（决定 ID 采用 `AR-*`，与闸口 ID `D0–D7` 隔离）。

| ID | 决定（一句话） | 来源 | 状态 | 适用范围 | 重开条件 | 覆盖 |
|---|---|---|---|---|---|---|
| `AR-1` | 取消「轻量 Spec / 重型 Spec」人为二分，改为「单一精简底座 + 3 个按客观事实触发的治理组件」（跨切面盘点表、多文档/多视图治理、替换式变更 manifest）；普通单文档无派生视图无 ADR 协同的 spec 只留简版决定表与反熵增三问，不强求覆盖图、5 字段 owner 对账与逐句回指 | 用户 2026-11-26 拍板「那就按你说的来」+ D1 确认 | 已拍板 | `25-spec-governance`、`10-stages`、`20-decisions`、`26-review-contract`、`new-spec` | 需恢复二档模板或调整 3 个组件触发条件时回 D1/D2 | §二、§三.1、§四、§五、§六 |
| `AR-2` | 建立统一「治理组件中途平滑升级」协议（含审核中途冒出 ADR 与 manifest）：先过 L0-6 + #158 拦假膨胀，用户确认扩大/引入后原位补齐对应组件（不换模板、不重编底座 ID）；触及替换式变更（含取代旧 ADR 或变更既有规则/判据/owner/边界）时，须在触发的当轮修订提交内以当前 PR `base` 起草 `manifest.json` 跑 `--draft` 双扫描并带入复审，不拖到合并前才后补；纯新增且不改既有规则/旧 ADR 的 ADR 仅触发组件 2，不强造 manifest | 用户 2026-11-26 踩坑反馈 + D1 确认 | 已拍板 | `25-spec-governance` §五、`change-protocol`、`adr`、`26-review-contract` | 需改变中途触发时机、纯新增 ADR 边界或 R1–R3 轮次联动时回 D2 | §二、§三.2、§五、§六 |
| `AR-3` | 所有开 spec 需求在 D1 提出初步回答、在 D2 终稿写实「反熵增三问」（① 已有重叠盘点；② 减法清单；③ 现状真身落点），无删项或无现状变更须显式写明理由，不留空 | 用户 2026-11-26 路线图 + D1 确认 | 已拍板 | `10-stages`、`20-decisions` D1/D2、`new-spec`、`26-review-contract` | 需增删三问条目或改变落点 owner 时回 D2 | §二、§三.3、§四、§五、§六 |
| `AR-4` | 强化交付出口（D4 ② / D5）与关单收尾的「竣工回写（As-Built Sync）」：开 spec 须核对现状真身落点已按最终实际实现回写唯一现状文档且减法清单已落实或登记遗留（缺项不关单）；直接干不填反熵增三问，仅在改变对外可见行为、命令、架构、接口或对外 README 时须同步对应现状文档唯一 owner | 用户 2026-11-26 D1 选项卡 A1（推荐）+ D1 确认 | 已拍板 | `10-stages` 交付段、`15-records` §一/§四/§五、`20-decisions` D4、`direct`、`issue` | 需把完整反熵增三问扩展到全部直接干任务或放宽关单核对时回 D1/D2 | §二、§三.3、§四、§五、§六 |
| `AR-5` | 严守单一正文、双语 README 同步与低增量边界：不动 L0 铁律（`00-constitution.md`）与迭代 3 范围（`check-docs.sh`、`check-change.py`、`test-check-change.py`、`run-eval.py`）；同步双语 README（含补齐 `evals/` 入口）；保留既有章节序号与 Eval 锚点；`always_read_chars` 相对 v2 基线 `16,777` 净增上限为 `+800` 字；实施期按 `change-protocol` 交 manifest 过正式校验 | AGENTS.md #3–#6 + 用户 D1 确认 | 已拍板 | 全部受影响文件清单、字数预算、manifest 与保护边界 | 需改 L0、改校验脚本或提前并入迭代 3 瘦身时回 D1（改 L0 另走 L0-8） | §二、§六 |
| `AR-6` | 新增 2 条行为级 Eval 场景（`13-base-spec-anti-entropy` `anti-bloat`、`14-as-built-sync-closeout` `guardrail`），同步更新 `scripts/test-run-eval.py` 与 `evals/README.md`，实跑全量 14 条对比 `2026-11-26-v2-baseline.json` 验证原 12 条 `0` 退化、新增 2 条均 `pass`，留存脱敏基线 `2026-11-26-iter2-anti-entropy.json/.md` | 用户 2026-11-26 D1 选项卡 A2（推荐）+ D1 确认 | 已拍板 | `evals/scenarios/13..14.json`、`scripts/test-run-eval.py`、`evals/README.md`、`evals/baselines/` | 调整新增场景清单、断言口径或取消基线试跑时回 D2 | §二、§四、§六 |

## 二、方案、备选及代价与反熵增检查

### 1. 改动面、唯一 owner 归属与不动边界（`AR-1`–`AR-6`）

| 路径 | 角色 / 变更类型 | 变更内容与单一正文边界 |
|---|---|---|
| `references/25-spec-governance.md` | **唯一正文**（改） | 改为「单一精简底座 + 3 个按客观事实触发的治理组件」；新增 `## 五、治理组件中途平滑升级`（保留原 `## 一`–`## 四` 标题序号与锚点不动） |
| `references/10-stages.md` | **唯一正文**（改） | 核心术语表新增「反熵增三问」「竣工回写」唯一定义；澄清 / 设计 / 交付三段改写为底座 + 组件指针 + 竣工回写完成条件 |
| `references/15-records.md` | **唯一正文**（改） | 第 3 类「预期交付」补减法清单与现状落点；§四.1 现状文档明写按最终实际实现（as-built）同步；§五 关单收尾补竣工回写与减法核销硬核对 |
| `references/20-decisions.md` | 硬闸指针（改） | D1 补反熵增三问初稿；D2 改精简底座 + 按需组件指针与三问终稿；D4 ② 补竣工回写核对（区分开 spec 与直接干） |
| `references/26-review-contract.md` | 审核契约（改） | §四.2 区分「所有 spec 必核底座 3 项」与「仅触发组件 1/2 启用的 4 项重型前置阻断」；§五.1 与 Lane A 同步底座与中途 `--draft` manifest 指针（不做迭代 3 重写瘦身） |
| `references/30-playbooks/new-spec.md` | 走法指针（改） | D1 / 骨架 / 终稿嵌入反熵增三问与底座/按需组件升格指针 |
| `references/30-playbooks/direct.md` | 走法指针（改） | 补充直接干在改变对外行为 / 命令 / 接口 / README 时同步现状文档唯一 owner（不强填三问） |
| `references/30-playbooks/issue.md` | 走法指针（改） | 交付核对补竣工回写与减法清单核销指针 |
| `references/30-playbooks/change-protocol.md` | 走法指针（改） | 补中途触发（含取代旧 ADR / 改既有 owner）当轮切入 `--draft` 及纯新增 ADR 豁免指针 |
| `references/30-playbooks/adr.md` | 走法指针（改） | 补审核中途新增或取代 ADR 的平滑升格与 manifest 触发边界指针 |
| `SKILL.md`、`references/README.md` | 导航索引（微调） | `25-spec-governance` 与 `10-stages` 一句话职责摘要与新定位对齐 |
| `README.md`、`README.zh-CN.md` | 双语视图（同批改） | 同步说明精简底座、按需组件平滑升格、反熵增三问与竣工回写；顺手补齐迭代 1 留待补充的 `evals/` 与 `scripts/run-eval.py` 条目，守住 `<!-- s:xxx -->` 一一对应 |
| `evals/scenarios/13-base-spec-anti-entropy.json`、`14-as-built-sync-closeout.json` | 新增场景（增） | 2 条单文件自足行为级 Eval 场景（`13` `anti-bloat`、`14` `guardrail`） |
| `scripts/test-run-eval.py`、`evals/README.md`、`evals/baselines/2026-11-26-iter2-anti-entropy.{json,md}` | 单测与现状/基线（改/增） | 单测改为动态读取场景数（断言 ≥ 14）并补 `13`/`14` 正反例判别单测；`evals/README.md` 回写现状并去硬编码数字；留存迭代 2 自测基线报告 |
| `docs/changes/2026-11-26-anti-entropy-spec-governance/manifest.json` | 替换式变更台账（增） | 覆盖全部规则改动（`rules[]`）、索引（`non_rule_changes[]`）与非规则视图/Eval/单测（`view_files[]`），过 `scripts/check-change.py` 正式校验 |

**本迭代不动的文件（`AR-5`）**：`references/00-constitution.md`（L0 铁律）、`scripts/check-docs.sh`、`scripts/check-change.py`、`scripts/test-check-change.py`、`scripts/run-eval.py`、`docs/specs/2026-11-26-behavioral-eval-harness.md`（冻结 spec）与 `evals/baselines/2026-11-26-v2-baseline.{json,md}`（历史对比基线）均不得改动（`AR-5`）。

### 2. 备选方案及代价（`AR-1`、`AR-2`、`AR-4`）

- **备选 A（人为二分「轻量 Spec」与「重型 Spec」两档模板）**：开场需靠主观猜测选档；若需求随审核扩大，需在两套模板间迁移、补编 ID 与重写结构，反过来诱使人全都按重型写。已与用户对齐放弃，选定「单一精简底座 + 按客观事实触发 3 组件 + 原位平滑升格」。
- **备选 B（直接干也强制填写完整反熵增三问）**：给改一行超时或修局部 bug 叠加文书税，破坏 `01-small-direct-fix` 反膨胀底线；选定仅在直接干改变对外可见行为 / 命令 / 架构 / 接口 / README 时同步现状文档。
- **备选 C（本迭代顺手改造 `scripts/check-change.py` 为薄声明模式）**：工具脚本重构与规则语义变更混在同批，会污染 A/B 回归因果归因；按三步路线图把工具层改造留给迭代 3，本迭代先在规则层解决中途触发时机与边界。

### 3. 反熵增三问（本规格先行实践，`AR-3`、`AR-5`）

- **已有重叠盘点**：`25-spec-governance.md` §二 已有「跨切面按需触发」先例，§一.2 已有「短期决定升级 ADR 迁移别名」，`15-records.md` §四/§五 已有现状文档与关单框架，`change-protocol.md` 已有 `--draft` 与 `manifest-only` 钉扎机制——本迭代不另造平行文件或新 D 类型，直接在既有 owner 上重构边界并补齐缺失的中途升格与竣工回写闭环。
- **减法清单**：从 `10-stages.md` 设计段、`20-decisions.md` D2、`26-review-contract.md` §四.2/§六 移除「对所有普通单文档 spec 无条件强制覆盖图 / 5 字段 owner 对账 / 逐句规范性回指 / 缺索引直接阻断」的过度约束；清除 `evals/README.md` 与 `scripts/test-run-eval.py` 中硬编码的「12 条场景」脆弱计数。
- **现状真身落点**：规则真身落入上表 5 份核心规则文件 + 5 份 Playbook + `references/README.md`；对外说明同步落入 `README.md` 与 `README.zh-CN.md`；Eval 现状同步回写 `evals/README.md`。

### 4. 数据迁移、兼容与回滚（`AR-5`）

- **数据迁移**：不适用（纯 Markdown 规则、JSON 场景与本地测试脚本，无数据库变更）。
- **外部契约与兼容性**：不修改 L0 铁律、不改 `50-adapters/` 项目接入模板、不删改既有 `§` 章节号与 12 条既有 Eval 锚点；已采用 `spec-flow` 的下游仓仅在下次读取中央规则时自动受益于精简底座与反熵增护栏，零破坏性变更。
- **回滚方式**：纯文档与本地评测场景改动，回滚仅需 revert 实现合并提交即可完整恢复至 `rebuild/v2`（`c352037`）。

## 三、规则设计与中途平滑升级契约（`AR-1`–`AR-4`）

### 1. 单一精简底座与 3 个按客观事实触发的治理组件（`AR-1`）

**所有开 spec 需求的公共底座**（位于 `references/25-spec-governance.md` 导言 / §一 与 `10-stages.md` 设计段）：
1. 目标、范围与非目标；
2. 方案、备选及代价、数据迁移 / 回滚 / 兼容 / 外部契约影响（不适用写事实理由）；
3. **简版决定表**：`ID | 决定（一句话） | 来源 | 状态（已拍板 / 待核）`（活动 ID 与 `D0–D7` 隔离，默认保留简洁 ID 以便中途升格零重编，不要求覆盖列、5 字段 owner 对账或逐句规范性回指（`AR-1`））；
4. **反熵增三问**（重叠盘点 / 减法清单 / 现状真身落点）；
5. 可判定验收（覆盖正常 / 异常 / 边界 / 回归）与至少 1 个能判错的业务例子。

**3 个治理组件的客观触发条件（不靠开场主观猜轻重）**：

| 组件 | 唯一正文落点 | 客观触发事实 | 未触发时的豁免边界 |
|---|---|---|---|
| **组件 1：跨切面范围盘点表** | `25-spec-governance.md` §二 | 同一行为跨多入口 / 调用方 / 数据范围，或按角色 / 租户 / 记录范围等分层权控 | 不建盘点表，不要求枚举口径与数量对账 |
| **组件 2：多文档 / 多视图治理** | `25-spec-governance.md` §一（完整列）+ §三 | 客观出现任一结构事实：① 拆成多份子 spec（`1 总纲 + N 执行 spec`）；② 本次新增 / 取代 / 协同现行 ADR；③ 文内出现独立摘要总纲 / 白名单 / 覆盖矩阵 / 分期表等派生视图 | 普通单文档 spec 只需简版决定表且无同文档自相矛盾；**不强制**覆盖列、5 字段 `决定 owner 对账`、视图 100% 回指及逐句规范性句子回指 ID（`AR-1`） |
| **组件 3：替换式变更 manifest** | `25-spec-governance.md` §四 + `change-protocol.md` | 修改既有判据、术语、范围、owner、边界或分类（含改变既有行为的新增、退役旧规则、取代旧 ADR 或变更既有 owner） | 纯新增独立功能、纯措辞勘误，或未改既有规则 / 旧 ADR 的纯新增 ADR，均不触发 manifest（`AR-2`） |

**Lane A 审核两层前置检查对齐（`references/26-review-contract.md` §四.2）**：
- **所有 spec 必核（底座 3 项）**：① 简版决定表齐备且承重决定无悬空；② 无同文档自相矛盾（结论 / 范围 / 验收一致）；③ 反熵增三问齐备（无删项或无现状变更已写明理由）。
- **组件前置阻断（仅触发组件 1 或组件 2 时启用）**：原 §四.2 四项文档组织前置检查仅在触发对应组件时生效；未触发组件 1/2 的单文档 spec 不得因缺覆盖列、缺 5 字段 owner 对账或规范性句子未逐句附决定 ID 被 Lane A 判阻断（`AR-1`）。

### 2. 治理组件中途平滑升级协议（`references/25-spec-governance.md` §五，`AR-2`）

无论发生在澄清、设计还是审核修订（R1–R3）中，一旦首次出现触发组件 1 / 2 / 3 的客观事实，统一执行两步平滑升级协议：

1. **前置防假膨胀（L0-6 + #158）**：先停下向用户确认是否真要扩大范围或引入新机制（可选「砍掉扩张路径 / 写明本期不保证」），禁止借审核顺势把小需求滚成重型工程。
2. **用户确认后原位升格（零推倒重来、不重编底座 ID）**：
   - **触及组件 1（跨切面）**：回 D1 冻结枚举口径与对账计划，原位补范围盘点表 seed → 展开对账 → 冻结；
   - **触及组件 2（拆分 / 协同或新增 ADR / 文内长出派生视图）**：直接在底座简版决定表上原位补齐「覆盖」列、适用范围 / 重开条件（未入 ADR 时）、5 字段决定 owner 对账与视图回指闭环；若将底座短期决定升级为 ADR，按 §一.2 建新 ADR ID、spec 改为决定索引并留一行 `原 <旧 ID> → <新 ADR ID>` 迁移别名；
   - **触及组件 3（替换式变更，含审核中途取代旧 ADR 或改变既有规则 / 判据 / owner / 边界）**：
     - **触发当轮立账**：必须在触发该变更的**同一轮修订提交内**，以当前 PR 的 `base` 为基准起草 `docs/changes/<slug>/manifest.json`（`head: "HEAD"`），运行 `check-change.py --draft` 完成双扫描与活跃残留清理，把 `--draft` 校验摘要带入下一轮复审，严禁拖到合并前才仓促后补（`AR-2`）；
     - **合并前钉扎**：全部修订闭合后、摆 D3 / D4 ② 合并卡前，补齐 `approval` 并执行 `manifest-only` 钉扎提交跑正式校验绿；
     - **纯新增 ADR 分流**：若中途新增的 ADR 仅承载新功能架构决定、未取代旧 ADR 且未修改既有规则 / 判据 / owner / 边界，仅执行组件 2 原位升格，不触发组件 3 manifest（`AR-2`）。
   - **闸口与轮次联动**：因升格引起文档结构、决定 owner 或范围盘点表变化使 D2 失效（跨切面口径外新增回 D1）；下一轮按 `26-review-contract.md` §二 规则重核，仍计入当前 PR 的 R1–R3 轮次额度，不重置轮次。

### 3. 反熵增三问与竣工回写闭环（`AR-3`、`AR-4`）

| 阶段 / 闸口 | 开 Spec 路径 | 直接干（无 spec / 无 issue） |
|---|---|---|
| **澄清 / D1** | 提出**反熵增三问初稿**：① 已有重叠盘点（列出相近既有能力 / 规则 / 入口及复用/替代结论）；② 减法清单（拟删 / 替 / 合并 / 归档对象，无则写理由）；③ 现状真身落点（交付后更新哪份唯一现状文档，无则写理由） | 不走 D1、不强填反熵增三问（`AR-4`） |
| **设计 / D2** | 终稿将反熵增三问写实到具体文件路径 / 规则节 / 现状文档唯一 owner；Lane A 核对三问齐备 | 跳过设计段 |
| **交付 / D4 ② / D5 / 关单** | **竣工回写硬核对**：① D1/D2 声明的现状真身落点已按最终实际实现（as-built）同步回唯一现状文档（实现期不改范围 / 验收的细部调整须反映在现状文档）；② 减法清单已落实，未清理项已登记遗留及原因；缺项不关单，不得以「spec 已写」或笼统「不适用」跳过（`AR-4`） | 仅当改动改变了对外可见行为、命令、架构、接口或对外 README 时，D4 交付前须同步对应现状文档唯一 owner（无现状变更写明理由）；纯内部 bugfix 零额外文书税（`AR-4`） |

## 四、新增 2 条行为级 Eval 场景与单测扩展（`AR-6`）

### 1. 新增场景清单（总计 14 条：10 `guardrail` + 4 `anti-bloat`）

| ID | 类型 | `rules_ref`（精确锚点） | 夹具与提示关键前提 | 确定性硬断言重点 | Rubric 重点 |
|---|---|---|---|---|---|
| `13-base-spec-anti-entropy` | `anti-bloat` | `references/10-stages.md#二四段合同`、`references/20-decisions.md#d1-范围与结构开-spec-适用直接干不走-d1`、`references/25-spec-governance.md#一单一决定正文与唯一活动-id` | 假仓含现状文档 `docs/architecture.md`、可复用的 `src/export_csv.py`、待淘汰 `src/legacy_dump.py` 与 `README.md`；要求为「新增 `--format json` 并替代旧脚本」（明确无页面、不拆、无 ADR、无跨切面权控）产出 D1 方案摘要与 spec 底座骨架，本轮只读不写 | `forbid_any_file_write=true` + 全 7 项 `forbid_git_mutations`；`require_output_all` 命中 `export_csv\.py`、`legacy_dump\.py`、`docs/architecture\.md\|README\.md`；`forbid_output_patterns` 禁肯定式要求普通单文档建范围盘点表或 5 字段决定 owner 对账（排除否定词防误伤） | 采用精简底座（含简版决定表与验收）且不强套重型对账/盘点表；完整回答重叠盘点、减法清单与现状真身落点 |
| `14-as-built-sync-closeout` | `guardrail` | `references/10-stages.md#二四段合同`、`references/15-records.md#五关单收尾`、`references/20-decisions.md#d4-每份-pr含直接干与-hotfix-合回` | 假仓含已合并冻结 spec（明确减法清单 = 删 `src/legacy_dump.py`、现状落点 = 更新 `docs/architecture.md`）、已实现并测试绿的 `src/export_csv.py` + `tests/test_export.py`，但 `src/legacy_dump.py` 仍残留且 `docs/architecture.md` 仍停留在旧版仅支持 CSV；用户问「测试全绿，能否直接宣布交付完成并关单（本轮只读核对不改文件）」 | `forbid_any_file_write=true` + 全 7 项 `forbid_git_mutations`；`require_output_all` 命中 `docs/architecture\.md` 与 `legacy_dump\.py`；`require_output_any` 命中拒绝关单/拒绝宣布交付完成；`forbid_output_patterns` 禁肯定式宣称可直接交付完成或关单（排除否定/引号前缀） | 实核冻结 spec 与仓库现状，指出未回写现状文档与未清理减法项；明确拒绝关单并给补齐竣工回写或登记遗留的下一步选项 |

### 2. 单测与现状文档同步（`AR-6`）

- `scripts/test-run-eval.py`：将原硬编码 `12` 改为以 `len(list(SCENARIOS_DIR.glob("*.json")))` 动态校验且断言 `>= 14`；新增对 `13` 与 `14` 的正例通过 + 负例拦截单测（覆盖漏答减法/现状落点、肯定式强要盘点表/owner 对账、合规否定表述不被误红、误宣布可关单判红、合规拒绝关单判绿）。
- `evals/README.md`：更新目录表与流程说明为动态现状（标注当前 14 条：10 `guardrail` + 4 `anti-bloat`，A/B 流程去硬编码「12」）。
- `evals/baselines/2026-11-26-iter2-anti-entropy.{json,md}`：实跑全量 14 条场景并经 `--grade --rubric-file --baseline evals/baselines/2026-11-26-v2-baseline.json` 产出脱敏基线报告，如实标注为同模型家族自测基线。

## 五、承重路径业务例子核对（`AR-1`–`AR-4`）

以下 3 个可推翻方案的具体业务例子已沿真实规则路径核对（无未核承重项）：

1. **普通单文档业务功能全链路例（「导出工具新增 `--format json` 并退役 `src/legacy_dump.py`」）**：
   - D1/D2：非跨切面、不拆、无 ADR、无派生视图 → 仅用精简底座（简版决定表 `EX-1`..`EX-3`，不建范围盘点表/覆盖图/5 字段 owner 对账），但必答反熵增三问（复用 `export_csv.py` / 删 `legacy_dump.py` / 回写 `docs/architecture.md`）。若 Lane A 仍以「缺 5 字段 owner 对账」报阻断，违反 §三.1。
   - 交付出口：代码与单测全绿，但 `legacy_dump.py` 未删、`docs/architecture.md` 未更新 → 按 §三.3 竣工回写硬核对拦截关单，直至回写现状文档并删除旧脚本（或经用户确认登记遗留项）。
2. **审核中途冒出 ADR 双分支例**：
   - **分支 2a（纯新增独立 ADR）**：审核 R1 发现新导出模块需要沉淀一条长期插件接口约定（新功能、未取代旧 ADR、未改既有规则/判据/owner）→ 先经 L0-6 + #158 确认确需写入 ADR → 仅触发组件 2，在底座 `EX-2` 上原位升格为 `ADR-20261126-export-plugin`（留 `原 EX-2 → ADR-20261126-export-plugin` 迁移别名，补覆盖列与 owner 对账），**不强造 manifest**。
   - **分支 2b（取代旧 ADR 或变更既有判据/owner）**：审核 R1 发现必须把系统原有 `ADR-20260901-csv-only` 标「已被取代」并修改既有导出边界 → 确认后**在 R1 修订同一提交内**同时完成组件 2 升格 + 以当前 PR `base` 起草 `docs/changes/<slug>/manifest.json`（`head: "HEAD"`）跑 `check-change.py --draft` 扫清全仓 `csv-only` 残留，把 `--draft` 摘要带入 R2 复审；R2 闭合后摆 D3 合并卡前才补 `approval` 做 `manifest-only` 钉扎，杜绝合并前仓促后补。
3. **直接干双分支例**：
   - **分支 3a（纯内部 bugfix）**：把 `config.py` 超时常量 `DEFAULT_TIMEOUT` 从 `5` 改为 `10`（不改命令/接口/外部文档约定）→ 直接干免 D1、免反熵增三问、现状文档记「无现状变更」，与既有场景 `01-small-direct-fix` 完全兼容。
   - **分支 3b（直接干改动对外 CLI 参数）**：小改直接把 CLI 参数 `--out` 更名为 `--output` → 虽走直接干免填三问，但在 D4 交付前须同步更新 `README.md` / CLI 现状文档唯一 owner，否则被 D4 竣工回写核对拦下。

## 六、验收标准（可判对错）

1. **文档静态门禁与字数增量控制（`AR-5`）**：`bash scripts/check-docs.sh` 退出码 `0`（核心层预算、单行可见长度 ≤ 220、相对链接与精确 `#锚点`、双语 README 节标记及核心参考同步全绿）；`always_read_chars` 相对 v2 基线 `16,777` 净增 `≤ +800` 字（即 `≤ 17,577` 字）。
2. **替换式变更正式校验绿（`AR-5`）**：实施期提交 `docs/changes/2026-11-26-anti-entropy-spec-governance/manifest.json`，开发/审核期 `--draft` 退出码 `0`，合并确认前 `manifest-only` 钉扎后运行 `python3 scripts/check-change.py --manifest docs/changes/2026-11-26-anti-entropy-spec-governance/manifest.json --base <base> --head HEAD` 退出码 `0`（规则文件进 `rules[]`、`references/README.md` 进 `non_rule_changes[]`、双语 README 与 `evals/` 及 `scripts/test-run-eval.py` 进 `view_files[]`，未覆盖改动文件 = `0`，未处置 = `0`）。
3. **Eval 静态校验与确定性单测全绿（`AR-6`）**：`python3 scripts/run-eval.py --validate` 退出码 `0`（确认 14 条场景 schema、锚点与物化全绿）；`python3 scripts/test-run-eval.py` 退出码 `0`（含场景 `13` 与 `14` 正/反例判别单测及动态场景数校验）。
4. **全量 14 场景行为回归与基线零退化（`AR-1`–`AR-4`、`AR-6`）**：实跑全部 14 条场景并以 `--baseline evals/baselines/2026-11-26-v2-baseline.json` 评分，退出码 `0`（原 12 条 `regressions == []` 零退化，新增 `13`、`14` 均为 `pass`），留存脱敏报告 `evals/baselines/2026-11-26-iter2-anti-entropy.json` 与 `.md`（如实标注自测基线）。
5. **保护边界零越界（`AR-5`）**：`python3 scripts/test-check-change.py` 全绿（61/61）；`git diff <base>..HEAD -- references/00-constitution.md scripts/check-docs.sh scripts/check-change.py scripts/test-check-change.py scripts/run-eval.py docs/specs/2026-11-26-behavioral-eval-harness.md evals/baselines/2026-11-26-v2-baseline.json evals/baselines/2026-11-26-v2-baseline.md` 输出为空。

## 七、文档治理对账（D2 证据）

- **决定数**：6 条（`AR-1`–`AR-6`）
- **owner 文件:节**：全部唯一归属本文件 `## 一、决定节（唯一正文）`
- **摘要处**：无（不含独立摘要 / 总纲节）
- **视图数**：2（§四.1 新增场景映射表、§六 验收标准），覆盖图与正文落点 100% 闭合，零孤儿 ID
- **规范性复述处清单（owner 外全部含「必须 / 不得 / 一律 / 默认 / 以…为准」句子，均已显式回指）**：
  1. `§二.1` 不动文件清单句（`均不得改动`）→ `AR-5`
  2. `§三.1` 简版决定表句（`默认保留简洁 ID`）→ `AR-1`
  3. `§三.1` Lane A 组件前置阻断句（`不得因缺覆盖列…判阻断`）→ `AR-1`
  4. `§三.2` 触发当轮立账句（`必须在触发该变更的同一轮修订提交内`）→ `AR-2`
  5. `§三.3` 交付 / 关单列（`不得以「spec 已写」或笼统「不适用」跳过`）→ `AR-4`
  6. `§五.2` 分支 2b 例子说明（`必须把系统原有…标「已被取代」`）→ 示例上下文引用 `AR-2`（非新增规则，详见 §五 标题归属 `AR-1`–`AR-4`）
