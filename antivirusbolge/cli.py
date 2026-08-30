"""CLI for ANTIVIRUSBOLGE.

Commands:
    scan   <specimen.mal>     full scan + verdict + receipt
    run    <specimen.mal>     execute on one backend -> canonical IR
    crossval <specimen.mal>   execute on all independent backends + compare
    backends                  list invocable backends
    capabilities              prior-art capability matrix summary
    disasm <specimen.mal>     decode each cell -> opcode
    state <specimen.mal> --step N   state (a/c/d) at a step
    debug <specimen.mal>      run with breakpoints/watchpoints
    trace  <specimen.mal>     trace excerpt (first N events)
    behavior <specimen.mal>   behavioral signature only
    compare <a.mal> <b.mal>   trace-level comparison ladder
    parity <specimen.mal>     cross-interpreter parity (walbolge vs malbolge-engine)
    rce <backend>             defensive interpreter-boundary analysis
    interpreter-audit <backend>  host capability boundary map
    verify <report.json>      re-print a stored report's verdict summary
"""
from __future__ import annotations

import argparse
import json
import sys

from . import __version__


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="antivirusbolge",
                                     description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--max-steps", type=int, default=5_000_000)
    parser.add_argument("--max-events", type=int, default=None)
    parser.add_argument("--max-output-bytes", type=int, default=256 * 1024)
    parser.add_argument("--max-wall-time", type=float, default=60.0)
    parser.add_argument("--classic", action="store_true")
    parser.add_argument("--json", help="Write machine-readable report to this path")
    parser.add_argument("--md", help="Write human-readable report to this path")

    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="Full scan + verdict")
    p_scan.add_argument("specimen")
    p_scan.set_defaults(handler="scan")

    p_trace = sub.add_parser("trace", help="Trace excerpt")
    p_trace.add_argument("specimen")
    p_trace.add_argument("--limit", type=int, default=40)
    p_trace.set_defaults(handler="trace")

    p_behavior = sub.add_parser("behavior", help="Behavioral signature only")
    p_behavior.add_argument("specimen")
    p_behavior.set_defaults(handler="behavior")

    p_cmp = sub.add_parser("compare", help="Compare two specimens")
    p_cmp.add_argument("a")
    p_cmp.add_argument("b")
    p_cmp.set_defaults(handler="compare")

    p_verify = sub.add_parser("verify", help="Re-print a stored report's verdict")
    p_verify.add_argument("report")
    p_verify.set_defaults(handler="verify")

    p_parity = sub.add_parser("parity", help="Cross-interpreter parity")
    p_parity.add_argument("specimen")
    p_parity.set_defaults(handler="parity")

    p_audit = sub.add_parser("interpreter-audit", help="Host capability boundary map")
    p_audit.add_argument("backend")
    p_audit.set_defaults(handler="audit")

    p_rce = sub.add_parser("rce", help="Defensive interpreter-boundary analysis")
    p_rce.add_argument("backend")
    p_rce.set_defaults(handler="rce")

    p_run = sub.add_parser("run", help="Execute on one backend -> canonical IR")
    p_run.add_argument("specimen")
    p_run.add_argument("--backend", default="walbolge")
    p_run.set_defaults(handler="run")

    p_cross = sub.add_parser("crossval", help="Cross-validate across independent backends")
    p_cross.add_argument("specimen")
    p_cross.set_defaults(handler="crossval")

    p_back = sub.add_parser("backends", help="List invocable backends")
    p_back.set_defaults(handler="backends")

    p_caps = sub.add_parser("capabilities", help="Prior-art capability matrix summary")
    p_caps.set_defaults(handler="capabilities")

    p_dis = sub.add_parser("disasm", help="Decode each program cell -> opcode")
    p_dis.add_argument("specimen")
    p_dis.add_argument("--limit", type=int, default=40)
    p_dis.set_defaults(handler="disasm")

    p_state = sub.add_parser("state", help="Show VM state at a step")
    p_state.add_argument("specimen")
    p_state.add_argument("--step", type=int, required=True)
    p_state.set_defaults(handler="state")

    p_debug = sub.add_parser("debug", help="Run with breakpoints/watchpoints")
    p_debug.add_argument("specimen")
    p_debug.add_argument("--bp-pc", type=int, action="append", default=None)
    p_debug.add_argument("--bp-step", type=int, action="append", default=None)
    p_debug.add_argument("--wp-cell", type=int, action="append", default=None)
    p_debug.set_defaults(handler="debug")

    args = parser.parse_args(argv)
    common = {
        "max_steps": args.max_steps,
        "max_events": args.max_events,
        "max_output_bytes": args.max_output_bytes,
        "max_wall_time_s": args.max_wall_time,
        "classic": args.classic,
    }
    handler = getattr(sys.modules[__name__], f"_cmd_{args.handler}")
    return handler(args, common)


