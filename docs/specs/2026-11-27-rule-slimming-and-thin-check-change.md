# 规格：迭代 3 — 借 Eval 砍重负（全仓字数硬闸、全域规则瘦身与 `check-change.py` v2 薄声明重构）

- **日期**：2026-11-27
- **状态**：Draft（待 D2 审核与确认）
- **目标分支**：`rebuild/v2`（当前基线 `4399980229cee154d1bc704f95e9361f9e31a190`）
- **形态**：无页面（纯文档规范、检查脚本与测试）；**不拆**（单 spec、单执行单）
- **治理组件判定**（按 [25-spec-governance](../../references/25-spec-governance.md)）：
  - **精简底座**：启用（4 列简版决定表 + 反熵增三问终稿 + 常规验收与改动文件表）。
  - **组件 1（跨切面范围盘点表）**：不适用（本需求不涉及多入口 / 多角色分层权控）。
  - **组件 2（多文档 / ADR / 派生视图治理）**：不适用（单文档 spec，无新增 / 取代 ADR，无按范围展开的派生视图）。
  - **组件 3（替换式变更 manifest）**：本 spec PR 不适用（仅新增本规格文件，未修改 `rebuild/v2` 既有规则正文）；**后续实施 PR 触发组件 3**，并直接作为首份实战用例使用本规格定义的 v2 薄声明 manifest 通过正式门禁。

---

## 一、简版决定表（精简底座）

| ID | 决定（一句话） | 来源（用户原话/日期） | 状态 |
|---|---|---|---|
| `SL-1` | 采用**激进全域瘦身**：压缩 `SKILL.md`、`references/{10,15,20,25,26,README}.md`、全部 9 条 playbook 与 `50-adapters/README.md`（共 17 份），目标全仓现行规则 `≤ 46,000` 字、必读核 `≤ 15,500` 字 | 用户 2026-11-27 拍板「激进全域瘦身…目标全仓 ≤ 46,000 字」及 D1 确认 | 已拍板 |
| `SL-2` | `scripts/check-docs.sh` 新增**必读核（`≤ 15,500`）与全仓现行规则总字数（`≤ 46,000`）硬上限**（与 `run-eval.py` 同口径），并收紧 `SKILL.md` 与 `CORE_BUDGETS` 单文件上限 | 用户 2026-11-27 D1 确认 | 已拍板 |
| `SL-3` | `scripts/check-change.py` 采用**纯 v2 薄声明替换**（`schema: 2` + `git -c diff.renames=true diff --name-status -M -z` 自动扫描），不保留 v1 双轨分支；历史 4 份 v1 manifest 标为历史快照不动，`test-check-change.py` 迁移为 v2 全套正负例 | 用户 2026-11-27 拍板「纯 v2 薄声明替换（最反熵增）」及 D1 确认 | 已拍板 |
| `SL-4` | **严格冻结现有 14 条 Eval 尺子不变**（不动 `evals/scenarios/*.json`、`scripts/run-eval.py`、`scripts/test-run-eval.py`，Iter 2 R3 遗留 `R3-M1`/`R3-M2` 留后），以同一把尺子验证瘦身后 `14/14 pass`、`0` 退化并落地 `evals/baselines/2026-11-27-iter3-slim.{json,md}` | 用户 2026-11-27 拍板「严格冻结现有 14 条 Eval 尺子不变」及 D1 确认 | 已拍板 |
| `SL-5` | 守住保护边界：不动 `references/00-constitution.md`（L0-8）、`references/v2/SKILL.md`、历史 v1 manifest、已冻结 spec 与 `docs/archive/`；保持全部 Eval `rules_ref` 锚点与 `check-docs.sh` 核心 owner 标记不破 | L0-8、AGENTS.md #3/#5 与 D1 确认（2026-11-27） | 已拍板 |
| `SL-6` | 单 spec 不拆，后续实施 PR 完成全部 4 项交付并在 `D4 ②` 前同步 `README.md` / `README.zh-CN.md` 与脱敏基线，不推送远端、不删除既有分支 / worktree | 用户 2026-11-27 D1 确认、L0-1 | 已拍板 |

---

## 二、背景、目标与非目标

### 背景与量化基线（`rebuild/v2` @ `4399980`）

迭代 1 已建立 12 条 CLI 无关行为级 Eval，迭代 2 引入「单一精简底座 + 3 按需治理组件 + 反熵增三问 + 竣工回写」并扩至 14 条场景（[2026-11-26-iter2-anti-entropy.md](../../evals/baselines/2026-11-26-iter2-anti-entropy.md)：`14/14 pass`）。当前暴露三处结构性熵增：

