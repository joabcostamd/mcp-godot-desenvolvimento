"""runtime_ops — Execução do jogo (subprocess) e bridge do editor.

Fase 2: run_game, stop_game, compile_test.
Fase 3: launch_editor, close_editor, take_screenshot, read_console_output.
"""

import json
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path

from tools.classdb import get_godot_bin, get_config
from tools.project_ops import _get_active_project, _check_path_traversal
from tools.gdscript_sandbox import validate_gdscript_code
from tools.subprocess_utils import run_subprocess_safe

# ── Estado interno ──────────────────────────────────────────────────

_game_process: subprocess.Popen | None = None
_console_buffer: list[str] = []
_buffer_lock = threading.Lock()

# ── Compilação pendente (Onda 2) ────────────────────────────────────

_pending_compile: bool = False

# ── Não-intrusão (Fatia 1.6) ──────────────────────────────────────
# Default: modo silencioso. Todas as tools têm intrusiveHint=False.
# Subprocessos usam SW_HIDE por padrão. Só run_game pode ser intrusivo.

def _get_startup_info(silent: bool = True):
    """Retorna STARTUPINFO com SW_HIDE (silencioso) ou SW_MINIMIZE (visível).

    Fatia 1.6: modo silencioso é o default — consistente com
    intrusiveHint=False em todas as 45 tools.
    """
    if os.name != "nt":
        return None
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0 if silent else 6  # SW_HIDE : SW_MINIMIZE
    return startup


def mark_pending_compile() -> None:
    """Marca que o projeto precisa de compilação (UID, import, etc).

    Chamado por create_scene, import_texture e outras operações que
    modificam arquivos. A compilação real só ocorre quando compile_test
    ou run_game são chamados explicitamente.
    """
    global _pending_compile
    _pending_compile = True


def needs_compile() -> bool:
    """Verifica se há compilação pendente."""
    return _pending_compile


def _run_pending_compile(proj: Path, godot: str, timeout: int) -> dict | None:
    """Executa compilação pendente se necessário. Retorna erros ou None."""
    global _pending_compile
    if not _pending_compile:
        return None
    _pending_compile = False
    return _do_compile(proj, godot, timeout)


def _enqueue_output(stream, label: str) -> None:
    """Thread que lê output linha a linha e acumula no buffer."""
    for line in iter(stream.readline, ""):
        with _buffer_lock:
            _console_buffer.append(f"[{label}] {line.rstrip()}")
    stream.close()


# ── API Pública ─────────────────────────────────────────────────────

def compile_test() -> dict:
    """Executa compile_test no projeto ativo (--headless --editor --quit).

    Se houver operações pendentes (create_scene, import_texture),
    executa a compilação. Caso contrário, apenas verifica.

    Returns:
        {"status": "success", "errors": []}
        ou {"status": "error", "message": str}
    """
    proj = _get_active_project()
    godot = get_godot_bin()
    cfg = get_config()
    timeout = cfg.get("timeouts", {}).get("compile", 30)  # reduzido de 60s para 30s

    if not (proj / "project.godot").exists():
        return {"status": "error", "message": f"Projeto '{proj}' não contém project.godot."}

    # Executa compilação pendente se necessário
    pending_result = _run_pending_compile(proj, godot, timeout)
    if pending_result:
        return pending_result

    # Se não havia pendência, executa verificação rápida
    return _do_compile(proj, godot, timeout)


