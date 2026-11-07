# ADR-20261105 · spec 正文交给 brainstorming 生成

- 状态：提议（未实施；实施记录见 `docs/specs/2026-11-05-spec-generation-wiring.md`）
- 日期：2026-11-05
- 决策人：用户
- 形态：一次性 ADR，**不代表本仓已采用 ADR 制度**（无规则页、无项目入口、无检查脚本）

## 背景

`spec-flow` 全文 0 处引用 superpowers / brainstorming（`grep -rn "superpowers\|brainstorm"` 无命中）；29 份 spec 里只有 2 份写了备选。同时 `~/.agents/AGENTS.md` 写着「superpowers 只用 `brainstorming`，禁用 `writing-plans`」。

三条放在一起说明一件事：**同一套活有两套生成器，全局规矩那一套从来没生效过**。spec 一直由 spec-flow 自建模板生成，而 brainstorming 的产物里有两段我们没有的东西——Approaches 和 anti-goals。

## 决定

1. **spec 正文归 brainstorming**：段一在机制卡、页面卡之后调用它，正文由它写，spec-flow 不碰。
2. **spec-flow 只加附录**：文末追加「路线表 + DoR 核对」，给派审挂步号、给拆分和验收当宿主；附录与正文冲突时以正文为准，附录不得引入正文没有的决定。
3. **拦 writing-plans**：brainstorming 批准后强制调下一个技能，我们截住，转入自己的闸与开单。
4. **ADR 保持选修**：不为"备选方案该放哪"而默认启用 ADR。

## 否决的方案

- **自建模板模仿原味**：仿品。模板能抄结构，抄不到 brainstorming 在对话里挖出来的东西；而且它每更新一次，我们就更像赝品。
- **ADR 默认启用，把 Approaches 搬进 ADR**：粒度错配。ADR 记的是跨任务长期决定，一份 spec 一条 ADR 会让 ADR 变成 spec 的镜像，取代链越滚越长；而且每个接入仓都要默认建目录和规则页，与"选修默认关闭"冲突。更关键的是——搬走 Approaches 会让 spec 不再自足，而 brainstorming 对设计文档的定义是「熟手不用回去问人就能照做」。

## 后果

- 依赖外部 skill 的产物契约：它改结构，我们接不住。缓解是附录必须能从正文推出，删附录 spec 仍可读。
- 多一处要守的边界：writing-plans 的拦截是文字约束，不是钩子，跨 harness 无强制。
- 需要一条回落路径（未决，见 spec §5 U1）：没装 superpowers 的机器不能直接瘫痪。

## 何时重开

1. brainstorming 的产物契约发生变化（段结构改名或合并）；
2. 回落路径在实际使用中成为常态而非例外；
3. 采用仓里没装 superpowers 的比例高到回落模板变成事实标准。