1. **缺乏全仓字数硬闸**：[scripts/check-docs.sh](../../scripts/check-docs.sh) 仅设单文件宽松预算（`CORE_BUDGETS` 6 份上限之和达 `33,500` 字），未对必读核 `always_read_chars`（现 `17,503` 字）及全仓现行规则 `total_rule_chars`（现 `58,382` 字，19 份）设硬上限，`50-adapters/README.md`（`6,436` 字）与 `change-protocol.md`（`4,921` 字）完全无字数约束。
2. **现行规则跨层复述显著**：`26-review-contract.md`（`6,769` 字）§六 Lane A 模板逐条复述 §二/§四.2/§五.2；`50-adapters/README.md`（`6,436` 字）5 份选修短入口模板高度重复；`15-records.md`（`4,438` 字）、`25-spec-governance.md`（`5,383` 字）与 9 条 playbook 多处重复 `10-stages.md` / `20-decisions.md` 正文。
3. **`check-change.py` 维护税过高**：现 `809` 行脚本要求人工手抄脆弱的 `old.line` / `old.text` / `new.section` / `new.anchor` / `same_trigger_search` / `evidence`，且强制为每个 README / Eval / 测试改动逐条填 `view_files[]`（重复填 `reviewer` / `review_ref`）并维护硬编码 `NON_RULE_ALLOW`；同时缺少 `--find-renames` 重命名识别与已删 / 改名路径残留自动反扫。

### 目标与非目标

- **目标**：在严格冻结 14 条 Eval 尺子证明零行为退化的前提下，完成 S1 全仓字数硬闸、S2 17 份现行规则激进瘦身、S3 `check-change.py` 纯 v2 重构与文档同步、S4 14 路全量 Eval 验收与双语 README 同步。
- **非目标**：不改 L0（`references/00-constitution.md`）；不改任何 Eval 场景、Runner 或单测；不改写 4 份历史 v1 manifest、已冻结 spec 或 `docs/archive/`；不推送远端、不删本地分支或 worktree。

---

## 三、反熵增三问终稿

1. **已有重叠盘点**：
   - `references/26-review-contract.md`（`6,769` 字）：§六 Lane A 模板与 §二（轮次）、§四.2（文档组织前置检查）、§五.2（四段正文 / 7 类处置 / 必填字段）大段重复。
   - `references/50-adapters/README.md`（`6,436` 字）：§三.1–§三.3 反复拷贝 5 份几乎同构的 `AGENTS.md` 选修短入口模板，且与 `labels.md` / `adr.md` / `15-records.md` / `release.md` 重复解释采纳后常规动作。
   - `references/15-records.md`（`4,438` 字）、`references/25-spec-governance.md`（`5,383` 字）、`references/10-stages.md`（`4,622` 字）、`references/20-decisions.md`（`3,687` 字）及 `references/30-playbooks/*.md`（9 份共 `20,236` 字）：多处跨文件复述阶段完成条件、D0–D7 触发条件、审核边界与收尾规则，而非单点指针引用。
   - `scripts/check-change.py`（`809` 行）+ `references/30-playbooks/change-protocol.md`（`4,921` 字）：人工转录 `old.line`/`old.text`/`new.anchor` 与 `git diff` 事实重复；`view_files[]` / `non_rule_changes[]` / `NON_RULE_ALLOW` / `count_checks[]` 与 Git diff 和独立脚本计数重复。
2. **减法清单**：
   - **脚本与协议减法**：从 `scripts/check-change.py` 彻底移除 v1 校验逻辑与 `old.line` / `old.text` / `new.section` / `new.anchor` / `same_trigger_search` / `evidence` / 顶层 `whitelist[]` / `view_files[]` / `non_rule_changes[]` / `NON_RULE_ALLOW` / `count_checks[]` 字段校验（代码量预计由 `809` 行降至 `~400–480` 行）；同步重写 `references/30-playbooks/change-protocol.md`（由 `4,921` 字砍至 `≤ 2,400` 字）与 `docs/changes/README.md`。
   - **规则正文减法**：17 份非 L0 现行规则全面去重压缩——`always_read_chars` 由 `17,503` 压至 `≤ 15,500`（净减 `≥ 2,003` 字），`total_rule_chars` 由 `58,382` 压至 `≤ 46,000`（净减 `≥ 12,382` 字，降幅 `≥ 21%`）。
   - **预算余量减法**：`scripts/check-docs.sh` 收紧 `SKILL.md` 正文上限（`3,200 → 2,600` 字、`70 → 60` 行）与 `CORE_BUDGETS` 5 份非 L0 文件上限，并锁死必读核与全仓总字数上限。
3. **现状真身落点**：
   - 现行规则唯一正文真身：`SKILL.md` 与 `references/{10,15,20,25,26,README}.md`、`references/30-playbooks/*.md`、`references/50-adapters/README.md`。
   - 文档字数与链接检查真身：`scripts/check-docs.sh`。
   - 替换式变更协议与校验器真身：`scripts/check-change.py`、`scripts/test-check-change.py`、`references/30-playbooks/change-protocol.md`、`docs/changes/README.md`。
   - 行为基线与对外视图：`evals/baselines/2026-11-27-iter3-slim.{json,md}`、`README.md`、`README.zh-CN.md`。

---

## 四、技术方案与精确契约

### 1. S1：`scripts/check-docs.sh` 全仓字数硬闸与收紧预算

与 [scripts/run-eval.py](../../scripts/run-eval.py) 保持严格同口径，防止两处数字口径漂移：

