# Change manifests（替换式变更清单）

一次替换式变更一个目录：`docs/changes/<slug>/manifest.json`。manifest 是这次变更的**唯一台账**；PR 正文只放摘要，不再把长表贴在 PR 里靠人肉对行号。**字段定义以 [change-protocol](../../references/v2/30-playbooks/change-protocol.md) §二 为准；本页只给最小模板和命令。**

## 最小用法

```bash
python3 scripts/check-change.py \
  --manifest docs/changes/<slug>/manifest.json \
  --base <base-rev> --head <head-rev>
```

退出码 0 = 结构 / 证据检查通过；1 = 有违规。它只做机器可判的检查，不判断规则语义；语义冲突仍由审核 agent 判断。

## 字段

```json
{
  "change": "replacement-change-manifest",
  "title": "一句话说明这次改什么",
  "base": "<base commit>",
  "head": "<head commit 或 HEAD>",
  "classification": "replace",
  "approval": {
    "user_quote": "用户原话",
    "timestamp": "2026-11-25",
    "scope": "批准覆盖的改动面",
    "base": "<base commit>",
    "head": "<head commit 或 HEAD>",
    "link": "<用户署名确认的 PR 评论链接>"
  },
  "rules": [
    {
      "id": "R-001",
      "type": "replace",
      "old": {"file": "references/v2/example.md", "line": 12, "text": "旧句的关键片段"},
      "new": {"file": "references/v2/example.md", "section": "§四", "anchor": "head 文件里唯一出现的字面片段"},
      "disposition": "keep-scoped",
      "evidence": "diff / scan / 引用链",
      "status": "whitelist"
    },
    {
      "id": "R-002",
      "type": "add",
      "old": null,
      "new": {"file": "references/v2/example.md", "section": "§五", "anchor": "head 文件里可反查的字面片段"},
      "same_trigger_search": "搜了哪些文件 / 词 / 条款；为什么没有同触发旧规则",
      "disposition": "not-applicable",
      "evidence": "diff",
      "status": "done"
    }
  ],
  "whitelist": [
    {"rule_id": "R-001", "reason": "为什么可以保留", "reviewer": "review-agent", "review_ref": "PR # / 轮次"}
  ],
  "scans": [
    {
      "query": "旧词|旧 ID",
      "scope": ["references/", "docs/"],
      "hits": [
        {"file": "references/v2/example.md", "text": "旧词", "conclusion": "whitelist", "reason": "为什么可以留", "reviewer": "review-agent", "review_ref": "<PR 评论链接>"}
      ],
      "conclusion": "whitelist"
    }
  ],
  "semantic_checks": [
    {"item": "旧规则 A 与现行规则 B 是否同触发不同行为", "conclusion": "changed", "evidence": "file:line / diff"}
  ],
  "count_checks": [
    {"name": "registry 行数", "value": 74, "source": "docs/facts/customer-read-endpoint-registry.tsv", "command": "awk -F'\\t' '!/^#/ && $1!=\"id\" && NF' <file> | wc -l"}
  ],
  "view_files": [
    {"file": "docs/facts/example-view.tsv", "reason": "只是 registry 的视图，不是规则", "reviewer": "review-agent", "review_ref": "PR # / 轮次"}
  ],
  "section_ref_whitelist": [
    {"ref": "§外部章", "reason": "引用外部项目文档，不在本仓语料", "reviewer": "review-agent", "review_ref": "PR # / 轮次"}
  ],
  "rebuild": {
    "triggered": false,
    "reason": "",
    "old_behaviors": []
  },
  "non_rule_changes": [
    {"file": "references/v2/README.md", "reason": "只改导航计数，不是规则"}
  ]
}
```

## 规则

- 一行一条规则；`old` 给 `file:line` 与 `text`（≥6 字）；`new` 给 `file` + `section` + `anchor`（head 中唯一，且落在新规则句上）。
- `type` / `disposition` / `status` 的枚举以 [change-protocol](../../references/v2/30-playbooks/change-protocol.md) §二 为准；本页不复述。
- 白名单逐条写 `reason` / `reviewer` / `review_ref`；作者贴标签不能单独成立。
- `scans[]` 的 query 由校验器复跑；未登记的命中即红；whitelist 命中逐条写 `reason` / `reviewer` / `review_ref`。
- `semantic_checks[]` 记反向冲突的语义结论（match / changed / whitelist / unresolved；中文：一致 / 改 / 白名单 / 未处置）；至少一条。
- `count_checks[]` 用于正文必须写数字的场景；`source` 必须在 head 存在，`command` 给复核方式。
- `view_files[]` 用于项目自定义的非规则视图；每条要 reviewer / review_ref，不能拿它盖规则文件。
- `section_ref_whitelist[]` 只用于外部章节引用；本仓语料能解析的引用不要白名单。
- 每个改动文件必须被 `rules[]`、`non_rule_changes[]` 或 `view_files[]` 覆盖；漏一个即红。
- 外部项目从 skill 路径调用：`python3 <skill>/scripts/check-change.py --root <project> --manifest docs/changes/<slug>/manifest.json --base <base> --head <head>`；项目自建 `docs/changes/`，不需要复制校验器。
