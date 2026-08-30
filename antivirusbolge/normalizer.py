"""Normalizer + static analysis for a Malbolge specimen.

Static inspection only: source size, valid/malformed cells, decoded opcodes,
bootstrap detection, non-opcode positions. This never executes anything.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import List, Optional

from .interpreter import ensure_walbolge

BOOTSTRAP_OPS = "i" + "o" * 99


@dataclass
class StaticFindings:
    source_chars: int
    opcode_count: int
    valid_cells: int
    malformed_cells: int
    non_opcode_positions: List[dict]
    bootstrap: Optional[dict]
    sha256: str
    first_invalid_chars: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "source_chars": self.source_chars,
            "opcode_count": self.opcode_count,
            "valid_cells": self.valid_cells,
            "malformed_cells": self.malformed_cells,
            "non_opcode_positions": self.non_opcode_positions[:200],
            "bootstrap": self.bootstrap,
            "sha256": self.sha256,
            "first_invalid_chars": self.first_invalid_chars[:50],
        }


def _detect_bootstrap(opcodes: str) -> Optional[dict]:
    if opcodes.startswith(BOOTSTRAP_OPS):
        return {"opcode_start": 0, "opcode_end": 100, "kind": "bootstrap"}
    head = opcodes[:120]
    if "i" in head:
        first_i = head.index("i")
        if opcodes[first_i:first_i + 100] == BOOTSTRAP_OPS:
            return {"opcode_start": first_i, "opcode_end": first_i + 100, "kind": "bootstrap"}
    return None


def static_analysis(raw: bytes, text: str) -> StaticFindings:
    ensure_walbolge()
    from walbolge.decoder import decode_program
    sha = hashlib.sha256(raw).hexdigest()
    decoded = decode_program(text)
    non_op = decoded.non_opcode_positions
    return StaticFindings(
        source_chars=len(text),
        opcode_count=decoded.opcode_count,
        valid_cells=decoded.opcode_count,
        malformed_cells=len(non_op),
        non_opcode_positions=non_op,
        bootstrap=_detect_bootstrap(decoded.opcodes),
        sha256=sha,
        first_invalid_chars=[p["char"] for p in non_op[:50]],
    )


def load_specimen(path: str) -> tuple:
    """Returns (raw_bytes, utf8_text). Raises on decode failure."""
    from pathlib import Path
    raw = Path(path).read_bytes()
    text = raw.decode("utf-8", errors="replace")
    return raw, text