# spec：issue 类型标签备忘录（可选，按需启用）

- 日期：2026-10-29
- Issue：待开（spec 合并后开）
- 状态：草案（方案期，待审核）

## 背景：要解什么问题

2026-10-29 对 29 个有 issue 的自有仓做了实测：

- 869 个 issue，334 个（38%）没有任何标签。
- 181 个 open，其中 128 个没有任何类型标签（8 类或旧等价物）。
- 6 个最活跃仓 711 条标题里：测试 27、文档 17、重构 12、安全 12、依赖 5、性能 3；feat / bug 是主体，但多数裸奔。
- 自定义类型标签只在 2 个仓出现（go_wechat_robot、llm_auto_report），写法是 `type:feat` / `type:fix` 等；其余仓只有 GitHub 默认 10 个标签。
- spec-flow 自己 27 个 issue 全部无标签，类型靠标题前缀（实施：/调研：/试用：/待决：）；taoxi_system 112/213 无标签。
- 本轮抽查的仓里没有 `.github/labels.yml` 之类的可复现标签配置。

问题不是“类型想少了”，是两件事：

1. **词表不统一**：默认 `bug` / `enhancement` / `documentation`、自定义 `type:*`、标题前缀三套并存，跨仓筛不出来。
2. **打标不绑定动作**：开单时不挂，事后没人补，38% 裸奔。

所以要做的是一个最小、可迁移、开单即挂的类型词表；不是把 Kubernetes 那套搬过来。

## 调研

