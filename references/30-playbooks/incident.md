# Playbook: 生产应急（热修 hotfix / 回滚 rollback）

> **适用**：仅已采用 `release` 项目；硬闸与不变式见 L0–L2 及 [release playbook](release.md#一发布安全不变式)。

## 一、热修（hotfix）

**适用**：生产确认缺陷且已有至少 1 颗真实生产 tag。

1. **基线与最小修复**：从最近真实生产 tag 开独立 worktree `hotfix/<tag>-<slug>`（**不从 staging / 集成 / 生产 HEAD 切**），只修该缺陷不夹带下一批改动。
2. **临时 tag 验证**：修复提交打临时 tag（如 `v2026.11.03-hotfix.1`），仅从该 tag 构建验证并贴原发布记录。
3. **D4 合回与发版**：按项目形态走 D4 合回开发线（列生产 tag / 修复提交 / 临时 tag / 验证）；不立即打生产 tag，跟下班车走 rc / 批次 / D6；三层验过后补同口径成功快照再 merge 回集成与候选，禁 cherry-pick 断祖先链。继续回填原发布记录。

## 二、回滚（rollback）

**适用**：生产崩溃、监控异常或验收失败。

1. **停住核证（L0-4）**：立即停受影响动作并报事实，**不自动回滚、不静默重试、不改写通过**；收集监控 / 日志 / 失败原文，核上一生产 tag / 快照真实可用且树一致（首次无上一 tag 核部署前快照或原恢复方案）。
2. **D7 确认与执行**：按 [20-decisions](../20-decisions.md) D7 获明确「回滚」后才从目标 tag / 产物重部署并验证端身份与健康；**不删 / 不移失败 tag**，不推进成功快照。
3. **收口**：回滚结果与原因记原发布记录（保持 open 直到收口）；根因另开 bug 单或走 §一 hotfix。

## 三、常见坑与指针

- **坑**：异常自动回滚掩盖现场；删移失败 tag；仅一颗 tag 虚构「回滚上一 tag」；无生产 tag 开 hotfix 或热修夹带需求跳过 D6；三层用 cherry-pick 断链。
- **指针**：D4 / D7 / L0-1 / L0-4（[00-constitution](../00-constitution.md)、[20-decisions](../20-decisions.md)）、[release playbook](release.md#一发布安全不变式)。
