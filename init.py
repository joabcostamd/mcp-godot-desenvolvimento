#!/usr/bin/env python3
"""
init.py — Instalador de 1 comando do MCP Godot Agent

Uso:
    python init.py                  # Instalação interativa
    python init.py --dir "C:/MeuJogo"  # Pasta específica
    python init.py --silent         # Sem perguntas (usa defaults)

Etapas:
    1. Detectar Python, Godot, VS Code
    2. Criar ambiente virtual Python
    3. Escrever configuração MCP no .vscode/mcp.json (merge)
    4. Perguntar/criar pasta do projeto
    5. Criar projeto Godot e abrir editor
    6. Verificar conectividade (bridge)
    7. Imprimir próximo passo

Princípios:
    - Idempotente: rodar 2x não quebra
    - Fail-safe: cada etapa reporta [OK] ou [FALHA] em português
    - Zero stack trace para o usuário final (modo normal)
    - Merge, nunca overwrite, em configurações existentes
"""

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import textwrap
import time
import urllib.request
import zipfile
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════
# Constantes
# ══════════════════════════════════════════════════════════════════════

ROOT = Path(__file__).resolve().parent
REQUIREMENTS = ROOT / "requirements.txt"
SERVER_SCRIPT = ROOT / "server.py"
ADDON_SRC = ROOT / "addons" / "mcp_addon"
RUNTIME_BRIDGE_SRC = ROOT / "addons" / "mcp_runtime_bridge"

GODOT_COMMON_PATHS = [
    r"C:\Godot\Godot_v4.7-stable_win64.exe",
    r"C:\Godot\Godot_v4.7-stable_win64_console.exe",
    r"C:\Program Files\Godot\Godot_v4.7-stable_win64.exe",
    str(Path.home() / "Godot" / "Godot_v4.7-stable_win64.exe"),
]

DEFAULT_PROJECT_PARENT = Path("C:/Projetos")
CLOUD_SYNC_PATTERNS = ["OneDrive", "Dropbox", "Google Drive", "iCloud"]


LSP_HOST = "127.0.0.1"
LSP_PORT = 6005
WS_HOST = "127.0.0.1"
WS_PORT = 9082
POLL_INTERVAL = 0.5
POLL_TIMEOUT_LSP = 30.0   # Godot pode demorar para abrir
POLL_TIMEOUT_WS = 30.0    # Addon inicia após importar assets do projeto


TEMPLATE_BASE_URL = "https://github.com/godotengine/godot-builds/releases/download"


# ══════════════════════════════════════════════════════════════════════
# Detectores
# ══════════════════════════════════════════════════════════════════════

def find_godot() -> str | None:
    """Encontra o executável do Godot 4.x no sistema."""
    # 1. Paths comuns
    for p in GODOT_COMMON_PATHS:
        if Path(p).exists():
            # Verifica se é 4.x
            try:
                v = subprocess.check_output(
                    [p, "--version"],
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=10,
                )
                if v.strip().startswith("4."):
                    return p
            except Exception:
                continue

    # 2. PATH
    result = shutil.which("godot")
    if result:
        try:
            v = subprocess.check_output(
                [result, "--version"],
                stderr=subprocess.STDOUT,
                text=True,
                timeout=10,
            )
            if v.strip().startswith("4."):
                return result
        except Exception:
            pass

    # 3. Varredura em C:\Godot e C:\Program Files\Godot
    for drive in ["C:", "D:"]:
        for base in [Path(drive) / "Godot", Path(drive) / "Program Files" / "Godot"]:
            if base.exists():
                for f in base.glob("**/Godot*.exe"):
                    try:
                        v = subprocess.check_output(
                            [str(f), "--version"],
                            stderr=subprocess.STDOUT,
                            text=True,
                            timeout=10,
                        )
                        if v.strip().startswith("4."):
                            return str(f)
                    except Exception:
                        continue

    return None


def find_python() -> str | None:
    """Encontra Python 3.10+ no sistema."""
    for cmd in ["python3", "python", "py"]:
        result = shutil.which(cmd)
        if result:
            try:
                v = subprocess.check_output(
                    [result, "--version"],
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=10,
                )
                if "Python 3" in v:
                    return result
            except Exception:
                continue
    return None


