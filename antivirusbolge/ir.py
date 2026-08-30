"""Canonical analysis IR (M2-C).

A normalized representation of Malbolge analysis across backends. Adapters
translate external results into this IR. The IR never invents fields a provider
cannot demonstrate; absence of evidence != a false value.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .effects import canonical_effects_from_events, effect_sequence_hash


@dataclass
class AnalysisEvent:
    step: int
    c: int
    d: int
    a: int
    opcode: str
    event_type: str
    output_char: Optional[str] = None
    jump_target: Optional[int] = None
    memory_write: Optional[dict] = None
    source_backend: str = ""

    def to_dict(self) -> dict:
        return {
            "step": self.step, "c": self.c, "d": self.d, "a": self.a,
            "opcode": self.opcode, "event_type": self.event_type,
            "output_char": self.output_char, "jump_target": self.jump_target,
            "memory_write": self.memory_write, "source_backend": self.source_backend,
        }


@dataclass
class AnalysisResult:
    specimen_sha256: str
    backend: str
    status: str                # OK / ERROR / TIMEOUT / INVALID / UNAVAILABLE
    halt_reason: Optional[str]
    steps: int
    output: str
    output_hash: str
    trace_hash: str
    events: List[AnalysisEvent] = field(default_factory=list)
    final_state: Optional[dict] = None
    structural_findings: dict = field(default_factory=dict)
    security_findings: dict = field(default_factory=dict)
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "specimen_sha256": self.specimen_sha256,
            "backend": self.backend,
            "status": self.status,
            "halt_reason": self.halt_reason,
            "steps": self.steps,
            "output": self.output,
            "output_hash": self.output_hash,
            "trace_hash": self.trace_hash,
            "events": [e.to_dict() for e in self.events[:2000]],
            "event_count": len(self.events),
            "final_state": self.final_state,
            "structural_findings": self.structural_findings,
            "security_findings": self.security_findings,
        }


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def normalize_events(backend_events: List[dict], backend: str) -> List[AnalysisEvent]:
    """Convert a backend's raw trace events into canonical AnalysisEvents.

    Backends that do not expose per-event trace yield an empty list (absence of
    evidence is preserved, not fabricated).
    """
    out = []
    for ev in backend_events:
        out.append(AnalysisEvent(
            step=ev.get("step", 0),
            c=ev.get("c", 0),
            d=ev.get("d", 0),
            a=ev.get("a_before", ev.get("a", 0)),
            opcode=ev.get("instruction", ev.get("opcode", "")),
            event_type=ev.get("event_type", "execute"),
            output_char=ev.get("output_char"),
            jump_target=ev.get("jump_target"),
            memory_write={"write_c": ev.get("write_c"),
                          "write_d": ev.get("write_d")}
            if ev.get("write_c") is not None or ev.get("write_d") is not None else None,
            source_backend=backend,
        ))
    return out