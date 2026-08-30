# Iizawa 2005 — erratum candidate (neutral scientific wording)

This is the neutral, third-party-reproducible statement of the finding. It does
not claim which side is "wrong"; it documents a reproducible internal
inconsistency and leaves authorial intent to the authors.

## Statement (recommended public wording)

> We independently identified a reproducible discrepancy between the published
> input/output description and the behavior of the interpreter code in Iizawa
> et al. (2005): §2.2 labels `<` as input and `/` as output, while Appendix C
> implements the opposite assignment. Two independent PDF extractions
> (pdfminer, pypdf) of the official full document reproduce the same inversion,
> so an extraction artifact is effectively ruled out. We do not resolve which
> side reflects the authors' intent; that remains for the authors to clarify.
> The underlying `<`/`/` spec-vs-reference-interpreter reversal is a known
> Malbolge quirk (documented by the esolangs community); our contribution is
> the specific, reproducible documentation of this paper's internal
> §2.2↔Appendix C inconsistency.

## Why "erratum candidate" and not "the paper is wrong"

- The paper is internally inconsistent (DEMONSTRATED_DISCREPANCY).
- Which side is erroneous is an authorial-intent question we cannot settle:
  §2.2 agrees with the widely published Malbolge assignment; Appendix C agrees
  with the reference interpreter.
- We reported it to the authors for clarification (COVER_NOTE_DRAFT.md) before
  claiming any resolution. In the absence of a published clarification, we
  preserve our independent finding, evidence, and provenance here without
  imputing intent.

## Minimal executable counterexample (third-party reproducible)

No Malbolge program is needed to expose the paper-internal inconsistency: it is
present in the paper's own text. To reproduce:

1. Obtain the official full IEICE SS2005-22 PDF (mirrored on the Nagoya
   Malbolge project page).
2. Extract §2.2 and Appendix C with pdfminer.
3. Re-extract with an independent engine (pypdf).
4. Confirm both extractions show §2.2 labeling `<` as INPUT and `/` as OUTPUT
   while Appendix C implements `case '<': putc(...)` and `case '/': getc(...)`.

Behavioral grounding (independent of trusting Antivirusbolge): the Appendix C
semantics are reproduced by the oracle smoke tests (T5/T6) and independently by
malbolge-rs (2018) on EOF (`a = 59048`), per `e31/evidence/rust_backend_phase1/d3_probe.json`.

## Status

DISCREPANCY DEMONSTRATED. ERRATUM CANDIDATE (authorial intent unresolved).
PRIORITY of the *paper-internal* observation: INCONCLUSIVE (see
IIZAWA_PRIORITY_SEARCH.md — no earlier report of this paper's inconsistency
found; the underlying reversal is prior art).