def find_vscode() -> str | None:
    """Encontra VS Code (ou Cursor) instalado."""
    for cmd in ["code", "code-insiders", "cursor"]:
        result = shutil.which(cmd)
        if result:
            return result

    # Fallback: paths comuns
    for base in [
        Path.home() / "AppData" / "Local" / "Programs" / "Microsoft VS Code" / "bin" / "code.cmd",
        Path("C:/") / "Program Files" / "Microsoft VS Code" / "bin" / "code.cmd",
    ]:
        if base.exists():
            return str(base)

    return None


def get_python_version(python_path: str) -> tuple[int, int]:
    """Retorna (major, minor) da versão do Python."""
    try:
        v = subprocess.check_output(
            [python_path, "--version"],
            stderr=subprocess.STDOUT,
            text=True,
            timeout=10,
        )
        parts = v.strip().split()
        if len(parts) >= 2:
            major, minor = parts[1].split(".")[:2]
            return int(major), int(minor)
    except Exception:
        pass
    return 0, 0


def get_godot_version(godot_path: str) -> str | None:
    """Tenta obter a versão do Godot."""
    try:
        v = subprocess.check_output(
            [godot_path, "--version"],
            stderr=subprocess.STDOUT,
            text=True,
            timeout=15,
        )
        return v.strip()
    except Exception:
        return None


def get_godot_version_short(godot_path: str) -> str | None:
    """Extrai a versão curta do Godot (ex: '4.7' ou '4.7.1') para paths."""
    full = get_godot_version(godot_path)
    if full:
        # "4.7.stable.official.5b4e0cb0f" → "4.7"
        # "4.7.1.stable.official.xxx" → "4.7.1"
        parts = full.split(".")
        if len(parts) >= 3 and parts[2] == "stable":
            # 4.7.stable → "4.7"
            return f"{parts[0]}.{parts[1]}"
        elif len(parts) >= 4 and parts[3] == "stable":
            # 4.7.1.stable → "4.7.1"
            return f"{parts[0]}.{parts[1]}.{parts[2]}"
        elif len(parts) >= 2:
            return f"{parts[0]}.{parts[1]}"
    return None


def get_godot_version_tag(godot_path: str) -> str | None:
    """Extrai a tag de release do Godot (ex: '4.7-stable' ou '4.7.1-stable')."""
    full = get_godot_version(godot_path)
    if full:
        # "4.7.stable.official.5b4e0cb0f" → "4.7-stable"
        # "4.7.1.stable.official.xxx" → "4.7.1-stable"
        parts = full.split(".")
        for i, p in enumerate(parts):
            if p == "stable":
                base = ".".join(parts[:i])
                return f"{base}-stable"
    return None


def is_cloud_synced(path: Path) -> bool:
    """Detecta se o caminho está em pasta sincronizada (OneDrive, Dropbox, etc)."""
    try:
        # Tenta resolver, fallback para absolute em caminhos não-existentes
        resolved = path.resolve()
    except (OSError, RuntimeError):
        resolved = path.absolute()
    path_str = str(resolved).lower()
    for pattern in CLOUD_SYNC_PATTERNS:
        if pattern.lower() in path_str:
            return True
    return False


# ══════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════

def print_banner():
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║     🎮 MCP GODOT AGENT — INSTALADOR         ║")
    print("║   Crie jogos em Godot com linguagem natural  ║")
    print("╚══════════════════════════════════════════════╝")
    print()


def print_step(step: int, msg: str, ok: bool = True, detail: str = ""):
    icon = "[OK]" if ok else "[FALHA]"
    print(f"  {icon}  Passo {step}: {msg}")
    if detail:
        for line in detail.split("\n"):
            print(f"         {line}")


def print_final_box(project_dir: Path):
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║     ✅ INSTALAÇÃO CONCLUÍDA!                ║")
    print("╠══════════════════════════════════════════════╣")
    pdir = str(project_dir)
    if len(pdir) > 36:
        pdir = "..." + pdir[-33:]
    print(f"║  📁 Projeto: {pdir:<36s} ║")
    print("╠══════════════════════════════════════════════╣")
    print("║  PRÓXIMO PASSO:                             ║")
    print("║  1. Abra esta pasta no VS Code              ║")
    print("║  2. No chat do Copilot, digite: /plan       ║")
    print("║  3. A IA vai te guiar na criação do jogo!   ║")
    print("╚══════════════════════════════════════════════╝")
    print()


