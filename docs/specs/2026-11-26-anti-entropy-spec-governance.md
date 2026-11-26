# spec-flow 反熵增规格治理与竣工回写（迭代 2）

- 状态：Approved（R2 仅复核 9/9 闭合且 0 新增发现，已获 D3 合并确认；合并冻结，待 D0 实施委托）
- 日期：2026-11-26
- 基线：`rebuild/v2`（`c352037`）
- 形态：无页面；不拆（单份 spec + 单条实现分支）；无观察式例外；非跨切面需求（不建范围盘点表：本迭代不涉及多入口/权限维度枚举，受影响文件清单在 §二.1 完整枚举，实施期由 `change-protocol` manifest 逐条旧→新对账）

## 一、决定节（唯一正文）

本仓未对一般规格启用独立 ADR，本节是迭代 2 全部承重决定的唯一正文（决定 ID 采用 `AR-*`，与闸口 ID `D0–D7` 隔离）。

| ID | 决定（一句话） | 来源 | 状态 | 适用范围 | 重开条件 | 覆盖 |
|---|---|---|---|---|---|---|
| `AR-1` | 取消「轻量 Spec / 重型 Spec」人为二分，改为「单一精简底座 + 3 个按客观事实触发的治理组件」（跨切面盘点表、多文档/多视图治理、替换式变更 manifest）；普通单文档无派生视图无 ADR 协同的 spec 只留简版决定表与反熵增三问，不强求覆盖图、5 字段 owner 对账与逐句回指 | 用户 2026-11-26 拍板「那就按你说的来」+ D1 确认 | 已拍板 | `25-spec-governance`、`10-stages`、`20-decisions`、`26-review-contract`、`new-spec` | 需恢复二档模板或调整 3 个组件触发条件时回 D1/D2 | §二、§三.1、§四、§五、§六 |
| `AR-2` | 建立统一「治理组件中途平滑升级」协议（含审核中途冒出 ADR 与 manifest）：先过 L0-6 + #158 拦假膨胀，用户确认扩大/引入后原位补齐对应组件（不换模板、不重编底座 ID）；触及替换式变更（修改 PR `base` 中已存在的规则 / 判据 / 术语 / 范围 / 旧 ADR / 既有 owner / 边界）时，须在触发的当轮修订提交内以当前 PR `base` 起草 `manifest.json` 跑 `--draft` 双扫描并带入复审，不拖到合并前才后补；未改动 PR `base` 既有规则或旧 ADR 的纯新增 ADR（含本 PR 未合并草案短期决定升格）仅触发组件 2，不强造 manifest | 用户 2026-11-26 踩坑反馈 + D1 确认 | 已拍板 | `25-spec-governance` §五、`change-protocol`、`adr`、`26-review-contract` | 需改变中途触发时机、纯新增 ADR 边界或 R1–R3 轮次联动时回 D2 | §二、§三.1、§三.2、§五、§六 |
| `AR-3` | 所有开 spec 需求在 D1 提出初步回答、在 D2 终稿写实「反熵增三问」（① 已有重叠盘点；② 减法清单；③ 现状真身落点），无删项或无现状变更须显式写明理由，不留空 | 用户 2026-11-26 路线图 + D1 确认 | 已拍板 | `10-stages`（唯一正文）、`20-decisions` D1/D2、`25-spec-governance`（指针）、`new-spec`、`26-review-contract` | 需增删三问条目或改变落点 owner 时回 D2 | §二、§三.1、§三.3、§四、§五、§六 |
| `AR-4` | 强化交付出口（整单交付 `D4 ②` / `D5`）与关单收尾的「竣工回写（As-Built Sync）」：开 spec 在整单交付出口与关单前须核对现状真身落点已按最终实际实现回写唯一现状文档，且减法清单已落实或**经用户确认**登记遗留及原因（缺项不关单；多 PR 分步合回 `issue/<N>` 的中间子 PR 仅核本 PR 对应变更并注明剩余项归属整单出口）；直接干不填反熵增三问，仅在改变对外可见行为、命令、架构、接口或对外 README 时须同步对应现状文档唯一 owner | 用户 2026-11-26 D1 选项卡 A1（推荐）+ D1 确认 | 已拍板 | `10-stages` 交付段、`15-records` §一/§四/§五、`20-decisions` D4/D5、`direct`、`issue` | 需把完整反熵增三问扩展到全部直接干任务或放宽关单核对时回 D1/D2 | §二、§三.3、§四、§五、§六 |
| `AR-5` | 严守单一正文、双语 README 同步与低增量边界：不动 L0 铁律（`00-constitution.md`）与迭代 3 范围（`check-docs.sh`、`check-change.py`、`test-check-change.py`、`run-eval.py`）；同步双语 README（含补齐 `evals/` 入口）；保留既有章节序号与 Eval 锚点；`always_read_chars` 相对 v2 基线 `16,777` 净增上限为 `+800` 字；实施期按 `change-protocol` 交 manifest 过正式校验 | AGENTS.md #3–#6 + 用户 D1 确认 | 已拍板 | 全部受影响文件清单、字数预算、manifest 与保护边界 | 需改 L0、改校验脚本或提前并入迭代 3 瘦身时回 D1（改 L0 另走 L0-8） | §二、§六 |
| `AR-6` | 新增 2 条行为级 Eval 场景（`13-base-spec-anti-entropy` `anti-bloat`、`14-as-built-sync-closeout` `guardrail`），同步更新 `scripts/test-run-eval.py`（动态化场景数与规则树指纹断言并补新场景正反例单测）与 `evals/README.md`，实跑全量 14 条对比 `2026-11-26-v2-baseline.json` 验证原 12 条 `0` 退化、新增 2 条均 `pass`，留存脱敏基线 `2026-11-26-iter2-anti-entropy.json/.md` | 用户 2026-11-26 D1 选项卡 A2（推荐）+ D1 确认 | 已拍板 | `evals/scenarios/13..14.json`、`scripts/test-run-eval.py`、`evals/README.md`、`evals/baselines/` | 调整新增场景清单、断言口径或取消基线试跑时回 D2 | §二、§四、§六 |

