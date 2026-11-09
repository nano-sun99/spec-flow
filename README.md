<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo/spec-flow-lockup-dark.svg">
    <img alt="spec-flow" src="assets/logo/spec-flow-lockup.svg" width="480">
  </picture>
</p>

**A set of process rules for AI coding agents.** You clone it into your agent's skills directory. From then on, when you ask for work worth designing, the agent agrees with you on what it is building *before* it writes code — and everything it produces has to pass a gate where **you** decide how much review it gets.

The workflow has no runtime or service. It is markdown the agent reads, plus a paper trail: on the spec path, a spec before code, an issue before implementation, and a permanent link between them. Direct implementation skips the spec and execution issue, not the delivery gate. Code mapping is disabled by default; ordinary tasks use source searches, the actual diff and relevant tests to check impact.

This revision limits the body to **4,700 characters**, frontmatter to **500**, and the whole skill to **5,200**, including newlines. [`scripts/check-docs.sh`](scripts/check-docs.sh) checks all three and rejects extra metadata fields or multiline descriptions. These are character budgets, not a cross-client token or compaction guarantee. Action-specific details are mandatory when needed; after compaction hides them, the agent reads them again.

Every rule has a recorded origin. The dossier is [`references/rationale.md`](references/rationale.md): 36 entries with dates, measurements, decisions, costs and verification limits.

**English** · [中文](README.zh-CN.md)

> The workflow itself is written in Chinese (`SKILL.md` and `references/`). This README is the English entry point, so you can tell whether it's for you before opening anything.

<!-- s:shape -->
## What using it looks like

You type the same request either way: *"add image upload to the profile page."*

**Without it**, the agent starts writing. Forty minutes later there is a diff across eleven files, a database table you didn't ask for, and a resize limit it picked itself. Reading the code is how you find out what it decided.

**With it**, a new request starts with your choice: implement directly or open a spec. The agent does not choose for you because a change looks small. For a spec, grill-me helps clarify where files live, mobile support and a 40MB upload; spec-flow collects what changes, how, the problem solved or capability gained, and the goal, scope and acceptance criteria into one plan. **No** feeds back into that same plan. No spec is written before the first **Yes**; Yes immediately leads to your choice of pages or no pages. There is no separate mechanism card or fixed three-question gate.

With pages, it writes a goal-and-acceptance draft in one Draft PR, asks about splitting, then pauses for your design. The agent uses grill-me to analyze interactions, states, permissions and API requests / responses / errors before completing that same spec. Without pages, normal, boundary and failure or rerun examples replace the design wait; the split choice still follows the draft. Only a final spec that passes the Definition of Ready, with your consent to send it for review, reaches the review card — **none / light / heavy / heavy + mutation testing**. Review walks the route: R1 full, R2 checks closures, R3 stops for your choice to redraw, cut scope or stop.

After review and any revision, every PR gets a separate merge confirmation. Only after the spec merges does it open an execution issue with a `SPEC_READY` handoff and stop for your explicit implementation delegation. Implementation uses an isolated worktree and gets a fresh review choice and merge confirmation. Exception and merged-spec-edit cards remain conditional, not mandatory questions on every run.

The misunderstanding that used to surface at minute forty now surfaces at minute two.

<!-- s:problem -->
## The problem

A coding agent fails at its seams, not inside its steps:

- **between your request and its understanding** — it starts from a half-formed brief, and you meet the misunderstanding in the diff;
- **between one deliverable and the next** — it finishes a large chunk in one go, so nothing interrupts a wrong turn before the whole chunk is built on top of it;
- **between the agent and the thing checking the agent** — it reports "an independent reviewer checked this" when the reviewer was a subagent it spawned, prompted and framed itself, chosen by the party that wants the green light;
- **between two agents** — both read the same issue as unclaimed and do the same work twice;
- **between last month's decision and today's work** — the reasoning behind a change lives in a conversation nobody can reopen.

None of these are model failures, and none are fixed by trying harder inside a single step. They are unowned boundaries.

<!-- s:scars -->
## Where the rules came from

Not from theory. Each rule is the residue of a specific failure, recorded with its date and numbers in [`references/rationale.md`](references/rationale.md). Five of the recorded cases:

