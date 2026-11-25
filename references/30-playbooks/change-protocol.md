# Playbook: 替换式变更（manifest + 校验器）

> 本页承载替换式变更的 **manifest schema、双扫描操作与跨项目校验脚本**（§一–§三 为规范性校验口径）。
> 触发原则见 [25-spec-governance](../25-spec-governance.md) §四；载体分流见 [15-records](../15-records.md) §四；本页不新增 D 类型。

- **适用**：修改判据、术语、范围、owner、边界或分类（含改变既有行为的新增与退役旧规则）。纯改错字 / 措辞且不改变判定 / 范围 / 默认 / 权限的，不触发。

## 一、工件与跨项目分发（规范性）

1. **change manifest**：一次变更一个 JSON，默认 `docs/changes/<slug>/manifest.json`（模板见 [docs/changes/README](../../docs/changes/README.md)）。PR 正文只放摘要，不贴长表靠人肉对行号。
2. **校验器（随 skill 分发）**：退出码 0 才算绿；只判机器可查的结构与证据，不代判语义冲突。
   - 正式校验（合入前）：`python3 scripts/check-change.py --manifest docs/changes/<slug>/manifest.json --base <base> --head HEAD`
   - 外部项目调用：`python3 <skill>/scripts/check-change.py --root <project> --manifest docs/changes/<slug>/manifest.json --base <base> --head <rev>`
   - 开发 / 审核期：加 `--draft`，允许本地未提交 manifest 与字面 `"HEAD"`，跳过 `approval` 完整性校验；其余规则、锚点、扫描与章节引用照常执行。
   - 外部项目只需自建 `docs/changes/`，无需复制校验器；非规则视图在 `view_files[]` 声明（须含 `reviewer` / `review_ref`）；文档不在 `references/` + `docs/` 时在 `scans[].scope` 声明并给 `scope_reason`。
3. **载体表**：以 [15-records](../15-records.md) §四 为准，manifest 只引用处置结果。

## 二、manifest 字段与钉扎规范（规范性）

| 段 | 必填 | 内容 |
|---|---|---|
| `change` / `title` / `base` / `head` / `classification` | 是 | 变更标识；`base` / `head` 解析为提交；`classification` ∈ `add` / `replace` / `retire` |
| `approval` | 正式模式是（`--draft` 可缺） | `user_quote` / `timestamp` / `scope` / `base` / `head` / `link`（用户对改动面的批准原话与可核链接） |
| `rules[]` | 是 | `id` / `type` / `old`（add 为 null）/ `new`（`file` / `section` / `anchor`）/ `disposition` / `evidence` / `status`；add 另需 `same_trigger_search` |
| `whitelist[]` | 有白名单时 | `rule_id` / `reason` / `reviewer`（`user` / `review-agent`）/ `review_ref`（`http` / `PR #` / `review:`） |
| `scans[]` | 是 | `query` / `scope` / `hits[]` / `conclusion`；`match` 命中必填 `evidence`；`whitelist` 命中必填 `reason` / `reviewer` / `review_ref` |
| `semantic_checks[]` | 是 | `item` / `conclusion` / `evidence`（反向冲突逐条结论） |
| `rebuild` | 是 | `triggered`（bool）/ `reason` / `old_behaviors[]`（触发时必填） |
| `non_rule_changes[]` | 有内置索引改动时 | `file` / `reason`（仅允许内置纯索引 / 模板 / 单测；规则、SKILL、README 须进 `rules[]` 或 `view_files[]`） |
| `view_files[]` | 项目自定义非规则视图 | `file` / `reason` / `reviewer` / `review_ref`（须在 head 存在） |
| `count_checks[]` | 正文须写数字时 | `name` / `value` / `source` / `command`（source 须存在；command 供人复核，校验器不执行） |
| `section_ref_whitelist[]` | 引用语料外章节号时 | `ref` / `reason` / `reviewer` / `review_ref` |

### 枚举、最小长度与 head 钉扎规则

