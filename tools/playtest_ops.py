"""playtest_ops.py — Playtesting Determinístico (Fase 2B / A3+A4+A5).

Ferramentas para controlar o relógio do jogo, capturar estado de
runtime como JSON e monitorar erros. Tudo via game bridge (TCP 9081).

Baseado no padrão satelliteoflove/godot-mcp.
"""

import json

# ── Helpers ─────────────────────────────────────────────────────────

def _run_gdscript(code: str) -> dict:
    """Executa GDScript no jogo rodando via game bridge."""
    try:
        from tools.runtime_ops import execute_gdscript_runtime
        return execute_gdscript_runtime(code)
    except Exception as e:
        return {"status": "error", "message": f"Game bridge indisponível: {e}"}


def _game_bridge_available() -> bool:
    """Verifica se a game bridge está conectada."""
    try:
        from tools.game_bridge import is_connected
        return is_connected()
    except Exception:
        return False


# ── A3: Game Clock ──────────────────────────────────────────────────

def freeze_game_clock() -> dict:
    """Congela o relógio do jogo (pausa sem parar o processo).

    O jogo para de atualizar física, animações e _process.
    Use antes de step_time para playtesting determinístico.
    Pré-condições: jogo rodando com game bridge (TCP 9081).
    """
    code = """
    get_tree().paused = true
    Engine.time_scale = 0.0
    return JSON.stringify({"status": "ok", "paused": true, "time_scale": 0.0})
    """
    result = _run_gdscript(code)
    if result.get("status") == "success":
        data = result.get("result", result)
        if isinstance(data, str):
            data = json.loads(data)
        return {"status": "success", "frozen": True, "details": data}
    return result


def unfreeze_game_clock() -> dict:
    """Descongela o relógio do jogo (retoma execução normal).

    Restaura time_scale para 1.0 e despausa a árvore.
    """
    code = """
    Engine.time_scale = 1.0
    get_tree().paused = false
    return JSON.stringify({"status": "ok", "paused": false, "time_scale": 1.0})
    """
    result = _run_gdscript(code)
    if result.get("status") == "success":
        data = result.get("result", result)
        if isinstance(data, str):
            data = json.loads(data)
        return {"status": "success", "frozen": False, "details": data}
    return result


def step_game_time(ms: int = 16) -> dict:
    """Avança o relógio do jogo em N milissegundos.

    O jogo processa exatamente N ms de física/animação e depois
    congela novamente. Ideal para playtesting frame a frame.

    Args:
        ms: Milissegundos a avançar (default: 16 = ~1 frame a 60fps).
    """
    code = f"""
    var ms_per_frame = {ms} / 1000.0
    var start = Time.get_ticks_msec()
    
    Engine.time_scale = 1.0
    get_tree().paused = false
    
    # Aguarda o tempo especificado
    var elapsed = 0.0
    while elapsed < ms_per_frame:
        await get_tree().process_frame
        elapsed = (Time.get_ticks_msec() - start) / 1000.0
    
    get_tree().paused = true
    Engine.time_scale = 0.0
    
    return JSON.stringify({{
        "status": "ok",
        "ms_advanced": {ms},
        "actual_elapsed_ms": Time.get_ticks_msec() - start
    }})
    """
    result = _run_gdscript(code)
    if result.get("status") == "success":
        data = result.get("result", result)
        if isinstance(data, str):
            data = json.loads(data)
        _watch_state_tick()  # Onda 1: coletar estado do watcher
        return {"status": "success", "stepped_ms": ms, "details": data}
    return result


def step_until(condition: str, timeout_ms: int = 5000) -> dict:
    """Avança o jogo até que uma condição GDScript seja verdadeira.

    Ex: \"get_node('/root/Main/Player').position.x > 500\"
    Ex: \"get_tree().get_node_count() >= 10\"

    Args:
        condition: Expressão GDScript que retorna bool.
        timeout_ms: Tempo máximo em ms antes de desistir.
    """
    code = f"""
    var start = Time.get_ticks_msec()
    var timeout = {timeout_ms} / 1000.0
    var met = false
    
    Engine.time_scale = 1.0
    get_tree().paused = false
    
    while not met:
        met = ({condition})
        if met:
            break
        await get_tree().process_frame
        if (Time.get_ticks_msec() - start) / 1000.0 > timeout:
            break
    
    get_tree().paused = true
    Engine.time_scale = 0.0
    
    return JSON.stringify({{
        "status": "ok",
        "condition_met": met,
        "elapsed_ms": Time.get_ticks_msec() - start,
        "condition": "{condition}"
    }})
    """
    result = _run_gdscript(code)
    if result.get("status") == "success":
        data = result.get("result", result)
        if isinstance(data, str):
            data = json.loads(data)
        return {"status": "success", "condition_met": data.get("condition_met", False), "details": data}
    return result


# ── A4: Runtime State Digest ────────────────────────────────────────

