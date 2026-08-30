# ANTIVIRUSBOLGE — Invariant Catalog

| # | Rule | Enforced (M0) |
|---|------|---------------|
| INV-001 | Malbolge VM state mutations remain inside VM-owned memory. | PASS by construction (Walbolge backend has no host writes) |
| INV-002 | No host process execution unless an explicit adapter declares and authorizes it. | PASS when `HOST_PROCESS_START` not exercised |
| INV-003 | No host filesystem effect unless explicitly declared. | PASS when no `HOST_FILE_*` exercised |
| INV-004 | No network effect unless explicitly declared. | PASS when `HOST_NETWORK` not exercised |
| INV-005 | Unknown external effect => DENY / INCONCLUSIVE. | PASS when no `HOST_UNKNOWN_EFFECT` |
| INV-006 | Interpreter crash != specimen compromise. | crash isolated as `INTERPRETER_CRASH`, origin `INTERPRETER_BEHAVIOR` |
| INV-007 | Resource exhaustion reported separately. | steps / peak_memory surfaced, not folded into a single verdict |
| INV-008 | Execution budget exceeded != safe. | budget exceeded -> `INCONCLUSIVE`, never `SAFE` |
| INV-009 | CAPABILITY_PRESENT != CAPABILITY_EXERCISED. | present / reachable / exercised kept as three distinct lists |
| INV-010 | technically_possible != authorized. | capability presence is not treated as authorization |

All ten invariants are evaluated per scan and reported with PASS/FAIL in the
report. A FAIL on INV-008 is *expected* and *correct* when a budget is hit —
that is the fail-closed behavior, not an error.