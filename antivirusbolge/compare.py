"""Behavioral comparison between two specimens.

Implements the trace-level comparison ladder (L0..L5) and the spec's
"same-output different-trace" classification.
"""
from __future__ import annotations

from typing import List

from .analyzer import scan, behavior_signature

LEVELS = {
    0: "source_equality",
    1: "output_equality",
    2: "halt_reason_equality",
    3: "canonical_effect_equality",
    4: "vm_trace_equality",
    5: "final_state_equality",
}


def compare(a_path: str, b_path: str, **kwargs) -> dict:
    ra = scan(a_path, **kwargs)
    rb = scan(b_path, **kwargs)

    same_source = ra["static"]["sha256"] == rb["static"]["sha256"]
    same_output = ra["outcome"]["output"] == rb["outcome"]["output"]
    same_halt = ra["outcome"]["halt_reason"] == rb["outcome"]["halt_reason"]
    same_effects = ra["signature"]["effect_multiset"] == rb["signature"]["effect_multiset"]
    same_trace = ra["signature"]["trace_hash"] == rb["signature"]["trace_hash"]
    # Final-state approximation from the bounded trace + output hash + halt.
    same_final = (same_trace and same_output and same_halt)

    ladder = {
        "L0_source": same_source,
        "L1_output": same_output,
        "L2_halt": same_halt,
        "L3_effects": same_effects,
        "L4_trace": same_trace,
        "L5_final": same_final,
    }
    if same_output and not same_trace:
        cls = "OUTPUT_EQUAL_TRACE_DIFFERENT"
    elif same_output and same_trace:
        cls = "OUTPUT_EQUAL_TRACE_EQUAL"
    elif not same_output and same_trace:
        cls = "TRACE_EQUAL_OUTPUT_DIFFERENT"
    else:
        cls = "DIVERGENT"

    return {
        "a": a_path, "b": b_path,
        "ladder": ladder,
        "comparison": cls,
        "a_signature": behavior_signature(ra),
        "b_signature": behavior_signature(rb),
    }