- **必读核（`always_read_chars`）**：`len(SKILL.md 去 frontmatter 正文) + sum(len(f) for f in {00-constitution, 10-stages, 15-records, 20-decisions})`；新增独立 `[绿]/[红]` 断言，硬上限 **`15,500` 字**。
- **全仓现行规则总字数（`total_rule_chars`）**：`len(SKILL.md 全文) + sum(len(f) for f in sorted(references/**/*.md 排除 references/40-cases/**))`（即 `active_rule_files` 全部字符之和）；新增独立 `[绿]/[红]` 断言，硬上限 **`46,000` 字**。
- **单文件预算收紧**：

| 文件 | 原上限（行 / 字） | 新上限（行 / 字） | 说明 |
|---|---:|---:|---|
| `SKILL.md`（全文件行数 / 去 frontmatter 正文字数） | `70 / 3,200` | `60 / 2,600` | 沿用 `check-docs.sh` 整文件 `len(lines) ≤ 60` 与去 frontmatter `len(body) ≤ 2,600`；frontmatter `≤ 500`、警示符 `≤ 3` 不变 |
| `references/00-constitution.md` | `62 / 2,800` | `62 / 2,800` | L0 不动 |
| `references/10-stages.md` | `120 / 5,500` | `95 / 4,200` | 收紧 |
| `references/15-records.md` | `140 / 6,200` | `95 / 3,800` | 重点瘦身对象 |
| `references/20-decisions.md` | `115 / 5,200` | `85 / 3,400` | 收紧 |
| `references/25-spec-governance.md` | `130 / 6,000` | `100 / 4,500` | 收紧 |
| `references/26-review-contract.md` | `165 / 7,800` | `110 / 4,800` | 重点瘦身对象 |

- 既有检查项（单行可见长度 `≤ 220`、精确 GitHub `#锚点`、零 `docs/archive` 外链、核心 owner 标记与全目录孤儿检查、双语 README 节标记与核心入口同步）全部保留；最终结果行仍输出 `绿`（退出码 `0`）或 `红`（退出码 `1`）。

### 2. S2：激进全域规则瘦身方案与硬不变量

#### 不可破坏的结构不变量（瘦身硬底线）

1. **所有 14 份冻结 Eval 的 `rules_ref` 标题锚点 100% 保持精确可达**（`python3 scripts/run-eval.py --validate` 校验）：
   - `SKILL.md`：`#spec-flow`、`#运行循环`、`#异常协议与重读`
   - `references/10-stages.md`：`#二四段合同`、`#三交付前置条件`（及 `### 澄清/设计/交付/发布`）
   - `references/15-records.md`：`#五关单收尾`
   - `references/20-decisions.md`：`#d0-实施委托`、`#d1-范围与结构开-spec-适用直接干不走-d1`、`#d3-spec-合并`、`#d4-每份-pr含直接干与-hotfix-合回`、`#d7-回滚`
   - `references/25-spec-governance.md`：`#一单一决定正文与唯一活动-id`、`#四草案替换重开边界与替换式变更`
   - `references/26-review-contract.md`：`#二轮次与范围检查`、`#三严重度与-158-五机制`
   - `references/30-playbooks/change-protocol.md`：`#一工件与跨项目分发规范性`
   - `references/30-playbooks/direct.md`：`#一参考走法`
   - `references/30-playbooks/issue.md`：`#二参考走法`
   - `references/50-adapters/README.md`：`#一只读检查与拟稿边界`
2. **`check-docs.sh` §4 核心 owner 必需标记与仓内跨文件 `#锚点` 全部保持存在**（包括 `release.md#一发布安全不变式`、`release.md#三批次测试失败修复fix`、`20-decisions.md#交互卡片契约`、`20-decisions.md#标签确认与观察式例外`、`15-records.md` 7 项核心词条等）。
3. **语义零丢失**：不删减任何硬闸触发/失效条件、D0 同窗口闭集/8 字段、L0 约束指针、#158 五机制与 R1–R3 上限、精简底座 + 3 组件 + 平滑升级、反熵增三问 + 竣工回写、选修默认关闭 + 5 项可执行资产升级闸、`待验收` 防重名与 `gh label` 8+8 定义。

#### 逐文件压缩目标与主要手法