- **A criterion was widened and nothing else moved.** An IDC rule went from "CIDR ranges" to "CIDR ∪ ASN". Only that sentence changed — while the mechanism, the implementation, the steps and the acceptance criteria all still described the old behaviour, as did the parent document's overview. Building from that spec would have shipped CIDR-only. An independent review caught two severe findings. → **R1**: change a criterion, sync every place it lands.
- **Two agents claimed the same issue.** Both read *open* as "nobody is working on this" and both did the work. One was wasted. → **R7**: the claim is the worktree being created, not the issue's state.
- **A customer fell through a twelve-way split.** Two of the specs each wrote their own version of "is this account enabled" — one checked a flag, the other only checked that a row could be found by name. Nothing owned the difference, and it surfaced in implementation. → **R15**: splitting means writing down the dependency edges, not just the file boundaries.
- **One spec, seventeen rewrites.** A project's single spec went from 448 to 762 lines over 17 commits, 14 of them changing its body. Its owner finally interrupted the agent mid-task: *"this is a new requirement — write a new spec, stop editing that one."* → **R12**: editing a merged spec is a card you answer, not a judgement call.
- **Five processes, one lock.** Measured: five processes raced for the same issue number; exactly one created the worktree and the other four were rejected. → **R6**: the lock is git's, not ours.

<!-- s:what -->
## How it solves them

**Two phases, one shared gate.** Each step owns one of the seams above.

- **Phase 1 · design** — entry choice for new requests only; open a spec → grill-me assists clarification, spec-flow collects one plan → Yes / No loop → Yes immediately opens the pages / no-pages choice → draft → separate split choice → with pages, pause for your design and then analyze pages and APIs; without pages, use examples → the same final spec passes the seven-point Definition of Ready → you consent to send it for review → Draft becomes Ready (or a normal PR opens) → choose review, revise if needed, separately confirm merge → merge spec, open execution issues with `SPEC_READY` handoffs and a batch table → stop. Draft, counterpart and final remain one file in one PR; only the final faces the gate. Direct implementation creates no mandatory spec or execution issue, but still faces the implementation delivery gate.
- **Phase 2 · implementation** — after you explicitly delegate implementation, claim the issue → implement → gate → confirm merge → merge → backfill the issue and release the lock.

| The step | The seam it owns |
|---|---|
| Agreeing on the need is a hard gate — no spec file gets touched until you nod | request ↔ understanding |
| Every deliverable passes a gate of its own | one deliverable ↔ the next |
| The agent may not produce a review verdict on its own behalf | the agent ↔ its checker |
| Claiming an issue means creating a worktree named after it | one agent ↔ another |
| An issue anchors a permanent link to the merged spec | last month ↔ today |

<!-- s:self-review -->
## The one rule worth stealing: a subagent is not a second opinion

Everything the agent spawns is still the agent — same task, same prompt, same framing, chosen by the party that wants the green light. A subagent's conclusion weighs exactly as much as the agent's own. No more.

So spec-flow forbids the agent from producing a review verdict on its own behalf: the review level is yours to pick, and it may not dispatch a reviewer to do the judging for it. When a step genuinely needs an opinion that isn't the agent's, the step stops and waits for a human.

<!-- s:smooth -->
## Why it doesn't feel heavy

It isn't restraint bolted onto the agent. It's rework moved to where rework is cheap — and every mechanism is shaped to cost you as little attention as possible.

| The design | Why it's smooth |
|---|---|
| The review level is chosen per deliverable and never inherited | Cost tracks risk: **none / light / heavy / heavy + mutation testing**. A one-line doc change costs nothing; a core change gets two reviewers. No blanket policy to argue about. |
| An unanswered card never adds anything | No entry choice means no file writes; no confirmed plan means no spec; unanswered page / split choices stop progress. Missing dependencies never imply installation consent. No review choice means no reviewer, and no merge choice means no merge; conditional exceptions and merged-spec edits are not silently included. |
| Confirm decisions once, without duplicate summaries | New approaches and their reasons belong in the same Yes / No plan, not a separate mechanism card or fixed three-question gate. Agent-chosen defaults, names and locations stay in a final details section to skim; only material plan changes return to the same confirmation loop. |
| The judgement is taken away from the agent | It may not decide "this one counts as core". That removes the argument, not just the risk. |
| Every rule cites the incident that produced it | Disagree with a rule and its origin is one hop away. You never re-litigate it from scratch. |

Review, revision and merge are three separate answers. An unanswered review card defaults to no review, but no card's silence approves a merge; zero findings, green checks and “agree to fix” don't either.

<!-- s:longrun -->
## Why it survives long work

**State lives in git, not in the agent's head.**