def _do_compile(proj: Path, godot: str, timeout: int) -> dict:
    """Executa a compilação real do Godot."""
    # B4 FIX: Remove --editor (desnecessario, carrega plugins/addons = 12x mais lento)
    # Apenas --headless --quit basta para verificar compilacao
    try:
        result = subprocess.run(
            [godot, "--headless", "--quit", "--path", str(proj)],
            capture_output=True, text=True, timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
        errors = []
        for line in (result.stdout + "\n" + result.stderr).splitlines():
            if any(kw in line for kw in ("ERROR", "SCRIPT ERROR", "Parse Error", "error:")):
                errors.append(line.strip())
        return {"status": "success", "errors": errors}
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": f"Timeout ao rodar compile_test ({timeout}s configurado em timeouts.compile)."}
    except Exception as e:
        return {"status": "error", "message": f"Erro: {e}"}


def compile_test_incremental(file_path: str) -> dict:
    """Compila APENAS um arquivo GDScript, sem compilar o projeto inteiro.

    Muito mais rápido que compile_test (2-5s vs 60s). Usa --headless -s
    com um script que faz load() e check de erro no recurso alvo.

    Use para feedback rápido após modificar um script — Canvas-like.

    Args:
        file_path: Caminho relativo do arquivo .gd no projeto.

    Returns:
        {"status": "success", "errors": [str]}
        ou {"status": "error", "message": str}
    """
    proj = _get_active_project()
    godot = get_godot_bin()
    cfg = get_config()
    timeout = cfg.get("timeouts", {}).get("fast", 15)

    if not (proj / "project.godot").exists():
        return {"status": "error", "message": f"Projeto '{proj}' não contém project.godot."}

    # Normaliza path
    target = file_path.replace("\\", "/")
    if not target.startswith("res://"):
        target = "res://" + target.lstrip("/")

    # Script GDScript que carrega e verifica o recurso
    check_script = f'''extends SceneTree

func _init() -> void:
    var res := load("{target}")
    if res == null:
        printerr("ERRO: nao foi possivel carregar {target}")
        quit(1)
        return

    if res is GDScript:
        var err := res.reload()
        if err != OK:
            printerr("ERRO: falha ao compilar {target} (codigo " + str(err) + ")")
            quit(1)
            return

    print("OK: {target} compilado sem erros.")
    quit()
'''

    script_file = proj / "_mcp_incr_compile.gd"
    script_file.write_text(check_script, encoding="utf-8")

    try:
        result = subprocess.run(
            [godot, "--headless", "-s", "_mcp_incr_compile.gd", "--path", str(proj)],
            capture_output=True, text=True, timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        script_file.unlink(missing_ok=True)
        return {"status": "error", "message": f"Timeout ({timeout}s) ao compilar {file_path}."}
    except Exception as e:
        script_file.unlink(missing_ok=True)
        return {"status": "error", "message": f"Erro: {e}"}
    finally:
        script_file.unlink(missing_ok=True)

    errors = []
    for line in (result.stdout or "").splitlines() + (result.stderr or "").splitlines():
        line = line.strip()
        if not line:
            continue
        if "ERRO:" in line or "ERROR" in line or "Parse Error" in line:
            errors.append(line)
        elif "SCRIPT ERROR" in line:
            errors.append(line)

    if result.returncode != 0 and not errors:
        errors.append(f"Godot exit code {result.returncode} ao compilar {file_path}.")

    return {"status": "success", "errors": errors, "file": file_path}


def run_game(scene_path: str | None = None, wait_for_bridge: bool = True) -> dict:
    """Inicia o jogo como subprocesso (não bloqueante).

    OPT2: Aguarda o game bridge ficar pronto automaticamente.
    Com wait_for_bridge=True, a funcao so retorna quando o bridge
    estiver aceitando conexoes (ou timeout de 15s).

    Args:
        scene_path: Cena opcional para rodar. Se None, usa main_scene do projeto.
        wait_for_bridge: Se True, aguarda o game bridge iniciar (default True).

    Returns:
        {"status": "success", "pid": int, "bridge_ready": bool, "note": str}
    """
    global _game_process, _console_buffer

    # Encerra jogo anterior se existir
    if _game_process is not None:
        stop_game()
        time.sleep(0.5)  # Pequena pausa para porta liberar

    proj = _get_active_project()
    godot = get_godot_bin()

    # ── Validação de segurança ──────────────────────────────────
    if scene_path:
        violation = _check_path_traversal(scene_path, proj)
        if violation:
            return violation

    if not (proj / "project.godot").exists():
        return {"status": "error", "message": f"Projeto '{proj}' não encontrado."}

    # ── Auto-compile se pendente ─────────────────────────────────
    if _pending_compile:
        godot = get_godot_bin()
        cfg = get_config()
        timeout = cfg.get("timeouts", {}).get("compile", 60)
        compile_result = _run_pending_compile(proj, godot, timeout)
        if compile_result and compile_result.get("errors"):
            return {
                "status": "error",
                "message": "Erros de compilação antes de rodar o jogo.",
                "compile_errors": compile_result.get("errors", []),
            }

    # Se scene_path não informado, verifica main_scene
    if not scene_path:
        from tools.project_ops import get_project_settings
        settings = get_project_settings("application")
        app = settings.get("settings", {}).get("application", {})
        # Godot salva como run/main_scene (sem prefixo config/)
        main = app.get("run/main_scene", "") or app.get("config/run/main_scene", "")
        if main:
            scene_path = main.strip('"')
        else:
            return {
                "status": "error",
                "message": "Nenhuma cena especificada e main_scene não definida. "
                           "Use set_main_scene ou informe scene_path.",
            }

    cmd = [godot, "--path", str(proj)]
    if scene_path:
        cmd.append(str(scene_path))

    try:
        # ── Modo invisível: não rouba foco, não atrapalha o usuário ──
        startup = _get_startup_info(silent=True)

        _game_process = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            startupinfo=startup,
        )

        with _buffer_lock:
            _console_buffer.clear()
        _console_buffer.append("[GameBridge] Jogo iniciado. Use stop_game() para encerrar.")

        result = {
            "status": "success",
            "pid": _game_process.pid,
            "bridge_ready": False,
            "note": "Jogo rodando.",
        }

        # OPT2: Aguarda o game bridge estar pronto
        if wait_for_bridge:
            bridge_ready = False
            for attempt in range(10):
                time.sleep(0.8)
                try:
                    from tools.game_bridge import connect as gb_connect, disconnect as gb_disconnect
                    r = gb_connect(port=cfg.get("game_port", 9081), retries=1)
                    if r.get("status") == "success":
                        bridge_ready = True
                        gb_disconnect()
                        break
                except Exception:
                    pass
            result["bridge_ready"] = bridge_ready
            if bridge_ready:
                result["note"] = "Jogo rodando + Game Bridge conectado."
            else:
                result["note"] = "Jogo rodando (Game Bridge ainda nao respondeu — aguarde mais 2-3s)."

        return result
    except Exception as e:
        return {"status": "error", "message": f"Erro ao iniciar jogo: {e}"}


def test_game(scene: str = "scenes/main.tscn") -> dict:
    """Atalho de teste: pula menu, vai direto pra cena do jogo.

    Diferente de run_game(), este:
    1. Salva a main_scene atual do projeto
    2. Define temporariamente a cena de jogo como principal
    3. Inicia o jogo e aguarda o Game Bridge
    4. NAO restaura a main_scene automaticamente (use restore_main_scene)

    Isso permite testar rapidamente sem passar pelo menu.

    Args:
        scene: Cena a testar (default: scenes/main.tscn).

    Returns:
        {"status": "success", "pid": int, "bridge_ready": bool, "original_main": str}
    """
    from tools.project_ops import get_project_settings, set_main_scene

    # Salva main_scene original
    settings = get_project_settings("application")
    app = settings.get("settings", {}).get("application", {})
    original = app.get("run/main_scene", "") or app.get("config/run/main_scene", "")

    # Define cena de teste como principal
    set_main_scene(scene)

    # Inicia com bridge
    result = run_game(wait_for_bridge=True)
    result["original_main"] = original
    result["test_scene"] = scene
    return result


def restore_main_scene(scene: str | None = None) -> dict:
    """Restaura a main_scene original (ou uma especifica) apos test_game()."""
    from tools.project_ops import set_main_scene
    target = scene or "scenes/main_menu.tscn"
    return set_main_scene(target)


def smart_restart(project_path: str | None = None) -> dict:
    """OPT4: Reinicio inteligente — kill, copia arquivos, compila, inicia, conecta.

    Um unico comando que faz tudo necessario para reiniciar o jogo com
    as ultimas alteracoes. Elimina o ciclo manual de 4-5 chamadas.

    Fluxo: stop_game() -> copia addon -> compile_test -> run_game -> connect bridge

    Returns:
        {"status": "success", "pid": int, "bridge_ready": bool, "compile_errors": [...], "time": float}
    """
    import time as _time
    t0 = _time.time()

    # 1. Para jogo anterior
    stop_result = stop_game()
    _time.sleep(0.3)

    # 2. Copia addon mcp_runtime_bridge (garante versao mais recente)
    proj = _get_active_project() if not project_path else Path(project_path)
    try:
        addon_src = Path(__file__).resolve().parent.parent / "addons" / "mcp_runtime_bridge" / "runtime_bridge.gd"
        addon_dst = proj / "addons" / "mcp_runtime_bridge" / "runtime_bridge.gd"
        if addon_src.exists():
            addon_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(addon_src), str(addon_dst))
    except Exception:
        pass  # Best-effort

    # 3. Compila
    godot = get_godot_bin()
    cfg = get_config()
    timeout = cfg.get("timeouts", {}).get("compile", 60)
    compile_result = _do_compile(proj, godot, timeout)

    # 4. Inicia jogo (sem esperar bridge aqui — run_game ja faz)
    run_result = run_game(wait_for_bridge=True)

    elapsed = round(_time.time() - t0, 1)

    return {
        "status": "success" if run_result.get("status") == "success" else "error",
        "pid": run_result.get("pid"),
        "bridge_ready": run_result.get("bridge_ready", False),
        "compile_errors": compile_result.get("errors", []),
        "time": elapsed,
        "note": f"Reinicio completo em {elapsed}s.",
    }