| 文件 | 现状（字） | 目标（字） | 主要瘦身手法（只去重复与赘词，不丢规则） |
|---|---:|---:|---|
| `SKILL.md` | 2,552 (正文 2,430) | ≤ 2,240 (正文 ≤ 2,118) | 精简运行循环与异常协议赘词；保外部技能禁用、4 行路由表、一跳导航 |
| `00-constitution.md` | 2,326 | 2,326（不动） | L0-8 冻结保护 |
| `10-stages.md` | 4,622 | ≤ 3,900 | 精炼术语表与四段完成/证据清单；去与 `25`/`26` 重复修饰语 |
| `15-records.md` | 4,438 | ≤ 3,450 | 合并紧凑表达 11+4 表与 D0 8 字段、精炼 §三–§七，保全部 15 类与载体表 |
| `20-decisions.md` | 3,687 | ≤ 3,100 | 提炼 D0–D7 共性表达，精简冗长括注，保全部触发/证据/默认/失效与卡片模板 |
| `25-spec-governance.md` | 5,383 | ≤ 4,200 | 消除导言与 §一–§五重复定义，收紧底座 / 3 组件 / 平滑升级措辞 |
| `26-review-contract.md` | 6,769 | ≤ 4,400 | 重头戏：§六 Lane A 改为紧凑契约，引用本页 §二/§四.2/§五.2 而不逐句重抄；精炼 §一–§五 |
| `30-playbooks/change-protocol.md` | 4,921 | ≤ 2,400 | 随 v2 薄声明重构，删除 v1 繁琐字段表与旧规范，仅留 v2 字段、自动扫描与钉扎时序 |
| `30-playbooks/` 其余 8 份 | 15,315 | ≤ 11,600 | 去与 `10-stages`/`15-records`/`20-decisions`/`25-spec-governance` 重复叙述，转为短指针 + 独有走法/坑 |
| `50-adapters/README.md` | 6,436 | ≤ 4,700 | 将 5 份同构 `AGENTS.md` 短入口模板合为 1 份统一模板 + 5 行模块专属参数，精简 §二/§四叙述，完整保留 8+8 `gh label` 命令与全部保护规则 |
| `references/README.md` | 1,695 | ≤ 1,300 | 精简文件地图与每层边界描述 |
| `references/v2/SKILL.md` | 238 | 238（不动） | 兼容跳转页 |
| **合计（19 份）** | **58,382** | **≤ 43,854（硬限 46,000）** | 必读核 `17,503 → ≤ 14,894`（硬限 `15,500`） |

### 3. S3：`scripts/check-change.py` 纯 v2 重构（薄声明 + 自动扫 diff）

#### CLI 接口与退出码（保持零破坏兼容）

```bash
python3 scripts/check-change.py \
  --manifest docs/changes/<slug>/manifest.json \
  --base <git-rev> [--head HEAD] [--root .] [--draft] [--from-disk]
```

- 退出码：`0` = 绿；`1` = 有违规、schema 不合法或运行错误。
- 模式语义完全沿用 v1 防绕过强保证：
  - **正式模式（默认）**：核对磁盘 manifest 与 `--head` 提交树内 manifest 完全一致；`manifest.base`/`manifest.head`/`approval.base`/`approval.head` 必须为 7–40 位不可变十六进制提交 SHA（排除分支/tag 符号引用与字面 `HEAD`）；`manifest.head` 严格为 `--base` 后代；支持 `manifest-only` 尾部钉扎提交，且 `pinned..head` 须以 `git diff --no-renames --name-only -z pinned head` 校验（杜绝通过将他文件重命名为 `manifest_rel` 静默删文件绕过），仅当全部差异路径减去 `{manifest_rel}` 为空时放行并记 `content_head = pinned`。
  - **`--draft`**：开发 / 审核期模式，允许本地未提交 manifest 与字面 `"HEAD"`，跳过 `approval` 必填校验（若存在仍校验合法对象及非空 `base`/`head` 可解析性）。
  - **`--from-disk`**：本地预检 / 单测模式，从磁盘读取 manifest 跳过提交树一致性比对，stdout 显式打印 `mode=from-disk` 与非正式合并门禁提示。

#### v2 Manifest Schema（薄声明）

```json
{
  "schema": 2,
  "change": "2026-11-27-example",
  "title": "一句话说明本次替换式变更",
  "base": "<base commit SHA>",
  "head": "<内容提交 SHA 或 --draft 期写 HEAD>",
  "classification": "replace",
  "rule_paths": ["SKILL.md", "references/"],
  "rule_exclude": ["references/40-cases/", "references/README.md", "references/v2/SKILL.md"],
  "approval": {
    "user_quote": "用户批准改动面的原话",
    "timestamp": "2026-11-27",
    "scope": "批准覆盖的改动面",
    "base": "<base commit SHA>",
    "head": "<内容提交 SHA>",
    "link": "PR #195 或用户批准记录链接"
  },
  "rules": [
    {
      "id": "R-001",
      "type": "replace",
      "files": ["references/30-playbooks/change-protocol.md"],
      "summary": "校验器由 v1 逐行声明改为 v2 薄声明 + 自动扫 diff",
      "disposition": "replace",
      "status": "done"
    }
  ],
  "scans": [
    {
      "query": "old\\.line|same_trigger_search|NON_RULE_ALLOW",
      "scope": ["SKILL.md", "references/", "docs/"],
      "allow": [
        {
          "file": "docs/changes/README.md",
          "match": "历史旧版字段（如 old.line）说明",
          "reason": "明确标注 2026-11-26 前旧版历史快照",
          "reviewer": "review-agent",
          "review_ref": "review:iter3-r1"
        }
      ]
    }
  ],
  "semantic_checks": [
    {
      "item": "25-spec-governance、26-review-contract 与 change-protocol 触发与钉扎口径一致",
      "conclusion": "changed",
      "evidence": "三处均只指向 v2 schema 与 manifest-only 尾部钉扎"
    }
  ],
  "rebuild": {
    "triggered": true,
    "reason": "check-change.py 由 v1 全量重构为 v2 薄声明",
    "old_behaviors": ["提交树一致性与 manifest-only 尾提交钉扎", "残留正则复扫与章节断链反扫"]
  }
}
```