def get_runtime_state_digest(groups: list[str] | None = None) -> dict:
    """Retorna estado do jogo como JSON estruturado.

    Coleta posição, velocidade, animação, grupos de TODAS as entidades.
    Sem gastar tokens de visão com screenshot — JSON é barato.

    Args:
        groups: Lista de grupos Godot a monitorar (opcional).
                Se None, retorna TODAS as entidades na cena.
    """
    group_filter = json.dumps(groups) if groups else "null"
    code = f"""
    var result = {{}}
    var root = get_tree().current_scene
    if root:
        result["scene"] = root.name
        result["entities"] = []
        _collect_state(root, result["entities"])
    result["time_scale"] = Engine.time_scale
    result["paused"] = get_tree().paused
    result["fps"] = Engine.get_frames_per_second()
    return JSON.stringify(result)
    
    func _collect_state(node, arr):
        if node is Node2D or node is Node3D:
            var entry = {{
                "name": node.name,
                "type": node.get_class(),
                "path": node.get_path(),
                "position": {{"x": node.position.x, "y": node.position.y}} if node is Node2D else {{"x": node.position.x, "y": node.position.y, "z": node.position.z}},
                "visible": node.visible,
                "groups": [],
            }}
            for g in node.get_groups():
                entry["groups"].append(g)
            if node.has_method("get_velocity"):
                var vel = node.get_velocity()
                entry["velocity"] = {{"x": vel.x, "y": vel.y}}
            arr.append(entry)
        for child in node.get_children():
            _collect_state(child, arr)
    """
    result = _run_gdscript(code)
    if result.get("status") == "success":
        data = result.get("result", result)
        if isinstance(data, str):
            data = json.loads(data)
        return {"status": "success", "state": data}
    return result


# ── A5: Runtime Error Capture ───────────────────────────────────────

def capture_runtime_errors() -> dict:
    """Captura erros e warnings do jogo em execução.

    Retorna os últimos erros registrados pelo sistema de log do Godot.
    Mais específico que read_console_output — foca só em erros.
    """
    code = """
    var errors = []
    var log = Engine.get_singleton("GodotLogger")
    # Tenta acessar o buffer de erros do engine
    # Nota: Godot 4 não expõe log de erros via GDScript diretamente.
    # Usamos uma abordagem alternativa: capturar erros pendentes.
    return JSON.stringify({
        "status": "ok",
        "errors": errors,
        "fps": Engine.get_frames_per_second(),
        "object_count": get_tree().get_node_count() if get_tree() else 0,
        "note": "Godot 4 nao expoe log de erros via GDScript. Use read_console_output para capturar erros do console."
    })
    """
    result = _run_gdscript(code)
    if result.get("status") == "success":
        data = result.get("result", result)
        if isinstance(data, str):
            data = json.loads(data)
        return {"status": "success", "runtime_info": data}
    return result


# ══════════════════════════════════════════════════════════════
# ONDA 1: Playtesting Avançado (watch_state, godot_exec, effect_probe)
# ══════════════════════════════════════════════════════════════

_WATCH_STATE = {
    "active": False,
    "targets": [],
    "history": [],
    "step": 0,
    "interval": 1,
}


def watch_state_start(
    targets: list[dict],
    interval_steps: int = 1,
) -> dict:
    """Comeca a observar propriedades de nos a cada step do jogo.

    Args:
        targets: Lista de alvos. Cada alvo:
            {"node_path": "Grid/Enemies/Scout", "properties": ["position", "hp", "velocity"]}
        interval_steps: A cada quantos steps coletar (1 = todo step).

    Returns:
        {"status": "success", "watching": len(targets), "interval": interval_steps}
    """
    global _WATCH_STATE
    _WATCH_STATE = {
        "active": True,
        "targets": targets,
        "history": [],
        "step": 0,
        "interval": interval_steps,
    }
    return {
        "status": "success",
        "watching": len(targets),
        "interval": interval_steps,
        "message": "Watcher ativo. Use watch_state_collect() para obter dados.",
    }


def watch_state_collect() -> dict:
    """Coleta o historico de estados observados desde watch_state_start().

    Returns:
        {"status": "success", "steps_recorded": 150, "targets": 3,
         "history": [{step, timestamp, states: [{node, properties}]}, ...]}
    """
    global _WATCH_STATE

    if not _WATCH_STATE["active"]:
        return {"status": "error", "message": "Watcher nao esta ativo. Use watch_state_start() primeiro."}

    return {
        "status": "success",
        "steps_recorded": len(_WATCH_STATE["history"]),
        "targets": len(_WATCH_STATE["targets"]),
        "history": _WATCH_STATE["history"][-200:],
        "message": f"{len(_WATCH_STATE['history'])} pontos coletados.",
    }


def _watch_state_tick():
    """Chamado internamente a cada step_game_time(). Coleta estado."""
    global _WATCH_STATE
    if not _WATCH_STATE["active"]:
        return

    _WATCH_STATE["step"] += 1
    if _WATCH_STATE["step"] % _WATCH_STATE["interval"] != 0:
        return

    import time

    states = []
    for target in _WATCH_STATE["targets"]:
        node_path = target["node_path"]
        props = target.get("properties", ["position", "name"])
        node_state = {"node": node_path}
        for prop in props:
            code = f"return str(get_node('{node_path}').{prop}) if hasattr(get_node('{node_path}'), '{prop}') else 'N/A'"
            result = _run_gdscript(code)
            val = result.get("result", "N/A")
            if isinstance(val, str) and val.startswith("{"):
                try:
                    val = json.loads(val)
                except Exception:
                    pass
            node_state[prop] = val
        states.append(node_state)

    _WATCH_STATE["history"].append({
        "step": _WATCH_STATE["step"],
        "timestamp": time.time(),
        "states": states,
    })


