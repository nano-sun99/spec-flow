<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo/spec-flow-lockup-dark.svg">
    <img alt="spec-flow" src="assets/logo/spec-flow-lockup.svg" width="480">
  </picture>
</p>

**A decision environment for AI coding agents — not a process compiler.** Agree on goals, scope and acceptance, then implement and deliver under explicit delegation. Hard gates stay strict; paths inside them stay flexible.

There is no runtime or service: these are Markdown rules an agent reads. Spec-driven work preserves an approved specification, an execution issue and traceable sources. Direct implementation skips the spec phase without skipping delivery or merge gates. Code mapping stays off by default; source code, real diffs and relevant tests establish impact.

[`SKILL.md`](SKILL.md) is the single entry point (under 2,600 body chars), backed by a compact always-read core (L0–L2, ≤ 15,500 chars), two on-demand governance specs, nine playbooks and a 15-case library. [`scripts/check-docs.sh`](scripts/check-docs.sh) enforces per-file, always-read and repo-wide active-rule (≤ 46,000 chars) budgets, single-line length caps, link/anchor integrity and bilingual README sync. Legacy v1 documents are archived in `docs/archive/v1/`.

**English** · [中文](README.zh-CN.md)

<!-- s:shape -->
## What using it looks like

With a request like “add avatar uploads,” an agent without shared understanding can deliver an unwanted table and invented size limits.

`spec-flow` checks existing facts first and asks only about gaps affecting scope, acceptance or authorization. Clear, small changes can go straight to direct implementation after stating the change surface. Complex requests clarify against real project facts and record decisions with verifiable sources.

When a spec is needed, the outline, design comparison and final draft stay in one document and one PR. Pages wait for user designs; non-UI work uses verifiable inputs, outputs and a falsifiable business example. Review choices, revisions, merging and implementation delegation are separate user decisions.

<!-- s:problem -->
## The problem

Failures happen at seams: unconfirmed understanding, duplicate claims on the same issue, review mistaken for merge approval, conflicting copies of the same decision across documents, or merged code declared “done” while docs or deployment are missing.

The answer is not more ceremony inside every step. It is a **single canonical owner** for every rule, decision, deliverable and piece of evidence: investigate facts first and stop only where the user must decide.

<!-- s:scars -->
## Where the rules came from

Real incidents are preserved in [`references/40-cases/`](references/40-cases/) (narrative + proposals, never authority on their own):

- **Criterion drift**: expanding an IDC rule to CIDR ∪ ASN while implementation and parent docs stayed stale → single-owner replacement protocol and dual scans.
- **Claim race**: two agents reading an `open` issue as unclaimed → real claim is Git creating the isolated `issue/<N>` worktree.
- **Review scope explosion**: six review rounds adding rules that contradicted each other → cause classification, “can we cut instead of adding rules?”, and a strict R1–R3 cap.
- **Merged-spec edits**: 17 commits rewriting a merged spec body → merged specs freeze; scope changes open a new spec via D3.
- **No delegation**: starting implementation right after spec merge without explicit authorization → explicit D0 delegation gate.

<!-- s:what -->
## How it solves them

Externally still **two phases** (Design & Implementation); internally structured in **clean layers**:

