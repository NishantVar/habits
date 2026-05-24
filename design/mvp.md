---
tags: [design, habits, mvp]
date_created: 2026-05-23
date_updated: 2026-05-23
status: draft
---

# Habits MVP

## Correction

<!-- node:deci-mvp-shape -->
The MVP cannot stop at a design-only initializer.

The first version must let someone create a real Habit, run it through a
common substrate, recover from failures through structured guidance, and
manually trigger improvement when the Habit proves incomplete or wrong.

The first version can be simple. It can require manual review before changing
itself. But recovery and self-evolution must be wired into the shape from day
one, because those are part of what makes a Habit different from a static
skill.
<!-- /node:deci-mvp-shape -->

## Decision

<!-- node:deci-lifecycle-commands -->
The MVP should provide the smallest complete Habit lifecycle:

```text
habit init <name>          # create guided design workspace
habit materialize <name>   # produce first runnable Habit version
habit next <name>          # return the next instruction packet
habit record <name>        # record evidence, outcome, or failure
habit recover <name>       # turn a failure into structured recovery guidance
habit evolve <name>        # manually propose improvements from ledger history
```

This is still not "convert any skill into a Habit." That remains later. But
the MVP must prove the full loop for a new Habit built from scratch.
<!-- /node:deci-lifecycle-commands -->

## Human-Learning Analogy

A human habit does not appear fully formed. The progression is:

1. conscious skill definition
2. repeated execution
3. failure and correction
4. refinement of the routine
5. more automatic execution next time

The product should mirror that:

1. `habit init` captures the conscious routine.
2. `habit materialize` turns it into a first executable routine.
3. `habit next` and `habit record` run the routine and collect experience.
4. `habit recover` handles breakdowns without dumping ambiguity back on the
   agent.
5. `habit evolve` uses recorded experience to propose an improved version.

<!-- node:deci-manual-evolution -->
The MVP does not need autonomous self-modification. It needs manual,
reviewable self-evolution: the user can tell the Habit to fix itself, review
the proposed change, then accept or reject it.
<!-- /node:deci-manual-evolution -->

## Core Split

<!-- node:deci-core-split -->
Habits have two layers:

```text
common substrate
habit-specific contract
```

The **common substrate** is system-owned machinery shared by all Habits:

- lifecycle commands
- contract validation
- state and ledger storage
- structured instruction packet schema
- structured handoff and recovery schema
- run history and failure capture
- test harness conventions
- manual evolution proposal workflow

The **habit-specific contract** is user-owned definition:

- the repeated routine
- inputs and parameters
- state and evidence fields
- gates and risk boundaries
- failure cases and recovery guidance
- references
- what remains agent judgment
- optional deterministic helper code
<!-- /node:deci-core-split -->

<!-- node:amb-contract-format -->
The user-owned contract does not have to be only JSON. It can include Markdown,
YAML, Glyph, Python adapters, or other code. The important boundary is
ownership: the user defines this Habit; the system provides the shared
machinery all Habits use.
<!-- /node:amb-contract-format -->

## MVP Scope

<!-- node:deci-mvp-scope-boundaries -->
In scope:

- guided initialization from scratch
- first runnable Habit materialization
- a minimal runtime loop
- a minimal ledger
- structured recovery handoffs
- manual self-evolution proposals
- a simple test harness
- one canonical example: a `p2p` Habit

Out of scope:

- automatic conversion of existing skills
- fully autonomous self-modification
- complex state-machine compilation
- trace mining across many projects
- DSPy or model-judgment nodes
- plugin marketplace packaging
- general-purpose arbitrary scripting

Existing skills still matter. A user can feed `p2p`, `tfork`, or another skill as
source context while designing a new Habit. The MVP does not need a separate
`import-skill` converter yet.
<!-- /node:deci-mvp-scope-boundaries -->

## Lifecycle

### 1. Initialize

`habit init <name>` creates the design and contract workspace:

```text
habits/<name>/
  habit.yaml
  habit.md
  contract/
    routine.md
    ownership.md
    state.md
    gates.md
    handoffs.md
    recovery.md
    evolution.md
    references.md
    tests.md
    open-questions.md
```

<!-- node:amb-init-interactive -->
The generated files contain the guided questions. The MVP does not need a
fully interactive interview; files are enough if they are clear and complete.
<!-- /node:amb-init-interactive -->

### 2. Materialize

`habit materialize <name>` turns the contract into a first runnable version:

```text
habits/<name>/
  SKILL.md
  habit.yaml
  machine/
    routine.yaml
    ledger.schema.yaml
    advice.schema.yaml
    recovery.schema.yaml
  references/
  tests/
    test_contract.py
    test_recovery.py
    test_evolution.py
```

<!-- node:amb-materializer-scope -->
The first materializer can be simple. It can translate a constrained contract
format into YAML files and test stubs. It does not need to support arbitrary
logic or compilation from Glyph.
<!-- /node:amb-materializer-scope -->

### 3. Run

`habit next <name>` reads the current ledger and returns one structured
instruction packet:

```yaml
ok: true
habit: p2p
phase: ensure_registered
code: needs_self_registration
agent_instruction: "Register this agent with a stable snake_case name before sending or listing peers."
ok_to_act: false
record_after: self_registration
```

