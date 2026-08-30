"""Classification model.

Every finding carries ORIGIN, STATUS, SECURITY_CLASS and a conservative
severity. Severity never replaces evidence status.
"""
from __future__ import annotations

from typing import Dict

# ORIGIN
ORIGIN_SPECIMEN = "SPECIMEN_BEHAVIOR"
ORIGIN_VM = "VM_BEHAVIOR"
ORIGIN_INTERPRETER = "INTERPRETER_BEHAVIOR"
ORIGIN_ADAPTER = "ADAPTER_BEHAVIOR"
ORIGIN_HOST = "HOST_CAPABILITY"
ORIGIN_UNKNOWN = "UNKNOWN"

# STATUS
ST_DEMONSTRATED = "DEMONSTRATED"
ST_FALSIFIED = "FALSIFIED"
ST_NOT_DEMONSTRATED = "NOT_DEMONSTRATED"
ST_INCONCLUSIVE = "INCONCLUSIVE"

# SECURITY_CLASS
CLS_PURE_VM_COMPUTE = "PURE_VM_COMPUTE"
CLS_OUTPUT_ONLY = "OUTPUT_ONLY"
CLS_NONTERMINATING = "NONTERMINATING_WITHIN_BUDGET"
CLS_EXCESSIVE_RESOURCE = "EXCESSIVE_RESOURCE_USE"
CLS_INVALID_PROGRAM = "INVALID_PROGRAM"
CLS_INTERPRETER_CRASH = "INTERPRETER_CRASH"
CLS_MEMORY_SAFETY = "MEMORY_SAFETY_FAILURE"
CLS_HOST_CAP_REQ = "HOST_CAPABILITY_REQUEST"
CLS_HOST_CAP_ESCAPE = "HOST_CAPABILITY_ESCAPE"
CLS_FILESYSTEM_EFFECT = "FILESYSTEM_EFFECT"
CLS_PROCESS_EFFECT = "PROCESS_EXECUTION_EFFECT"
CLS_NETWORK_EFFECT = "NETWORK_EFFECT"
CLS_ENV_DISCLOSURE = "ENVIRONMENT_DISCLOSURE"
CLS_UNKNOWN_EXTERNAL = "UNKNOWN_EXTERNAL_EFFECT"

SEVERITY = {
    CLS_PURE_VM_COMPUTE: "INFO",
    CLS_OUTPUT_ONLY: "INFO",
    CLS_INVALID_PROGRAM: "LOW",
    CLS_NONTERMINATING: "LOW",
    CLS_EXCESSIVE_RESOURCE: "MEDIUM",
    CLS_INTERPRETER_CRASH: "MEDIUM",
    CLS_MEMORY_SAFETY: "MEDIUM",
    CLS_HOST_CAP_REQ: "HIGH",
    CLS_HOST_CAP_ESCAPE: "CRITICAL",
    CLS_FILESYSTEM_EFFECT: "CRITICAL",
    CLS_PROCESS_EFFECT: "CRITICAL",
    CLS_NETWORK_EFFECT: "CRITICAL",
    CLS_ENV_DISCLOSURE: "CRITICAL",
    CLS_UNKNOWN_EXTERNAL: "CRITICAL",
}


def classify(static: dict, outcome, canonical: dict, budget_exceeded: bool,
             interpreter_error: bool, max_steps: int) -> Dict:
    """Conservative classification. Fail closed on uncertainty."""
    if interpreter_error:
        return _verdict(CLS_INTERPRETER_CRASH, ORIGIN_INTERPRETER, ST_INCONCLUSIVE,
                        "interpreter raised while tracing the specimen")
    if static["malformed_cells"] > 0 and static["opcode_count"] == 0:
        return _verdict(CLS_INVALID_PROGRAM, ORIGIN_SPECIMEN, ST_DEMONSTRATED,
                        "no valid executable cells; malformed input")
    if budget_exceeded:
        return _verdict(CLS_NONTERMINATING, ORIGIN_SPECIMEN, ST_INCONCLUSIVE,
                        "execution exceeded budget; not classified safe (INV-008)")
    if outcome.halt_reason == "interpreter_error":
        return _verdict(CLS_INTERPRETER_CRASH, ORIGIN_INTERPRETER, ST_INCONCLUSIVE,
                        "interpreter error during execution")

    host = canonical.get("host_effects") or {}
    if host:
        top = max(host, key=host.get)
        cls = _host_class(top)
        return _verdict(cls, ORIGIN_HOST, ST_DEMONSTRATED,
                        "host-level effect observed at the interpreter seam")

    has_output = bool(outcome.output)
    has_halt = outcome.halted and outcome.halt_reason == "halt_opcode"
    vm_effects = canonical.get("vm_effects") or {}
    only_vm = set(vm_effects) <= {"VM_READ", "VM_WRITE", "VM_JUMP",
                                  "VM_ARITHMETIC", "STEP"}
    if has_output and has_halt:
        cls = CLS_OUTPUT_ONLY
        status = ST_DEMONSTRATED
    elif not has_output and only_vm:
        cls = CLS_PURE_VM_COMPUTE
        status = ST_DEMONSTRATED
    elif not has_output and not has_halt:
        cls = CLS_PURE_VM_COMPUTE
        status = ST_NOT_DEMONSTRATED
    else:
        cls = CLS_OUTPUT_ONLY
        status = ST_DEMONSTRATED
    return _verdict(cls, ORIGIN_SPECIMEN, status,
                    f"VM-only effects; output={len(outcome.output)} chars, "
                    f"halted={outcome.halted} ({outcome.halt_reason})")


def _host_class(top_effect: str) -> str:
    from .effects import (
        HOST_FILE_READ, HOST_FILE_WRITE, HOST_PROCESS_START, HOST_NETWORK,
        HOST_ENV_READ, HOST_NATIVE_CALL,
    )
    if top_effect in (HOST_FILE_READ, HOST_FILE_WRITE):
        return CLS_FILESYSTEM_EFFECT
    if top_effect == HOST_PROCESS_START:
        return CLS_PROCESS_EFFECT
    if top_effect == HOST_NETWORK:
        return CLS_NETWORK_EFFECT
    if top_effect == HOST_ENV_READ:
        return CLS_ENV_DISCLOSURE
    if top_effect == HOST_NATIVE_CALL:
        return CLS_HOST_CAP_ESCAPE
    return CLS_UNKNOWN_EXTERNAL


def _verdict(cls: str, origin: str, status: str, note: str) -> Dict:
    return {
        "security_class": cls,
        "origin": origin,
        "status": status,
        "severity": SEVERITY.get(cls, "LOW"),
        "note": note,
    }