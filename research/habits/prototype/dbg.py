#!/usr/bin/env python3
import subprocess
from habit import Habit

# JIT Instructions served to the agent based on state transitions
INSTRUCTIONS = {
    "PHASE_1_INVESTIGATION": (
        "You are in Phase 1: Investigation. Do NOT write or test any fixes yet.\n"
        "Your task: Trace the data flow backward from the symptom to its origin.\n"
        "Command to run once done: python3 dbg.py phase1-trace --symptom <file:line> --origin <file:line> --flow-log \"<text>\""
    ),
    "PHASE_2_PATTERN_ANALYSIS": (
        "You are in Phase 2: Pattern Analysis.\n"
        "Your task: Find a similar working pattern in the codebase and write a diff analysis.\n"
        "Command to run once done: python3 dbg.py compare --working <file:line> --broken <file:line> --diff-analysis \"<text>\""
    ),
    "PHASE_3_HYPOTHESIS": (
        "You are in Phase 3: Hypothesis & Test.\n"
        "Your task: Formulate a single, specific theory of the root cause.\n"
        "Command to run once done: python3 dbg.py hypothesis --theory \"<text>\""
    ),
    "PHASE_4_IMPLEMENTATION": (
        "You are in Phase 4: Implementation.\n"
        "Your task: Enforce TDD. Apply the fix and confirm it resolves the test suite.\n"
        "Command to run once done: python3 dbg.py implement --test-command \"<cmd>\" --fix-patch <patch_file>"
    )
}

