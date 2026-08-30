# GUIA.md — ANTIVIRUSBOLGE para el que lo opera

Esta guía es para la persona que corre los comandos. Todo lo de aquí está
*ejecutado*, con su salida real pegada. Nada inventado.

## 1. El comando que viniste a buscar

```powershell
py -m antivirusbolge scan corpus\benign\quijote_ch001.mal
```

## 2. La regla de oro

**Si el programa no termina dentro del presupuesto, el veredicto es
`INCONCLUSIVE`, jamás `SAFE`.** Un virus no se declara inocente porque el
escáner se cansó antes que él.

## 3. Antes de empezar

Usa `py`, no `python` (el `python` desnudo puede estar shim-eliminado en esta
máquina y morir con exit 2718). Desde la raíz de `Antivirusbolge\`:

```powershell
py -m pytest tests\test_avb.py -q
```

Salida real (últimas líneas):

```
........                                                                 [100%]
8 passed in 0.99s
```

## 4. Cada comando, con su salida real

### Escanear un espécimen benigno del Quijote

```powershell
py -m antivirusbolge scan corpus\benign\quijote_ch001.mal
```

Salida real (fragmento):

```
Specimen      : corpus\benign\quijote_ch001.mal
Interpreter   : walbolge 0.1.0
Execution     : 2632 steps | peak_memory=2730
Halt          : halt_opcode (halted=True)
Decoded output: 'CHAPTER I WHICH TREATS OF THE CHARACTER AND\nPURSUITS OF THE ...'

VM effects:
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
    INV-001   PASS  VM writes bounded to VM tape ...
    ...
    INV-008   PASS  within budget.
```

### Guardar reportes (.md humano + .json máquina)

Los flags globales van **antes** del subcomando:

```powershell
py -m antivirusbolge --md evidence\run_receipts\quijote_ch001.md scan corpus\benign\quijote_ch001.mal
```

Salida real (última línea):

```
Reports: evidence\run_receipts\quijote_ch001.md / evidence\run_receipts\quijote_ch001.json
```

### Espécimen clásico (interpretador clásico)

```powershell
py -m antivirusbolge --classic scan corpus\benign\hello_classic.mal
```

Salida real (fragmento):

```
Decoded output: 'Hello, world.'
    OUTPUT             13
Verdict       : OUTPUT_ONLY
Evidence      : DEMONSTRATED
```

El `hello.malbolge` de Malbolge-Engine para en **48 pasos** — el mismo número
que reporta Malbolge-Engine. Buen control de paridad clásico.

### Espécimen inválido

```powershell
py -m antivirusbolge scan corpus\malformed\invalid_chars.mal
```

Salida real:

```
Verdict       : INVALID_PROGRAM
Severity      : LOW
Evidence      : DEMONSTRATED
```

### Presupuesto agotado (lo importante)

```powershell
py -m antivirusbolge --classic --max-steps 10 scan corpus\stress\runaway.mal
```

Salida real:

```
Verdict       : NONTERMINATING_WITHIN_BUDGET
Severity      : LOW
Evidence      : INCONCLUSIVE
    INV-008   FAIL  budget exceeded; NOT classified safe (INCONCLUSIVE).
```

**El `FAIL` de INV-008 aquí es correcto y esperado.** Es el fail-closed
trabajando: cortamos el programa y el veredicto no es "seguro", es "no se
demostró".

### Comparar dos especímenes

```powershell
py -m antivirusbolge compare corpus\malformed\truncated.mal corpus\malformed\invalid_chars.mal
```

Salida real (fragmento):

```
    "L0_source": false,
    "L1_output": true,
    "L3_effects": false,
    "L4_trace": false,
  "comparison": "OUTPUT_EQUAL_TRACE_DIFFERENT",
```

### Firma de comportamiento

```powershell
py -m antivirusbolge behavior corpus\benign\hello_classic.mal
```

Salida real (fragmento):

```
  "source_sha256": "c8a95363...",
  "trace_hash": "986390e4...",
  "halt_reason": "halt_opcode",
```

### Paridad entre intérpretes (M1)

Compara el mismo espécimen en Walbolge (clásico) y en Malbolge-Engine (C):

```powershell
py -m antivirusbolge parity corpus\benign\hello_classic.mal
```

Salida real:

```
  "backend_a": { "name": "walbolge", "steps": 48, "halt": "halt_opcode", ... },
  "backend_b": { "name": "malbolge-engine", "steps": 48, "halt": "halt_opcode", ... },
  "output_match": true,
  "halt_match": true,
  "classification": "SEMANTIC_PARITY",
  "status": "DEMONSTRATED"