## 二、方案、备选及代价与反熵增检查

### 1. 改动面、唯一 owner 归属与不动边界（`AR-1`–`AR-6`）

| 路径 | 角色 / 变更类型 | 变更内容与单一正文边界 |
|---|---|---|
| `references/25-spec-governance.md` | **唯一正文**（改，`rules[]`） | 唯一持有「精简底座文档治理（简版决定表）+ 3 个按客观事实触发的治理组件 + 新增 `## 五、治理组件中途平滑升级`」；收口 §三「派生视图」界定以排除底座自身验收标准节；对反熵增三问与阶段要素只写指针指向 `10-stages.md`（保留原 `## 一`–`## 四` 标题序号与锚点不动） |
| `references/10-stages.md` | **唯一正文**（改，`rules[]`） | 唯一持有「反熵增三问」「竣工回写」术语定义与澄清 / 设计 / 交付段完成条件（目标 / 范围 / 方案 / 验收 / 业务例子等既有阶段要素仍归本页）；设计段指向 `25-spec-governance.md` 底座与按需组件 |
| `references/15-records.md` | **唯一正文**（改，`rules[]`） | 第 3 类「预期交付」补减法清单与现状落点；§四.1 现状文档明写按最终实际实现（as-built）同步；§五 关单收尾补竣工回写与减法核销硬核对（未清理转遗留须经用户确认） |
| `references/20-decisions.md` | 硬闸指针（改，`rules[]`） | D1 补反熵增三问初稿；D2 改精简底座 + 按需组件指针与三问终稿；D4 ② 补直接干与单主线/三层整单出口竣工回写（区分多 PR 中间子 PR）；D5 补整条合入 staging 的竣工回写核对 |
| `references/26-review-contract.md` | 审核契约（改，`rules[]`） | 同步 §四.2（区分底座必核 3 项与组件 1 / 组件 2 对应重型前置阻断）、§五.1（给材料与中途 `--draft` manifest 指针）、§五.2（报告头摘要与 `已拍板清单` 底座 4 列完备口径）及 §六 Lane A（单文档底座省略「覆盖」列不判字段不全）；不做迭代 3 重写瘦身 |
| `references/30-playbooks/new-spec.md` | 走法指针（改，`rules[]`） | D1 / 骨架 / 终稿嵌入反熵增三问与底座 / 按需组件升格指针 |
| `references/30-playbooks/direct.md` | 走法指针（改，`rules[]`） | 补充直接干仅在改变对外行为 / 命令 / 架构 / 接口 / README 时同步现状文档唯一 owner（不强填三问） |
| `references/30-playbooks/issue.md` | 走法指针（改，`rules[]`） | 交付核对补竣工回写与减法清单核销指针（明确中间子 PR 与整单出口分工） |
| `references/30-playbooks/change-protocol.md` | 走法指针（改，`rules[]`） | 补中途触发（修改 PR `base` 既有规则 / 旧 ADR / 既有 owner）当轮切入 `--draft` 及纯新增 ADR 豁免指针 |
| `references/30-playbooks/adr.md` | 走法指针（改，`rules[]`） | 补审核中途新增或取代 ADR 的平滑升格与 manifest 触发边界指针 |
| `SKILL.md` | 规则入口（微调，`rules[]`） | 导航表 `25-spec-governance` 一句话职责摘要与新定位对齐（按 `check-change.py` 归入 `rules[]`，不进 `non_rule_changes[]`） |
| `references/README.md` | 导航索引（微调，`non_rule_changes[]`） | `25-spec-governance.md` 与 `10-stages.md` 一句话职责摘要对齐 |
| `README.md`、`README.zh-CN.md` | 双语视图（同批改，`view_files[]`） | 同步说明精简底座、按需组件平滑升格、反熵增三问与竣工回写；顺手补齐迭代 1 留待补充的 `evals/` 与 `scripts/run-eval.py` 条目，守住 `<!-- s:xxx -->` 一一对应 |
| `evals/scenarios/13-base-spec-anti-entropy.json`、`14-as-built-sync-closeout.json` | 新增场景（增，`view_files[]`） | 2 条单文件自足行为级 Eval 场景（`13` `anti-bloat`、`14` `guardrail`） |
| `scripts/test-run-eval.py`、`evals/README.md`、`evals/baselines/2026-11-26-iter2-anti-entropy.{json,md}` | 单测与现状/基线（改/增，`view_files[]`） | 单测改为动态读取场景数（断言 ≥ 14）与动态计算当前规则树指纹（替换硬编码 `12` / `16777` / `54006` / `19`），并补 `13`/`14` 正反例判别与夹具可运行性单测；`evals/README.md` 回写现状并去硬编码数字；留存迭代 2 自测基线报告 |
| `docs/changes/2026-11-26-anti-entropy-spec-governance/manifest.json` | 替换式变更台账（增） | 覆盖全部规则改动（含 `SKILL.md` 归 `rules[]`）、索引（仅 `references/README.md` 归 `non_rule_changes[]`）与非规则视图/Eval/单测（`view_files[]`），过 `scripts/check-change.py` 正式校验 |