- **合法枚举**：
  - `type`：`add` / `replace` / `retire`；`retire` 的 `new` 仍须指向 `head` 中承接退役说明、替代规则或归档入口的有效文件、节与唯一锚点。
  - `disposition`：`replace` / `delete` / `merge` / `alias` / `keep-history` / `keep-scoped` / `not-applicable`（`add` 固定为 `not-applicable`）。
  - `status`：`done` / `whitelist` / `unresolved`（遇 `unresolved` 即红）。
  - `conclusion`（`scans[]`、`hits[]`、`semantic_checks[]` 共用）：`match` / `changed` / `whitelist` / `unresolved`（遇 `unresolved` 即红）。
- **最小长度与唯一性**：
  - `old.text` ≥ 6 字（按 `base` 核）；`same_trigger_search` ≥ 6 字；`evidence` ≥ 6 字；`count_checks[].command` ≥ 6 字。
  - `new.anchor` ≥ 4 字且在 `head` 文件中唯一（同 section 可复用，跨 section 拒绝）；`semantic_checks.{item,evidence}` ≥ 4 字；`review_ref` 统一以 `http`、`PR #` 或 `review:` 开头。
- **head 钉扎与防死循环（时序）**：
  1. **开发与审核期**：`head` 可写 `"HEAD"`，配合 `--draft` 校验；无须伪造合并批准。
  2. **合并确认前钉扎**：全部内容提交与审核修订完成后、**摆 D3 / D4 ② 合并卡之前**，将最终内容提交 SHA 写入 `manifest.head` 与 `approval.head`（`approval.link` 指向用户对改动面 / 方案的批准记录），单独提交一次 **`manifest-only` 钉扎提交**。
  3. **正式模式强校验**：拒绝字面 `"HEAD"`，核对 `--head` 提交树内 manifest 与待检文件一致，且要求 `manifest.head` 严格是 `--base` 的后代。
  4. **尾提交放行与豁免**：若 `manifest.head` 到 `HEAD` 之间**仅改动该 manifest 本身**，校验自动通过并输出内容钉扎 SHA，否则报红；该钉扎提交豁免 D3 / D4 重选审核档位（见 [20-decisions](../20-decisions.md) D3 / D4）。

## 三、双扫描、章节与计数检查（规范性）

1. **活跃残留扫描**：`scans[]` 覆盖 `.md` / `.tsv` / `.txt`（默认 `references/` + `docs/`，收窄写 `scope_reason`），校验器复跑正则，未登记命中即红；零命中不得写 `conclusion=match`。删 / 移章节须扫旧章节号。
2. **章节引用校验**：取 `scans[].scope` 并集作语料；新增 / 改动的 `§X.Y` 须解析到现存 Markdown 标题（数字或中文序号），删 / 改号章节反扫全语料（TSV / TXT 兼查裸章号），语料外引用走 `section_ref_whitelist[]`。
3. **计数单 owner**：行数 / 端点数 / 页数只由 registry / 表 / 脚本输出持有，正文不手抄；确需写数字时登进 `count_checks[]` 并在同一变更更新唯一来源。
4. **反向冲突语义核对**：读同层与相邻层，核五类冲突（同触发不同行为、旧 owner 仍现行、多 owner、验收 / 范围 / 默认不一致、权限 / 载体错配），并对 gate / 字段白名单 / 校验开关等**非决定原则**逐条核单 owner，写进 `semantic_checks[]`。
5. **重建判定**：owner、边界或分类变化，或旧结构无法一行换一行时，触发 `rebuild=true` 并在 `old_behaviors[]` 逐条对账，防止旧行为静默丢失。

## 四、关联闸口（指针）

- 完成条件与入闸证据：[10-stages](../10-stages.md) 设计 / 交付段、[20-decisions](../20-decisions.md) D2 / D3 / D4、[26-review-contract](../26-review-contract.md) §五。
- 载体处置与触发原则：[15-records](../15-records.md) §四、[25-spec-governance](../25-spec-governance.md) §四。
