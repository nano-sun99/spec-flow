<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo/spec-flow-lockup-dark.svg">
    <img alt="spec-flow" src="assets/logo/spec-flow-lockup.svg" width="480">
  </picture>
</p>

**给 AI 编码 agent 用的一套流程规矩。** 把它 clone 进 agent 的技能目录；此后你交办一件值得先设计的活时，agent 会先跟你把「要做什么」谈定，**再**动代码——而它产出的每一份东西都要过一道闸，**由你**决定给它多少审核。

**默认只读 3 份。** 开工读一页，过闸读闸表，动 PR / issue 读项目页；其余 17 份分层放好——场景包触发才读，选修默认关闭，地图归档。另有一个 `spec-check` 脚本做确定性检查：三行锚缺失、验收为空、占位符没填、diff 越出「改」清单，任何一条当场红。

**这套规矩不许再长胖。** 新翻车只准进检查脚本，或替换一条旧规矩；不准新增章节、卡片、参考文件。预算写在 `scripts/check-docs.sh` 里——正文 2,800 字符、`SKILL.md` 60 行、默认 3 份 180 行——超了就红。

流程本身没有运行时或服务。它是 agent 读的 Markdown，加上纸面痕迹：代码前有 spec、动手前有 issue、两者有永久链接。

[English](README.md) · **中文**

> 本 skill 的正文是中文（`SKILL.md` 与 `references/`），这份是中文全文。

<!-- s:shape -->
## 用起来是什么样

两边你对 agent 打的字一模一样：**「给个人资料页加个头像上传」**。

**没有它**，agent 当场开写。四十分钟后你拿到一个横跨十一个文件的 diff、一张你没要过的数据库表，和一个它自己定的体积上限。它是怎么决定的——你得读代码才知道。

**有它**，agent 两分钟就回来，带着三个它替不了你决定的问题——文件存哪、要不要支持手机、40MB 的上传该怎么办——此外什么都没有。然后它写一页开工单：目标 / 不做 / 验收，改哪些 / 不改哪些，加一张验收表；先跑脚本，任何一条红就停。这一页单独开一个 PR，你点审核档——**不审 / 轻审 / 重审 / 重审 + 变异**。审核固定四进三出、最多两轮，范围外的发现进建议池，不变成修订；每轮第一行是「目标 / 本轮推进 / 还差」。审完它单独问你要不要合并；合并 spec、开执行 issue，实施仍要你明确委托。代码在自己的 worktree 里改，每轮拿 diff 对一次「改」清单。

**那个本来要等到第四十分钟才暴露的误解，现在第二分钟就暴露了。**

<!-- s:problem -->
## 它解决什么

编码 agent 栽跟头的地方不在某一步里面，在**接缝**上：

- **在你的交代和它的理解之间**——它拿着半成形的需求就开写，你到看 diff 时才撞见误解；
- **在一份交付物和下一份之间**——它一口气干完一大坨，中间没有一处能拦住那个走错的弯；
- **在 agent 和「检查 agent 的那个东西」之间**——它报告「已由独立审核复核」，而那个审核是它自己派的、自己写的 prompt、自己给的角度；
- **在两个 agent 之间**——两边都把同一个 issue 读成「没人认领」，同一件事做了两遍；
- **在上个月的决定和今天的活之间**——一次改动背后的道理留在一场没人能重新打开的对话里。

这些都不是模型能力问题，也不是「某一步再努力一点」能修的。它们是**没人认领的边界**。

<!-- s:constitution -->
## 它为什么不会再长胖

**每翻一次车加一条规矩，规矩就不可执行，下次再补。** 8 周里这套东西从 44 行长到 2,945 行，涨的从来不是能力，是默认面。所以这一版停的不是历史，是「默认面继续长」。

- **分层**：3 份常驻——开工一页、闸表、项目页；其余 17 份全部保留，按层放好（场景包 / 选修 / 归档 / 按需），每份一行触发条件，默认路径不读第 4 份。深水区不删，只是不默认读。
- **宪法**：只准加检查，不准加规矩。新翻车要么变成 `spec-check` 的一条规则，要么替换一条旧规矩；不准新增章节、卡片、reference。默认面 3 份是白名单，加第 4 份要你点头。
- **检查进脚本**：`spec-check` 管 E1–E5——三行锚、AC 是否可验、占位符、未处置的 ❌、diff 越界；warn 不拦，error 退出 1。人能盯住的事，交给能重跑的东西。

**账**：默认面 2,945 → 137 行，`SKILL.md` 118 → 60 行；仓库总量没降，降的是你每次要读的那部分。

<!-- s:what -->
## 两段怎么转

**两段流程，共用一道闸。** 每一步认领上面的一条接缝。

```
段一 · 方案期（1–6，一行代码都不写）
1 需求 → 2 确认 → 3 骨架 → 4 拆分 / 对照 / 实施版 → 5 修订 / 合并 → 6 开执行 issue
                              ↓
                              ⏸ 停：第 6 步开完 issue 就收手，等你说「开始实施」
                              ↓
段二 · 实施期（7–9，你明确委托后才开工）
7 认领（worktree `issue-<N>`）→ 8 实施（每轮 `spec-check --base`）→ 9 过闸 / 合并 / 回填
```

