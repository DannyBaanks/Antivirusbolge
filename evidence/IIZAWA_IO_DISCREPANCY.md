# Iizawa 2005 — input/output discrepancy audit

This document audits the discrepancy observed and documented by the E31-A
package (2026-08-13), now primary internal priority evidence for Antivirusbolge.

## CLAIM

The Iizawa et al. (2005) paper on Malbolge contains an internal inconsistency:
its §2.2 instruction table labels `<` as INPUT and `/` as OUTPUT, while its
Appendix C interpreter code implements the opposite (`<` = `putc`, `/` = `getc`).

## SOURCE

Hisashi Iizawa et al., "Malbolge — プログラム作成支援の試み" (the E31-A package
`REFERENCES.md`; IEICE Technical Report **SS2005-22**, full PDF mirrored on the
official Nagoya Malbolge project page).

## SOURCE_LOCATION

- **§2.2 instruction table**: `'<'` labeled `INPUT：入力命令` (input command);
  `'/'` labeled `OUTPUT：出力命令` (output command).
- **Appendix C interpreter pseudocode** (lines 1012-1048 of the pdfminer
  extraction): `case '<': putc( a, stdout ); break;` and
  `case '/': x = getc( stdin ); if ( x == EOF ) a = 59048; else a = x; break;`.

## EXPECTED_BEHAVIOR (relative to the paper as a coherent document)

Within a single document, the labels in §2.2 and the code in Appendix C should
agree on which opcode is input and which is output. They do not.

## OBSERVED_BEHAVIOR

Two independent PDF extractions of the official full document agree on BOTH
sides:
1. **pdfminer** — §2.2 reads `'<' … INPUT：入力命令` / `'/' … OUTPUT：出力命令`;
   Appendix C reads `case '<': putc(a, stdout)` / `case '/': getc(...)`.
2. **pypdf** (run 2026-08-13 for verification) — Appendix C reads identically.

Because two unrelated extraction engines reproduce the same content, an
extraction-level inversion of the two symbols is effectively ruled out: the
inconsistency is in the PDF text itself (the official mirror copy).

## SPECIMEN

E31-A used a constructed 91-byte op-column program (`e31/artifacts/program.seed{0,1}.mal`)
demonstrating single-pass `mem[86] = MEM1 + 1`; the I/O discrepancy was NOT
exercised by the shipped specimen (no `/`). The I/O behavior was pinned by the
oracle smoke tests (T5/T6) instead.

## INTERPRETERS / ORACLES

- **E31 Appendix C oracle** (`e31/harness/oracle.py`) — faithful translation of
  Appendix C pseudocode; `sha256 ad790a82fdf644acbde20f3db891570b99403659b4a331554f748d4921d90193`.
- **Sensei** (malbolge-toolkit, wallstop, vendored, MIT) — used as a second
  Appendix-C-semantics runtime.
- **malbolge-rs** (2018, independent) — third vote, added later in
  `e31/RUST_BACKEND_INVESTIGATION.md`.

## REPRO_COMMAND

```
cd C:\Development\E31-A-Nagoya
python e31/harness/smoke_test_oracle.py      # 29/29 PASS; T5/T6 pin < outputs, / inputs
# discrepancy text reproduced by two PDF extractions (see SOURCE_LOCATION)
```

## RAW_OUTPUT

`e31/evidence/oracle_smoke_tests.txt` → `RESULT: pass=29 fail=0`. D3 record:
oracle on `/` with EOF → `a = 59048` (Iizawa Appendix C); Sensei on `/` with
empty input → `InputUnderflowError`; malbolge-rs → `a = 59048`. Full D3 detail:
`e31/evidence/rust_backend_phase1/d3_probe.json`, `e31/RUST_BACKEND_INVESTIGATION.md`.

## VARIANT

Classic Malbolge, 3^10 (Iizawa Appendix C semantics). The `<`/`/` reversal is a
known spec-vs-reference-interpreter quirk (see IIZAWA_PRIORITY_SEARCH.md).

## ALTERNATIVE_EXPLANATIONS

1. **Extraction artifact** — RULED OUT: two independent engines (pdfminer, pypdf)
   reproduce the same inversion.
2. **§2.2 is a typo; Appendix C is intended** — PLAUSIBLE; the paper's own
   §2.2 agrees with the widely published Malbolge assignment, so if the spec is
   authoritative, Appendix C is the inverted side. Authors are the authority.
3. **Appendix C is a copy of the reference interpreter** (which uses the
   reversed convention) while §2.2 kept the spec labels — PLAUSIBLE and
   consistent with the esolangs prior-art note.
4. **The paper intended a non-standard Malbolge variant** — NOT SUPPORTED by
   available evidence.

## VERDICT

**DEMONSTRATED_DISCREPANCY** — an internal, reproducible inconsistency between
the paper's §2.2 labels and its Appendix C code is established. Which side
carries the intended assignment is **NOT resolved** by E31-A; that is the
authors' call (see COVER_NOTE_DRAFT.md, which asks them to confirm which is
intended).

Note: this is the specific *paper-internal* inconsistency. The broader `<`/`/`
spec-vs-interpreter reversal is prior art (esolangs) and is NOT claimed as an
original discovery.