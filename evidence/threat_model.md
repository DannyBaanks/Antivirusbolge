# ANTIVIRUSBOLGE — Threat Model (M0)

Defensive analysis only. This project never builds payloads. It reduces an
opaque Malbolge specimen to observable, classifiable behavior.

## Scope

Analyze a Malbolge specimen `P` executed by interpreter `I` and answer, with
evidence, what `P` demonstrably does inside the VM, and whether any effect
crosses a host boundary.

## Out of scope (do not build)

Working RCE payloads, persistence payloads, host-compromise tooling, arbitrary
shell-payload generators, malware deployment logic. A specimen that shows
dangerous behavior is analyzed, never improved or weaponized.

## Layer model

```
MALBOLGE SOURCE        (opaque text)
  -> MALBOLGE SEMANTICS (decoded opcodes)
  -> VM / INTERPRETER   (Walbolge tracer)
  -> ADAPTER / WRAPPER  (antivirusbolge.interpreter backend)
  -> HOST               (the Python process)
```

Danger can exist at different seams. A malicious-looking source over a VM
without host capabilities is not host danger; a benign source over a vulnerable
interpreter is interpreter danger; a wrapper exposing filesystem/process/
network is adapter danger.

## Seams of interest

| Seam | Question |
|------|----------|
| source -> semantics | is the source decodable? how many valid cells? |
| semantics -> VM | what effects happen inside the tape? |
| VM -> interpreter | does the interpreter crash, hang, overconsume? |
| interpreter -> adapter | does the adapter expose host primitives? |
| adapter -> host | does any host capability get exercised? |

## Separations that must never collapse

- Program behavior != host behavior.
- Vulnerable interpreter != malicious specimen.
- Suspicious != proven malicious.
- Bounded execution != universal safety.
- `capability != authority`; `CAPABILITY_PRESENT != CAPABILITY_EXERCISED`.

## False-positive discipline

Malbolge is unreadable by design. Weird syntax is not malicious. The analyzer
classifies *behavior*, not aesthetics.

## Current concrete threat posture (Walbolge backend)

By code inspection the `walbolge.trace`/`tables`/`decoder`/`decompiler` core
uses **no** host primitives (no `subprocess`, `socket`, `ctypes`, `cffi`,
`mmap`, `eval`, `exec` of specimen content). The only I/O is reading the
specimen file and writing report JSON. Therefore, for this backend:

- `HOST_CAPABILITY_REQUEST` / `HOST_CAPABILITY_ESCAPE` are **not reachable**.
- A host effect cannot be attributed to any specimen — there is no seam.
- Remaining classifications are VM-level and resource-level only.

This is a structural negative, not merely "no effect observed this run."