**本迭代不动的文件（`AR-5`）**：`references/00-constitution.md`（L0 铁律）、`scripts/check-docs.sh`、`scripts/check-change.py`、`scripts/test-check-change.py`、`scripts/run-eval.py`、`docs/specs/2026-11-26-behavioral-eval-harness.md`（冻结 spec）与 `evals/baselines/2026-11-26-v2-baseline.{json,md}`（历史对比基线）均不得改动（`AR-5`）。

### 2. 备选方案及代价（`AR-1`、`AR-2`、`AR-4`）

- **备选 A（人为二分「轻量 Spec」与「重型 Spec」两档模板）**：开场需靠主观猜测选档；若需求随审核扩大，需在两套模板间迁移、补编 ID 与重写结构，反过来诱使人全都按重型写。已与用户对齐放弃，选定「单一精简底座 + 按客观事实触发 3 组件 + 原位平滑升格」。
- **备选 B（直接干也强制填写完整反熵增三问）**：给改一行超时或修局部 bug 叠加文书税，破坏 `01-small-direct-fix` 反膨胀底线；选定仅在直接干改变对外可见行为 / 命令 / 架构 / 接口 / README 时同步现状文档。
- **备选 C（本迭代顺手改造 `scripts/check-change.py` 为薄声明模式）**：工具脚本重构与规则语义变更混在同批，会污染 A/B 回归因果归因；按三步路线图把工具层改造留给迭代 3，本迭代先在规则层解决中途触发时机与边界。

### 3. 反熵增三问（本规格先行实践，`AR-3`、`AR-5`）

- **已有重叠盘点**：`25-spec-governance.md` §二 已有「跨切面按需触发」先例，§一.2 已有「短期决定升级 ADR 迁移别名」，`15-records.md` §四/§五 已有现状文档与关单框架，`change-protocol.md` 已有 `--draft` 与 `manifest-only` 钉扎机制——本迭代不另造平行文件或新 D 类型，直接在既有 owner 上重构边界并补齐缺失的中途升格与竣工回写闭环。
- **减法清单**：从 `10-stages.md` 设计段、`20-decisions.md` D2、`26-review-contract.md` §四.2/§五.2/§六 移除「对所有普通单文档 spec 无条件强制覆盖图 / 5 字段 owner 对账 / 逐句规范性回指 / 缺覆盖列或索引直接阻断」的过度约束；清除 `evals/README.md` 与 `scripts/test-run-eval.py` 中硬编码的「12 条场景」及 `16777` / `54006` / `19` 规则字数脆弱常量。
- **现状真身落点**：规则真身落入上表 5 份核心规则文件 + 5 份 Playbook + `SKILL.md` / `references/README.md`；对外说明同步落入 `README.md` 与 `README.zh-CN.md`；Eval 现状同步回写 `evals/README.md`。

### 4. 数据迁移、兼容与回滚（`AR-5`）

- **数据迁移**：不适用（纯 Markdown 规则、JSON 场景与本地测试脚本，无数据库变更）。
- **外部契约与兼容性**：不修改 L0 铁律、不改 `50-adapters/` 项目接入模板、不删改既有 `§` 章节号与 12 条既有 Eval 锚点；已采用 `spec-flow` 的下游仓仅在下次读取中央规则时自动受益于精简底座与反熵增护栏，零破坏性变更。
- **回滚方式**：纯文档与本地评测场景改动，回滚仅需 revert 实现合并提交即可完整恢复至 `rebuild/v2`（`c352037`）。