def godot_exec(code: str) -> dict:
    """Executa codigo GDScript DENTRO do jogo rodando.

    Util para setup de cenarios de teste: spawnar inimigos,
    modificar HP, teleportar jogador, etc.

    Args:
        code: Codigo GDScript a executar. Use 'return' para obter valor.
            Ex: "return get_tree().get_nodes_in_group('enemies').size()"

    Returns:
        {"status": "success", "result": 5, "output": ""}
    """
    result = _run_gdscript(code)
    if result.get("status") == "success":
        val = result.get("result", result)
        if isinstance(val, str):
            try:
                val = json.loads(val)
            except Exception:
                pass
        return {"status": "success", "result": val, "output": result.get("output", "")}
    return result


def effect_probe(
    before: str,
    action: str,
    after: str,
    wait_ms: int = 100,
) -> dict:
    """Verifica se uma acao produziu o efeito esperado.

    Args:
        before: Expressao GDScript avaliada ANTES da acao.
        action: Codigo GDScript da acao (ex: injetar input).
        after: Expressao GDScript avaliada DEPOIS da acao.
        wait_ms: Tempo de espera entre acao e verificacao.

    Returns:
        {"status": "success", "before": 100, "after": 80,
         "delta": -20, "effect_detected": true}

    Exemplo:
        effect_probe(
            before="return $Player.hp",
            action="$Player.take_damage(20)",
            after="return $Player.hp",
        )
    """
    import time

    r_before = _run_gdscript(before)
    before_val = r_before.get("result")

    _run_gdscript(action)
    time.sleep(wait_ms / 1000.0)
    step_game_time(wait_ms)

    r_after = _run_gdscript(after)
    after_val = r_after.get("result")

    delta = None
    try:
        if isinstance(before_val, (int, float)) and isinstance(after_val, (int, float)):
            delta = after_val - before_val
    except Exception:
        pass

    return {
        "status": "success",
        "before": before_val,
        "after": after_val,
        "delta": delta,
        "effect_detected": before_val != after_val,
    }


# ══════════════════════════════════════════════════════════════════════
# Fatia 3.14 — SELF-PLAY (Playtest Autônomo)
# ══════════════════════════════════════════════════════════════════════

def self_play(
    duration: float = 30.0,
    inputs: list[dict] | None = None,
    max_steps: int = 100,
    capture_interval: float = 2.0,
) -> dict:
    """Agente joga o jogo automaticamente e reporta anomalias.

    Compila, lança, injeta inputs, captura screenshots e detecta
    anomalias: crash, tela preta (softlock), erros de input, timeout.

    Args:
        duration: Duração máxima em segundos (> 0).
        inputs: Sequência [{type, data, delay}, ...]. Auto-gerado se None.
        max_steps: Máximo de passos de input.
        capture_interval: Intervalo entre screenshots (s).

    Returns:
        {"status": "success", "anomalies": [...],
         "steps": int, "duration": float, "result": str}
    """
    import time as _time

    # ── Guardas ─────────────────────────────────────────────
    if duration <= 0:
        return {"status": "error", "message": "duration deve ser > 0"}
    if max_steps <= 0:
        return {"status": "error", "message": "max_steps deve ser > 0"}

    # ── Inputs padrão ───────────────────────────────────────
    if inputs is None:
        inputs = _default_play_inputs(duration, max_steps)
    if len(inputs) > 10000:
        return {"status": "error", "message": "Máximo de 10000 inputs permitido"}

    # ── Imports (topo para evitar classificação errada) ─────
    from tools.runtime_ops import compile_test, run_game, stop_game, inject_input_event, capture_game_screenshot

    anomalies = []
    step_count = 0
    start = _time.time()
    last_cap = 0.0

    # ── Compilar ────────────────────────────────────────────
    try:
        compile_result = compile_test()
        if compile_result.get("errors"):
            return {
                "status": "error",
                "message": "Erros de compilação antes do playtest",
                "compile_errors": compile_result["errors"],
            }
    except Exception as e:
        return {"status": "error", "message": f"Compilação falhou: {e}"}

    # ── Lançar ──────────────────────────────────────────────
    try:
        run_result = run_game()
        if run_result.get("status") != "success":
            try:
                stop_game()
            except Exception:
                pass
            return {"status": "error", "message": "Falha ao lançar jogo para playtest",
                    "detail": run_result}
    except Exception as e:
        return {"status": "error", "message": f"Lançamento falhou: {e}"}

    # ── Loop ────────────────────────────────────────────────
    try:
        for i, inp in enumerate(inputs):
            if _time.time() - start > duration:
                break

            _time.sleep(inp.get("delay", 0.3))
            try:
                inject_input_event(inp.get("type", "key"), inp.get("data", {}))
            except Exception as e:
                anomalies.append({"type": "input_error", "step": i, "error": str(e)})

            if _time.time() - last_cap >= capture_interval:
                try:
                    ss = capture_game_screenshot()
                    if ss.get("status") == "success":
                        mode = ss.get("mode", "")
                        b64 = ss.get("image_base64", "")
                        # Só detecta tela preta em modo persistente (cold-start pode não ter imagem)
                        if mode == "persistent" and (not b64 or len(b64) < 100):
                            anomalies.append({
                                "type": "black_screen",
                                "step": i,
                                "time": round(_time.time() - start, 1),
                                "note": "Tela preta/vazia — possível softlock.",
                            })
                    last_cap = _time.time()
                except Exception as e:
                    anomalies.append({"type": "capture_error", "step": i, "error": str(e)})

            step_count = i + 1

    except Exception as e:
        anomalies.append({"type": "crash", "step": step_count, "error": str(e)})

    # ── Parar jogo ─────────────────────────────────────────
    try:
        stop_game()
    except Exception as e:
        anomalies.append({"type": "cleanup_error", "error": str(e)})

    elapsed = round(_time.time() - start, 1)

    if any(a["type"] == "crash" for a in anomalies):
        result = "crash"
    elif any(a["type"] == "black_screen" for a in anomalies):
        result = "softlock"
    elif anomalies:
        result = "warnings"
    elif step_count >= len(inputs):
        result = "completed"
    else:
        result = "timeout"

    return {
        "status": "success",
        "result": result,
        "steps": step_count,
        "duration": elapsed,
        "anomalies": anomalies,
        "anomaly_count": len(anomalies),
        "note": f"Playtest {result}: {step_count} steps em {elapsed}s, {len(anomalies)} anomalias.",
    }


