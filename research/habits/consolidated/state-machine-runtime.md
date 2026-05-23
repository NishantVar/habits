---
tags: [research, habits, executable-skills, consolidated, glyph, state-machines]
date_created: 2026-05-21
date_updated: 2026-05-23
sources: 1
---

# State-Machine Habits

## Summary

Habits should compile into a **Habit bundle**, not only an agent-facing `SKILL.md`. The `SKILL.md` should stay small because it is for the agent's attention: call the controller, follow the returned packet, record evidence, and do not bypass gates. The machine-facing material should live in sidecar files: a manifest, schemas, a normalized state machine, references, and a reusable generic runtime.

The preferred implementation direction is a **generic runtime** that interprets compiled state-machine contracts. Individual Habits should not generate bespoke controller scripts unless they need domain-specific probes. A state-machine-driven Habit should author behavior once in Glyph-like source, then compile to a portable contract consumed by the generic runtime.

The former working name for this pattern was **Executable Skills**.

## Core Design

The split remains:

- The **runtime** owns state lookup, validation, gate evaluation, response shaping, command routing, retries, and failure classification.
- The **agent** owns intent, ambiguity, user interaction, code interpretation, architecture judgment, and recovery choices when the runtime yields back.

For protocol-heavy skills, the agent should not remember a long checklist from prose. It should repeatedly ask the runtime what to do next. The runtime returns one small, contextual instruction packet. This is the agent equivalent of procedural memory: the workflow runs in a low-attention automatic mode until judgment is needed.

## Bundle Shape

```text
systematic-debugging/
  SKILL.md
  habit.json
  machine/
    state-machine.json
    ledger.schema.json
    advice.schema.json
    references.json
  references/
    root-cause-tracing.md
    condition-based-waiting.md
    defense-in-depth.md
```

There is no skill-specific `debugctl.py` in the preferred design. Instead, the manifest points at a generic runtime command:

```text
habitctl next --contract habit.json --scope .
habitctl record --contract habit.json --event evidence --data '<json>'
habitctl reset --contract habit.json
```

The runtime can be provided by the agent environment, plugin, or package manager. The Habit bundle provides declarative machine contracts.

## Speculative Glyph Source Shape

```glyph
habit systematic_debugging(scope = ".")
    description: "Debug bugs, test failures, and unexpected behavior through an enforced root-cause workflow."
    goal: "The root cause is identified, fixed once, and verified with a failing-before/passing-after check."

    runtime habitctl
        contract: "habit.json"
        command: "habitctl next --contract {contract} --scope {scope}"
        record: "habitctl record --contract {contract} --event {event} --data {data}"
        reset: "habitctl reset --contract {contract}"
        state_path: ".agents/state/systematic-debugging.json"
        response: DebugAdvice

    response DebugAdvice
        ok: Bool
        ok_to_fix: Bool
        phase: DebugPhase
        code: DebugCode
        human_message: Text
        agent_instruction: Text
        retryable: Bool
        suggested_commands: List<Command>
        load_reference: Optional<Reference>

    enum DebugPhase
        intake
        reproduction
        evidence_collection
        root_cause_investigation
        fix_authorized
        verification
        architecture_review
        complete

    ledger DebugLedger
        full_error_output: Optional<Text>
        reproduction_command: Optional<Command>
        reproduction_result: Optional<ReproductionStatus>
        recent_changes_checked: Bool = false
        working_comparison: Optional<Text>
        root_cause_hypothesis: Optional<Text>
        failing_test_or_repro: Optional<PathOrCommand>
        fix_attempt_count: Int = 0
        last_fix_result: Optional<Text>
        symptom_class: Optional<SymptomClass>

    references:
        root_cause_tracing = "references/root-cause-tracing.md"
        condition_based_waiting = "references/condition-based-waiting.md"
        defense_in_depth = "references/defense-in-depth.md"

    state_machine debugging over DebugLedger
        initial intake

        gate missing_full_error
            when ledger.full_error_output is none
            phase evidence_collection
            block_fix
            advice:
                code: "missing_full_error"
                instruction: "Do not propose a fix yet. Run the failing command once and capture the complete error, including stack trace and line numbers."

        gate missing_reproduction
            when ledger.reproduction_result is none
            phase reproduction
            block_fix
            advice:
                code: "missing_reproduction"
                instruction: "Reproduce the failure consistently. Record the exact command, environment, and observed output."

        gate recent_changes_unchecked
            when ledger.recent_changes_checked == false
            phase evidence_collection
            block_fix
            advice:
                code: "recent_changes_unchecked"
                instruction: "Inspect local diffs and recent commits before forming a fix hypothesis."

        gate needs_root_cause_tracing
            when ledger.symptom_class == "deep_stack" or ledger.root_cause_hypothesis is none
            phase root_cause_investigation
            block_fix
            load_reference root_cause_tracing
            advice:
                code: "needs_root_cause_tracing"
                instruction: "Use root-cause tracing. Identify the immediate cause, then walk backward through callers until you find the original trigger."

        gate missing_failing_artifact
            when ledger.root_cause_hypothesis exists and ledger.failing_test_or_repro is none
            phase root_cause_investigation
            block_fix
            advice:
                code: "missing_failing_artifact"
                instruction: "Create or identify a failing test, repro command, or minimal artifact that proves the hypothesis before editing production code."

        gate too_many_failed_fixes
            when ledger.fix_attempt_count >= 3
            phase architecture_review
            block_fix
            advice:
                code: "architecture_review_required"
                instruction: "Stop attempting fixes. Explain the failed attempts and discuss whether the architecture or assumption model is wrong."

        gate authorize_fix
            when ledger.root_cause_hypothesis exists
             and ledger.failing_test_or_repro exists
             and ledger.fix_attempt_count < 3
            phase fix_authorized
            allow_fix once
            advice:
                code: "fix_authorized"
                instruction: "Implement exactly one targeted fix for the recorded root cause, then run the failing artifact and relevant regression checks."

    flow:
        advice = habitctl.next(scope)
        follow(advice.agent_instruction)

        if advice.load_reference exists:
            load(advice.load_reference)

        if not advice.ok_to_fix:
            record_evidence_after_step()
            return DebugAdvice

        implement_one_root_cause_fix()
        verify_fix()
        habitctl.record_verification()
        return DebugAdvice
```