def _cmd_scan(args, common) -> int:
    from .analyzer import scan
    from .report import render_md, render_json, write_report
    report = scan(args.specimen, **common)
    print(render_md(report))
    if args.md:
        json_out = args.json or (args.md.rsplit(".", 1)[0] + ".json")
        write_report(report, args.md, json_out)
        print(f"\nReports: {args.md} / {json_out}")
    elif args.json:
        from pathlib import Path
        p = Path(args.json)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(render_json(report), encoding="utf-8")
        print(f"\nReport: {p}")
    return 0


def _cmd_trace(args, common) -> int:
    from .analyzer import scan
    report = scan(args.specimen, max_events=args.limit, **common)
    o = report["outcome"]
    print("TRACE (first events)")
    for ev in o["events"][:args.limit]:
        out = f" -> {ev['output_char']!r}" if ev.get("output_char") else ""
        jmp = f" -> {ev['jump_target']}" if ev.get("jump_target") is not None else ""
        print(f"  step={ev['step']:>6} c={ev['c']:>6} op={ev['instruction']:>2} "
              f"a={ev['a_before']:>8} {ev['event_type']}{out}{jmp}")
    print(f"\nsteps={o['steps']} halted={o['halted']} reason={o['halt_reason']} "
          f"output_len={len(o['output'])}")
    return 0


def _cmd_behavior(args, common) -> int:
    from .analyzer import scan, behavior_signature
    report = scan(args.specimen, **common)
    print(json.dumps(behavior_signature(report), indent=2, ensure_ascii=False))
    return 0


def _cmd_compare(args, common) -> int:
    from .compare import compare
    result = compare(args.a, args.b, **common)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def _cmd_parity(args, common) -> int:
    from .parity import parity
    print(json.dumps(parity(args.specimen, max_steps=args.max_steps),
                     indent=2, ensure_ascii=False))
    return 0


def _cmd_audit(args, common) -> int:
    from .interpreter import get_backend
    backend = get_backend(args.backend)
    print(json.dumps(backend.host_map.to_dict(), indent=2, ensure_ascii=False))
    return 0


def _cmd_rce(args, common) -> int:
    from .rce import analyze_rce
    print(json.dumps(analyze_rce(args.backend), indent=2, ensure_ascii=False))
    return 0


def _cmd_run(args, common) -> int:
    from .workbench import run
    r = run(args.specimen, backend_name=args.backend, max_steps=args.max_steps)
    print(json.dumps(r.to_dict(), indent=2, ensure_ascii=False))
    return 0


def _cmd_crossval(args, common) -> int:
    from .workbench import crossval
    print(json.dumps(crossval(args.specimen, max_steps=args.max_steps),
                     indent=2, ensure_ascii=False))
    return 0


def _cmd_backends(args, common) -> int:
    from .interpreter import available_backends
    print(json.dumps(available_backends(), indent=2))
    return 0


def _cmd_capabilities(args, common) -> int:
    from pathlib import Path
    import json as _json
    p = Path(__file__).resolve().parent.parent / "evidence" / "PRIOR_ART_CAPABILITY_MATRIX.json"
    m = _json.loads(p.read_text(encoding="utf-8"))
    print(f"{len(m['rows'])} capabilities as_of {m['as_of']}")
    by = {}
    for r in m["rows"]:
        s = r["status"].split(" ")[0]
        by[s] = by.get(s, 0) + 1
    print(_json.dumps(by, indent=2))
    return 0


def _cmd_disasm(args, common) -> int:
    from .debug import disassemble
    ins = disassemble(args.specimen)
    print(f"decoded {len(ins)} cells (first {args.limit}):")
    for i in ins[:args.limit]:
        print(f"  [{i['pos']:>4}] char={i['char']!r} opcode={i['opcode']}")
    return 0


def _cmd_state(args, common) -> int:
    from .debug import state_at
    from .normalizer import load_specimen
    from .interpreter import ensure_walbolge
    from walbolge.decoder import decode_program
    from walbolge.trace import trace_program
    _, text = load_specimen(args.specimen)
    ensure_walbolge()
    dec = decode_program(text)
    tr = trace_program(dec.opcodes, max_steps=args.max_steps, classic=False)
    ev = state_at([e.to_dict() for e in tr.events], args.step)
    print(json.dumps(ev if ev else {"error": f"no event at step {args.step}"},
                     indent=2, ensure_ascii=False))
    return 0


def _cmd_debug(args, common) -> int:
    from .debug import run_debug
    r = run_debug(args.specimen, breakpoints_pc=args.bp_pc,
                  breakpoints_step=args.bp_step, watchpoints_cell=args.wp_cell,
                  max_steps=args.max_steps)
    print(json.dumps(r, indent=2, ensure_ascii=False))
    return 0


def _cmd_verify(args, common) -> int:
    from pathlib import Path
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    v = report["verdict"]
    r = report["receipt"]
    print(f"Specimen    : {report['specimen_path']}")
    print(f"Classification: {v['security_class']}")
    print(f"Status      : {v['status']}")
    print(f"Severity    : {v['severity']}")
    print(f"Origin      : {v['origin']}")
    print(f"Host effects: {r['host_effects'] or 'NONE'}")
    print(f"Budget      : exceeded={r['budget_exceeded']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())