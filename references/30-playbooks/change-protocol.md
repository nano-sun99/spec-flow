# Playbook: 替换式变更（v2 薄声明 + 自动扫 diff）

> §一–§三 规范性唯一正文；触发见 [25-spec-governance](../25-spec-governance.md) §四，载体见 [15-records](../15-records.md) §四。

- **适用**：改 PR `base` 既有判据/术语/范围/owner/边界/分类（含改行为新增、退役旧规则、取代旧 ADR）；纯错字修或纯新增功能/ADR 不触发。

## 一、工件与跨项目分发（规范性）

1. **v2 manifest**：单次一份 `docs/changes/<slug>/manifest.json`（[模板](../../docs/changes/README.md)），必填整型 `"schema": 2`，PR 只放摘要；`2026-11-26` 及以前 v1 作只读历史快照。
2. **校验器（退出码 `0` 绿，不代判语义）**：
   - `python3 scripts/check-change.py --manifest <path> --base <base> --head HEAD`（外部加 `--root <project>` 自建 `docs/changes/`，免复制脚本）
   - `--draft`：开发/审核期（允许未提交与 `"HEAD"`、跳 `approval`）；`--from-disk` 仅本地预检，禁作合并门禁。
3. **载体分流**：按 [15-records](../15-records.md) §四 载体表处置旧→新关系。

## 二、v2 字段、合法枚举与钉扎（规范性）

- **顶层**：`schema: 2`（整型）、`change`/`title`/`base`/`head`/`classification`（`add`/`replace`/`retire`）；正式必填 `approval`（`user_quote`/`timestamp`/`scope`/`base`/`head`/`link`，`base`/`head` 须不可变十六进制 SHA）。
- **范围（可选）**：`rule_paths`（缺省 `["SKILL.md","references/"]`）、`rule_exclude`（排 `40-cases/`、`references/README.md`、`v2/SKILL.md`），恒豁免 manifest；尾 `/` 前缀，余精确匹配。
- **`rules[]`（非空）**：`id`/`type`/`files[]`（须在 diff 禁填 manifest）/`summary`(≥6)/`status`（`done`/`whitelist`/`unresolved`，后者红；`whitelist` 同对象填白名单元数据）；
  - `disposition`：`replace`/`delete`/`merge`/`alias`/`keep-history`/`keep-scoped`/`not-applicable`（`add` 固定末项）。
- **`scans[]`（非空）**：`query`（正则）、`scope`（缺省 `rule_paths+["docs/"]`，未按精确或目录前缀覆盖全 `rule_paths` 须填 `scope_reason`）、`allow[]`（`file`/`match`≥4/白名单元数据/正整数 `count` 默认 1）。
- **`semantic_checks[]` / `rebuild` / 白名单**：
  - `semantic_checks[]`：`item`/`conclusion`（`match`/`changed`/`whitelist`/`unresolved`，禁 `unresolved`）/`evidence`(≥4)；`rebuild.triggered=true` 填 `reason` 与 `old_behaviors[]`。
  - 白名单元数据：`reason` + `reviewer`（`user`/`review-agent`）+ `review_ref`（`https?://...`/`PR #<N>...`/`review:...`）。按需加 `section_ref_whitelist[]`（`{ref,...}`）与 `path_ref_whitelist[]`（`{file,path,...}`，后者过期即红）。
- **自动扫 diff 与钉扎**：自动识 `A/M/T/D` 与 `R*/C*`；变更规则 100% 进 `rules[].files`，非规则配套自动归 `aux_files`（免手写 `view_files[]`）。
  - 审核期 `--draft`（中途触发按 [25-spec-governance](../25-spec-governance.md) §五 当轮起草）；合并前钉 SHA，单交 `manifest-only` 尾提交跑正式绿，豁免重选审核档。

## 三、双扫描、自动反扫与指针（规范性）

1. **活跃残留（`scans[]`）**：扫 `content_head` 文本，默认排除 manifest、`docs/archive/`、`docs/changes/*/`、`references/40-cases/` 与未触及冻结 `docs/specs/`（留 `docs/changes/README.md` 与 PR 草案，显式 `scope` 可取消）。
   - 0 命中且无 `allow` 直绿；有命中须被唯一 1 条 `allow`（字符 span 包含）覆盖，且命中数严格等于 `count`。
2. **三道自动反扫**（同活跃语料，第 3 道含根 `README*.md`）：① 新增断链 `§`（`R*` 配对跳代码块）；② 删/改号章节反扫（去代码块对比扫描）；③ `D`/`R*` 文本旧路径边界与 Markdown 链接（去锚点/查询并解码）反扫。
3. **反向冲突与重建**：核五类冲突（同触发异行为、旧 owner 现行、多 owner、验收/范围/默认不一、权限/载体错配）入 `semantic_checks[]`；owner/边界/分类变设 `rebuild=true` 并核 `old_behaviors[]`。
4. **指针**：[10-stages](../10-stages.md)、[20-decisions](../20-decisions.md) D2–D4、[26-review-contract](../26-review-contract.md) §五、[25-spec-governance](../25-spec-governance.md) §四–§五、[15-records](../15-records.md) §四。
