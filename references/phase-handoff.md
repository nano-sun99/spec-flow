# 方案交接与实施委托（交接、授权、接手时读）

> 本文件展开 `SKILL.md`〈方案交接〉与第 6 / 9 步。状态语义、交接区、授权记录和接手协议以本文件为准；交接与授权不是新的审核档位，方案期与实施期的审核档位互不继承。依据：rationale R29、R30。

## 一、状态模型

| 状态 | 谁负责 | 可做什么 | 不可做什么 | 离开条件 |
|---|---|---|---|---|
| `DESIGNING` | 方案 agent | 调研、确认需求、用户点头后写 spec、摆方案期卡 | 写代码、认领实施 worktree | 用户点头且草案成形 → `SPEC_REVIEW` |
| `SPEC_REVIEW` | 方案 agent + 用户 | 选审核档位、审核、贴结论、按用户选择修订、摆合并卡；spec PR 已合并但创建执行 issue 失败时重试创建 | 把审核选择当实施授权 | 合并卡取得同意且 spec PR 合并 → `SPEC_READY`；用户关闭 → `CANCELLED` |
| `SPEC_READY` | 方案 agent 已交付 | 创建执行 issue、写交接区、报告结果、按用户指令关闭 issue | 创建实施 worktree、改代码、派实施 agent、跑实施任务；未经用户指令改 issue 生命周期状态或实施阶段标签 | 用户明确委托 → `IMPLEMENTATION_AUTHORIZED`；返修 / 重审 → `SPEC_REVIEW`；关闭 → `CANCELLED` |
| `IMPLEMENTATION_AUTHORIZED` | 实施 agent 接收 | 读交接材料、核当前基线、写授权记录、准备认领 | 在授权对象不明时扩大范围；已有授权记录时再追加一份 | 认领成功 → `IMPLEMENTING`；认领失败 / 撤销 → `SPEC_READY` |
| `IMPLEMENTING` | 实施 agent | 认领锁、读写代码、测试、开实施 PR；把流程状态更新为 `IMPLEMENTING` | 越过授权范围或擅自改长期决定 | 实施 PR 形成 → `DELIVERY_REVIEW`；暂停 / 范围变化 → `PAUSED` |
| `DELIVERY_REVIEW` | 实施 agent + 用户 | 摆当次实施审核卡、处理发现、取得用户单独的合并确认；把流程状态更新为 `DELIVERY_REVIEW` | 沿用方案期审核档或自动合并 | 合并并回填 → `COMPLETED`；暂停 → `PAUSED` |
| `PAUSED` | 用户 + 当前 agent | 报告暂停、保留或释放锁、记录恢复条件 | 未经用户恢复就继续实施、悄悄关单 | 用户恢复 → 暂停前状态；取消 → `CANCELLED` |
| `CANCELLED` | 用户 + 当前 agent | 记录原因、按既有规则放锁 | 继续实施或把取消伪装成完成 | 用户重新打开 → `SPEC_REVIEW` / `SPEC_READY` |
| `COMPLETED` | 实施 agent | 回填验收、issue、ADR、状态并放锁 | 把未完成观察或已知阻断伪装成完成 | 收尾完成 |

- `SPEC_READY` 是方案期的正常终点；方案 agent 在交接报告后停止当前回合，但用户后续仍可委托。
- 没有用户委托时，`SPEC_READY` 不得跳到任何实施状态。
- 「本轮消息结束」不是状态转移，只是 `SPEC_READY` 下的责任终点。
- `CANCELLED` 可以被用户重新打开；打开后按用户选择回到 `SPEC_REVIEW` 或 `SPEC_READY`，不自动恢复实施授权。

## 二、状态转移

```text
DESIGNING -> SPEC_REVIEW
SPEC_REVIEW -> SPEC_READY [合并卡同意且 spec PR 合并] / CANCELLED [用户关闭] / SPEC_REVIEW [继续修订或重试创建]
SPEC_READY -> IMPLEMENTATION_AUTHORIZED [用户明确委托] / SPEC_REVIEW [返修/重审] / CANCELLED [用户关闭]
IMPLEMENTATION_AUTHORIZED -> IMPLEMENTING [认领成功] / SPEC_READY [认领失败/撤销]
IMPLEMENTING -> DELIVERY_REVIEW [实施 PR 形成] / PAUSED [暂停/范围变化]
DELIVERY_REVIEW -> COMPLETED [合并并回填] / PAUSED [用户暂停]
PAUSED -> IMPLEMENTING / SPEC_READY [用户恢复] / CANCELLED [用户取消]
CANCELLED -> SPEC_REVIEW / SPEC_READY [用户重新打开]
```

