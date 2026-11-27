<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo/spec-flow-lockup-dark.svg">
    <img alt="spec-flow" src="assets/logo/spec-flow-lockup.svg" width="480">
  </picture>
</p>

**给 AI 编码 agent 用的决策环境——不是流程编译器。** 先谈清目标、范围和验收，再按明确委托实现与交付；硬闸严格，闸内路径灵活。

它没有运行时或服务，是 agent 读取的 Markdown 规则。开 spec 路径保留获批规格、执行 issue 与可追溯来源；直接干跳过方案期，但不免独立 worktree、验收与合并闸。代码地图默认停用，影响判断靠源码、真实 diff 与相关测试。

[`SKILL.md`](SKILL.md) 是唯一入口（正文 ≤ 2,600 字），背后是极简的必读内核（L0–L2，≤ 15,500 字）、两份按需专项总纲、9 条精简 Playbook 与 15 条案例库。[`scripts/check-docs.sh`](scripts/check-docs.sh) 守卫单文件、必读核与全仓现行规则总字数（≤ 46,000 字）预算、单行长度上限、链接 / 锚点可达性与双语 README 同步。已废弃的 v1 文档归档于 `docs/archive/v1/`。

[English](README.md) · **中文**

<!-- s:shape -->
## 用起来是什么样

同一句“给个人资料页加头像上传”，没有共识时 agent 可能直接交来你没要的数据库表和自定上限。

`spec-flow` 先核现有事实，只把影响范围、验收或授权的缺口交给你选。边界清晰的小改一句话说明改动面后即可直接干；复杂需求先按项目事实澄清，记录决定与可核来源。

需要规格时，骨架、设计对照和终稿沿用同一份文件与同一个 PR。有页面等你的设计稿，无页面用可判对错的输入输出与能推翻方案的业务例子核对。审核档位、修订范围、合并与实施委托各自独立确认。

<!-- s:problem -->
## 它解决什么

失误常在接缝：需求没对齐、多人撞车认领同号任务、审核被当成合并同意、同一决定在多份文档里互相打架，或代码刚合并就漏掉文档与部署宣称完成。

解法不是让每一步更啰嗦，而是让每条规则、决定、交付物与证据**各有唯一 owner**：查得清的事实先查，只在用户必须拍板的硬闸停下。

<!-- s:scars -->
## 这些规矩是从哪来的

真实事故保存在 [`references/40-cases/`](references/40-cases/)（只叙述与提议，本身不构成授权）：

- **判据漂移**：IDC 判据扩成 CIDR ∪ ASN，实现与父文档却停在旧口径 → 单一 owner 替换式变更与双扫描。
- **并发认领**：两个 agent 都把 `open` issue 当无人认领 → 真实认领锁是 Git 建出独立 `issue/<N>` worktree。
- **审核范围扩散**：连续六轮审核不断加规则导致互殴 → 成因分类、「能不能不修 / 砍路径」与 R1–R3 轮次上限。
- **改已合并 spec**：17 个提交反复改已合并规格正文 → 合并即冻结，范围变化走 D3 新开 spec。
- **无委托开工**：spec 刚合就自动动手写代码 → 明确的 D0 实施委托闸。

<!-- s:what -->
## 它怎么解决

对外仍是**两段主线**（方案期与实施期），对内按清晰层次组织：

- **每次必读内核**：L0 铁律（8 条）→ L1 阶段合同与记录（4 段完成条件、反熵增三问与竣工回写、15 类记录）→ L2 决策目录（D0–D7 硬闸 + 交互卡片契约）。
- **按需专项总纲**：规格文档治理（精简底座 + 3 个按需治理组件与中途平滑升级）与审核契约（档位、R1–R3、#158 机制、Lane A/B 模板）。
- **按需 Playbook 与案例**：[`references/30-playbooks/`](references/30-playbooks/) 下 9 条精简走法与 [`references/40-cases/`](references/40-cases/) 下 15 条案例。

完整文件地图见 [`references/README.md`](references/README.md)。

<!-- s:self-review -->
## 唯一值得直接拿走的一条：分身不是第二个人

agent 派出的子 agent 仍是它自己的执行分身。换模型、名字或 prompt 不会自动变成独立意见；自测和草拟也不能冒充审核。

每份交付审不审、审哪档由用户当场选（不审 / 轻审 / 重审 / 重审+变异）。真正需要另一方裁决时，材料备好后停等指定方。Markdown 规则不等于平台权限隔离。

<!-- s:smooth -->
## 为什么它不累赘

必要决定优先用客户端选项卡（无工具列等价文字选项），给出事实、差别与推荐。只有 D0–D7 八类固定决策加上 L0-1 不可逆动作与 L0-7 承重缺口会停住 agent；非承重写法由 agent 自主决定并报告。

开 spec 统一从单一精简底座起步（4 列简版决定表 + 反熵增三问：重叠盘点 / 减法清单 / 现状真身落点）；重型治理（跨切面盘点表、多文档/视图对账、替换式变更 manifest）只按客观事实按需激活，审核中途扩大也可原位平滑升级。直接干不填三问，纯内部小改零额外文书税，仅改变对外可见行为、命令、架构、接口或 README 时同步现状文档。

<!-- s:longrun -->
## 它凭什么扛得住长活