def stop_game() -> dict:
    """Encerra o jogo em execucao e retorna as ultimas 100 linhas do console.

    Returns:
        {"status": "success", "console_tail": [str]}
    """
    global _game_process, _console_buffer

    if _game_process is None:
        return {"status": "success", "note": "Nenhum jogo em execucao."}

    try:
        # B17 FIX: No Windows, terminate() envia SIGTERM que Godot ignora.
        # Usamos taskkill /F para encerramento garantido.
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/PID", str(_game_process.pid)],
                         capture_output=True, timeout=5)
        else:
            _game_process.terminate()
        _game_process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        _game_process.kill()
        _game_process.wait()
    except Exception:
        pass

    _game_process = None

    with _buffer_lock:
        tail = _console_buffer[-100:]

    return {"status": "success", "console_tail": tail}


# ── Fase 3: Editor ao vivo ─────────────────────────────────────────

_editor_process: subprocess.Popen | None = None
_editor_open: bool = False


def _ensure_addon_installed(proj: Path) -> None:
    """Garante que o addon mcp_addon está copiado e habilitado no projeto."""
    addon_src = Path(__file__).resolve().parent.parent / "addons" / "mcp_addon"
    addon_dst = proj / "addons" / "mcp_addon"

    if not addon_dst.exists():
        addon_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(str(addon_src), str(addon_dst))

    godot_file = proj / "project.godot"
    if godot_file.exists():
        content = godot_file.read_text(encoding="utf-8")
        if "[editor_plugins]" not in content:
            godot_file.write_text(content + '\n[editor_plugins]\nenabled=PackedStringArray("res://addons/mcp_addon/plugin.cfg")\n')
        elif "mcp_addon" not in content:
            lines = content.splitlines(keepends=True)
            for i, line in enumerate(lines):
                if line.strip().startswith("enabled="):
                    lines[i] = line.rstrip()[:-1] + ', "res://addons/mcp_addon/plugin.cfg")\n'
                    break
            godot_file.write_text("".join(lines))


def ensure_godot_windows() -> dict:
    """Garante que as 2 janelas Godot estejam abertas (Editor + Jogo).

    Verifica se já existem instâncias rodando antes de abrir novas.
    Regra: durante produção, manter ambas abertas. Não fechar a cada iteração.

    Returns:
        {"status": "success", "editor_pid": int|None, "game_pid": int|None,
         "editor_was_open": bool, "game_was_open": bool}
    """
    global _game_process, _editor_process, _editor_open

    result = {"status": "success", "editor_pid": None, "game_pid": None,
              "editor_was_open": False, "game_was_open": False}

    # B7 FIX: Verifica portas 9080/9081 em vez de contar processos Godot
    # (evita confundir Godot de outros projetos ou headless consoles)
    editor_running = False
    game_running = _game_process is not None and _game_process.poll() is None
    try:
        import socket
        for port, label in [(9080, "editor"), (9081, "game")]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            try:
                sock.connect(("127.0.0.1", port))
                if label == "editor":
                    editor_running = True
                    result["editor_was_open"] = True
                elif not game_running:
                    game_running = True
                    result["game_was_open"] = True
                sock.close()
            except (ConnectionRefusedError, socket.timeout, OSError):
                sock.close()
    except Exception:
        pass

    if not editor_running and not _editor_open:
        r = launch_editor()
        if r["status"] == "success":
            result["editor_pid"] = r.get("pid")
    else:
        result["editor_was_open"] = True

    # ── Verificar Jogo ────────────────────────────────────────
    game_running = _game_process is not None and _game_process.poll() is None
    if not game_running:
        r = run_game()
        if r["status"] == "success":
            result["game_pid"] = r.get("pid")
    else:
        result["game_was_open"] = True
        result["game_pid"] = _game_process.pid

    return result


