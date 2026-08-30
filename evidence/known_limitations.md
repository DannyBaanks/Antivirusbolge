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

4. **RCE / interpreter-boundary reachability analysis is deferred.** The host
   path is structurally absent for both backends (present=HOST_PROCESS_START at
   adapter level only for malbolge-engine; specimen-reachable=[] everywhere), so
   the honest answer today is `NO_HOST_PATH_FOUND`. A dedicated RCE mode that
   maps MALBOLGE_OPERATION -> INTERPRETER_HANDLER -> ADAPTER -> HOST_PRIMITIVE
   is the next milestone.

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