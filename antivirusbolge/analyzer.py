"""Top-level scan orchestrator.

Specimen -> normalizer -> Walbolge trace -> canonical effects -> invariants ->
host map -> classification -> receipt.
"""
from __future__ import annotations

import time
from typing import List, Optional

from .normalizer import load_specimen, static_analysis
from .interpreter import get_backend
from .effects import canonical_effects_from_events, effects_to_signature
from .classify import classify
from .invariants import evaluate_invariants
from .receipt import build_receipt, DEFAULT_LIMITS

MAX_OUTPUT_BYTES_DEFAULT = 256 * 1024
MAX_WALL_TIME_S_DEFAULT = 60.0


def scan(specimen_path: str,
         max_steps: int = 5_000_000,
         max_events: Optional[int] = None,
         max_output_bytes: Optional[int] = MAX_OUTPUT_BYTES_DEFAULT,
         max_wall_time_s: Optional[float] = MAX_WALL_TIME_S_DEFAULT,
         classic: bool = False,
         backend_name: str = "walbolge") -> dict:
    raw, text = load_specimen(specimen_path)
    static = static_analysis(raw, text).to_dict()

    limits = DEFAULT_LIMITS(max_steps, max_output_bytes, max_wall_time_s)

    backend = get_backend(backend_name)

    # Static short-circuit: nothing valid to execute -> INVALID_PROGRAM without a run.
    if static["malformed_cells"] > 0 and static["opcode_count"] == 0:
        canonical = canonical_effects_from_events([])
        outcome = {"steps": 0, "halted": False, "halt_reason": "invalid_program",
                   "output": "", "peak_memory": 0, "events": [],
                   "events_dropped": False, "executed_positions": [],
                   "jumps_count": 0, "error": None}
        budget = {"exceeded": False, "reason": None}
        verdict = classify(static, _as_outcome(outcome), canonical, False, False, max_steps)
        host_map = backend.host_map.to_dict()
        invariants = evaluate_invariants(_report_shape(
            static, outcome, canonical, host_map, verdict, budget))
        signature = effects_to_signature(canonical, "", "invalid_program", max_events)
        not_demo = ["behavior beyond static inspection"]
        receipt = build_receipt(specimen_path, static, outcome, canonical, host_map,
                                verdict, budget, {"name": backend.name,
                                                  "version": backend.version},
                                limits, not_demo)
        return _assemble(specimen_path, static, outcome, canonical, host_map,
                         verdict, budget, invariants, signature, receipt, limits,
                         not_demo)

    started = time.monotonic()
    bo = backend.trace(text, max_steps=max_steps, max_events=max_events,
                       classic=classic)
    wall = time.monotonic() - started

    budget_exceeded = bo.halt_reason == "max_steps" or wall > (max_wall_time_s or 1e9)
    budget_reason = "max_steps" if bo.halt_reason == "max_steps" else \
        ("max_wall_time" if wall > (max_wall_time_s or 1e9) else None)
    out_truncated = (max_output_bytes is not None
                     and len(bo.output.encode("utf-8", "replace")) > max_output_bytes)
    if out_truncated:
        budget_exceeded = True
        budget_reason = "max_output_bytes"
        bo_output = bo.output[:max_output_bytes]
    else:
        bo_output = bo.output

    canonical = canonical_effects_from_events(bo.events)
    host_map = backend.host_map.to_dict()
    verdict = classify(static, bo, canonical, budget_exceeded,
                       bo.error is not None, max_steps)
    outcome = {
        "steps": bo.steps, "halted": bo.halted, "halt_reason": bo.halt_reason,
        "output": bo_output, "peak_memory": bo.peak_memory,
        "events": bo.events, "events_dropped": bo.events_dropped,
        "executed_positions": bo.executed_positions, "jumps_count": bo.jumps_count,
        "error": bo.error, "wall_time_s": round(wall, 4),
    }
    budget = {"exceeded": budget_exceeded, "reason": budget_reason,
              "wall_time_s": round(wall, 4)}

    signature = effects_to_signature(canonical, bo_output, bo.halt_reason, max_events)
    invariants = evaluate_invariants(_report_shape(
        static, outcome, canonical, host_map, verdict, budget))

    not_demo = [
        "behavior beyond step budget",
        "behavior on other interpreters",
        "universal harmlessness",
    ]
    receipt = build_receipt(specimen_path, static, outcome, canonical, host_map,
                            verdict, budget, {"name": backend.name,
                                              "version": backend.version},
                            limits, not_demo)
    return _assemble(specimen_path, static, outcome, canonical, host_map,
                     verdict, budget, invariants, signature, receipt, limits,
                     not_demo)


def _as_outcome(d: dict):
    from .interpreter import BackendOutcome
    return BackendOutcome(**{k: d[k] for k in (
        "steps", "halted", "halt_reason", "output", "peak_memory")})


def _report_shape(static, outcome, canonical, host_map, verdict, budget):
    return {
        "host_map": host_map,
        "canonical": canonical,
        "verdict": verdict,
        "outcome": outcome,
        "budget": budget,
    }


def _assemble(specimen_path, static, outcome, canonical, host_map, verdict,
              budget, invariants, signature, receipt, limits, not_demo):
    return {
        "specimen_path": specimen_path,
        "static": static,
        "outcome": outcome,
        "canonical": canonical,
        "signature": signature,
        "host_map": host_map,
        "verdict": verdict,
        "budget": budget,
        "limits": limits,
        "invariants": invariants,
        "receipt": receipt,
        "not_demonstrated": not_demo,
    }


def behavior_signature(report: dict) -> dict:
    """The important experiment: source hash != behavioral signature."""
    return {
        "source_sha256": report["static"]["sha256"],
        "behavioral": report["signature"],
    }