#### 字段规则与自动扫 diff 机器闸（逐条可判对错）

1. **版本门禁**：顶层必须有整型 `"schema": 2`（拒绝 `bool` 如 `True`）；缺省或非 `2` 时报明确错误并提示 `2026-11-26` 及以前 v1 manifest 为历史快照。
2. **`rule_paths` / `rule_exclude`（外部项目友好）**：
   - 可选；省略时默认 `rule_paths = ["SKILL.md", "references/"]`，`rule_exclude = ["references/40-cases/", "references/README.md", "references/v2/SKILL.md"]`。
   - 显式声明时 `rule_paths` 必须为非空字符串数组，元素与 `rule_exclude`（可为空 `[]`）均须为合法相对路径（非空、不以 `/` 开头、不含 `..` 分段）。
   - 路径匹配规则（全脚本 `rule_paths` / `rule_exclude` / `scans[].scope` 统一口径）：以 `/` 结尾匹配目录前缀（`p.startswith(pat)`），否则精确路径匹配（`p == pat`）。`is_rule(p)` = `p != manifest_rel` 且命中 `rule_paths` 且未命中 `rule_exclude`（显式豁免 `manifest_rel` 自身，避免外部项目配置 `rule_paths = ["docs/"]` 时出现覆盖/自禁死锁）。
3. **自动扫 diff 覆盖率（`git -c diff.renames=true diff --name-status -M -z base content_head`）**：
   - 显式隔离全局 `diff.renames` 配置并严格按 Git `--name-status -z` 协议解析 NUL 令牌流：`A`/`M`/`T`/`D` 为 2 字段 `(status, path)`；`R*` 与 `C*` 均为 3 字段 `(status, old_path, new_path)`；遇未知状态码显式报错。集合 `all_diff_paths` 包含全部涉及路径（`R*`/`C*` 含 `old_path` 与 `new_path`）。
   - **规则覆盖正向校验**：跳过 `manifest_rel` 本身；其余每条满足规则判定的 diff 条目（`A/M/T/C*` 判 `is_rule(new_path)`；`D` 判 `is_rule(old_path)`；`R*` 判 `is_rule(old_path) or is_rule(new_path)`）必须被 `rules[].files` 覆盖（`R*` 覆盖 `new_path` 或 `old_path` 之一即算覆盖）；未覆盖即红，列明状态与路径。
   - **声明反向真实性校验**：`rules[].files` 中每条路径必须真实出现在 `all_diff_paths` 中（不允许填未改动文件凑数），且不许填 `manifest_rel` 自身。
   - **配套文件自动分流**：不满足 `is_rule`、未列入 `rules[].files` 且不为 `manifest_rel` 的改动（如 `README.md`、`scripts/`、`evals/`、`references/README.md`）自动归入 `aux_files` 计数并在摘要输出（`manifest_rel` 自身不计入 `aux_files`，保持 `--draft` / 提交态 / 尾钉扎态计数稳定），**彻底取消手写 `view_files[]` 与硬编码 `NON_RULE_ALLOW`**。
4. **`rules[]` 薄声明校验**：
   - 必填非空数组；每条必填唯一 `id`、`type`（`add`/`replace`/`retire`）、非空 `files[]`、`summary`（`≥ 6` 字）、`disposition`（7 值枚举同 v1，`add` 固定 `not-applicable`）、`status`（`done`/`whitelist`/`unresolved`，遇 `unresolved` 即红）。
   - `status == "whitelist"` 时直接在同对象内校验 `reason`（非空）、`reviewer`（`user`/`review-agent`）、`review_ref`（严格匹配 `https?://\S+` / `PR #\d+.*` / `review:\S+.*`），取消独立顶层 `whitelist[]` 跨表 join。
5. **`scans[]` 活跃残留复扫**：
   - 必填非空数组；每条必填合法正则 `query`，可选 `scope`（省略时默认取 `rule_paths + ["docs/"]` 去重，外部项目无需自带 `references/`），可选 `allow[]`（默认 `[]`）。
   - `scope` 共用第 2 条路径合法性与匹配规则（无尾 `/` 为精确匹配，有尾 `/` 为目录前缀）。严格覆盖谓词：`s` 覆盖 `rp` 当且仅当 `s == rp` 或（`s.endswith("/")` 且 `rp.startswith(s)`）；若 `scope` 未覆盖全部 `rule_paths` 须提供非空 `scope_reason`（防 `"ref"` 伪前缀绕过）。
   - 扫描 `content_head` 提交树内 `scope` 覆盖的 `.md`/`.tsv`/`.txt` 文件（自动排除 `manifest_rel` 自身；默认仅排除 `docs/archive/` 与历史变更子目录 `docs/changes/*/`，**保留根级活跃文档 `docs/changes/README.md` 纳入默认扫描**；若 `scan.scope` 中某项前缀或精确路径落在 `docs/archive/` 或 `docs/changes/<slug>/` 内则取消该目录默认排除）。`scope` 在 `content_head` 中无任何可扫描文本文件时报错。
   - 0 命中且 `allow` 为空 → **直接绿**（取消 `conclusion` / `hits[]` 样板字段）。
   - 存在命中时：每条正则命中 `(rel, line_no, matched)` 必须由某条 `allow` 精准覆盖——要求 `allow.file == rel`、`allow.match` 在该整行出现且 **`matched in allow.match`**（禁止与命中词无关的常见词绕过或同行第二命中搭便车）；`allow` 必填 `file`、`match`（`≥ 4` 字）、`reason`、`reviewer`、`review_ref`，可选正整数 `count`（默认 `1`，拒绝 `bool`）。
   - **防白名单吞没与腐烂**：每条 `allow` 实际匹配的正则命中次数必须**严格等于**其 `count`（默认 `1`；既阻止一条常见词吞没同文件多处残留，又拦截 `0` 命中的过期无效 `allow`）。