def _default_play_inputs(duration: float, max_steps: int) -> list[dict]:
    """Gera sequência básica de inputs para self-play.

    Usa keycodes Godot (inteiros) compatíveis com inject_input_event.
    """
    # Godot Key constants (Godot 4.x)
    GODOT_KEYS = {
        "ui_right": 4194309,   # KEY_RIGHT
        "ui_left": 4194311,    # KEY_LEFT
        "ui_up": 4194310,      # KEY_UP
        "ui_down": 4194312,    # KEY_DOWN
        "ui_accept": 4194307,  # KEY_ENTER
        "ui_select": 32,       # KEY_SPACE
        "ui_cancel": 4194305,  # KEY_ESCAPE
    }
    keys = list(GODOT_KEYS.values())
    key_names = list(GODOT_KEYS.keys())
    steps = []
    step = 0
    while step < max_steps and step * 0.5 < duration:
        idx = step % len(keys)
        steps.append({
            "type": "key",
            "data": {"keycode": keys[idx], "pressed": True, "action": key_names[idx]},
            "delay": 0.3,
        })
        steps.append({
            "type": "key",
            "data": {"keycode": keys[idx], "pressed": False},
            "delay": 0.2,
        })
        step += 2
    return steps


# ══════════════════════════════════════════════════════════════════════
# Fatia 3.15 — REGRESSION FROM RECORDING
# ══════════════════════════════════════════════════════════════════════

def regression_from_recording(
    session_name: str = "default",
    mode: str = "record",
    duration: float = 15.0,
    max_steps: int = 50,
    tolerance: float = 0.05,
) -> dict:
    """Grava/reproduz sessão de gameplay para teste de regressão.

    Modo 'record': grava inputs + screenshots de uma sessão.
    Modo 'replay': reproduz inputs, captura screenshots e compara
    com a gravação original. Detecta divergência visual (regressão).

    Usa comparação perceptual (compare_screenshots) quando disponível,
    com fallback para hash SHA256 do base64.

    Args:
        session_name: Nome da sessão (sanitizado automaticamente).
        mode: "record" para gravar, "replay" para reproduzir e comparar.
        duration: Duração máxima em segundos.
        max_steps: Máximo de passos de input.
        tolerance: Taxa de divergência aceitável (0-1).

    Returns:
        {"status": "success", "mode": str, "session": str,
         "frames": int, "divergences": int (replay)}
    """
    import hashlib
    import json as _json
    import time as _time

    from tools.project_ops import _get_active_project
    from tools.safety import checkpoint
    from tools.runtime_ops import compile_test, run_game, stop_game
    from tools.runtime_ops import inject_input_event, capture_game_screenshot, compare_screenshots

    proj = _get_active_project()

    # ── Sanitizar session_name contra path traversal ────────
    safe_name = str(session_name)
    for char in "\\/.":
        safe_name = safe_name.replace(char, "_")
    safe_name = safe_name.strip("_") or "default"

    rec_dir = proj / "recordings"
    rec_dir.mkdir(parents=True, exist_ok=True)
    session_file = rec_dir / f"{safe_name}.json"

    # ── Guardas ─────────────────────────────────────────────
    if mode not in ("record", "replay"):
        return {"status": "error", "message": "mode deve ser 'record' ou 'replay'."}
    if duration <= 0:
        return {"status": "error", "message": "duration deve ser > 0"}

    if mode == "record":
        return _record_session(session_name, session_file, duration, max_steps, proj)
    return _replay_session(session_name, session_file, duration, tolerance, proj)


