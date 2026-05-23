---
tags: [research, habits, executable-skills, concept]
parent: "AGENTS.md"
date_created: 2026-05-19
date_updated: 2026-05-23
---

### Habits

| Field | Value |
|-------|-------|
| Source | User-supplied concept and naming decision from conversation |
| Found | 2026-05-19 |
| Confidence | high |
| Tags | #habits #executable-skills #agent-tooling #skill-design #procedural-memory |

**Habits** are a skill design pattern where a coding-agent skill has been
proceduralized. Instead of asking the agent to consciously remember every
step, a Habit exposes a small executable interface, such as a script, CLI, API,
or runtime contract, that owns deterministic workflow and hands control back
to the agent when judgment is needed.

The name comes from the human counterpart: learned automatic behavior, like
brushing teeth, where the action sequence runs with low conscious attention
while the conscious mind can still intervene. In agent terms, a Habit is a
skill running in a subconscious or automatic mode.

Former working name: **Executable Skills**.

The core split:

- The **runtime** owns state lookup, validation, exact protocol steps, retries,
  routing, parsing, gate evaluation, and failure classification.
- The **agent** owns intent, ambiguity, user interaction, and choosing among
  recovery paths when the runtime yields back with structured guidance.

For a complex skill such as agent messaging, the agent should not have to
remember a long operational procedure from prose. It should call a simple
interface, such as sending a message to a named teammate or cmux tab. The
runtime can then resolve registrations, handle stale state, bootstrap peers,
and deliver the message.

When the runtime cannot complete the task, it should yield to the agent with a
structured failure response instead of vague text. A useful response shape:

```json
{
  "ok": false,
  "code": "peer_not_registered",
  "human_message": "No registered peer named reviewer.",
  "agent_instruction": "Use cmux discovery to find the teammate by tab title, then connect.",
  "retryable": true,
  "suggested_next_command": "agent_msg.py resolve --peer reviewer --fallback-tab"
}
```

This keeps deterministic and fragile behavior in code while preserving the
agent's ability to adapt. The pattern is especially useful for protocol-heavy
skills where prose-only execution is error-prone.

Related names:

- **Habit** — the full packaged pattern: a proceduralized skill with executable stateful guidance.
- **Habit Bundle** — the packaged artifact: `SKILL.md`, manifest, schemas, state machine, references, and optional helper code.
- **Habit Runtime** — the controller or generic runtime that interprets the Habit contract.
- **Habit Ledger** — the durable evidence and state record.
- **Agent handoff** — the moment the runtime yields back with structured guidance.

---
