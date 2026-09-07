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
from pathlib import Path
from typing import List, Optional

from .effects import canonical_effects_from_events, effects_to_signature

WALBOLGE_PATH = os.environ.get("AVB_WALBOLGE_PATH")


def ensure_walbolge() -> None:
    if not WALBOLGE_PATH:
        raise RuntimeError(
            "Walbolge path not configured: set the AVB_WALBOLGE_PATH "
            "environment variable to the Walbolge repository directory")
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
    final_state: Optional[dict] = None
    memory_snapshot: Optional[list] = None
    variant: str = "classic_3_10"


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
    if name == "oracle":
        return OracleBackend()
    if name == "autobolge":
        return AutobolgeBackend()
    if name == "bolge19":
        return Bolge19Backend()
    raise ValueError(f"Unknown backend: {name}")


BOLGE19_EXE = os.environ.get(
    "AVB_BOLGE19_EXE",
    str(Path(__file__).resolve().parent.parent / "tools" / "bolge19.exe"))


class Bolge19Backend:
    """malbolge-lisp-forensics bolge19: native Zig Malbolge Unshackled 3^19 VM.

    IMPORTANT: this is a DIFFERENT Malbolge variant (Unshackled, END=3^19,
    fast20 semantics). A classic 3^10 specimen runs under it but yields a
    different observation model (hello: 47 steps / different bytes vs 48 /
    'Hello, world.' on 3^10 backends). It is a 5th independent backend but not a
    parity peer for classic specimens; crossval groups by variant."""
    name = "bolge19"
    version = "0.1.0"
    language = "Zig"
    variant = "unshackled_3_19"
    host_map = HostCapabilityMap(
        backend="bolge19",
        capabilities_present=["HOST_PROCESS_START"],
        capabilities_reachable=[],
        capabilities_exercised=[],
        boundary_violations=0,
        seam="antivirusbolge.interpreter.Bolge19Backend -> bolge19.exe (subprocess) -> main.zig",
    )

    def trace(self, text: str, max_steps: int, max_events: Optional[int],
              classic: bool = False) -> BackendOutcome:
        import re
        import subprocess
        import tempfile
        try:
            fd, path = tempfile.mkstemp(suffix=".mb")
            with os.fdopen(fd, "w", encoding="latin-1") as f:
                f.write(text)
            proc = subprocess.run(
                [BOLGE19_EXE, path, "--max-steps", str(max_steps)],
                capture_output=True, timeout=180)
            out = proc.stdout.decode("latin-1", "replace")
            err = proc.stderr.decode("latin-1", "replace")
        except Exception as exc:
            return BackendOutcome(steps=0, halted=False,
                                  halt_reason="interpreter_error",
                                  output="", peak_memory=0, error=f"bolge19: {exc}",
                                  variant=self.variant)
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass

        m = re.search(r"HALT steps=(\d+) c=\S+ d=\S+ a=\S+", err)
        if m:
            steps = int(m.group(1))
            return BackendOutcome(steps=steps, halted=True,
                                  halt_reason="halt_opcode", output=out,
                                  peak_memory=0, variant=self.variant)
        m = re.search(r"steps=(\d+)", err)
        steps = int(m.group(1)) if m else max_steps
        return BackendOutcome(steps=steps, halted=False,
                              halt_reason="max_steps", output=out,
                              peak_memory=0, variant=self.variant)


AUTOBOLGE_EXE = os.environ.get("AVB_AUTOBOLGE_EXE")