def _record_session(session_name: str, session_file, duration: float, max_steps: int, proj) -> dict:
    """Grava sessão de gameplay: inputs + screenshots."""
    import json as _json
    import time as _time

    from tools.runtime_ops import compile_test, run_game, stop_game
    from tools.runtime_ops import inject_input_event, capture_game_screenshot
    from tools.safety import checkpoint

    cr = compile_test()
    if cr.get("errors"):
        return {"status": "error", "message": "Erros de compilação", "errors": cr["errors"]}
    rr = run_game()
    if rr.get("status") != "success":
        return {"status": "error", "message": "Falha ao lançar", "detail": rr}

    inputs = _default_play_inputs(duration, max_steps)
    frames = []
    input_errors = []
    start = _time.time()

    try:
        for i, inp in enumerate(inputs):
            if _time.time() - start > duration:
                break
            _time.sleep(inp.get("delay", 0.3))
            try:
                inject_input_event(inp.get("type", "key"), inp.get("data", {}))
            except Exception as e:
                input_errors.append({"step": i, "error": str(e)})

            ss = capture_game_screenshot()
            b64 = ss.get("image_base64", "")
            frames.append({
                "step": i,
                "input": inp,
                "image_base64": b64,
                "time": round(_time.time() - start, 2),
            })

            if len(frames) > 5000:
                break
    except Exception as e:
        return {"status": "error", "message": f"Gravação interrompida: {e}"}
    finally:
        try: stop_game()
        except Exception: pass

    checkpoint(f"recordings/{session_file.name}", proj)
    session_data = {
        "session": session_name,
        "duration": duration,
        "max_steps": max_steps,
        "recorded_at": _time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_frames": len(frames),
        "input_errors": len(input_errors),
        "frames": frames,
    }
    session_file.write_text(_json.dumps(session_data, indent=2), encoding="utf-8")

    return {
        "status": "success",
        "mode": "record",
        "session": session_name,
        "frames": len(frames),
        "input_errors": len(input_errors),
        "saved_to": str(session_file.relative_to(proj)),
    }


def _replay_session(session_name: str, session_file, duration: float, tolerance: float, proj) -> dict:
    """Reproduz sessão gravada e compara screenshots."""
    import hashlib
    import json as _json
    import time as _time

    from tools.runtime_ops import compile_test, run_game, stop_game
    from tools.runtime_ops import inject_input_event, capture_game_screenshot, compare_screenshots

    if not session_file.exists():
        return {"status": "error", "message": f"Sessão '{session_name}' não encontrada. Execute mode='record' primeiro."}

    session_data = _json.loads(session_file.read_text(encoding="utf-8"))
    recorded_frames = session_data.get("frames", [])

    if not recorded_frames:
        return {"status": "error", "message": "Sessão vazia — sem frames para comparar."}

    cr = compile_test()
    if cr.get("errors"):
        return {"status": "error", "message": "Erros de compilação", "errors": cr["errors"]}
    rr = run_game()
    if rr.get("status") != "success":
        return {"status": "error", "message": "Falha ao lançar", "detail": rr}

    divergences = []
    input_errors = []
    crashed = False
    start = _time.time()

    try:
        for i, rec in enumerate(recorded_frames):
            if _time.time() - start > duration:
                break
            inp = rec.get("input", {})
            _time.sleep(inp.get("delay", 0.3))
            try:
                inject_input_event(inp.get("type", "key"), inp.get("data", {}))
            except Exception as e:
                input_errors.append({"step": i, "error": str(e)})

            ss = capture_game_screenshot()
            if ss.get("status") == "success":
                # Comparação perceptual (compare_screenshots) quando disponível
                try:
                    cmp = compare_screenshots(ss.get("image_base64", ""), rec.get("image_base64", ""))
                    if cmp.get("status") == "success" and cmp.get("different", False):
                        divergences.append({
                            "step": i,
                            "diff_pct": cmp.get("diff_percent", 0),
                            "time": round(_time.time() - start, 2),
                        })
                except Exception:
                    # Fallback: hash SHA256
                    b64 = ss.get("image_base64", "")
                    current_hash = hashlib.sha256(b64.encode()).hexdigest() if b64 else ""
                    original_hash = hashlib.sha256(rec.get("image_base64", "").encode()).hexdigest()
                    if current_hash and original_hash and current_hash != original_hash:
                        divergences.append({
                            "step": i,
                            "method": "hash",
                            "time": round(_time.time() - start, 2),
                        })
    except Exception as e:
        crashed = True
    finally:
        try: stop_game()
        except Exception: pass

    total = len(recorded_frames)
    div_count = len(divergences)
    div_rate = div_count / total if total > 0 else 0.0
    passed = not crashed and div_rate <= tolerance

    result = {
        "status": "success",
        "mode": "replay",
        "session": session_name,
        "frames": total,
        "divergences": div_count,
        "divergence_rate": round(div_rate, 3),
        "input_errors": len(input_errors),
        "tolerance": tolerance,
        "passed": passed,
    }
    if crashed:
        result["result"] = "crash"
        result["note"] = f"CRASH durante replay após {div_count} divergências."
    elif passed:
        result["result"] = "pass"
        result["note"] = f"PASSOU: {div_count}/{total} frames divergentes ({div_rate:.1%}, tolerância {tolerance:.0%})."
    else:
        result["result"] = "fail"
        result["note"] = f"FALHOU: {div_count}/{total} frames divergentes ({div_rate:.1%}, tolerância {tolerance:.0%})."
    return result


# ══════════════════════════════════════════════════════════════════════
# Fatia 3.16 — DIFFICULTY CURVE
# ══════════════════════════════════════════════════════════════════════

