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