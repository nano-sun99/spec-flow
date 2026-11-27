# Playbook: 替换式变更（v2 薄声明 + 自动扫 diff）

> §一–§三 为规范性唯一正文；触发见 [25-spec-governance](../25-spec-governance.md) §四，载体分流见 [15-records](../15-records.md) §四；不增 D 类型。

- **适用**：改 PR `base` 既有判据 / 术语 / 范围 / owner / 边界 / 分类（含改行为新增、退役旧规则、取代旧 ADR）。纯改错字不改判定 / 范围 / 默认 / 权限，或纯新增功能 / 纯新增 ADR 不触发。

## 一、工件与跨项目分发（规范性）

1. **v2 manifest**：每次变更一份 `docs/changes/<slug>/manifest.json`（模板见 [docs/changes/README](../../docs/changes/README.md)），必填 `"schema": 2`；PR 正文只放摘要。`2026-11-26` 前旧 v1 manifest 作历史快照，不走现行校验器。
2. **校验器（随 skill 分发）**：退出码 `0` = 绿；只判结构、覆盖与残留，不代判语义冲突。
   - 正式：`python3 scripts/check-change.py --manifest docs/changes/<slug>/manifest.json --base <base> --head HEAD`
   - 外部：`python3 <skill>/scripts/check-change.py --root <project> --manifest docs/changes/<slug>/manifest.json --base <base> --head <rev>`（自建 `docs/changes/`，按需配 `rule_paths`/`rule_exclude`，免复制脚本）
   - `--draft`：开发 / 审核期（允许未提交与 `"HEAD"`、跳过 `approval`）；`--from-disk` 仅本地预检，禁作合并门禁。
3. **载体分流**：按 [15-records](../15-records.md) §四 载体表处置旧→新关系。

## 二、v2 薄声明字段、自动扫 diff 与钉扎（规范性）

- **顶层必填**：`schema: 2`（拒 `bool`）、`change`、`title`、`base`、`head`、`classification`（`add`/`replace`/`retire`）；正式模式另必填 `approval`（`user_quote`/`timestamp`/`scope`/`base`/`head`/`link`，`base`/`head` 须不可变十六进制 SHA）。
- **规则范围（可选）**：`rule_paths`（缺省 `["SKILL.md","references/"]`）、`rule_exclude`（缺省排 `40-cases/`、`references/README.md`、`v2/SKILL.md`），恒豁免 manifest 自身；尾 `/` 前缀匹配，余精确匹配。
- **`rules[]`（非空）**：`id`、`type`、`files[]`（须在 diff 中且禁填 manifest）、`summary`（≥6）、`disposition`（7 值，`add` 固定 `not-applicable`）、`status`（`done`/`whitelist`/`unresolved`，`whitelist` 同对象填 `reason`/`reviewer`/`review_ref`）。
- **`scans[]`（非空）**：`query`（正则）、可选 `scope`（缺省 `rule_paths+["docs/"]`，未按目录前缀覆盖全部 `rule_paths` 须填 `scope_reason`）、可选 `allow[]`（`file`/`match`≥4/`reason`/`reviewer`/`review_ref`/正整数 `count` 默认 1）。
- **`semantic_checks[]` 与 `rebuild`**：`item`/`conclusion`（禁 `unresolved`）/`evidence`（≥4）；`rebuild.triggered=true` 须填 `reason` 与非空 `old_behaviors[]`。
  - 白名单（按需）：`section_ref_whitelist[]`（`{ref,...}`）与 `path_ref_whitelist[]`（`{file,path,...}`，均验 `reason`/`reviewer`/`review_ref`，过期即红）。
- **自动扫 diff 与钉扎**：自动识别 `A/M/T/D` 与 `R*/C*`；变更规则须 100% 进 `rules[].files`，非规则配套自动归 `aux_files`（免手写 `view_files[]`）。
  - 审核期跑 `--draft`（中途触发按 [25-spec-governance](../25-spec-governance.md) §五 当轮起草）；合并前钉内容 SHA，单交 `manifest-only` 尾提交跑正式绿，豁免重选审核档位。

## 三、双扫描、三道自动反扫与关联闸口（规范性）

1. **活跃残留（`scans[]`）**：扫 `content_head` 文本，默认排除 manifest、`docs/archive/`、`docs/changes/*/`、`references/40-cases/` 与未触及冻结 `docs/specs/`（保留 `docs/changes/README.md` 与 PR 草案，显式 `scope` 可取消）。
   - 0 命中且无 `allow` 直绿；有命中须以字符区间包含且唯一 1 条 `allow` 覆盖，次数严格等于 `count`。
2. **三道自动反扫**：同口径活跃语料（第 3 道含根 `README*.md`）——① 新增断链 `§`（`R*` 配对、跳代码块）；② 删 / 改号章节反扫（去代码块对比与扫描）；③ `D`/`R*` 文本旧路径字面边界与 Markdown 链接（去锚点 / 查询并解码）反扫。
3. **反向冲突与重建**：核五类冲突（同触发异行为、旧 owner 仍现行、多 owner、验收/范围/默认不一致、权限/载体错配）写入 `semantic_checks[]`；owner / 边界 / 分类变触发 `rebuild=true` 并逐条核 `old_behaviors[]`。
4. **指针**：[10-stages](../10-stages.md) 设计/交付、[20-decisions](../20-decisions.md) D2–D4、[26-review-contract](../26-review-contract.md) §五、[25-spec-governance](../25-spec-governance.md) §四–§五、[15-records](../15-records.md) §四。
