# Antivirusbolge — provenance table

Classification legend:
- **ORIGINAL_TO_ANTIVIRUSBOLGE** — written for Antivirusbolge.
- **ORIGINAL_TO_OUR_PROJECT_FAMILY** — original to the author's wider ISyCo /
  E31-A family, not copied from upstream.
- **ADAPTED_UPSTREAM** — adapted from an upstream project (credit preserved).
- **VALIDATED_AGAINST_UPSTREAM** — our implementation, checked against upstream.
- **THIRD_PARTY_DEPENDENCY** — required external artifact (credit to its author).
- **HISTORICAL_PRIOR_ART** — exists independent of us (not invented here).
- **NOT_DEMONSTRATED** — presence/dependency not demonstrated.

CAPABILITY REUSE != IMPLEMENTATION AUTHORSHIP. INTEGRATION != INVENTION.

| Component | Identity | Provenance |
|-----------|----------|------------|
| Antivirusbolge workbench (analyzer, IR, classify, invariants, receipts, crossval, debugger/RE, synthesis pipeline) | ours | ORIGINAL_TO_ANTIVIRUSBOLGE |
| E31 Appendix C oracle (`e31/harness/oracle.py`) | ours, written from Iizawa 2005 Appendix C pseudocode | ORIGINAL_TO_OUR_PROJECT_FAMILY |
| E31 discrepancy documentation + 2 extractions | ours | ORIGINAL_TO_OUR_PROJECT_FAMILY |
| Walbolge (decompiler/tracer) | upstream, consumed as a backend | ADAPTED_UPSTREAM (author: Danny Banks / ISyCo family) |
| Malbolge-Engine (C VM) | upstream, consumed via IPC | ADAPTED_UPSTREAM |
| malbolge-oracle (reference VM) | upstream, consumed in-process | ADAPTED_UPSTREAM |
| Autobolge (Zig VM, BOLG1/BOLG2) | upstream, consumed via subprocess | ADAPTED_UPSTREAM |
| bolge19 (`bolge19.exe`) | built from our own `malbolge-lisp-forensics/src/bolge19/main.zig` | ORIGINAL_TO_OUR_PROJECT_FAMILY (implementation); see row below for its 3^19 images |
| MalbolgeLISP 3^19 Unshackled runtime images (`init_module.mb`/`core.mb`/`lisp.mb`) | upstream (iczelia/kspalaiologos malbolge-lisp) | THIRD_PARTY_DEPENDENCY / VALIDATED_AGAINST_UPSTREAM — needed for bolge19's native-variant demonstration |
| Malbolge-Translator + malbolge-generator package | upstream project family (wallstop toolkit vendored; generator package) | ADAPTED_UPSTREAM / VALIDATED_AGAINST_UPSTREAM |
| meowbolge generator | upstream family | ADAPTED_UPSTREAM |
| Malbolge language + spec | Ben Olmstead (1998); Iizawa et al. (2005) paper | HISTORICAL_PRIOR_ART |
| `<`/`/` spec-vs-interpreter reversal | esolangs.org documentation (pre-existing) | HISTORICAL_PRIOR_ART |
| MalbolgeLISP on a genuine 3^19 Unshackled specimen | — | NOT_DEMONSTRATED (no clean text-output 3^19 specimen bundled; gated on MalbolgeLISP images) |

## The table in one line

We claim the workbench, the independent oracle, the discrepancy documentation,
and the integration/security-attribution layer — all original to our project
family. Everything else (the language, the reversal, the upstream interpreters,
generators, and MalbolgeLISP images) is credited upstream and reused, not
invented.