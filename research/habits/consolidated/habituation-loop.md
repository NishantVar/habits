---
tags: [research, habits, consolidated, habituation, procedural-memory]
date_created: 2026-05-23
date_updated: 2026-05-23
sources: 1
status: design-seed
---

# Habituation Loop

## Summary

**Habituation** is the process by which repeated skill executions become
encoded into a **Habit**. A skill starts as conscious agent effort: visible
instructions, manual judgment, explicit imports, and repeated operational
steps. Over time, successful repetitions and recurring failures are mined from
run traces, consolidated into executable behavior, and hidden behind a leaner
agent-facing interface.

The guiding law:

> Unless manual effort is required, that instruction is not seen.

This is the human counterpart to learning an action like brushing teeth. At
first, attention is required. With repetition, the sequence becomes procedural
memory: the action runs automatically until judgment, adaptation, or exception
handling is needed.

## Core Idea

A Habit should not casually rewrite itself after every run. Every run should
produce material that can later be consolidated into the Habit.

The runtime records what happened. A consolidation process looks across many
runs and asks:

- What repeated?
- What failed?
- What did the agent keep needing to remember?
- Which imports or references were repeatedly useful?
- Where did the human need to intervene?
- Which recovery path solved the issue reliably?

Stable answers become candidate Habit improvements. Risky or ambiguous
answers remain visible to the agent or require human approval.

## Learning Progression

1. **Conscious execution**
   The agent reads more instructions, chooses steps, loads references, and
   performs more manual coordination.

2. **Repeated execution**
   The ledger accumulates traces across successful and failed runs.

3. **Pattern discovery**
   A trace miner identifies repeated action sequences, common imports,
   recurring failure modes, and repeated user interventions.

4. **Consolidation**
   Repeated patterns become candidate runtime gates, advice packets,
   references, schemas, or conditional imports.

5. **Proceduralization**
   Approved changes move out of the visible instruction surface and into the
   Habit runtime, state machine, ledger schema, or on-demand references.

6. **Lean execution**
   The agent-facing instruction remains small: call the Habit, obey the
   returned packet, load references only when asked, and use judgment when the
   runtime yields.

## Architecture Components

### Habit Ledger

The Habit Ledger records each run:

- inputs and environment
- runtime state transitions
- advice packets returned
- references and imports loaded
- commands or tools used
- failures, bypasses, and recovery paths
- user interventions
- verification evidence
- final outcome

The ledger is not just audit history. It is the raw material for future Habit
consolidation.

### Trace Miner

The Trace Miner analyzes ledgers across runs. Its job is to identify repeated
structure, not to make final design decisions.

Candidate findings:

- a repeated command sequence should become a runtime action
- a recurring issue should become a gate
- a repeated explanatory note should become a reference
- a frequently useful import should become conditional loading logic
- repeated human intervention should remain visible as a judgment point
- repeated bypasses may indicate the Habit is overconstrained or missing an
  exception path

### Consolidation Pass

The consolidation pass converts mined patterns into candidate changes:

- new runtime gate
- new advice packet
- new ledger field
- new state transition
- new reference file
- new conditional import
- shorter `SKILL.md` instruction
- stricter verification requirement
- explicit human-judgment handoff

This is the Habit equivalent of memory consolidation. It turns repeated
experience into more reliable automatic behavior.

### Promotion Gate

Not every observation should become doctrine. Promotion should require enough
confidence for the risk involved.

Low-risk candidates can be promoted automatically when repeated enough:

- frequently loaded reference
- clearer wording
- common command suggestion
- new diagnostic field

Higher-risk candidates should require human approval:

- new blocking gate
- new permission or tool behavior
- change to fix authorization
- removal of visible instruction
- new default recovery strategy

The promotion gate prevents the Habit from overfitting to a few unusual runs.

## Design Principle

The visible interface should shrink as the Habit matures.

The agent should see:

```text
call Habit -> obey packet -> record evidence -> repeat
```

The agent should not see stable procedural mechanics unless they require
manual judgment. Reliable behavior belongs in the runtime, ledger, gates,
schemas, references, and conditional imports.

The agent's conscious context should be reserved for:

- ambiguity
- taste
- tradeoffs
- exception handling
- user interaction
- architecture judgment
- recovery choices when the runtime yields

## Relationship To Habits

Habits are proceduralized skills. Habituation is how they become procedural.

The core split remains:

- The **Habit Runtime** owns deterministic and repeated behavior.
- The **Habit Ledger** records experience.
- The **Trace Miner** discovers repeated patterns.
- The **Consolidation Pass** proposes codification.
- The **Promotion Gate** controls what becomes part of the Habit.
- The **agent** owns judgment, ambiguity, and conscious intervention.

## Open Questions

- Should habituation run after every execution, nightly, or only when manually
  triggered?
- What confidence threshold is enough for automatic promotion?
- How should the system distinguish a useful repeated pattern from accidental
  overfitting?
- Should each Habit maintain its own miner, or should there be a generic miner
  for all Habits?
- How should conflicting patterns from different projects or users be handled?
- Should rejected consolidation candidates remain in the ledger for future
  reconsideration?