6. **三道自动结构反扫（零手工配置）**：
   - **活跃语料口径**：默认取 `scans[].scope` 与 `rule_paths` 并集（第 3 道额外包含根目录现存 `README*.md`），排除 `manifest_rel`、`docs/archive/`、`docs/changes/*/`、`references/40-cases/`，以及**本 PR 未触及的冻结 `docs/specs/` 文件**（本 PR 在 `base..content_head` 中新增或修改的 `docs/specs/*.md` 草案仍纳入活跃语料）。
   - **新增断链 `§` 章节引用**：仅扫描活跃语料内变动文本文件相对 `base` 的新增行（`R*` 以 `git diff --unified=0 base:old_path content_head:new_path` 精确配对，跳过落在 `content_head` 围栏代码块内的新增行），若含 `§<数字或中文序号>` 且在 `content_head` 活跃语料去代码块标题中不存在，报红；语料外引用走可选 `section_ref_whitelist[]`（`{ref, reason, reviewer, review_ref}`，沿用严格 `reviewer`/`review_ref` 校验）。
   - **删 / 改号章节反扫**：按同一活跃语料范围分别从 `base` 与 `content_head` 去代码块正文提取标题，计算被删 / 改号章节号，反扫 `content_head` 活跃语料残留 `§` 引用（TSV/TXT 兼查裸章号），报红（走 `section_ref_whitelist[]` 豁免）。
   - **已删 / 改名文件路径残留反扫（v2 新增）**：对 diff 中状态为 `D` 或 `R*`（不含 `C*` 拷贝）且旧路径以 `.md`/`.tsv`/`.txt` 结尾的 `old_path`，自动扫描 `content_head` 活跃语料去代码块正文，检出以下两类残留即报红：① 路径边界精确匹配 `(?<![/\w.-])<old_path>(?![/\w.-])`（防子串误报）；② Markdown 链接 `` `[...](target)` `` 跳过外链（`http://`/`https://`/`mailto:`）、剥离可选标题与 `#anchor`/`?query` 并做 URL 解码后，相对当前文件规范化等于 `old_path`。确需点名历史路径说明的走可选 `path_ref_whitelist[]`（`{file, path, reason, reviewer, review_ref}`，其中 `file` 绑定具体引用文件、`path` 绑定被删/改名历史路径 `old_path`，沿用严格 `reviewer`/`review_ref` 校验，且过期无效项报红，防止全局白名单致盲）。
7. **`semantic_checks[]` 与 `rebuild`**：保留 v1 结构校验（`semantic_checks[]` 非空，`item`/`evidence ≥ 4` 字，`conclusion ∈ {match, changed, whitelist, unresolved}` 禁 `unresolved`；`rebuild.triggered` 布尔，为 `true` 时必填 `reason` 与非空 `old_behaviors[]`）。
8. **摘要输出**：单行打印 `schema=2 base=... head=... [content_pinned=...] [mode=...] rules=N add/replace/retire=A/R/T status done/whitelist/unresolved=D/W/U rule_files=M aux_files=K scans=S allow=L semantic_checks=C`（与 `references/26-review-contract.md` §五.1 所需 `rules / whitelist / scans / unresolved` 计数保持一致）及绿/红明细。

### 4. 备选方案与代价

- **备选 1（仅瘦身 3 文件）**：仅瘦身 `26-review-contract` / `15-records` / `change-protocol`，改动小但留住 `50-adapters`（`6,436` 字）与 8 条 playbook 跨层复述，全仓仍超 `52,000` 字。用户已拍板选全域瘦身 `≤ 46,000`（`SL-1`）。
- **备选 2（v1/v2 双轨兼容）**：保留 v1 校验分支让旧 4 份 manifest 持续可跑，但脚本膨胀至 ~1,000+ 行违背反熵增目标。用户已拍板选纯 v2 替换、旧 manifest 标历史快照（`SL-3`）。
- **备选 3（顺手改 Eval 正则）**：同步修改 `13`/`14` 的 `R3-M1`/`R3-M2` 会改变对比尺子本身，削弱瘦身前后 A/B 说服力。用户已拍板严格冻结 14 条 Eval 不动（`SL-4`）。

### 5. 承重路径业务例子（可推翻方案）