def launch_editor(scene_path: str | None = None) -> dict:
    """Abre o editor Godot com o addon mcp_addon instalado."""
    global _editor_process, _editor_open
    proj = _get_active_project()
    godot = get_godot_bin()

    # ── Validação de segurança ──────────────────────────────────
    if scene_path:
        violation = _check_path_traversal(scene_path, proj)
        if violation:
            return violation

    if not (proj / "project.godot").exists():
        return {"status": "error", "message": "Projeto não encontrado."}

    _ensure_addon_installed(proj)

    if _editor_process is not None:
        close_editor()

    cmd = [godot, "--editor", "--path", str(proj)]
    if scene_path:
        cmd.append(str(scene_path))

    try:
        _editor_process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
        _editor_open = True

        addon_ok = False
        for _ in range(10):
            time.sleep(0.5)
            from tools.editor_bridge import connect as br_connect, is_connected as br_connected
            if br_connected() or br_connect().get("status") == "success":
                addon_ok = True
                break

        return {
            "status": "success", "pid": _editor_process.pid,
            "addon_connected": addon_ok,
        }
    except Exception as e:
        _editor_open = False
        return {"status": "error", "message": f"Erro ao abrir editor: {e}"}


def close_editor() -> dict:
    """Fecha o editor Godot."""
    global _editor_process, _editor_open
    from tools.editor_bridge import disconnect as br_disconnect
    br_disconnect()

    if _editor_process is not None:
        try:
            _editor_process.terminate()
            _editor_process.wait(timeout=10)
        except Exception:
            pass
        _editor_process = None
    _editor_open = False
    return {"status": "success"}


def take_screenshot() -> dict:
    """Captura screenshot via addon TCP."""
    if not _editor_open:
        return {"status": "error", "message": "Editor não está aberto."}
    from tools.editor_bridge import take_screenshot as br_ss, connect as br_connect
    br_connect()
    return br_ss()


def read_console_output(since_timestamp: float | None = None) -> dict:
    """Lê console do editor via addon TCP."""
    if not _editor_open:
        with _buffer_lock:
            return {"status": "success", "lines": _console_buffer[-100:], "note": "Offline — console do subprocess."}
    from tools.editor_bridge import read_console_since as br_console
    return br_console(since_timestamp)


def is_editor_open() -> bool:
    """Verifica se o editor está aberto."""
    return _editor_open


# ── Debounce re-import (Fatia 1.7) ────────────────────────────────
_debounce_timer: threading.Timer | None = None
_DEBOUNCE_MS = 0.5  # 500ms


def notify_file_change(file_path: str) -> None:
    """Notifica editor sobre mudanca com debounce de 500ms.

    Acumula chamadas e so dispara rescan_filesystem apos 500ms
    de inatividade — evita re-imports excessivos em edicoes em lote.
    """
    global _debounce_timer
    if not _editor_open:
        return

    # Cancela timer anterior e reinicia
    if _debounce_timer is not None:
        _debounce_timer.cancel()
    _debounce_timer = threading.Timer(_DEBOUNCE_MS, _do_rescan)
    _debounce_timer.daemon = True
    _debounce_timer.start()


def _do_rescan() -> None:
    """Executa o rescan_filesystem (chamado pelo timer de debounce)."""
    try:
        from tools.editor_bridge import rescan_filesystem
        rescan_filesystem()
    except Exception:
        pass


# ── Fase 6: Game Bridge (runtime) ────────────────────────────────────

def _ensure_game_bridge_connected() -> dict:
    """Garante conexão com o game bridge (autoload no jogo em execução)."""
    from tools.game_bridge import connect as gb_connect, is_connected as gb_connected
    if gb_connected():
        return {"status": "success"}
    return gb_connect()


def inject_input_event(event_type: str, event_data: dict) -> dict:
    """Injeta um evento de input no jogo em execução via game bridge.

    Args:
        event_type: "key", "mouse_button", ou "mouse_motion".
        event_data: Dados do evento:
            key: {"keycode": int, "pressed": bool}
            mouse_button: {"button_index": int, "pressed": bool, "x": int, "y": int}
            mouse_motion: {"x": int, "y": int}

    Returns:
        {"status": "success", "injected": str}
    """
    conn = _ensure_game_bridge_connected()
    if conn["status"] != "success":
        return conn

    from tools.game_bridge import inject_input as gb_inject
    return gb_inject(event_type, event_data)


def execute_gdscript_runtime(code: str) -> dict:
    """Executa código GDScript arbitrário no jogo em execução.

    Aceita tanto expressões (ex: "2 + 2") quanto statements (ex:
    "get_node('/root/Main').position.x = 100"). A detecção é por
    compilação: tenta como expressão primeiro; se falhar, compila
    como corpo de _execute(). GDScript.new() em memória, sem arquivo.

    Guard-rail: timeout curto (fast do config). Só funciona com jogo
    rodando (run_game), não com editor.

    ⚠️ SANDBOX: Código validado antes do envio. Classes como OS,
    FileAccess, DirAccess são BLOQUEADAS.

    Args:
        code: Código GDScript a executar.

    Returns:
        {"status": "success", "type": "expression"|"statement", "value": str}
    """
    # ── Validação de segurança (sandbox) ────────────────────────────
    sandbox_result = validate_gdscript_code(code, mode="runtime")
    if not sandbox_result.get("safe", False):
        return sandbox_result

    conn = _ensure_game_bridge_connected()
    if conn["status"] != "success":
        return conn

    from tools.game_bridge import execute_gdscript as gb_exec
    return gb_exec(code)


