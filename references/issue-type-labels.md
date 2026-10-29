# 备忘录：用类型标签给 issue 分类

> 这是可选备忘录，不改变 spec-flow 两段流程的步骤与顺序，默认不启用。只有用户明确要求采用，或项目规则已经声明采用，才按它执行；不因项目 issue 多就自动启用。采用动作见 [〈应用到项目〉§九之二](apply-to-project.md)，本仓不维护采用项目名单。

## 采用口径

- 默认：选修，不因项目复杂自动启用
- 本次按需读取：用户明确要求本次按本备忘录执行时读取
- 项目级采用：通过 `apply-to-project` 的 `issue-type`，或项目指令明确声明已采用时生效
- 项目入口：采用后由 `apply-to-project` 写入项目指令的指针节
- 项目资产：8 个标签（feat / bug / docs / refactor / perf / test / chore / security）；不新增可执行资产
- 执行时点：新建 issue 时挂类型；项目首次采用时迁移旧标签、回填 open 单
- 验收：机械检查不适用；dogfood 验证默认不建标签、采用后同名不覆盖、改名保留已挂单、重复采用不重复建

## 一、8 个类型

| 标签 | 标什么 | 边界 / 对应 |
|---|---|---|
| `feat` | 新功能或能力变更 | 原 `enhancement`；对应 commit `feat` |
| `bug` | 行为不符合预期 | 含线上故障、回归；对应 commit `fix` |
| `docs` | 文档、spec、README | 原 `documentation`；用 `docs` 不用 `doc` |
| `refactor` | 不改外部行为的代码重构 | 对应 commit `refactor` |
| `perf` | 性能优化 | 要有可对比指标，不接受“感觉快了” |
| `test` | 测试、用例、测试基建 | 对应 commit `test` |
| `chore` | 依赖、构建、CI、配置、杂务 | 对应 commit `chore`；`style` / `build` / `ci` / `deps` / `revert` 并入这里或 `refactor` |
| `security` | 安全整改或漏洞 | 可叠加在 `bug` / `feat` 上；不单独占一个“类型”位置 |

为什么是这 8 类：`feat` / `bug` / `docs` 是任何仓都绕不开的三类；`refactor` / `perf` / `test` / `chore` 对应 Conventional Commits 的常用扩展，能和 commit 词表对上；`security` 在发布说明里要能单独捞出。`design` 用 `scope:design`，`research` 归 `docs` / `feat`，不单列。

## 二、命名与互斥

- **裸名小写**，不加 `type:` 前缀；与 GitHub 默认的 `bug` 和 Conventional Commits 的 `feat` / `docs` 对齐。
- **一单一个类型**；唯一例外是 `security`，它可以叠加在 `bug` / `feat` 上。
- **类型不是阶段**：`未开始` / `进行中` / `待测试` / `待上线` / `待验证` 归 `issue-status` 备忘录，本备忘录不建同类标签。
- **类型不是范围**：`scope:*` 由各仓自己管；`design` 用 `scope:design`，不新增 `design` 类型。
- **类型不是优先级**：本备忘录不设 `p0`–`p2`。
- **类型不清先问**，不猜；一个单同时像 `bug` 和 `feat` 时，按“用户感知到的行为是否发生变化”判：行为坏了是 `bug`，行为按预期新增是 `feat`。

## 三、迁移映射

| 现状 | 动作 | 覆盖范围 |
|---|---|---|
| `enhancement` 在、`feat` 不在 | 改名 `enhancement` → `feat` | open + closed（改名保留全部挂单） |
| `enhancement` 与 `feat` 都在 | 报告；用户点头后把 `feat` 加到所有挂 `enhancement` 的单，再删 `enhancement` | open + closed |
| `documentation` 在、`docs` 不在 | 改名 `documentation` → `docs` | open + closed |
| `documentation` 与 `docs` 都在 | 同上报号、合并、删旧 | open + closed |
| `type:feat` / `type:docs` / `type:chore` / `type:refactor` | 目标名不存在就改名；存在就合并后删旧 | open + closed |
| `type:fix` | 迁到 `bug`，不新建 `fix` | open + closed |
| 缺的 `perf` / `test` / `security`（以及改名后仍缺的 `feat` / `docs` / `chore` / `refactor`） | 新建 | — |
| GitHub 默认 `bug` | 保留，不改名 | — |

原则：

- **机械迁移不等于回填**：已有旧类型标签的单（含 closed）都要迁，因为那是保留已有分类；没有类型标签的 closed 单不补。
- 同名已存在不覆盖颜色和描述，只报告差异；删旧标签前先给用户看清单。
- 中文旧词（如果有）只报告、不自动映射；语义重叠由用户拍板。

## 四、回填口径

- 只回填 **open** 单里没有任何类型标签的；closed 单不回填（机械迁移已有标签除外）。
- 做法：`gh issue list --state open --limit 1000 --json number,title,labels` → 逐单提议一个类型 → 汇总清单给用户抽检 → 用户点头后 `gh issue edit <N> --add-label <type>`。
- 判不准的单列“待定”，不猜；`security` 只在明确是安全问题时叠加，不因为“可能有关”就挂。
- 回填完成后报告：已挂多少、待定多少、closed 跳过多少。

## 五、开单挂标

- 新建 issue 必须带一个类型标签：`gh issue create ... --label <type>`；手工在网页建单也一样。
- 类型默认单选；`security` 可与其他类型叠加。
- 类型不清先问用户，不猜；一个单只挂一个主类型，避免 `feat` + `bug` 同时挂。
- 采用本备忘录的项目，按项目指令指针节执行；未采用的项目不加这条动作。

## 六、项目怎样采用

- 通过〈应用到项目〉的附加描述 `issue-type` 采用：建 8 个标签、迁移旧类型标签、回填 open 单、在项目指令留一段指针。
- 步骤、`gh label create` 命令、指针节模板见 [〈应用到项目〉§九之二](apply-to-project.md)。
- 本仓不维护采用项目名单；哪个仓采用了，问那个仓自己的指令。

## 七、验收

dogfood 在临时假仓（不碰真实采用项目）跑以下场景，产物写进实施 PR：

1. 默认不建标签：未采用时 `gh label list` 没有这 8 个类型。
2. 应用后 8 个标签齐全，颜色 / 描述与 §九之二 一致。
3. `enhancement` → `feat` 改名后，原先挂 `enhancement` 的单仍挂着 `feat`。
4. 重复采用幂等：标签已全在时跳过创建，指针节不重复追加。
5. 回填只动 open：open 单补类型，closed 单不动；机械迁移的旧标签 open + closed 都迁。