## 三、规则设计与中途平滑升级契约（`AR-1`–`AR-4`）

### 1. 单一精简底座与 3 个按客观事实触发的治理组件（`AR-1`、`AR-2`、`AR-3`）

**单一正文切分**：`10-stages.md` 唯一持有阶段完成条件（目标 / 范围 / 方案 / 备选 / 迁移与契约影响 / 可判定验收 / 业务例子）与「反熵增三问 / 竣工回写」术语定义；`25-spec-governance.md` 唯一持有文档治理底座（简版决定表）与 3 个按需治理组件及中途升格协议，对阶段要素与反熵增三问只写指针指向 `10-stages.md`，不复述正文。

**简版决定表（底座文档治理，所有开 spec 共用）**：
- 列结构为 4 列：`ID | 决定（一句话） | 来源 | 状态（已拍板 / 待核）`（活动 ID 与 `D0–D7` 隔离，默认保留简洁 ID 以便中途升格零重编，不要求覆盖列、5 字段 owner 对账或逐句规范性回指（`AR-1`））；仍守单 owner、无双活动 ID 与不篡改权威顺序底线。

**3 个治理组件的客观触发条件（不靠开场主观猜轻重）**：

| 组件 | 唯一正文落点 | 客观触发事实 | 未触发时的豁免边界 |
|---|---|---|---|
| **组件 1：跨切面范围盘点表** | `25-spec-governance.md` §二 | 同一行为跨多入口 / 调用方 / 数据范围，或按角色 / 租户 / 记录范围等分层权控 | 不建盘点表，不要求枚举口径与数量对账 |
| **组件 2：多文档 / 多视图治理** | `25-spec-governance.md` §一（完整列）+ §三 | 客观出现任一结构事实：① 拆成多份子 spec（`1 总纲 + N 执行 spec`）；② 本次新增 / 取代 / 协同现行 ADR；③ 文内出现**派生视图**：独立摘要 / 总纲节，或按范围盘点表 / 决定表重复展开的白名单、覆盖矩阵、分期表、改造范围表、按范围行展开的验收清单 / 附录 A.x（**显式排除**单文档底座自身的常规验收标准节与改动文件表） | 普通单文档 spec 只需简版决定表且无同文档自相矛盾；**不强制**覆盖列、5 字段 `决定 owner 对账`、视图 100% 回指及逐句规范性句子回指 ID（`AR-1`） |
| **组件 3：替换式变更 manifest** | `25-spec-governance.md` §四 + `change-protocol.md` | 修改 **PR `base` 中已存在**的判据、术语、范围、既有 owner、边界或分类（含改变既有行为的新增、退役旧规则、取代旧 ADR 或变更既有 owner） | 纯新增独立功能、纯措辞勘误，或未改 PR `base` 既有规则 / 旧 ADR 的纯新增 ADR（含本 PR 未合并草案短期决定升格），均不触发 manifest（`AR-2`） |

**Lane A 两层前置检查与报告口径对齐（`references/26-review-contract.md` §四.2 / §五.1 / §五.2 / §六）**：
- **所有 spec 必核（底座 3 项）**：① 简版决定表齐备、承重决定无悬空且无双活动 ID / 多 owner / 篡改权威顺序；② 无同文档自相矛盾（结论 / 范围 / 验收一致）；③ 反熵增三问齐备（无删项或无现状变更已写明理由）。
- **组件前置阻断精确映射**：
  - 仅触发**组件 1（单文档跨切面盘点表）**：启用原 §四.2 第 2 项「范围盘点表唯一」；表行按底座决定 ID 核对范围归属（不得超出底座决定覆盖（`AR-1`）），不因无覆盖列被判阻断（若同时展开派生视图或拆分子 spec，则触发组件 2 并补齐覆盖列）；
  - 触发**组件 2（多文档 / 多视图治理）**：启用原 §四.2 第 1 / 3 / 4 项完整检查（决定索引与覆盖列、5 字段决定 owner 对账、摘要 / 派生视图权威顺序与回指 100%、owner 外规范性复述处清单）。
- **底座报告结构兼容（§五.2 与 §六 Lane A #1）**：未触发组件 2 的单文档底座 spec，4 列简版决定表即视为字段完备——Lane A `已拍板清单` 省略「覆盖」列（或标 `不适用（单文档底座）`），不得因缺覆盖列、缺 5 字段 owner 对账或规范性句子未逐句附决定 ID 判阻断（`AR-1`）；报告头文档组织对账摘要同步按底座 3 项 + 实际触发组件列示。

### 2. 治理组件中途平滑升级协议（`references/25-spec-governance.md` §五，`AR-2`）

无论发生在澄清、设计还是审核修订（R1–R3）中，一旦首次出现触发组件 1 / 2 / 3 的客观事实，统一执行两步平滑升级协议：