- 结构决定（拆分卡）未答或结构实质变化时，不自动创建执行 issue / 交接区，先让用户选结构。
- `SPEC_REVIEW` 离开前必须单独摆合并卡；审核完成、零发现或修订完成都不代替合并同意（依据：rationale R30）。
- spec PR 已合并但创建执行 issue 失败：报告失败，在 `SPEC_REVIEW` 下重试创建；失败报告不是 `SPEC_READY` 报告，同窗口入口不成立。
- 认领失败或用户撤销、回到 `SPEC_READY` 时，把 `实施授权` 改为「待用户明确委托（上次认领失败）」，旧授权记录保留并标注「未生效」；下一次委托追加新记录，不覆盖历史。
- 已合并 spec 需要返修，先走「改旧 spec 卡」；旧执行 issue 按用户指令关闭或标记失效，返修合并后重新交接。

## 三、交接区

方案 PR 合并后，对每张执行 issue 写 `## spec-flow 交接`。必填字段：

| 字段 | 必填 | 谁写 / 更新 |
|---|---|---|
| 流程状态 | 是 | 方案 agent 写 `SPEC_READY`；实施 agent 依次更新为 `IMPLEMENTATION_AUTHORIZED` → `IMPLEMENTING` → `DELIVERY_REVIEW` → `COMPLETED` |
| 实施授权 | 是 | 方案 agent 写「待用户明确委托」；实施 agent 写授权对象；认领失败回退时写「待用户明确委托（上次认领失败）」 |
| Spec | 是 | 方案 agent 写合并后的永久链接 |
| Spec 合并 commit | 是 | 方案 agent 写；实施 agent 核对是否为当前应实施的最新合并版本 |
| 方案 PR | 是 | 方案 agent 写一个或多个永久链接 |
| 上游 / ADR | 是 | 按项目规则；默认见 spec 上游节、一跳可达；项目规定 issue 只链 spec 时写「见 spec 上游节」，不直链 |
| 实施范围 | 是 | 做什么 / 不做什么 / 验收入口 / 已知限制；范围建议用 spec 章节锚或逐字摘录 |
| 接手条件 | 是 | 必读材料、开工命令、当前状态；实施 agent 更新当前状态 |
| 当前状态 | 是 | 方案 agent 写「未创建实施 worktree」；实施 agent 在认领、PR 形成、合并回填时同步更新 |
| 授权记录 | 认领前必填 | 实施 agent 追加；至少含对象、方式、原话、时间、本次范围；同窗口方式抄报告固定行；只追加，不改历史 |

模板：

```markdown
## spec-flow 交接

- 流程状态：`SPEC_READY`
- 实施授权：`待用户明确委托`
- Spec：<永久链接>
- Spec 合并 commit：<sha>
- 方案 PR：<一个或多个永久链接>
- 上游 / ADR：<按项目规则；无则写“无”；只链 spec 时写“见 spec 上游节”>

### 实施范围
- 做什么：<章节锚或逐字摘录>
- 不做什么：<明确排除项>
- 验收入口：<spec 验收节 / 证据要求>
- 已知限制：<未决、风险、未纳入项>

### 接手条件
- 实施前必读：项目 `AGENTS.md` / `CLAUDE.md`、获批 spec、现行 ADR（如已采用）、本 issue。
- 开工命令：同一窗口紧接本交接报告（本报告是当前上下文最后一条 agent 消息、用户的开始意图是紧接着的下一条用户消息、当前窗口恰好只有本交接）时，用户说“开始实施”“开始干”或“开工”可以续接当前 `#N`；中间有任何问答 / 工具结果 / 上下文压缩，或报告列出多张执行 issue 时，必须说“开始实施 #N”。全局只有一个候选不能替代这条上下文条件。
- 当前状态：未创建实施 worktree，未修改实施代码。
- 授权记录：收到明确委托后，先写授权对象、方式、原话、时间、范围；同窗口方式还要抄本报告 Spec / 执行 issue / 下一步三行，`issue-direct` 写“不适用”。这一步是机械留痕，不再向用户追加确认。

