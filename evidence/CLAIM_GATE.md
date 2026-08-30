# ANTIVIRUSBOLGE — CLAIM GATE (M2 + historical/priority dossier)

## TARGET CLAIM

> "Antivirusbolge is a full-spectrum Malbolge analysis and security workbench:
> execution, debugging, reverse engineering, synthesis, differential validation,
> behavioral analysis, and explicit VM-to-host security attribution in one
> evidence-driven system."

## TARGET NOVELTY CLAIM (conditional)

> "To the best of our documented public-source review as of 2026-08-30,
> Antivirusbolge appears to be the first publicly documented Malbolge-specific
> platform combining traditional Malbolge execution, debugging, reverse
> engineering and synthesis with explicit behavioral security verdicts and
> VM/interpreter/adapter/host boundary attribution."

## REQUIRED_CAPABILITIES (from PRIOR_ART_CAPABILITY_MATRIX, 27 rows)

| Cluster | Capability | Status |
|---------|-----------|--------|
| execution | EXECUTE, TRACE, CORPUS_EXECUTION, MALFORMED_INPUT_ANALYSIS, RESOURCE_BUDGET_ANALYSIS | DEMONSTRATED (4 classic 3^10 backends + bolge19 3^19) |
| debugging | STEP, BREAKPOINT, WATCHPOINT, STATE_INSPECT, MEMORY_INSPECT, REWIND_OR_STEP_BACK | DEMONSTRATED |
| reverse-engineering | DISASSEMBLE, DECOMPILE_OR_HIGH_LEVEL_RECONSTRUCTION, CONTROL_FLOW_ANALYSIS, SELF_MODIFICATION_ANALYSIS, STRUCTURAL_ANALYSIS | DEMONSTRATED |
| synthesis | GENERATE_OR_SYNTHESIZE, ROUNDTRIP_VERIFY | DEMONSTRATED (compact generator + roundtrip on 3 independent backends) |
| differential | DIFFERENTIAL_EXECUTION, CROSS_INTERPRETER_PARITY | DEMONSTRATED (crossval on 4 classic 3^10 backends; variant-aware) |
| security | HOST_CAPABILITY_MAP, HOST_REACHABILITY, HOST_EFFECT_ATTRIBUTION, BEHAVIORAL_SECURITY_VERDICT, REPRODUCIBLE_RECEIPT, REPORT_VERIFY, INTERPRETER_CRASH_ATTRIBUTION | DEMONSTRATED |

## DEMONSTRATED (by execution, not prose)

- Execution + per-event trace across **4 independent classic 3^10 Malbolge VMs**
  (Walbolge, Malbolge-Engine C, malbolge-oracle, Autobolge Zig) plus a 5th,
  **bolge19 (Unshackled 3^19)**, isolated as a different variant.
- Cross-validation: `hello` -> `SEMANTIC_PARITY` on all 4 classic backends (48
  steps, identical output hash); a malformed specimen honestly reveals
  `SEMANTIC_DIVERGENCE`.
- Debugger/RE: disassemble, step/rewind, breakpoints (pc/step), watchpoints
  (cell writes), state a/c/d, executed/written-region recovery, control flow.
- Synthesis: `generate_compact` (Malbolge-Translator + malbolge-generator)
  produces cybersecurity specimens verified `ROUNDTRIP_PASS` on 3 independent
  backends (never self-validated); corpus of 10 scanned benign.
- Security core: ORIGIN/STATUS/SECURITY_CLASS/SEVERITY verdicts, per-backend host
  capability map, defensive RCE (walbolge `NO_HOST_PATH_FOUND`,
  malbolge-engine/autobolge `HOST_PATH_PRESENT_NOT_REACHED`), receipts + `verify`.

## HISTORICAL / PRIORITY CLAIMS

Separated by evidence threshold (never collapsed).

| Claim | Wording | Status |
|-------|---------|--------|
| I1 — observed a discrepancy | "On 2026-08-13 we observed a reproducible internal inconsistency between §2.2 and Appendix C of Iizawa et al. (2005) for `<`/`/`." | DEMONSTRATED (E31-A package, hashed, two extractions) |
| I2 — independently documented | "We independently documented and reproduced that inconsistency." | DEMONSTRATED (oracle written from paper text; pypdf second extraction) |
| I3 — apparent error in published description | "We independently identified an apparent inconsistency in the published I/O description of Iizawa 2005." | DEFENSIBLE, with the caveat that which side is "wrong" is authorial intent |
| I4 — no earlier public report found (specific) | "To the best of our documented public-source search as of August 30, 2026, we found no earlier public report explicitly identifying the internal inconsistency between §2.2 and Appendix C of Iizawa et al. (2005) in their assignment of the Malbolge `<` and `/` I/O operations." | NO_EARLIER_EXPLICIT_REPORT_FOUND_IN_DOCUMENTED_SEARCH (bounded by search limitations; 2006 thesis is the open suspect) |
| I5 — first to discover the I/O reversal | "We were the first to discover the Malbolge `<`/`/` I/O reversal." | **NOT_ALLOWED** — the reversal is prior art (esolangs, Qiita 2023, general Malbolge literature) |

## Protective distinction (mandatory alongside I4)

