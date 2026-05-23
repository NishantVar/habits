---
tags: [research, habits, executable-skills, consolidated, dspy, trajectory]
date_created: 2026-05-21
date_updated: 2026-05-23
sources: 1
status: passive-trajectory
---

# DSPy Trajectory for Habits

## Summary

DSPy is a plausible future backend for the **judgment-producing parts** of Habits, but it should not replace the deterministic state-machine runtime. The preferred trajectory is to compile Glyph Habit source into the normal Habit bundle, with optional DSPy files generated for model-mediated judgment nodes.

This is not the main design decision yet. It is a passive potential path to keep in view while the reusable-runtime design matures.

## Current Read

DSPy fits places where a Habit needs typed model judgment:

- classify a symptom from full error output
- decide whether an error looks flaky or timing-dependent
- summarize evidence into a root-cause hypothesis candidate
- compare a broken implementation against a working example
- produce an agent-facing instruction from structured state

DSPy is less appropriate for core enforcement:

- loading and validating the ledger
- evaluating deterministic gates
- enforcing `ok_to_fix`
- tracking failed fix attempts
- blocking premature edits
- recording evidence events
- maintaining runtime state

The clean split is:

```text
Glyph -> Habit bundle
      -> state-machine JSON
      -> schemas
      -> tiny SKILL.md
      -> optional DSPy modules for judgment gates
```

## Bundle Shape With DSPy

```text
systematic-debugging/
  SKILL.md
  habit.json
  machine/
    state-machine.json
    ledger.schema.json
    advice.schema.json
    dspy_modules.py
    metrics.py
    evalset.jsonl
  references/
    root-cause-tracing.md
    condition-based-waiting.md
    defense-in-depth.md
```

The generic runtime still runs the skill. DSPy becomes an optional judgment engine that the runtime can invoke when a gate or transition requires model interpretation.

## Speculative Glyph Shape

```glyph
judge symptom_classification with dspy
    input:
        full_error_output
        stack_trace
        recent_changes
    output:
        symptom_class: SymptomClass
        confidence: Confidence
        rationale: Text

state_machine debugging over DebugLedger
    gate classify_symptom
        when ledger.full_error_output exists
         and ledger.symptom_class is none
        judge symptom_classification
        writes:
            ledger.symptom_class
            ledger.symptom_confidence
            ledger.symptom_rationale
        advice:
            code: "symptom_classification_needed"
            instruction: "Classify the symptom from the captured evidence before deciding which debugging technique applies."

    gate needs_root_cause_tracing
        when ledger.symptom_class == "deep_stack"
        block_fix
        load_reference root_cause_tracing
        advice:
            code: "needs_root_cause_tracing"
            instruction: "Use root-cause tracing. Identify the immediate cause, then walk backward through callers until you find the original trigger."
```

## Generated DSPy Module Sketch

```python
import dspy


class ClassifySymptom(dspy.Signature):
    """Classify a debugging symptom from captured evidence."""

    full_error_output: str = dspy.InputField()
    stack_trace: str = dspy.InputField()
    recent_changes: str = dspy.InputField()

    symptom_class: str = dspy.OutputField()
    confidence: str = dspy.OutputField()
    rationale: str = dspy.OutputField()


class SymptomClassifier(dspy.Module):
    def __init__(self):
        self.classify = dspy.ChainOfThought(ClassifySymptom)

    def forward(self, full_error_output, stack_trace="", recent_changes=""):
        return self.classify(
            full_error_output=full_error_output,
            stack_trace=stack_trace,
            recent_changes=recent_changes,
        )
```

## Machine Contract Hook

The normalized state machine could reference DSPy modules only for explicit `judgment` nodes:

```json
{
  "id": "classify_symptom",
  "kind": "judgment",
  "engine": "dspy",
  "module": "machine.dspy_modules.SymptomClassifier",
  "inputs": {
    "full_error_output": "ledger.full_error_output",
    "stack_trace": "ledger.stack_trace",
    "recent_changes": "ledger.recent_changes_summary"
  },
  "writes": [
    "ledger.symptom_class",
    "ledger.symptom_confidence",
    "ledger.symptom_rationale"
  ]
}
```

The runtime can then:

1. Load the state-machine contract.
2. Encounter a `judgment` node.
3. Invoke the configured DSPy module.
4. Validate the returned fields.
5. Write the result back into the ledger.
6. Continue deterministic gate evaluation.

## Why This Could Be Useful

DSPy would make the model-mediated parts more explicit and testable. Instead of hiding judgment inside prose, the skill would define typed inputs, typed outputs, and optional metrics. Over time, DSPy optimizers could improve specific judgment modules using examples from prior debugging sessions.

This also gives Habits a richer compilation target than Markdown alone: Glyph could produce both the human/agent surface and an evaluable LM-program surface.

## Risks

- DSPy adds dependency weight; simple Habits should not require it.
- Optimization only matters if there are metrics and examples worth optimizing against.
- The state machine must remain authoritative; DSPy output should not bypass deterministic gates.
- Generated DSPy code may become another artifact that needs versioning and compatibility management.

## Position

Treat DSPy as an **optional backend for `judge` nodes**, not as the Habit runtime itself.

The durable architecture remains:

```text
generic runtime + declarative state machine + evidence ledger
```

The possible DSPy trajectory adds:

```text
typed, optimizable LM judgment modules for ambiguous decisions
```

## References

- [confirmed/concept.md#habits](../confirmed/concept.md#habits) — base Habits concept.
- [state-machine-runtime.md#generic-runtime-contract](state-machine-runtime.md#generic-runtime-contract) — current consolidated reusable-runtime direction.
