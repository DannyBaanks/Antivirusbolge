ANTIVIRUSBOLGE
==============

Specimen      : corpus\benign\hello_classic.mal
SHA256        : c8a95363dbe2e997192834cf42a6f317be4a3bef93263e026300bc8243e77601
Interpreter   : walbolge 0.1.0
Execution     : 48 steps | peak_memory=59049
Halt          : halt_opcode (halted=True)
Decoded output: 'Hello, world.'

Static analysis:
    source_chars=89 valid_cells=89 malformed=0
    bootstrap=absent

VM effects:
    VM_JUMP            4
    VM_READ            10
    VM_WRITE           72
    VM_ARITHMETIC      24
    OUTPUT             13
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
    INV-007   PASS  resource use reported separately (steps=48, peak_mem=59049).
    INV-008   PASS  within budget.
    INV-009   PASS  present=[] exercised=[] kept distinct.
    INV-010   PASS  capability presence is not treated as authorization.

Budget:
    exceeded=False reason=None wall=0.125s

Behavioral signature:
    trace_hash=986390e4ac54afcd… effect_count=124
    output_hash=f8c3bf62a9aa3e6f…

Not demonstrated:
    - behavior beyond step budget
    - behavior on other interpreters
    - universal harmlessness
