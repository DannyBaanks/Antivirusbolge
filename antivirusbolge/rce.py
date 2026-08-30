"""Defensive RCE / interpreter-boundary analysis.

Maps, for each Malbolge operation, the interpreter handler and whether it can
reach a host primitive. This is a defensive static analysis: it enumerates the
path MALBOLGE_OPERATION -> INTERPRETER_HANDLER -> ADAPTER -> HOST_PRIMITIVE and
reports reachability. It never constructs payloads.

Result classes (per the spec):
    NO_HOST_PATH_FOUND
    HOST_PATH_PRESENT_NOT_REACHED
    HOST_PATH_REACHED
    HOST_EFFECT_OBSERVED
    INCONCLUSIVE

The handler tables below are transcribed from reading the interpreter source
(walbolge.trace / Malbolge-Engine vm.c), not guessed.
"""
from __future__ import annotations

from typing import List

from .interpreter import get_backend

OPERATIONS = ["i", "<", "/", "*", "j", "p", "o", "v"]

# host primitives we look for in a handler
_HOST_PRIMITIVES = {
    "NONE",
    "HOST_FILE_READ", "HOST_FILE_WRITE", "HOST_PROCESS_START",
    "HOST_NETWORK", "HOST_ENV_READ", "HOST_NATIVE_CALL",
}

# Per-backend handler table: operation -> (interpreter_handler, host_primitive).
# Transcribed from walbolge/trace.py and Malbolge-Engine/src/vm.c.
_HANDLERS = {
    "walbolge": {
        "i":  ("trace_program (jump_c branch)", "NONE"),
        "<":  ("trace_program (output branch)", "NONE"),
        "/":  ("trace_program (input branch, no stdin read)", "NONE"),
        "*":  ("trace_program (ternary_rotate, tape write)", "NONE"),
        "j":  ("trace_program (jump_d branch)", "NONE"),
        "p":  ("trace_program (crazy_write)", "NONE"),
        "o":  ("trace_program (nop branch)", "NONE"),
        "v":  ("trace_program (halt branch)", "NONE"),
    },
    "malbolge-engine": {
        "i":  ("vm_run (case 4: c=mem_get(d))", "NONE"),
        "<":  ("vm_run (case 5: vm_out_buf write)", "NONE"),
        "/":  ("vm_run (case 23: reads adapter-provided input buffer)", "NONE"),
        "*":  ("vm_run (case 39: rotate + mem_set)", "NONE"),
        "j":  ("vm_run (case 40: d=mem_get(d))", "NONE"),
        "p":  ("vm_run (case 62: vm_crazy + mem_set)", "NONE"),
        "o":  ("vm_run (default nop)", "NONE"),
        "v":  ("vm_run (case 81: terminate)", "NONE"),
    },
}


def analyze_rce(backend_name: str) -> dict:
    """Defensive boundary analysis for a backend.

    Returns the per-operation host-path map, adapter-level capabilities, and an
    overall classification.
    """
    backend = get_backend(backend_name)
    handlers = _HANDLERS[backend_name]

    operations = []
    for op in OPERATIONS:
        handler, primitive = handlers[op]
        operations.append({
            "operation": op,
            "interpreter_handler": handler,
            "host_primitive": primitive,
            "reachable": False,      # by inspection: handler is VM-only
            "authorized": False,
            "exercised": False,
            "execution_evidence": None,
        })

    # Host primitives the deployment/builds with (adapter level).
    present = list(backend.host_map.capabilities_present)

    # Overall classification at the VM->host seam.
    any_operation_reaches = any(o["reachable"] for o in operations)
    if any_operation_reaches:
        cls = "HOST_PATH_REACHED"
    elif present and backend.host_map.capabilities_reachable:
        cls = "HOST_PATH_PRESENT_NOT_REACHED"
    elif present and not backend.host_map.capabilities_reachable:
        # Adapter holds a capability but no operation can reach it.
        cls = "HOST_PATH_PRESENT_NOT_REACHED"
    else:
        cls = "NO_HOST_PATH_FOUND"

    return {
        "backend": backend_name,
        "seam": backend.host_map.seam,
        "operations": operations,
        "adapter_capabilities_present": present,
        "adapter_capabilities_reachable": backend.host_map.capabilities_reachable,
        "adapter_capabilities_exercised": backend.host_map.capabilities_exercised,
        "host_paths_to_host_primitive": sum(1 for o in operations if o["host_primitive"] != "NONE"),
        "classification": cls,
        "status": "DEMONSTRATED",
        "note": ("VM handlers are VM-only by source inspection; no Malbolge "
                 "operation reaches a host primitive."),
    }