# ══════════════════════════════════════════════════════════════════════
# Utilidades
# ══════════════════════════════════════════════════════════════════════

def _is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """Verifica se uma porta TCP está aberta (Godot LSP ou Addon WS)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════
# Etapas
# ══════════════════════════════════════════════════════════════════════

def step1_detect(godot_path: str | None, python_path: str | None) -> tuple[str, str]:
    """Detecta ou solicita Godot e Python. Retorna (godot, python)."""
    # ── Godot ──
    if godot_path:
        ver = get_godot_version(godot_path)
        if ver and not ver.strip().startswith("4."):
            print_step(1, "Detectar Godot", False,
                       f"Godot {ver} encontrado, mas precisa da versão 4.x.\n"
                       f"         Caminho: {godot_path}\n"
                       "         Baixe Godot 4.7: https://godotengine.org/download")
            sys.exit(1)
        print_step(1, "Detectar Godot", True, f"{godot_path}\n         versão: {ver or 'desconhecida'}")
    else:
        godot_path = find_godot()
        if godot_path:
            ver = get_godot_version(godot_path)
            print_step(1, "Detectar Godot", True, f"{godot_path}\n         versão: {ver or 'desconhecida'}")
        else:
            print_step(1, "Detectar Godot", False,
                       "Godot 4.7 não encontrado.\n"
                       "         Baixe em: https://godotengine.org/download\n"
                       "         Coloque o .exe em C:\\Godot\\")
            sys.exit(1)

    # ── Python ──
    if python_path:
        major, minor = get_python_version(python_path)
        print_step(2, "Detectar Python", True, f"{python_path}\n         versão: {major}.{minor}")
    else:
        python_path = find_python()
        if python_path:
            major, minor = get_python_version(python_path)
            if major < 3 or (major == 3 and minor < 10):
                print_step(2, "Detectar Python", False,
                           f"Python {major}.{minor} encontrado, mas precisa de 3.10+.\n"
                           "         Instale: https://python.org/downloads")
                sys.exit(1)
            print_step(2, "Detectar Python", True, f"{python_path}\n         versão: {major}.{minor}")
        else:
            print_step(2, "Detectar Python", False,
                       "Python 3.10+ não encontrado.\n"
                       "         Instale: https://python.org/downloads\n"
                       "         Marque 'Add Python to PATH' na instalação.")
            sys.exit(1)

    # ── VS Code ──
    vscode = find_vscode()
    if vscode:
        print_step(3, "Detectar VS Code", True, vscode)
    else:
        print_step(3, "Detectar VS Code", False,
                   "VS Code não encontrado no PATH.\n"
                   "         Instale: https://code.visualstudio.com\n"
                   "         O Copilot precisa do VS Code para funcionar.")

    return godot_path, python_path


def step2_venv(root: Path, python_path: str) -> Path:
    """Cria ou verifica ambiente virtual Python. Retorna path do python do venv."""
    venv_dir = root / ".venv"
    venv_python = venv_dir / "Scripts" / "python.exe"

    if venv_python.exists():
        print_step(4, "Ambiente virtual", True, f"já existe: {venv_dir}")
        return venv_python

    # Se .venv existe como diretório mas python.exe foi perdido, recria
    if venv_dir.exists():
        print_step(4, "Ambiente virtual", True,
                   f"pasta existe mas está incompleta — recriando: {venv_dir}")
        shutil.rmtree(venv_dir, ignore_errors=True)

    try:
        subprocess.run(
            [python_path, "-m", "venv", str(venv_dir)],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        print_step(4, "Criar ambiente virtual", True, str(venv_dir))
    except subprocess.CalledProcessError as e:
        print_step(4, "Criar ambiente virtual", False,
                   f"Não foi possível criar venv.\n"
                   f"         Erro: {e.stderr.strip() if e.stderr else 'desconhecido'}")
        sys.exit(1)

    # Instalar dependências
    if REQUIREMENTS.exists():
        try:
            subprocess.run(
                [str(venv_python), "-m", "pip", "install", "-r", str(REQUIREMENTS), "--quiet"],
                check=True,
                capture_output=True,
                text=True,
                timeout=180,
            )
            print_step(5, "Instalar dependências Python", True, "requirements.txt")
        except subprocess.CalledProcessError:
            print_step(5, "Instalar dependências Python", False,
                       "Falha ao instalar requirements.txt.\n"
                       "         Verifique sua conexão com a internet.")
            sys.exit(1)
        except subprocess.TimeoutExpired:
            print_step(5, "Instalar dependências Python", False,
                       "Timeout ao instalar requirements.txt (>180s).\n"
                       "         Verifique sua conexão com a internet.")
            sys.exit(1)
    else:
        print_step(5, "Instalar dependências Python", True, "requirements.txt não encontrado — pulando")

    return venv_python


def step3_mcp_config(project_dir: Path, venv_python: Path) -> None:
    """Escreve ou mescla .vscode/mcp.json no projeto Godot."""
    vscode_dir = project_dir / ".vscode"
    mcp_json = vscode_dir / "mcp.json"

    new_server = {
        "godot-agent": {
            "type": "stdio",
            "command": str(venv_python),
            "args": [str(SERVER_SCRIPT)],
            "cwd": str(ROOT),
            "env": {
                "PYTHONUNBUFFERED": "1",
                "PYTHONIOENCODING": "utf-8",
            },
        }
    }

    vscode_dir.mkdir(parents=True, exist_ok=True)

    if mcp_json.exists():
        # ── MESCLAR, nunca sobrescrever ──
        try:
            existing = json.loads(mcp_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print_step(7, "Configuração MCP", False,
                       f"{mcp_json} existe mas está corrompido.\n"
                       "         Remova o arquivo manualmente e rode init.py novamente.")
            return

        if not isinstance(existing, dict):
            print_step(7, "Configuração MCP", False,
                       f"{mcp_json} não é um objeto JSON válido (esperado: {{}}).\n"
                       "         Remova o arquivo manualmente e rode init.py novamente.")
            return

        existing_servers = existing.get("servers", {})
        if not isinstance(existing_servers, dict):
            existing_servers = {}

        if "godot-agent" in existing_servers:
            print_step(7, "Configuração MCP", True,
                       f"já configurado em {mcp_json}\n"
                       "         (mantido como estava — merge)")
            return

        existing["servers"] = {**existing_servers, **new_server}
        mcp_json.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
        print_step(7, "Configuração MCP", True,
                   f"{mcp_json}\n"
                   f"         (mesclado — servidores existentes preservados)")
    else:
        config = {"servers": new_server}
        mcp_json.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        print_step(7, "Configuração MCP", True, str(mcp_json))


def step4_install_addon(project_dir: Path) -> None:
    """Instala o addon MCP no projeto Godot."""
    if not ADDON_SRC.exists():
        print_step(8, "Instalar addon MCP", False,
                   "Pasta addons/mcp_addon não encontrada no MCP.\n"
                   "         O servidor MCP parece incompleto.")
        return

    dest = project_dir / "addons" / "mcp_addon"
    dest.mkdir(parents=True, exist_ok=True)

    files_copied = 0
    for f in ADDON_SRC.glob("*"):
        if f.is_file() and not f.name.endswith(".uid"):
            shutil.copy2(f, dest / f.name)
            files_copied += 1

    # Copia runtime_bridge também
    if RUNTIME_BRIDGE_SRC.exists():
        bridge_dest = project_dir / "addons" / "mcp_runtime_bridge"
        bridge_dest.mkdir(parents=True, exist_ok=True)
        for f in RUNTIME_BRIDGE_SRC.glob("*"):
            if f.is_file() and not f.name.endswith(".uid"):
                shutil.copy2(f, bridge_dest / f.name)

    # Ativa plugin no project.godot (merge com plugins existentes)
    godot_file = project_dir / "project.godot"
    if godot_file.exists():
        content = godot_file.read_text(encoding="utf-8")
        plugin_path = "res://addons/mcp_addon/plugin.cfg"

        if "[editor_plugins]" not in content:
            # Sem plugins: cria seção nova
            content += f"\n[editor_plugins]\nenabled=PackedStringArray(\"{plugin_path}\")\n"
        else:
            # Já tem plugins: mescla na PackedStringArray existente
            match = re.search(
                r'enabled\s*=\s*PackedStringArray\(([^)]*)\)',
                content
            )
            if match:
                current = match.group(1).strip()
                if plugin_path not in current:
                    # Adiciona ao array existente
                    if current:
                        new_array = f'enabled=PackedStringArray({current}, "{plugin_path}")'
                    else:
                        new_array = f'enabled=PackedStringArray("{plugin_path}")'
                    content = content[:match.start()] + new_array + content[match.end():]
                # plugin já existe → não faz nada
            elif 'enabled=PackedStringArray("' + plugin_path + '")' not in content:
                # PackedStringArray não encontrada, mas seção existe: adiciona
                content = content.replace(
                    "[editor_plugins]",
                    f"[editor_plugins]\nenabled=PackedStringArray(\"{plugin_path}\")"
                )

        godot_file.write_text(content, encoding="utf-8")
        print_step(8, "Instalar addon MCP", True,
                   f"{files_copied} arquivos → {dest}\n"
                   "         plugin ativado no project.godot")
    else:
        print_step(8, "Instalar addon MCP", True,
                   f"{files_copied} arquivos → {dest}\n"
                   "         (project.godot não encontrado — plugin não ativado)")


def step5_verify_connection() -> bool:
    """Verifica se Godot Editor e Addon Bridge estão respondendo.

    Polling nas portas LSP (6005) e WebSocket (9082) com timeout.
    Se Godot já estava aberto, as portas respondem imediatamente.

    Returns:
        True se ambas as portas responderam, False caso contrário.
    """
    # ── Verificar LSP (Godot Editor) ──
    if _is_port_open(LSP_HOST, LSP_PORT):
        print_step(11, "Godot Editor (LSP :6005)", True,
                   "editor já estava respondendo")
    else:
        print_step(11, "Aguardando Godot Editor (LSP :6005)", True,
                   f"polling até {POLL_TIMEOUT_LSP:.0f}s...")
        start = time.time()
        while time.time() - start < POLL_TIMEOUT_LSP:
            if _is_port_open(LSP_HOST, LSP_PORT):
                elapsed = (time.time() - start) * 1000
                print(f"         conectado em {elapsed:.0f}ms")
                break
            time.sleep(POLL_INTERVAL)
        else:
            print_step(11, "Godot Editor (LSP :6005)", False,
                       f"timeout após {POLL_TIMEOUT_LSP:.0f}s.\n"
                       "         O editor pode ainda estar abrindo.\n"
                       "         Se não abrir, feche e rode init.py novamente.")
            return False

    # ── Verificar Addon Bridge (WebSocket) ──
    if _is_port_open(WS_HOST, WS_PORT):
        print_step(12, "Addon Bridge (WS :9082)", True,
                   "bridge já estava respondendo")
    else:
        print_step(12, "Aguardando Addon Bridge (WS :9082)", True,
                   f"polling até {POLL_TIMEOUT_WS:.0f}s...")
        start = time.time()
        while time.time() - start < POLL_TIMEOUT_WS:
            if _is_port_open(WS_HOST, WS_PORT):
                elapsed = (time.time() - start) * 1000
                print(f"         conectado em {elapsed:.0f}ms")
                break
            time.sleep(POLL_INTERVAL)
        else:
            print_step(12, "Addon Bridge (WS :9082)", False,
                       f"timeout após {POLL_TIMEOUT_WS:.0f}s.\n"
                       "         Possíveis causas:\n"
                       "         1. Plugin MCP não está ativo em:\n"
                       "            Projeto → Configurações do Projeto → Plugins\n"
                       "         2. Outro projeto Godot já está usando a porta 9082.\n"
                       "            Feche o outro editor e rode init.py novamente.")
            return False

    print_step(13, "Conexão MCP ↔ Godot", True,
               "tudo pronto! LSP + Bridge respondendo")
    return True


def step_templates(godot_path: str, skip: bool = False) -> bool:
    """Verifica e instala templates de exportação do Godot.

    Detecta a versão exata do Godot, verifica se os templates estão
    instalados em %APPDATA%/Godot/export_templates/<versão>/ e,
    se ausentes, baixa e extrai do site oficial.

    Args:
        godot_path: Caminho do executável do Godot.
        skip: Se True, pula a verificação (--no-templates).

    Returns:
        True se templates estão OK ou foram instalados, False se falhou.
    """
    if skip:
        print_step(14, "Templates de exportação", True, "pulados (--no-templates)")
        return True

    # ── Obter versão exata ──
    full_version = get_godot_version(godot_path)
    if not full_version:
        print_step(14, "Templates de exportação", False,
                   "Não foi possível detectar a versão do Godot.")
        return False

    # Validação antecipada: confirma que conseguimos parsear a versão
    short_version = get_godot_version_short(godot_path)  # noqa: F841 — validação
    if not short_version:
        print_step(14, "Templates de exportação", False,
                   f"Versão não reconhecida: {full_version}")
        return False

    # ── Pasta de templates ──
    appdata = os.environ.get("APPDATA", "")
    templates_root = Path(appdata) / "Godot" / "export_templates" if appdata else Path.home() / "AppData" / "Roaming" / "Godot" / "export_templates"
    templates_dir = templates_root / full_version

    # Verifica se já existem (pasta com version.txt = instalação completa)
    version_marker = templates_dir / "version.txt"
    if version_marker.exists():
        print_step(14, "Templates de exportação", True,
                   f"já instalados: {templates_dir}")
        return True

    # Se a pasta existe sem version.txt, pode estar corrompida — remove
    if templates_dir.exists():
        shutil.rmtree(templates_dir, ignore_errors=True)

    # ── Download ──
    # URL: https://github.com/godotengine/godot-builds/releases/download/4.7-stable/Godot_v4.7-stable_export_templates.tpz
    tag = get_godot_version_tag(godot_path)
    if not tag:
        print_step(14, "Templates de exportação", False,
                   f"Não foi possível determinar a tag de release: {full_version}")
        return False

    url = f"{TEMPLATE_BASE_URL}/{tag}/Godot_v{tag}_export_templates.tpz"
    print_step(14, "Baixando templates de exportação", True,
               f"versão: {full_version}\n"
               f"         url: {url}\n"
               f"         (~800MB, isso pode levar alguns minutos...)")

    tpz_path = templates_root / f"Godot_v{tag}_export_templates.tpz"
    templates_root.mkdir(parents=True, exist_ok=True)

    try:
        # Download com barra de progresso e timeout
        def _progress(count: int, block_size: int, total_size: int):
            mb_done = count * block_size / (1024 * 1024)
            if total_size > 0:
                pct = min(int(count * block_size * 100 / total_size), 100)
                mb_total = total_size / (1024 * 1024)
                print(f"\r         {pct}% ({mb_done:.0f}/{mb_total:.0f} MB)", end="", flush=True)
            else:
                print(f"\r         {mb_done:.0f} MB...", end="", flush=True)

        urllib.request.urlretrieve(url, str(tpz_path), reporthook=_progress)
        print()  # nova linha após barra de progresso

        # ── Extrair (com proteção anti-path-traversal) ──
        print_step(15, "Extraindo templates", True, f"para {templates_dir}")
        templates_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(tpz_path, "r") as zf:
            for member in zf.infolist():
                # Proteção Zip Slip: rejeita paths que escapam do diretório alvo
                member_path = templates_dir / member.filename
                resolved = member_path.resolve()
                if not str(resolved).startswith(str(templates_dir.resolve())):
                    print_step(15, "Extraindo templates", False,
                               f"Path inseguro no .tpz: {member.filename}")
                    return False
            zf.extractall(str(templates_dir))

        # Limpa o .tpz (não é mais necessário)
        tpz_path.unlink(missing_ok=True)

        # Verifica se extraiu corretamente (version.txt é o marcador oficial)
        if (templates_dir / "version.txt").exists():
            print_step(16, "Templates de exportação", True,
                       f"instalados com sucesso em {templates_dir}")
            return True
        else:
            print_step(16, "Templates de exportação", False,
                       "Extração concluída mas version.txt não encontrado.\n"
                       "         O arquivo .tpz pode estar corrompido.")
            return False

    except urllib.error.URLError as e:
        print_step(15, "Download de templates", False,
                   f"Erro de rede: {e}\n"
                   "         Verifique sua conexão e tente novamente.\n"
                   "         Você pode baixar manualmente em:\n"
                   f"         {url}")
        return False
    except urllib.error.HTTPError as e:
        print_step(15, "Download de templates", False,
                   f"Erro HTTP {e.code}: {e.reason}\n"
                   f"         URL: {url}\n"
                   "         Verifique se a versão do Godot é suportada.")
        return False
    except Exception as e:
        print_step(15, "Download de templates", False,
                   f"Erro: {e}\n"
                   "         Você pode baixar manualmente em:\n"
                   f"         {url}")
        return False


def create_godot_project(project_dir: Path, project_name: str) -> bool:
    """Cria um projeto Godot mínimo se não existir."""
    godot_file = project_dir / "project.godot"
    if godot_file.exists():
        return True  # já existe

    project_dir.mkdir(parents=True, exist_ok=True)

    # Sanitiza project_name: remove aspas que quebrariam o INI
    safe_project_name = project_name.replace('"', "'").replace("\n", " ").replace("\r", "")

    config_engine = f"""; Engine configuration file.