def difficulty_curve(
    sessions: int = 3,
    duration: float = 20.0,
    max_steps: int = 80,
) -> dict:
    """Analisa a curva de dificuldade via múltiplos self-plays.

    Roda N sessões de self-play, coleta métricas de cada uma
    (steps completados, anomalias, tempo) e compila um relatório
    de curva de dificuldade: onde o agente trava, consistência
    entre sessões, taxa de falha.

    Args:
        sessions: Número de sessões de self-play (1-10).
        duration: Duração de cada sessão em segundos.
        max_steps: Máximo de steps por sessão.

    Returns:
        {"status": "success", "curve": [...], "summary": {...}}
    """
    if sessions < 1 or sessions > 10:
        return {"status": "error", "message": "sessions deve ser entre 1 e 10."}
    if duration <= 0:
        return {"status": "error", "message": "duration deve ser > 0."}

    results = []
    total_steps = 0
    crashes = 0
    softlocks = 0
    completed = 0
    errors = 0

    for s in range(sessions):
        try:
            r = self_play(duration=duration, max_steps=max_steps,
                         capture_interval=duration / 5 if duration > 0 else 5.0)
            # Detectar erros do self_play (status=error, não exception)
            if r.get("status") == "error":
                results.append({
                    "session": s + 1, "result": "error", "steps": 0,
                    "duration": 0, "anomaly_count": 0,
                    "error": r.get("message", "Erro no self_play"),
                })
                errors += 1
                continue

            result_type = r.get("result", "unknown")
            results.append({
                "session": s + 1, "result": result_type,
                "steps": r.get("steps", 0), "duration": r.get("duration", 0),
                "anomaly_count": r.get("anomaly_count", 0),
            })
            total_steps += r.get("steps", 0)
            if result_type == "crash":
                crashes += 1
            elif result_type == "softlock":
                softlocks += 1
            elif result_type == "completed":
                completed += 1
        except Exception as e:
            results.append({"session": s + 1, "result": "error", "error": str(e)})
            errors += 1

    avg_steps = total_steps / sessions if sessions > 0 else 0
    total_failures = errors + crashes + softlocks
    fail_rate = total_failures / sessions if sessions > 0 else 0

    # Curva: distribuição de steps por sessão
    curve = [
        {"session": r["session"], "steps": r["steps"], "result": r["result"]}
        for r in results
    ]

    # Tendência: steps aumentam ou diminuem? (exclui falhas)
    steps_list = [r["steps"] for r in results if r["result"] not in ("crash", "error", "unknown")]
    trend = "flat"
    if len(steps_list) >= 2:
        if steps_list[-1] > steps_list[0] * 1.1:
            trend = "improving"
        elif steps_list[-1] < steps_list[0] * 0.9:
            trend = "degrading"

    summary = {
        "sessions": sessions,
        "avg_steps": round(avg_steps, 1),
        "max_steps_per_session": max_steps,
        "completed": completed,
        "crashes": crashes,
        "softlocks": softlocks,
        "errors": errors,
        "fail_rate": round(fail_rate, 2),
        "trend": trend,
        "interpretation": _interpret_curve(completed, crashes, softlocks, errors, trend, fail_rate, sessions),
    }

    return {
        "status": "success",
        "curve": curve,
        "summary": summary,
    }


def _interpret_curve(completed: int, crashes: int, softlocks: int, errors: int,
                     trend: str, fail_rate: float, sessions: int) -> str:
    """Gera interpretação textual da curva de dificuldade."""
    total_fail = crashes + softlocks + errors
    if total_fail >= sessions * 0.5:
        parts = []
        if crashes: parts.append(f"{crashes} crashes")
        if softlocks: parts.append(f"{softlocks} softlocks")
        if errors: parts.append(f"{errors} erros")
        return f"ALERTA: {total_fail}/{sessions} sessões falharam ({', '.join(parts)}). Jogo instável — corrija antes de balancear."
    if completed >= sessions * 0.8 and fail_rate < 0.2:
        return f"Jogo estável: {completed}/{sessions} sessões completas, {fail_rate:.0%} falha. Dificuldade adequada."
    if trend == "degrading":
        return "Dificuldade AUMENTANDO entre sessões — possível vazamento de estado ou scaling incorreto."
    if trend == "improving" and fail_rate > 0.3:
        return f"Dificuldade ALTA ({fail_rate:.0%} falha) mas melhorando entre sessões."
    if fail_rate > 0.5:
        return f"Dificuldade ALTA: {fail_rate:.0%} das sessões falham. Considere reduzir dificuldade inicial."
    return f"Curva mista: {completed} completas, {crashes} crashes, {softlocks} softlocks, {errors} erros. Ajuste balanceamento."


# ══════════════════════════════════════════════════════════════
# ONDA 3: Rollup playtest_manage (Fatia 3.A — smoke test do jogo)
# ══════════════════════════════════════════════════════════════

import time as _time

# Constantes do smoke test
_DEFAULT_SMOKE_DURATION = 10
_DEFAULT_FPS_THRESHOLD = 30
_DEFAULT_DRAW_CALL_LIMIT = 1000


def _is_runtime_bridge_available(timeout: float = 2.0) -> bool:
    """Verifica se o runtime bridge (:8790) esta respondendo."""
    try:
        from runtime_bridge_client import send_bridge_command
        result = send_bridge_command({"cmd": "runtime_info"}, timeout=timeout)
        return result.get("ok", False)
    except Exception:
        return False


def _collect_playtest_metrics() -> dict | None:
    """Coleta metricas do jogo via runtime bridge.

    Returns:
        dict com fps, draw_calls, memory_mb ou None.
    """
    try:
        from runtime_bridge_client import send_bridge_command
        result = send_bridge_command({"cmd": "runtime_info"}, timeout=3.0)
        if result.get("ok"):
            return {
                "fps": result.get("fps", 0),
                "draw_calls": result.get("draw_calls", 0),
                "memory_mb": round(result.get("static_memory_mb", 0), 1),
                "physics_ms": round(result.get("physics_process_time_ms", 0), 1),
            }
        return None
    except Exception:
        return None


