# v2 P6.5 覆盖审计（18 闸口 + 25 步）

- 日期：2026-11-14
- 依据：总纲 `docs/specs/2026-11-13-spec-flow-v2-master.md` §三 P8 准入 1-2、§十一 B4；批次 spec `docs/specs/2026-11-13-v2-b4-entry.md` §三.3 / §四
- 范围：v1 `references/gate-details.md` §一 的 18 个闸口；drill `docs/specs/2026-11-11-branch-release-flow-drill.md` §一 的 25 步主流程（1-23 + 14a + 14b）
- 口径：每条必须有 v2 运行落点（`references/v2/` 内的 L0 / L1 / L2 / L3 / L4），并给 `file:line` 证据。有意丢弃或降级必须指到 `docs/rebuild/inventory.md` 的 drop / 行为变化条目，并写明替代行为或「本期不保证」；「由 v1 继续」不算 v2 落点。
- 结论：**18/18、25/25 有落点；0 条「无落点」**。其中 1 条有意丢弃（安装卡）、1 条行为变化（入口用户选不再必停）、4 条降级/并入（落点判定、送审、标签、hotfix 合回），均有 inventory 依据与替代行为/本期不保证，见各表「判定」列。

## 一、18 个闸口

来源：`references/gate-details.md` §一 的卡片表（18 行，一行一个决定）。

| # | v1 闸口 | v2 落点（层） | 证据（`file:line`） | 判定 |
|---|---|---|---|---|
| 1 | 新需求入口（直接干 / 开 spec） | L1 澄清段 + L3 `direct` / `new-spec` + D1 | `10-stages.md:37`（入口已判定并报告，用户可按 L0-6 否决）；`10-stages.md:99-101`（入口与跳过）；`direct.md:14-16`；`new-spec.md:14-20` | 落点（行为变化 V1 / D5：不再必停入口卡，agent 判定并报告） |
| 2 | 落点判定（续 issue / 新 issue / 直接干） | L3 `issue` 落点表 + `direct` + L2 说明 | `issue.md:12-23`（落点表）；`direct.md:15`；`20-decisions.md:5`（入口/落点 agent 判，不进目录）；`inventory.md:100`（卡 2 → playbook） | 落点（降为 playbook；落点表标题是「示例非必须」，L1/L2 未写成硬规则——**本期不保证每次执行**） |
| 3 | 缺梳理依赖安装（Yes / No） | L3 `spec` 入口澄清 + `new-spec` v1 差异 | `spec.md:16`（澄清工具为推荐做法，不可用退回手动并记录原因）；`new-spec.md:51`（不设安装卡，不因缺工具阻断）；`inventory.md:101`（卡 3 → 丢弃）、`inventory.md:205`（D4） | 有意丢弃 → 替代行为：推荐做法 + 记录原因，不是「无落点」 |
| 4 | 同一方案（Yes / No） | L2 D2 + L1 设计段 | `20-decisions.md:23-28`（D2 确认 / 改 / 重做）；`10-stages.md:44-56` | 落点（D2） |
| 5 | 页面（有页面 / 无页面） | L2 D1 + L3 `spec` 对照 | `20-decisions.md:19`（D1 证据含页面/无页面）；`new-spec.md:15-17`；`spec.md:18-20` | 落点（D1） |
| 6 | 公共缺口（给口径 / 补充入口） | L0-7 + L3 `spec` 缺口清单 | `00-constitution.md:44-49`（L0-7）；`spec.md:17`（未决问题标出）；`inventory.md:209`（D8） | 落点（并入 L0-7，行为变化 V3） |
| 7 | 拆分（拆 / 不拆） | L2 D1 + L3 `spec` 拆分评估 | `20-decisions.md:16-21`；`spec.md:23-32` | 落点（D1 + playbook） |
| 8 | 同意送审（送审 / 继续完善） | L2 D2 | `20-decisions.md:23-28`（确认 / 改 / 重做 + 审核档位）；`new-spec.md:19`；`review.md:15`；`inventory.md:106`（卡 8 → D2 选项） | 落点（并入 D2，行为变化 V4 / D9） |
| 9 | 当份派审（不审 / 轻审 / 重审 / 重审+变异） | L2 D2 / D4 ① + L3 `review` | `20-decisions.md:27,41`；`review.md:12-28` | 落点（D2/D4 选项） |
| 10 | 按发现修订（全改 / 只改阻断+高 / 不改） | L2 D2 / D4 修订范围 + L3 `review` | `20-decisions.md:27,41`（含砍路径 / 写明本期不保证）；`review.md:24` | 落点（D2/D4 选项） |
| 11 | 观察式例外（纳入 / 不纳入） | L2 D1 子项 + L1 `15-records` §六 | `20-decisions.md:72-74`；`15-records.md:88-102` | 落点 |
| 12 | 改已合并 spec（新开 / 改旧的） | L0-1 + L2 D3 条件分支 + L1 `15-records` | `00-constitution.md:9`；`20-decisions.md:34`；`15-records.md:71`；`spec.md:71` | 落点 |
| 13 | 合并（每份 PR） | L2 D4 ② + L0-5 + L3 `review` | `20-decisions.md:39-42`；`00-constitution.md:32-36`；`review.md:27` | 落点 |
| 14 | 整条 issue 合入 staging | L2 D5 + L1 交付段 + L3 `issue` | `20-decisions.md:44-49`；`10-stages.md:63`；`issue.md:34` | 落点 |
| 15 | 标签转换（转 / 先不转） | L2 标签规则 + L3 `labels` | `20-decisions.md:65-70`（只有待上线/待验证/关单必须确认）；`labels.md:12-35,55-63`；`inventory.md:207,220`（D6 / V2） | 落点（降级为视图；三标签保留确认） |
| 16 | hotfix 合回 staging（合回 / 先不合） | L2 D4（含 hotfix）+ L3 `hotfix` | `20-decisions.md:37-42`；`hotfix.md:39-45`；`inventory.md:114`（卡 16 → D4） | 落点（并入 D4） |
| 17 | 回滚（仅用户批准） | L2 D7 + L3 `rollback` | `20-decisions.md:58-63`；`rollback.md:39-45` | 落点 |
| 18 | 本批发布（发布 / 先不发） | L2 D6 + L3 `release` | `20-decisions.md:51-56`；`release.md:45-53` | 落点 |

