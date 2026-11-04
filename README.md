<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo/spec-flow-lockup-dark.svg">
    <img alt="spec-flow" src="assets/logo/spec-flow-lockup.svg" width="480">
  </picture>
</p>

**A set of process rules for AI coding agents.** Clone it into your agent's skills directory. From then on, when you ask for work worth designing, the agent agrees with you on what it is building *before* it writes code — and everything it produces has to pass a gate where **you** decide how much review it gets.

**Three files by default.** A start page, a gate sheet, and a project page for PRs and issues. The other seventeen are layered: scenario packs on trigger, optional memos off by default, the map archived. One `spec-check` script does the deterministic checks: a missing anchor, empty acceptance, an unfilled placeholder, a diff outside the declared files — any one turns red on the spot.

**These rules are not allowed to get fatter.** A new failure may only become a check or replace an old rule — never a new section, card or reference file. The budgets live in `scripts/check-docs.sh` (2,800 characters of body, 60 lines of `SKILL.md`, 180 lines across the three default files), and it goes red when they are exceeded.

The workflow has no runtime or service. It is markdown the agent reads, plus a paper trail: a spec before code, an issue before work, and a permanent link between them.

**English** · [中文](README.zh-CN.md)

> The workflow itself is written in Chinese (`SKILL.md` and `references/`). This README is the English entry point, so you can tell whether it's for you before opening anything.

<!-- s:shape -->
## What using it looks like

You type the same request either way: *"add image upload to the profile page."*

**Without it**, the agent starts writing. Forty minutes later there is a diff across eleven files, a database table you didn't ask for, and a resize limit it picked itself. Reading the code is how you find out what it decided.

**With it**, it comes back in two minutes with the three things it cannot answer for you — where the files live, does this need to work on mobile, what should happen to a 40MB upload — and nothing else. Then it writes a one-page start: goal / not doing / acceptance, the files it will and will not touch, and an acceptance table. The script runs first; anything red stops the run. The page goes to its own PR, and you pick the review level — **none / light / heavy / heavy + mutation testing**. Review has a fixed shape: four inputs, three columns, at most two rounds, and findings outside scope go into a suggestion pool instead of becoming revisions. Every round opens with one line: goal / progress / still missing. After review it asks separately whether to merge; the spec merges, an execution issue opens, and implementation waits for your explicit delegation. Code changes run in a worktree, and every round checks the diff against the declared file list.

**The misunderstanding that used to surface at minute forty now surfaces at minute two.**

<!-- s:problem -->
## The problem

A coding agent fails at its seams, not inside its steps:

- **between your request and its understanding** — it starts from a half-formed brief, and you meet the misunderstanding in the diff;
- **between one deliverable and the next** — it finishes a large chunk in one go, so nothing interrupts a wrong turn before the chunk is built on it;
- **between the agent and the thing checking the agent** — it reports "an independent reviewer checked this" when the reviewer was a subagent it spawned, prompted and framed itself;
- **between two agents** — both read the same issue as unclaimed and do the work twice;
- **between last month's decision and today's work** — the reasoning behind a change lives in a conversation nobody can reopen.

None of these are model failures, and none are fixed by trying harder inside a single step. They are unowned boundaries.

<!-- s:constitution -->
## Why it can't keep growing

**Add a rule every time something goes wrong, and the rules stop being executable — so you add another.** In eight weeks this went from 44 lines to 2,945, and what grew was never capability; it was the surface you had to read. So this version stops the growth of the default surface, not the history.

- **Layering.** Three standing files — the start page, the gate sheet, the project page. All seventeen others stay, sorted into layers (scenario packs / optional memos / archive / on demand) with one trigger line each; the default path never opens a fourth file. Nothing deep was deleted; it just isn't read by default.
- **A constitution.** New failures may only become checks or replace an existing rule. No new sections, cards or reference files. The three-file default is a whitelist; a fourth needs your nod.
- **Checks move into a script.** `spec-check` covers E1–E5: the three-line anchor, testable acceptance criteria, placeholders, undisposed ❌, and diffs outside the declared files. Warnings don't block; errors exit 1. Anything a human has to keep watching goes to something that can be rerun.

**The arithmetic:** default surface 2,945 → 137 lines, `SKILL.md` 118 → 60. The repo did not get smaller; what you have to read every time did.

<!-- s:what -->
## How it runs

**Two phases, one shared gate.** Each step owns one of the seams above.

```
Phase 1 · design (steps 1–6, no code is written)
1 need → 2 confirm → 3 skeleton → 4 split / contrast / implementation-ready → 5 revise / merge → 6 open the execution issue
                              ↓
                              ⏸ stop: step 6 opens the issue and ends — wait for the handoff
                              ↓
Phase 2 · implementation (steps 7–9, only after your explicit go-ahead)
7 claim (worktree `issue-<N>`) → 8 implement (`spec-check --base` each round) → 9 gate / merge / backfill
```

