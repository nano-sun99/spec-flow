<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo/spec-flow-lockup-dark.svg">
    <img alt="spec-flow" src="assets/logo/spec-flow-lockup.svg" width="480">
  </picture>
</p>

**给 AI 编码 agent 用的两段流程：必要闸口严格，闸内方法灵活。** 先谈清目标、范围和验收，再按明确委托实现与交付；哪些审核、修订、合并和生产动作获准，由用户决定。

它没有运行时或服务，是 agent 读取的 Markdown。开 spec 的路径保留获批规格、执行 issue 和可追溯来源；直接干不补造 spec 或执行单，但不免实施交付与合并确认。代码地图仍默认停用，影响判断靠源码、实际 diff 和相关测试。

`SKILL.md` **只做入口和导航**。正文预算仍为 **4,700 字符**、frontmatter **500**、整份 **5,200**，含换行；[`scripts/check-docs.sh`](scripts/check-docs.sh) 不把规则挤进元信息。预算不是跨客户端 token 或压缩保证，动作细则不可见或版本变化时重新读取。

每条规则有可回溯来源：[`references/rationale.md`](references/rationale.md) 的 **37 条记录**保留案例、决定、代价和验证边界，历史不是另一套运行规则。

[English](README.md) · **中文**

<!-- s:shape -->
## 用起来是什么样

同一句“给个人资料页加头像上传”，没有共同理解时，agent 可能直接交来你没要的数据库表和自定上传上限。

有 spec-flow，新需求先选直接干或开 spec。开 spec 后，grill-me 帮助查清目标和真实岔路，spec-flow 汇成同一份方案。No 可以重新构思，不限于局部打补丁；首次 Yes 前不写 spec。

**Yes 后先写公共骨架并开同一 Draft PR，再判断页面。** 有页面等你提供设计后分析交互与接口，无页面结合规则/接口及可判对错的材料分析。两支汇合，确认待决定缺口已补齐，再统一选拆或不拆、细化终稿；充分的段落、表格或图都可以，不靠固定四列或三个样例卡住。

可实施且你同意送审才进入本份审核；按选择修订，单独确认合并。规格合并、执行单交接后停等明确实施委托；实施交付重新选档，不继承方案期审核。例外和改旧规格只在触发时问。

<!-- s:problem -->
## 它解决什么

失误常在接缝：需求理解没有确认、下一份交付漏了上游、两人认领同号任务、审核被当成合并同意，或代码合并后文档/部署还没交就宣称完成。

解决办法不是让每一步更啰嗦，而是让**决定、授权、交付和证据各有归属**：查得清的事实先查，只有用户能定的事才问。

<!-- s:scars -->
## 这些规矩是从哪来的

案例与原始边界见 rationale，不拿旧案例扩大新任务范围：

- **R1**：IDC 判据扩成 CIDR ∪ ASN，却漏改实现、验收与父文档；改一句要核所有现行落点。
- **R7**：两个 agent 都把 issue open 当无人认领；真正的认领证据是 Git worktree 建成。
- **R15**：拆分只划文件地盘，却让同一“是否启用”判定有两个 owner；依赖与共享决定同样需要归属。
- **R12**：一份规格跨 17 个提交反复改正文；动已合并规格要先让用户决定新开还是改旧。
- **R37**：整体按职责归位，公共骨架/Draft 前置，去掉把格式、样例数量和汇报口吻当审批的做法。

<!-- s:what -->
## 它怎么解决

**两段主线不变，不增加第三套管理流程。**

- **方案期**：澄清与方案确认 → 公共骨架/Draft → 页面或规则分析 → 公共缺口确认 → 统一拆分 → 终稿 → 审核/独立合并 → 执行任务交接。
- **实施期**：明确委托 → 隔离认领、实现/测试/配套文档 → 本份审核/独立合并 → 实际来源及证据回填 → 必要验收与适用发布 → 完成收尾。

职责唯一正文：流程/状态在 [one-path](references/one-path.md)，选项与权限在 [gate-details](references/gate-details.md)，交付信息在 [phase-handoff](references/phase-handoff.md)，完成在 [done-criteria](references/done-criteria.md)。入口和指南不重复立规。

<!-- s:self-review -->
## 唯一值得直接拿走的一条：分身不是第二个人

agent 派出去的仍是它自己的执行分身。换模型、名字或 prompt 不自动变独立意见；自测、草拟也不能冒充审核。

审不审、审哪档由用户当份选择；真正需要“我以外的一方”裁决时，材料备好后停等指定方，不自己派分身顶替。规则不把纯 Markdown 说成权限隔离。

<!-- s:smooth -->
## 为什么它不累赘

必要用户决定用选项工具，说明推荐、主要代价并允许补充；客户端没工具就列等价选项，不把缺工具或沉默当同意。已有效确认不因换方法重复问，用户自发明确指令也不被卡片形式抹掉。

审核仍有不审/轻审/重审/重审+变异，修订仍有全改/只改阻断+高/不改，合并仍独立确认；具体默认、轮次、成本与停止只在闸口正文。表达/同步瑕疵可修，越权、漏交付和真正安全缺口不能借“灵活”放过。

<!-- s:longrun -->
## 它凭什么扛得住长活

认领锁由 Git 保存；当前阶段在原交接区，获批范围在规格，全部实现来源与通过证据在原任务。换会话不需要靠私有记忆猜谁在做或最后一份 PR 是否代表全部交付。

分拣先读预期交付，再核方案 PR 和全部实现/补充来源。规格归档核真实正文，已有内容只核验，共享文件不整体取移动 dev，未就绪任务不搭车；缺记录补原记录，缺产物补交付，不另建账。

