"""bootstrap_ops.py — Auto-Bootstrap VS Code ↔ MCP ↔ Godot (Fase 2C).

Ferramenta de bootstrap 100% automático que elimina os 12 passos manuais
de conexão. A IA agêntica chama UMA tool e recebe tudo pronto.

Fluxo interno:
    1. validate_mcp_environment()
    2. validate_godot_version()
    3. setup_mcp_config() → gera mcp.json
    4. install_mcp_addon() → addon no projeto
    5. detectar/abrir Godot → runtime_manage launch_editor
    6. polling LSP :6005 → aguardar Godot abrir
    7. gdscript_lsp_connect()
    8. polling WS :9082 → aguardar addon iniciar
    9. addon_connect()
    10. health_check()
"""

import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# ── Constantes ──────────────────────────────────────────────────────

LSP_HOST = "127.0.0.1"
LSP_PORT = 6005
WS_HOST = "127.0.0.1"
WS_PORT = 9082
POLL_INTERVAL = 0.5  # segundos entre tentativas


# ── Helpers de Polling ──────────────────────────────────────────────

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


def _poll_port(host: str, port: int, timeout: float, label: str) -> dict:
    """Aguarda uma porta ficar disponível com polling.

    Args:
        host: Host (ex: "127.0.0.1").
        port: Porta (ex: 6005).
        timeout: Tempo máximo em segundos.
        label: Nome amigável para logs.

    Returns:
        dict com status e duração.
    """
    start = time.time()
    while time.time() - start < timeout:
        if _is_port_open(host, port, timeout=1.0):
            elapsed = (time.time() - start) * 1000
            return {
                "status": "ok",
                "port": port,
                "label": label,
                "duration_ms": round(elapsed),
                "attempts": int((time.time() - start) / POLL_INTERVAL) + 1,
            }
        time.sleep(POLL_INTERVAL)

    elapsed = (time.time() - start) * 1000
    return {
        "status": "timeout",
        "port": port,
        "label": label,
        "duration_ms": round(elapsed),
        "error": f"Porta {host}:{port} não respondeu em {timeout}s",
    }


def _is_godot_editor_open() -> bool:
    """Detecta se o Godot Editor já está aberto (verifica porta LSP)."""
    return _is_port_open(LSP_HOST, LSP_PORT)


def _is_addon_available() -> bool:
    """Detecta se o addon WebSocket já está respondendo."""
    return _is_port_open(WS_HOST, WS_PORT)


# ── Passos do Bootstrap ─────────────────────────────────────────────

def _step_validate_env() -> dict:
    """Passo 1: Validar ambiente MCP."""
    from tools.vscode_config import validate_environment
    return validate_environment()


