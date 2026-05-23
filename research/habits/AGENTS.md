---
tags: [research, habits, executable-skills]
date_created: 2026-05-19
date_updated: 2026-05-23
status: active
---

# Habits

This topic is part of the **Athena** tiered research wiki. Findings flow
`unconfirmed/` -> `confirmed/` -> `consolidated/` with increasing trust.
Reading `confirmed/` and `consolidated/` directly is fine; `unconfirmed/`
content should be read via a subagent.

## Research Question

How should coding-agent **Habits** combine skill-like prose instructions,
scripts, state, and structured handoffs so complex workflows can run in a
subconscious or automatic mode without removing the agent's judgment?

## Key Questions

- What should the runtime own versus what should the agent own?
- What should the command or API contract look like?
- How should failure scenarios yield structured guidance back to the agent?
- How should this pattern be packaged as a reusable Habit?

## Decision Context

The initial use case is a complex coding-agent skill such as agent messaging,
where prose-only instructions leave too much fragile protocol execution in the
agent's hands. The pattern is now named **Habits**: skills that have been
proceduralized into executable, stateful workflows, analogous to human
procedural memory or muscle memory.

The former working name was **Executable Skills**.

## Tiers

- [unconfirmed/](unconfirmed/) — raw findings, possibly wrong
- [confirmed/](confirmed/) — user-verified findings
- [consolidated/](consolidated/) — synthesised wiki pages

## Prototype

- [prototype/](prototype/) — early runtime and systematic debugging Habit prototype files

## See also

- [log.md](log.md) — chronological audit trail of every ingest, promotion, and move