- **Always-read core**: L0 Constitution (8 iron rules) → L1 Stage Contracts & Records (4 stages, anti-entropy 3 questions & as-built sync, 15 record groups) → L2 Decision Catalog (D0–D7 hard gates + interaction card contract).
- **On-demand governance specs**: Spec Governance (streamlined base + 3 fact-triggered governance components & smooth mid-review escalation) & Review Contract (tiers, R1–R3 rounds, #158 mechanisms, Lane A/B prompts).
- **On-demand playbooks & cases**: 9 concise playbooks under [`references/30-playbooks/`](references/30-playbooks/) and 15 cases under [`references/40-cases/`](references/40-cases/).

See [`references/README.md`](references/README.md) for the full file map.

<!-- s:self-review -->
## The one rule worth stealing: a subagent is not a second opinion

A spawned subagent is still the main agent's execution delegate. Changing models, names or prompts does not make its opinion independent; self-testing and drafting never substitute for review.

The user chooses whether and how to review each deliverable (none / light / heavy / heavy+mutation). Where another party must truly decide, prepare the evidence and stop for that party. Markdown rules are not platform access control.

<!-- s:smooth -->
## Why it doesn't feel heavy

Decisions use the client's choice tool (or equivalent explicit text options) with facts, differences and a recommendation. Only 8 fixed decision types (D0–D7) plus irreversible actions (L0-1) and load-bearing gaps (L0-7) stop the agent; non-load-bearing methods are chosen autonomously and reported.

Specs start from one streamlined base (4-column decision table + three anti-entropy questions: overlap audit, subtraction list, as-built doc target); heavy governance (cross-cutting inventory tables, multi-doc/view audits, replacement manifests) activates only on objective facts and escalates smoothly in place if scope grows mid-review. Direct fixes skip the three questions and incur zero extra doc tax unless external behavior, commands, architecture, interfaces or READMEs change.

<!-- s:longrun -->
## Why it survives long work

Git holds the claim lock (`issue/<N>` worktree); the issue handoff holds current phase and all merged PR sources; the frozen spec holds approved scope; append-only records hold D0–D7 approvals. A new session never relies on private chat memory to guess what shipped or who owns the work.

<!-- s:limits -->
## What it doesn't do

- It does not schedule agents, auto-resume sessions or provide platform permission isolation.
- It does not promise zero future bugs; “done” means agreed deliverables exist, required checks pass, no known blockers remain and evidence is verifiable.
- It does not equate a merged PR, label or tag with verified production deployment.
- It does not silently install external skills, create long-lived branches, CI/hooks or release platforms; issue/PR workflows assume GitHub.

<!-- s:install -->
## Install

```bash
git clone https://github.com/nano-sun99/spec-flow.git ~/.claude/skills/spec-flow
```

Or clone into a workspace directory and symlink it into your client's skill path. `spec-flow` handles clarification natively using your client's choice tool or text options — no external clarification skills required. For project adoption, see [`references/50-adapters/README.md`](references/50-adapters/README.md).

<!-- s:usage -->
## Using it

Describe a request or invoke `spec-flow`. For an existing issue, say “do #12.” Follow [`references/20-decisions.md`](references/20-decisions.md) for delegation evidence and interaction cards.

Say “apply spec-flow to this project” to adopt (or “update this project's spec-flow integration” for an explicit upgrade). Adoption writes only pointer-only references — never copies workflow rules or turns on optional modules unasked.

The five optional modules (`adr`, `doc-lifecycle`, `issue-status`, `issue-type`, `release`) remain **off by default**. `release` covers Git branching shapes (single-mainline, three-layer, staging-line), release safety invariants, batch fixes and production incidents together.

<!-- s:evidence -->
## This repo is its own case study

Specifications, change manifests, behavioral evals, cases and verification scripts live in this repository. Static green is necessary, never sufficient for client or production verification: `scripts/check-docs.sh` guards budgets, single-line limits, links/anchors and bilingual sync; `scripts/check-change.py` (with `scripts/test-check-change.py`) validates replacement change manifests across this repo and external projects (`--root <project>`); `evals/` and `scripts/run-eval.py` (with `scripts/test-run-eval.py`) run CLI-agnostic behavioral guardrail and anti-bloat regressions against saved baselines.

<!-- s:docs -->
## Files

| File / Directory | Responsibility |
|---|---|
| `SKILL.md` | Single entry point, execution loop, 1-hop navigation and exception protocol |
| `AGENTS.md`, `CLAUDE.md` | Repository maintenance rules; `CLAUDE.md` imports `AGENTS.md` |
| `references/README.md` | Layer overview and reading-order map |
| `references/00-constitution.md` | L0: 8 iron rules (user-only edits via L0-8) |
| `references/10-stages.md` | L1: 4 stage contracts, core glossary (incl. anti-entropy 3 questions & as-built sync) and delivery preconditions |
| `references/15-records.md` | L1: 15 record groups, D0–D7 logs, document carriers, close-out and exceptions |
| `references/20-decisions.md` | L2: D0–D7 hard gates, interaction card contract and label confirmations |
| `references/25-spec-governance.md` | Sole owner for streamlined base, 3 fact-triggered governance components, view authority and smooth mid-review escalation |
| `references/26-review-contract.md` | Sole owner for review tiers, R1–R3 rounds, #158 mechanisms, doc checks and Lane A/B prompts |
| `references/30-playbooks/` | 9 on-demand playbooks (`new-spec`, `direct`, `issue`, `change-protocol`, `release`, `incident`, `labels`, `worktree`, `adr`) |
| `references/40-cases/` | L4: 15 incident & drill cases (narrative + proposals, not authority) |
| `references/50-adapters/` | Self-contained pointer-only adoption contract and 5 optional modules |
| `evals/` | Behavioral Eval regression suite (`evals/README.md`, self-contained JSON `scenarios/`, sanitized `baselines/`) |
| `docs/archive/v1/` | Archived v1 documents & frozen `rationale.md` (historical reference only) |
| `docs/maintainer-notes.md` | Local symlink wiring and repo history |
| `scripts/check-docs.sh` | Guards per-file, always-read and repo-wide rule budgets, single-line caps, links/anchors, owners and bilingual README sync |
| `scripts/check-change.py` | Portable v2 thin-manifest + auto-diff validator (`schema: 2`, `--root`, `--draft`, manifest-only head pinning) |
| `scripts/run-eval.py` | CLI-agnostic behavioral Eval runner (`--validate`, `--materialize`, `--run`, `--grade`, `--baseline`; tested by `scripts/test-run-eval.py`) |

The README introduces the system; follow `SKILL.md` to each sole canonical owner.

<!-- s:contributing -->
## Contributing

Open an issue or PR. Keep every rule in one canonical owner, record new lessons in `references/40-cases/`, run `scripts/check-change.py` for replacement changes, update both READMEs together, and pass `bash scripts/check-docs.sh`.

<!-- s:license -->
## License

MIT — see [LICENSE](LICENSE).