### 授权记录
<认领前由实施 agent 按 §五追加；方案期留空>
```

- 「交接」指一张执行 issue 的交接区，不是一整份报告；拆分组每张执行 issue 各有交接区。
- 父 / 总览 issue 只跟踪，不进入状态机，不写实施交接区，也不被认领为执行任务。
- 既有 issue 没有交接区时，不要求补造 `SPEC_READY`；按 §四「既有 issue 入口」处理。

## 四、授权识别

- 对象必须是 issue；PR 号（即使与 issue 共用编号）不触发实施。
- **定向入口**：任何窗口收到“开始实施 #N”“按 #N 开工”“请做 #N”等绑定 issue 的表达，授权方式记 `issue-direct`。
- **同窗口交接入口**（三条件同时成立才生效）：
  1. 方案 agent 的 `SPEC_READY` 交接报告是当前上下文中本 agent 的最后一条消息；
  2. 用户的开始意图是紧接着的下一条用户消息；
  3. 当前窗口恰好只有一张尚未授权的执行 issue 交接区。
  满足时授权方式记 `same-window-handoff`。
- **紧接的边界**：中间出现任何用户提问、agent 回答、工具结果、上下文压缩摘要或压缩标记，都不算紧接；交接报告不在当前上下文逐字可见时也不成立。出现这些情况一律要求 `#N` 或让用户选择。
- **开始意图是闭集**：“开始实施”“开始干”“开工”。“继续”“就按这个做”“开始吧”不在集合内，即使同窗口也不授权。礼貌前缀（如「请你开始实施」）不改变闭集判断；授权原话照录。
- **多执行 issue**：报告列出多张执行 issue 时，裸“开始实施”不授权，必须点名 `#N` 或让用户选择。
- 新窗口、其他 agent、上下文不完整或存在多张未授权执行单时，不得用全局候选推断对象。
- **既有 issue 入口**：没有交接区的既有 issue，用户明确说“做 #N”“开始实施 #N”即构成委托；不要求 `SPEC_READY`，授权记录写 issue 评论（项目允许改正文时也可写正文）。没有交接区的 issue 不适用同窗口入口。
- 实施授权只覆盖实施阶段，不包含任何 PR 的合并同意；每份 PR 仍须单独摆合并卡（依据：rationale R30）。
- **免方案期路径**：用户说“直接干 / 别走流程”，或改动属于改一行、纯查事实时，不产生 spec / 执行 issue / 交接区；当场指令即授权实施，不授权合并，作用域是被点名的任务，不需要 `#N`。若开 worktree，按 `references/worktree-lock.md` 的「没有 issue 号的活」执行，无锁可领；交付前仍照摆闸卡与合并卡，交付与回填规则不变。显式“直接干”优先于同窗口入口；若用户点名了交接报告里的 issue，一律走 `issue-direct` 并写授权记录，不按免方案期跳过记录。

## 五、授权记录

交接 issue 写在正文 `### 授权记录` 小节；既有 issue 写评论（项目允许时也可写正文）。最小形态：

```markdown
### 授权记录

- 流程状态：`IMPLEMENTATION_AUTHORIZED`
- 实施授权：用户明确委托实施 `#N`
- 授权方式：`issue-direct` 或 `same-window-handoff`
- 授权原话：<用户原话>
- 授权时间：<记录时间>
- 本次范围：<spec 全量 / 用户明确缩小的范围>
- 交接报告摘录：<same-window-handoff 时抄 Spec / 执行 issue / 下一步三行；issue-direct 写“不适用”>
- Spec 合并 commit 核对：<交接区记录的 sha == 当前应实施的最新合并版本；没有交接区时写“不适用”>
- 基线核对：`git worktree list` / `git branch --list 'issue-N'` / `git status` 的结果摘要
```

- 只追加，不改历史；不扩写用户没有授权的范围；同一 issue 不追加第二份生效授权。
- `same-window-handoff` 是记录者对相邻性与唯一性的自述；审计先核用户原话与报告摘录，再核 issue 状态和 Spec 合并 commit。
- 交接区正文 `流程状态` 是唯一权威；项目标签、issue 评论、旧摘要都只是辅助。冲突时停下报告，不自行选一个继续。

## 六、接手协议

1. **解析对象**：定向入口按 `#N` 解析；同窗口入口按 §四三条件解析。PR 号不触发；交接 issue 必须处于 `SPEC_READY` 且 open；父 / 总览 issue 不是交接单位；没有交接区的既有 issue 按 §四处理，必须点名 `#N`。
2. **读项目规则**：项目 `AGENTS.md` / `CLAUDE.md`，确认体例、已采用制度和工作区边界。
3. **读交接材料**：交接区（或既有 issue 正文 / 评论）、获批 spec、相关 ADR、当前项目事实；合并后的 spec 是范围与验收的唯一权威。
4. **核事实**：issue 仍 open、交接区仍 `SPEC_READY`、spec 链接指向最新合并版本且与 Spec 合并 commit 一致、实施范围与 spec 一致、该 issue 尚无生效授权记录；实跑 `git worktree list`、`git branch --list 'issue-<N>'`、`git status` 并记录结果。已授权 / 已返修 / spec 已改 / issue 已关闭时停下，按 §七处理。
5. **写授权记录**：按 §五追加，并把流程状态改为 `IMPLEMENTATION_AUTHORIZED`。
6. **认领 worktree**：从远端基线认领 `issue-<N>`；锁失败按 `references/worktree-lock.md` 停下；接手前必须有用户明确授权并追加接管记录。
7. **进入 `IMPLEMENTING`**：此后才允许写实施代码和测试；把流程状态与当前状态同步更新。范围变化或 spec 事实错误，暂停受影响实施，按改旧 spec 卡 / 新 spec / ADR 规则处理。