| 说法 | 出处 | 对本 spec 的含义 |
|---|---|---|
| 只强制 `feat` / `fix`；`build` / `chore` / `ci` / `docs` / `style` / `refactor` / `perf` / `test` / `revert` 是推荐扩展 | [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) | 取 `feat`/`fix`/`docs`/`refactor`/`perf`/`test`/`chore`；`fix` 在 issue 侧叫 `bug` |
| 新仓默认 10 个标签：`bug`/`documentation`/`enhancement`/…；不规定分类法 | [GitHub Docs 管理标签](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels) | 不另造前缀；把 `enhancement`→`feat`、`documentation`→`docs` 改名收编 |
| `kind/*` 分 9 类：`bug`/`feature`/`documentation`/`cleanup`/`api-change`/`design`/`failing-test`/`flake`/`support`；`security` 不在 `kind/*`，走 `sig/security` | [Kubernetes label_sync](https://github.com/kubernetes/test-infra/blob/master/label_sync/labels.md)、[Issue Triage](https://www.kubernetes.dev/docs/guide/issue-triage/) | 证明 8 类够用；`flake`/`api-change`/`cleanup` 不抄；`security` 作为可叠加限定词保留 |
| 变更类别：Added / Changed / Deprecated / Removed / Fixed / Security | [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) | `security` 单列，发布说明能捞出安全修复 |
| 组织级原生 Issue Types：Task / Bug / Feature，最多 25 个自定义；个人账号没有 | [GitHub Docs 管理 issue types](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/managing-issue-types-in-an-organization) | taoxi-project 有原生类型（0 单在用），nano-sun99 是个人号；`gh issue list` 不支持 `issueType`。统一用标签，不开两条轨 |
| GitLab 默认标签含 `bug`/`documentation`/`enhancement`/`support` 等 | [GitLab Docs labels](https://docs.gitlab.com/ee/user/project/labels.html) | 同样证明 `bug`/`docs` 是通用词，不需造新词 |

坑：

- 以上体系都是为多人协作 + 自动分拣设计的；本场景是一人 + 多 agent，标签首先是给 agent 和 `gh` 过滤用的，不是给人看的分类学。
- 标签越多，开单时选择成本越高；8 类是上限，不是起点。
- 历史单的语义分类会错；机械迁移（已有标签改名 / 合并）可以全量做，语义回填只做 open。

## owner 拍板（2026-10-29 对话，卡片记录）

- 8 类：`feat` / `bug` / `docs` / `refactor` / `perf` / `test` / `chore` / `security`；裸名小写，不加 `type:` 前缀。
- 迁移：`enhancement`→`feat`、`documentation`→`docs`、`type:feat/fix/docs/chore/refactor`→裸名（`type:fix`→`bug`）。
- 落地：**各项目全包**——spec-flow 只定清单与采用动作；每个项目的 agent 在本仓自己改名、补标签、回填 open、写指针。不做中央批量脚本。
- 回填：只回填 open 单里没有类型标签的（128 个）；closed 不语义回填；已有旧类型标签的机械迁移覆盖 open + closed。
- 本轮不做优先级、不做卡点；`design`/`research` 不单列（前者用 `scope:design`，后者归 `docs`/`feat`）。
- 机制卡：全要。落地分工：各项目全包。历史回填：随落地分工，默认 open-only（D9，可 veto）。

## 机制清单

| # | 机制 | 解决什么 / 没有它会怎样 |
|---|---|---|
| 1 | **8 类类型标签**（裸名、小写、一单一个；`security` 可叠加） | 跨仓用同一套词筛 issue / 没有它：默认标签、`type:*`、标题前缀三套并存 |
| 2 | **迁移映射**：`enhancement`→`feat`、`documentation`→`docs`、`type:*`→裸名 | 保留已有分类，不丢历史单的标签 / 没有它：新旧两套并存，越用越乱 |
| 3 | **采用开关 `issue-type`**：项目指令写指针，项目 agent 按同一份清单改名 / 补标签 / 写入口 | 各项目按需启用、不复制正文 / 没有它：每仓手搭一遍，名字颜色又各不同 |
| 4 | **回填口径**：机械迁移覆盖 open+closed；语义回填只做 open，closed 不动 | 修好 open 视图，不把成本花在沉没单上 / 没有它：要么全量补（贵），要么视图继续缺类型 |
| 5 | **开单强制挂类型**：新建 issue 必须带一个类型；类型不清先问，不猜 | 防止新单继续裸奔 / 没有它：历史修完，新单马上又缺 |

## 标签定义

| 标签 | 标什么 | 边界 / 对应 |
|---|---|---|
| `feat` | 新功能或能力变更 | 原 `enhancement`；对应 commit `feat` |
| `bug` | 行为不符合预期 | 含线上故障、回归；对应 commit `fix` |
| `docs` | 文档、spec、README | 原 `documentation`；用 `docs` 不用 `doc` |
| `refactor` | 不改外部行为的代码重构 | 对应 commit `refactor` |
| `perf` | 性能优化 | 要有可对比指标，不接受“感觉快了” |
| `test` | 测试、用例、测试基建 | 对应 commit `test` |
| `chore` | 依赖、构建、CI、配置、杂务 | 对应 commit `chore`；`style`/`build`/`ci`/`deps`/`revert` 并入这里或 `refactor` |
| `security` | 安全整改或漏洞 | 可叠加在 `bug`/`feat` 上；不单独占一个“类型”位置 |

规则：

- 类型单选，`security` 例外（可叠加）。
- 类型不是阶段：`未开始`/`进行中`/… 由 `issue-status` 备忘录管，本备忘录不建同类标签。
- 类型不是范围：`scope:*` 继续由各仓自己管；`design` 用 `scope:design`，不新增 `design` 类型。
- 类型不是优先级：本轮不设 `p0`–`p2`。

## 迁移映射

| 现状 | 动作 | 覆盖范围 |
|---|---|---|
| `enhancement` 在、`feat` 不在 | `gh label edit enhancement --name feat --color 1D76DB --description "类型：新功能或能力变更"` | open + closed（改名保留全部挂单） |
| `enhancement` 与 `feat` 都在 | 报告；用户点头后把 `feat` 加到所有挂 `enhancement` 的单，再删 `enhancement` | open + closed |
| `documentation` 在、`docs` 不在 | `gh label edit documentation --name docs --color 0075CA --description "类型：文档、spec、README"` | open + closed |
| `documentation` 与 `docs` 都在 | 同上报号、合并、删旧 | open + closed |
| `type:feat` / `type:docs` / `type:chore` / `type:refactor` | 目标名不存在就改名；存在就合并后删旧 | open + closed |
| `type:fix` | 迁到 `bug`，不新建 `fix` | open + closed |
| 缺的 `perf` / `test` / `security`（以及改名后仍缺的 `feat`/`docs`/`chore`/`refactor`） | `gh label create` | — |
| GitHub 默认 `bug` | 保留，不改名 | — |

原则：

- **机械迁移不等于回填**：已有旧类型标签的单（含 closed）都要迁，因为那是保留已有分类；没有类型标签的 closed 单不补。
- 同名已存在不覆盖颜色和描述，只报告差异；删旧标签前先给用户看清单。
- 中文旧词（如果有）只报告、不自动映射；语义重叠由用户拍板。

## 回填口径

- 只回填 **open** 单里没有任何类型标签的（2026-10-29 实测 128 个）。
- 做法：`gh issue list --state open --limit 1000 --json number,title,labels` → 逐单提议一个类型 → 汇总清单给用户抽检 → 用户点头后 `gh issue edit <N> --add-label <type>`。
- 判不准的单列“待定”，不猜；`security` 只在明确是安全问题时叠加，不因为“可能有关”就挂。
- closed 单不回填；机械迁移已有标签除外。
- 回填完成后报告：已挂多少、待定多少、closed 跳过多少。

## 改动面

### 1. 新增 `references/issue-type-labels.md`

节序：

1. 头部可选提示 + `## 采用口径` 区块（七项：默认 / 本次按需读取 / 项目级采用 / 项目入口 / 项目资产 / 执行时点 / 验收）。
2. 一、8 个类型（表：标签 / 标什么 / 边界）。
3. 二、命名与互斥规则（裸名、小写、单选、`security` 可叠加、类型≠阶段/范围/优先级）。
4. 三、迁移映射（表 + 覆盖范围 + 先报告后动手）。
5. 四、回填口径（open only、待定不猜、closed 不动）。
6. 五、项目怎样采用（指向 `apply-to-project.md` §九之二；本仓不维护采用名单）。
7. 六、验收（dogfood 场景）。

头部提示沿用 `issue-status-labels.md` 的体例：可选、不改变两段流程、不因项目 issue 多就自动启用、本仓不维护采用项目名单。

### 2. `references/apply-to-project.md`

- **§六 意图表**加一行：`issue-type` / 「同时启用 issue 类型标签」等变体 → 按语义执行 §九之二。
- **§六 已注册修饰词清单**：`adr`、`doc-lifecycle`、`issue-status` → 加 `issue-type`。
- **新增 §九之二「issue 类型标签（附加描述含 `issue-type` 时）」**（排在 §九 与 §十 之间；不重排 §十，避免改历史引用）：
  1. **先查后报告**：`gh label list --limit 200`；列出 `enhancement` / `documentation` / `type:*` 的存在与挂单数、open 无类型单数、拟改名/合并清单。用户点头前不动远端。
  2. **迁移**：按“迁移映射”表执行；目标名已存在时先合并再加，删旧前给出清单；closed 也迁（机械迁移）。
  3. **建 8 个标签**：逐条 `gh label create`（名字/颜色/描述见本 spec D6）；同名已存在的跳过，不覆盖颜色描述。
  4. **回填 open**：按“回填口径”执行；待定单不猜。
  5. **往 `AGENTS.md` 写指针节**，模板：

     ```markdown
     ## 已采用：issue 类型标签

     本仓**已采用** spec-flow 的[issue 类型标签备忘录](https://github.com/Strelizialeomon/spec-flow/blob/main/references/issue-type-labels.md)（【应用日期】用户拍板）。**规则正文不在本文件复述**——8 类定义、迁移映射、开单挂标、回填口径都去读那一份。

     - 新建 issue 时挂一个类型标签：`feat` / `bug` / `docs` / `refactor` / `perf` / `test` / `chore` / `security`；`security` 可与其他类型叠加。
     - 历史单只回填 open，closed 不动；旧类型标签已机械迁移。
     ```

  6. **幂等**：8 个标签全在（含改名后的等价名）→ 跳过第 3 步；指针节已存在 → 只校验形制；重复采用不重复建、不重复回填。
  - 结尾报告：改名/合并/新建了哪些、跳过哪些、回填多少、待定多少、closed 跳过多少。
- **§十 采用契约**：
  - `#### issue-type` 登记表（八项字段齐全）。
  - 散文里的「三个现有修饰词」→「四个」；「§四／§八／§九 的三份入口模板」→ 加 §九之二，改成四份。

### 3. `SKILL.md`

| 位置 | 改动 |
|---|---|
| 参考表 | 新增一行：路径 `references/issue-type-labels.md`，右格「选修 `issue-type`——开单挂类型与回填」 |
| 正文预算 | 改后正文会超 4,700（改前 4,699）；同批腾挪 ≥ 新行长（约 65 字），候选：参考表各行描述压缩、第 31/78/85/105/111 行去冗词；最终以 `scripts/check-docs.sh` 绿且 ≤4,700 为准，不调预算 |

### 4. `README.md` / `README.zh-CN.md`

- 两份「文件」表各加一行：`references/issue-type-labels.md | 可选：issue 类型标签` / `Optional: issue type labels`。
- 两份 rationale 计数：`30 entries` → `31 entries`；`30 条记录` → `31 条记录`；`R1–R30` → `R1–R31`。
- 两份必须同步；`scripts/check-docs.sh` 核节标记与 references 路径。

### 5. `references/rationale.md`

新增 `## R31 issue 类型标签（主文件·项目体例与参考；references/issue-type-labels.md；apply-to-project.md §九之二）`，记录：

- 2026-10-29 实测：29 仓 / 869 单 / 334 裸单（38%）；open 181 / 128 无类型；711 条标题 keyword 计数。
- 调研出处（Conventional Commits / GitHub / Kubernetes / Keep a Changelog / GitLab / GitHub Issue Types）。
- 拍板：8 类、裸名、迁移、各项目全包、open-only 回填、不做优先级/卡点、不设 design/research。
- 边界：历史单语义分类可能错；不建中央脚本、不维护采用名单；taoxi-project 原生类型 0 单在用，不依赖。

### 6. `scripts/check-docs.sh`

- 预期无需改代码：参考表新增选修行 + §十 新增 `#### issue-type` 表后，检查器应自动核到 4 个备忘录 / 4 张登记表。
- 实施时必须实跑：若报红，优先修文档形制（字段、节标题），不改检查器；确需改检查器时另列理由。

## 回响自查

| 落点 | 结论 |
|---|---|
| 机制 / 原理 | 8 类定义、迁移、回填、采用动作全部落在新备忘录与 §九之二 |
| 实现 / 数据源 | 不写脚本；只用 `gh label` / `gh issue list` / `gh issue edit` |
| 实施步骤 | 新备忘录 + §六 表 + §九之二 + §十 登记表 + SKILL.md 参考行 + 双语 README + R31 |
| 验收标准 | 见下 |
| 跨文档引用 | 全文搜 `三个现有修饰词`、`三份入口模板`、`R1–R30`、`30 条`/`30 entries`；只改与本次相关的 |
| 历史记录 | 旧 spec 不回改；rationale 历史 R 条目不改 |

## 不做清单

- 不做优先级（`p0`–`p2`）、不做卡点标签（`等拍板`/`受阻` 已由 `issue-status` 管）。
- 不设 `style` / `build` / `ci` / `deps` / `revert`；分别并入 `refactor` / `chore`。
- 不设 `design` / `research`；`design` 用 `scope:design`，`research` 归 `docs`/`feat`，open 数 ≥5 且需要单独过滤时再立。
- 不做中央批量脚本、不做 `labels.yml`、不做 CI 同步；各项目 agent 自己跑。
- 不维护采用项目名单；不依赖 GitHub 原生 Issue Types。
- 不给 closed 单做语义回填。

## 验收标准

- [ ] 1. 实施分支上 `scripts/check-docs.sh` 全绿；正文 ≤4,700；警示符仍为 3；references 路径全部存在；README 双语节标记一一对应。
- [ ] 2. `references/issue-type-labels.md` 存在，含：可选提示 + 采用口径七项；8 类定义表；命名/互斥规则；迁移映射；回填口径；采用指针；dogfood 验收。
- [ ] 3. `references/apply-to-project.md` §六 有 `issue-type` 行、已注册清单含 `issue-type`；§九之二 六步齐全；§十 有 `issue-type` 八字段登记表；散文里的“三个”改成“四个”。
- [ ] 4. `SKILL.md` 参考表有新行；正文预算绿。
- [ ] 5. 两份 README 都有新 references 行；R 计数为 31；`R1–R31`。
- [ ] 6. `references/rationale.md` 有 R31，含 2026-10-29 实测数据、调研出处、拍板与边界。
- [ ] 7. dogfood（临时假仓）：默认不建标签；应用后 8 个标签齐全；`enhancement`→`feat` 改名保留已挂单；重复采用幂等；回填只动 open；closed 不补。

## 自定细节

| # | 自定细节 | 理由 |
|---|---|---|
| D1 | spec 落 `docs/specs/2026-10-29-issue-type-labels.md` | 仓体例 |
| D2 | worktree `~/code/spec-flow.worktrees/spec-issue-type-labels`、分支 `spec/issue-type-labels` | spec 期不占实施锁 |
| D3 | 备忘录文件名 `references/issue-type-labels.md` | 与 `issue-status-labels.md` 同体例，说清是什么 |
| D4 | 修饰词 `issue-type` | 短、与文件名对得上 |
| D5 | 8 类裸名小写；`docs` 不用 `doc`，`bug` 不用 `fix` | 与 Conventional Commits / GitHub 默认词对齐 |
| D6 | 颜色与描述：`feat` 1D76DB「类型：新功能或能力变更」；`bug` D73A4A「类型：行为不符合预期（含线上故障、回归）」；`docs` 0075CA「类型：文档、spec、README」；`refactor` 6F42C1「类型：不改外部行为的代码重构」；`perf` FBCA04「类型：性能优化，需有可对比指标」；`test` 0E8A16「类型：测试、用例、测试基建」；`chore` BFD4F2「类型：依赖、构建、CI、配置、杂务」；`security` B60205「类型：安全整改或漏洞，可叠加在 bug/feat 上」 | 冷色功能/文档、红橙缺陷/安全、灰蓝杂务；描述都在 GitHub 100 字上限内 |
| D7 | 新采用动作编 §九之二，不重排 §十 | §十 被 20+ 处引用；重排会改历史 rationale 与检查器 |
| D8 | 类型单选，`security` 可叠加 | 安全是限定词，不是与 bug/feat 互斥的类型 |
| D9 | 机械迁移覆盖 open+closed；语义回填只 open | 保留已有分类 vs 不花成本猜历史 |
| D10 | 不建中央登记表 / 采用名单 | 本仓规矩 R9；项目指令就是入口 |
| D11 | 不新增可执行资产（脚本 / CI / labels.yml） | 可执行资产升级闸；本轮只需 `gh` 命令 |
| D12 | 原生 Issue Types 不用 | nano-sun99 是个人号、`gh` 不认 `issueType`、跨仓要一致 |
| D13 | `design`/`research` 不单列 | `scope:design` 已存在；research 量小，先归 docs/feat |
| D14 | 预算腾挪不调 4,700 | R25 明确不上调；靠压缩参考行与冗词腾 |
| D15 | 「应用 `issue-type`」先报告再动手；删旧标签、回填 open 前给清单 | 改远端标签对外可见；与 `issue-status` §九 的窄授权一致 |

## 审核修订记录

（待审核）
