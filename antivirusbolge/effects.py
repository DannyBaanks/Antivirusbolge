"""Canonical effect IR for ANTIVIRUSBOLGE.

Observable Malbolge behavior is reduced to a small set of canonical effects.
VM-level effects stay separate from host-level effects. A host effect may only
appear when a concrete interpreter/wrapper seam demonstrates a host boundary
crossing; for the Walbolge Python backend that seam is structurally absent.
"""
from __future__ import annotations

from collections import Counter
from typing import List, Optional

# --- VM-level canonical effects -------------------------------------------
VM_READ = "VM_READ"
VM_WRITE = "VM_WRITE"
VM_JUMP = "VM_JUMP"
VM_ARITHMETIC = "VM_ARITHMETIC"
INPUT = "INPUT"
OUTPUT = "OUTPUT"
HALT = "HALT"
STEP = "STEP"
ERROR = "ERROR"

# --- Host-level canonical effects (separate layer) ------------------------
HOST_FILE_READ = "HOST_FILE_READ"
HOST_FILE_WRITE = "HOST_FILE_WRITE"
HOST_PROCESS_START = "HOST_PROCESS_START"
HOST_NETWORK = "HOST_NETWORK"
HOST_ENV_READ = "HOST_ENV_READ"
HOST_NATIVE_CALL = "HOST_NATIVE_CALL"
HOST_UNKNOWN_EFFECT = "HOST_UNKNOWN_EFFECT"

ALL_VM = {VM_READ, VM_WRITE, VM_JUMP, VM_ARITHMETIC, INPUT, OUTPUT, HALT, STEP, ERROR}
ALL_HOST = {
    HOST_FILE_READ, HOST_FILE_WRITE, HOST_PROCESS_START,
    HOST_NETWORK, HOST_ENV_READ, HOST_NATIVE_CALL, HOST_UNKNOWN_EFFECT,
}

# Walbolge trace event_type -> canonical effect sequence.
# A single Walbolge event may map to several canonical effects (e.g. a write
# of an arithmetic result is both VM_WRITE and VM_ARITHMETIC).
_EVENT_EFFECTS = {
    "execute": (STEP, VM_READ),
    "jump_c": (VM_JUMP, VM_READ),
    "jump_d": (VM_JUMP, VM_READ),
    "output": (OUTPUT,),
    "input": (INPUT,),
    "rotate_write": (VM_WRITE, VM_ARITHMETIC),
    "crazy_write": (VM_WRITE, VM_ARITHMETIC),
    "nop": (VM_READ,),
    "halt": (HALT,),
}


def event_to_effects(event_type: str) -> List[str]:
    """Map a backend trace event to canonical effects."""
    return list(_EVENT_EFFECTS.get(event_type, (STEP,)))


def canonical_effects_from_events(events: List[dict], with_self_encrypt: bool = True) -> dict:
    """Reduce a list of backend trace events (dicts) to a canonical effect summary.

    Returns:
        {
            "vm_effects": {effect: count},          # present + counted
            "host_effects": {},                      # empty unless a seam proves it
            "sequence": [effect, ...],               # bounded ordered sequence
            "event_effect_count": int,
        }
    """
    vm_counts: Counter = Counter()
    sequence: List[str] = []
    max_seq = 100_000  # bounded canonical sequence; beyond this we count only

    for ev in events:
        ev_type = ev.get("event_type", "execute")
        effects = event_to_effects(ev_type)
        for fx in effects:
            vm_counts[fx] += 1
            if len(sequence) < max_seq:
                sequence.append(fx)
        # The auto-encrypt of the executed cell is a VM write.
        if with_self_encrypt and ev.get("write_c") is not None:
            vm_counts[VM_WRITE] += 1

    return {
        "vm_effects": dict(vm_counts),
        "host_effects": {},  # structurally empty for the Walbolge backend
        "sequence": sequence,
        "event_effect_count": sum(vm_counts.values()),
    }


def effect_sequence_hash(sequence: List[str]) -> str:
    import hashlib
    return hashlib.sha256("|".join(sequence).encode("utf-8")).hexdigest()


def effects_to_signature(canonical: dict, output: str, halt_reason: str,
                         max_events: Optional[int]) -> dict:
    """Behavioral signature inputs (source hash stays separate)."""
    import hashlib
    out_hash = hashlib.sha256(output.encode("utf-8", "replace")).hexdigest()
    trace_hash = hashlib.sha256(
        "|".join(canonical["sequence"]).encode("utf-8")).hexdigest()
    return {
        "trace_hash": trace_hash,
        "effect_count": canonical["event_effect_count"],
        "effect_multiset": canonical["vm_effects"],
        "output_hash": out_hash,
        "halt_reason": halt_reason,
        "events_bounded": bool(max_events) and len(canonical["sequence"]) >= max_events,
    }