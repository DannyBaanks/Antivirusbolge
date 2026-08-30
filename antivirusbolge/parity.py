"""Cross-interpreter parity: same specimen on Walbolge (classic) vs Malbolge-Engine (C).

Classifies SEMANTIC_PARITY / OUTPUT_DIVERGENCE / TRACE_DIVERGENCE /
CRASH_ONLY_ONE_BACKEND / HOST_EFFECT_ONLY_ONE_BACKEND. This is the critical
question M1 answers: dangerous behavior may belong to the interpreter, not to
Malbolge semantics.
"""
from __future__ import annotations

from .analyzer import scan


def parity(specimen_path: str, max_steps: int = 5_000_000) -> dict:
    ra = scan(specimen_path, classic=True, backend_name="walbolge",
              max_steps=max_steps)
    rb = scan(specimen_path, backend_name="malbolge-engine",
              max_steps=max_steps)

    a_out = ra["outcome"]
    b_out = rb["outcome"]

    a_err = a_out.get("error") is not None or a_out.get("halt_reason") == "interpreter_error"
    b_err = b_out.get("error") is not None or b_out.get("halt_reason") == "interpreter_error"

    # Host-effect-only-one-backend is only reachable if one backend exercises a
    # host capability the other does not. Neither specimen can drive host via
    # either backend, so this stays NOT_DEMONSTRATED.
    a_ex = ra["host_map"]["capabilities_exercised"]
    b_ex = rb["host_map"]["capabilities_exercised"]
    host_only_one = (set(a_ex) != set(b_ex)) and (set(a_ex) or set(b_ex))

    if a_err and b_err:
        cls = "CRASH_BOTH"
    elif a_err or b_err:
        cls = "CRASH_ONLY_ONE_BACKEND"
    elif host_only_one:
        cls = "HOST_EFFECT_ONLY_ONE_BACKEND"
    else:
        same_output = a_out["output"] == b_out["output"]
        same_halt = a_out["halt_reason"] == b_out["halt_reason"]
        if same_output and same_halt:
            cls = "SEMANTIC_PARITY"
        elif not same_output:
            cls = "OUTPUT_DIVERGENCE"
        else:
            cls = "TRACE_DIVERGENCE"

    return {
        "specimen": specimen_path,
        "backend_a": {"name": "walbolge", "steps": a_out.get("steps"),
                      "halt": a_out.get("halt_reason"),
                      "output_len": len(a_out.get("output", "")),
                      "error": a_out.get("error"),
                      "capabilities_exercised": a_ex},
        "backend_b": {"name": "malbolge-engine", "steps": b_out.get("steps"),
                      "halt": b_out.get("halt_reason"),
                      "output_len": len(b_out.get("output", "")),
                      "error": b_out.get("error"),
                      "capabilities_exercised": b_ex},
        "output_match": a_out.get("output", "") == b_out.get("output", ""),
        "halt_match": a_out.get("halt_reason") == b_out.get("halt_reason"),
        "steps_a": a_out.get("steps"),
        "steps_b": b_out.get("steps"),
        "classification": cls,
        "status": "DEMONSTRATED" if not a_err and not b_err else "NOT_DEMONSTRATED",
    }