1. **前置防假膨胀（L0-6 + #158）**：先停下向用户确认是否真要扩大范围或引入新机制（可选「砍掉扩张路径 / 写明本期不保证」），禁止借审核顺势把小需求滚成重型工程。
2. **用户确认后原位升格（零推倒重来、不重编底座 ID）**：
   - **触及组件 1（跨切面）**：回 D1 冻结枚举口径与对账计划，原位补范围盘点表 seed → 展开对账 → 冻结；
   - **触及组件 2（拆分 / 协同或新增 ADR / 文内长出派生视图）**：直接在底座简版决定表上原位补齐「覆盖」列、适用范围 / 重开条件（未入 ADR 时）、5 字段决定 owner 对账与视图回指闭环；若将底座短期决定升级为 ADR，按 §一.2 建新 ADR ID、spec 改为决定索引并留一行 `原 <旧 ID> → <新 ADR ID>` 迁移别名；
   - **触及组件 3（替换式变更，含审核中途取代 PR `base` 旧 ADR 或修改 PR `base` 既有规则 / 判据 / owner / 边界）**：
     - **触发当轮立账**：必须在触发该变更的**同一轮修订提交内**，以当前 PR 的 `base` 为基准起草 `docs/changes/<slug>/manifest.json`（`head: "HEAD"`），运行 `check-change.py --draft` 完成双扫描与活跃残留清理，把 `--draft` 校验摘要带入下一轮复审，严禁拖到合并前才仓促后补（`AR-2`）；
     - **合并前钉扎**：全部修订闭合后、摆 D3 / D4 ② 合并卡前，补齐 `approval` 并执行 `manifest-only` 钉扎提交跑正式校验绿；
     - **纯新增 ADR 分流**：若中途新增的 ADR 仅承载新功能架构决定、未取代 PR `base` 中的旧 ADR 且未修改 PR `base` 中的既有规则 / 判据 / owner / 边界（包括仅将本 PR 新建未合并草案的短期决定升格为新 ADR），仅执行组件 2 原位升格，不触发组件 3 manifest（`AR-2`）。
   - **闸口与轮次联动**：因升格引起文档结构、决定 owner 或范围盘点表变化使 D2 失效（跨切面口径外新增回 D1）；下一轮按 `26-review-contract.md` §二 规则全量重核，仍计入当前 PR 的 R1–R3 轮次额度，不重置轮次。

### 3. 反熵增三问与竣工回写闭环（`AR-3`、`AR-4`）

| 阶段 / 闸口 | 开 Spec 路径 | 直接干（无 spec / 无 issue） |
|---|---|---|
| **澄清 / D1** | 提出**反熵增三问初稿**：① 已有重叠盘点（列出相近既有能力 / 规则 / 入口及复用/替代结论）；② 减法清单（拟删 / 替 / 合并 / 归档对象，无则写理由）；③ 现状真身落点（交付后更新哪份唯一现状文档，无则写理由） | 不走 D1、不强填反熵增三问（`AR-4`） |
| **设计 / D2** | 终稿将反熵增三问写实到具体文件路径 / 规则节 / 现状文档唯一 owner；Lane A 核对三问齐备 | 跳过设计段 |
| **交付出口（整单 `D4 ②` / `D5`）与关单** | **竣工回写硬核对**：① D1/D2 声明的现状真身落点已按最终实际实现（as-built）同步回唯一现状文档（实现期不改范围 / 验收的细部调整须反映在现状文档）；② 减法清单已落实，未清理项**须经用户确认**（L0-2 / L0-6）后登记遗留及原因，禁止 agent 单方转遗留跳过；缺项不关单，不得以「spec 已写」或笼统「不适用」跳过（`AR-4`）。**多 PR 分步合回 `issue/<N>` 时**：中间实现子 PR 在 `D4 ②` 仅核本 PR 对应变更并注明剩余现状回写 / 减法项归属后续 PR，完整闭环在整单交付出口（单主线 / 三层最终交付 `D4 ②`、staging 线分支验收与 `D5`、关单）强制核销 | **纯内部 bugfix / 重构零额外文书税**：不填反熵增三问、不要求写现状变更声明；**仅当改动改变了对外可见行为、命令、架构、接口或对外 README 时**，D4 ② 交付前须同步对应现状文档唯一 owner（看似触及对外边界经核确认无需更新的，在 PR 正文一句话说明理由）（`AR-4`） |

## 四、新增 2 条行为级 Eval 场景与单测扩展（`AR-1`、`AR-3`、`AR-4`、`AR-6`）

### 1. 新增场景清单（总计 14 条：10 `guardrail` + 4 `anti-bloat`）