; It's best edited using the editor UI and not directly,
; since the parameters that go here are not all obvious.
;
; Format:
;   [section] ; section goes between []
;   param=value ; assign values to parameters

config_version=5

[application]

config/name="{safe_project_name}"
"""

    godot_file.write_text(config_engine, encoding="utf-8")

    # Cria .gitignore
    gitignore = project_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(
            "# Godot\n.godot/\n*.uid\n*.import\n\n# Python\n__pycache__/\n*.pyc\n.venv/\n\n# MCP\n.mcp_*\n",
            encoding="utf-8",
        )

    # Cria cena principal vazia
    scenes_dir = project_dir / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    main_scene = scenes_dir / "main.tscn"
    main_scene.write_text(
        '[gd_scene load_steps=2 format=3]\n\n'
        '[ext_resource type="Script" path="res://scripts/main.gd" id="1_main"]\n\n'
        '[node name="Main" type="Node"]\n'
        'script = ExtResource("1_main")\n',
        encoding="utf-8",
    )

    # Cria script principal vazio
    scripts_dir = project_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    main_script = scripts_dir / "main.gd"
    main_script.write_text(
        'extends Node\n\n\n'
        'func _ready() -> void:\n'
        '\tprint("Olá! Seu jogo está pronto para começar.")\n',
        encoding="utf-8",
    )

    return False  # projeto novo


def normalize_project_name(name: str) -> str:
    """Normaliza nome de projeto: sem acento, sem espaço, minúsculo, só [a-z0-9_]."""
    import unicodedata

    # NFKD: decompõe acentos
    normalized = unicodedata.normalize("NFKD", name)
    # Remove diacríticos (acentos)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    # Substitui tudo que não for letra/número por _
    safe = re.sub(r"[^a-zA-Z0-9]", "_", ascii_name)
    # Minúsculo
    safe = safe.lower()
    # Remove underscores duplicados
    safe = re.sub(r"_+", "_", safe)
    # Remove underscore inicial/final
    safe = safe.strip("_")
    # Se ficou vazio, usa fallback
    if not safe:
        safe = "meu_jogo"
    return safe


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="MCP Godot Agent — Instalador de 1 comando",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Exemplos:
              python init.py                        # Modo interativo
              python init.py --dir "C:/MeuJogo"     # Pasta específica
              python init.py --name "Meu Jogo"      # Nome do projeto
              python init.py --silent               # Sem perguntas
        """),
    )
    parser.add_argument("--dir", "-d", help="Pasta do projeto Godot")
    parser.add_argument("--name", "-n", help="Nome do jogo (ex: 'Meu Jogo Legal')")
    parser.add_argument("--godot", "-g", help="Caminho do executável do Godot")
    parser.add_argument("--python", "-p", help="Caminho do Python 3.10+")
    parser.add_argument("--silent", "-s", action="store_true", help="Modo silencioso (sem perguntas)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mostrar stack traces em erros")
    parser.add_argument("--no-verify", action="store_true", help="Pular verificação de conexão (bridge polling)")
    parser.add_argument("--no-templates", action="store_true", help="Pular download de templates de exportação")
    args = parser.parse_args()

    if not args.silent:
        print_banner()

    # ══════════════════════════════════════════════════════════════════
    # ETAPA 1: Detectar
    # ══════════════════════════════════════════════════════════════════
    godot_path, python_path = step1_detect(args.godot, args.python)

    # ══════════════════════════════════════════════════════════════════
    # ETAPA 2: Ambiente virtual
    # ══════════════════════════════════════════════════════════════════
    venv_python = step2_venv(ROOT, python_path)

    # ══════════════════════════════════════════════════════════════════
    # ETAPA 3: Pasta do projeto
    # ══════════════════════════════════════════════════════════════════
    if args.dir:
        project_dir = Path(args.dir)
    else:
        # Perguntar ou usar default
        if args.silent:
            project_dir = DEFAULT_PROJECT_PARENT / "meu_jogo"
        else:
            print()
            default_dir = DEFAULT_PROJECT_PARENT / "meu_jogo"
            user_input = input(f"  Pasta do projeto Godot [{default_dir}]: ").strip()
            project_dir = Path(user_input) if user_input else default_dir

    # Normalizar nome
    if args.name:
        project_name = args.name
    else:
        project_name = project_dir.name.replace("_", " ").title()

    safe_name = normalize_project_name(project_name)
    if safe_name != project_dir.name and not args.dir:
        # Se a pasta foi sugerida por default, ajusta para usar o nome normalizado
        project_dir = project_dir.parent / safe_name

    # ── Verificar pasta sincronizada (Fatia 0.I) ──
    if is_cloud_synced(project_dir):
        print()
        print(f"  ⚠️  ATENÇÃO: A pasta '{project_dir}' está em uma nuvem sincronizada")
        print(f"  (OneDrive, Dropbox, etc). Isso pode corromper o cache do Godot.")
        print(f"  Recomendação: use uma pasta fora da nuvem, como C:\\Projetos\\")
        if not args.silent:
            resp = input("  Continuar mesmo assim? [s/N]: ").strip().lower()
            if resp not in ("s", "sim", "y", "yes"):
                print("  Instalação cancelada.")
                sys.exit(0)

    print_step(6, "Pasta do projeto", True, str(project_dir))

    # ══════════════════════════════════════════════════════════════════
    # ETAPA 4: Criar projeto Godot
    # ══════════════════════════════════════════════════════════════════
    existed = create_godot_project(project_dir, project_name)
    if existed:
        print_step(9, "Projeto Godot", True, f"já existia: {project_dir / 'project.godot'}")
    else:
        print_step(9, "Projeto Godot", True, f"criado: {project_dir / 'project.godot'}\n         nome: {project_name}")

    # ══════════════════════════════════════════════════════════════════
    # ETAPA 5: Instalar addon
    # ══════════════════════════════════════════════════════════════════
    step4_install_addon(project_dir)

    # ══════════════════════════════════════════════════════════════════
    # ETAPA 6: Configurar MCP
    # ══════════════════════════════════════════════════════════════════
    step3_mcp_config(project_dir, venv_python)

    # ══════════════════════════════════════════════════════════════════
    # ETAPA 7: Templates de exportação
    # ══════════════════════════════════════════════════════════════════
    step_templates(godot_path, skip=args.no_templates)

    # ══════════════════════════════════════════════════════════════════
    # ETAPA 8: Abrir Godot
    # ══════════════════════════════════════════════════════════════════
    # Verificar se já tem Godot rodando
    godot_ja_aberto = _is_port_open(LSP_HOST, LSP_PORT, timeout=0.5)

    if godot_ja_aberto:
        print_step(10, "Godot Editor", True,
                   "editor já está aberto (LSP :6005 respondendo)\n"
                   "         O projeto será aberto no editor existente.")
        try:
            subprocess.Popen(
                [godot_path, "--path", str(project_dir), "--editor"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass  # já estava aberto, pode falhar silenciosamente
    else:
        try:
            subprocess.Popen(
                [godot_path, "--path", str(project_dir), "--editor"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print_step(10, "Abrir Godot Editor", True, "editor iniciado em segundo plano")
        except Exception as e:
            print_step(10, "Abrir Godot Editor", False,
                       f"Não foi possível abrir o editor.\n"
                       f"         Abra manualmente: {godot_path} --path \"{project_dir}\" --editor")

    # ══════════════════════════════════════════════════════════════════
    # ETAPA 8: Verificar conectividade (bridge polling)
    # ══════════════════════════════════════════════════════════════════
    if not args.no_verify:
        step5_verify_connection()  # resultado informativo, efeito colateral via print
    else:
        print_step(11, "Verificação de conexão", True, "pulada (--no-verify)")

    # ══════════════════════════════════════════════════════════════════
    # Pronto!
    # ══════════════════════════════════════════════════════════════════
    print_final_box(project_dir)

    if not args.silent:
        try:
            input("Pressione Enter para sair...")
        except (EOFError, OSError):
            pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Instalação cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n  [FALHA] Erro inesperado: {e}")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            import traceback
            traceback.print_exc()
        print("  Se o erro persistir, rode: python init.py --verbose")
        sys.exit(1)