def _capture_viewport_screenshot() -> dict | None:
    """Captura screenshot para confirmar viewport ativo."""
    try:
        from runtime_bridge_client import send_bridge_command
        result = send_bridge_command({"cmd": "screenshot"}, timeout=5.0)
        if result.get("ok"):
            return {
                "width": result.get("width", 0),
                "height": result.get("height", 0),
            }
        return None
    except Exception:
        return None


def _op_playtest_smoke(params: dict) -> dict:
    """Smoke test do jogo: abre, aguenta N segundos sem crash, FPS ok.

    Usa o runtime bridge (:8790) para metricas em tempo real.
    NAO requer Godot editor fechado — requer jogo rodando em debug (F5).

    Campos em params:
        duration: int (default 10) — segundos de observacao
        fps_threshold: int (default 30) — FPS minimo aceitavel
    """
    duration = params.get("duration", _DEFAULT_SMOKE_DURATION)
    fps_threshold = params.get("fps_threshold", _DEFAULT_FPS_THRESHOLD)

    if not isinstance(duration, (int, float)) or duration < 1:
        return {
            "status": "error",
            "message": f"Duracao invalida: {duration}. Use um valor >= 1 segundo.",
        }
    if duration > 300:
        return {
            "status": "error",
            "message": f"Duracao muito longa: {duration}s. Maximo permitido: 300s (5 min).",
        }
    if not isinstance(fps_threshold, (int, float)) or fps_threshold < 1:
        return {
            "status": "error",
            "message": f"FPS threshold invalido: {fps_threshold}. Use um valor >= 1.",
        }

    duration = int(duration)
    fps_threshold = int(fps_threshold)

    if not _is_runtime_bridge_available():
        return {
            "status": "error",
            "message": (
                "Jogo nao esta rodando em modo debug. "
                "Abra o Godot e rode o jogo (F5) antes do smoke test. "
                "O runtime bridge (porta 8790) precisa estar ativo."
            ),
        }

    initial = _collect_playtest_metrics()
    if initial is None:
        return {
            "status": "error",
            "message": "Falha ao coletar metricas iniciais. Bridge respondeu mas runtime_info falhou.",
        }

    viewport = _capture_viewport_screenshot()
    viewport_ok = viewport is not None and viewport.get("width", 0) > 0

    _time.sleep(duration)

    final = _collect_playtest_metrics()
    if final is None:
        return {
            "status": "fail",
            "message": (
                "Jogo crashou durante o smoke test. "
                f"Metricas iniciais OK (FPS: {initial['fps']}), "
                f"mas bridge parou de responder apos {duration}s."
            ),
            "initial_metrics": initial,
            "duration_s": duration,
            "crashed": True,
        }

    warnings = []
    fps_min = round(min(initial["fps"], final["fps"]), 1)
    fps_avg = round((initial["fps"] + final["fps"]) / 2, 1)
    fps_max = round(max(initial["fps"], final["fps"]), 1)

    if fps_min < fps_threshold:
        warnings.append(
            f"FPS abaixo do threshold: minimo {fps_min} < {fps_threshold}."
        )

    if fps_avg < 60:
        warnings.append(
            f"FPS medio baixo: {fps_avg}. "
            "No editor, FPS < 60 e esperado em modo debug."
        )

    max_draw = max(initial["draw_calls"], final["draw_calls"])
    if max_draw > _DEFAULT_DRAW_CALL_LIMIT:
        warnings.append(
            f"Draw calls elevadas: {max_draw} > {_DEFAULT_DRAW_CALL_LIMIT}."
        )

    if not viewport_ok:
        warnings.append(
            "Viewport nao retornou screenshot valida. Camera ou cena podem estar vazias."
        )

    passed = fps_min >= fps_threshold

    return {
        "status": "pass" if passed else "warn",
        "message": (
            f"Smoke test concluido em {duration}s. "
            f"FPS: {fps_min}/{fps_avg}/{fps_max} (min/med/max). "
            + (f"{len(warnings)} alerta(s)." if warnings else "Sem alertas.")
        ),
        "metrics": {
            "initial": initial,
            "final": final,
            "fps_min": fps_min,
            "fps_avg": fps_avg,
            "fps_max": fps_max,
            "fps_threshold": fps_threshold,
            "draw_calls_max": max_draw,
        },
        "viewport_active": viewport_ok,
        "viewport_width": viewport.get("width", 0) if viewport else 0,
        "viewport_height": viewport.get("height", 0) if viewport else 0,
        "duration_s": duration,
        "warnings": warnings,
        "crashed": False,
        "note": (
            "Metricas coletadas no editor (debug). "
            "FPS no export tende a ser maior. "
            "Este teste NAO substitui playtest humano — "
            "verifica apenas que o jogo abre e nao crasha."
        ),
    }


# ── Operacao persona_run (Fatia 3.B) ───────────────────────────────

