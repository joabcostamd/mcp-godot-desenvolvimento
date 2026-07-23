"""
scripts/_godot_utils.py — Utilitários compartilhados para scripts que invocam Godot.

Usado por: rodar_testes_pares.py, mutar.py.
"""

import os
import subprocess
from subprocess import DEVNULL
from typing import Optional, Tuple

DEFAULT_GODOT = r"C:\Godot\Godot_v4.7-stable_win64.exe"
GDTOOL = "addons/gdUnit4/bin/GdUnitCmdTool.gd"


def encontrar_godot() -> Optional[str]:
    """Encontra o executável do Godot (caminho padrão, GODOT_BIN, PATH)."""
    if os.path.exists(DEFAULT_GODOT):
        return DEFAULT_GODOT

    env_godot = os.environ.get("GODOT_BIN")
    if env_godot and os.path.exists(env_godot):
        return env_godot

    import shutil
    for name in ["godot", "Godot_v4.7-stable_win64"]:
        p = shutil.which(name)
        if p:
            return p

    return None


def rodar_godot_headless(
    godot_exe: str,
    test_paths: list,
    project_path: str = ".",
    timeout: int = 120,
) -> Tuple[int, str, str]:
    """
    Roda Godot em modo headless com GdUnit4 CLI.

    Args:
        godot_exe: Caminho do executável do Godot.
        test_paths: Lista de paths res:// para testar.
        project_path: Caminho do projeto Godot.
        timeout: Timeout em segundos.

    Returns:
        (exit_code, stdout, stderr).
    """
    args = [
        godot_exe,
        "--headless",
        "--path", project_path,
        "-s", GDTOOL,
        "--ignoreHeadlessMode",
        "-c",
    ]
    for tp in test_paths:
        args.extend(["-a", tp])

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            stdin=DEVNULL,  # Regra do projeto: evita deadlock no Windows
            timeout=timeout,
            cwd=os.path.abspath(project_path),
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout após {timeout}s"
