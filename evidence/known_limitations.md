# ANTIVIRUSBOLGE — Known Limitations (M0)

1. **Single backend.** Only the Walbolge (Python) backend is wired. `compare`
   supports two specimens on one backend; cross-interpreter parity (Walbolge vs
   Malbolge-Engine) is M1.

2. **`INPUT` is not consumed.** Walbolge marks the `/` opcode as an `input`
   event but never reads stdin; register `a` stays at its prior value. The
   analyzer therefore reports INPUT conservatively and treats unread input as
   fail-closed, never as observed host I/O. Recorded, not hidden.

3. **Final-state hash is bounded, not exact.** `L5` final-state equality is
   approximated from the bounded trace hash + output hash + halt reason. Walbolge
   does not expose the final tape; a full final-state hash needs a backend
   change (M1).

4. **Behavioral signature is bounded.** The canonical effect sequence is capped
   (see `effects.py`); beyond the cap only counts are kept. Two long programs
   that differ only past the cap may share a trace hash. This is a deliberate
   bound to keep the trace finite.

5. **No wall-clock guarantee for very long programs.** `max_wall_time_s` is
   checked *after* the backend returns; a single pathological step could run long
   before the check. Step and output-byte budgets bound the practical cost.

6. **`INVALID_PROGRAM` is a decode-level verdict.** A specimen with no valid
   instruction cells is classified INVALID. A printable-ASCII program that decodes
   to *some* opcodes is treated as executable (as classic Malbolge does).

7. **Interpreter audit is single-backend.** `interpreter-audit` and the RCE
   boundary analysis (host-path reachability) are M1; for the Walbolge backend the
   host path is structurally absent, so the only honest M0 answer is
   `NO_HOST_PATH_FOUND`.

## Claim discipline

Allowed (M0, demonstrated):
- "No host effect was observed in this bounded run (and the backend has no host
  capability seam)."

NOT allowed (M0):
- "This program is universally safe." (not demonstrated)
- "Malbolge cannot execute malware." (not demonstrated)
- "All interpreters are vulnerable." (not demonstrated)
- "No malware exists because this specimen only prints text." (not demonstrated)