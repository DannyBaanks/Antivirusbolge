# Antivirusbolge — historical timeline / genealogy

Timestamps are from artifacts in this project family. We do not backdate
causality; each event lists what it demonstrated and what it did NOT yet contain.

| # | Date | Artifact / file | What was demonstrated | What was NOT yet known | Why it mattered |
|---|------|-----------------|-----------------------|------------------------|-----------------|
| T0 | 2026-08-13 | `E31-A-Nagoya/e31/harness/oracle.py` (sha256 ad790a82…) | A literal, independent implementation of Iizawa 2005 Appendix C semantics (written from the paper's pseudocode, not from any interpreter's source) | Nothing yet about the discrepancy | The "no single authority" posture is born: the paper text is the spec, implemented independently |
| T1 | 2026-08-13 | `E31-A-Nagoya/discrepancy/IIZAWA_2005_INPUT_OUTPUT_DISCREPANCY.md` | The oracle's Appendix C behavior disagrees with the paper's §2.2 labels for `<`/`/` | Which side (if any) the paper "got wrong" | The first documented friction between an independent observer and the textual authority |
| T2 | 2026-08-13 | pypdf second extraction (same package) | The inconsistency is in the PDF text, not an extraction artifact (pdfminer + pypdf agree) | Author intent | Kills the cheap "your extractor inverted the symbols" objection |
| T3 | 2026-08-13 | `e31/harness/cross_validate.py` + 29 smoke tests + evidence JSON | A second runtime (Sensei) and the oracle agree byte-for-byte on Appendix C semantics; 29/29 PASS | — | Instead of picking a side, a second observer is built; divergence (D1/D3) is pinned, not hidden |
| T4 | 2026-08-13.. | `RUST_BACKEND_INVESTIGATION.md`, `d3_probe.json` | malbolge-rs (2018, independent) takes a side on D3 (`/` EOF → a=59048), giving "two against one" on EOF semantics | — | Differential execution across ≥3 independent implementations becomes the method |
| T5 | (ecosystem) | Walbolge, Malbolge-Engine, malbolge-oracle, Autobolge, meowbolge, Malbolge-Translator (repos in `C:\Development\ISyCo Git`) | Independent interpreters, generators, decompiler | exact dates not re-verified in this dossier | The independent-observers idea, later reused as Antivirusbolge backends |
| T6 | 2026-08-30 | Antivirusbolge M1 (commits 8d412ce, 2116315, 3c9b7d6) | Behavioral security analyzer: execution, cross-interpreter parity, defensive RCE, receipts | full workbench scope | Applies the "independent observers + no single authority" method to security attribution |
| T7 | 2026-08-30 | Antivirusbolge M2 (commits 5d79ded..0613dcc, 2e35230) | Full workbench: 5 backends (4 classic 3^10 + bolge19), crossval variant-aware, debugger/RE, synthesis, claim gate | — | The genealogy matures into a unified evidence-driven system |

## Genealogy statement (methodological, not teleological)

The earliest dated artifact in this project family is E31-A (2026-08-13): a
literal Appendix C oracle built from the paper's own text. Its documented
observation — that the paper's §2.2 labels and its Appendix C code disagree —
was met not by choosing a side but by building additional observers and
differential checks. That methodological precedent (independent observers;
divergence pinned, not hidden; no single document or runtime as authority by
decree) reappears, two weeks later, as the design principle of Antivirusbolge:
multiple independent backends, cross-validation, receipts, variant attribution.

This is a *precedent* claim, not a claim that E31-A already contained the whole
later workbench idea. The sentence the evidence supports is:

> "The project began with disagreement: the first oracle did not match the
> paper, and rather than decide which was wrong, we built more observers."

Not retroactively: "the antivirus was always the plan."