| To know | It's written in | Why you can trust it |
|---|---|---|
| Who is working on it | the worktree name — the lock itself | Creating `issue-42` succeeds = nobody has it; refused = somebody does. (`git worktree list` shows the same at a glance, but the lock is the create succeeding.) No separate assignment board to fall out of sync. |
| How far along it is | the issue's state and the pull request | Durable, readable across sessions, unchanged when you switch machines or hand it to someone else. |
| Why it was built that way | the spec in `docs/specs/`, linked from the issue | It passed the gate, it's in prose, and it's versioned with the code — diffable, blamable, revertable. |

Tools that keep this in their own private index drift without telling you. This one can't: git says so, loudly, the moment it happens.

<!-- s:limits -->
## What it doesn't do

- **It doesn't remember the process.** What was tried and abandoned, which dead end cost an hour, which step you were mid-way through — if it wasn't written down, it's gone. One part does get written down: the review trail, every finding and how it was disposed of, appended to the spec. So a new session reads *what to do*, *how far along*, and *what was caught last time* — but not *why the road not taken didn't work*.
- **It isn't a runtime.** Nothing here schedules an agent, checkpoints a run, or resumes one that died at 3am. It assumes you are there for the gate.
- **Most of it isn't enforced.** These are rules the agent is asked to follow, not mechanisms that force it — including the independent merge confirmation. The parts that *are* enforced are enforced by git (the worktree lock) and by this repo's own check script.
- **It assumes GitHub.** Issues and pull requests are load-bearing, not decoration.

<!-- s:install -->
## Install

```bash
git clone https://github.com/Strelizialeomon/spec-flow.git ~/.claude/skills/spec-flow
```

That's the skill installation, not project adoption or tool setup. Claude Code loads personal skills from `~/.claude/skills/<name>/SKILL.md`; update that checkout with `git pull`. Other clients use their own skill discovery paths.

If you keep your repos elsewhere (as the author does), clone anywhere and symlink it in:

```bash
git clone https://github.com/Strelizialeomon/spec-flow.git ~/code/spec-flow
ln -s ~/code/spec-flow ~/.claude/skills/spec-flow
```

Requirements: an agent that discovers skills, runs shell commands (`git worktree`), and opens PRs (`gh`). Professional clarification in PLAN / ANALYZE also needs loadable `grill-me` and its actual `grilling` dependency; an entry directory alone is not enough. Loading spec-flow checks this read-only. Only a clarification path that needs missing skills asks Yes / No with specific installation contents; refusal or failure pauses that path. Existing dependencies are not reinstalled, and other repositories or machine configuration are not silently changed. Missing clarification skills do not block direct implementation, existing-task implementation or delivery. The rules are markdown; discovery, permissions and compaction still need real client tests. Passing doc checks does not prove compliance, and superpowers is no longer a dependency.

<!-- s:usage -->
## Using it

Describe work worth designing, or invoke spec-flow by name. Only a new request starts with the entry choice. Choosing a spec immediately brings in grill-me; spec-flow collects the plan, No adjusts it, and Yes immediately asks you to choose pages or no pages. The spec lives in `docs/specs/<date>-<name>.md`: with pages, a goal / acceptance / design-brief draft goes into a Draft PR; without pages, use three real examples or one decision table. After the chosen branch's draft, the agent assesses size, offers real split candidates and a recommendation, and you choose split or keep. Multiple implementation milestones, including in children, require a reminder; ordinary coding, testing and PR steps are not milestones. No split choice means no further progress.

With pages, the split choice is followed by a pause for your design; only afterward does grill-me help analyze pages and APIs. The agent neither draws for you nor automatically switches to no pages, and valid designs need not be resubmitted. Without pages there is no design wait: normal, boundary / exception, and failure or rerun examples fill the same route table (step | trigger → response | failure / empty state | landing · basis · evidence). Results complete the same final spec. Unresolved load-bearing decisions or unexecutable acceptance block review. Only passing the DoR plus your consent makes it Ready for a review choice; only the final faces the gate and a merge confirmation, before execution issues open. No implementation-planning stage is added.

Splitting produces smaller execution specs, each with its own execution issue, plus an overview and one tracking-only parent issue. A stable group ID and child number connect filenames, specs and issue titles; parent-child links show membership, while blocking links show real dependencies. Maximize parallel work where practical, without requiring it: explicit sequential dependencies and coordinated releases are allowed. Choosing not to split preserves one spec and one execution issue, rather than silently creating a set of phase-only issues.

You can also enter from the middle: "do #12" starts phase 2 for an existing issue, and still passes the gate and gets a separate merge confirmation before merging. In the same window right after a single `SPEC_READY` handoff, "start implementation" continues that issue; a new window, another agent, or multiple un-authorized handoffs requires the issue number.

