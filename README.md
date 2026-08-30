# ANTIVIRUSBOLGE

Defensive behavioral security analyzer for Malbolge. Given an opaque Malbolge
specimen, it reduces execution to canonical VM effects and produces a verdict
with evidence. It never builds payloads.

The goal is not "Malbolge looks scary." The goal is: **we can explain exactly
what this specimen did, what its interpreter allowed, and what crossed into the
host.**

## Core idea

`capability != authority` and `program behavior != host behavior`. The analyzer
keeps VM effects and host effects in separate layers, and only attributes a host
effect when a concrete interpreter seam demonstrates it.

For the default backend (Walbolge, pure Python), that seam is **structurally
absent**: the tracer core uses no subprocess, socket, ctypes, ffi, mmap, eval or
exec of specimen content. So host effects are `NONE` by construction, and the
remaining verdict space is VM-level and resource-level.

## Install / run

```bash
py -m antivirusbolge scan corpus/benign/quijote_ch001.mal
py -m pytest tests/test_avb.py -q
```

`py` (the Python launcher) is used because bare `python` may be shim-guarded on
this machine.

## Commands

| Command | Purpose |
|---------|---------|
| `scan <specimen>` | full scan + verdict + receipt |
| `run <specimen> [--backend B]` | execute on one backend -> canonical IR |
| `crossval <specimen>` | execute on all independent backends + compare |
| `backends` | list invocable backends |
| `capabilities` | prior-art capability matrix summary |
| `disasm <specimen>` | decode each cell -> opcode |
| `state <specimen> --step N` | VM state (a/c/d) at a step |
| `debug <specimen> [--bp-pc N] [--wp-cell N]` | run with breakpoints/watchpoints |
| `generate "<text>" [--out F]` | synthesize a classic specimen (meowbolge) |
| `roundtrip <specimen> --expect <text>` | verify on independent backends |
| `corpus <dir> --phrases "A;B"` | generate+verify a small corpus |
| `trace <specimen> [--limit N]` | first N trace events |
| `behavior <specimen>` | behavioral signature (source hash != trace hash) |
| `compare <a> <b>` | L0..L5 trace-level comparison ladder |
| `parity <specimen>` | cross-interpreter parity (walbolge vs malbolge-engine) |
| `interpreter-audit <backend>` | host capability boundary map per backend |
| `verify <report.json>` | re-print a stored report's verdict |

## Verdict model

Every finding carries `ORIGIN` (`SPECIMEN_BEHAVIOR` / `VM_BEHAVIOR` /
`INTERPRETER_BEHAVIOR` / `ADAPTER_BEHAVIOR` / `HOST_CAPABILITY` / `UNKNOWN`),
`STATUS` (`DEMONSTRATED` / `FALSIFIED` / `NOT_DEMONSTRATED` / `INCONCLUSIVE`),
a `SECURITY_CLASS` (`OUTPUT_ONLY`, `PURE_VM_COMPUTE`, `INVALID_PROGRAM`,
`NONTERMINATING_WITHIN_BUDGET`, `INTERPRETER_CRASH`, ...) and a conservative
`SEVERITY`. Budget exceedance yields `INCONCLUSIVE`, never `SAFE`.

## Two backends

- **Walbolge** (pure Python) — full per-event VM trace; host seam absent.
- **Malbolge-Engine** (C) — independent interpreter via JSONL IPC (output/steps/
  status). The harness spawns the binary as a process (declared
  `HOST_PROCESS_START` present), but no specimen can reach or exercise it.
- **malbolge-oracle** (Python) — independent reference VM exposing final
  state a/c/d and the full 59049-cell memory.

`parity` and `crossval` run the same specimen on independent backends and
classify parity/divergence. `hello_classic.mal` demonstrates `SEMANTIC_PARITY`
across all three (48 steps, `Hello, world.`).

## M2: workbench

M2 turned Antivirusbolge into a full-spectrum workbench over the independent
Malbolge VMs: canonical IR (`run`), cross-validation (`crossval`), debugger/RE
(`disasm`/`state`/`debug`), and a generation+roundtrip pipeline (`generate`/
`roundtrip`/`corpus`). The compact word-by-word generator (`malbolge-generator`,
found at `C:\Development\E31-A-Nagoya\malbolge_toolkit\malbolge\`) produces
short cybersecurity specimens verified ROUNDTRIP_PASS on all 3 independent
backends; the antivirus scans them OUTPUT_ONLY / no host effects. See
`evidence/CLAIM_GATE.md`: verdict **READY** (synthesis gap closed); the novelty
claim is conditional on a broader prior-art sweep.

## Structure

```
antivirusbolge/     core package (normalizer, interpreter, effects, classify,
                    invariants, receipt, analyzer, compare, parity, rce, ir,
                    workbench, debug, synthesis, report, cli)
corpus/             benign | malformed | stress | interpreter_boundary | generated | source
evidence/           threat_model, architecture, invariants, manifests, matrix,
                    tool discovery, claim gate, receipts
tests/              test_avb.py (20 tests)
```

The analyzer consumes **Walbolge** (the Malbolge->text decompiler) through an
adapter; Walbolge is the evidence producer, not the security authority.

Human operator guide (Spanish, commands with real output): `GUIA.md`.