## Generated Agent-Facing SKILL.md Shape

```md
---
name: systematic-debugging
description: Debug bugs, test failures, and unexpected behavior through an enforced root-cause workflow.
habit_contract: ./habit.json
effects: [reads_files, runs_commands, writes_files]
---

## Goal

The root cause is identified, fixed once, and verified with a failing-before/passing-after check.

## Steps

1. Call the Habit runtime:

   `habitctl next --contract ./habit.json --scope {scope}`

2. Follow the returned `agent_instruction` exactly.

3. Do not propose or implement a fix unless the response includes `ok_to_fix: true`.

4. If `load_reference` is present, load only that reference before continuing.

5. After each investigation step, record new evidence through the runtime.

6. When `ok_to_fix: true`, implement exactly one targeted root-cause fix, then verify with the recorded failing artifact.

7. If the runtime returns `architecture_review_required`, stop fixing and discuss the failed attempts and architecture assumptions with the user.

## Constraints

- You must not fix before the runtime authorizes fixing.
- You must record evidence after each investigation step.
- You must stop after three failed fix attempts.
```

## Machine-Facing Manifest

```json
{
  "kind": "habit",
  "name": "systematic-debugging",
  "version": "0.1.0",
  "runtime": {
    "name": "habitctl",
    "minimum_version": "0.1.0",
    "state_path": ".agents/state/systematic-debugging.json",
    "commands": {
      "next": "habitctl next --contract habit.json --scope {scope}",
      "record": "habitctl record --contract habit.json --event {event} --data {data}",
      "reset": "habitctl reset --contract habit.json"
    }
  },
  "schemas": {
    "ledger": "./machine/ledger.schema.json",
    "advice": "./machine/advice.schema.json",
    "state_machine": "./machine/state-machine.json"
  },
  "agent_contract": {
    "must_call_runtime_first": true,
    "fix_requires_ok_to_fix": true,
    "record_evidence_after_each_step": true,
    "max_failed_fix_attempts": 3
  }
}
```

## Normalized State Machine