<!-- s:limits -->
## 它不做什么

- 不调度 agent、不自动续跑、不提供平台授权隔离；Git 锁和本仓静态检查只覆盖各自有限范围。
- 不保证永不出错；完成是本次约定已实现、必要测试/验收通过、无已知阻断、证据齐全。
- 不把实现合并、标签或 tag 当作部署成功；成功快照也不表示所有服务实时同版。
- 不自动安装工具、升级采用仓、建长期分支、造 CI/Hook 或发布平台；issue/PR 路径假定 GitHub，平台能力不足如实说明。

<!-- s:install -->
## 装

```bash
git clone https://github.com/Strelizialeomon/spec-flow.git ~/.claude/skills/spec-flow
```

也可 clone 到自己的代码目录，再软链进客户端技能目录。Claude Code 的个人技能路径如上；其他客户端使用各自发现路径。安装技能不等于项目接入、配置就绪或客户端已经验证。

PLAN / ANALYZE 的专业梳理需能加载 grill-me 及其实际调用的 grilling。需要且缺失时，核来源和具体安装位置再问 Yes/No；拒绝或失败只暂停该梳理路径，不挡直接干、既有实施或交付。不自动换模板或冒称技能已运行；superpowers 不是依赖。

<!-- s:usage -->
## 怎么用

描述需求或点名 spec-flow；实施已有单直接说“做 #12”。既有任务从当前有效阶段接，不重新访谈；同窗口紧接唯一交接时的裸开工命令及其严格边界见 gate-details，不凭全局唯一任务猜授权。

方案指南可按需选用：样例、图、段落和表格都服务于可判定规则/接口/验收。项目明确格式仍遵守，不因指南可替换省必要合同。范围内改实现方法不逐内部阶段求许可，真正触发停止点才停受影响部分。

接入说“把 spec-flow 应用到本项目”，显式升级说“更新本项目的 spec-flow 接入”：只写获准指针和项目落点，重复执行幂等，不复制流程、不顺手开启选修或迁移旧项目。

选修仍是 `adr`、`doc-lifecycle`、`issue-status`、`issue-type`、`release`，默认关闭。`release` 同时管 **Git 分支流程与发布**：采用时明确单主线/三层及实际分支映射，不新增独立 Git 开关。三层普通文档也按任务进入 staging；无部署义务且分支交付/验收完成可结束，等下次正常快照，不另造文档热修/tag；仍需部署的代码不能提前完成。

代码地图默认停用，仅明确试用/恢复才读 [code-map](references/code-map.md)。已采用 ADR、文档读序等按其真实时点执行；当前获批施工规格仍必读，不为结构对称重做这些制度。

<!-- s:evidence -->
## 本仓自己就是样板

规格、issue、PR 与 rationale 保留设计及交付依据；旧规格和裁决不重写成新运行规则。每次交付的测试记录说明输入、预期、实际及边界：静态绿不证明客户端遵守，假仓/有限客户端不证明真实生产或全模型认证。

本次整体重组依据已合并方案 PR #164 和执行单 #165；实施审核与合并仍等本次用户选择，规格审核不能充作实施验收。

<!-- s:docs -->
## 文件

| 文件 | 职责 |
|---|---|
| `SKILL.md` | 入口与导航，不承接完整流程/卡片/模板 |
| `AGENTS.md`、`CLAUDE.md` | 本仓维护规矩，后者导入前者 |
| `references/one-path.md` | 流程/定稿图/状态与衔接唯一正文 |
| `references/gate-details.md` | 选项、批准范围、放行/停止、审核与合并唯一正文 |
| `references/phase-handoff.md` | 交付信息、全部来源与更新责任唯一正文 |
| `references/done-criteria.md` | 有限完成、必要证据与已批准例外唯一判据 |
| `references/spec-maturity.md` | 可替换的骨架/对照/终稿工作指南 |
| `references/split-large-spec.md` | 可替换的交付物/依赖/拆分指南 |
| `references/spec-revision-sync.md` | 可替换的现行落点同步方法 |
| `references/worktree-lock.md` | Git 工作区、锁、接管和安全边界 |
| `references/apply-to-project.md` | 采用意图、指针、落点与资产/安装边界 |
| `references/release-discipline.md` | 选修 release：Git 映射、完整候选与必要发布 |
| `references/adr-decision-records.md` | 选修 ADR，保留原制度职责 |
| `references/documentation-lifecycle.md` | 选修文档生命周期和读序 |
| `references/issue-status-labels.md` | 选修阶段/卡点标签与分拣 |
| `references/issue-type-labels.md` | 选修类型标签及获准迁移 |
| `references/code-map.md` | 默认停用的地图试用/恢复边界 |
| `references/adoption-model.md` | 历史采纳解释，不增加义务 |
| `references/rationale.md` | R1–R37：依据、取舍及验证边界 |
| `docs/maintainer-notes.md` | 本仓接线与历史说明 |
| `scripts/check-docs.sh` | 原预算/链接/双语/采用契约及必要 owner/交付信息存在性；不强制指南字面写法 |

README 是介绍，入口导航到各唯一正文；冲突核相应 owner，不拿 README 另立规则。

<!-- s:contributing -->
## 参与

开 issue 或 PR。新增/修改规则，把真实依据记 rationale 并编新 R 号；主入口只留导航与必要理由指针。两份 README 同批同步并运行现有文档检查。

<!-- s:license -->
## 许可

MIT，见 [LICENSE](LICENSE)。
