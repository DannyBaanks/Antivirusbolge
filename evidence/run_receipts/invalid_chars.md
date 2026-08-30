ANTIVIRUSBOLGE
==============

Specimen      : corpus\malformed\invalid_chars.mal
SHA256        : 26beb9ec2ea27227cfd8c689e76dce474e1994ca11824d388f75c97078b053c5
Interpreter   : walbolge 0.1.0
Execution     : 0 steps | peak_memory=0
Halt          : invalid_program (halted=False)
Decoded output: ''

Static analysis:
    source_chars=21 valid_cells=0 malformed=21
    bootstrap=absent

VM effects:
Host capabilities present: NONE
Host capabilities exercised: NONE
Boundary violations: 0

Verdict       : INVALID_PROGRAM
Severity      : LOW
Origin        : SPECIMEN_BEHAVIOR
Evidence      : DEMONSTRATED

Invariants:
    INV-001   PASS  VM writes bounded to VM tape (Walbolge backend, no host writes).
    INV-002   PASS  no host process effect observed.
    INV-003   PASS  no host filesystem effect observed.
    INV-004   PASS  no network effect observed.
    INV-005   PASS  no unknown external effect; DENY/INCONCLUSIVE would apply otherwise.
    INV-006   PASS  crash isolated as INVALID_PROGRAM.
    INV-007   PASS  resource use reported separately (steps=0, peak_mem=0).
    INV-008   PASS  within budget.
    INV-009   PASS  present=[] exercised=[] kept distinct.
    INV-010   PASS  capability presence is not treated as authorization.

Budget:
    exceeded=False reason=None wall=Nones

Behavioral signature:
    trace_hash=e3b0c44298fc1c14… effect_count=0
    output_hash=e3b0c44298fc1c14…

Not demonstrated:
    - behavior beyond static inspection