def _send_key_event(action: str, hold_ms: int) -> dict:
    """Envia evento(s) de tecla via runtime bridge.

    O runtime bridge processa input_event como press+release atomico.
    Para simular hold, envia o evento repetidamente com intervalos
    de ~50ms (aproximadamente 1 frame a 60fps).

    Args:
        action: Nome da acao (ex: 'ui_right', 'space').
        hold_ms: Milissegundos para "segurar" a tecla.

    Returns:
        dict com resultado.
    """
    from tools.personas import KEY_MAP

    keycode = KEY_MAP.get(action)
    if keycode is None:
        return {"status": "error", "message": f"Acao desconhecida: '{action}'"}

    try:
        from runtime_bridge_client import send_bridge_command

        # Simula hold enviando o evento a cada ~50ms
        TAP_INTERVAL_MS = 50
        elapsed = 0
        errors = 0

        while elapsed < hold_ms:
            result = send_bridge_command({
                "cmd": "input_event",
                "event": {
                    "type": "key",
                    "keycode": keycode,
                },
            }, timeout=2.0)

            if not result.get("ok"):
                errors += 1

            _time.sleep(TAP_INTERVAL_MS / 1000.0)
            elapsed += TAP_INTERVAL_MS

        if errors > 0:
            return {"status": "warning", "message": f"{errors} erros em {hold_ms}ms de hold"}

        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _op_persona_run(params: dict) -> dict:
    """Executa uma persona scriptada contra o jogo rodando.

    A persona envia uma sequencia de inputs e coleta metricas:
    tempo total, se completou, caminho percorrido.

    Campos em params:
        persona: str — ID da persona ('apressado', 'cauteloso', 'explorador')
        duration: int (default 60) — timeout maximo em segundos
    """
    from tools.personas import get_persona, list_personas

    persona_id = params.get("persona", "").strip().lower()
    max_duration = params.get("duration", 60)

    if not isinstance(max_duration, (int, float)) or max_duration < 5:
        return {
            "status": "error",
            "message": f"Duracao invalida: {max_duration}. Use um valor >= 5 segundos.",
        }

    max_duration = int(max_duration)

    if not persona_id:
        personas_list = list_personas()
        return {
            "status": "error",
            "message": "Campo 'persona' e obrigatorio. Use uma das personas disponiveis.",
            "available_personas": [p["id"] for p in personas_list["personas"]],
        }

    persona = get_persona(persona_id)
    if persona is None:
        personas_list = list_personas()
        return {
            "status": "error",
            "message": f"Persona '{persona_id}' nao encontrada.",
            "available_personas": [p["id"] for p in personas_list["personas"]],
        }

    # Verifica bridge
    if not _is_runtime_bridge_available():
        return {
            "status": "error",
            "message": (
                "Jogo nao esta rodando em modo debug. "
                "Abra o Godot e rode o jogo (F5) antes do playtest."
            ),
        }

    # Coleta metrica inicial
    initial_metrics = _collect_playtest_metrics()
    if initial_metrics is None:
        return {
            "status": "error",
            "message": "Bridge respondeu mas falhou ao coletar metricas iniciais.",
        }

    start_time = _time.time()
    total_inputs = 0
    input_errors = 0
    events: list[dict] = []

    # Executa sequencia de inputs da persona
    for step in persona["inputs"]:
        elapsed = _time.time() - start_time
        if elapsed >= max_duration:
            events.append({"type": "timeout", "elapsed_s": round(elapsed, 1)})
            break

        action = step.get("action", "")
        hold_ms = step.get("hold_ms", 100)
        wait_ms = step.get("wait_ms", 200)

        result = _send_key_event(action, hold_ms)
        total_inputs += 1

        if result.get("status") == "error":
            input_errors += 1
            events.append({
                "type": "input_error",
                "action": action,
                "error": result.get("message", ""),
                "elapsed_s": round(elapsed, 1),
            })

        # Aguarda entre inputs
        if wait_ms > 0:
            _time.sleep(wait_ms / 1000.0)

    end_time = _time.time()
    total_time = round(end_time - start_time, 1)

    # Metricas finais
    final_metrics = _collect_playtest_metrics()

    return {
        "status": "success",
        "persona": {
            "id": persona_id,
            "name": persona["name"],
            "strategy": persona["strategy"],
        },
        "result": {
            "completed": total_time < max_duration and input_errors == 0,
            "total_time_s": total_time,
            "total_inputs": total_inputs,
            "input_errors": input_errors,
            "timeout": total_time >= max_duration,
        },
        "metrics": {
            "initial": initial_metrics,
            "final": final_metrics,
        },
        "events": events[-20:],  # ultimas 20 eventos
        "note": (
            "Playtest por persona scriptada — heuristicas simplificadas. "
            "NAO substitui playtest humano. "
            "Fisica nao-deterministica pode produzir resultados diferentes "
            "entre execucoes."
        ),
    }


_PLAYTEST_OPS = {
    "smoke": _op_playtest_smoke,
    "persona_run": _op_persona_run,
}


def playtest_manage(op: str, params: dict | None = None) -> dict:
    """Gerencia playtesting automatizado do jogo (ONDA 3).

    Args:
        op: Operacao ('smoke' ou 'persona_run').
        params: Parametros especificos da operacao.

    Returns:
        dict com resultado da operacao.
    """
    if op not in _PLAYTEST_OPS:
        from difflib import get_close_matches
        suggestions = get_close_matches(op, list(_PLAYTEST_OPS.keys()), n=3)
        return {
            "status": "error",
            "message": f"Operacao '{op}' desconhecida.",
            "available_ops": list(_PLAYTEST_OPS.keys()),
            "suggestions": suggestions,
        }

    return _PLAYTEST_OPS[op](params or {})
