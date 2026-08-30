# ANTIVIRUSBOLGE — Test Matrix (M0 + M1)

Executed 2026-08-29 with `py -m pytest tests/test_avb.py` (12 tests).

| Test | Specimen | Expected | Result |
|------|----------|----------|--------|
| benign output specimen | `benign/quijote_ch001.mal` | `OUTPUT_ONLY`, DEMONSTRATED, halt_opcode | PASS |
| valid halting classic | `benign/hello_classic.mal` (classic) | halt detected, 48 steps, `Hello, world.` | PASS |
| long-running / budget | `stress/runaway.mal` (classic, max_steps=10) | budget exceeded -> INCONCLUSIVE (`NONTERMINATING_WITHIN_BUDGET`), INV-008 FAIL | PASS |
| malformed specimen | `malformed/invalid_chars.mal` | `INVALID_PROGRAM`, DEMONSTRATED | PASS |
| interpreter crash fixture | classify() direct, interpreter_error=True | `INTERPRETER_CRASH`, origin INTERPRETER_BEHAVIOR (INV-006) | PASS |
| interpreter host-capability fixture | `interpreter_boundary/probe_high_activity.mal` | host capabilities present/exercised = [], all invariants PASS | PASS |
| same-output different-trace | `truncated.mal` vs `invalid_chars.mal` | `OUTPUT_EQUAL_TRACE_DIFFERENT`, L1 output equal, L4 trace different | PASS |
| source hash != behavior signature | hello vs truncated | distinct source + trace hashes | PASS |
| **cross-interpreter parity (M1)** | `hello_classic.mal` walbolge vs malbolge-engine | `SEMANTIC_PARITY`, DEMONSTRATED, both 48 steps / `Hello, world.` | PASS |
| **boundary map distinguishes backends (M1)** | backend host_map | walbolge present=[], malbolge-engine present=[HOST_PROCESS_START], reachable/exercised=[] both | PASS |
| **RCE walbolge (M1)** | rce("walbolge") | `NO_HOST_PATH_FOUND`, 0 host paths, all operations unreachable | PASS |
| **RCE malbolge-engine (M1)** | rce("malbolge-engine") | `HOST_PATH_PRESENT_NOT_REACHED`, adapter launches binary but 0 specimen-reachable paths | PASS |

## Cross-interpreter detail

`hello_classic.mal` on both backends:

| backend | steps | halt | output_len | output |
|---------|-------|------|-----------|--------|
| walbolge (classic) | 48 | halt_opcode | 13 | `Hello, world.` |
| malbolge-engine (C) | 48 | halt_opcode | 13 | `Hello, world.` |

Classification: `SEMANTIC_PARITY` (output_match=true, halt_match=true).

## Boundary map (M1)

| backend | capabilities_present | reachable | exercised |
|---------|----------------------|-----------|-----------|
| walbolge | `[]` | `[]` | `[]` |
| malbolge-engine | `[HOST_PROCESS_START]` (harness spawns the C binary) | `[]` | `[]` |

Neither backend lets a *specimen* reach or exercise a host capability. The
presence of `HOST_PROCESS_START` on malbolge-engine is an adapter/harness
capability (launching the interpreter), not a specimen capability — INV-009
holds (present != exercised).

## Controls / negative results

- No specimen produced a host effect on either backend; neither backend exposes
  a specimen-reachable host seam.
- The `invalid_chars.mal` fixture was corrected twice: `!@#$` and `?` sequences
  actually decode to valid opcodes (Malbolge decode is injective per position);
  `)`*21 is the verified all-invalid corpus entry (see `specimen_manifest.json`).
- `runaway.mal` halts natively at 65 steps under classic (auto-encrypt makes a
  cell non-printable); budget handling is exercised by cutting at 10 steps.
- `TRACE_DIVERGENCE` / `HOST_EFFECT_ONLY_ONE_BACKEND` are not reachable on this
  corpus: the C backend exposes no per-event trace, and no specimen can cross to
  host on either backend.