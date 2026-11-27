# spec-flow 目录导航

- **唯一入口**：[SKILL.md](../SKILL.md)（启动、运行循环、一跳导航、异常协议）。
- **读序**：L0 → L1 → L2 每次必读；专项总纲（`25`/`26`）与 L3 按任务按需读；L4 缺落点或遇异常时查。

## 文件地图

| 层 | 文件 | 唯一职责 | 何时读 |
|---|---|---|---|
| 入口 | [SKILL.md](../SKILL.md) | 启动、运行循环与异常协议 | 每次先读 |
| L0 | [00-constitution.md](00-constitution.md) | 8 条铁律（用户按 L0-8 改，最高优先） | 每次先读；不可逆重读 L0-1 |
| L1 | [10-stages.md](10-stages.md) | 4 段完成、术语（三问 / 竣工回写）与前置 | 每次先读；出段核对 |
| L1 | [15-records.md](15-records.md) | 15 类记录、留痕、4 载体、关单与例外 | 认领 / 交接 / 关单 |
| L2 | [20-decisions.md](20-decisions.md) | D0–D7 硬闸、卡片契约与标签确认 | 每次先读；硬闸对照 |
| 总纲 | [25-spec-governance.md](25-spec-governance.md) | 精简底座 + 3 按需组件与中途升格 | 写 / 改 / 审 spec 或替换 |
| 总纲 | [26-review-contract.md](26-review-contract.md) | 档位、R1–R3、#158、文档检查与 Lane A/B | 派审 / 审核 / 复审 |
| L3 | [30-playbooks/](30-playbooks/) | 9 条走法（标「规范性」为该领域唯一正文） | 按任务选读 |
| L4 | [40-cases/INDEX.md](40-cases/INDEX.md) | 15 条案例（只叙述提议，非授权） | 异常或无落点 |
| 接入 | [50-adapters/README.md](50-adapters/README.md) | 5 选修与只指向式接入契约（自足） | 接入或升级 |

## 每层边界

- **L0 铁律**上限 8 条且最高优先；**L1** 定完成与留证（除 manifest 外不新建台账）；**L2** 定 D0–D7 硬闸（自判细节不进目录）；**专项总纲**（25 / 26）为治理与审核唯一正文。
- **L3 Playbook** 走法非必须顺序，标「规范性」为唯一正文（`release.md` §一、`change-protocol.md` §一–§三），不增 D 类型；**L4 案例**非授权；废弃 v1 归档 `docs/archive/v1/`，`references/v2/SKILL.md` 仅为过渡跳转。