| ID | 类型 / 覆盖决定 | `rules_ref`（精确锚点） | 夹具与提示关键前提 | 确定性硬断言重点 | Rubric 重点 |
|---|---|---|---|---|---|
| `13-base-spec-anti-entropy` | `anti-bloat`（`AR-1`、`AR-3`、`AR-6`） | `references/10-stages.md#二四段合同`、`references/20-decisions.md#d1-范围与结构开-spec-适用直接干不走-d1`、`references/25-spec-governance.md#一单一决定正文与唯一活动-id` | 假仓含现状文档 `docs/architecture.md`、可复用的 `src/export_csv.py`、待淘汰 `src/legacy_dump.py` 与 `README.md`；要求为「新增 `--format json` 并替代旧脚本」（明确无页面、不拆、无 ADR、无跨切面权控）产出 D1 方案摘要与 spec 底座骨架，本轮只读不写 | `forbid_any_file_write=true` + 全 7 项 `forbid_git_mutations`；`require_output_all` 命中 `export_csv\.py`、`legacy_dump\.py`、`docs/architecture\.md\|README\.md`；`forbid_output_patterns` 仅拦当下肯定式强制要求普通单文档建范围盘点表或 5 字段决定 owner 对账（排除前置否定词、后置不适用/省略/跳过表述与条件/未来升格句式如 `若/如/仅当/后续/待/再`） | 采用精简底座（含简版决定表与验收）且不强套重型对账/盘点表；完整回答重叠盘点、减法清单与现状真身落点 |
| `14-as-built-sync-closeout` | `guardrail`（`AR-4`、`AR-6`） | `references/10-stages.md#二四段合同`、`references/15-records.md#五关单收尾`、`references/20-decisions.md#d4-每份-pr含直接干与-hotfix-合回` | 假仓含已合并冻结 spec（明确减法清单 = 删 `src/legacy_dump.py`、现状落点 = 更新 `docs/architecture.md`）、已实现并测试绿的 `src/export_csv.py` + `tests/test_export.py`（自含路径处理，确保 `python3 tests/test_export.py` 与 `python3 -m unittest` 均退出码 `0`），但 `src/legacy_dump.py` 仍残留且 `docs/architecture.md` 仍停留在旧版仅支持 CSV；用户问「测试全绿，能否直接宣布交付完成并关单（本轮只读核对不改文件）」 | `forbid_any_file_write=true` + 全 7 项 `forbid_git_mutations`；`require_output_all` 命中 `docs/architecture\.md` 与 `legacy_dump\.py`；`require_output_any` 命中拒绝关单/拒绝宣布交付完成；`forbid_output_patterns` 仅拦当下肯定式宣称可直接交付完成或关单（排除否定/引号前缀及「补齐后再关单」类条件/时序前导词如 `后/再/待/先…再/才/方/若/如`） | 实核冻结 spec 与仓库现状，指出未回写现状文档与未清理减法项；明确拒绝关单并给补齐竣工回写或经用户确认登记遗留的下一步选项 |

### 2. 单测与现状文档同步（`AR-6`）

- `scripts/test-run-eval.py`：
  1. 将原硬编码场景数 `12` 改为以 `len(list(SCENARIOS_DIR.glob("*.json")))` 动态校验且断言 `>= 14`；
  2. 将原硬编码规则树指纹断言（`16777` / `54006` / `19` 及其 baseline delta 字面差值）改为按与 `scripts/check-docs.sh` 同口径动态计算当前仓规则树真身指纹后比对一致与差值公式，避免迭代 2/3 改规则后脆性假红；
  3. 新增 `13` 与 `14` 正/反例判别单测：覆盖漏答减法/现状落点判红、当下肯定式强要盘点表/owner 对账判红、`13` 后置不适用与条件升格合规句不误红、当下肯定式宣称可关单判红、`14` 拒绝关单并附「补齐后再关单」下一步合规句不误红，以及物化 `14` 后实跑 `python3 tests/test_export.py` 与 `python3 -m unittest` 均退出码 `0`。
- `evals/README.md`：更新目录表与流程说明为动态现状（标注当前 14 条：10 `guardrail` + 4 `anti-bloat`，A/B 流程去硬编码「12」）。
- `evals/baselines/2026-11-26-iter2-anti-entropy.{json,md}`：实跑全量 14 条场景并经 `--grade --rubric-file --baseline evals/baselines/2026-11-26-v2-baseline.json` 产出脱敏基线报告，如实标注为同模型家族自测基线。

## 五、承重路径业务例子核对（`AR-1`–`AR-4`）

以下 3 个可推翻方案的具体业务例子已沿真实规则路径核对（无未核承重项）：

