# Change manifests（替换式变更清单）

一次替换式变更一个目录：`docs/changes/<slug>/manifest.json`。manifest 是这次变更的**唯一台账**；PR 正文只放摘要。**完整字段规范与钉扎规则见 [change-protocol](../../references/30-playbooks/change-protocol.md) §二，本页只给最小命令与模板。**

## 最小用法

```bash
# 开发 / 审核期（尚未取得合并批准时加 --draft）
python3 scripts/check-change.py \
  --manifest docs/changes/<slug>/manifest.json \
  --base <base-rev> --head HEAD --draft

# 合并前（钉扎内容提交 SHA 后，即使单独提交 manifest 钉扎提交也支持 --head HEAD）
python3 scripts/check-change.py \
  --manifest docs/changes/<slug>/manifest.json \
  --base <base-rev> --head HEAD
```

外部项目从 skill 路径调用：`python3 <skill>/scripts/check-change.py --root <project> --manifest docs/changes/<slug>/manifest.json --base <base> --head <head>`。退出码 0 = 通过，1 = 有违规；语义冲突仍由审核判断。

## 模板

```json
{
  "change": "example-change",
  "title": "一句话说明这次改什么",
  "base": "<base commit>",
  "head": "<内容提交 SHA 或 HEAD>",
  "classification": "replace",
  "approval": {
    "user_quote": "用户原话",
    "timestamp": "2026-11-25",
    "scope": "批准覆盖的改动面",
    "base": "<base commit>",
    "head": "<内容提交 SHA 或 HEAD>",
    "link": "<用户署名确认的 PR 评论链接>"
  },
  "rules": [
    {
      "id": "R-001",
      "type": "replace",
      "old": {"file": "references/example.md", "line": 12, "text": "旧句的关键片段"},
      "new": {"file": "references/example.md", "section": "§四", "anchor": "head 文件里唯一出现的字面片段"},
      "disposition": "keep-scoped",
      "evidence": "diff / scan / 引用链",
      "status": "whitelist"
    },
    {
      "id": "R-002",
      "type": "add",
      "old": null,
      "new": {"file": "references/example.md", "section": "§五", "anchor": "head 文件里可反查的字面片段"},
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
        {"file": "references/example.md", "text": "旧词", "conclusion": "whitelist", "reason": "为什么可以留", "reviewer": "review-agent", "review_ref": "<PR 评论链接>"}
      ],
      "conclusion": "whitelist"
    }
  ],
  "semantic_checks": [
    {"item": "旧规则 A 与现行规则 B 是否同触发不同行为", "conclusion": "changed", "evidence": "file:line / diff"}
  ],
  "count_checks": [
    {"name": "registry 行数", "value": 74, "source": "docs/facts/registry.tsv", "command": "awk -F'\\t' '!/^#/ && $1!=\"id\" && NF' <file> | wc -l"}
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
    {"file": "references/README.md", "reason": "只改导航计数，不是规则"}
  ]
}
```