1. **全仓字数硬闸反例**：在 `26-review-contract` 达标前提下，向不在 `CORE_BUDGETS` 内的 `50-adapters/README.md` 塞入 `3,000` 字使全仓达 `46,500` 字；`bash scripts/check-docs.sh` 必须在全仓现行规则总字数行报 `[红]` 且退出码 `1`。
2. **v2 自动扫 diff + 改名反扫 + 配套文件免填反例**：某 PR 重命名 `references/30-playbooks/old.md → new.md`、修改 `references/15-records.md` 与 `README.md`，但 v2 manifest 漏写 `15-records.md` 且 `10-stages.md` 仍含 `[旧](30-playbooks/old.md#一参考走法)`；`check-change.py --draft` 须同时报「未覆盖变更规则文件 `15-records.md`」与「已删 / 改名路径残留 `10-stages.md → references/30-playbooks/old.md`」并退出码 `1`；修复 `10-stages.md` 链接并将 `15-records.md` 与 `10-stages.md` 均补入 `rules[].files` 后，即使 `README.md` 未列任何 `view_files[]`（且 `manifest_rel` 已提交）仍须直接绿并稳定报 `aux_files=1`。
3. **瘦身防行为退化反例**：若压缩 `26-review-contract.md` 误删「R3 停、不派第 4 轮」或压缩 `15-records.md` 误删 D0 8 字段，虽 `check-docs.sh` 可绿，但冻结的 Eval `07-review-scope-creep` / `04-valid-d0-delegation` 会在双层评分中 `fail` 并报 `regressions != []`（退出码 `1`），直接阻断合入。

---

## 五、迁移、兼容、依赖、回滚与外部契约影响

- **外部依赖**：无新增外部依赖（仅依赖现有 Python 3.9+ 标准库、bash 与 git）。
- **外部契约影响**：外部项目调用 `scripts/check-change.py` 的 CLI 参数（`--manifest` / `--base` / `--head` / `--root` / `--draft` / `--from-disk`）保持 100% 不变；manifest 文件格式由 v1 替换为 v2（须含 `"schema": 2`），在 `references/30-playbooks/change-protocol.md`、`docs/changes/README.md` 与双语 README 中明示升级口径，2026-11-26 及以前的历史 manifest 保留为只读快照不重写。
- **数据迁移 / 数据库变更**：不适用（纯 Markdown 与本地校验脚本仓，无数据库或状态存储）。
- **回滚策略**：全部实施改动位于独立分支与单次可定位提交序列；若合入后发现回归，可直接 `git revert`（按 L0-1 / D7 经用户确认执行）。

---

## 六、改动文件清单（实施期预期交付）

| 类别 | 文件路径 | 预期动作 |
|---|---|---|
| 检查脚本 | `scripts/check-docs.sh` | 新增必读核 `≤ 15,500`、全仓 `≤ 46,000` 硬闸并收紧单文件预算 |
| 校验脚本与单测 | `scripts/check-change.py`、`scripts/test-check-change.py` | 纯 v2 薄声明 + 自动扫 diff 重构与全套正负例迁移 |
| 核心规则（6 份） | `SKILL.md`、`references/{10-stages,15-records,20-decisions,25-spec-governance,26-review-contract}.md` | 激进瘦身，保锚点、保 owner 标记、保语义 |
| Playbooks（9 份） | `references/30-playbooks/{adr,change-protocol,direct,incident,issue,labels,new-spec,release,worktree}.md` | 重写 `change-protocol.md`（v2）并全面压缩其余 8 份 |
| 接入与导航（2 份） | `references/50-adapters/README.md`、`references/README.md` | 合并 5 份重复模板与精简叙述 |
| 模板与本轮台账 | `docs/changes/README.md`、`docs/changes/2026-11-27-iter3-rule-slimming-and-thin-check-change/manifest.json` | 更新 v2 模板与历史快照说明；产出本轮实战 v2 manifest 并钉扎 |
| 基线与双语视图 | `evals/baselines/2026-11-27-iter3-slim.{json,md}`、`README.md`、`README.zh-CN.md` | 落盘 14 路全绿脱敏基线，同步双语 README 预算数字与 v2 校验器描述 |

**不可碰保护清单（实施后 `git diff` 必须为空）**：`references/00-constitution.md`、`references/v2/SKILL.md`、`evals/scenarios/`、`scripts/run-eval.py`、`scripts/test-run-eval.py`、`evals/baselines/2026-11-26-v2-baseline.{json,md}`、`evals/baselines/2026-11-26-iter2-anti-entropy.{json,md}`、`docs/changes/2026-11-25-*/`、`docs/changes/2026-11-26-*/`、`docs/archive/`、整个 `docs/specs/`（含全部 40 份既有冻结 spec 及本规格经 D3 合并后的冻结正文）。

---

## 七、验收标准（正常 / 异常 / 边界 / 回归）