def _step_check_godot() -> dict:
    """Passo 2: Verificar versão do Godot."""
    from tools.project_ops import validate_godot_version
    try:
        result = validate_godot_version()
        return {"status": "ok", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _step_detect_project(project_path: str | None) -> dict:
    """Detecta ou define o projeto Godot ativo."""
    from tools.project_ops import set_active_project, get_project_settings

    if project_path:
        try:
            set_active_project(project_path)
            return {"status": "ok", "project": project_path, "source": "provided"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # Auto-detectar: procurar project.godot nos subprojetos
    nucleo = ROOT.parent.parent.parent  # servidor → mcp-godot → sistema → NUCLEO
    projetos_dir = nucleo / "projetos"
    if projetos_dir.is_dir():
        for child in projetos_dir.iterdir():
            if child.is_dir() and (child / "project.godot").exists():
                try:
                    set_active_project(str(child))
                    return {"status": "ok", "project": str(child), "source": "auto-detect"}
                except Exception as e:
                    return {"status": "error", "error": str(e)}

    return {"status": "skipped", "reason": "Nenhum projeto Godot encontrado para auto-detectar"}


def _step_setup_config() -> dict:
    """Passo 3: Gerar mcp.json para VS Code."""
    from tools.vscode_config import auto_config
    try:
        result = auto_config("vscode")
        return {"status": "ok", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _step_install_addon(project_path: str | None) -> dict:
    """Passo 4: Instalar addon MCP no projeto Godot."""
    from tools.project_ops import install_mcp_addon
    try:
        result = install_mcp_addon(project_path)
        return {"status": "ok", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _step_launch_editor(args: dict) -> dict:
    """Passo 5: Abrir Godot Editor (se não estiver aberto)."""
    if not args.get("launch_editor", True):
        return {"status": "skipped", "reason": "launch_editor=false"}

    if _is_godot_editor_open():
        return {"status": "skipped", "reason": "Godot Editor já está aberto (LSP :6005 responde)"}

    try:
        # Tenta via runtime_manage (precisa do handler do rollup)
        from tools.runtime_ops import launch_editor as _launch
        _launch(args.get("project_path"))
        return {"status": "ok", "action": "launched"}
    except Exception as e:
        return {"status": "error", "error": str(e), "hint": "Abra o Godot Editor manualmente"}


def _step_wait_lsp(args: dict) -> dict:
    """Passo 6: Aguardar LSP do Godot ficar disponível."""
    timeout = args.get("timeout_godot", 30)
    return _poll_port(LSP_HOST, LSP_PORT, timeout, "Godot LSP")


def _step_connect_lsp(args: dict) -> dict:
    """Passo 7: Conectar ao LSP do Godot."""
    from tools.lsp_ops import LspClient
    try:
        client = LspClient()
        result = client.connect(args.get("project_path"))
        return {"status": "ok", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _step_wait_addon(args: dict) -> dict:
    """Passo 8: Aguardar WebSocket do addon ficar disponível."""
    timeout = args.get("timeout_addon", 15)
    return _poll_port(WS_HOST, WS_PORT, timeout, "Addon WebSocket")


def _step_connect_addon(args: dict) -> dict:
    """Passo 9: Conectar ao addon GDScript."""
    from tools.addon_bridge import AddonBridge
    try:
        bridge = AddonBridge()
        result = bridge.connect()
        return {"status": "ok", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _step_health_check(args: dict) -> dict:
    """Passo 10: Health check final."""
    try:
        from server import _tool_defs
        tool_count = len(_tool_defs())
        return {
            "status": "ok",
            "tool_count": tool_count,
            "lsp": _is_port_open(LSP_HOST, LSP_PORT),
            "addon": _is_port_open(WS_HOST, WS_PORT),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ── Bootstrap Principal ─────────────────────────────────────────────

def bootstrap_godot_mcp(
    target: str = "full",
    project_path: str | None = None,
    godot_path: str | None = None,
    launch_editor: bool = True,
    timeout_godot: int = 30,
    timeout_addon: int = 15,
) -> dict:
    """Executa bootstrap completo: VS Code ↔ MCP ↔ Godot.

    Esta é a ÚNICA tool que a IA agêntica precisa chamar para conectar
    todo o ecossistema. Substitui 12+ chamadas manuais.

    Args:
        target: "full" (tudo), "connect_only" (só conexão), "validate_only" (só validação).
        project_path: Caminho do projeto Godot. Auto-detecta se None.
        godot_path: Caminho do executável Godot. Auto-detecta do config.json se None.
        launch_editor: Se True, abre o Godot Editor se não estiver aberto.
        timeout_godot: Segundos máximos esperando o Godot abrir (default 30).
        timeout_addon: Segundos máximos esperando o addon iniciar (default 15).

    Returns:
        dict com status geral, passos executados, e estado das conexões.
    """
    args = {
        "project_path": project_path,
        "godot_path": godot_path,
        "launch_editor": launch_editor,
        "timeout_godot": timeout_godot,
        "timeout_addon": timeout_addon,
    }

    steps = []
    overall_start = time.time()
    has_errors = False

    def _run(step_name: str, fn, *fn_args):
        nonlocal has_errors
        t0 = time.time()
        try:
            result = fn(*fn_args)
        except Exception as e:
            result = {"status": "error", "error": str(e)}
        elapsed = round((time.time() - t0) * 1000)
        step = {"step": step_name, "duration_ms": elapsed, **result}
        if result.get("status") == "error":
            has_errors = True
        steps.append(step)
        return result

    # ── Fase 1: Validação ──
    if target in ("full", "validate_only"):
        _run("validate_env", _step_validate_env)
        _run("check_godot", _step_check_godot)
        _run("detect_project", _step_detect_project, project_path)

    if target == "validate_only":
        total_ms = round((time.time() - overall_start) * 1000)
        return {
            "status": "error" if has_errors else "success",
            "target": target,
            "steps": steps,
            "total_duration_ms": total_ms,
        }

    # ── Fase 2: Configuração ──
    if target in ("full",):
        _run("setup_config", _step_setup_config)
        _run("install_addon", _step_install_addon, project_path)

    # ── Fase 3: Conexão ──
    if target in ("full", "connect_only"):
        _run("launch_editor", _step_launch_editor, args)

        lsp_wait = _run("wait_lsp", _step_wait_lsp, args)
        if lsp_wait.get("status") == "ok":
            _run("connect_lsp", _step_connect_lsp, args)
        else:
            steps.append({
                "step": "connect_lsp",
                "status": "skipped",
                "reason": "LSP não disponível — Godot não abriu?",
                "duration_ms": 0,
            })

        addon_wait = _run("wait_addon", _step_wait_addon, args)
        if addon_wait.get("status") == "ok":
            _run("connect_addon", _step_connect_addon, args)
        else:
            steps.append({
                "step": "connect_addon",
                "status": "skipped",
                "reason": "Addon não disponível — está instalado?",
                "duration_ms": 0,
            })

    # ── Fase 4: Verificação ──
    _run("health_check", _step_health_check, args)

    total_ms = round((time.time() - overall_start) * 1000)

    # Estado das conexões
    connections = {
        "mcp": "running",
        "lsp": "connected" if _is_port_open(LSP_HOST, LSP_PORT) else "disconnected",
        "addon": "connected" if _is_port_open(WS_HOST, WS_PORT) else "disconnected",
    }

    return {
        "status": "error" if has_errors else "success",
        "target": target,
        "steps": steps,
        "connections": connections,
        "total_duration_ms": total_ms,
    }


# ── Atalho para IA Agêntica ─────────────────────────────────────────

def auto_bootstrap() -> dict:
    """Atalho zero-config: bootstrap completo com auto-detecção.

    A IA chama esta função sem nenhum argumento. Equivalente a:
        bootstrap_godot_mcp(target="full")
    """
    return bootstrap_godot_mcp(target="full")


# ── Godot Keep-Alive ─────────────────────────────────────────────────

def godot_keep_alive(project_path: str | None = None, 
                     godot_path: str | None = None) -> dict:
    """Garante que o Godot Editor está aberto. Se não estiver, abre.

    Esta tool DEVE ser chamada pela IA no início de toda sessão e sempre
    que suspeitar que o Godot foi fechado. NÃO fecha o Godot em hipótese
    alguma — só abre se não estiver rodando.

    Args:
        project_path: Caminho do projeto (usa config.json se None).
        godot_path: Caminho do executável Godot (usa config.json se None).

    Returns:
        {"status": "success", "godot": "running"|"started", "pid": int}
    """
    import subprocess
    from pathlib import Path

    # Verificar se já está rodando
    try:
        result = subprocess.run(
            ['tasklist', '/fi', 'imagename eq Godot_v4.7-stable_win64.exe'],
            capture_output=True, text=True, timeout=5
        )
        if 'Godot_v4.7-stable_win64.exe' in result.stdout:
            # Já está rodando
            return {
                "status": "success",
                "godot": "running",
                "message": "Godot Editor ja esta aberto. Nao feche.",
            }
    except Exception:
        pass

    # Resolver paths
    if not project_path:
        try:
            from tools.config_loader import load_config
            cfg = load_config()
            project_path = cfg.get("default_project")
        except Exception:
            pass

    if not godot_path:
        try:
            from tools.config_loader import load_config
            cfg = load_config()
            godot_path = cfg.get("godot_path", r"C:\Godot\Godot_v4.7-stable_win64.exe")
        except Exception:
            godot_path = r"C:\Godot\Godot_v4.7-stable_win64.exe"

    if not project_path:
        return {"status": "error", "message": "project_path nao definido"}

    # Abrir Godot
    try:
        subprocess.Popen(
            [godot_path, "--path", project_path, "--editor"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        import time
        time.sleep(3)

        return {
            "status": "success",
            "godot": "started",
            "message": "Godot Editor iniciado. MANTENHA ABERTO.",
            "project": project_path,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
