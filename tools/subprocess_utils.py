"""subprocess_utils.py — Wrapper seguro para subprocess em handlers MCP.

Problema: subprocess.run() sem stdin=DEVNULL herda o pipe stdin do
servidor MCP (stdio JSON-RPC), causando deadlock na thread pool do
asyncio no Windows (bugs.python.org/issue28348, #38427).

Solução: usar SEMPRE run_subprocess_safe() em qualquer handler chamável
via protocolo MCP. Para chamadas diretas (fora do MCP), subprocess.run
comum funciona normalmente, mas não há desvantagem em usar o wrapper.
"""

import subprocess
from typing import Any


def run_subprocess_safe(
    cmd: list[str] | str,
    timeout: int = 30,
    **kwargs: Any,
) -> subprocess.CompletedProcess:
    """Wrapper seguro para subprocess.run em handlers MCP no Windows.

    Força stdin=DEVNULL e close_fds=True para evitar deadlock quando o
    processo filho herda o pipe stdin do servidor MCP JSON-RPC/stdio.

    Args:
        cmd: Comando (lista de argumentos ou string com shell=True).
        timeout: Timeout em segundos.
        **kwargs: Repassados a subprocess.run (exceto stdin e close_fds,
                  que são fixados para segurança).

    Returns:
        subprocess.CompletedProcess com stdout/stderr capturados.
    """
    return subprocess.run(
        cmd,
        stdin=subprocess.DEVNULL,
        close_fds=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        **kwargs,
    )
