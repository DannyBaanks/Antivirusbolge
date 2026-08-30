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

## Backends

- **Walbolge** (pure Python) — full per-event VM trace; host seam absent.
- **Malbolge-Engine** (C) — independent interpreter via JSONL IPC (output/steps/
  status). The harness spawns the binary as a process (declared
  `HOST_PROCESS_START` present), but no specimen can reach or exercise it.
- **malbolge-oracle** (Python) — independent reference VM exposing final
  state a/c/d and the full 59049-cell memory.
- **Autobolge** (Zig) — independent 3^10 VM via BOLG1->BOLG2 container.
- **bolge19** (Zig, malbolge-lisp-forensics) — native Malbolge **Unshackled
  3^19** VM (a different Malbolge variant). Runs `.mb`/image files.

> **bolge19 dependency note (the only one).** bolge19 itself is built from our
> own `malbolge-lisp-forensics/src/bolge19/main.zig` and compiles/runs with just
> Zig. But to run *properly in its native 3^19 variant* it needs a genuine
> Malbolge Unshackled 3^19 image, and those come from the third-party
> **MalbolgeLISP** runtime (`init_module.mb`/`core.mb`/`lisp.mb`). The `.mb`
> files floating in the corpus are actually classic 3^10 programs stored as
> `.mb`, so running them under bolge19 yields 3^19-interpreted output, not the
> intended bytes. Therefore bolge19's **native-variant demonstration is
> NOT_DEMONSTRATED** — it is gated on the third-party MalbolgeLISP images.
> **Everything else in Antivirusbolge runs entirely on its own**; only this one
> component depends on an external repo to demonstrate its native variant.

`parity` and `crossval` run the same specimen on independent backends and
classify parity/divergence **within the same Malbolge variant**. `hello_classic`
shows `SEMANTIC_PARITY` across the 4 classic 3^10 backends (48 steps, `Hello,
world.`); bolge19 (Unshackled 3^19) runs it at 47 steps / different bytes and is
reported separately as a distinct variant, not folded into parity. Backends may
expose different final-state models; parity is keyed on output + halt.

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

## Historical context and provenance

We do not claim to have invented the Malbolge ecosystem we depend on.
Antivirusbolge exists because of that ecosystem.

Prior interpreters, generators, MalbolgeLISP, and other research provided
important reference points and, in limited cases, upstream artifacts used for
validation. Their authorship is preserved (see `evidence/PROVENANCE.md`).

Our contribution is the evidence-driven workbench and the integration of
execution, debugging, reverse engineering, synthesis, differential validation,
behavioral security classification, and explicit VM/interpreter/adapter/host
attribution.

**The project began with disagreement.** The earliest dated artifact in this
project family is E31-A (2026-08-13): a literal, independent implementation of
the Iizawa et al. (2005) Appendix C Malbolge semantics, written from the paper's
own pseudocode. It did not agree with the paper's §2.2 labels for `<` and `/`.
Rather than choose which authority was wrong, we built additional observers and
differential checks. That method — independent observers, pinned (not hidden)
divergence, no single document or runtime as authority by decree — became the
design principle of Antivirusbolge. The I/O discrepancy is documented
separately, with reproducible evidence and exact provenance
(`evidence/IIZAWA_IO_DISCREPANCY.md`, `IIZAWA_ERRATUM_CANDIDATE.md`,
`IIZAWA_PRIORITY_SEARCH.md`, `HISTORICAL_TIMELINE.md`).

We claim the workbench, not the history we stand on. The goal is not to replace
the tools that came before it. The goal is to contribute enough original,
reproducible work to deserve a place beside them.

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