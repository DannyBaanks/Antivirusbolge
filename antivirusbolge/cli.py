"""CLI for ANTIVIRUSBOLGE.

Commands:
    scan   <specimen.mal>     full scan + verdict + receipt
    trace  <specimen.mal>     trace excerpt (first N events)
    behavior <specimen.mal>   behavioral signature only
    compare <a.mal> <b.mal>   trace-level comparison ladder
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