## 二、25 步主流程

来源：drill §一 主流程表第 1-23 步，加 14a 合入预演、14b 四类核对。

| 步 | v1 步骤 | v2 落点（层） | 证据（`file:line`） | 判定 |
|---|---|---|---|---|
| 1 | 用户描述需求，澄清 | L3 `spec` 入口澄清 + L1 澄清段证据 | `spec.md:16`；`new-spec.md:14`；`10-stages.md:38`（澄清记录） | 落点（工具推荐非硬依赖；G1 / D4） |
| 2 | 选入口（直接干 / 开 spec） | L1 澄清段 + L3 `direct` / `new-spec` | `10-stages.md:37,99-101`；`direct.md:15`；`new-spec.md:14` | 落点（agent 判定并报告；V1 / D5） |
| 3 | 写 spec | L3 `new-spec` + `spec` 成熟度 | `new-spec.md:15-19`；`spec.md:16-21` | 落点 |
| 4 | 选 spec 审核档位 | L2 D2 + L3 `review` | `20-decisions.md:27`；`review.md:15,17-20` | 落点 |
| 5 | 审核结果 → 选修订范围 | L2 D2 + L3 `review` | `20-decisions.md:27`；`review.md:24` | 落点 |
| 6 | spec 合并确认 | L2 D3 + L3 `new-spec` | `20-decisions.md:30-35`；`new-spec.md:19` | 落点 |
| 7 | 开执行 issue，写交接 | L1 `15-records` + L3 `new-spec` | `15-records.md:11-21,45-58`（获批依据、预期交付、原任务字段等）；`new-spec.md:19` | 落点 |
| 8 | **停**：等实施委托 | L2 D0 + L1 设计段出口 | `20-decisions.md:9-14`；`10-stages.md:55`；`new-spec.md:20` | 落点 |
| 9 | 记实施委托，认领 worktree | L1 `15-records` §二 + L3 `worktree` / `issue` | `15-records.md:25-43`；`worktree.md:14-16`；`issue.md:26-30` | 落点 |
| 10 | 实施完成，开实施 PR | L1 交付段 + L3 `issue` | `10-stages.md:58-70`；`issue.md:31` | 落点 |
| 11 | 选实施 PR 审核档位 | L2 D4 ① + L3 `review` | `20-decisions.md:39`；`review.md:15` | 落点 |
| 12 | 审核结果 → 选修订范围 | L2 D4 ① + L3 `review` | `20-decisions.md:41`；`review.md:24` | 落点 |
| 13 | 实施 PR 合并确认 | L2 D4 ② + L3 `review` | `20-decisions.md:41`；`review.md:27` | 落点 |
| 14 | issue 分支测试 | L1 交付段 + L3 `issue` / `labels` | `10-stages.md:62`；`issue.md:32`；`labels.md:20-22` | 落点 |
| 14a | 合入预演（staging 线） | L1 术语 / 交付段 + L3 `issue` + L1 `15-records` | `10-stages.md:14,63`；`issue.md:33`；`15-records.md:18` | 落点 |
| 14b | 四类核对 | L1 交付段 + L1 `15-records` + L3 `issue` | `10-stages.md:62`；`15-records.md:19`；`issue.md:32` | 落点 |
| 15 | 整条合入 staging 闸口 | L2 D5 + L3 `issue` | `20-decisions.md:44-49`；`issue.md:34` | 落点 |
| 16 | 合入 + 标签 | L3 `issue` / `labels` + L2 标签规则 | `issue.md:34`；`labels.md:22`；`20-decisions.md:65-70` | 落点（待上线需确认） |
| 17 | 批次测试 | L1 发布段 + L3 `release` / `batch-fix` | `10-stages.md:15,76`；`release.md:16`；`batch-fix.md:14-20` | 落点 |
| 18 | rc 标签 | L1 术语 / 发布段 + L3 `release` | `10-stages.md:16,77`；`release.md:17` | 落点 |
| 19 | rc 验收测试 | L1 术语 / 发布段 + L3 `release` | `10-stages.md:16,77`；`release.md:18` | 落点 |
| 20 | 最终标签 | L1 发布段 + L3 `release` | `10-stages.md:80`；`release.md:20` | 落点 |
| 21 | 生产发布批准 | L2 D6 + L3 `release` | `20-decisions.md:51-56`；`release.md:19` | 落点 |
| 22 | 部署 + 监控 | L3 `release` + L0-4 + L1 发布段 | `release.md:21`；`00-constitution.md:26-30`；`10-stages.md:17,79` | 落点 |
| 23 | 收尾（main 快进、关单、清分支、发布记录） | L3 `release` / `main-snapshot` / `worktree` / `labels` + L1 `15-records` §五 | `release.md:22`；`main-snapshot.md:14-19`；`15-records.md:75-86`；`worktree.md:19`；`labels.md:55-63` | 落点 |

