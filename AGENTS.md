# spec-flow 仓的维护规矩

本仓就是 spec-flow 的唯一真身（本机接线说明见 [docs/maintainer-notes.md](docs/maintainer-notes.md)）。v1 已归档至 `docs/archive/v1/`，不再维护；改 `SKILL.md`、`references/`、`scripts/` 或任一 README 时遵守以下规矩：

1. **仓名只作一次性证据**：不攒成可追加的登记表——外部仓改了自己的规矩没人会回来更新这里。
2. **不维护采用名单**：不登记哪个仓采用了什么选修或禁了哪一档审核；问那个仓自己的指令，不去猜。
3. **案例与铁律分工**：`docs/archive/v1/rationale.md`（R1–R40）冻结为历史档案；新案例写进 `references/40-cases/`（只叙述与提议，不是授权依据）。改动 `references/00-constitution.md`（L0 铁律）必须按 L0-8 经用户批准并在原文件留变更记录。
4. **单一正文与替换式变更**：规则只落在唯一 owner，他处只写指针不复述。修改判据、术语、范围、owner、边界或分类时，按 `references/30-playbooks/change-protocol.md` 提交 manifest 并跑 `scripts/check-change.py`（开发 / 审核期加 `--draft`，合并前钉扎内容 SHA）。
5. **改完必跑文档检查**：执行 `bash scripts/check-docs.sh`，守住核心层字数与行数预算、单行可见字数上限、相对链接与 `#锚点` 可达性，且现行规则不得回指 `docs/archive/`。
6. **双语 README 同批同步**：改 `README.md` 或 `README.zh-CN.md` 必须同步另一份——节标记 `<!-- s:xxx -->` 一一对应、核心参考入口两份均点到，改完跑 `bash scripts/check-docs.sh` 验绿。
