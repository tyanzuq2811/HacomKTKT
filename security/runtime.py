from __future__ import annotations

import contextlib
import ipaddress
import json
import os
import shutil
import socket
import tempfile
import time
from pathlib import Path
from typing import Iterator


def configure_offline_environment() -> None:
    """Force common ML libraries into offline mode before model import."""
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
    os.environ.setdefault("DO_NOT_TRACK", "1")
    os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
    os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")


def _is_local_host(host: str) -> bool:
    if host in {"localhost", "::1"}:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        try:
            return all(ipaddress.ip_address(x[4][0]).is_loopback for x in socket.getaddrinfo(host, None))
        except Exception:
            return False


@contextlib.contextmanager
def deny_external_network(enabled: bool = True) -> Iterator[None]:
    """Best-effort process-level egress guard; loopback remains available."""
    if not enabled:
        yield
        return
    original_connect = socket.socket.connect
    original_create = socket.create_connection

    def guarded_connect(sock, address):
        host = address[0] if isinstance(address, tuple) else str(address)
        if not _is_local_host(str(host)):
            raise PermissionError(f"Strict privacy blocked external network connection to {host}")
        return original_connect(sock, address)

    def guarded_create(address, *args, **kwargs):
        host = address[0] if isinstance(address, tuple) else str(address)
        if not _is_local_host(str(host)):
            raise PermissionError(f"Strict privacy blocked external network connection to {host}")
        return original_create(address, *args, **kwargs)

    socket.socket.connect = guarded_connect
    socket.create_connection = guarded_create
    try:
        yield
    finally:
        socket.socket.connect = original_connect
        socket.create_connection = original_create


@contextlib.contextmanager
def secure_workspace(prefix: str = "hsmt_") -> Iterator[Path]:
    root = Path(tempfile.mkdtemp(prefix=prefix))
    try:
        try:
            os.chmod(root, 0o700)
        except Exception:
            pass
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)


def append_audit_event(log_path: str | Path, event: dict) -> None:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **event}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
