# Case: 2026-11-11 staging 线演练

- **情况**：三轮 staging 演练（录音 App 起步、taoxi_system 审批拆分、客户线索筛选）。演练里一次直接干把 PR 先合进 staging，再问「用 staging 测吗」；另一次发现在删除 rc 监控时把 rc 验收整步删了，批次测试测的是 staging HEAD，替代不了从 rc tag 构建。用户随后提出「一个需求 PR 很多时，怎么保证整体到达 staging 并被发布」。
- **预期**：issue 分支各自绿就代表可以一起发；rc tag 固定已测提交即可。
- **实际**：issue 分支只在自身绿，合入后可能与别的 issue 或 staging 新提交冲突；四类核对只在发布分拣时做，合入闸没有；直接干的测试对象已经不是待合入版本；rc tag 后没有从 tag 构建的验收。
- **意外**：dev + 分拣与 issue 集成分支解的是同一个问题的三层——分支管「单元」、预演管「合入」、tag 管「发布」。行业里 GitHub merge queue、Gerrit `submitWholeTopic`、Chromium CQ 各解其中一层；staging 线取「集成分支 + 原子合入 + 预演」三件，不需要引入 merge queue 改造。
- **学到什么**：整条 issue 合入前的合入预演发生在真实 merge 树上，结果树与真实 merge 树一致才算绿；四类核对前移到合入闸；整条合入是真 merge，不是 squash；直接干的验收对象是 PR 分支而不是已合并的候选；rc 验收从 tag 构建，通过后才打最终 tag；多 PR 需求以 issue 分支作为集成单元。
- **影响提议**：无。已进 [issue playbook](../30-playbooks/issue.md)、[direct playbook](../30-playbooks/direct.md)、[release playbook](../30-playbooks/release.md) 与 [batch-fix playbook](../30-playbooks/batch-fix.md)。
- **用户是否批准偏离**：是。用户要求按演练结论落规则；R38-R40 记录了本轮决定。
- **被哪条规则覆盖 / superseded_by**：覆盖于 `30-playbooks/issue.md` 合入预演、`30-playbooks/direct.md` 先测后合、`30-playbooks/release.md` rc；superseded_by：无。