> The broader reversal between the original Malbolge **specification and
> reference interpreter** is established prior art and is **not** claimed as our
> discovery. Our finding concerns the independently documented **internal
> inconsistency within the Iizawa paper itself** (§2.2 labels vs Appendix C
> code).

```
KNOWN BEFORE US        OUR DOCUMENTED FINDING
Malbolge spec        ↔   Iizawa §2.2
Malbolge reference      Iizawa Appendix C
interpreter             internally inconsistent
I/O reversed            representation
```

> "We did not discover that Malbolge has conflicting historical semantics. We
> independently discovered that a major paper about Malbolge reproduces that
> conflict internally."

## Open suspect (I4 gate)

**Iizawa's master's thesis (2005年度 cohort, M2005): "難解言語Malbolgeに基づく
プログラム難読化に関する研究"** (CiNii `CRID 1574231874010037248`) is the last
serious unchecked item. If it states/implies the earlier paper's I/O symbols
were inverted, I4 is contradicted. **Full text was NOT obtainable in this
search** (esolangs-linked URL and current Nagoya mirror → 404; CiNii not
scrapeable; Nagoya repo → HTTP 406). The suspect remains OPEN (see
IIZAWA_PRIORITY_SEARCH.md, which records an action plan: author contact > ILL >
repo/archive retries > Wayback Machine). Closing it needs the Nagoya thesis
archive, an interlibrary loan, or the author's copy.

## HISTORICAL GENEALOGY (origin story, evidence-supported)

> "The project began with disagreement. Our first independent Malbolge oracle —
> a literal implementation of Iizawa 2005 Appendix C — did not agree with the
> paper's own §2.2 labels. Rather than decide which authority was wrong, we
> built additional observers and differential checks. That method — independent
> observers, pinned (not hidden) divergence, no single document or runtime as
> authority by decree — became the design principle of Antivirusbolge."

Evidence for the sequence: `evidence/HISTORICAL_TIMELINE.md` (T0..T7). The
earliest dated artifact is E31-A (2026-08-13). This is a *precedent* claim, not
a claim that E31-A already contained the workbench idea.

## MISSING / GAP

- **Full-book synthesis is a performance bound, not a correctness gap** (the
  compact generator produces correct compact specimens; per-word search cost
  scales with text length). Correctness demonstrated; throughput on a full book
  not demonstrated in-session.
- **bolge19 native-variant demonstration is NOT_DEMONSTRATED** — gated on
  third-party MalbolgeLISP 3^19 images (see README + PROVENANCE.md). This is the
  only external dependency; it does not affect the classic 3^10 parity claims.
- **I5 (first-to-discover the reversal) and Level-4 "absolute first" remain
  NOT_ALLOWED.**

## PRIOR_ART_CONFLICTS

Public search (2026-08-30, DuckDuckGo x3 + esolangs.org):
- `wallstop/malbolge-toolkit` + MalbolgeGenerator (generator/interpreter).
- `albertovillaosorno/malbolge` (C-to-Malbolge compiler lab, self-modifying-code
  analysis — RE/tooling prior art).
- esolangs.org/wiki/Malbolge — documents the **spec-vs-reference-interpreter
  `<`/`/` reversal** (prior art for the phenomenon).
- Generic AV/behavioral/formal-verification literature (NOT Malbolge-specific).

No source found that combines Malbolge execution+debugging+RE+synthesis with
explicit behavioral security verdicts + VM/interpreter/adapter/host attribution
as a security analyzer.

## SEARCH_LIMITATIONS

- 2026-08-30: DuckDuckGo (3 workbench queries + Iizawa-specific) + esolangs.org.
- Iizawa paper is Japanese; **no Japanese-language search** (CiNii / CiNii
  Articles / Nagoya project page) was run — a likely gap.
- No GitHub code-search / issue-tracker sweep; no paper-revision/erratum check.
- "First publicly documented" can only be *not-yet-contradicted*, not proven.

## VERDICT

**READY** for the workbench claim (all 27 capabilities DEMONSTRATED).

**READY** for the genealogy claim ("the project began with disagreement";
E31-A 2026-08-13 is the fossil date; the independent-oracle/discrepancy method
is documented, hashed, and reproducible).

**NOT_READY / NOT_ALLOWED** for:
- the novelty claim at Level 3 ("first publicly documented") — conditional,
  needs the Japanese/academic/GitHub sweep to complete;
- Level 4 ("absolute first") — NOT_ALLOWED;
- I5 ("first to discover the I/O reversal") — NOT_ALLOWED (prior art).

## CLAIM LADDER (summary)

| Level | Statement | Status |
|-------|-----------|--------|
| 1 | evidence-driven full-spectrum workbench | READY |
| 2 | novelty, conditional (no earlier combined platform found) | READY (conditional, with documented search limits) |
| 3 | "to the best of our documented public-source review … appears to be the first" | PENDING broader search |
| 4 | "absolute first ever" | NOT_ALLOWED |

Historical ladder: I1/I2 DEMONSTRATED, I3 DEFENSIBLE, I4
NO_EARLIER_EXPLICIT_REPORT_FOUND_IN_DOCUMENTED_SEARCH, I5 NOT_ALLOWED.