Git 持有认领锁（`issue/<N>` worktree）；原 issue 交接区记录当前阶段与全部合入 PR 来源；冻结 spec 锁定获批范围；只追加记录保存 D0–D7 拍板。换会话不用靠私有聊天记忆猜谁在做或上线带了什么。

<!-- s:limits -->
## 它不做什么

- 不调度 agent、不自动续跑，也不提供平台级权限隔离。
- 不保证永不出错；完成意味着约定交付存在、必要检查通过、无已知阻断且证据可核。
- 不把实现合并、标签或 tag 等同于线上部署验证成功。
- 不静默安装外部技能、建长期分支、造 CI/Hook 或发布平台；issue/PR 流程假定 GitHub。

<!-- s:install -->
## 装

```bash
git clone https://github.com/nano-sun99/spec-flow.git ~/.claude/skills/spec-flow
```

也可 clone 到工作目录再软链进客户端技能目录。`spec-flow` 用客户端自带选项卡或文字选项自主完成需求澄清，不依赖任何外部澄清技能。项目接入见 [`references/50-adapters/README.md`](references/50-adapters/README.md)。

<!-- s:usage -->
## 怎么用

描述需求或点名 `spec-flow`；实施既有单直接说“做 `#12`”。委托证据与交互卡片口径见 [`references/20-decisions.md`](references/20-decisions.md)。

说“把 spec-flow 应用到本项目”接入，说“更新本项目的 spec-flow 接入”做显式升级。接入只写只指向式指针——绝不复制流程正文，也不顺手开启选修模块。

5 个选修模块（`adr`、`doc-lifecycle`、`issue-status`、`issue-type`、`release`）均**默认关闭**。其中 `release` 统一覆盖 Git 分支形态（单主线 / 三层 / staging 线）、发布安全不变式、批次失败修复与生产应急。

<!-- s:evidence -->
## 本仓自己就是样板

规格、变更清单、行为评测、案例与校验脚本均留在本仓。静态绿是必要条件，不代替客户端或生产实测：`scripts/check-docs.sh` 守卫预算、单行长度、链接锚点与双语同步；`scripts/check-change.py`（配 `scripts/test-check-change.py`）支持本仓与外部项目（`--root <project>`）的替换式变更校验；`evals/` 与 `scripts/run-eval.py`（配 `scripts/test-run-eval.py`）提供 CLI 无关的行为级护栏与反膨胀回归评测及基线对比。

<!-- s:docs -->
## 文件

| 文件 / 目录 | 职责 |
|---|---|
| `SKILL.md` | 唯一入口、运行循环、一跳导航与异常协议 |
| `AGENTS.md`、`CLAUDE.md` | 本仓维护规矩；`CLAUDE.md` 导入 `AGENTS.md` |
| `references/README.md` | 分层说明与阅读顺序地图 |
| `references/00-constitution.md` | L0：8 条铁律（仅用户按 L0-8 修改） |
| `references/10-stages.md` | L1：4 段阶段合同、核心术语（含反熵增三问 / 竣工回写）与交付前置 |
| `references/15-records.md` | L1：15 类记录、D0–D7 留痕、文档载体、关单与观察式例外 |
| `references/20-decisions.md` | L2：D0–D7 硬闸、交互卡片契约与标签确认 |
| `references/25-spec-governance.md` | 规格文档治理唯一正文（精简底座、3 按需治理组件、视图权威顺序与中途平滑升级） |
| `references/26-review-contract.md` | 审核契约唯一正文（档位、R1–R3、#158 五机制、文档检查与 Lane A/B 模板） |
| `references/30-playbooks/` | 9 条按需 Playbook（`new-spec`、`direct`、`issue`、`change-protocol`、`release`、`incident`、`labels`、`worktree`、`adr`） |
| `references/40-cases/` | L4：15 条事故与演练案例（叙述 + 提议，不是授权） |
| `references/50-adapters/` | 自足的只指向式项目接入契约与 5 个选修模块 |
| `evals/` | 行为级 Eval 回归套件（`evals/README.md`、自足 JSON `scenarios/` 与脱敏 `baselines/`） |
| `docs/archive/v1/` | 已废弃的 v1 文档与冻结的 `rationale.md`（历史档案） |
| `docs/maintainer-notes.md` | 本机软链接线与仓库历史 |
| `scripts/check-docs.sh` | 守卫单文件、必读核与全仓现行规则总字数预算、单行上限、链接与锚点、owner 章节与双语 README 同步 |
| `scripts/check-change.py` | 跨项目 v2 薄声明 + 自动扫 diff 替换式变更校验器（`schema: 2`、`--root`、`--draft`、manifest-only 尾提交钉扎） |
| `scripts/run-eval.py` | CLI 无关行为级 Eval Runner（`--validate`、`--materialize`、`--run`、`--grade`、`--baseline`；配 `scripts/test-run-eval.py`） |

README 是介绍，实际执行请从 `SKILL.md` 进入各唯一正文 owner。

<!-- s:contributing -->
## 参与

开 issue 或 PR。每条规则保持单一 owner，新教训记入 `references/40-cases/`，替换式变更跑 `scripts/check-change.py`，两份 README 同批同步并通过 `bash scripts/check-docs.sh`。

<!-- s:license -->
## 许可

MIT，见 [LICENSE](LICENSE)。
