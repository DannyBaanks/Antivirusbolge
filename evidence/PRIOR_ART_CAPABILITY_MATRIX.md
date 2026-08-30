# ANTIVIRUSBOLGE ? Prior-Art Capability Matrix

as_of 2026-08-30 ? method: code+execution evidence, not prose.

| capability | AVB_current | local_tool_provider | external_prior_art | implementation_mode | evidence | status |
|---|---|---|---|---|---|---|
| EXECUTE | run command (walbolge/engine/oracle) | walbolge, malbolge-engine, malbolge-oracle, autobolge | public Malbolge interpreters | native + adapter | tests + run crossval | DEMONSTRATED |
| TRACE | per-event trace (walbolge) | walbolge (TraceEvent) | debuggers/tracers | native (walbolge) | trace_excerpt | DEMONSTRATED |
| STEP | state at any step (event log rewinds) | malbolge-oracle (OracleResult state), walbolge debugger path | debuggers | adapter | state command + test | DEMONSTRATED |
| BREAKPOINT | debug --bp-pc/--bp-step | malbolge-oracle (state inspect) | debuggers | adapter | debug breakpoint_pc test | DEMONSTRATED |
| WATCHPOINT | debug --wp-cell | walbolge trace (written_positions) | debuggers | native | write_c/write_d watch | DEMONSTRATED |
| STATE_INSPECT | final_state a/c/d via oracle adapter | malbolge-oracle (a,c,d) | debuggers | adapter | run --backend oracle final_state | DEMONSTRATED |
| MEMORY_INSPECT | peak_memory only; oracle memory_snapshot available | malbolge-oracle (full 59049-cell memory) | debuggers | adapter | oracle memory verified | DEMONSTRATED (provider) / PARTIAL (AVB) |
| REWIND_OR_STEP_BACK | state_at(step) from event log | walbolge trace (full event log) | reverse debuggers | native | state_at test | DEMONSTRATED |
| DISASSEMBLE | disasm command | walbolge (decode_program, opcode_at) | disassemblers | native | disassemble test (2730 cells) | DEMONSTRATED |
| DECOMPILE_OR_HIGH_LEVEL_RECONSTRUCTION | no | walbolge (decompile -> text + structure) | decompilers | adapter | walbolge decompile verified (quijote roundtrip) | DEMONSTRATED (provider) / PARTIAL (AVB) |
| CONTROL_FLOW_ANALYSIS | no | walbolge (jumps graph, executed_positions) | CFG tools | native | jumps + executed_positions in debug output | DEMONSTRATED |
| SELF_MODIFICATION_ANALYSIS | no | walbolge (written_positions, write_c/write_d) | RE tools | native | written_positions + cell_before/cell_after on writes | DEMONSTRATED |
| STRUCTURAL_ANALYSIS | bootstrap/segments (walbolge) | walbolge (bootstrap, words, segments) | RE tools | native | segments in report | DEMONSTRATED |
| GENERATE_OR_SYNTHESIZE | no | meowbolge (working text->Malbolge), Autobolge relational, Malbolge-Translator (import broken) | generators | adapter | meowbolge imports; translator broken | DEMONSTRATED (meowbolge) / PARTIAL (AVB) |
| ROUNDTRIP_VERIFY | no | walbolge (roundtrip_vs_manifest), meowbolge self-check | verifiers | adapter | walbolge roundtrip verified | DEMONSTRATED (provider) / PARTIAL (AVB) |
| DIFFERENTIAL_EXECUTION | crossval command (N independent backends) | malbolge-differential, opera-solver UnifiedEvaluator | differential runners | adapter | crossval hello SEMANTIC_PARITY on 3 backends; malformed -> SEMANTIC_DIVERGENCE | DEMONSTRATED |
| CROSS_INTERPRETER_PARITY | parity + crossval (walbolge/engine/oracle) | walbolge, malbolge-engine, malbolge-oracle, autobolge | differential testing | native + adapter | hello SEMANTIC_PARITY (all 48 steps); malformed SEMANTIC_DIVERGENCE | DEMONSTRATED |
| CORPUS_EXECUTION | scan over corpus | walbolge, engine, oracle | test suites | native | corpus/ scanned | DEMONSTRATED |
| MALFORMED_INPUT_ANALYSIS | INVALID_PROGRAM | walbolge decode | fuzzing | native | invalid_chars test | DEMONSTRATED |
| RESOURCE_BUDGET_ANALYSIS | max_steps/wall/output budgets | walbolge, engine | limits | native | INV-008 budget test | DEMONSTRATED |
| INTERPRETER_CRASH_ATTRIBUTION | INTERPRETER_CRASH | walbolge | crash reporting | native | INV-006 test | DEMONSTRATED |
| HOST_CAPABILITY_MAP | per-backend host_map | interpreter backends | sandboxing | native | boundary map test | DEMONSTRATED |
| HOST_REACHABILITY | rce command | interpreter source inspection | threat modeling | native | rce NO_HOST_PATH_FOUND / HOST_PATH_PRESENT_NOT_REACHED | DEMONSTRATED |
| HOST_EFFECT_ATTRIBUTION | structural (host effects empty by seam) | interpreter backends | sandbox telemetry | native | no host effect on any backend | DEMONSTRATED |
| BEHAVIORAL_SECURITY_VERDICT | classification + severity | classify.py | AV/behavioral analysis | native | 12 tests | DEMONSTRATED |
| REPRODUCIBLE_RECEIPT | receipt v1 | receipt.py | SBOM/attestation | native | run_receipts/ | DEMONSTRATED |
| REPORT_VERIFY | verify command | cli verify | attestation check | native | verify re-reads receipt | DEMONSTRATED |

Status values: DEMONSTRATED / PARTIAL / NOT_DEMONSTRATED / UNAVAILABLE / OUT_OF_SCOPE.