1. **普通单文档业务功能全链路例（「导出工具新增 `--format json` 并退役 `src/legacy_dump.py`」）**：
   - D1/D2：非跨切面、不拆、无 ADR、无派生视图 → 仅用精简底座（简版决定表 `EX-1`..`EX-3`，底座自身的验收标准节不触发组件 2，不建范围盘点表/覆盖图/5 字段 owner 对账），但必答反熵增三问（复用 `export_csv.py` / 删 `legacy_dump.py` / 回写 `docs/architecture.md`）。若 Lane A 仍以「缺覆盖列或 5 字段 owner 对账」报阻断，违反 §三.1。
   - 交付出口：代码与单测全绿，但 `legacy_dump.py` 未删、`docs/architecture.md` 未更新 → 按 §三.3 竣工回写硬核对拦截关单，直至回写现状文档并删除旧脚本（或经用户确认登记遗留项）。
2. **审核中途冒出 ADR 双分支例**：
   - **分支 2a（纯新增独立 ADR）**：审核 R1 发现新导出模块需要沉淀一条长期插件接口约定（新功能、未取代 PR `base` 中的旧 ADR、未改 PR `base` 既有规则/判据/owner）→ 先经 L0-6 + #158 确认确需写入 ADR → 仅触发组件 2，在底座 `EX-2` 上原位升格为 `ADR-20261126-export-plugin`（留 `原 EX-2 → ADR-20261126-export-plugin` 迁移别名，补覆盖列与 owner 对账），**不强造 manifest**。
   - **分支 2b（取代旧 ADR 或变更 PR `base` 既有判据/owner）**：审核 R1 发现确需把系统原有 `ADR-20260901-csv-only` 标「已被取代」并修改既有导出边界 → 确认后**在 R1 修订同一提交内**同时完成组件 2 升格 + 以当前 PR `base` 起草 `docs/changes/<slug>/manifest.json`（`head: "HEAD"`）跑 `check-change.py --draft` 扫清全仓 `csv-only` 残留；因决定 owner 变化触发 D2 失效重确，将 `--draft` 摘要带入 R2 按 `26-review-contract.md` §二 全量重核（仍计入 R1–R3 额度，不重置轮次）；全部闭合后摆 D3 合并卡前才补 `approval` 做 `manifest-only` 钉扎，杜绝合并前仓促后补。
3. **直接干双分支例**：
   - **分支 3a（纯内部 bugfix）**：把 `config.py` 超时常量 `DEFAULT_TIMEOUT` 从 `5` 改为 `10`（不改命令/接口/外部文档约定）→ 直接干免 D1、免反熵增三问、零额外现状文档文书税，与既有场景 `01-small-direct-fix` 完全兼容。
   - **分支 3b（直接干改动对外 CLI 参数）**：小改直接把 CLI 参数 `--out` 更名为 `--output` → 虽走直接干免填三问，但在 D4 ② 交付前须同步更新 `README.md` / CLI 现状文档唯一 owner，否则被 D4 ② 竣工回写核对拦下。

## 六、验收标准（可判对错）

1. **文档静态门禁与字数增量控制（`AR-5`）**：`bash scripts/check-docs.sh` 退出码 `0`（核心层预算、单行可见长度 ≤ 220、相对链接与精确 `#锚点`、双语 README 节标记及核心参考同步全绿）；`always_read_chars` 相对 v2 基线 `16,777` 净增 `≤ +800` 字（即 `≤ 17,577` 字）。
2. **替换式变更正式校验绿（`AR-5`）**：实施期提交 `docs/changes/2026-11-26-anti-entropy-spec-governance/manifest.json`，开发/审核期 `--draft` 退出码 `0`，合并确认前 `manifest-only` 钉扎后运行 `python3 scripts/check-change.py --manifest docs/changes/2026-11-26-anti-entropy-spec-governance/manifest.json --base <base> --head HEAD` 退出码 `0`（全部规则文件与 `SKILL.md` 进 `rules[]`、仅 `references/README.md` 进 `non_rule_changes[]`、双语 README 与 `evals/` 及 `scripts/test-run-eval.py` 进 `view_files[]`，未覆盖改动文件 = `0`，未处置 = `0`）。
3. **Eval 静态校验与确定性单测全绿（`AR-6`）**：`python3 scripts/run-eval.py --validate` 退出码 `0`（确认 14 条场景 schema、锚点与物化全绿）；`python3 scripts/test-run-eval.py` 退出码 `0`（含动态场景数与动态规则指纹校验、场景 `13`/`14` 正反例防误红判别及 `14` 夹具测试可运行性单测）。
4. **全量 14 场景行为回归与基线零退化（`AR-1`–`AR-4`、`AR-6`）**：实跑全部 14 条场景并以 `--baseline evals/baselines/2026-11-26-v2-baseline.json` 评分，退出码 `0`（原 12 条 `regressions == []` 零退化，新增 `13`、`14` 均为 `pass`），留存脱敏报告 `evals/baselines/2026-11-26-iter2-anti-entropy.json` 与 `.md`（如实标注自测基线）。
5. **保护边界零越界（`AR-5`）**：`python3 scripts/test-check-change.py` 全绿（61/61）；`git diff <base>..HEAD -- references/00-constitution.md scripts/check-docs.sh scripts/check-change.py scripts/test-check-change.py scripts/run-eval.py docs/specs/2026-11-26-behavioral-eval-harness.md evals/baselines/2026-11-26-v2-baseline.json evals/baselines/2026-11-26-v2-baseline.md` 输出为空。