| The step | The seam it owns |
|---|---|
| No spec file is touched until you nod | request ↔ understanding |
| Every deliverable passes a gate of its own | one deliverable ↔ the next |
| The agent may not produce a review verdict on its own behalf | the agent ↔ its checker |
| Claiming an issue means creating a worktree named after it | one agent ↔ another |
| An issue anchors a permanent link to the merged spec | last month ↔ today |

<!-- s:self-review -->
## The one rule worth stealing: a subagent is not a second opinion

Everything the agent spawns is still the agent — same task, same prompt, same framing, chosen by the party that wants the green light. A subagent's conclusion weighs exactly as much as the agent's own. No more.

So spec-flow forbids the agent from producing a review verdict on its own behalf: the review level is yours to pick, and it may not dispatch a reviewer to do the judging for it. When a step genuinely needs an opinion that isn't the agent's, the step stops and waits for a human.

<!-- s:scars -->
## Where the rules came from

Not from theory. Each rule is the residue of a specific failure, with its date and numbers in [`references/rationale.md`](references/rationale.md). Three of the cases:

- **A criterion was widened and nothing else moved.** An IDC rule went from "CIDR ranges" to "CIDR ∪ ASN". Only that sentence changed — while the mechanism, the implementation, the steps and the acceptance criteria all still described the old behaviour, as did the parent document's overview. Building from that spec would have shipped CIDR-only. → **R1**: change a criterion, sync every place it lands.
- **Two agents claimed the same issue.** Both read *open* as "nobody is working on this" and both did the work. One was wasted. → **R7**: the claim is the worktree being created, not the issue's state.
- **One spec, seventeen rewrites.** 448 to 762 lines over 17 commits, 14 of them changing its body. Its owner finally interrupted the agent mid-task: *"this is a new requirement — write a new spec, stop editing that one."* → **R12**: editing a merged spec is a card you answer, not a judgement call.

The other 33 are in the same file, each with its date, measurement, decision, cost and verification limits.

<!-- s:longrun -->
## Why it survives long work

**State lives in git, not in the agent's head.**

| To know | It's written in | Why you can trust it |
|---|---|---|
| Who is working on it | the worktree name — the lock itself | Creating `issue-42` succeeds = nobody has it; refused = somebody does. No separate assignment board to fall out of sync. |
| How far along it is | the issue's state and the pull request | Same answer across sessions, machines and people. |
| Why it was built that way | the spec in `docs/specs/`, linked from the issue | It passed the gate, it's in prose, and it's versioned with the code — diffable, blamable, revertable. |

Tools that keep this in their own private index drift without telling you. This one can't: git says so, loudly, the moment it happens.

<!-- s:limits -->
## What it doesn't do

- **It doesn't remember the process.** What was tried and abandoned, which dead end cost an hour — if it wasn't written down, it's gone. One part does get written down: the review trail, every finding and how it was disposed of, appended to the spec.
- **It isn't a runtime.** Nothing here schedules an agent, checkpoints a run, or resumes one that died at 3am. It assumes you are there for the gate.
- **Most of it isn't enforced.** These are rules the agent is asked to follow, not mechanisms that force it — including the independent merge confirmation. What is enforced comes from git (the worktree lock) and this repo's own check script.
- **It assumes GitHub.** Issues and pull requests are load-bearing, not decoration.

<!-- s:install -->
## Install

```bash
# install directly
git clone https://github.com/nano-sun99/spec-flow.git ~/.claude/skills/spec-flow

# or keep it elsewhere and symlink it in
git clone https://github.com/nano-sun99/spec-flow.git ~/code/spec-flow
ln -s ~/code/spec-flow ~/.claude/skills/spec-flow
```

That's the skill installation, not project adoption. Claude Code loads personal skills from `~/.claude/skills/<name>/SKILL.md`; update that checkout with `git pull`. Other clients use their own skill discovery paths.

The scripts live inside the skill: `~/.claude/skills/spec-flow/scripts/spec-check.py`; run it with `python3` from the repo you are checking.

Requirements: an agent that discovers skills, runs shell commands (`git worktree`) and opens PRs (`gh`). A passing document check does not prove a client loaded or followed the rules.

<!-- s:usage -->
## Using it

