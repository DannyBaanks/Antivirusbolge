# Iizawa 2005 — Priority / prior-art search for the I/O discrepancy

Date of search: 2026-08-30 (English + Japanese sweep).

## Question

Was the internal inconsistency between §2.2 and Appendix C of Iizawa et al.
(2005) — the specific contradiction in the assignment of the Malbolge `<` and
`/` I/O operations — publicly documented before E31-A (2026-08-13)?

This is distinct from the broader question of whether the Malbolge
spec-vs-reference-interpreter I/O reversal is known (it is; see below).

## Queries run (English + Japanese)

| Query / source | Language | Result |
|----------------|----------|--------|
| DuckDuckGo: exact paper title variants (`Programming Method in Obfuscated Language Malbolge`; `難読プログラミング言語Malbolgeにおけるプログラム構成手法`) | EN/JP | Paper well identified in CiNii / J-GLOBAL / Nagoya; no erratum found |
| DuckDuckGo: `飯澤 / 飯沢 Malbolge` | JP | Nagoya project page, Wikipedia, PDF mirror; no erratum |
| DuckDuckGo: `Malbolge 入出力 反転 仕様` (I/O reversed spec) | JP | Wikipedia/qiita/blog; documents the known spec↔interpreter reversal |
| esolangs.org/wiki/Malbolge | EN | **prior art**: spec vs reference interpreter I/O reversed |
| esolangs.org/wiki/Talk:Malbolge | EN | **2006 discussion of the Iizawa paper** (see below) |
| esolangs.org wiki search "Malbolge analysis debugger security" | EN | no results |
| CiNii Research | JP | paper record `CRID 1520572359236469376`; no erratum |
| J-GLOBAL | JP | paper record `JGLOBAL_ID 200902281986673262`; no erratum |
| GitHub global code search: `"Programming Method in Obfuscated Language Malbolge"`, `"SS2005-22" Malbolge`, `Iizawa reversed Malbolge`, `Iizawa putc Malbolge` | EN | **0 results each**; broad `Malbolge Iizawa` → ~5 files (documentation/references), none stating "§2.2 contradicts Appendix C" |
| CiNii: Iizawa master's thesis (2006) | JP | record `CRID 1574231874010037248` exists; full text not inspected (see OPEN SUSPECT) |

## Established prior art (NOT our discovery)

1. **esolangs.org/wiki/Malbolge** (page last edited 13 Nov 2025): the table "uses a
   criterion for input and output instruction codes that matches the reference
   interpreter instead of the one from the specification, which are reversed
   with respect to each other." — documents the spec↔reference-interpreter
   `<`/`/` reversal.
2. **Qiita (2023)**: a Japanese article on Malbolge states, in essence, `<` =
   output, `/` = input, and "in the original implementation they are reversed,"
   while also using Iizawa's paper as a terminology/programming reference.
3. **Lou Scheffer, "Programming in Malbolge"** and general Malbolge literature:
   the spec/interpreter I/O quirk is longstanding community knowledge.

These establish the broader reversal as prior art. We do NOT claim to have
discovered it.

## Near-miss prior art: esolangs.org/wiki/Talk:Malbolge (1 Jun 2006)

A 2006 discussion (Rune/Keymaker) found the Iizawa paper, obtained the Japanese
PDF, and discussed Appendix C:
- Rune: "the C code is obviously just a Malbolge interpreter."
- The discussion also links Iizawa's master's thesis (M2005) and a 2012 thesis
  with a Malbolge decompiler + an EOF-halting cat program (Appendix B).

The indexed discussion **does not** state the §2.2 ↔ Appendix C internal I/O
inconsistency for `<`/`/`. It recognizes Appendix C as an interpreter and
comments on the paper's content, but the specific self-contradiction is not
identified there. This is the closest public near-miss found; it does not
contain our claim, but it proves people examined the same document as early as
2006.

## OPEN SUSPECT (not resolved in this search)

**Iizawa's master's thesis (2005年度 cohort; M2005): "難解言語Malbolgeに基づく
プログラム難読化に関する研究"** (CiNii `CRID 1574231874010037248`, NII Article ID
`20001704788`; listed on the Nagoya `m-thema.html` page under 2005年度,
first author 飯澤 恒). Chronologically:

```
Jun 2005   paper
   ↓
M2005        Iizawa master's thesis (defended early 2006)
```

If the thesis states or implies the earlier paper's I/O symbols were inverted,
I4 would be contradicted. If it uses a consistent convention without mentioning
the earlier error, it shows later consistency but not necessarily a prior public
report of the discrepancy. If nothing appears, the claim strengthens.

**Full-text access attempted and FAILED in this search:**
- esolangs-linked PDF `http://www.is.nagoya-u.ac.jp/thesis/M2005/i/M350402019e.pdf`
  → 404 (host decommissioned).
- Current mirror variants on `www.trs.css.i.nagoya-u.ac.jp` → 404.
- `cir.nii.ac.jp/crid/1574231874010037248` → record not scrapeable (JS-heavy).
- `nagoya.repo.nii.ac.jp` search → HTTP 406 (blocked).
- No live public PDF found via DuckDuckGo.

The thesis is therefore **NOT accessible in this search**; the suspect remains
OPEN. Closing it requires the Nagoya thesis archive (access-restricted or
offline), a library interlibrary loan, or the author's copy.

## Status

**NO_EARLIER_EXPLICIT_REPORT_FOUND_IN_DOCUMENTED_SEARCH.**

- No earlier public source was found that explicitly identifies the *internal
  §2.2 ↔ Appendix C inconsistency* in Iizawa et al. (2005) for the `<`/`/`
  assignment.
- The broader spec↔reference-interpreter reversal IS prior art (esolangs,
  Qiita 2023, general Malbolge literature) and is explicitly not claimed.
- The 2026 esolangs Talk shows people examined the paper since 2006 without
  (in the indexed record) stating this specific contradiction.
- The 2006 thesis remains the last serious, unchecked suspect.

Absence of a search hit is NOT proof of first report.

## Search limitations

- Search engines used: DuckDuckGo, CiNii Research, J-GLOBAL, GitHub code search,
  esolangs.org (wiki + talk). Not exhaustive of all Japanese academic indexes
  (CiNii Articles full-text, J-STAGE full-text of SS2005-22 not opened).
- No direct full-text inspection of the 2006 thesis (the OPEN SUSPECT).
- No check of Nagoya thesis repository full text, no IEICE membership portal
  access, no paper-revision/erratum logs at IEICE.
- Date-sensitive: pages may be edited after 2026-08-30.