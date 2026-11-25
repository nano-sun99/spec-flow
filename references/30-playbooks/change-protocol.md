# Playbook: 替换式变更（manifest + 校验器）

> 本页承载替换式变更的 **manifest schema、双扫描操作与跨项目校验脚本**。
> 触发原则见 [25-spec-governance](../25-spec-governance.md) §四；载体分流见 [15-records](../15-records.md) §四；本页不新增 D 类型。

- **适用**：修改判据、术语、范围、owner、边界或分类（含改变既有行为的新增与退役旧规则）。纯改错字 / 措辞且不改变判定 / 范围 / 默认 / 权限的，不触发。

## 一、工件与跨项目分发

1. **change manifest**：一次变更一个 JSON，默认 `docs/changes/<slug>/manifest.json`（模板见 [docs/changes/README](../../docs/changes/README.md)）。PR 正文只放摘要，不贴长表靠人肉对行号。
2. **校验器（随 skill 分发）**：退出码 0 才算绿；只判机器可查的结构与证据，不代判语义冲突。
   - 本仓调用：`python3 scripts/check-change.py --manifest docs/changes/<slug>/manifest.json --base <base> --head <rev>`
   - 外部项目调用：`python3 <skill>/scripts/check-change.py --root <project> --manifest docs/changes/<slug>/manifest.json --base <base> --head <rev>`
   - 开发 / 审核期（尚未取得合并审批时）：加 `--draft`，跳过 `approval` 完整校验，其余规则、锚点、扫描与章节引用检查照常执行。
   - 外部项目只需自建 `docs/changes/`，无需复制校验器；项目自定义非规则视图在 manifest `view_files[]` 声明；文档不在 `references/` + `docs/` 时在 `scans[].scope` 声明并给 `scope_reason`。
3. **载体表**：以 [15-records](../15-records.md) §四 为准，manifest 只引用处置结果。

## 二、manifest 字段规范

| 段 | 必填 | 内容 |
|---|---|---|
| `change` / `title` / `base` / `head` / `classification` | 是 | 变更标识；`base` / `head` 解析为提交；`classification` ∈ `add` / `replace` / `retire` |
| `approval` | 正式模式是（`--draft` 可缺） | `user_quote` / `timestamp` / `scope` / `base` / `head` / `link`（用户原话与可核链接） |
| `rules[]` | 是 | `id` / `type` / `old`（add 为 null）/ `new`（`file` / `section` / `anchor`）/ `disposition` / `evidence` / `status`；add 另需 `same_trigger_search`（≥6 字） |
| `whitelist[]` | 有白名单时 | `rule_id` / `reason` / `reviewer`（`user` / `review-agent`）/ `review_ref`（链接 / `PR #` / `review:`） |
| `scans[]` | 是 | `query` / `scope` / `hits[]` / `conclusion`；whitelist 命中须含 `reason` / `reviewer` / `review_ref` |
| `semantic_checks[]` | 是 | `item` / `conclusion` / `evidence`（反向冲突逐条结论） |
| `rebuild` | 是 | `triggered`（bool）/ `reason` / `old_behaviors[]`（触发时必填） |
| `non_rule_changes[]` | 有内置视图改动时 | `file` / `reason`（仅允许内置视图文件） |
| `view_files[]` | 项目自定义非规则视图 | `file` / `reason` / `reviewer` / `review_ref`（须在 head 存在） |
| `count_checks[]` | 正文须写数字时 | `name` / `value` / `source` / `command`（source 须存在；command 供人复核，校验器不执行） |
| `section_ref_whitelist[]` | 引用语料外章节号时 | `ref` / `reason` / `reviewer` / `review_ref` |

### 关键约束与 head 钉扎方式（防死循环）

- `disposition` ∈ `replace` / `delete` / `merge` / `alias` / `keep-history` / `keep-scoped` / `not-applicable`；`status` ∈ `done` / `whitelist` / `unresolved`（遇 `unresolved` 即红）。
- `old` 给 `file` + `line` + `text`（≥6 字，按 `base` 核）；`new` 给 `file` + `section` + `anchor`（≥4 字，在 `head` 文件中唯一；同 section 可复用，跨 section 拒绝）。
- **head 钉扎规则**：
  1. 开发与送审期：`head` 与 `approval.head` 可写 `"HEAD"`，配合 `--draft` 校验。
  2. 合并前钉扎：在全部内容提交完成后，将内容提交的完整 SHA 写入 `manifest.head` / `approval.head`（及用户审批链接写入 `approval.link`），单独提交一次 **manifest-only 钉扎提交**。
  3. 运行 `check-change.py --head HEAD` 时，若 `manifest.head` 是 `HEAD` 的祖先且两者之间**仅改动了该 manifest 文件本身**，校验器自动校验通过并报告内容钉扎 SHA；若钉扎后又改动了任何非 manifest 文件，立即报红。

## 三、双扫描、章节与计数检查

1. **活跃残留扫描**：`scans[]` 覆盖 `.md` / `.tsv` / `.txt`（默认 `references/` + `docs/`，收窄写 `scope_reason`），校验器复跑正则，未登记命中即红；零命中不得写 `conclusion=match`。删 / 移章节须扫旧章节号。
2. **章节引用校验**：校验器取 `scans[].scope` 并集作语料；新增 / 改动的 `§X.Y` 须解析到现存 Markdown 标题（数字或中文序号），删 / 改号章节反扫全语料（TSV / TXT 兼查裸章号），语料外引用走 `section_ref_whitelist[]`。
3. **计数单 owner**：行数 / 端点数 / 页数只由 registry / 表 / 脚本输出持有，正文不手抄；确需写数字时登进 `count_checks[]` 并在同一变更更新唯一来源。
4. **反向冲突语义核对**：读同层与相邻层，核五类冲突（同触发不同行为、旧 owner 仍现行、多 owner、验收 / 范围 / 默认不一致、权限 / 载体错配），并对 gate / 字段白名单 / 校验开关等**非决定原则**逐条核单 owner，写进 `semantic_checks[]`。
5. **重建判定**：owner、边界或分类变化，或旧结构无法一行换一行时，触发 `rebuild=true` 并在 `old_behaviors[]` 逐条对账，防止旧行为静默丢失。

## 四、关联闸口（指针）

- 完成条件与入闸证据：[10-stages](../10-stages.md) 设计 / 交付段、[20-decisions](../20-decisions.md) D2 / D3 / D4、[26-review-contract](../26-review-contract.md) §五。
- 载体处置与触发原则：[15-records](../15-records.md) §四、[25-spec-governance](../25-spec-governance.md) §四。