- **Trigger it** by describing work that deserves designing — "this touches the API, the DB and the frontend" — or invoke it by name.
- **Enter from the middle:** "do #12" starts phase 2 for that issue, with the same gate and its own merge confirmation. Right after a single `SPEC_READY` handoff in the same window, "start implementation" continues it; a new window, another agent or several unauthorized handoffs require the issue number.
- **Splitting** is a card after the skeleton: smaller execution specs, each with its own execution issue, plus one tracking-only parent issue. Not splitting keeps one spec and one issue. The mechanics are in a scenario pack.
- **Adopt it** by saying "apply spec-flow to this project": it writes a pointer in `AGENTS.md` and does not copy the body. "Update this project's spec-flow integration" upgrades an old entry idempotently and does not enable unadopted options. Projects that adopted ADR rules search and record them by their own conditions, and check the outcome at close-out.
- **Code mapping is off by default.** Ordinary work does not query the map or repair its configuration; read the [code-map notes](references/code-map.md) only when you explicitly ask for a trial or a restoration.

The currently approved spec must be read before implementation.

<!-- s:evidence -->
## This repo is its own case study

spec-flow is developed with spec-flow. **101 merged PRs, 33 issues, 30 specs** — numbers you can recompute rather than a snapshot to be trusted: `gh pr list --state merged --limit 500 | wc -l`, `ls docs/specs/*.md | wc -l`.

The 2026-11-04 slimming went through the same two phases: one heavy review round found 1 blocking and 11 high findings, all fixed; the default surface went 2,945 → 137 lines, `SKILL.md` 118 → 60, plus two scripts. What shrank is what you read by default, not what is covered.

Rules are cited by `R` number, like `（依据：rationale R12）`, and all 37 live in [`references/rationale.md`](references/rationale.md): date, measurement, decision, cost and verification limits, plus the full cases — including the IDC criterion widened in one place while four others and the parent document stayed stale, and the completion contract that stops "no bugs" from meaning "we promise nothing will ever break".

<!-- s:docs -->
## Files

| Layer | File | What's in it |
|---|---|---|
| Body | `SKILL.md` | The workflow itself — the file the agent loads |
| Repo | `AGENTS.md` / `CLAUDE.md` | Maintenance rules; `CLAUDE.md` is one line: `@AGENTS.md` |
| Default | `references/one-page.md` | The start page: three-line anchor, scope, AC table, four choices, change request |
| Default | `references/gates.md` | Three gates, the seven-point DoR, four-in three-out review, the four levels |
| Default | `references/project-integration.md` | PR / issue / worktree / backfill; project rules only by pointer |
| Pack | `references/one-path.md` | Route template, plan page, walking review, batch table, the eight cards |
| Pack | `references/gate-details.md` | How the four review levels differ, stacking, doc-check red/green |
| Pack | `references/spec-maturity.md` | The three spec stages and the DoR in detail |
| Pack | `references/split-large-spec.md` | Split assessment, stable IDs, parent/child issues, dependencies, batches |
| Pack | `references/phase-handoff.md` | Handoff state, implementation authorization, takeover, the handoff block |
| Pack | `references/done-criteria.md` | Done criteria, observational close-outs, the three exceptions |
| Pack | `references/spec-revision-sync.md` | Changing one clause means syncing every place it lands |
| Pack | `references/worktree-lock.md` | The worktree lock, and how it breaks |
| Pack | `references/apply-to-project.md` | Applying, explicit upgrades, pointer templates, asset boundaries |
| Pack | `references/adoption-model.md` | The adoption model, explained historically; adds no obligations |
| Optional | `references/adr-decision-records.md` | Architecture decision records (ADR) |
| Optional | `references/documentation-lifecycle.md` | How specs, ADRs and issues divide the work |
| Optional | `references/issue-status-labels.md` | Issue status labels |
| Optional | `references/issue-type-labels.md` | Issue type labels |
| Optional | `references/release-discipline.md` | Release loop: release record, readiness, mainline alignment, post-release backfill |
| Archived | `references/code-map.md` | Disabled; read only for an explicit trial or restoration |
| On demand | `references/rationale.md` | Why each rule exists: cases, measurements, decisions (R1–R37) |
| Script | `scripts/spec-check.py` | One-page / scope / AC / placeholders / scope creep: E1–E5, W1–W2 |
| Script | `scripts/replay-legacy-spec.py` | Maps an old-format spec to a start page + AC table and replays `spec-check` |
| Script | `scripts/check-docs.sh` | Budgets, paths, bilingual sync, adoption contract |
| Repo | `docs/maintainer-notes.md` | How this checkout is wired, and why the earliest commits were rebuilt |

Optional files are off by default and are read only when a project's rules declare them adopted. The workflow body is `SKILL.md` — where this README and `SKILL.md` disagree, `SKILL.md` wins.

<!-- s:contributing -->
## Contributing

Small steps. Open an issue, or just send a PR. One convention: if a change adds or alters a rule, record the case behind it in `references/rationale.md` under a new `R` number — the rules here have to point at something that happened.

<!-- s:license -->
## License

MIT — see [LICENSE](LICENSE).
