# 项目接入总则（50-adapters）

> 本页是项目接入、显式升级、指针与选修模板、5 选修采纳动作与资产边界的**唯一自足正文**。普通任务不顺手接入、不补制度、不自动开选修；本 skill 不维护采用名单。

## 一、只读检查与拟稿边界

用户要求「先检查、给出拟写指针，本轮不写」时，仅用只读工具核入口、链接与现有制度，交付两项即结束（不列多余备选，不追问「现在写入吗」）：
1. **检查结果**：区分已核实事实与未核事项（实核元数据、软链与末字节 `tail -c1`）。
2. **拟写指针**：指向本次实际读过的中央入口（默认根 `SKILL.md`）；远端分支与路径须有可核来源，未核实与未采用选修均省略，不为填模板枚举客户端技能目录。

## 二、只指向式契约、目标文件判定与显式升级

- **只指向式**：项目入口仅放指针块指中央真身，**不复制流程正文、不做同步机制**。
- **写入前置**：`AGENTS.md`/`CLAUDE.md` 若软链指向仓内另一文件则写目标，指向**仓外**共享文件（如 `~/.agents/AGENTS.md`）则**停手报告不写**；目标末行无换行（`tail -c1`）先补换行与空行。
- **目标文件判定**（指针本体只写 `AGENTS.md`，双工具共用单源）：
  - 无双文件 → 新建 `AGENTS.md`；仅 `CLAUDE.md` → 新建 `AGENTS.md` + `CLAUDE.md` 补独立一行 `@AGENTS.md`；
  - 仅 `AGENTS.md` → 追加指针节；双文件皆有 → 追加指针节 + 核 `CLAUDE.md` 含顶格 `^@AGENTS.md$`（不在反引号或代码块内）。
- **幂等与旧副本检测**：已有指针节须**同时**命中「spec-flow」与「唯一真相源 / 不复述 / 不放副本」，过期才就地更新。旧副本按含流程特征句（`name: spec-flow`、流程表、审核档位表等）或大段复述判定，**不用行数相似度阈值**；命中一律报告交用户定夺，不自动删改。
- **显式升级（「更新本项目的 spec-flow 接入」）**：仅用户明确要求时幂等执行，只补获准缺项，**不自动启用未采用选修，也不恢复代码地图**；`adr` 核四项动作、`doc-lifecycle` 核读序与施工 spec；与项目明确条款冲突则报告并停受影响部分，不宣布自动覆盖。
- **零补写与 ADR 断链**：普通任务缺入口或查需未授权写入时只报并回落源码，对指令 / 配置 / Git 元数据**零补写**；ADR 断链只读找回遵守，不改未采用，持久修交显式升级。

### 核心指针块模板（写入 `AGENTS.md`，按实际路径替换）

```markdown
## 流程规矩：来自 spec-flow

本仓复杂任务按 spec-flow 执行；规则唯一真相源在中央真身，**本文件不复述正文、不放副本、不做同步机制**。
- 读取入口：<核实的中央路径或远端 SKILL.md 链接>；认领既有 issue 同样从交付段进；改中央规矩去改真身。
- 项目入口与已采用选修不因中央改动自动改写；需补齐时显式要求更新接入。
```

## 三、5 个选修模块（默认全部关闭）

支持**本次按需读**与**项目级持久采用**（写 `AGENTS.md` 短入口与非可执行资产）；未知修饰词当场问。持久入口最低 6 项：① 模块名；② 中央正文链；③ 本仓落点；④ 后续动作；⑤ 本仓差异 / 验收；⑥ 「不复制、不建第二真相源」。

| 修饰词 | `AGENTS.md` 标题 | 默认资产 | 唯一正文 | 落点 / 动作 / 差异要点 |
|---|---|---|---|---|
| `adr` | `## 已启用：决策记录（ADR）` | `docs/decisions/README.md` | [adr.md](../30-playbooks/adr.md) | 复用自带制度，无则建短页（启用+载体表+默认 `ADR-YYYYMMDD-<slug>`+链接）；开工查、长期决定新增/取代不改旧正文、spec 只链不抄、收尾核一致 |
| `doc-lifecycle` | `## 已采用：文档生命周期备忘录` | 无 | [15-records.md](../15-records.md) §四 | 向用户确认现状文档路径（不代挑）；已用 ADR 补其载体表；先核现状与现行 ADR、实施前必读施工 spec、历史与实测冲突以后者为准 |
| `issue-status` | `## 已采用：issue 状态标签` | 8 状态 / 卡点标 | [labels.md](../30-playbooks/labels.md) §一 | 记测试环境；「待上线」「待验证」「关单」须确认；完成判据读 `10-stages.md` |
| `issue-type` | `## 已采用：issue 类型标签` | 8 类型标 | [labels.md](../30-playbooks/labels.md) §二 | 新单挂 1 主类型（`security` 可叠加 `bug`/`feat`）；验 `gh label list` 含 8 类，历史只补 open |
| `release` | `## 已采用：发布纪律` | 现有发布记录；不建分支/tag/脚本 | [release.md](../30-playbooks/release.md) | 先核分支与 `issue-status` 前提（缺项只报不顺便开）；用户定形态（单主线/三层/staging）、分支映射与发布记录落点 |

