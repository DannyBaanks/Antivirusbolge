# ANTIVIRUSBOLGE

Analizador de seguridad conductual defensivo para Malbolge. Dado un especimen
opaco de Malbolge, reduce la ejecucion a efectos VM canonicos y produce un veredicto
con evidencia. Nunca construye payloads.

El objetivo no es "Malbolge se ve aterrador". El objetivo es: **podemos explicar exactamente
que hizo este especimen, que permitio su interprete, y que cruzo hacia el host.**

## Idea central

`capability != authority` y `program behavior != host behavior`. El analizador
mantiene los efectos VM y los efectos del host en capas separadas, y solo atribuye un efecto
del host cuando una costura concreta del interprete lo demuestra.

Para el backend por defecto (Walbolge, Python puro), esa costura esta **ausente
estructuralmente**: el nucleo del tracer no usa subprocess, socket, ctypes, ffi, mmap, eval ni
exec de contenido del especimen. Entonces los efectos del host son `NONE` por construccion, y
el espacio restante de veredictos es de nivel VM y de nivel de recursos.

## Instalar / correr

```bash
py -m antivirusbolge scan corpus/benign/quijote_ch001.mal
py -m pytest tests/test_avb.py -q
```

Se usa `py` (el launcher de Python) porque `python` desnudo puede estar protegido por shim en
esta maquina.

## Comandos

| Comando | Proposito |
|---------|-----------|
| `scan <especimen>` | escaneo completo + veredicto + recibo |
| `run <especimen> [--backend B]` | ejecuta en un backend -> IR canonico |
| `crossval <especimen>` | ejecuta en todos los backends independientes + compara |
| `backends` | lista backends invocables |
| `capabilities` | resumen de matriz de capacidades previas |
| `disasm <especimen>` | decodifica cada celda -> opcode |
| `state <especimen> --step N` | estado VM (a/c/d) en un paso |
| `debug <especimen> [--bp-pc N] [--wp-cell N]` | corre con breakpoints/watchpoints |
| `generate "<texto>" [--out F]` | sintetiza un especimen clasico (meowbolge) |
| `roundtrip <especimen> --expect <texto>` | verifica en backends independientes |
| `corpus <dir> --phrases "A;B"` | genera+verifica un corpus pequeno |
| `trace <especimen> [--limit N]` | primeros N eventos de trace |
| `behavior <especimen>` | firma conductual (hash del fuente != hash del trace) |
| `compare <a> <b>` | escalera de comparacion nivel L0..L5 |
| `parity <especimen>` | paridad cross-interprete (walbolge vs malbolge-engine) |
| `interpreter-audit <backend>` | mapa de frontera de capacidades del host por backend |
| `verify <report.json>` | re-imprime el veredicto de un reporte guardado |

## Modelo de veredicto

Cada hallazgo trae `ORIGIN` (`SPECIMEN_BEHAVIOR` / `VM_BEHAVIOR` /
`INTERPRETER_BEHAVIOR` / `ADAPTER_BEHAVIOR` / `HOST_CAPABILITY` / `UNKNOWN`),
`STATUS` (`DEMONSTRATED` / `FALSIFIED` / `NOT_DEMONSTRATED` / `INCONCLUSIVE`),
un `SECURITY_CLASS` (`OUTPUT_ONLY`, `PURE_VM_COMPUTE`, `INVALID_PROGRAM`,
`NONTERMINATING_WITHIN_BUDGET`, `INTERPRETER_CRASH`, ...) y un `SEVERITY`
conservador. El exceso de presupuesto genera `INCONCLUSIVE`, nunca `SAFE`.

## Backends

- **Walbolge** (Python puro) — traza VM completa por evento; costura del host ausente.
- **Malbolge-Engine** (C) — interprete independiente via JSONL IPC (output/steps/status).
  El harness spawne el binario como proceso (declarado `HOST_PROCESS_START` presente),
  pero ningun especimen puede alcanzarlo o ejercerlo.
- **malbolge-oracle** (Python) — VM de referencia independiente que expone el
  estado final a/c/d y las 59049 celdas de memoria completas.
- **Autobolge** (Zig) — VM 3^10 independiente via contenedor BOLG1->BOLG2.
- **bolge19** (Zig, malbolge-lisp-forensics) — VM nativa de Malbolge **Unshackled
  3^19** (una variante distinta de Malbolge). Corre archivos `.mb`/imagen.