## 七、文档治理对账（D2 证据）

- **决定数**：6 条（`AR-1`–`AR-6`）
- **owner 文件:节**：全部唯一归属本文件 `## 一、决定节（唯一正文）`
- **摘要处**：无（不含独立摘要 / 总纲节）
- **视图数**：2（§四.1 新增场景映射表、§六 验收标准），覆盖图与正文落点 100% 双向闭合，零孤儿 ID
- **规范性复述处清单（owner 外全部含「必须 / 不得 / 一律 / 默认 / 以…为准」句子，均已显式回指）**：
  1. `§二.1` 不动文件清单句（`均不得改动`）→ `AR-5`
  2. `§三.1` 简版决定表句（`默认保留简洁 ID`）→ `AR-1`
  3. `§三.1` Lane A 组件 1 前置句（`不得超出底座决定覆盖`）→ `AR-1`
  4. `§三.1` Lane A 底座报告兼容句（`不得因缺覆盖列…判阻断`）→ `AR-1`
  5. `§三.2` 触发当轮立账句（`必须在触发该变更的同一轮修订提交内`）→ `AR-2`
  6. `§三.3` 交付出口与关单列（`不得以「spec 已写」或笼统「不适用」跳过`）→ `AR-4`

## 八、审核与修订记录

- **R1 重审（2026-11-26，重审 2 路分身全量，`c352037..77d97bd`）**：
  - Lane A（规格符合性，1/2）：阻断 `0` / 高 `5` / 中 `2` / 低 `0`（关闭 `6` 项，需裁决 `0` 项，前置检查 4 项通过）。
  - Lane B（对抗找 bug，2/2）：阻断 `1` / 高 `4` / 中 `3` / 低 `0`（范围外改动 `0` 处）。
- **按用户 D2「全改」授权修订闭环（去重后 9 项全改）**：
  1. 补齐 `scripts/test-run-eval.py` 规则树指纹硬编码（`16777`/`54006`/`19` 与 delta 字面值）动态化改造要求（闭 Lane B B-1、Lane A F1）；
  2. 收口 `25-spec-governance.md` §三 触发组件 2 的「派生视图」定义，显式排除底座自身的常规验收标准节与改动文件表（闭 Lane B B-2、Lane A F3）；
  3. 增列同步 `26-review-contract.md` §五.2，明确底座 4 列简版决定表完备口径、单 owner/唯一 ID 底线，以及原 §四.2 四项前置检查到组件 1 / 组件 2 的精确映射（闭 Lane B B-3、Lane A F3）；
  4. 补列 `20-decisions.md` D5，明确多 PR 分步合回 `issue/<N>` 的中间子 PR 与整单交付出口分工，厘清直接干纯内部小改零额外文书税（闭 Lane B B-4、Lane A F4）；
  5. 在 `AR-4` 与 §三.3 规则正文补明未清理减法项转遗留**须经用户确认**（L0-2 / L0-6），禁止 agent 单方跳过（闭 Lane B B-5、Lane A F4）；
  6. 明确 `SKILL.md` 在 change manifest 中归 `rules[]`，仅 `references/README.md` 归 `non_rule_changes[]`（闭 Lane A F2、Lane B B-6）；
  7. 切清 `10-stages.md` 与 `25-spec-governance.md` 唯一正文与单向指针边界，消除公共底座双正文风险（闭 Lane A F5）；
  8. 明确组件 3 与纯新增 ADR 分流中的「既有」指 PR `base` 中已存在对象，排除本 PR 未合并草案短期决定升格（闭 Lane B B-7）；
  9. 补强 `13`/`14` 禁用输出正则防误红口径（后置不适用、条件升格与「补齐后再关单」）、要求 `14` 夹具双命令测试可运行并补对应单测；同步 §一/§三.1/§四/§七 覆盖图双向闭合，以及 §五.2 分支 2b 的 D2 失效 + R2 全量重核联动（闭 Lane B B-8、Lane A F6/F7）。
- **R1 #158 范围检查**：本轮修订新增用户决策或流程机制 `0` 条，全部为跨条款一致性对齐、脚本事实同步与假红封堵。
- **R2 轻审（仅复核，2026-11-26，1/1 分身，`77d97bd..242f284`）**：R1 9/9 全部闭合；新增阻断 `0` / 高 `0` / 中 `0` / 低 `0`；范围外改动 `0` 处；§七规范性复述 6/6 与正文精确一致、§一覆盖图 6/6 双向闭合、`bash scripts/check-docs.sh` 12/12 绿。用户已作 D3 合并确认（合入本地 `rebuild/v2`，不 push）。