def watch_signal(node_path: str, signal_name: str, timeout_sec: float = 5.0) -> dict:
    """Observa um sinal por N segundos no jogo em execução.

    Verifica imediatamente se o nó e sinal existem (erro instantâneo se não).
    A espera é não-bloqueante no lado GDScript (callback one-shot + timer).
    Timeout do TCP = timeout_sec + 5s.

    Args:
        node_path: Path do nó (ex: "/root/Main/Player").
        signal_name: Nome do sinal (ex: "health_changed").
        timeout_sec: Tempo máximo de espera em segundos (default 5).

    Returns:
        {"status": "success", "fired": bool, "signal": str}
    """
    conn = _ensure_game_bridge_connected()
    if conn["status"] != "success":
        return conn

    from tools.game_bridge import watch_signal as gb_watch
    return gb_watch(node_path, signal_name, timeout_sec)


# ── Onda 1: Visão — Screenshot e análise visual ─────────────────────

def capture_game_screenshot(
    wait_frames: int = 10,
    scene_path: str | None = None,
    resolution_width: int = 640,
    resolution_height: int = 360,
) -> dict:
    """Captura screenshot do jogo. Dois modos:

    MODO PERSISTENTE (0.1s): se game bridge TCP estiver conectado,
    envia comando 'screenshot' e retorna o PNG instantaneamente.

    MODO RAPIDO (3s): cold-start via --write-movie com SW_HIDE.
    640x360, 60fps, 10 frames. Janela invisivel.

    Returns:
        {"status": "success", "image_base64": str, "image_path": str}
    """
    import base64, shutil
    from datetime import datetime

    proj = _get_active_project()
    godot = get_godot_bin()
    cfg = get_config()

    if not (proj / "project.godot").exists():
        return {"status": "error", "message": "Projeto nao encontrado."}

    # ── Validação de segurança ──────────────────────────────────
    if scene_path:
        violation = _check_path_traversal(scene_path, proj)
        if violation:
            return violation

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    capture_dir = proj / "captures"
    capture_dir.mkdir(exist_ok=True)

    # ── Modo 1: Persistente (TCP bridge) ──────────────────────────
    from tools.game_bridge import is_connected, gb_screenshot
    import os

    if is_connected():
        filename = f"screenshot_{timestamp}.png"
        r = gb_screenshot(filename)
        if r.get("status") == "success" or r.get("result", {}).get("saved"):
            appdata = os.environ.get("APPDATA", "")
            user_png = Path(appdata) / "Godot" / "app_userdata" / proj.name / filename
            if user_png.exists():
                img_data = user_png.read_bytes()
                b64 = base64.b64encode(img_data).decode("ascii")
                final = capture_dir / filename
                shutil.copy2(str(user_png), str(final))
                return {
                    "status": "success", "mode": "persistent",
                    "image_base64": b64, "image_path": str(final),
                    "image_size_bytes": len(img_data),
                }

    # ── Modo 2: Rapido (--write-movie cold start) ─────────────────
    timeout = cfg.get("timeouts", {}).get("compile", 60) + 10
    movie_path = capture_dir / f"mcp_{timestamp}.png"

    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0  # SW_HIDE

    cmd = [
        godot, "--path", str(proj),
        "--write-movie", str(movie_path),
        "--fixed-fps", "60",
        "--quit-after", str(wait_frames),
        "--disable-vsync",
        "--resolution", f"{resolution_width}x{resolution_height}",
    ]
    if scene_path:
        cmd.append(scene_path)

    try:
        run_subprocess_safe(cmd, timeout=timeout, startupinfo=startup)
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": f"Timeout apos {timeout}s."}
    except Exception as e:
        return {"status": "error", "message": f"Erro: {e}"}

    frames = sorted(capture_dir.glob(f"mcp_{timestamp}*.png"))
    if not frames:
        return {"status": "error", "message": "Nenhum frame gerado."}

    last = frames[-1]
    img_data = last.read_bytes()
    b64 = base64.b64encode(img_data).decode("ascii")
    final = capture_dir / f"screenshot_{timestamp}.png"
    shutil.move(str(last), str(final))

    return {
        "status": "success", "mode": "fast",
        "image_base64": b64, "image_path": str(final),
        "image_size_bytes": len(img_data),
        "frames_captured": len(frames),
    }


