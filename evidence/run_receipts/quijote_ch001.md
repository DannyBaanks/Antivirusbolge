ANTIVIRUSBOLGE
==============

Specimen      : corpus\benign\quijote_ch001.mal
SHA256        : bfaa91e096e2fba39734607f1109688356da46bb03bb731f97b164edf7794ac3
Interpreter   : walbolge 0.1.0
Execution     : 2632 steps | peak_memory=2730
Halt          : halt_opcode (halted=True)
Decoded output: 'CHAPTER I WHICH TREATS OF THE CHARACTER AND\nPURSUITS OF THE FAMOUS GENTLEMAN DON QUIXOTE OF LA MANCHA'

Static analysis:
    source_chars=2730 valid_cells=2730 malformed=0
    bootstrap=present

VM effects:
    VM_JUMP            1
    VM_READ            1233
    VM_WRITE           3929
    VM_ARITHMETIC      1297
    OUTPUT             101
    HALT               1
Host capabilities present: NONE
Host capabilities exercised: NONE
Boundary violations: 0

Verdict       : OUTPUT_ONLY
Severity      : INFO
Origin        : SPECIMEN_BEHAVIOR
Evidence      : DEMONSTRATED

Invariants:
    INV-001   PASS  VM writes bounded to VM tape (Walbolge backend, no host writes).
    INV-002   PASS  no host process effect observed.
    INV-003   PASS  no host filesystem effect observed.
    INV-004   PASS  no network effect observed.
    INV-005   PASS  no unknown external effect; DENY/INCONCLUSIVE would apply otherwise.
    INV-006   PASS  crash isolated as OUTPUT_ONLY.
    INV-007   PASS  resource use reported separately (steps=2632, peak_mem=2730).
    INV-008   PASS  within budget.
    INV-009   PASS  present=[] exercised=[] kept distinct.
    INV-010   PASS  capability presence is not treated as authorization.

Budget:
    exceeded=False reason=None wall=0.0s

Behavioral signature:
    trace_hash=a9a4aff8cadbc6cb… effect_count=6562
    output_hash=9efd9d8e84252422…

Not demonstrated:
    - behavior beyond step budget
    - behavior on other interpreters
    - universal harmlessness
