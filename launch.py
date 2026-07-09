#!/usr/bin/env python3
"""launch.py — Lançador MCP IA DEV.

UM comando para conectar tudo:
    python launch.py

Fluxo:
1. Abre Godot com o projeto (ou Project Manager se nenhum configurado)
2. Aguarda o bridge TCP ficar disponível (porta 9080)
3. Mostra status: "Pronto para receber comandos da IA!"

Uso:
    python launch.py                    # Abre com projeto padrão
    python launch.py --project <path>   # Abre com projeto específico
    python launch.py --no-godot         # Só verifica bridge (Godot já aberto)
    python launch.py --monitor          # Mantém monitor de status ativo
"""

import argparse
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ══════════════════════════════════════════════════════════════════════
# Config
# ══════════════════════════════════════════════════════════════════════

def load_config() -> dict:
    cfg_path = ROOT / "config.json"
    if cfg_path.exists():
        with open(cfg_path, encoding="utf-8") as f:
            return json.load(f)
    return {}

# ══════════════════════════════════════════════════════════════════════
# Terminal colors (Windows 10+)
# ══════════════════════════════════════════════════════════════════════

G = "\033[92m"  # green
R = "\033[91m"  # red
Y = "\033[93m"  # yellow
B = "\033[94m"  # blue
C = "\033[96m"  # cyan
W = "\033[97m"  # white bold
X = "\033[0m"   # reset

def ok(msg: str) -> str:   return f"{G}  ✓{X} {msg}"
def err(msg: str) -> str:  return f"{R}  ✗{X} {msg}"
def info(msg: str) -> str: return f"{B}  ℹ{X} {msg}"
def warn(msg: str) -> str: return f"{Y}  ⚠{X} {msg}"
def hdr(msg: str) -> str:  return f"\n{W}{msg}{X}"
def sub(msg: str) -> str:  return f"    {msg}"

# ══════════════════════════════════════════════════════════════════════
# Core
# ══════════════════════════════════════════════════════════════════════

def check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    """Verifica se a porta TCP está respondendo."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except Exception:
        return False


def launch_godot(godot_path: str, project_path: str | None = None) -> subprocess.Popen | None:
    """Abre o Godot (editor GUI)."""
    if not Path(godot_path).exists():
        print(err(f"Godot não encontrado: {godot_path}"))
        return None

    cmd = [godot_path, "--editor"]
    if project_path and Path(project_path).exists():
        cmd.extend(["--path", str(project_path)])
        print(info(f"Abrindo projeto: {project_path}"))
    else:
        print(info("Abrindo Project Manager..."))

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        return proc
    except Exception as e:
        print(err(f"Erro ao abrir Godot: {e}"))
        return None


def wait_for_bridge(port: int, timeout: float = 30.0) -> bool:
    """Aguarda o bridge TCP do editor ficar disponível."""
    print(info(f"Aguardando bridge TCP na porta {port}..."), end="", flush=True)
    start = time.time()
    dots = 0
    while time.time() - start < timeout:
        if check_port("127.0.0.1", port, timeout=0.5):
            print(f"\r{ok(f'Bridge TCP disponível na porta {port}')}   ")
            return True
        dots = (dots + 1) % 4
        print(f"\r{Y}  ⏳{X} Aguardando bridge TCP na porta {port}{'.' * dots}  ", end="", flush=True)
        time.sleep(1.0)
    print(f"\r{err(f'Timeout: bridge TCP não respondeu em {timeout:.0f}s')}   ")
    return False


def show_status(cfg: dict, bridge_ok: bool):
    """Exibe status completo."""
    print(hdr("┌──────────────────────────────────────────┐"))
    print(hdr("│         🔌 MCP IA DEV — STATUS           │"))
    print(hdr("└──────────────────────────────────────────┘"))

    if bridge_ok:
        print(ok(f"Bridge Editor  — porta {cfg.get('addon_port', 9080)}"))
    else:
        print(err(f"Bridge Editor  — porta {cfg.get('addon_port', 9080)} (offline)"))

    game_port = cfg.get("game_port", 9081)
    if check_port("127.0.0.1", game_port):
        print(ok(f"Bridge Jogo    — porta {game_port}"))
    else:
        print(warn(f"Bridge Jogo    — porta {game_port} (jogo não está rodando)"))

    godot = cfg.get("godot_path", "")
    if godot and Path(godot).exists():
        print(ok(f"Godot          — {Path(godot).name}"))
    else:
        print(err("Godot          — não configurado"))

    proj = cfg.get("default_project", "")
    if proj and Path(proj).exists():
        print(ok(f"Projeto        — {Path(proj).name}"))
    elif proj:
        print(warn(f"Projeto        — caminho não encontrado"))

    print()

    if bridge_ok:
        print(f"{G}╔════════════════════════════════════════════╗{X}")
        print(f"{G}║  ✅ PRONTO! A IA pode usar o MCP agora.   ║{X}")
        print(f"{G}║  Conectado na porta {cfg.get('addon_port', 9080):<21}║{X}")
        print(f"{G}╚════════════════════════════════════════════╝{X}")
    else:
        print(f"{Y}⚠  Godot aberto mas bridge não detectado.{X}")
        print(f"{Y}   Verifique se o plugin 'MCP IA DEV' está ativo em:{X}")
        print(f"{Y}   Project → Project Settings → Plugins{X}")


def monitor_loop(cfg: dict):
    """Loop de monitoramento contínuo."""
    port = cfg.get("addon_port", 9080)
    game_port = cfg.get("game_port", 9081)
    print(info("Monitor ativo — Ctrl+C para sair"))
    try:
        while True:
            editor_ok = check_port("127.0.0.1", port)
            game_ok = check_port("127.0.0.1", game_port)
            status_line = f"  Editor: {'✅' if editor_ok else '❌'}  |  Jogo: {'✅' if game_ok else '❌'}  |  {time.strftime('%H:%M:%S')}"
            print(f"\r{status_line}", end="", flush=True)
            time.sleep(2.0)
    except KeyboardInterrupt:
        print(f"\n{info('Monitor encerrado.')}")


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="MCP IA DEV — Lançador")
    parser.add_argument("--project", "-p", help="Caminho do projeto Godot")
    parser.add_argument("--no-godot", action="store_true", help="Não abrir Godot (só verificar bridge)")
    parser.add_argument("--monitor", "-m", action="store_true", help="Manter monitor de status ativo")
    args = parser.parse_args()

    cfg = load_config()
    port = cfg.get("addon_port", 9080)
    godot_path = cfg.get("godot_path", "")
    project = args.project or cfg.get("default_project", "")

    print(f"\n{B}🔌 MCP IA DEV — Lançador{X}\n")

    # Passo 1: Abrir Godot
    if not args.no_godot:
        if not godot_path:
            print(err("godot_path não configurado em config.json"))
            sys.exit(1)
        launch_godot(godot_path, project if project else None)

    # Passo 2: Aguardar bridge
    bridge_ok = wait_for_bridge(port, timeout=45.0 if not args.no_godot else 5.0)

    # Passo 3: Status
    show_status(cfg, bridge_ok)

    # Passo 4: Monitor (opcional)
    if args.monitor:
        monitor_loop(cfg)


if __name__ == "__main__":
    main()