class AutobolgeBackend:
    """Autobolge Zig 3^10 VM via BOLG1->BOLG2 container.

    An independent Malbolge VM written in Zig. The harness spawns bolge.exe as a
    host process (HOST_PROCESS_START present at adapter level); no specimen can
    reach or exercise it."""
    name = "autobolge"
    version = "0.1.0"
    language = "Zig"
    host_map = HostCapabilityMap(
        backend="autobolge",
        capabilities_present=["HOST_PROCESS_START"],
        capabilities_reachable=[],
        capabilities_exercised=[],
        boundary_violations=0,
        seam="antivirusbolge.interpreter.AutobolgeBackend -> bolge.exe (subprocess, BOLG1/BOLG2) -> zig/vm.zig",
    )

    def trace(self, text: str, max_steps: int, max_events: Optional[int],
              classic: bool = False) -> BackendOutcome:
        import struct
        import subprocess
        import tempfile
        if not AUTOBOLGE_EXE:
            return BackendOutcome(steps=0, halted=False,
                                  halt_reason="interpreter_error",
                                  output="", peak_memory=0,
                                  error="autobolge: set AVB_AUTOBOLGE_EXE "
                                        "to the Autobolge zig/bolge.exe path")
        try:
            cells = [ord(c) for c in text.strip()]
            blob = b"BOLG1" + struct.pack("<Q", 1)
            blob += struct.pack("<I", len(cells))
            for c in cells:
                blob += struct.pack("<I", c)
            blob += struct.pack("<I", 0)
            blob += struct.pack("<I", max_steps)
            tmp = tempfile.gettempdir()
            ib = os.path.join(tmp, "avb_bolg_in.bin")
            ob = os.path.join(tmp, "avb_bolg_out.bin")
            with open(ib, "wb") as f:
                f.write(blob)
            proc = subprocess.run([AUTOBOLGE_EXE, ib, ob],
                                  capture_output=True, timeout=120)
            data = open(ob, "rb").read()
        except Exception as exc:
            return BackendOutcome(steps=0, halted=False,
                                  halt_reason="interpreter_error",
                                  output="", peak_memory=0, error=f"autobolge: {exc}")

        try:
            if len(data) < 13 or data[:5] != b"BOLG2":
                return BackendOutcome(steps=0, halted=False,
                                      halt_reason="interpreter_error",
                                      output="", peak_memory=0,
                                      error=f"bad BOLG2 ({proc.returncode})")
            pos = 5
            (count,) = struct.unpack_from("<Q", data, pos); pos = 13
            (olen,) = struct.unpack_from("<I", data, pos); pos += 4
            out = data[pos:pos + olen]; pos += olen
            (steps, term) = struct.unpack_from("<QB", data, pos); pos += 9
            fc, fa, fd = struct.unpack_from("<III", data, pos)
        except Exception as exc:
            return BackendOutcome(steps=0, halted=False,
                                  halt_reason="interpreter_error",
                                  output="", peak_memory=0, error=f"parse: {exc}")

        halted = bool(term)
        halt_reason = "halt_opcode" if halted else "max_steps"
        return BackendOutcome(
            steps=steps, halted=halted, halt_reason=halt_reason,
            output=out.decode("latin-1", "replace"), peak_memory=0,
            final_state={"a": fa, "c": fc, "d": fd},
        )


def available_backends() -> dict:
    """Report which backends are invocable right now (presence-based)."""
    import os
    return {
        "walbolge": bool(WALBOLGE_PATH),
        "malbolge-engine": bool(MALBOLGE_ENGINE_EXE) and os.path.exists(MALBOLGE_ENGINE_EXE),
        "oracle": bool(ORACLE_PATH) and os.path.isdir(ORACLE_PATH),
        "autobolge": bool(AUTOBOLGE_EXE) and os.path.exists(AUTOBOLGE_EXE),
        "bolge19": os.path.exists(BOLGE19_EXE),
    }


MALBOLGE_ENGINE_EXE = os.environ.get("AVB_MALBOLGE_ENGINE")

ORACLE_PATH = os.environ.get("AVB_ORACLE_PATH")


def ensure_oracle() -> None:
    if not ORACLE_PATH:
        raise RuntimeError(
            "malbolge-oracle path not configured: set the AVB_ORACLE_PATH "
            "environment variable to the malbolge-oracle repository directory")
    if ORACLE_PATH not in sys.path:
        sys.path.insert(0, ORACLE_PATH)


class OracleBackend:
    """Reference-semantics VM (malbolge-oracle), in-process.

    Exposes final state (a, c, d) and the full 59049-cell memory, which makes
    it the deepest state-inspection backend available. Reference semantics
    written independently from the Iizawa spec (malbolge-oracle DIVERGENCES.md)."""
    name = "oracle"
    version = "0.1.0"
    language = "Python"
    host_map = HostCapabilityMap(
        backend="oracle",
        capabilities_present=[],      # in-memory VM, no host primitives
        capabilities_reachable=[],
        capabilities_exercised=[],
        boundary_violations=0,
        seam="antivirusbolge.interpreter.OracleBackend -> malbolge-oracle.Oracle",
    )

    def trace(self, text: str, max_steps: int, max_events: Optional[int],
              classic: bool = False) -> BackendOutcome:
        ensure_oracle()
        try:
            from oracle import Oracle
            o = Oracle()
            o.load_ascii(text)
            r = o.run(max_steps)
        except Exception as exc:
            return BackendOutcome(steps=0, halted=False, halt_reason="interpreter_error",
                                  output="", peak_memory=0, error=str(exc))
        # Oracle always uses classic semantics; map its result.
        halt_reason = r.halt_reason if r.halted else "program_end"
        return BackendOutcome(
            steps=r.steps, halted=r.halted, halt_reason=halt_reason,
            output=r.output, peak_memory=len(r.memory),
            final_state={"a": r.a, "c": r.c, "d": r.d},
            memory_snapshot=list(r.memory),
        )


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
        if not MALBOLGE_ENGINE_EXE:
            return BackendOutcome(steps=0, halted=False,
                                  halt_reason="interpreter_error",
                                  output="", peak_memory=0,
                                  error="malbolge-engine: set AVB_MALBOLGE_ENGINE "
                                        "to the malbolge-ipc.exe path")
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