```json
{
  "initial_phase": "intake",
  "phases": [
    "intake",
    "reproduction",
    "evidence_collection",
    "root_cause_investigation",
    "fix_authorized",
    "verification",
    "architecture_review",
    "complete"
  ],
  "gates": [
    {
      "id": "missing_full_error",
      "phase": "evidence_collection",
      "when": { "missing": "full_error_output" },
      "ok_to_fix": false,
      "advice": {
        "code": "missing_full_error",
        "agent_instruction": "Do not propose a fix yet. Run the failing command once and capture the complete error, including stack trace and line numbers.",
        "suggested_commands": ["{failing_command} 2>&1"]
      }
    },
    {
      "id": "needs_root_cause_tracing",
      "phase": "root_cause_investigation",
      "when": {
        "any": [
          { "equals": ["symptom_class", "deep_stack"] },
          { "missing": "root_cause_hypothesis" }
        ]
      },
      "ok_to_fix": false,
      "load_reference": "references/root-cause-tracing.md",
      "advice": {
        "code": "needs_root_cause_tracing",
        "agent_instruction": "Use root-cause tracing. Identify the immediate cause, then walk backward through callers until you find the original trigger."
      }
    },
    {
      "id": "too_many_failed_fixes",
      "phase": "architecture_review",
      "when": { "gte": ["fix_attempt_count", 3] },
      "ok_to_fix": false,
      "advice": {
        "code": "architecture_review_required",
        "agent_instruction": "Stop attempting fixes. Summarize the failed attempts and discuss whether the architecture or assumptions are wrong."
      }
    },
    {
      "id": "authorize_fix",
      "phase": "fix_authorized",
      "when": {
        "all": [
          { "present": "root_cause_hypothesis" },
          { "present": "failing_test_or_repro" },
          { "lt": ["fix_attempt_count", 3] }
        ]
      },
      "ok_to_fix": true,
      "advice": {
        "code": "fix_authorized",
        "agent_instruction": "Implement exactly one targeted fix for the recorded root cause, then verify with the failing artifact."
      }
    }
  ]
}
```

## Generic Runtime Contract

The reusable runtime should behave like an interpreter for the compiled Habit contract.

Responsibilities:

- Load `habit.json`.
- Resolve schema paths and state path.
- Load or initialize the ledger.
- Validate ledger shape.
- Evaluate gates in declared order.
- Return the first matching advice packet.
- Enforce `ok_to_fix` gates.
- Accept structured `record` events from the agent.
- Increment failed fix attempts when verification fails.
- Return structured failure packets for invalid state, invalid events, missing contracts, malformed JSON, or unsupported runtime versions.

Example runtime loop:

```text
agent reads SKILL.md
agent runs habitctl next --contract habit.json --scope .
habitctl reads the ledger
habitctl evaluates gates
habitctl returns one DebugAdvice JSON packet
agent performs exactly that next step
agent records evidence with habitctl record ...
repeat until ok_to_fix: true or architecture_review_required
```

## Runtime Response Example

```json
{
  "ok": false,
  "ok_to_fix": false,
  "phase": "root_cause_investigation",
  "code": "needs_root_cause_tracing",
  "human_message": "The symptom appears deep in the call stack and the origin of the bad value is unknown.",
  "agent_instruction": "Use root-cause tracing. Identify the immediate cause, then walk backward through callers until you find the original trigger.",
  "retryable": true,
  "suggested_commands": ["rg -n \"symbol_or_error\" ."],
  "load_reference": "references/root-cause-tracing.md"
}
```

## General Framework

A reusable state-machine-driven Habit has this abstract shape:

```glyph
habit X
    runtime habitctl
    response AdvicePacket
    ledger EvidenceLedger
    references:
        ...
    state_machine workflow over EvidenceLedger
        gate ...
```

The compiled agent-facing loop is always:

```text
call runtime -> obey packet -> record evidence -> repeat
```

The compiled machine-facing bundle is always:

```text
manifest -> schemas -> normalized state machine -> references
```

This means future Habits can share one runtime while differing only in their ledger schema, gate set, advice packets, and progressive references.

## Open Questions

- Should the runtime be globally installed as `habitctl`, bundled inside each plugin, or resolved through the agent host?
- Should Glyph compile state machines directly to JSON, or should it also provide a generated TypeScript/Rust/Python library for validating the contract?
- How should the runtime distinguish evidence events from fix-attempt events?
- Should gates have priorities, or is declaration order enough?
- How much static validation should Glyph perform on references between gates, ledger fields, phases, and response codes?

## References

- [confirmed/concept.md#habits](../confirmed/concept.md#habits) — base concept and runtime/agent split.