## 三、drill 直接干旁支（7 步）

drill §一「直接干路径」是主流程旁支，不在 25 步内；同样有 v2 落点：

| 旧步骤 | v2 落点 | 证据 |
|---|---|---|
| 1-2 选直接干、切 `task/<slug>` | L3 `direct` + L3 `worktree` | `direct.md:14-16`；`worktree.md:16,35-44` |
| 3-4 改动测试、PR 先不合、部署 PR 分支验收 | L1 交付段 + L3 `direct` | `10-stages.md:64`；`direct.md:17-18` |
| 5 合并闸单独确认 | L2 D4 ② + L3 `direct` | `20-decisions.md:39-42`；`direct.md:19` |
| 6 发布记录手工列直接干任务 | L1 `15-records` + L3 `direct` | `15-records.md:58`；`direct.md:20` |
| 7 批次失败切 `fix/<slug>` | L3 `batch-fix` | `batch-fix.md:16` |

## 四、审计边界与不自欺

- **不把 v1 继续适用算落点**：项目接入动作仍以 v1 `references/apply-to-project.md` 为准，这是 `50-adapters/README.md:3,22-29` 的明确设计（只指向式、不改 adopt 行为），不属于 18 闸口 / 25 步的运行路径，因此未计为覆盖缺口。
- **有意丢弃不算无落点**：安装卡（卡 3）与入口用户选择（卡 1）在 `inventory.md` 的 drop 列表（D4、D5）有理由与「砍掉后不保证什么」，替代行为分别落在 `spec.md:16` 和 `10-stages.md:37`。
- **check-docs 绿不是充分条件**：本审计与 3 个剧本回放是 P8 准入 1-2 的额外证据；`check-docs.sh` 只核 v1 结构，不能替代本文件。
- **证据可核**：`file:line` 以 v2 运行文件（`references/v2/`）为主；`inventory.md`、drill、`gate-details.md` 只作处置来源与计数来源，不是运行落点。所有引用均落在现存文件有效行；v2 内部链接见 §五。
- **L0 过期条件**：`00-constitution.md:23,48` 仍写「阶段合同未交付前」「L3/L4 未交付时」，B2/B3 交付后这些条件不再触发。按 L0-8，本批不改铁律；留待用户单独批准清理。

## 五、v2 链接检查（一次性命令）

仓内 `scripts/check-docs.sh` 只核 v1 顶层 `references/*.md`，不覆盖 `references/v2/`；按总纲「不引入新工具 / CI / 脚本」的边界，B4 用一次性命令检查并在 PR 记录结果：

```bash
python3 - <<'PY'
import os, re
bad = []; n = 0
for dp, _, fs in os.walk("references/v2"):
    for fn in fs:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(dp, fn)
        for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", open(p, encoding="utf-8").read()):
            t = m.group(1).split("#")[0]
            if not t or t.startswith(("http", "mailto")):
                continue
            n += 1
            if not os.path.exists(os.path.normpath(os.path.join(dp, t))):
                bad.append(p + ": " + t)
print(n, len(bad)); print("\n".join(bad))
PY
```

结果（2026-11-14，提交 `fe8be6d`）：检查 148 条 v2 内部相对链接，0 断；入口 `SKILL.md` 直链 4 个核心文件、13 条 playbook、15 条案例、INDEX 与 50-adapters。

## 六、P8 准入（只登记，不执行）

P8 准入标准见总纲 §三：① 覆盖审计通过（18 闸口 + 25 步无「无落点」）；② 3 个剧本回放通过且用户确认次数 ≤v1；③ v2 内部链接全部可达 + `check-docs.sh` 绿 + v2 专用链接检查绿；④ 用户明确批准切换 + legacy 迁移清单就绪。

本批 B4 只交付并验证 ①②③；④ 不在本期，**未执行切换**，根 `SKILL.md` 未动。
