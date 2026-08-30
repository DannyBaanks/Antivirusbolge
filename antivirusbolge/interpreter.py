"""Interpreter backend abstraction.

A backend turns a Malbolge specimen into canonical VM effects. The default
backend is Walbolge (pure Python, no host-capability surface). A backend must
declare its host-capability map: what host primitives it is *built* with, so
the analyzer never assumes safety it did not inspect.

The Walbolge backend is declared CAPABILITY_PRESENT: NONE because the
walbolge.trace core contains no subprocess, socket, ctypes, ffi, eval, or exec
of specimen content — only file reads of the specimen and report writes.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional

from .effects import canonical_effects_from_events, effects_to_signature

WALBOLGE_PATH = os.environ.get("AVB_WALBOLGE_PATH", r"C:\Development\ISyCo Git\Walbolge")


def ensure_walbolge() -> None:
    if WALBOLGE_PATH not in sys.path:
        sys.path.insert(0, WALBOLGE_PATH)


@dataclass
class BackendOutcome:
    steps: int
    halted: bool
    halt_reason: str
    output: str
    peak_memory: int
    events: List[dict] = field(default_factory=list)
    events_dropped: bool = False
    executed_positions: List[int] = field(default_factory=list)
    jumps_count: int = 0
    error: Optional[str] = None


@dataclass
class HostCapabilityMap:
    backend: str
    capabilities_present: List[str]
    capabilities_reachable: List[str]
    capabilities_exercised: List[str]
    boundary_violations: int = 0
    seam: str = ""

    def to_dict(self) -> dict:
        return {
            "backend": self.backend,
            "capabilities_present": self.capabilities_present,
            "capabilities_reachable": self.capabilities_reachable,
            "capabilities_exercised": self.capabilities_exercised,
            "boundary_violations": self.boundary_violations,
            "seam": self.seam,
        }


class WalbolgeBackend:
    """Runs a specimen inside the Walbolge VM tracer. No host effects possible."""
    name = "walbolge"
    version = "0.1.0"
    language = "Python"
    host_map = HostCapabilityMap(
        backend="walbolge",
        capabilities_present=[],      # verified by inspection: no host primitives
        capabilities_reachable=[],
        capabilities_exercised=[],
        boundary_violations=0,
    )

    def trace(self, text: str, max_steps: int, max_events: Optional[int],
              classic: bool = False) -> BackendOutcome:
        ensure_walbolge()
        from walbolge.decoder import decode_program
        from walbolge.trace import trace_program

        decoded = decode_program(text)
        # classic treats the RAW source as the tape; toolkit traces decoded opcodes.
        trace_source = text if classic else decoded.opcodes
        try:
            tr = trace_program(trace_source, max_steps=max_steps,
                               max_events=max_events, classic=classic)
        except Exception as exc:  # interpreter-side failure, not specimen success
            return BackendOutcome(steps=0, halted=False, halt_reason="interpreter_error",
                                  output="", peak_memory=0, error=str(exc))
        return BackendOutcome(
            steps=tr.steps,
            halted=tr.halted,
            halt_reason=tr.halt_reason,
            output=tr.output,
            peak_memory=tr.peak_memory,
            events=[e.to_dict() for e in tr.events],
            events_dropped=tr.events_dropped,
            executed_positions=sorted(tr.executed_positions),
            jumps_count=tr.jumps_count,
        )


def get_backend(name: str = "walbolge"):
    if name == "walbolge":
        return WalbolgeBackend()
    if name == "malbolge-engine":
        return MalbolgeEngineBackend()
    raise ValueError(f"Unknown backend: {name}")


MALBOLGE_ENGINE_EXE = os.environ.get(
    "AVB_MALBOLGE_ENGINE",
    r"C:\Development\ISyCo Git\Malbolge-Engine\malbolge-ipc.exe")


class MalbolgeEngineBackend:
    """Runs a specimen inside the C Malbolge-Engine VM via its JSONL IPC.

    Boundary map: the *adapter* launches the interpreter binary as a host
    process (HOST_PROCESS_START present at the harness level), but the C VM
    exposes no host operation to the specimen, so capabilities_reachable and
    capabilities_exercised stay empty. This is the seam recorded, not assumed.
    """
    name = "malbolge-engine"
    version = "0.1.0"
    language = "C"
    host_map = HostCapabilityMap(
        backend="malbolge-engine",
        capabilities_present=["HOST_PROCESS_START"],   # harness spawns the C binary
        capabilities_reachable=[],
        capabilities_exercised=[],
        boundary_violations=0,
        seam="antivirusbolge.interpreter.MalbolgeEngineBackend -> "
             "malbolge-ipc.exe (subprocess) -> vm_run",
    )

    def trace(self, text: str, max_steps: int, max_events: Optional[int],
              classic: bool = False) -> BackendOutcome:
        import json
        import subprocess
        try:
            proc = subprocess.Popen(
                [MALBOLGE_ENGINE_EXE], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except Exception as exc:
            return BackendOutcome(steps=0, halted=False, halt_reason="interpreter_error",
                                  output="", peak_memory=0, error=f"spawn: {exc}")
        try:
            banner = json.loads(proc.stdout.readline())
            if banner.get("status") != "ready":
                return BackendOutcome(steps=0, halted=False,
                                      halt_reason="interpreter_error",
                                      output="", peak_memory=0,
                                      error=f"banner: {banner}")
            request = {"id": 1, "op": "run", "program": text,
                       "steps": max_steps, "input": ""}
            proc.stdin.write(json.dumps(request) + "\n")
            proc.stdin.flush()
            resp = json.loads(proc.stdout.readline())
            try:
                proc.stdin.write(json.dumps({"id": 2, "op": "quit"}) + "\n")
                proc.stdin.flush()
            except Exception:
                pass
        except Exception as exc:
            return BackendOutcome(steps=0, halted=False,
                                  halt_reason="interpreter_error",
                                  output="", peak_memory=0, error=f"ipc: {exc}")
        finally:
            proc.kill()

        status = resp.get("status", "ERROR")
        steps = resp.get("steps", 0)
        output = resp.get("output", "") or ""
        if status == "OK":
            halt_reason, halted, error = "halt_opcode", True, None
        elif status == "INVALID":
            halt_reason, halted, error = "invalid_program", False, None
        elif status == "TIMEOUT":
            halt_reason, halted, error = "max_steps", False, None
        else:
            halt_reason, halted, error = "interpreter_error", False, status
        return BackendOutcome(
            steps=steps, halted=halted, halt_reason=halt_reason,
            output=output, peak_memory=0, error=error)