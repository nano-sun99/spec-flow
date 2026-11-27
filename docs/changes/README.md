# Change manifests（v2 薄声明替换式变更清单）

一次替换式变更一个目录：`docs/changes/<slug>/manifest.json`（必填 `"schema": 2`），PR 正文只放摘要。**完整字段、自动扫 diff 规则与钉扎时序见 [change-protocol](../../references/30-playbooks/change-protocol.md) §二–§三，本页只给最小命令与模板。**

> 历史快照说明：`2026-11-26` 及以前（`2026-11-25-*`、`2026-11-26-*`）的 4 份 manifest 沿用旧版 v1 格式（含已退役的逐行转录与人工清单字段），保留为只读历史快照不重写，不再走现行 v2 校验器。

## 最小用法

```bash
# 开发 / 审核期（允许未提交 manifest 与字面 HEAD，跳过 approval 必填）
python3 scripts/check-change.py \
  --manifest docs/changes/<slug>/manifest.json \
  --base <base-rev> --head HEAD --draft

# 合并前正式校验（须已提交 manifest-only 钉扎提交，禁止字面 HEAD，校验提交树一致）
python3 scripts/check-change.py \
  --manifest docs/changes/<slug>/manifest.json \
  --base <base-rev> --head HEAD
```

外部项目从 skill 路径调用：`python3 <skill>/scripts/check-change.py --root <project> --manifest docs/changes/<slug>/manifest.json --base <base> --head <rev>`（按需设置 `rule_paths` / `rule_exclude`）。退出码 `0` = 通过，`1` = 有违规；语义冲突仍由审核判断。本地预检未提交正式文件可临时加 `--from-disk`，合并门禁禁用。

## v2 模板（正式模式填不可变内容 SHA；`--draft` 期 `head` 可写 `"HEAD"`）

```json
{
  "schema": 2,
  "change": "2026-11-27-example",
  "title": "一句话说明本次替换式变更",
  "base": "<base commit SHA>",
  "head": "<内容提交 SHA>",
  "classification": "replace",
  "rule_paths": ["SKILL.md", "references/"],
  "rule_exclude": ["references/40-cases/", "references/README.md", "references/v2/SKILL.md"],
  "approval": {
    "user_quote": "用户批准改动面的原话",
    "timestamp": "2026-11-27",
    "scope": "批准覆盖的改动面",
    "base": "<base commit SHA>",
    "head": "<内容提交 SHA>",
    "link": "<PR 评论或用户批准记录链接>"
  },
  "rules": [
    {
      "id": "R-001",
      "type": "replace",
      "files": ["references/example.md"],
      "summary": "旧口径替换为新口径并同步关联引用",
      "disposition": "replace",
      "status": "done"
    },
    {
      "id": "R-002",
      "type": "replace",
      "files": ["references/scoped.md"],
      "summary": "保留一处带范围说明的旧条款",
      "disposition": "keep-scoped",
      "status": "whitelist",
      "reason": "说明保留理由",
      "reviewer": "review-agent",
      "review_ref": "PR #200 R1"
    }
  ],
  "scans": [
    {
      "query": "旧术语|已退役字段",
      "allow": [
        {
          "file": "docs/changes/README.md",
          "match": "含命中词的上下文片段",
          "reason": "历史快照说明保留",
          "reviewer": "review-agent",
          "review_ref": "PR #200 R1"
        }
      ]
    },
    {
      "query": "已彻底删除的旧词"
    }
  ],
  "semantic_checks": [
    {
      "item": "旧规则与现行规则是否同触发异行为",
      "conclusion": "changed",
      "evidence": "同层与相邻层核对一致"
    }
  ],
  "section_ref_whitelist": [
    {
      "ref": "§外部章",
      "reason": "引用外部项目文档，不在本仓语料",
      "reviewer": "review-agent",
      "review_ref": "PR #200 R1"
    }
  ],
  "path_ref_whitelist": [
    {
      "file": "docs/changes/README.md",
      "path": "references/deleted-old.md",
      "reason": "历史迁移说明中点名旧路径",
      "reviewer": "review-agent",
      "review_ref": "PR #200 R1"
    }
  ],
  "rebuild": {
    "triggered": false,
    "reason": "",
    "old_behaviors": []
  }
}
```
