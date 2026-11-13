# v1 漂移记录（P0-P6 期间）

- 日期：2026-11-13
- 口径：总纲 §三——P0-P6 期间任何对 v1（根 `SKILL.md`、现有 `references/`、双语文档、脚本、项目指令）的改动都必须记在这里，并在 B1 盘点表重新归类。

## 结论

**无。**

## 核对方式（可复现）

```bash
# 排除 v2 目录本身，只核 v1 文件
git log --oneline 6b447ab..HEAD -- SKILL.md references/ README.md README.zh-CN.md scripts/ AGENTS.md \
  ':(exclude)references/v2'
# 输出为空
```

- 基线 `6b447ab`（`docs: checkpoint staging-line rules before v2 rebuild`）是切 `rebuild/v2` 前最后一次 v1 改动。
- 其后只有 `378c648`（新增 5 份 v2 总纲/批次 spec，全在 `docs/specs/` 下）与 B1 本批新增（`docs/rebuild/`、`references/v2/`）。
- 根 `SKILL.md`、旧 `references/*.md`、`README*.md`、`scripts/` 自 `6b447ab` 起零改动。
- 唯一例外是 B1 按用户批准补做 G4 时对 `AGENTS.md` 第 3 条的修订，已单独记在下方。

## 已知例外

| 文件 | 改动 | 授权 |
|---|---|---|
| `AGENTS.md` 第 3 条 | rationale 冻结为历史档案；R 号只用于铁律变更；新案例进案例库 | 用户 2026-11-13 拍板「B1 补做」（总纲 §十三 开放问题指定的 B1 动作） |

该改动不改变 v1 运行规则（`SKILL.md` 与 `references/` 正文未动），只改维护者约定。

## 重新归类

除上述一行外无新增改动，盘点表 §一 的文件级处置继续有效。
