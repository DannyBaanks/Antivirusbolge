# ANTIVIRUSBOLGE — Architecture (M0)

## Pipeline

```
specimen.mal
  -> normalizer        (load bytes, SHA-256, decode opcodes, static analysis)
  -> interpreter       (Walbolge backend trace)
  -> effects           (canonical effect IR + signature)
  -> classify          (ORIGIN / STATUS / SECURITY_CLASS / severity)
  -> invariants        (INV-001..INV-010)
  -> receipt           (machine-readable verdict artifact)
  -> report            (.md human + .json machine)
```

## Module map

| module | responsibility |
|--------|----------------|
| `normalizer.py` | read specimen, SHA-256, `decode_program`, static findings (source chars, valid/malformed cells, bootstrap, non-opcode positions). No execution. |
| `interpreter.py` | backend abstraction; `WalbolgeBackend.trace()` runs a specimen in the VM tracer and returns `BackendOutcome` + declared `HostCapabilityMap`. |
| `effects.py` | canonical effect IR; maps backend events to VM effects; host effects separate; behavioral signature (trace hash / effect multiset / output hash / halt reason). |
| `classify.py` | `classify()` -> verdict dict (ORIGIN, STATUS, SECURITY_CLASS, severity). Fail-closed. |
| `invariants.py` | evaluates INV-001..INV-010. |
| `receipt.py` | `ExecutionReceipt` schema. |
| `analyzer.py` | orchestrates scan; budget enforcement (steps, wall time, output bytes); builds report dict. |
| `compare.py` | L0..L5 trace-level comparison ladder + OUTPUT_EQUAL_TRACE_DIFFERENT. |
| `parity.py` | cross-interpreter parity: same specimen on Walbolge (classic) vs Malbolge-Engine (C) -> SEMANTIC_PARITY / OUTPUT_DIVERGENCE / TRACE_DIVERGENCE / CRASH_ONLY_ONE_BACKEND / HOST_EFFECT_ONLY_ONE_BACKEND. |
| `rce.py` | defensive interpreter-boundary analysis: per-operation MALBOLGE_OPERATION -> INTERPRETER_HANDLER -> HOST_PRIMITIVE reachability map; classification NO_HOST_PATH_FOUND / HOST_PATH_PRESENT_NOT_REACHED / HOST_PATH_REACHED / HOST_EFFECT_OBSERVED / INCONCLUSIVE. Never constructs payloads. |
| `ir.py` | canonical analysis IR: AnalysisEvent / AnalysisResult. Adapters translate external results here; never invents fields a provider cannot show. |
| `workbench.py` | run() (one backend -> IR) + crossval() (all independent backends -> SEMANTIC_PARITY / DIVERGENCE / OBSERVATION_MODEL_DIFFERENCE / INCONCLUSIVE). |
| `debug.py` | debugger/RE over the Walbolge per-event trace: disassemble, step/rewind, breakpoints (pc/step), watchpoints (cell writes), state a/c/d, executed/written-region recovery, control flow. |
| `synthesis.py` | generate (meowbolge adapter) + roundtrip (verify on independent backends, never self-validated) + corpus_from_phrases. Coverage bounded by generator; full-text synthesis NOT_DEMONSTRATED. |
| `report.py` | renders .md and .json. |
| `cli.py` | commands: scan, run, crossval, backends, capabilities, disasm, state, debug, generate, roundtrip, corpus, trace, behavior, compare, parity, rce, interpreter-audit, verify. |

## Security superset (capability != authority)

Debugger/RE/differential/generation tools *observe or produce*; they do not
acquire security authority. The verdict always originates in the security core:
ORIGIN / STATUS / SECURITY_CLASS / SEVERITY / HOST_REACHABILITY / HOST_EFFECT.
A RE finding is evidence into the pipeline; it never by itself becomes a
verdict.

## Canonical effect IR

VM-level: `VM_READ, VM_WRITE, VM_JUMP, VM_ARITHMETIC, INPUT, OUTPUT, HALT, STEP, ERROR`.
Host-level (separate layer): `HOST_FILE_READ, HOST_FILE_WRITE, HOST_PROCESS_START,
HOST_NETWORK, HOST_ENV_READ, HOST_NATIVE_CALL, HOST_UNKNOWN_EFFECT`.

A host effect may only appear when a concrete seam demonstrates a host boundary
crossing. For the Walbolge backend the seam is structurally absent, so host
effects are always `{}` by construction.

## Backend contract

A backend must:
1. turn a specimen into canonical VM effects;
2. declare its `HostCapabilityMap` (present / reachable / exercised / boundary
   violations) — the analyzer never assumes safety it did not inspect;
3. expose budget (max_steps) and error isolation (interpreter crash != specimen).

Walbolge is consumed through an adapter; it is the evidence producer, not the
security authority.

## Behavioral normalization

Source hash and behavioral signature are distinct:

- source hash = SHA-256 of raw file bytes.
- behavioral signature = { trace_hash, effect_multiset, output_hash, halt_reason }.

Trace ladder (compare): L0 source, L1 output, L2 halt reason, L3 canonical
effects, L4 bounded trace hash, L5 final state (trace+output+halt). Same output
`!=` same behavior.

## Budget enforcement (fail closed)

`max_steps`, `max_wall_time_s`, `max_output_bytes`. If any budget is exceeded,
the verdict becomes `INCONCLUSIVE` (NOT `SAFE`), per INV-008.