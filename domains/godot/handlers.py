"""domains/godot/handlers.py — Handlers do domínio godot (F5.11).

Wrappers keyword-only (*). NÃO conhecem MCP, Tool, nem annotations.
"""

from typing import Any
import subprocess, sys, os, time


def run_project(*, project_path: str, godot_executable: str) -> dict:
    """Lança o projeto Godot como processo separado."""
    if not project_path or not godot_executable:
        return {"status": "error", "message": "project_path e godot_executable obrigatorios"}
    try:
        proc = subprocess.Popen(
            [godot_executable, "--path", project_path],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        return {"status": "success", "pid": proc.pid}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def stop_project(*, pid: int) -> dict:
    """Para o processo Godot pelo PID."""
    if not pid:
        return {"status": "error", "message": "pid obrigatorio"}
    try:
        if sys.platform == "win32":
            from tools.subprocess_utils import run_subprocess_safe
            result = run_subprocess_safe(["taskkill", "/F", "/PID", str(pid)], timeout=10)
            if result.returncode != 0:
                return {"status": "error", "message": f"taskkill falhou: {result.stderr.strip()}"}
        else:
            import signal
            os.kill(pid, signal.SIGKILL)
        return {"status": "success", "pid": pid}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def wait_bridge(*, timeout_sec: float = 10.0) -> dict:
    """Espera o bridge do Godot responder."""
    try:
        from server import send_bridge_command, BridgeUnavailable
    except ImportError:
        return {"status": "error", "message": "Bridge não disponível neste contexto"}
    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            result = send_bridge_command({"cmd": "runtime_info"})
            return {"status": "success", "data": result}
        except BridgeUnavailable:
            time.sleep(0.3)
    return {"status": "error", "message": f"bridge não respondeu em {timeout_sec}s"}


def exec_gdscript(*, code: str) -> dict:
    """Executa código GDScript no jogo rodando."""
    import json as _json
    if not code:
        return {"status": "error", "message": "code obrigatorio"}
    try:
        from tools.playtest_ops import godot_exec
        result = godot_exec(code=code)
        if isinstance(result, str):
            result = _json.loads(result)
        return result if isinstance(result, dict) else {"status": "success", "data": result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def runtime_info() -> dict:
    """Obtém FPS, draw calls, memória do jogo rodando."""
    try:
        from server import send_bridge_command, BridgeUnavailable
    except ImportError:
        return {"status": "error", "message": "Bridge não disponível"}
    try:
        result = send_bridge_command({"cmd": "runtime_info"})
        return {"status": "success", "data": result}
    except BridgeUnavailable as e:
        return {"status": "error", "message": str(e)}


__all__ = [
    "run_project",
    "stop_project",
    "wait_bridge",
    "exec_gdscript",
    "runtime_info",
]
