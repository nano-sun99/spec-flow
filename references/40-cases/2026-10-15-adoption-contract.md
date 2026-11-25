# Case: 2026-10-15 采用契约缺位与判据住选修

- **来源**：v1 rationale R19、R21；`docs/specs/2026-10-15-optional-memo-adoption-contract.md`、`2026-10-15-script-boundary-and-issue-close-semantics.md`

- **情况**：三个选修备忘录各写各的采用口径——ADR 写在「三种使用状态」、文档生命周期散在 §三、issue 标签在 §六；`SKILL.md` 参考表里只有 ADR 行写了读取条件；`apply-to-project.md` 有三个注册修饰词，却没有统一规定一个修饰词该声明哪些元数据、执行时点、验收方式。
- **预期**：把正文放进 `references/` 就能被 agent 用到。
- **实际**：新增备忘录只放正文、不登记时，就成了「仓库里有正文，agent 平时不知道它存在」。实测两个方向同时出现：jasmine-lottery 没采用标签备忘录，`AGENTS.md` 里没有对应节，判据读不到；taoxi_system 采用了，却把〈上线时分拣〉复述进 `AGENTS.md`，成了第二份。检查脚本只核已有登记项，只加文件不登记时九项全绿。
- **意外**：采用契约的失效方式不是写错，是没人读——未登记 = 未生效；而判据住在选修里，分量取决于有没有人选修。
- **学到什么**：采用契约的事实形态是三态（默认关闭 / 本次按需 / 项目级持久）、最低元数据、执行时点和可复跑验收；判据与采用动作分家，什么算完进阶段合同与记录，标签和时点表留在选修；默认项目资产不含脚本 / CI，确需新增时停在「材料备好」。
- **影响提议**：无。已进 [50-adapters](../50-adapters/README.md) 采用边界与 [labels playbook](../30-playbooks/labels.md)。
- **用户是否批准偏离**：是。采用契约与判据提级按 owner 拍板落地；未采用项目不新增制度入口。
- **被哪条规则覆盖 / superseded_by**：覆盖于 `50-adapters/README.md`；superseded_by：无。
