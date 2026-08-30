"""Minimum test set for ANTIVIRUSBOLGE M0.

Each test asserts an observable classification, keeping raw output available.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from antivirusbolge.analyzer import scan, behavior_signature
from antivirusbolge.compare import compare
from antivirusbolge.classify import classify, CLS_OUTPUT_ONLY, CLS_PURE_VM_COMPUTE, \
    CLS_INVALID_PROGRAM, CLS_INTERPRETER_CRASH, CLS_NONTERMINATING

CORPUS = Path(__file__).resolve().parent.parent / "corpus"
HELLO = CORPUS / "benign" / "hello_classic.mal"
QUIJOTE = CORPUS / "benign" / "quijote_ch001.mal"
RUNAWAY = CORPUS / "stress" / "runaway.mal"
INVALID = CORPUS / "malformed" / "invalid_chars.mal"
TRUNCATED = CORPUS / "malformed" / "truncated.mal"
PROBE = CORPUS / "interpreter_boundary" / "probe_high_activity.mal"


def test_benign_output_specimen_output_only():
    report = scan(str(QUIJOTE), max_steps=5_000_000)
    assert report["verdict"]["security_class"] == CLS_OUTPUT_ONLY
    assert report["verdict"]["status"] == "DEMONSTRATED"
    assert report["outcome"]["halt_reason"] == "halt_opcode"
    assert report["outcome"]["output"].startswith("CHAPTER")
    assert report["host_map"]["capabilities_exercised"] == []


def test_valid_halting_classic_halt_detected():
    report = scan(str(HELLO), classic=True, max_steps=1_000_000)
    assert report["outcome"]["halted"] is True
    assert report["outcome"]["halt_reason"] == "halt_opcode"
    assert report["outcome"]["steps"] == 48
    assert report["outcome"]["output"] == "Hello, world."
    assert report["verdict"]["security_class"] == CLS_OUTPUT_ONLY


def test_long_running_specimen_budget_exceeded():
    # runaway.mal is a long printable program; we cut it at 10 steps so the
    # execution is unobserved to completion. INV-008: budget exceeded != safe.
    report = scan(str(RUNAWAY), classic=True, max_steps=10)
    assert report["budget"]["exceeded"] is True
    assert report["budget"]["reason"] == "max_steps"
    assert report["verdict"]["status"] == "INCONCLUSIVE"
    assert report["verdict"]["security_class"] == CLS_NONTERMINATING


def test_malformed_specimen_invalid_program():
    report = scan(str(INVALID))
    assert report["verdict"]["security_class"] == CLS_INVALID_PROGRAM
    assert report["verdict"]["status"] == "DEMONSTRATED"


def test_interpreter_crash_classified_not_as_specimen_compromise():
    # Walbolge does not crash on our corpus, so classify() is exercised directly
    # with an interpreter-side error to prove INV-006 isolation.
    static = {"malformed_cells": 0, "opcode_count": 10}
    outcome = {"halt_reason": "interpreter_error", "output": "", "halted": False}
    canonical = {"host_effects": {}, "vm_effects": {}}
    verdict = classify(static, type("O", (), outcome)(), canonical,
                       False, True, 1000)
    assert verdict["security_class"] == CLS_INTERPRETER_CRASH
    assert verdict["origin"] == "INTERPRETER_BEHAVIOR"


def test_host_capability_path_classified():
    # A high-activity specimen on the Walbolge backend: capability path is
    # structurally empty; no host effect can be attributed.
    report = scan(str(PROBE))
    assert report["host_map"]["capabilities_present"] == []
    assert report["host_map"]["capabilities_exercised"] == []
    assert report["host_map"]["boundary_violations"] == 0
    assert report["canonical"]["host_effects"] == {}
    for inv in report["invariants"]:
        assert inv["pass"], f"{inv['invariant']} failed: {inv['note']}"


def test_same_output_different_trace_pair():
    # truncated and invalid_chars both produce zero output but trace differently.
    result = compare(str(TRUNCATED), str(INVALID))
    assert result["comparison"] == "OUTPUT_EQUAL_TRACE_DIFFERENT"
    assert result["ladder"]["L1_output"] is True
    assert result["ladder"]["L4_trace"] is False


def test_source_hash_differs_from_behavior_signature():
    a = scan(str(HELLO), classic=True)
    sig_a = behavior_signature(a)
    b = scan(str(TRUNCATED))
    sig_b = behavior_signature(b)
    assert sig_a["source_sha256"] != sig_b["source_sha256"]
    assert sig_a["behavioral"]["trace_hash"] != sig_b["behavioral"]["trace_hash"]
    # Same behavioral-structure example: probe == quijote source (identical bytes)
    p = scan(str(PROBE))
    assert p["static"]["sha256"] == scan(str(QUIJOTE))["static"]["sha256"]


# ---- M1: cross-interpreter parity + boundary map --------------------------

MALBOLGE_ENGINE_EXE = r"C:\Development\ISyCo Git\Malbolge-Engine\malbolge-ipc.exe"


def _engine_present() -> bool:
    return Path(MALBOLGE_ENGINE_EXE).exists()


@pytest.mark.skipif(not _engine_present(), reason="Malbolge-Engine binary not present")
def test_cross_interpreter_semantic_parity():
    from antivirusbolge.parity import parity
    result = parity(str(HELLO), max_steps=1_000_000)
    assert result["classification"] == "SEMANTIC_PARITY"
    assert result["status"] == "DEMONSTRATED"
    assert result["steps_a"] == result["steps_b"] == 48
    assert result["output_match"] is True


def test_boundary_map_distinguishes_backends():
    from antivirusbolge.interpreter import get_backend
    w = get_backend("walbolge").host_map
    e = get_backend("malbolge-engine").host_map
    # The harness spawns the C binary as a process; Walbolge does not.
    assert w.capabilities_present == []
    assert e.capabilities_present == ["HOST_PROCESS_START"]
    # Neither backend lets a *specimen* reach or exercise a host capability.
    assert w.capabilities_reachable == [] and w.capabilities_exercised == []
    assert e.capabilities_reachable == [] and e.capabilities_exercised == []
    assert w.boundary_violations == 0 and e.boundary_violations == 0