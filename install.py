#!/usr/bin/env python3
"""
install.py — Instalador Universal MCP IA DEV
=============================================
1 clique: detecta Godot + Python, configura tudo, cria atalho na área de trabalho.

Uso:
    python install.py                  # Instalação padrão
    python install.py --dir "C:/MeuMCP"  # Pasta customizada
"""

import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════
# Constantes
# ══════════════════════════════════════════════════════════════════════

ROOT = Path(__file__).resolve().parent
GODOT_COMMON_PATHS = [
    r"C:\Godot\Godot_v4.7-stable_win64.exe",
    r"C:\Godot\Godot_v4.7-stable_win64_console.exe",
    r"C:\Program Files\Godot\Godot_v4.7-stable_win64.exe",
    str(Path.home() / "Godot" / "Godot_v4.7-stable_win64.exe"),
]

# ══════════════════════════════════════════════════════════════════════
# Detectores automáticos
# ══════════════════════════════════════════════════════════════════════

def find_godot() -> str | None:
    """Encontra o executável do Godot no sistema."""
    # 1. Verifica paths comuns
    for p in GODOT_COMMON_PATHS:
        if Path(p).exists():
            return p

    # 2. Procura no PATH
    for ext in [".exe", ".EXE"]:
        result = shutil.which(f"Godot_v4.7-stable_win64{ext}")
        if result:
            return result

    # 3. Procura qualquer Godot*.exe no PATH
    for d in os.environ.get("PATH", "").split(os.pathsep):
        try:
            for f in Path(d).glob("Godot*.exe"):
                return str(f)
        except OSError:
            continue

    # 4. Varredura em drives comuns
    for drive in ["C:", "D:"]:
        search_dirs = [
            Path(drive) / "Godot",
            Path(drive) / "Program Files" / "Godot",
        ]
        for sd in search_dirs:
            if sd.exists():
                for f in sd.glob("**/Godot*.exe"):
                    return str(f)

    return None


def find_python() -> str | None:
    """Encontra o Python 3 no sistema."""
    for cmd in ["python3", "python", "py"]:
        for ext in [".exe", ""]:
            result = shutil.which(f"{cmd}{ext}")
            if result:
                try:
                    v = subprocess.check_output(
                        [result, "--version"], stderr=subprocess.STDOUT, text=True
                    )
                    if "Python 3" in v:
                        return result
                except Exception:
                    continue
    return None


def find_godot_projects() -> list[dict]:
    """Encontra projetos Godot recentes."""
    projects = []
    cfg_path = Path.home() / "AppData" / "Roaming" / "Godot" / "projects.cfg"
    if cfg_path.exists():
        content = cfg_path.read_text(encoding="utf-8")
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                p = line[1:-1]
                if Path(p).exists():
                    godot_file = Path(p) / "project.godot"
                    if godot_file.exists():
                        projects.append({
                            "path": str(Path(p).resolve()),
                            "name": Path(p).name,
                        })
    return projects


# ══════════════════════════════════════════════════════════════════════
# Instalação
# ══════════════════════════════════════════════════════════════════════

def create_config(godot_path: str, python_path: str, target_dir: Path) -> dict:
    """Cria config.json com paths detectados."""
    config = {
        "godot_path": godot_path,
        "godot_console_path": godot_path.replace("_win64.exe", "_win64_console.exe"),
        "python_path": python_path,
        "default_project": "",
        "addon_port": 9080,
        "game_port": 9081,
        "timeouts": {"fast": 15, "compile": 60, "export": 300},
    }
    cfg_file = target_dir / "config.json"
    cfg_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    return config


def install_addon_to_project(project_path: str, source_addon: Path) -> bool:
    """Instala o addon MCP em um projeto Godot."""
    dest = Path(project_path) / "addons" / "mcp_addon"
    dest.mkdir(parents=True, exist_ok=True)

    # Copia arquivos do addon
    for f in source_addon.glob("*"):
        if f.is_file() and not f.name.endswith(".uid"):
            shutil.copy2(f, dest / f.name)

    # Ativa plugin no project.godot
    godot_file = Path(project_path) / "project.godot"
    if not godot_file.exists():
        return False

    content = godot_file.read_text(encoding="utf-8")
    plugin_line = 'enabled=PackedStringArray("res://addons/mcp_addon/plugin.cfg")'

    if "[editor_plugins]" not in content:
        content += f"\n[editor_plugins]\n{plugin_line}\n"
    elif plugin_line not in content:
        content = content.replace("[editor_plugins]", f"[editor_plugins]\n{plugin_line}")

    godot_file.write_text(content, encoding="utf-8")
    return True


def create_desktop_shortcut(target_bat: Path):
    """Cria atalho na área de trabalho do Windows via PowerShell (zero dependências)."""
    desktop = str(Path.home() / "Desktop")
    lnk_path = f"{desktop}\\MCP IA DEV.lnk"

    ps_cmd = (
        f'$ws = New-Object -ComObject WScript.Shell; '
        f'$s = $ws.CreateShortcut("{lnk_path}"); '
        f'$s.TargetPath = "{target_bat}"; '
        f'$s.WorkingDirectory = "{target_bat.parent}"; '
        f'$s.Description = "Abre Godot + MCP IA DEV"; '
        f'$s.IconLocation = "{find_godot()},0"; '
        f'$s.Save()'
    )
    subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, timeout=15)
    return lnk_path


