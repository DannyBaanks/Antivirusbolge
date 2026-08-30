# ANTIVIRUSBOLGE — Test Matrix (M0)

Executed 2026-08-29 with `py -m pytest tests/test_avb.py`.

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

## Cross-interpreter (M1, NOT_DEMONSTRATED)

Same specimen on Walbolge vs Malbolge-Engine and parity/divergence classification
is deferred to M1. Only a single manual cross-check is recorded: `hello.malbolge`
halts in 48 steps on both Walbolge classic trace and Malbolge-Engine (see
`Malbolge-Engine/README.md` and this repo's `interpreter_manifest.json`).

## Controls / negative results

- No specimen produced a host effect; the backend has no host-capability seam.
- The `invalid_chars.mal` fixture was corrected twice: `!@#$` and `?` sequences
  actually decode to valid opcodes (Malbolge decode is injective per position);
  `)`*21 is the verified all-invalid corpus entry (see `specimen_manifest.json`).
- `runaway.mal` halts natively at 65 steps under classic (auto-encrypt makes a
  cell non-printable); budget handling is exercised by cutting at 10 steps.