# Iizawa 2005 — Priority / prior-art search for the I/O discrepancy

Date of search: 2026-08-30 (Antivirusbolge historical-claim dossier).

## Question

Was the internal inconsistency between §2.2 and Appendix C of Iizawa et al.
(2005) — and the underlying `<`/`/` I/O reversal — publicly documented before
E31-A (2026-08-13)?

## Queries run

| Query / source | Date | Result |
|----------------|------|--------|
| DuckDuckGo: "Iizawa 2005 Malbolge IEICE input output Appendix C discrepancy" | 2026-08-30 | No results |
| esolangs.org/wiki/Malbolge | 2026-08-30 | **Prior-art data point found (see below)** |
| DuckDuckGo: "malbolge disassembler OR debugger OR differential testing tool" | 2026-08-30 | No Malbolge-specific security analyzer |
| DuckDuckGo: "Malbolge behavioral security analysis verdict VM host boundary" | 2026-08-30 | No Malbolge-specific security analyzer |
| esolangs.org wiki search "Malbolge analysis debugger security" | 2026-08-30 | No results |

## Key prior-art data point (esolangs.org/wiki/Malbolge, page last edited 13 Nov 2025)

The Malbolge esolang wiki documents the I/O instruction-table convention and an
explicit note:

> "The table above uses a criterion for input and output instruction codes that
> matches the reference interpreter instead of the one from the specification,
> **which are reversed with respect to each other**."

This is public, dated prior art (page revision last edited 13 Nov 2025) that
already records that the Malbolge **specification** and the **reference
interpreter** assign `<` and `/` in opposite directions. It does **not** cite
Iizawa 2005 or its internal §2.2/Appendix C inconsistency specifically.

## What this means for the claims

- **The underlying `<`/`/` reversal (spec vs reference interpreter) is KNOWN
  prior art.** We do NOT claim to have discovered that inversion.
- The E31-A finding is **consistent with** that known quirk: Iizawa §2.2 labels
  match the specification side (`<`=INPUT, `/`=OUTPUT), while Appendix C code
  matches the reference-interpreter side (`<`=putc, `/`=getc). The paper mixes
  the two conventions inside one document.
- **The scoped, defensible independent finding** is: the *specific internal
  inconsistency inside Iizawa et al. (2005)* — §2.2 labels vs the same paper's
  Appendix C code — was independently documented by E31-A (2026-08-13) with two
  independent PDF extractions. Whether a specific report of *that paper's*
  internal inconsistency predates E31-A is not resolved by this search.

## Status

**CONTEMPORARY / INCONCLUSIVE.** The esolangs page documents the underlying
spec/interpreter reversal (prior art for the *phenomenon*), but no earlier
report of the *specific Iizawa 2005 internal §2.2↔Appendix C inconsistency* was
found. Absence of a search hit is NOT proof of first report.

## Search limitations

- Single-search-engine (DuckDuckGo) + esolangs.org only.
- No Japanese-language search (the paper and its Nagoya project pages are
  Japanese) — a likely gap for this paper.
- No GitHub code-search / issue-tracker sweep for "Iizawa" or the specific
  symbols, no academic database (CiNii/CiNii Articles would be the natural
  Japanese index), no paper-revision/erratum check at the IEICE / Nagoya page.
- The IEICE Technical Report SS2005-22 revision history was not directly
  verified.