### 统一选修短入口模板（写入 `AGENTS.md`，按上表填）

```markdown
## <上表 AGENTS.md 标题>
本仓已采用 <模块名>（<日期> 拍板），唯一正文见中央 `<唯一正文路径>`（不复述、不建第二真相源）。
- 落点：<规则页/现状文档/分支映射/发布记录/测试环境>；动作与差异：<按上表填>；验收：<命令或无>。
```

### `issue-status` / `issue-type` 标签命令与防冲突保护

- **授权边界**：「应用 `issue-status`」仅授权新建缺失标签，**改 / 删已有标签或给旧单挂标须另问**；先 `gh label list --limit 200`，同名已存在不覆盖颜色描述只报差异。
- **老项目 `待验收` 防重名**：若存在旧名 `待验收`，**建标时必须跳过新建 `待验证`**，报用户点头后执行 `gh label edit "待验收" --name "待验证" --description "阶段：已上线，剩现在能由我方主动去正式环境验的项，或方案期批准的长尾项；正文首行写下次看"` 再按 `labels.md` 重分原挂单。

```bash
# issue-status（8 标；同名跳过，有「待验收」跳过「待验证」）
gh label create "未开始" --color EDEDED --description "阶段：开了单还没动手（含挂账、待复现、待评估）"
gh label create "进行中" --color 1D76DB --description "阶段：已认领，改动还没合进 issue 分支"
gh label create "待测试" --color 5319E7 --description "阶段：开发完成，预期交付已合入 issue 分支，等分支验收"
gh label create "测试完成" --color 006B75 --description "阶段：issue 分支验收通过，等整条合入 staging"
gh label create "待上线" --color 0E8A16 --description "阶段：整条已合入 staging（不可逆），批次失败切 fix 修"
gh label create "待验证" --color C2E0C6 --description "阶段：已上线，剩现在能由我方主动去正式环境验的项，或方案期批准的长尾项；正文首行写下次看"
gh label create "等拍板" --color D93F0B --description "卡点：等 owner 做决定，拍完摘掉"
gh label create "受阻"   --color B60205 --description "卡点：等外部条件；正文首行写下次看"

# issue-type（8 标；先按 labels.md §二 获准迁移旧标再建缺项，只回填 open 单）
gh label create feat --color 1D76DB --description "类型：新功能或能力变更"
gh label create bug --color D73A4A --description "类型：行为不符合预期（含线上故障、回归）"
gh label create docs --color 0075CA --description "类型：文档、spec、README"
gh label create refactor --color 6F42C1 --description "类型：不改外部行为的代码重构"
gh label create perf --color FBCA04 --description "类型：性能优化，需有可对比指标"
gh label create test --color 0E8A16 --description "类型：测试、用例、测试基建"
gh label create chore --color BFD4F2 --description "类型：依赖、构建、CI、配置、杂务"
gh label create security --color B60205 --description "类型：安全整改或漏洞，可叠加在 bug/feat 上"
```

- **代码地图**：默认停用，普通接入 / 升级不探测不配置；当次试用不写长期声明，配置请求不含工具安装许可；持久恢复须核分母、扫描范围与写授权，不因已安装推定恢复。

## 四、默认资产边界与可执行资产升级闸

- **默认资产**：仅限文档入口与上表非可执行资产；脚本 / CI / Hook / Workflow / 生成器 / 机器人绝不随采纳自动创建。
- **可执行资产升级闸**：确需新增时停在「材料备好」，列齐 5 项——`路径与类型`、`解决的问题`、`触发方式`、`维护成本`、`Markdown-only 替代方案`——经用户明确同意才建（授权仅覆当次路径）。拒绝则回落 Markdown-only 写明人工部分并报告「未加脚本，因此没有机械拦截」。
- **收尾报告**：分项报规则入口、工具、配置、跳过项、旧物与验证末态，不以「已启用」冒充全就绪；演练只在假仓进行。
