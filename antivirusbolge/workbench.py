"""Workbench runner + cross-validation (M2-C, M2-F).

run(): execute a specimen on one backend, normalized to the canonical IR.
crossval(): execute a specimen on all available independent backends and
classify agreement.
"""
from __future__ import annotations

import hashlib
from typing import List

from .interpreter import get_backend, available_backends
from .ir import AnalysisResult, normalize_events
from .normalizer import load_specimen, static_analysis
from .effects import canonical_effects_from_events, effect_sequence_hash


def _hash_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", "replace")).hexdigest()


def run(specimen_path: str, backend_name: str = "walbolge",
        max_steps: int = 5_000_000, classic: bool = False) -> AnalysisResult:
    raw, text = load_specimen(specimen_path)
    sha = _hash_bytes(raw)
    backend = get_backend(backend_name)
    try:
        bo = backend.trace(text, max_steps=max_steps, max_events=None,
                           classic=classic)
    except Exception as exc:
        return AnalysisResult(specimen_sha256=sha, backend=backend_name,
                              status="ERROR", halt_reason="adapter_error",
                              steps=0, output="", output_hash=_hash(""),
                              trace_hash=_hash(""), evidence={"error": str(exc)})

    if bo.error is not None:
        status = "ERROR"
    elif bo.halt_reason == "max_steps":
        status = "TIMEOUT"
    elif bo.halt_reason == "invalid_program":
        status = "INVALID"
    else:
        status = "OK"

    events = normalize_events(bo.events, backend_name)
    canon = canonical_effects_from_events([e.to_dict() for e in events])
    return AnalysisResult(
        specimen_sha256=sha,
        backend=backend_name,
        status=status,
        halt_reason=bo.halt_reason,
        steps=bo.steps,
        output=bo.output,
        output_hash=_hash(bo.output),
        trace_hash=effect_sequence_hash(canon["sequence"]),
        events=events,
        final_state=bo.final_state,
        evidence={"peak_memory": bo.peak_memory, "error": bo.error},
    )


def crossval(specimen_path: str, backends: List[str] = None,
             max_steps: int = 5_000_000) -> dict:
    """Run a specimen on independent backends and compare.

    Classification:
        SEMANTIC_PARITY            all backends agree on output + halt
        SEMANTIC_DIVERGENCE        backends disagree on output or halt
        OBSERVATION_MODEL_DIFFERENCE  disagree only on non-semantic fields (steps)
        INCONCLUSIVE               a backend was unavailable or errored
    """
    from .normalizer import load_specimen
    raw, text = load_specimen(specimen_path)
    sha = _hash_bytes(raw)
    avail = available_backends()
    if backends is None:
        backends = [b for b in avail if avail[b]]

    results = {}
    for b in backends:
        if not avail.get(b):
            results[b] = {"status": "UNAVAILABLE"}
            continue
        r = run(specimen_path, b, max_steps=max_steps)
        results[b] = {
            "status": r.status, "halt": r.halt_reason, "steps": r.steps,
            "output_len": len(r.output), "output_hash": r.output_hash,
            "trace_hash": r.trace_hash, "final_state": r.final_state,
        }

    ok = [b for b, r in results.items() if r.get("status") == "OK"]
    if not ok:
        return {"specimen_sha256": sha, "results": results,
                "classification": "INCONCLUSIVE", "agreeing": []}

    outputs = {results[b]["output_hash"] for b in ok}
    halts = {results[b]["halt"] for b in ok}
    if len(outputs) == 1 and len(halts) == 1:
        cls = "SEMANTIC_PARITY"
    elif len(outputs) > 1 or len(halts) > 1:
        cls = "SEMANTIC_DIVERGENCE"
    else:
        cls = "OBSERVATION_MODEL_DIFFERENCE"

    return {"specimen_sha256": sha, "results": results,
            "classification": cls, "agreeing": ok}