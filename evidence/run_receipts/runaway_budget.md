ANTIVIRUSBOLGE
==============

Specimen      : corpus\stress\runaway.mal
SHA256        : d45ac34ae17521ca62b7b74a44662a386d6d971a84327c5419bd4e3998f60011
Interpreter   : walbolge 0.1.0
Execution     : 10 steps | peak_memory=59049
Halt          : max_steps (halted=True)
Decoded output: ''

Static analysis:
    source_chars=248 valid_cells=21 malformed=227
    bootstrap=absent

VM effects:
    STEP               9
    VM_READ            9
    VM_WRITE           10
    INPUT              1
Host capabilities present: NONE
Host capabilities exercised: NONE
Boundary violations: 0

Verdict       : NONTERMINATING_WITHIN_BUDGET
Severity      : LOW
Origin        : SPECIMEN_BEHAVIOR
Evidence      : INCONCLUSIVE

Invariants:
    INV-001   PASS  VM writes bounded to VM tape (Walbolge backend, no host writes).
    INV-002   PASS  no host process effect observed.
    INV-003   PASS  no host filesystem effect observed.
    INV-004   PASS  no network effect observed.
    INV-005   PASS  no unknown external effect; DENY/INCONCLUSIVE would apply otherwise.
    INV-006   PASS  crash isolated as NONTERMINATING_WITHIN_BUDGET.
    INV-007   PASS  resource use reported separately (steps=10, peak_mem=59049).
    INV-008   FAIL  budget exceeded; NOT classified safe (INCONCLUSIVE).
    INV-009   PASS  present=[] exercised=[] kept distinct.
    INV-010   PASS  capability presence is not treated as authorization.

Budget:
    exceeded=True reason=max_steps wall=0.141s

Behavioral signature:
    trace_hash=35db6780e65c1dc9… effect_count=29
    output_hash=e3b0c44298fc1c14…

Not demonstrated:
    - behavior beyond step budget
    - behavior on other interpreters
    - universal harmlessness
