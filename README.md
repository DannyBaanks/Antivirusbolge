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
| `trace <specimen> [--limit N]` | first N trace events |
| `behavior <specimen>` | behavioral signature (source hash != trace hash) |
| `compare <a> <b>` | L0..L5 trace-level comparison ladder |
| `verify <report.json>` | re-print a stored report's verdict |

## Verdict model

Every finding carries `ORIGIN` (`SPECIMEN_BEHAVIOR` / `VM_BEHAVIOR` /
`INTERPRETER_BEHAVIOR` / `ADAPTER_BEHAVIOR` / `HOST_CAPABILITY` / `UNKNOWN`),
`STATUS` (`DEMONSTRATED` / `FALSIFIED` / `NOT_DEMONSTRATED` / `INCONCLUSIVE`),
a `SECURITY_CLASS` (`OUTPUT_ONLY`, `PURE_VM_COMPUTE`, `INVALID_PROGRAM`,
`NONTERMINATING_WITHIN_BUDGET`, `INTERPRETER_CRASH`, ...) and a conservative
`SEVERITY`. Budget exceedance yields `INCONCLUSIVE`, never `SAFE`.

## Structure

```
antivirusbolge/     core package (normalizer, interpreter, effects, classify,
                    invariants, receipt, analyzer, compare, report, cli)
corpus/             benign | malformed | stress | interpreter_boundary
evidence/           threat_model, architecture, invariants, manifests, receipts
tests/              test_avb.py (8 tests)
```

The analyzer consumes **Walbolge** (the Malbolge->text decompiler) through an
adapter; Walbolge is the evidence producer, not the security authority.

Human operator guide (Spanish, commands with real output): `GUIA.md`.