def create_launcher_bat(target_dir: Path, python_path: str) -> Path:
    """Cria start-mcp.bat genérico."""
    bat_content = f'''@echo off
chcp 65001 >nul
title MCP IA DEV

cd /d "{target_dir}"

echo.
echo 🔌 MCP IA DEV — Iniciando...
echo.

"{python_path}" launch.py %*

echo.
pause
'''
    bat_file = target_dir / "start-mcp.bat"
    bat_file.write_text(bat_content, encoding="utf-8")
    return bat_file


# ══════════════════════════════════════════════════════════════════════
# UI Simples (modo texto com emojis)
# ══════════════════════════════════════════════════════════════════════

def print_banner():
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║        🔌 MCP IA DEV — INSTALADOR           ║")
    print("║     Conecte IAs ao Godot em 1 clique        ║")
    print("╚══════════════════════════════════════════════╝")
    print()


def print_step(step: int, msg: str, ok: bool = True, detail: str = ""):
    icon = "✅" if ok else "❌"
    print(f"  {icon} Passo {step}: {msg}")
    if detail:
        print(f"     {detail}")


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Instalador MCP IA DEV")
    parser.add_argument("--dir", "-d", help="Pasta de instalação (padrão: C:\\MCP-Godot-IA-Dev)")
    parser.add_argument("--silent", "-s", action="store_true", help="Modo silencioso")
    args = parser.parse_args()

    if not args.silent:
        print_banner()

    target_dir = Path(args.dir) if args.dir else Path("C:/MCP-Godot-IA-Dev")

    # Passo 1: Detectar Godot
    godot_path = find_godot()
    if not godot_path:
        print_step(1, "Detectar Godot", False, "Godot 4.7 não encontrado. Instale o Godot primeiro: https://godotengine.org")
        input("\nPressione Enter para sair...")
        sys.exit(1)
    print_step(1, "Detectar Godot", True, godot_path)

    # Passo 2: Detectar Python
    python_path = find_python()
    if not python_path:
        print_step(2, "Detectar Python", False, "Python 3 não encontrado. Instale: https://python.org")
        input("\nPressione Enter para sair...")
        sys.exit(1)
    print_step(2, "Detectar Python", True, python_path)

    # Passo 3: Copiar arquivos MCP
    if target_dir != ROOT:
        target_dir.mkdir(parents=True, exist_ok=True)
        for item in ROOT.iterdir():
            if item.name not in ["__pycache__", ".git", ".gitignore", "test_fast.py"]:
                dest = target_dir / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
        print_step(3, "Copiar arquivos MCP", True, str(target_dir))
    else:
        print_step(3, "Copiar arquivos MCP", True, "já está na pasta correta")

    # Passo 4: Criar config.json
    config = create_config(godot_path, python_path, target_dir)
    print_step(4, "Criar config.json", True, f"porta: {config['addon_port']}")

    # Passo 5: Detectar projetos Godot
    projects = find_godot_projects()
    if projects:
        print_step(5, "Encontrar projetos", True, f"{len(projects)} projeto(s)")
        for p in projects:
            print(f"     📁 {p['name']}")
    else:
        print_step(5, "Encontrar projetos", True, "nenhum (você pode criar depois)")

    # Passo 6: Instalar addon nos projetos
    addon_src = Path(__file__).resolve().parent / "addons" / "mcp_addon"
    installed = 0
    for p in projects:
        if install_addon_to_project(p["path"], addon_src):
            installed += 1
    print_step(6, "Instalar addon nos projetos", True, f"{installed}/{len(projects)} projetos")

    # Passo 7: Criar launcher .bat
    bat_file = create_launcher_bat(target_dir, python_path)
    print_step(7, "Criar launcher", True, str(bat_file))

    # Passo 8: Criar atalho na Área de Trabalho
    shortcut = create_desktop_shortcut(bat_file)
    print_step(8, "Atalho Área de Trabalho", True, "MCP IA DEV")

    # Passo 9: Instalar dependências Python
    try:
        subprocess.run(
            [python_path, "-m", "pip", "install", "-r", str(target_dir / "requirements.txt"), "--quiet"],
            capture_output=True, timeout=120,
        )
        print_step(9, "Dependências Python", True, "ok")
    except Exception:
        print_step(9, "Dependências Python", True, "já instaladas ou offline")

    # Pronto!
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║     ✅ INSTALAÇÃO CONCLUÍDA!                ║")
    print("╠══════════════════════════════════════════════╣")
    print(f"║  📁 Pasta: {str(target_dir)[:36]:<36s} ║")
    print(f"║  🖱️  Atalho: MCP IA DEV na Área de Trabalho  ║")
    print("╠══════════════════════════════════════════════╣")
    print("║  PRÓXIMOS PASSOS:                           ║")
    print("║  1. Clique no atalho MCP IA DEV             ║")
    print("║  2. Godot abre com o dock MCP IA DEV        ║")
    print("║  3. Use a IA no VS Code para criar jogos!   ║")
    print("╚══════════════════════════════════════════════╝")
    print()

    if not args.silent:
        try:
            input("Pressione Enter para sair...")
        except (RuntimeError, EOFError, OSError):
            pass


if __name__ == "__main__":
    main()