def compare_screenshots(
    before_path: str,
    after_path: str,
) -> dict:
    """Compara duas screenshots usando Image.compute_image_metrics() do Godot.

    Roda um script GDScript mínimo que carrega as duas imagens e calcula
    métricas de similaridade: max, mean, mean_squared, root_mean_squared,
    peak_snr (Peak Signal-to-Noise Ratio).

    Args:
        before_path: Caminho relativo da screenshot "antes".
        after_path: Caminho relativo da screenshot "depois".

    Returns:
        {"status": "success", "metrics": {"max": float, "mean": float,
         "mean_squared": float, "root_mean_squared": float, "peak_snr": float,
         "difference_percent": float}}
    """
    proj = _get_active_project()
    godot = get_godot_bin()

    before_full = proj / before_path
    after_full = proj / after_path

    if not before_full.exists():
        return {"status": "error", "message": f"Screenshot 'antes' não encontrada: {before_path}"}
    if not after_full.exists():
        return {"status": "error", "message": f"Screenshot 'depois' não encontrada: {after_path}"}

    # ── Script GDScript de comparação ──────────────────────────────
    compare_script = f'''extends SceneTree

func _init():
    var img_before := Image.load_from_file("{before_full.as_posix()}")
    var img_after := Image.load_from_file("{after_full.as_posix()}")

    if not img_before or not img_after:
        printerr("ERRO: não foi possível carregar as imagens.")
        quit(1)
        return

    # Converte para mesmo formato se necessário
    if img_before.get_format() != img_after.get_format():
        img_after.convert(img_before.get_format())

    # Redimensiona para mesmo tamanho se necessário
    if img_before.get_size() != img_after.get_size():
        img_after.resize(img_before.get_width(), img_before.get_height(), Image.INTERPOLATE_LANCZOS)

    var metrics := img_before.compute_image_metrics(img_after, true)

    # Calcula % de diferença baseado no mean_squared
    var max_possible := 1.0
    if img_before.get_format() == Image.FORMAT_RGBA8:
        max_possible = 255.0 * 255.0
    var diff_pct := sqrt(metrics["mean_squared"]) / sqrt(max_possible) * 100.0

    print("METRICS_JSON:" + JSON.stringify({{
        "max": metrics["max"],
        "mean": metrics["mean"],
        "mean_squared": metrics["mean_squared"],
        "root_mean_squared": metrics["root_mean_squared"],
        "peak_snr": metrics["peak_snr"],
        "difference_percent": diff_pct
    }}))

    quit()
'''

    script_file = proj / "_mcp_compare.gd"
    script_file.write_text(compare_script, encoding="utf-8")

    try:
        result = subprocess.run(
            [godot, "--headless", "-s", str(script_file.relative_to(proj)), "--path", str(proj)],
            capture_output=True, text=True, timeout=30,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        script_file.unlink(missing_ok=True)
        return {"status": "error", "message": "Timeout na comparação."}
    except Exception as e:
        script_file.unlink(missing_ok=True)
        return {"status": "error", "message": f"Erro: {e}"}
    finally:
        script_file.unlink(missing_ok=True)

    for line in (result.stdout or "").splitlines():
        if "METRICS_JSON:" in line:
            import json
            metrics = json.loads(line.split("METRICS_JSON:", 1)[1])
            return {"status": "success", "metrics": metrics}

    return {
        "status": "error",
        "message": f"Não foi possível extrair métricas. Output: {(result.stdout or '')[-200:]}",
    }


def detect_empty_screen(
    screenshot_path: str | None = None,
    image_base64: str | None = None,
    empty_threshold: float = 0.95,
) -> dict:
    """Detecta se uma screenshot está vazia (tela preta, branca ou cor sólida).

    Útil para detectar problemas comuns: esqueceu de adicionar câmera,
    cena vazia, fundo não configurado, todos os sprites fora da tela.

    Analisa os pixels da imagem (em Python, sem precisar do Godot).
    Se >empty_threshold (95%) dos pixels têm a mesma cor → tela vazia.

    Args:
        screenshot_path: Caminho da screenshot no projeto.
        image_base64: Alternativa: PNG em base64 (de capture_game_screenshot).
        empty_threshold: Limiar de similaridade para considerar vazia (0.0-1.0).

    Returns:
        {"status": "success", "empty": bool, "reason": str, "dominant_color": [...]}
    """
    import base64
    import io

    img_bytes = None
    if screenshot_path:
        proj = _get_active_project()
        img_file = proj / screenshot_path
        if not img_file.exists():
            return {"status": "error", "message": f"Screenshot não encontrada: {screenshot_path}"}
        img_bytes = img_file.read_bytes()
    elif image_base64:
        img_bytes = base64.b64decode(image_base64)
    else:
        return {"status": "error", "message": "Forneça screenshot_path ou image_base64."}

    # ── Análise de pixels sem Pillow (puro Python + struct) ────────
    import struct
    import zlib

    # Parse PNG mínimo (assume PNG RGBA 8-bit, o formato do Godot)
    try:
        # Pula header PNG (8 bytes)
        data = img_bytes
        if data[:8] != b'\x89PNG\r\n\x1a\n':
            return {"status": "error", "message": "Arquivo não é PNG válido."}

        # Encontra IHDR para obter dimensões
        # Simplificado: vamos usar uma abordagem mais bruta
        # Pula header e chunks até encontrar IDAT
        pos = 8
        width = height = 0
        while pos < len(data) - 4:
            length = struct.unpack('>I', data[pos:pos+4])[0]
            chunk_type = data[pos+4:pos+8].decode('ascii', errors='ignore')
            if chunk_type == 'IHDR':
                width = struct.unpack('>I', data[pos+8:pos+12])[0]
                height = struct.unpack('>I', data[pos+12:pos+16])[0]
            elif chunk_type == 'IDAT':
                break
            pos += 12 + length

        if width == 0 or height == 0:
            return {"status": "error", "message": "Não foi possível ler dimensões do PNG."}

        # Extrai pixels de todos os chunks IDAT
        compressed_data = b''
        while pos < len(data) - 4:
            length = struct.unpack('>I', data[pos:pos+4])[0]
            chunk_type = data[pos+4:pos+8].decode('ascii', errors='ignore')
            if chunk_type == 'IDAT':
                compressed_data += data[pos+8:pos+8+length]
            elif chunk_type == 'IEND':
                break
            pos += 12 + length

        raw_data = zlib.decompress(compressed_data)

        # Conta cores por pixel (RGBA, 4 bytes por pixel, +1 byte de filtro por linha)
        color_counts = {}
        total_pixels = 0
        row_stride = width * 4 + 1  # 4 canais + 1 byte de filtro PNG

        for y in range(height):
            row_start = y * row_stride + 1  # pula byte de filtro
            for x in range(width):
                px_start = row_start + x * 4
                r = raw_data[px_start]
                g = raw_data[px_start + 1]
                b = raw_data[px_start + 2]
                a = raw_data[px_start + 3]
                # Agrupa cores similares (tolera variação de ±8)
                key = (r // 16, g // 16, b // 16, a // 16)
                color_counts[key] = color_counts.get(key, 0) + 1
                total_pixels += 1

        if total_pixels == 0:
            return {"status": "error", "message": "Imagem sem pixels."}

        # Encontra cor dominante
        dominant = max(color_counts, key=color_counts.get)
        dominant_ratio = color_counts[dominant] / total_pixels
        dominant_color = [dominant[0] * 16, dominant[1] * 16, dominant[2] * 16, dominant[3] * 16]

        if dominant_ratio >= empty_threshold:
            reason = _classify_empty_screen(dominant_color)
            return {
                "status": "success",
                "empty": True,
                "reason": reason,
                "dominant_color": dominant_color,
                "dominant_ratio": round(dominant_ratio * 100, 1),
            }

        return {
            "status": "success",
            "empty": False,
            "dominant_color": dominant_color,
            "dominant_ratio": round(dominant_ratio * 100, 1),
            "unique_color_groups": len(color_counts),
        }

    except Exception as e:
        return {"status": "error", "message": f"Erro ao analisar PNG: {e}"}


def _classify_empty_screen(dominant_color: list) -> str:
    """Classifica o tipo de tela vazia baseado na cor dominante."""
    r, g, b, a = dominant_color
    brightness = (r + g + b) / 3

    if a < 10:
        return "Tela transparente — possível cena vazia ou todos os nós invisíveis."
    elif brightness < 30:
        return "Tela preta — possível ausência de câmera (Camera2D) ou fundo não configurado."
    elif brightness > 240:
        return "Tela branca — possível cena sem elementos visuais ou shader com problema."
    elif abs(r - g) < 10 and abs(g - b) < 10:
        return f"Tela com cor sólida RGB({r},{g},{b}) — possível fundo sem elementos de jogo."
    else:
        return f"Tela dominada por cor RGB({r},{g},{b}) — verifique se os sprites estão visíveis."


# ── Constante ROOT ──────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent


def record_gameplay_gif(
    duration: int = 5,
    fps: int = 10,
    resolution_width: int = 480,
    resolution_height: int = 270,
) -> dict:
    """Grava gameplay e retorna GIF animado em base64.

    Usa Godot --write-movie para gerar frames PNG, depois PIL para
    compor GIF animado. Útil para a IA "ver" o que aconteceu no jogo.

    Args:
        duration: Duração da gravação em segundos (max 30).
        fps: Quadros por segundo do GIF (menor = arquivo menor).
        resolution_width: Largura em pixels.
        resolution_height: Altura em pixels.

    Returns:
        {"status": "success", "gif_base64": str, "frames": int, "size_kb": int}
        ou {"status": "error", "message": str}
    """
    import base64
    import io
    import tempfile

    duration = min(duration, 30)
    proj = _get_active_project()
    godot = get_godot_bin()

    # Verifica main scene
    godot_file = proj / "project.godot"
    if not godot_file.exists():
        return {"status": "error", "message": "project.godot não encontrado."}

    # Usa pasta temporaria para os frames
    with tempfile.TemporaryDirectory(prefix="mcp_gif_") as tmpdir:
        tmp = Path(tmpdir)

        # Comando Godot --write-movie (gera PNGs)
        total_frames = duration * fps
        cmd = [
            godot,
            "--path", str(proj),
            "--write-movie", str(tmp / "frame.png"),
            "--fixed-fps", str(fps),
            "--resolution", f"{resolution_width}x{resolution_height}",
            "--disable-vsync",
            "--quit-after", str(total_frames),
        ]

        # SW_HIDE no Windows
        startupinfo = None
        if hasattr(subprocess, "STARTUPINFO"):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE

        try:
            run_subprocess_safe(
                cmd, timeout=duration + 30, cwd=str(proj),
                startupinfo=startupinfo,
            )
        except subprocess.TimeoutExpired:
            pass  # Frames ja foram gerados

        # Coleta frames gerados
        frames = sorted(tmp.glob("frame*.png"))
        if not frames:
            return {"status": "error", "message": "Nenhum frame gerado. Verifique se ha uma main scene definida."}

        # Compoe GIF com PIL (ou fallback: retorna frames PNG individuais)
        try:
            from PIL import Image

            images = []
            for f in frames:
                img = Image.open(f)
                img = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
                images.append(img)

            buf = io.BytesIO()
            images[0].save(
                buf, format="GIF", save_all=True,
                append_images=images[1:],
                duration=int(1000 / fps), loop=0,
                optimize=True,
            )
            buf.seek(0)
            gif_bytes = buf.read()

            return {
                "status": "success",
                "gif_base64": base64.b64encode(gif_bytes).decode("ascii"),
                "frames": len(frames),
                "size_kb": len(gif_bytes) // 1024,
                "duration_s": duration,
                "fps": fps,
                "format": "gif",
            }
        except ImportError:
            # Fallback: retorna primeiro e ultimo frame como PNG base64
            import base64 as b64
            frames_b64 = []
            for f in [frames[0], frames[-1]]:
                with open(f, "rb") as fh:
                    frames_b64.append(b64.b64encode(fh.read()).decode("ascii"))

            return {
                "status": "success",
                "frames_png_base64": frames_b64,
                "total_frames": len(frames),
                "duration_s": duration,
                "fps": fps,
                "format": "png_frames",
                "note": "PIL nao instalado — retornando frames PNG em vez de GIF. Instale Pillow para GIF: pip install Pillow",
            }


def visual_regression(args=None):
    """Compara screenshot atual contra baseline salvo — detecta regressao visual.

    Pipeline: (1) Se baseline nao existe, salva a captura atual como baseline.
    (2) Captura screenshot atual. (3) Compara via Godot compute_image_metrics().
    (4) Reporta passed/failed com difference_percent vs threshold.

    Thresholds recomendados:
      0.0% — identico (pixel-perfect, mesma resolucao/formato)
      0.5% — quase identico (ruido de render mínimo, mesma placa)
      1.0% — default (pequenas diferenças de anti-aliasing)
      2.0% — tolerante (diferentes GPUs, Godot versions próximas)
      5.0% — muito tolerante (mudanca de resolucao, so pega erros grosseiros)

    Args:
        scene_path: Cena a capturar (opcional — usa cena ativa).
        threshold: Limiar de diferença em % (default: 1.0).
        baseline_name: Nome do baseline (default: "baseline").

    Returns:
        {"status": "success", "passed": bool, "difference_percent": float, ...}
    """
    import shutil; from pathlib import Path; args=args or {}
    sp=args.get("scene_path"); th=args.get("threshold",1.0); bn=args.get("baseline_name","baseline")
    proj=_get_active_project(); bd=proj/"captures"/"baselines"; bd.mkdir(parents=True,exist_ok=True); bf=bd/f"{bn}.png"
    if not bf.exists():
        cap=capture_game_screenshot(scene_path=sp) if sp else capture_game_screenshot()
        if cap.get("status")!="success": return {"status":"error","message":f"Falha: {cap.get('message','')}"}
        shutil.copy2(str(Path(cap["image_path"])),str(bf))
        return {"status":"baseline_saved","baseline_path":str(bf),"message":"Baseline salvo. Execute novamente para comparar."}
    cap=capture_game_screenshot(scene_path=sp) if sp else capture_game_screenshot()
    if cap.get("status")!="success": return {"status":"error","message":f"Falha: {cap.get('message','')}"}
    cp=Path(cap["image_path"]); tb=proj/"captures"/f"_rb_{bn}.png"; tc=proj/"captures"/f"_rc_{bn}.png"
    shutil.copy2(str(bf),str(tb)); shutil.copy2(str(cp),str(tc))
    cmp=compare_screenshots(before_path=f"captures/_rb_{bn}.png",after_path=f"captures/_rc_{bn}.png")
    tb.unlink(missing_ok=True); tc.unlink(missing_ok=True)
    if cmp.get("status")!="success": return {"status":"error","message":f"Comparação: {cmp.get('message','')}"}
    m=cmp["metrics"]; dp=m.get("difference_percent",100.0); passed=dp<=th
    r={"status":"success","passed":passed,"difference_percent":round(dp,2),"threshold":th,"metrics":m}
    r["message" if passed else "recommendation"]=f"OK - {dp:.2f}%" if passed else f"Diferenca {dp:.1f}% > {th}%. Verifique mudancas visuais."
    return r


def manage_visual_baselines(args=None):
    """Gerencia baselines visuais: listar, aprovar (promover captura atual),
    remover, inspecionar.

    Operacoes:
      op="list" — Lista todos os baselines salvos com tamanho e data.
      op="approve" — Promove a captura mais recente a baseline (sobrescreve).
      op="delete" — Remove um baseline.
      op="inspect" — Mostra detalhes de um baseline (dimensoes, tamanho, data).

    Args:
        op: Operacao (list, approve, delete, inspect). Default: list.
        baseline_name: Nome do baseline (para approve/delete/inspect).

    Returns:
        dict com resultado da operacao.
    """
    from pathlib import Path; import os; from datetime import datetime; args=args or {}
    op=args.get("op","list"); bn=args.get("baseline_name")
    proj=_get_active_project(); bd=proj/"captures"/"baselines"; bd.mkdir(parents=True,exist_ok=True)

    if op=="list":
        baselines=[]
        for f in sorted(bd.glob("*.png")):
            st=f.stat()
            baselines.append({"name":f.stem,"size_kb":round(st.st_size/1024,1),"modified":datetime.fromtimestamp(st.st_mtime).isoformat()})
        return {"status":"success","op":"list","total":len(baselines),"baselines":baselines}

    if op in ("approve","delete","inspect") and not bn:
        return {"status":"error","message":"baseline_name obrigatorio para approve/delete/inspect."}

    bf=bd/f"{bn}.png"
    if op=="inspect":
        if not bf.exists(): return {"status":"error","message":f"Baseline '{bn}' nao encontrado."}
        st=bf.stat()
        return {"status":"success","op":"inspect","name":bn,"path":str(bf),"size_kb":round(st.st_size/1024,1),"modified":datetime.fromtimestamp(st.st_mtime).isoformat()}

    if op=="delete":
        if not bf.exists(): return {"status":"error","message":f"Baseline '{bn}' nao encontrado."}
        bf.unlink()
        return {"status":"success","op":"delete","name":bn,"message":f"Baseline '{bn}' removido."}

    if op=="approve":
        # Encontra a captura mais recente e promove a baseline
        captures_dir=proj/"captures"
        captures=sorted(captures_dir.glob("*.png"),key=lambda p:p.stat().st_mtime,reverse=True)
        if not captures and not bf.exists():
            return {"status":"error","message":"Nenhuma captura encontrada para promover."}
        if captures:
            import shutil; shutil.copy2(str(captures[0]),str(bf))
            return {"status":"success","op":"approve","name":bn,"source":captures[0].name,"message":f"Baseline '{bn}' atualizado com {captures[0].name}."}
        return {"status":"error","message":f"Sem capturas para promover. Baseline '{bn}' mantido."}

    return {"status":"error","message":f"Operacao desconhecida: {op}. Use list, approve, delete ou inspect."}