> **Nota de dependencia de bolge19 (la unica).** bolge19 se construye desde nuestro
> propio `malbolge-lisp-forensics/src/bolge19/main.zig` y compila/corre solo con
> Zig. Pero para correr *correctamente en su variante nativa 3^19* necesita una imagen
> genuina de Malbolge Unshackled 3^19, y esas vienen del runtime de terceros
> **MalbolgeLISP** (`init_module.mb`/`core.mb`/`lisp.mb`). Los archivos `.mb`
> que flotan en el corpus son en realidad programas classicos 3^10 guardados como
> `.mb`, asi que correrlos bajo bolge19 produce salida interpretada en 3^19, no los
> bytes esperados. Por lo tanto la **demostracion de variante nativa de bolge19 es
> NOT_DEMONSTRATED** — esta bloqueada por las imagenes de terceros MalbolgeLISP.
> **Todo lo demas en Antivirusbolge corre completamente por su cuenta**; solo este
> componente depende de un repo externo para demostrar su variante nativa.

`parity` y `crossval` corren el mismo especimen en backends independientes y
clasifican paridad/divergencia **dentro de la misma variante de Malbolge**. `hello_classic`
muestra `SEMANTIC_PARITY` en los 4 backends classicos 3^10 (48 pasos, `Hello,
world.`); bolge19 (Unshackled 3^19) lo corre en 47 pasos / bytes diferentes y se
reporta por separado como variante distinta, no se mezcla en paridad. Los backends pueden
exponer modelos de estado final diferentes; la paridad se clave en output + halt.

## M2: workbench

M2 convirtio a Antivirusbolge en un workbench de espectro completo sobre las VMs
independientes de Malbolge: IR canonico (`run`), cross-validation (`crossval`),
debugger/RE (`disasm`/`state`/`debug`), y un pipeline de generacion+roundtrip (`generate`/
`roundtrip`/`corpus`). El generador compacto palabra por palabra (`malbolge-generator`,
encontrado en `C:\Development\E31-A-Nagoya\malbolge_toolkit\malbolge\`) produce
especimenes cortos de ciberseguridad verificados ROUNDTRIP_PASS en los 3 backends
independientes; el antivirus los escanea como OUTPUT_ONLY / sin efectos en el host. Ver
`evidence/CLAIM_GATE.md`: veredicto **READY** (gap de sintesis cerrado); el claim de
novedad esta condicionado a un barrido mas amplio de previo estado del arte.

## Contexto historico y procedencia

No pretendemos haber inventado el ecosistema Malbolge del que dependemos.
Antivirusbolge existe gracias a ese ecosistema.

Interpretes previos, generadores, MalbolgeLISP, y otra investigacion proporcionaron
puntos de referencia importantes y, en casos limitados, artifacts upstream usados para
validacion. Su autorship se preserva (ver `evidence/PROVENANCE.md`).

Nuestra contribucion es el workbench basado en evidencia y la integracion de
ejecucion, debugging, reverse engineering, sintesis, validacion diferencial,
clasificacion de seguridad conductual, y atribucion explicita VM/interprete/adapter/host.

**El proyecto empezo con una discrepancia.** El artifact mas antiguo con fecha en esta
familia de proyectos es E31-A (2026-08-13): una implementacion literal e independiente de
las semanticas de Malbolge de Iizawa et al. (2005) Appendix C, escrita desde el pseudocodigo
del propio paper. No coincidia con las etiquetas §2.2 del paper para `<` y `/`.
En vez de elegir cual autoridad estaba mal, construimos observadores adicionales y
verificaciones diferenciales. Ese metodo — observadores independientes, divergencia
fijada (no oculta), sin documento o runtime unico como autoridad por decreto — se convirtio en
el principio de diseno de Antivirusbolge. La discrepancia I/O se documenta
por separado, con evidencia reproducible y procedencia exacta
(`evidence/IIZAWA_IO_DISCREPANCY.md`, `IIZAWA_ERRATUM_CANDIDATE.md`,
`IIZAWA_PRIORITY_SEARCH.md`, `HISTORICAL_TIMELINE.md`).

Para ser preciso sobre que afirmamos y que no: **no descubrimos que
Malbolge tiene semanticas historicas en conflicto — la reversal entre la
especificacion original y el interprete de referencia es un previo estado del arte establecido.
Descubrimos independientemente que un paper importante sobre Malbolge reproduce ese
conflicto internamente** (etiquetas §2.2 vs codigo de Appendix C).

Afirmamos el workbench, no la historia sobre la que estamos parados. El objetivo no es reemplazar
las herramientas que vinieron antes. El objetivo es contribuir suficiente trabajo original,
reproducible para merecer un lugar junto a ellas.

## Estructura

```
antivirusbolge/     paquete central (normalizer, interpreter, effects, classify,
                    invariants, receipt, analyzer, compare, parity, rce, ir,
                    workbench, debug, synthesis, report, cli)
corpus/             benign | malformed | stress | interpreter_boundary | generated | source
evidence/           threat_model, architecture, invariants, manifests, matrix,
                    tool discovery, claim gate, receipts
tests/              test_avb.py (20 pruebas)
```

El analizador consume **Walbolge** (el decompilador Malbolge→text) a traves de un
adaptador; Walbolge es el productor de evidencia, no la autoridad de seguridad.

Guia del operador humano (espanol, comandos con salida real): `GUIA.md`.
