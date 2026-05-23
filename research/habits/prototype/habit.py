# Habit Runtime Framework
# This is the reusable library that ships with the agent platform.
# Developers import this to create new CLI-based Habits.

import os
import json
import sys
import argparse

class SkillSession:
    """Manages persistence of the execution state."""
    def __init__(self, state_dir, session_file="session.json"):
        self.state_dir = state_dir
        self.state_file = os.path.join(state_dir, session_file)
        self.bypass_file = os.path.join(state_dir, "bypass_audit.log")

    def load(self):
        if not os.path.exists(self.state_file):
            return None
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def save(self, data):
        os.makedirs(self.state_dir, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)

    def log_bypass(self, session_id, reason):
        os.makedirs(self.state_dir, exist_ok=True)
        with open(self.bypass_file, 'a') as f:
            f.write(f"SESSION: {session_id} | BYPASS REASON: {reason}\n")


class Habit:
    """Base class for defining an executable procedural skill."""
    def __init__(self, name, state_dir=".skill_state", max_failures=3):
        self.name = name
        self.session = SkillSession(state_dir)
        self.max_failures = max_failures
        self.parser = argparse.ArgumentParser(description=f"Habit: {name}")
        self._setup_core_commands()

    def _setup_core_commands(self):
        # Every Habit inherits a global bypass/escape-hatch command
        subparsers = self.parser.add_subparsers(dest="command", required=True)
        self.subparsers = subparsers
        
        p_bypass = subparsers.add_parser("bypass", help="Activate escape hatch to bypass gates")
        p_bypass.add_argument("--reason", required=True, help="Detailed explanation of bypass")

    def add_command(self, name, help_text=""):
        return self.subparsers.add_parser(name, help=help_text)

    def response(self, ok, status, message, next_instruction=None, **kwargs):
        """Standardizes the JIT instruction output format for the agent."""
        res = {
            "ok": ok,
            "status": status,
            "human_message": message
        }
        if next_instruction:
            res["agent_instruction"] = next_instruction
        res.update(kwargs)
        
        print(json.dumps(res, indent=2))
        sys.exit(0 if ok else 1)

    def verify_transition(self, current_state, expected_states):
        """Enforces the strict order of phases."""
        if current_state not in expected_states:
            self.response(
                ok=False,
                status="INVALID_TRANSITION",
                message=f"Cannot perform this action while session is in state: {current_state}",
                next_instruction=f"Complete the tasks for state {current_state} first."
            )

    def track_failure(self, state, error_message, escalation_instruction):
        """Enforces architectural review gates when failures accumulate."""
        attempts = state.setdefault("failures", [])
        attempts.append(error_message)
        
        failures_count = len(attempts)
        if failures_count >= self.max_failures:
            state["blocked"] = True
            state["current_phase"] = "BLOCKED_ARCHITECTURAL_REVIEW"
            self.session.save(state)
            self.response(
                ok=False,
                status="BLOCKED_ARCHITECTURAL_REVIEW",
                message=f"Maximum failures reached ({failures_count}/{self.max_failures}).",
                next_instruction=escalation_instruction,
                failures_count=failures_count
            )
        else:
            self.session.save(state)
            self.response(
                ok=False,
                status="ACTION_FAILED",
                message=f"Action failed. Attempt {failures_count}/{self.max_failures}.",
                next_instruction="Address the failure and retry the action."
            )

    def handle_bypass(self, reason):
        state = self.session.load()
        session_id = state.get("session_id", "no_session") if state else "no_session"
        
        self.session.log_bypass(session_id, reason)
        if state:
            state["current_phase"] = "BYPASS_UNLOCKED"
            self.session.save(state)
            
        self.response(
            ok=True,
            status="BYPASS_SUCCESSFUL",
            message="Escape hatch activated. Tool enforcement unlocked.",
            next_instruction="You are now permitted to perform manual file edits and debugging. Document your verification path."
        )

    def run(self):
        args = self.parser.parse_args()
        
        if args.command == "bypass":
            self.handle_bypass(args.reason)
            return

        # Delegate subclass specific commands
        if hasattr(self, f"handle_{args.command}"):
            getattr(self, f"handle_{args.command}")(args)
        else:
            self.response(False, "UNKNOWN_COMMAND", f"Command {args.command} is not implemented.")
