"""Human-readable .md and machine-readable .json rendering of a scan."""
from __future__ import annotations

import json
from pathlib import Path


def render_md(report: dict) -> str:
    s = report["static"]
    o = report["outcome"]
    v = report["verdict"]
    c = report["canonical"]
    h = report["host_map"]
    b = report["budget"]
    sig = report["signature"]
    lines = []
    lines.append("ANTIVIRUSBOLGE")
    lines.append("=" * 14)
    lines.append("")
    lines.append(f"Specimen      : {report['specimen_path']}")
    lines.append(f"SHA256        : {s['sha256']}")
    lines.append(f"Interpreter   : {report['receipt']['interpreter_name']} "
                 f"{report['receipt']['interpreter_version']}")
    lines.append(f"Execution     : {o.get('steps', 0)} steps | "
                 f"peak_memory={o.get('peak_memory', 0)}")
    lines.append(f"Halt          : {o.get('halt_reason')} "
                 f"(halted={o.get('halted')})")
    lines.append(f"Decoded output: {o.get('output', '')!r}")
    lines.append("")
    lines.append("Static analysis:")
    lines.append(f"    source_chars={s['source_chars']} valid_cells={s['valid_cells']} "
                 f"malformed={s['malformed_cells']}")
    lines.append(f"    bootstrap={'present' if s['bootstrap'] else 'absent'}")
    lines.append("")
    lines.append("VM effects:")
    for fx, n in (c.get("vm_effects") or {}).items():
        lines.append(f"    {fx:<18} {n}")
    lines.append(f"Host capabilities present: {h['capabilities_present'] or 'NONE'}")
    lines.append(f"Host capabilities exercised: {h['capabilities_exercised'] or 'NONE'}")
    lines.append(f"Boundary violations: {h['boundary_violations']}")
    lines.append("")
    lines.append(f"Verdict       : {v['security_class']}")
    lines.append(f"Severity      : {v['severity']}")
    lines.append(f"Origin        : {v['origin']}")
    lines.append(f"Evidence      : {v['status']}")
    lines.append("")
    lines.append("Invariants:")
    for inv in report["invariants"]:
        mark = "PASS" if inv["pass"] else "FAIL"
        lines.append(f"    {inv['invariant']:<9} {mark}  {inv['note']}")
    lines.append("")
    lines.append("Budget:")
    lines.append(f"    exceeded={b.get('exceeded')} reason={b.get('reason')} "
                 f"wall={b.get('wall_time_s')}s")
    lines.append("")
    lines.append("Behavioral signature:")
    lines.append(f"    trace_hash={sig['trace_hash'][:16]}… "
                 f"effect_count={sig['effect_count']}")
    lines.append(f"    output_hash={sig['output_hash'][:16]}…")
    lines.append("")
    lines.append("Not demonstrated:")
    for nd in report["not_demonstrated"]:
        lines.append(f"    - {nd}")
    lines.append("")
    return "\n".join(lines)


def render_json(report: dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False)


def write_report(report: dict, md_path: str, json_path: str) -> None:
    p_md = Path(md_path)
    p_json = Path(json_path)
    p_md.parent.mkdir(parents=True, exist_ok=True)
    p_json.parent.mkdir(parents=True, exist_ok=True)
    p_md.write_text(render_md(report), encoding="utf-8")
    p_json.write_text(render_json(report), encoding="utf-8")