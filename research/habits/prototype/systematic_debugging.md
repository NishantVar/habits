# Systematic Debugging

Initialize the systematic debugging Habit to investigate and resolve a bug.

## Goal

The bug is fixed at the root cause, and a regression test prevents it from returning.

## Parameters

* **repro_cmd**: The shell command that consistently reproduces the bug (e.g., `cargo test test_timeout`).
* **test_cmd**: The target test command that verifies the specific fix.

## Constraints

* **Must avoid:** Proposing or applying code edits before Phase 1 and Phase 2 are complete and a formal hypothesis is registered.
* **Require:** Matching existing naming, conventions, and architectures in the codebase.

## Steps

1. Run the systematic debugging tool to initialize the session:
   ```bash
   python3 dbg.py init --repro-cmd "{repro_cmd}"
   ```
2. Parse the JSON output from the command execution. Inspect the `agent_instruction` field.
3. Perform the task described in the `agent_instruction` field. Do not write any code changes unless explicitly instructed by the current phase's instructions.
4. Execute the command specified in the `suggested_next_command` field, or the command instructed by the current phase.
5. Repeat steps 2-4, following the dynamic instructions returned at each step.
6. **If the tool returns the status `BLOCKED_ARCHITECTURAL_REVIEW`:**
   * Stop coding immediately.
   * Do not make any further edits.
   * Run the command:
     ```bash
     python3 dbg.py discuss-architecture
     ```
   * Present the resulting report to your human partner and discuss the architectural coupling before proceeding.
7. **If the companion tool encounters an environmental lock, crashes, or fails due to a bug:**
   * Activate the escape hatch by running:
     ```bash
     python3 dbg.py bypass --reason "<detailed_reason_for_bypass>"
     ```
   * Once the bypass is registered, proceed with manual verification steps.
