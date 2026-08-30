"""Execution receipt — the machine-readable verdict artifact."""
from __future__ import annotations

import datetime
from typing import Optional


def build_receipt(specimen_path: str, static: dict, outcome, canonical: dict,
                  host_map: dict, verdict: dict, budget: dict, backend: dict,
                  limits: dict, not_demonstrated: list) -> dict:
    return {
        "schema": "antivirusbolge.receipt.v1",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "specimen_path": specimen_path,
        "specimen_sha256": static.get("sha256"),
        "interpreter_name": backend.get("name"),
        "interpreter_version": backend.get("version"),
        "interpreter_sha256": None,
        "steps": outcome.get("steps"),
        "halt_reason": outcome.get("halt_reason"),
        "vm_effects": list((canonical.get("vm_effects") or {}).keys()),
        "host_effects": list((canonical.get("host_effects") or {}).keys()),
        "capabilities_present": host_map.get("capabilities_present", []),
        "capabilities_exercised": host_map.get("capabilities_exercised", []),
        "budget_exceeded": budget.get("exceeded", False),
        "limits": limits,
        "classification": verdict.get("security_class"),
        "status": verdict.get("status"),
        "not_demonstrated": not_demonstrated,
    }


def DEFAULT_LIMITS(max_steps: int, max_output_bytes: Optional[int],
                   max_wall_time_s: Optional[float]) -> dict:
    return {
        "max_steps": max_steps,
        "max_output_bytes": max_output_bytes,
        "max_wall_time_s": max_wall_time_s,
    }