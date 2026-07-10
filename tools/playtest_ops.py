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
