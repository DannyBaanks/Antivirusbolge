"""Synthesis / generation + roundtrip (M2-E, M2-F).

The generator is meowbolge (an existing, working text->Malbolge synthesizer).
A generated specimen is NEVER validated by its own generator: roundtrip() runs
it on independent interpreters (walbolge-classic, malbolge-engine, oracle) and
requires the exact target output on every backend. Per the M2 rule, correctness
first; size optimization is not a requirement.

Note on coverage: meowbolge's per-character search is fast for some transitions
and exponential (exhaustive fallback) for others. Long/arbitrary text is not
guaranteed feasible. This is recorded as a known limitation, not hidden.
"""
from __future__ import annotations

from typing import Dict, List

from .normalizer import load_specimen, static_analysis
from .workbench import run as _run


def generate(target_text: str, out_path: str = None, timeout_s: int = 120) -> str:
    """Generate a classic Malbolge specimen that outputs target_text."""
    import os
    import sys
    meow = os.environ.get("AVB_MEOWBOLGE_PATH", r"C:\Development\ISyCo Git\meowbolge")
    if meow not in sys.path:
        sys.path.insert(0, meow)
    import meowbolge
    prog = meowbolge.generar(target_text, ancho=40, verbose=False, rapido=True)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(prog)
    return prog


def generate_compact(text: str, out_dir: str, base_name: str = "specimen",
                     translator_path: str = None,
                     generator_path: str = None) -> str:
    """Generate with the compact word-by-word generator (Malbolge-Translator).

    Requires the malbolge-generator package. generator_path points at the
    toolkit dir that contains a `malbolge` package with a `generator` module.
    Returns the path to the generated .mal.
    """
    import os
    import sys
    gen = generator_path or os.environ.get(
        "AVB_MALBOLGE_GENERATOR",
        r"C:\Development\E31-A-Nagoya\malbolge_toolkit")
    if gen not in sys.path:
        sys.path.insert(0, gen)
    tr = translator_path or os.environ.get(
        "AVB_TRANSLATOR",
        r"C:\Development\ISyCo Git\Malbolge-Translator")
    if tr not in sys.path:
        sys.path.insert(0, tr)

    from pathlib import Path
    import tempfile
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkstemp(suffix=".txt", prefix="avb_in_")[1])
    try:
        tmp.write_text(text, encoding="utf-8")
        from malbolge_translator.cli import main
        rc = main(["--file", str(tmp), "--output-dir", str(out),
                   "--base-name", base_name])
        if rc != 0:
            raise RuntimeError(f"translator exit {rc}")
    finally:
        import time
        for _ in range(5):
            try:
                tmp.unlink(missing_ok=True)
                break
            except OSError:
                time.sleep(0.2)
    mal = out / f"{base_name}_full.mal"
    return str(mal)


def roundtrip(specimen_path: str, expected_text: str,
              max_steps: int = 5_000_000) -> dict:
    """Verify a specimen reproduces expected_text on independent interpreters."""
    backends = {"walbolge": dict(classic=True),
                "malbolge-engine": dict(classic=False),
                "oracle": dict(classic=False)}
    results = {}
    for b, kw in backends.items():
        try:
            r = _run(specimen_path, backend_name=b, max_steps=max_steps, **kw)
            results[b] = {
                "status": r.status, "output": r.output,
                "output_hash": r.output_hash,
                "halt": r.halt_reason, "steps": r.steps,
                "match": r.output == expected_text,
            }
        except Exception as exc:
            results[b] = {"status": "ERROR", "error": str(exc), "match": False}

    matched = [b for b, r in results.items() if r.get("match")]
    ok_outputs = {r["output"] for r in results.values()
                  if r.get("status") == "OK"}
    cross_backend_parity = len(ok_outputs) == 1
    observed = next(iter(ok_outputs), "") if len(ok_outputs) == 1 else None
    return {
        "specimen": specimen_path,
        "expected": expected_text,
        "results": results,
        "backends_matching": matched,
        "cross_backend_parity": cross_backend_parity,
        "observed_output": observed,
        "verdict": "ROUNDTRIP_PASS" if len(matched) >= 2 else "ROUNDTRIP_FAIL",
    }


def corpus_from_phrases(phrases: List[str], out_dir: str, max_steps: int = 5_000_000,
                        generate_each: bool = True) -> List[dict]:
    """Generate+verify a set of short specimens (a corpus) from phrases."""
    import hashlib
    from pathlib import Path
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    entries = []
    for i, phrase in enumerate(phrases):
        safe = "".join(c if c.isalnum() else "_" for c in phrase)[:24]
        p = out / f"gen_{i:02d}_{safe}.mal"
        if generate_each:
            prog = generate(phrase)
            p.write_text(prog, encoding="utf-8")
        raw = p.read_bytes()
        rt = roundtrip(str(p), phrase, max_steps=max_steps)
        entries.append({
            "phrase": phrase, "file": str(p),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "size": len(raw), "roundtrip": rt["verdict"],
            "backends_matching": rt["backends_matching"],
        })
    return entries