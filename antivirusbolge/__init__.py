"""ANTIVIRUSBOLGE — defensive behavioral security analyzer for Malbolge.

This is a defensive analyzer. It never builds payloads. It consumes VM-level
trace evidence from a Malbolge backend (Walbolge by default) and classifies
observable behavior, separating VM effects from host effects by construction.
"""
from __future__ import annotations

__version__ = "0.1.0"

from .effects import (  # noqa: F401
    VM_READ,
    VM_WRITE,
    VM_JUMP,
    VM_ARITHMETIC,
    INPUT,
    OUTPUT,
    HALT,
    STEP,
    ERROR,
    HOST_FILE_READ,
    HOST_FILE_WRITE,
    HOST_PROCESS_START,
    HOST_NETWORK,
    HOST_ENV_READ,
    HOST_NATIVE_CALL,
    HOST_UNKNOWN_EFFECT,
)