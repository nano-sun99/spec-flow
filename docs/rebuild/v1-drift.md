# v1 漂移记录（P0-P6 期间）

- 日期：2026-11-13
- 口径：总纲 §三——P0-P6 期间任何对 v1（根 `SKILL.md`、现有 `references/`、双语文档）的改动都必须记在这里，并在 B1 盘点表重新归类。

## 结论

**无。**

## 核对方式（可复现）

```bash
git log --oneline 6b447ab..HEAD -- SKILL.md references/ README.md README.zh-CN.md scripts/
# 输出为空
```

- 基线 `6b447ab`（`docs: checkpoint staging-line rules before v2 rebuild`）是切 `rebuild/v2` 前最后一次 v1 改动。
- 其后只有 `378c648`（新增 5 份 v2 总纲/批次 spec，全在 `docs/specs/` 下）与 B1 本批新增（`docs/rebuild/`、`references/v2/`）。
- 根 `SKILL.md`、旧 `references/*.md`、`README*.md`、`scripts/` 自 `6b447ab` 起零改动。

## 重新归类

无新增改动，盘点表 §一 的文件级处置继续有效，无需回填。
