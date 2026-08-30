# E31-A — corrigendum to hashed source documents

The E31-A package hashes its source documents in `MANIFEST.json` (`files`:
`CLAIMS.md`, `discrepancy/IIZAWA_2005_INPUT_OUTPUT_DISCREPANCY.md`). To preserve
that integrity we do NOT rewrite those files in place. These two corrections are
an appended note that supersedes the stale lines.

Correction date: 2026-08-30.

## Correction 1 — CLAIMS.md C1 "No second PDF extraction was performed"

CLAIMS.md C1 limitation reads: *"No second PDF extraction was performed."*

**This is stale.** A second, independent extraction with **pypdf** was performed
on 2026-08-13 and is documented in C17, in
`discrepancy/IIZAWA_2005_INPUT_OUTPUT_DISCREPANCY.md` ("two independent
extractions, pdfminer + pypdf"), and in `MANIFEST.json` `discrepancy_status`
("confirmed in the paper's own text via two independent extractions (pdfminer,
pypdf)").

**Correct reading:** two independent extractions (pdfminer + pypdf) were
performed and agree. C17 and the manifest are authoritative; C1's "No second PDF
extraction" is a superseded line.

## Correction 2 — discrepancy doc §4 "Both runtimes agree on `<` and `/` semantics"

`discrepancy/IIZAWA_2005_INPUT_OUTPUT_DISCREPANCY.md`, §4 item 2 reads:
*"Both runtimes agree on `<` and `/` semantics."*

**This is imprecise.** The runtimes agree on the **direction** of the I/O
opcodes (`<` outputs, `/` inputs), but their **empty-input / EOF handling
differs** (D3). Precise wording:

> Both runtimes agree on the direction of the I/O opcodes (`<` outputs, `/`
> inputs), while their empty-input/EOF handling differs as separately
> documented in D3: on `/` with EOF, the oracle and malbolge-rs set `a = 59048`
> (Iizawa Appendix C), whereas Sensei raises `InputUnderflowError`.

Evidence: `e31/RUST_BACKEND_INVESTIGATION.md` D3 row;
`e31/evidence/rust_backend_phase1/d3_probe.json` (malbolge-rs also `a = 59048`).