`habit record <name>` appends evidence or outcomes to the ledger:

```text
habit record p2p --event self_registration --data '<json>'
habit record p2p --event peer_resolution --data '<json>'
habit record p2p --event failure --data '<json>'
```

The runtime loop can be deliberately basic: ordered phases, required evidence,
and gates. That is enough to prove the common substrate.

### 4. Recover

`habit recover <name>` is the first wired-in recovery mechanism. It reads the
latest failure event and returns a structured handoff:

```yaml
ok: false
code: surface_resolution_failed
human_message: "The Habit could not resolve the caller's terminal surface."
agent_instruction: "Do not retry verbatim. Ask the user to provide the surface ref or set AGENT_MSG_SURFACE_ID, then retry once."
retryable: true
suggested_next_command: "AGENT_MSG_SURFACE_ID=surface:N habit next p2p"
record_after: recovery_attempt
```

<!-- node:risk-recovery-coverage -->
The first recovery system does not need to repair every issue automatically.
It needs to stop failures from becoming vague prose. Every recoverable failure
should produce a specific instruction, retry policy, and record event.
<!-- /node:risk-recovery-coverage -->

### 5. Evolve

`habit evolve <name>` is the first manual self-evolution mechanism.

It reads the ledger and produces a reviewable improvement proposal:

```text
habits/<name>/evolution/proposals/2026-05-23-surface-resolution.md
```

The proposal should include:

- repeated failure or friction observed
- affected contract files
- proposed change
- risk level
- tests that should be added or updated
- exact patch if safe to generate
- review checklist

<!-- node:amb-evolution-apply -->
The user must approve before the Habit changes. For the MVP, applying the
change can be manual. The important part is that the loop exists:

```text
run -> fail -> recover -> record -> evolve -> review -> improve
```
<!-- /node:amb-evolution-apply -->

## Canonical Example: p2p

<!-- node:deci-canonical-example -->
The canonical MVP Habit should be `p2p`: peer-to-peer messaging between agents
running in cmux.

`p2p` is a strong candidate because it is already trying to become habitual:

- the agent should not remember the full protocol every time
- identity and peer routing need durable state
- transport details are deterministic and fragile
- failures need structured recovery, not vague prose
- repeated routing problems can teach the Habit how to improve
- the workflow naturally separates common substrate from habit-specific
  contract

In Habit terms, `p2p` would produce:

- routine: ensure this agent is registered, classify the requested messaging
  action, resolve peers, deliver messages, and record what happened.
- state: this agent's identity, known peer manifests, recent routing attempts,
  sent-message events, incoming bootstrap events, and recovery attempts.
- gates: self must be registered before sending; peer must resolve before
  delivery; stale manifests must be swept before trusting registry state;
  outgoing prose messages must carry a `[from: <name>]` prefix.
- recovery: unsupported terminal, own surface unresolved, name collision, peer
  not found, stale peer surface, bootstrap parse failure, send-buffer failure.
- evolution: if repeated recovery events show the same friction, write a
  proposal to improve the contract, recovery guidance, tests, or helper code.
<!-- /node:deci-canonical-example -->

<!-- node:deci-p2p-slice -->
The first p2p Habit does not need every current p2p feature. The MVP slice
is **registered-peer messaging only**:

1. register or confirm this agent's identity
2. list known live peers
3. send a message to a registered peer
4. recover cleanly when the peer or own surface cannot be resolved
5. generate an evolution proposal from repeated recovery events

Connect-to-existing-peer and spawn-new-peer are the next layer. They are
important, but the first slice should prove the Habit substrate without
depending on fork-terminal or multi-agent bootstrap timing.
<!-- /node:deci-p2p-slice -->

<!-- node:risk-habituation-unproven -->
The main thing to learn from this MVP is whether habituation works in practice:
use the p2p Habit across real cases, record friction and recoveries, then run
`habit evolve p2p` to see whether the system can produce useful reviewable
improvement proposals.
<!-- /node:risk-habituation-unproven -->

## Success Criteria

<!-- node:deci-success-criteria -->
The MVP is successful when:

- A user can initialize a new Habit from scratch.
- The user can fill in enough contract files to create a first runnable Habit.
- The system can materialize that contract into a runnable Habit bundle.
- The runtime can return next-step instruction packets.
- The runtime can record evidence and failures.
- The recovery command can turn a failure into structured guidance.
- The evolution command can produce a manual improvement proposal from ledger
  history.
- The whole loop is testable on the p2p canonical example.
<!-- /node:deci-success-criteria -->

## Implementation Order

<!-- node:deci-impl-order -->
1. Define the common substrate schemas: manifest, advice packet, ledger event,
   recovery handoff, evolution proposal.
2. Build `habit init` to generate the contract workspace.
3. Build `habit materialize` for a constrained first contract shape.
4. Build `habit next` and `habit record` around ordered phases and required
   evidence.
5. Build `habit recover` from recorded failure events.
6. Build `habit evolve` to write reviewable proposal files.
7. Add the p2p canonical example and tests.
<!-- /node:deci-impl-order -->

## Deferred

- Fully automatic conversion from existing skills.
- Autonomous self-modification without user review.
- Rich state-machine language.
- Cross-Habit trace mining.
- Model-judgment nodes.
- Habit packaging and distribution.