| 步骤 | 它认领的接缝 |
|---|---|
| 你没点头，spec 文件碰都不许碰 | 交代 ↔ 理解 |
| 每份交付物各过各的闸 | 一份交付物 ↔ 下一份 |
| agent 不许替自己产出审核结论 | agent ↔ 检查它的东西 |
| 认领 issue = 建一个以它命名的 worktree | 一个 agent ↔ 另一个 |
| issue 锚着 spec 合并后的永久链接 | 上个月 ↔ 今天 |

<!-- s:self-review -->
## 唯一值得直接拿走的一条：分身不是第二个人

agent 派出去的一切都还是它自己——同一件事、同一段 prompt、同一个看问题的框架，而且是想要放行的那一方自己挑的。分身的结论只有它自己的分量，一分不多。

所以 spec-flow 禁止 agent 替自己产出审核结论：审不审、审哪档由你点，它不许派一个来替它判。某一步真的需要一份不属于它的意见时，这一步停下来，等人。

<!-- s:scars -->
## 这些规矩是从哪来的

不是从理论来的。每条规矩都是一次具体事故的沉淀，日期和数字都在 [`references/rationale.md`](references/rationale.md) 里。三个例子：

- **一条判据放宽了，别处一个没动。** IDC 判据从「CIDR 段」扩成「CIDR ∪ ASN」，只改了那一句——机制、实现、实施步骤、验收四处还在描述旧行为，父文档总纲也没改。照那份 spec 施工，做出来是 CIDR-only。→ **R1**：改一条判据，它的每个落点都要同步。
- **两个 agent 认领了同一个 issue。** 两边都把 *open* 读成「没人在做」，同一件事做了两遍，废掉一份。→ **R7**：认领的证据是 worktree 建成了，不是 issue 的状态。
- **一份 spec，被改了十七次。** 从 448 行长到 762 行，横跨 17 个提交，其中 14 个改的是正文。owner 最后在 agent 干到一半时打断：「我们这是新需求，写新的 spec，别老是改以前的 spec。」→ **R12**：改已合并的 spec 是一张要你点的卡，不是可以自己拿的主意。

另外 33 条在同一个文件里，每条都带日期、实测、决定、代价和验证边界。

<!-- s:longrun -->
## 它凭什么扛得住长活

**状态存在 git 里，不存在 agent 的脑袋里。**

| 想知道 | 写在哪 | 为什么信得过 |
|---|---|---|
| 谁在做 | worktree 的名字——锁本身 | 开 `issue-42` 开得成 = 没人做；被拒 = 有人在做。没有另一张会对不上的任务分配表。 |
| 做到哪了 | issue 的状态和 PR | 跨会话、换机器、交给别人，读到的还是同一份。 |
| 当初为什么这么做 | `docs/specs/` 里的 spec，issue 链过去 | 过了闸、是人话、跟代码一起版本化——能 diff、能 blame、能回滚。 |

把这类东西存在自己私有索引里的工具，漂了不会告诉你。这个不会：git 会在出事的那一刻当场喊出来。

<!-- s:limits -->
## 它不做什么

- **它不记得过程。** 试过什么又放弃了、哪个死胡同耗了一小时——没写下来的就没了。写下来的那部分是审核留痕：每条发现和它的处置，追加在 spec 末尾。
- **它不是运行时。** 没有东西会去调度 agent、给一次跑留检查点、或把凌晨三点挂掉的那次续起来。它假定你在场，站在闸前面。
- **它大部分靠自觉。** 这些是请 agent 遵守的规矩，不是逼它遵守的机制——包括独立合并确认。真正被强制的那部分，靠 git（worktree 那把锁）和本仓的检查脚本。
- **它假定你用 GitHub。** issue 和 PR 在这里是承重墙，不是装饰。

<!-- s:install -->
## 装

```bash
# 直接装
git clone https://github.com/nano-sun99/spec-flow.git ~/.claude/skills/spec-flow

# 或放在别处，再软链进来
git clone https://github.com/nano-sun99/spec-flow.git ~/code/spec-flow
ln -s ~/code/spec-flow ~/.claude/skills/spec-flow
```

这是技能安装，不是项目接入。Claude Code 从 `~/.claude/skills/<名字>/SKILL.md` 读个人 skill；在该检出里 `git pull` 更新。其他客户端走各自的技能发现路径。

脚本在 skill 根下；安装后是 `~/.claude/skills/spec-flow/scripts/spec-check.py`，在目标仓里用 `python3` 跑。

要求：一个能发现 skills、跑 shell（`git worktree`）、开 PR（`gh`）的 agent。文档检查绿，不证明客户端读到或遵守了规则。

<!-- s:usage -->
## 怎么用

