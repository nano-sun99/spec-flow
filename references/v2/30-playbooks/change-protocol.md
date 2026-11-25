# Playbook: 替换式变更（manifest + 校验脚本）

> **示例非必须**：本页的字段、顺序和扫描方法可替换；manifest schema 与校验器是当前实现。
> **规范性**：只有标「（规范性）」的章节；它们引用 L0-L2，不新增 D 类型，也不放宽闸口。完成条件在 [10-stages](../10-stages.md) 设计段与交付段；证据字段在 [20-decisions](../20-decisions.md) D2/D3/D4 与 [review](review.md)；载体处置在 [15-records](../15-records.md) §四。本页只给方法与证据格式。

- **适用**：改判据、术语、范围、owner、边界或分类；包括新增会改变既有行为的规则、退役旧规则。只改错字 / 措辞且不改变判定 / 范围 / 默认 / 权限的，不触发。
- **失败模式**：只加新句不列旧 owner；只 grep 新词；把已合并 / 冻结正文当草稿删改；把历史 / 别名当残留删；新增规则不说明取代或合并了哪条；台账写在 PR 正文里靠人肉对行号。
- **证据**：change manifest（JSON）、`scripts/check-change.py` 输出、载体分流结果、D2/D3/D4 与 review 的摘要。

## 一、三个工件（规范性）

1. **change manifest**：一次变更一个 JSON，默认 `docs/changes/<slug>/manifest.json`。它是唯一台账；PR 正文只放摘要。字段见 §二，模板见 [docs/changes/README](../../../docs/changes/README.md)。
2. **校验器**：`python3 scripts/check-change.py --manifest <path> --base <base> --head <rev>`；退出码 0 才算绿。它检查：必填字段、rules / scans / semantic_checks 非空、枚举、base 行号与 old.text（≥6 字）、new.anchor 在 head 文件中、add 的 same_trigger_search（≥6 字）、白名单 reviewer / review_ref、扫描 scope 非空且命中正反双向、未处置 0、改动文件覆盖（non_rule 只允许视图文件）。它不判断语义冲突。
3. **载体表**：[15-records](../15-records.md) §四 是载体处置的唯一正文；manifest 只引用。

## 二、manifest 字段（规范性）

| 段 | 必填 | 内容 |
|---|---|---|
| `change` / `title` / `base` / `head` / `classification` | 是 | 变更标识；base/head 解析为提交；classification ∈ add/replace/retire |
| `approval` | 是 | `user_quote` / `timestamp` / `scope` / `base` / `head` / `link`；用户原话与可核链接，不能只写 agent 转述 |
| `rules[]` | 是 | `id` / `type` / `old`（add 为 null）/ `new`（`file` / `section` / `anchor`）/ `disposition` / `evidence` / `status`；add 另需 `same_trigger_search`（≥6 字） |
| `whitelist[]` | 有白名单时 | `rule_id` / `reason` / `reviewer` / `review_ref`（user 与 review-agent 都必填）；每条白名单规则必须有对应条目 |
| `scans[]` | 是 | `query` / `scope` / `hits[]` / `conclusion`；hits 每条给 file/text/conclusion；whitelist 命中另给 reason/reviewer/review_ref |
| `semantic_checks[]` | 是 | `item` / `conclusion` / `evidence`；反向冲突逐条结论 |
| `rebuild` | 是 | `triggered` / `reason` / `old_behaviors[]`；触发时必须给旧行为清单 |
| `non_rule_changes[]` | 有视图 / 计数改动时 | `file` / `reason`；让校验器能覆盖非规则文件 |

- `type`：`add` / `replace` / `retire`。
- `disposition`：`replace` / `delete` / `merge` / `alias` / `keep-history` / `keep-scoped` / `not-applicable`。
- `status`：`done` / `whitelist` / `unresolved`；校验器遇到 `unresolved` 直接红。
- 一行一条规则；旧 owner 给 `file:line` 与 `text`（≥6 字），校验器按 base 核；新 owner 给 `file` + `section` + `anchor`（head 文件中唯一出现的字面片段）。`section` 是给人看的标签，机器校验靠 `anchor`。
- `manifest.head` / `approval.head` 写 `HEAD` 只用于开发期；合并卡必须写具体 head SHA。
- `non_rule_changes` 只允许视图 / 计数文件；规则文件必须落在 `rules[]`。

## 三、双扫描（规范性）

1. **活跃残留**：manifest 的 `scans[]` 写 query 与 scope（默认 `references/`、`docs/`）；校验器复跑 query，未登记的命中即红。白名单命中逐条写理由与 reviewer；作者自证标签不能单独成立。
2. **反向冲突**：语义读同层 / 相邻层，找五类（同触发不同行为、旧 owner 仍现行、多 owner、验收 / 范围 / 默认不一致、权限 / 载体错配）。结果写进 `rules[]` / `scans[]`；关键词只作线索，不能单独作为「无冲突」证据。

## 四、载体分流（非规范性指针）

载体处置以 [15-records](../15-records.md) §四 为准；manifest 只写处置与证据。判不清按 L0-7 停。

## 五、重建（规范性）

满足任一条件按新不变量重建受影响面：owner 变了、边界 / 分类变了、旧结构无法一行换一行。重建判定写进 `rebuild`；`old_behaviors[]` 逐条对账，不能静默丢失。

## 六、证据入闸（非规范性指针）

D2 / D3 / D4 与 review 读 manifest + 校验输出；本页不另定完成条件。校验器绿是必要条件，不是语义审核的替代。

## 七、与现有规则的关系

- 不新增 D 类型；完成条件 / 证据 / 载体处置分别由 [10-stages](../10-stages.md)、[20-decisions](../20-decisions.md)、[15-records](../15-records.md) 定义。
- 与「只追加不篡改」「已合并不改正文」不冲突：那些规则管记录 / 基线载体；本协议管未合并草案 / 现行文档的替换。载体表是分界线。
- 与 D3「改旧的」：默认不改；用户明确确认 + D3 记录；勘误限「事实写错且会误导读者」；范围 / 验收变化走新 spec。
- 与 L0-8 同向：新增铁律必须替换 / 合并一条；本协议把同一纪律下沉到 L1-L3。
- 与 v1 [spec-revision-sync](../../spec-revision-sync.md)：v1 任务按该页；v2 任务按本页。

## 八、例子（#190 / #191）

#190 在 5 个文件各加一句「删旧句 + 0 残留」，没有台账；`grep 作废|反向扫描` 只扫新词，反话用旧词写，0 命中。#191 改用 36 行散文台账，但台账写在 PR 正文，行号 / 计数 / 白名单靠人肉对，R1-R3 每轮仍有阻断 / 高。本页改为 manifest + 校验器：结构 / 行号 / 命中 / 覆盖由脚本判，语义冲突由审核判。样本（用户 2026-11-25，外部项目事实，本仓未复核）：旧口径逐条处置 + 表 / registry 对账；关键是每条有处置和证据，不是「扫到 0」。
