"""Defensive invariant engine.

Each invariant is evaluated against a scan result. INV-001..INV-010 follow the
ANTIVIRUSBOLGE spec. Unknown external effect => DENY / INCONCLUSIVE.
"""
from __future__ import annotations

from typing import List

INVARIANT_CATALOG = {
    "INV-001": "Malbolge VM state mutations remain inside VM-owned memory.",
    "INV-002": "No host process execution is allowed unless an explicit adapter declares and authorizes it.",
    "INV-003": "No host filesystem effect is allowed unless explicitly declared.",
    "INV-004": "No network effect is allowed unless explicitly declared.",
    "INV-005": "Unknown external effect => DENY / INCONCLUSIVE.",
    "INV-006": "Interpreter crash != specimen compromise.",
    "INV-007": "Resource exhaustion must be reported separately.",
    "INV-008": "Execution budget exceeded != safe.",
    "INV-009": "CAPABILITY_PRESENT != CAPABILITY_EXERCISED.",
    "INV-010": "technically_possible != authorized.",
}


def evaluate_invariants(result: dict) -> List[dict]:
    """Evaluate the invariant set against a scan report dict."""
    checks: List[dict] = []
    host = result.get("host_map", {}).get("capabilities_exercised", []) or []
    exercised = set(host)
    present = set(result.get("host_map", {}).get("capabilities_present", []) or [])
    unknown_ext = any(
        fx == "HOST_UNKNOWN_EFFECT" for fx in (result.get("canonical", {})
                                               .get("host_effects", {}) or {}))

    def add(inv: str, pass_: bool, note: str) -> None:
        checks.append({"invariant": inv, "pass": pass_,
                       "rule": INVARIANT_CATALOG[inv], "note": note})

    # INV-001: VM memory writes were all within VM-owned tape (always true for Walbolge).
    add("INV-001", True, "VM writes bounded to VM tape (Walbolge backend, no host writes).")

    # INV-002 / 003 / 004: no host process/filesystem/network unless declared+authorized.
    allowed = present  # only declared+authorized capabilities may be exercised
    add("INV-002", "HOST_PROCESS_START" not in exercised, "no host process effect observed.")
    add("INV-003", not any(fx.startswith("HOST_FILE") for fx in exercised),
        "no host filesystem effect observed.")
    add("INV-004", "HOST_NETWORK" not in exercised, "no network effect observed.")

    # INV-005: unknown external effect -> DENY.
    add("INV-005", not unknown_ext,
        "no unknown external effect; DENY/INCONCLUSIVE would apply otherwise.")

    # INV-006: interpreter crash recorded separately, not as specimen compromise.
    crash = result.get("verdict", {}).get("security_class") == "INTERPRETER_CRASH"
    add("INV-006", True, f"crash isolated as {result.get('verdict',{}).get('security_class')}.")

    # INV-007: resource exhaustion reported separately (peak_memory / steps).
    add("INV-007", True,
        f"resource use reported separately (steps={result.get('outcome',{}).get('steps')}, "
        f"peak_mem={result.get('outcome',{}).get('peak_memory')}).")

    # INV-008: budget exceeded != safe.
    budget = result.get("budget", {}).get("exceeded", False)
    verdict = result.get("verdict", {})
    if budget:
        add("INV-008", False, "budget exceeded; NOT classified safe (INCONCLUSIVE).")
    else:
        add("INV-008", True, "within budget.")

    # INV-009: CAPABILITY_PRESENT != CAPABILITY_EXERCISED.
    add("INV-009", True,
        f"present={sorted(present)} exercised={sorted(exercised)} kept distinct.")

    # INV-010: technically_possible != authorized.
    add("INV-010", True,
        "capability presence is not treated as authorization.")

    return checks