## 七、返修、撤销、接管与范围变化

- **返修 / 重审**：回到方案侧；已合并 spec 先走改旧 spec 卡；旧交接 issue 按用户指令关闭或标记失效，返修合并后重新交接。
- **撤销**：用户授权后反悔，进入 `PAUSED` 或按用户指令回到 `SPEC_READY`；已认领 worktree 按锁规则释放，不把撤销伪装成完成。
- **认领失败**：按 §二回退到 `SPEC_READY`，标注旧授权「未生效」；不改写历史记录。
- **接管**：前一个 agent 已写授权记录但锁已失效时，新 agent 必须在用户明确授权后按锁规则接手，并追加接管记录：新授权原话、授权方式 `takeover`、时间、本次范围、旧记录链接；不得把旧授权当新授权。
- **已有授权**：写授权记录前先查该 issue 是否已有生效授权记录；已有则停下，按接管规则处理，不追加第二份生效记录。
- **范围变化**：用户缩小范围时，授权记录写本次范围，交接区实施范围仍是 spec 全量，以更窄者为准；扩大到 spec 之外，暂停受影响实施，按改旧 spec 卡 / 新 spec 处理。

## 八、状态与项目标签映射（仅采用 `issue-status` 时）

标签映射的唯一 owner 是 `references/issue-status-labels.md`〈与 `spec-flow 交接` 区的映射〉；本节只留指针，不复制表格。要点：`SPEC_READY` / `IMPLEMENTATION_AUTHORIZED` 对应「未开始」；`IMPLEMENTING` 与未合并的 `DELIVERY_REVIEW` 对应「进行中」；合并后按备忘录 §四换「待测试 / 待上线」；`COMPLETED` 按上线分拣与关单规则。未采用该备忘录的项目不假设标签存在，只核交接区正文状态。

「下次看」行可以放在 `spec-flow 交接` 区之前；正文流程状态仍是唯一权威，标签与它冲突时停下报告。

## 九、方案 agent 的最终交接报告

方案 agent 在 spec PR 合并、执行 issue 创建和交接区写入完成后，只输出一次固定报告：

```text
方案阶段已完成，实施尚未授权。

Spec：<永久链接>
执行 issue：#N、#M（项目默认状态）
本次方案覆盖：<一行范围>
实施授权：待用户明确委托

下一步：当前窗口恰好只有一张未授权执行单时，紧接本报告可以直接说“开始实施”“开始干”或“开工”；有多张执行单、或新窗口 / 其他 agent / 中间隔了问答 / 上下文压缩时，请说“开始实施 #N”。收到前我不会创建 worktree、修改代码或派实施 agent。
```

报告之后不得继续调用工具做实施准备：不建 worktree、不写代码、不跑实施测试、不改 issue 为进行中、不派实施 agent。用户追问 spec 与现状的差异时，可以只读查看代码 / diff 并回答，但不得把只读检查扩展成实施准备。报告之后中间出现任何问答、工具结果或上下文压缩，同窗口入口即失效，必须点名 `#N`。