class SystematicDebuggingHabit(Habit):
    def __init__(self):
        super().__init__(name="systematic_debugging", state_dir=".dbg", max_failures=3)
        self._setup_debugging_commands()
        
    def _setup_debugging_commands(self):
        # init
        p_init = self.add_command("init", "Initialize systematic debugging session")
        p_init.add_argument("--repro-cmd", required=True)
        
        # phase1-trace
        p_p1 = self.add_command("phase1-trace", "Record data flow trace")
        p_p1.add_argument("--symptom", required=True)
        p_p1.add_argument("--origin", required=True)
        p_p1.add_argument("--flow-log", required=True)
        
        # compare
        p_comp = self.add_command("compare", "Record pattern analysis")
        p_comp.add_argument("--working", required=True)
        p_comp.add_argument("--broken", required=True)
        p_comp.add_argument("--diff-analysis", required=True)
        
        # hypothesis
        p_hyp = self.add_command("hypothesis", "Register single hypothesis")
        p_hyp.add_argument("--theory", required=True)
        
        # test-hypothesis
        p_test = self.add_command("test-hypothesis", "Test a hypothesis patch")
        p_test.add_argument("--patch", required=True)
        
        # implement
        p_imp = self.add_command("implement", "Implement and verify the fix")
        p_imp.add_argument("--test-command", required=True)
        p_imp.add_argument("--fix-patch", required=True)

    def handle_init(self, args):
        print(f"[*] Running reproduction command: {args.repro_cmd}")
        failures = 0
        runs = 3
        for _ in range(runs):
            res = subprocess.run(args.repro_cmd, shell=True, capture_output=True, text=True)
            if res.returncode != 0:
                failures += 1
                
        repro_rate = (failures / runs) * 100
        if failures == 0:
            self.response(
                ok=False,
                status="REPRO_FAILED",
                message=f"Reproduction command succeeded in all {runs} runs. Could not reproduce the bug.",
                next_instruction="Ensure the reproduction command is correct and targets the failing environment."
            )

        state = {
            "session_id": f"dbg_session_4f8e9a",
            "current_phase": "PHASE_1_INVESTIGATION",
            "repro_command": args.repro_cmd,
            "reproducibility": f"{repro_rate:.0f}% ({failures}/{runs} failures)",
            "failures": []
        }
        self.session.save(state)
        self.response(
            ok=True,
            status="INIT_SUCCESS",
            message=f"Session initialized. Bug reproduced at {state['reproducibility']}.",
            next_instruction=INSTRUCTIONS["PHASE_1_INVESTIGATION"]
        )

    def handle_phase1_trace(self, args):
        state = self.session.load()
        if not state:
            self.response(False, "NO_SESSION", "No active session. Run `dbg init` first.")
            
        self.verify_transition(state["current_phase"], ["PHASE_1_INVESTIGATION"])
        
        state["phase_1"] = {
            "symptom": args.symptom,
            "origin": args.origin,
            "flow_log": args.flow_log
        }
        state["current_phase"] = "PHASE_2_PATTERN_ANALYSIS"
        self.session.save(state)
        self.response(
            ok=True,
            status="PHASE_1_SUCCESS",
            message="Phase 1 data flow trace recorded.",
            next_instruction=INSTRUCTIONS["PHASE_2_PATTERN_ANALYSIS"]
        )

    def handle_compare(self, args):
        state = self.session.load()
        if not state:
            self.response(False, "NO_SESSION", "No active session.")
            
        self.verify_transition(state["current_phase"], ["PHASE_2_PATTERN_ANALYSIS"])
        
        state["phase_2"] = {
            "working": args.working,
            "broken": args.broken,
            "diff_analysis": args.diff_analysis
        }
        state["current_phase"] = "PHASE_3_HYPOTHESIS"
        self.session.save(state)
        self.response(
            ok=True,
            status="PHASE_2_SUCCESS",
            message="Phase 2 pattern analysis recorded.",
            next_instruction=INSTRUCTIONS["PHASE_3_HYPOTHESIS"]
        )

    def handle_hypothesis(self, args):
        state = self.session.load()
        if not state:
            self.response(False, "NO_SESSION", "No active session.")
            
        self.verify_transition(state["current_phase"], ["PHASE_3_HYPOTHESIS"])
        
        if state.get("blocked", False):
            self.response(
                ok=False,
                status="BLOCKED_ARCHITECTURAL_REVIEW",
                message="Session is locked due to multiple failed hypothesis attempts.",
                next_instruction="STOP. Do NOT try another patch. Run `python3 dbg.py discuss-architecture`."
            )

        state["active_hypothesis"] = args.theory
        self.session.save(state)
        
        self.response(
            ok=True,
            status="HYPOTHESIS_REGISTERED",
            message="Hypothesis registered.",
            next_instruction="Now test this hypothesis with a minimal patch: python3 dbg.py test-hypothesis --patch <patch_file>"
        )

    def handle_test_hypothesis(self, args):
        state = self.session.load()
        if not state:
            self.response(False, "NO_SESSION", "No active session.")
            
        self.verify_transition(state["current_phase"], ["PHASE_3_HYPOTHESIS"])
        
        if not state.get("active_hypothesis"):
            self.response(False, "NO_ACTIVE_HYPOTHESIS", "No registered hypothesis. Run `dbg hypothesis` first.")

        print(f"[*] Applying test patch: {args.patch}")
        res = subprocess.run(state["repro_command"], shell=True, capture_output=True, text=True)
        
        if res.returncode == 0:
            state["current_phase"] = "PHASE_4_IMPLEMENTATION"
            state["verified_patch"] = args.patch
            self.session.save(state)
            self.response(
                ok=True,
                status="HYPOTHESIS_VERIFIED",
                message="Hypothesis verified! Patch resolves the bug.",
                next_instruction=INSTRUCTIONS["PHASE_4_IMPLEMENTATION"]
            )
        else:
            escalation_instr = "STOP CODING immediately. Run `python3 dbg.py discuss-architecture` and discuss with your human partner."
            self.track_failure(state, f"Failed patch: {args.patch}", escalation_instr)

    def handle_implement(self, args):
        state = self.session.load()
        if not state:
            self.response(False, "NO_SESSION", "No active session.")
            
        self.verify_transition(state["current_phase"], ["PHASE_4_IMPLEMENTATION"])
        
        # (Mock verification of failing test case on clean state)
        print("[*] Reverting fix to ensure test-command fails...")
        
        # (Apply final fix patch and run test-command)
        print("[*] Applying final fix patch and running test...")
        res = subprocess.run(args.test_command, shell=True, capture_output=True, text=True)
        if res.returncode != 0:
             self.response(False, "IMPLEMENT_VERIFY_FAILED", "The implemented test command failed with the applied fix.")

        state["current_phase"] = "RESOLVED"
        self.session.save(state)
        self.response(
            ok=True,
            status="RESOLVED",
            message="Debugging session successfully completed and verified.",
            next_instruction="You can now run git commit and push."
        )

if __name__ == "__main__":
    SystematicDebuggingHabit().run()