```

### Boundary map por intérprete (M1)

```powershell
py -m antivirusbolge interpreter-audit walbolge
py -m antivirusbolge interpreter-audit malbolge-engine
```

Salida real (fragmentos):

```
walbolge:        "capabilities_present": []
malbolge-engine: "capabilities_present": ["HOST_PROCESS_START"]
                 "capabilities_reachable": []
                 "capabilities_exercised": []
```

El `HOST_PROCESS_START` de malbolge-engine es del **harness** (lanza el binario
C como proceso), no del espécimen. `reachable` y `exercised` vacíos = ningún
espécimen cruza al host.

### Cross-validation entre intérpretes independientes (M2)

```powershell
py -m antivirusbolge crossval corpus\benign\hello_classic.mal
```

Salida real (fragmento):

```
  "walbolge":        { "status": "OK", "steps": 48, "output_hash": "f8c3bf62..." },
  "malbolge-engine": { "status": "OK", "steps": 48, "output_hash": "f8c3bf62..." },
  "oracle":          { "status": "OK", "steps": 48, "output_hash": "f8c3bf62..." },
  "classification": "SEMANTIC_PARITY"
```

Tres intérpretes independientes coinciden en 48 pasos y mismo hash de salida.

### Disassembly / debug (M2)

```powershell
py -m antivirusbolge disasm corpus\benign\quijote_ch001.mal --limit 3
```

Salida real:

```
decoded 2730 cells (first 3):
  [   0] char='b' opcode=i
  [   1] char='C' opcode=o
  [   2] char='B' opcode=o
```

### Generación + roundtrip en 3 intérpretes (M2)

```powershell
py -m antivirusbolge roundtrip corpus\generated\gen_NO.mal --expect NO
```

Salida real (fragmento):

```
  "verdict": "ROUNDTRIP_PASS",
  "backends_matching": ["walbolge", "malbolge-engine", "oracle"]
```

La generación **nunca se auto-valida**: el espécimen debe reproducir el texto en
intérpretes independientes.

## 5. Cómo leer la salida

| Veredicto | Qué significa | Qué hacer |
|-----------|---------------|-----------|
| `OUTPUT_ONLY` | Solo efectos VM + salida, halt normal | Nada; es benigno dentro del presupuesto |
| `PURE_VM_COMPUTE` | Solo cómputo VM, sin salida | Revisar que fuera lo esperado |
| `INVALID_PROGRAM` | No hay celdas de instrucción válidas | El archivo no es un programa Malbolge real |
| `NONTERMINATING_WITHIN_BUDGET` | No terminó a tiempo | Subir `--max-steps` o marcar `INCONCLUSIVE` |
| `INTERPRETER_CRASH` | El intérprete falló | Es problema del intérprete, no del espécimen |
| `HOST_*` | Efecto host demostrado | **Solo M1 / solo si hay un seam real** |

`Evidence: DEMONSTRATED` = se observó. `INCONCLUSIVE` = no se pudo concluir,
no es inocencia.

## 6. Trampas

- **`python` muere (exit 2718).** Usa `py`. Si un script "falla", revisa que
  no sea el shim.
- **Los flags globales van ANTES del subcomando.** `antivirusbolge --md ... scan X`
  funciona; `antivirusbolge scan X --md ...` no (argparse lo rechaza).
- **Un `FAIL` en INV-008 no es un bug.** Es el fail-closed cuando se agota el
  presupuesto.
- **No todo archivo raro es "malware".** `INVALID_PROGRAM` es un programa que
  no se puede ejecutar, no una amenaza. Malbolge es ilegible por diseño; se
  clasifica comportamiento, no estética.
- **`INCONCLUSIVE` ≠ `SAFE`.** Nunca cites un espécimen como seguro si solo lo
  viste dentro de un presupuesto.
- **El corpus del Quijote viene de `Malbolge-Translator`.** Si lo regeneras, el
  SHA-256 de `specimen_manifest.json` deja de cuadrar; vuelve a generarlo.
- **`parity` y el backend C necesitan el binario.** `malbolge-ipc.exe` debe
  existir (por defecto en `C:\Development\ISyCo Git\Malbolge-Engine\`). Si no
  está, ese test se salta; ajusta `AVB_MALBOLGE_ENGINE` para apuntar a otro.
- **`parity` usa `classic=True` para Walbolge.** Es lo correcto para comparar
  contra el intérprete clásico C; un programa del Translator (toolkit) no es
  comparable 1:1 contra Malbolge-Engine.