- **触发**：描述一件值得先设计的活——比如「这个改动要动接口、数据库和前端」——也可以直接点名。
- **从中间进**：说「做 #12」就从段二开始，同样过闸、单独确认合并。同一窗口紧接唯一的 `SPEC_READY` 交接时说「开始实施」可续接；新窗口、别的 agent 或有多张未授权交接时，必须点名 issue 号。
- **要拆分**：骨架后摆拆分卡，拆成更小的执行 spec、各自的执行 issue，加一张只跟踪的父 issue；不拆就保留 1 份 spec、1 张单。细则在场景包里。
- **接入项目**：说「把 spec-flow 应用到本项目」，写入 `AGENTS.md` 指针，不抄正文；说「更新本项目的 spec-flow 接入」做幂等升级，不顺手启用没采用的选修。已采用 ADR 的项目，按它自己的规则检索、记录，收尾时核本次处理。
- **代码地图默认停用**：普通任务不查图、不补配置；只有你明确要求试用或恢复时才读[地图细则](references/code-map.md)。

实施前必须读当前获批的施工 spec。

<!-- s:evidence -->
## 本仓自己就是样板

spec-flow 是用 spec-flow 开发的。**101 个已合 PR、33 个 issue、30 份 spec**——这几个数随时能自己重算（`gh pr list --state merged --limit 500 | wc -l`；`ls docs/specs/*.md | wc -l`），不用信文档里的快照。

2026-11-04 这次瘦身也走了一遍两段流程：一轮重审抓出 1 阻断 / 11 高，全改后默认面 2,945 → 137 行，`SKILL.md` 118 → 60 行，新增 `spec-check` 与回放脚本。删掉的是默认要读的量，不是覆盖。

规矩按 `R` 编号被引用，形如 `（依据：rationale R12）`，36 条全在 [`references/rationale.md`](references/rationale.md)：日期、实测、决定、代价、验证边界，外加完整案例——包括 IDC 那条在一处放宽而另外四处连同父文档都没改，以及让「没有 bug」不再等于「我们保证以后永不出错」的完成标准。

<!-- s:docs -->
## 文件

| 层 | 文件 | 装什么 |
|---|---|---|
| 正文 | `SKILL.md` | 流程正文——agent 加载的就是它 |
| 本仓 | `AGENTS.md` / `CLAUDE.md` | 维护规矩；`CLAUDE.md` 只有一行 `@AGENTS.md` |
| 默认 | `references/one-page.md` | 开工一页：三行锚、范围、AC 表、四个选择、变更单 |
| 默认 | `references/gates.md` | 三闸、DoR 七条、审核四进三出、四档 |
| 默认 | `references/project-integration.md` | PR / issue / worktree / 回填；项目制度只放指针 |
| 场景包 | `references/one-path.md` | 路模板、方案页、走路审核、批次表、8 卡选项 |
| 场景包 | `references/gate-details.md` | 四档差异、多份叠加、文档检查红绿 |
| 场景包 | `references/spec-maturity.md` | 三阶段、DoR 细则 |
| 场景包 | `references/split-large-spec.md` | 拆分评估、稳定编号、父子单、依赖与批次表 |
| 场景包 | `references/phase-handoff.md` | 交接状态、实施授权、接手与交接区模板 |
| 场景包 | `references/done-criteria.md` | 完成标准、观察式收尾、三类例外 |
| 场景包 | `references/spec-revision-sync.md` | 改一条判据要同步所有落点 |
| 场景包 | `references/worktree-lock.md` | worktree 那把锁，以及它怎么坏 |
| 场景包 | `references/apply-to-project.md` | 应用、显式升级、指针模板与资产边界 |
| 场景包 | `references/adoption-model.md` | 采纳模型的历史解释，不增加流程义务 |
| 选修 | `references/adr-decision-records.md` | 架构决策记录（ADR） |
| 选修 | `references/documentation-lifecycle.md` | spec / ADR / issue 分工 |
| 选修 | `references/issue-status-labels.md` | issue 状态标签 |
| 选修 | `references/issue-type-labels.md` | issue 类型标签 |
| 选修 | `references/release-discipline.md` | 发布闭环：发布记录、就绪门槛、主干对齐、发布后回填 |
| 归档 | `references/code-map.md` | 已停用；明确试用 / 恢复才读 |
| 按需 | `references/rationale.md` | 每条规矩的依据：案例、实测、决定（R1–R36） |
| 脚本 | `scripts/spec-check.py` | 一页 / 范围 / AC / 占位 / 越界：E1–E5、W1–W2 |
| 脚本 | `scripts/replay-legacy-spec.py` | 把旧格式 spec 映射成一页 + AC 表，回放 `spec-check` |
| 脚本 | `scripts/check-docs.sh` | 预算、路径、双语同步、采用契约 |
| 本仓 | `docs/maintainer-notes.md` | 这份检出怎么接的线、最早的提交为什么是重建的 |

选修的文件默认关闭，项目规则声明已采用才读。流程正文是 `SKILL.md`——这份 README 与它说法不一致时，以 `SKILL.md` 为准。

<!-- s:contributing -->
## 参与

小步来。开个 issue，或者直接发 PR。一条约定：改动新增或修改了规矩，就把背后的案例记进 `references/rationale.md`、编个新 `R` 号——这里的规矩得指得出发生过的事。

<!-- s:license -->
## 许可

MIT，见 [LICENSE](LICENSE)。
