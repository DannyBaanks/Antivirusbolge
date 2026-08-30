# ANTIVIRUSBOLGE — Known Limitations (M0)

1. **Two backends, one traced.** Walbolge (Python) exposes a per-event trace;
   Malbolge-Engine (C) exposes only output/steps/status via IPC. Cross-parity is
   therefore classified at the output/halt/steps level; `TRACE_DIVERGENCE` is not
   reachable because the C backend has no per-event trace to compare.

2. **`INPUT` is not consumed (Walbolge).** Walbolge marks the `/` opcode as an
   `input` event but never reads stdin; register `a` stays at its prior value.
   The analyzer reports INPUT conservatively and treats unread input as
   fail-closed, never as observed host I/O. Recorded, not hidden.

3. **`HOST_EFFECT_ONLY_ONE_BACKEND` is not reachable on this corpus.** Neither
   backend lets a specimen reach or exercise a host capability, so this
   classification stays NOT_DEMONSTRATED (it is implemented, not triggered).

4. **RCE / interpreter-boundary reachability analysis is implemented (defensive).**
   `rce.py` maps each Malbolge operation to its interpreter handler and host
   primitive by source inspection, and classifies the VM->host path.
   - walbolge -> `NO_HOST_PATH_FOUND` (no host primitive anywhere).
   - malbolge-engine -> `HOST_PATH_PRESENT_NOT_REACHED` (the adapter launches the
     C binary as a process, but no Malbolge operation reaches that seam).
   It never constructs payloads; existing specimens are only replayed for
   classification.

5. **Final-state hash is bounded, not exact.** `L5` final-state equality is
   approximated from the bounded trace hash + output hash + halt reason. Walbolge
   does not expose the final tape.

6. **Behavioral signature is bounded.** The canonical effect sequence is capped
   (see `effects.py`); beyond the cap only counts are kept.

7. **No wall-clock guarantee for very long programs.** `max_wall_time_s` is
   checked *after* the backend returns.

8. **`INVALID_PROGRAM` is a decode-level verdict.** A specimen with no valid
   instruction cells is classified INVALID; printable ASCII that decodes to some
   opcodes is treated as executable.

9. **Generation works via the compact generator; coverage scales with text
   length.** The `malbolge-generator` package lives at
   `C:\Development\E31-A-Nagoya\malbolge_toolkit\malbolge\` and is used by
   `generate_compact` (Malbolge-Translator). Short cybersecurity specimens
   generate in <1s and are ROUNDTRIP_PASS on 3 independent backends. The
   meowbolge generator (also wired) is fast only for easy character transitions.
   A full book chapter is feasible but slow (per-word search); the Quijote
   chapters in `Malbolge-Translator/artifacts/quijote` are real, pre-generated
   proof of that scale.

## Claim discipline

Allowed (M0+M1, demonstrated):
- "No host effect was observed on either backend in these bounded runs."
- "The malbolge-engine adapter launches the interpreter as a host process
  (HOST_PROCESS_START present), but no specimen can reach or exercise it."
- "hello_classic.mal shows SEMANTIC_PARITY across walbolge-classic and
  malbolge-engine (both 48 steps, `Hello, world.`)."

NOT allowed:
- "This program is universally safe." (not demonstrated)
- "Malbolge cannot execute malware." (not demonstrated)
- "All interpreters are vulnerable." (not demonstrated)