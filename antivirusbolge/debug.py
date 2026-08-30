"""Debugger / reverse-engineering capabilities (M2-D).

Built natively over the Walbolge per-event trace (the deepest trace available)
plus Walbolge decode/decompile. Capabilities:
  - DISASSEMBLE: decode each program cell to its opcode
  - single step / rewind: query state at any step from the event log
  - breakpoints: on program counter (c) or step number
  - watchpoints: on memory write position
  - state view: a/c/d/output at a step
  - memory write inspection: cell_before/cell_after on writes
  - executed-region recovery + control-flow (jumps)
"""
from __future__ import annotations

from typing import List, Optional

from .normalizer import load_specimen
from .interpreter import ensure_walbolge


def disassemble(specimen_path: str) -> List[dict]:
    """Decode every program cell to its opcode (DISASSEMBLE)."""
    ensure_walbolge()
    from walbolge.decoder import decode_program
    _, text = load_specimen(specimen_path)
    dec = decode_program(text)
    return [{"pos": p["index"], "char": p["char"], "opcode": p["opcode"]}
            for p in dec.positions]


def _trace_events(text: str, max_steps: int):
    ensure_walbolge()
    from walbolge.decoder import decode_program
    from walbolge.trace import trace_program
    dec = decode_program(text)
    return trace_program(dec.opcodes, max_steps=max_steps, max_events=None,
                         classic=False), dec


def state_at(events: List[dict], target_step: int) -> Optional[dict]:
    """State (a/c/d/output) at a given step, from the event log (rewind/forward)."""
    for ev in events:
        if ev["step"] == target_step:
            return {
                "step": ev["step"], "c": ev["c"], "d": ev["d"],
                "a": ev["a_after"], "opcode": ev["instruction"],
                "event_type": ev["event_type"],
                "output_char": ev["output_char"],
                "cell_before": ev["cell_before"], "cell_after": ev["cell_after"],
            }
    return None


def run_debug(specimen_path: str, breakpoints_pc: Optional[List[int]] = None,
              breakpoints_step: Optional[List[int]] = None,
              watchpoints_cell: Optional[List[int]] = None,
              max_steps: int = 5_000_000) -> dict:
    """Run and halt at the first breakpoint/watchpoint, returning the trigger."""
    _, text = load_specimen(specimen_path)
    trace, dec = _trace_events(text, max_steps)
    events = [e.to_dict() for e in trace.events]
    bp_pc = set(breakpoints_pc or [])
    bp_step = set(breakpoints_step or [])
    wp_cell = set(watchpoints_cell or [])

    trigger = None
    for ev in events:
        if ev["step"] in bp_step:
            trigger = {"kind": "breakpoint_step", "step": ev["step"], "state": state_at(events, ev["step"])}
            break
        if ev["c"] in bp_pc:
            trigger = {"kind": "breakpoint_pc", "c": ev["c"], "state": state_at(events, ev["step"])}
            break
        w = ev.get("write_c")
        if w is not None and w in wp_cell:
            trigger = {"kind": "watchpoint_write_c", "cell": w, "state": state_at(events, ev["step"])}
            break
        w = ev.get("write_d")
        if w is not None and w in wp_cell:
            trigger = {"kind": "watchpoint_write_d", "cell": w, "state": state_at(events, ev["step"])}
            break

    return {
        "steps": trace.steps,
        "halted": trace.halted,
        "halt_reason": trace.halt_reason,
        "output": trace.output,
        "trigger": trigger,
        "executed_positions": sorted(trace.executed_positions),
        "written_positions": sorted(trace.written_positions),
        "jumps": trace.jumps,
        "events_recorded": trace.events_recorded,
        "peak_memory": trace.peak_memory,
    }