To adopt it, say **"apply spec-flow to this project"**. It writes a pointer in `AGENTS.md`, adding `@AGENTS.md` to `CLAUDE.md` only if that file exists. **"Update this project's spec-flow integration"** explicitly checks and upgrades an old entry, including already adopted ADR actions and document reading order; repeat runs are idempotent and do not enable unadopted options. Ordinary work does not repair project rules as a side effect.

**Code mapping is disabled by default.** Ordinary work and integration updates do not query the map, check its readiness or repair its configuration. Source searches, the actual diff and relevant tests remain required where applicable. Read the [code-map notes](references/code-map.md) only when the user explicitly requests a new trial or restoration; old adoption, an installed tool or existing configuration does not restore it. A one-task trial does not authorize persistent adoption, installation or hooks. The trial results and decision are recorded in rationale R27.

Already adopted ADR rules apply during discovery, before old-issue or design-exempt implementation, on explicit long-term decisions, and when checking this task's outcome. The current approved spec must be read before implementation; only historical specs are optional tracing material. These are existing action points, not new steps or three fixed ADR gates.

<!-- s:evidence -->
## This repo is its own case study

spec-flow is developed with spec-flow. As of 2026-10-16: 66 merged PRs, 17 issues, 16 specs in `docs/specs/`. Each spec is the design record of one change; the PRs that went through a review hold its findings in the discussion, including the findings that changed a rule.

The rules are cited by `R` number, like `（依据：rationale R12）`, and every one of those points into [`references/rationale.md`](references/rationale.md). That file records the cases in full: the IDC criterion widened in one place while four others and the parent document stayed stale, the completion contract that stops "no bugs" from meaning "we promise nothing will ever break", and a controlled comparison of how two projects consumed and recorded adopted architecture decisions, with the limits of that evidence.

<!-- s:docs -->
## Files

| File | What's in it |
|---|---|
| `SKILL.md` | The workflow itself — the file the agent loads |
| `AGENTS.md` | This repo's maintenance rules for the agent |
| `CLAUDE.md` | One line: `@AGENTS.md` |
| `references/rationale.md` | Why each rule exists: cases, measurements, decisions (R1–R36) |
| `references/one-path.md` | The route template, one plan-confirmation loop, page branches, walking review, batch table and card defaults |
| `references/gate-details.md` | How the gate runs: walking review (R1–R3), severity, doc checks, batching, merge confirmation |
| `references/worktree-lock.md` | File changes, claiming an issue; the worktree lock, and how it breaks |
| `references/phase-handoff.md` | Handoff state, authorization, takeover and the issue handoff block |
| `references/spec-maturity.md` | One spec's draft, post-design page / API counterpart, final and DoR; the user chooses the page branch |
| `references/spec-revision-sync.md` | Changing one clause means syncing every place it lands |
| `references/code-map.md` | Disabled by default; explicit trials, coverage limits and fallback |
| `references/done-criteria.md` | Done criteria, observational close-outs, the three exception types |
| `references/split-large-spec.md` | Pre-issue sizing and choice, small delivery units, stable IDs and parent-child issues; maps, dependencies and the batch table |
| `references/adr-decision-records.md` | Optional: architecture decision records |
| `references/documentation-lifecycle.md` | Optional: spec / ADR / issue division of labour |
| `references/issue-status-labels.md` | Optional: issue status labels |
| `references/issue-type-labels.md` | Optional: issue type labels |
| `references/release-discipline.md` | Optional: release closed loop (release record, readiness gate, mainline alignment, post-release backfill) |
| `references/apply-to-project.md` | Applying and explicitly upgrading; pointer templates, asset boundaries, clarification dependencies and install consent, explicit map-restoration requests |
| `references/adoption-model.md` | Historical explanation of the adoption model; no additional workflow obligations |
| `docs/maintainer-notes.md` | Repo-local notes: how this checkout is wired, why the first commits are reconstructed |
| `scripts/check-docs.sh` | Body / frontmatter / whole-skill budgets, reference paths, relative links, release adoption and release-loop sections, README sync, region-bound adoption contract |

The workflow itself is `SKILL.md`; where this README and that file disagree, `SKILL.md` wins. Which reference to read when is listed at the bottom of `SKILL.md`.

<!-- s:contributing -->
## Contributing

Keep it small. Open an issue, or send a PR. One convention: if your change adds or alters a rule, record the case behind it in `references/rationale.md` under a new `R` number — rules here are supposed to be able to point at something that actually happened.

<!-- s:license -->
## License

MIT — see [LICENSE](LICENSE).