1. **文档与预算门禁（正常）**：`bash scripts/check-docs.sh` 全绿（退出码 `0`），输出证实 `SKILL.md` 正文 `≤ 2,600` 字 / 全文件 `≤ 60` 行、`always_read_chars ≤ 15,500`、`total_rule_chars ≤ 46,000`、`CORE_BUDGETS` 全达标、单行 `≤ 220`、全链 / 精确 `#锚点` 可达、双语 README 同步。
2. **预算超限拦截（异常 / 边界）**：在临时测试或单测中验证必读核超 `15,500` 或非核心文件拉高全仓超 `46,000` 时 `check-docs.sh` 明确报 `[红]` 并以退出码 `1` 拦截（验完恢复干净树）。
3. **v2 校验器正负例单测（正常 + 异常 + 边界）**：`PYTHONDONTWRITEBYTECODE=1 python3 scripts/test-check-change.py` 全绿，完整覆盖：
   - 正常：v2 真实提交树一致、`manifest-only` 尾部 SHA 钉扎、`--draft`、`--from-disk` 输出标记、0 命中 `scans[]` 自动绿、有命中 `allow[]` 精准放行（含 `count`）、重命名 `R*` 覆盖与拷贝 `C*` 3 字段解析、`aux_files` 免填且不含 `manifest_rel`、外部项目 `rule_paths = ["docs/"]` 豁免 `manifest_rel` 不死锁、`docs/changes/README.md` 纳入默认扫描；
   - 异常 / 边界：缺 `schema` 或 `schema != 2` / `schema: true`、旧 v1 manifest 被清晰拒并提示历史快照、正式模式符号引用（`HEAD`/`@`/`HEAD~0`/分支）与 JSON `null` 拦截、钉扎后非 manifest 尾改及尾提交重命名他文件为 `manifest_rel` 绕过拦截、未覆盖变更规则文件拦截、`rules[].files` 声明未改动文件或 `manifest_rel` 拦截、`scans[].scope` 伪前缀（如 `"ref"`）绕过拦截、`scans[]` 漏报命中 / 无关词 `allow` 搭便车 / 单条 `allow` 吞没多命中 / 过期无效 `allow` 拦截、新增断链 `§`（跳代码块）与删改章节残留拦截、已删 / 改名文本文件（`.md`/`.tsv`/`.txt`）字面路径与带 `#锚点` 相对 Markdown 链接残留拦截及 `{file, path}` 绑定式 `path_ref_whitelist[]`（含过期拦截）、`rebuild.triggered=true` 缺 `old_behaviors` 拦截、容器畸形防崩溃。
4. **实战自验（本轮 v2 manifest 正式门禁）**：本轮实施 PR 的 `docs/changes/2026-11-27-iter3-rule-slimming-and-thin-check-change/manifest.json` 经 `manifest-only` 钉扎后，执行 `python3 scripts/check-change.py --manifest docs/changes/2026-11-27-iter3-rule-slimming-and-thin-check-change/manifest.json --base <iter3-base> --head HEAD` 退出码 `0` 绿。
5. **冻结 Eval 零退化回归（回归）**：
   - `python3 scripts/run-eval.py --validate` 14/14 绿且 `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test-run-eval.py` 全绿；
   - 14 路隔离执行后运行 `python3 scripts/run-eval.py --grade <out> --rubric-file <rubric.json> --baseline evals/baselines/2026-11-26-iter2-anti-entropy.json`，输出 `pass=14`、`fail=0`、`regressions=[]`、`always_read_chars_delta < 0`、`total_rule_chars_delta < 0`；
   - 脱敏基线 `evals/baselines/2026-11-27-iter3-slim.{json,md}` 落盘且无本机绝对路径残留（并诚实标明自测基线来源）。
6. **保护边界零改动（回归）**：对全部不可碰保护清单运行 `git diff <base>..HEAD -- ...` 输出为空。

---

## 八、审核与修订记录

| 轮次 | 基准 | 档位与结论 | 修订处置（全部 11 项去重闭合） |
|---|---|---|---|
| R1 | `4399980..6996ba0` | 重审（2/2）：Lane A `0/4/2/1`（`F1`–`F7`），Lane B `3/3/2/0`（`B-1`–`B-8`），范围外 `0` | 按 D2「全改」闭合全部 11 项：① 排除收窄至 `docs/changes/*/` 保留 `docs/changes/README.md` 并对齐示例（`F1`/`B-1`）；② `allow[]` 强绑 `matched in allow.match` 与精确 `count` 默认 `1`（`B-2`）；③ `manifest_rel` 豁免 `is_rule` 与 `aux_files` 且补齐例 2 的 `10-stages.md`（`B-3`/`F3`）；④ 活跃语料排除未触及冻结 `docs/specs/` 与 `40-cases/`、`path_ref_whitelist[]` 绑 `{file, path}` 并补 `#anchor` 解码与路径边界（`B-4`/`F6`）；⑤ 修正 `C*` 3 字段、`git -c diff.renames=true` 及尾钉扎 `--no-renames`（`B-5`）；⑥ 统一 `scope` 校验与严格目录前缀覆盖（`B-6`）；⑦ 摘要保留 `status done/whitelist/unresolved` 与 `allow`（`F2`/`B-8`）；⑧ 保护清单扩至全 `docs/specs/` 与历史基线（`F4`）；⑨ 第 1/2 道章节反扫跳代码块、`R*` 配对与同语料提取（`B-7`）；⑩ 统一目标数字、`SKILL.md` 整文件行数口径与补 `release.md#三批次测试失败修复fix`（`F5`/`B-8`）；⑪ 补 `§五` 外部依赖声明（`F7`） |
