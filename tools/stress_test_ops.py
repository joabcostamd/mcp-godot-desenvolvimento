"""stress_test_ops.py — Stress Test com carga e input aleatório (Feature 10).

Orquestra tools existentes do MCP para testar o jogo sob carga:
- game_spawn_node: spawna N instâncias
- inject_input_event: injeta input aleatório com seed explícito
- game_performance: coleta FPS/memória/draw calls em intervalos
- capture_runtime_errors: verifica crash/erros ao final

Teste REPRODUTÍVEL — seed explícito obrigatório.
"""

import json
import random
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def run_stress_test(
    project_path: str = "",
    spawn_scene_path: str = "",
    spawn_count: int = 10,
    duration_seconds: int = 5,
    input_actions: list[str] | None = None,
    random_seed: int = 42,
    fps_threshold: float = 30.0,
    sample_interval_ms: int = 500,
) -> dict:
    """Executa teste de stress no jogo: spawna N entidades, injeta input
    aleatório com seed explícito, e coleta métricas de performance.

    Args:
        project_path: Caminho do projeto (para set_active_project).
        spawn_scene_path: Cena/prefab a instanciar em massa (ex: "res://scenes/enemy.tscn").
        spawn_count: Quantidade de instâncias a spawnar.
        duration_seconds: Duração total do teste.
        input_actions: Lista de ações do InputMap a injetar aleatoriamente
                       (ex: ["move_left","move_right","jump"]). Default: [].
        random_seed: Seed explícita para reprodutibilidade (OBRIGATÓRIO).
        fps_threshold: FPS mínimo aceitável — abaixo disso marca FALHOU.
        sample_interval_ms: Intervalo entre amostras de performance.

    Returns:
        dict com relatório completo: fps_min, fps_avg, fps_below_threshold,
        errors_detected, node_count_final, spawn_results, input_count.
    """
    if input_actions is None:
        input_actions = []

    # ═══ Validação ═══
    if spawn_count < 0:
        return {"status": "error", "message": "spawn_count não pode ser negativo."}
    if duration_seconds < 1:
        return {"status": "error", "message": "duration_seconds deve ser >= 1."}
    if fps_threshold <= 0:
        return {"status": "error", "message": "fps_threshold deve ser > 0."}
    if sample_interval_ms < 50:
        return {"status": "error", "message": "sample_interval_ms deve ser >= 50ms."}

    # ═══ Seed explícita para reprodutibilidade ═══
    rng = random.Random(random_seed)

    # ═══ Estado do projeto ═══
    if project_path:
        try:
            from tools.project_ops import set_active_project
            set_active_project(project_path)
        except Exception as e:
            return {"status": "error", "message": f"Erro ao definir projeto: {e}"}

    # ═══ Verificação de disponibilidade do bridge ═══
    bridge_available = _check_bridge_available()

    # ═══ Fase 1: Spawn ═══
    spawn_results = []
    spawn_errors = 0

    if bridge_available:
        for i in range(spawn_count):
            node_name = f"stress_spawn_{i}"
            try:
                from tools.runtime_rich import game_spawn_node
                result = game_spawn_node(
                    parent_path="/root/Main",
                    node_type=spawn_scene_path if spawn_scene_path else "Node2D",
                    node_name=node_name,
                )
                spawn_results.append({
                    "index": i,
                    "name": node_name,
                    "status": result.get("status", "unknown"),
                })
                if result.get("status") == "error":
                    spawn_errors += 1
            except Exception as e:
                spawn_results.append({
                    "index": i,
                    "name": node_name,
                    "status": "error",
                    "error": str(e)[:100],
                })
                spawn_errors += 1
    else:
        spawn_results = [{"index": i, "status": "skipped", "note": "bridge offline"} for i in range(spawn_count)]
        spawn_errors = spawn_count

    # ═══ Fase 2: Input aleatório + amostragem ═══
    fps_samples: list[float] = []
    node_counts: list[int] = []
    mem_samples: list[float] = []
    input_count = 0

    start_time = time.monotonic()
    elapsed = 0.0

    while elapsed < duration_seconds:
        # ── Input aleatório (seed-based, reprodutível) ──
        if input_actions and bridge_available:
            action = rng.choice(input_actions)
            try:
                from tools.runtime_ops import inject_input_event
                inject_input_event("key", {
                    "keycode": _action_to_keycode(action, rng),
                    "pressed": True,
                })
                input_count += 1
                inject_input_event("key", {
                    "keycode": _action_to_keycode(action, rng),
                    "pressed": False,
                })
            except Exception:
                bridge_available = False

        # ── Amostragem de performance ──
        if bridge_available:
            try:
                from tools.runtime_ui import game_performance
                perf = game_performance()
                if perf.get("status") == "success":
                    data = perf.get("result", perf)
                    if isinstance(data, str):
                        try:
                            data = json.loads(data)
                        except json.JSONDecodeError:
                            pass
                    if isinstance(data, dict):
                        fps = data.get("fps", 0)
                        if isinstance(fps, (int, float)) and fps > 0:
                            fps_samples.append(float(fps))
                        nodes = data.get("nodes", 0)
                        if isinstance(nodes, (int, float)):
                            node_counts.append(int(nodes))
                        mem = data.get("memory_static_mb", 0)
                        if isinstance(mem, (int, float)):
                            mem_samples.append(float(mem))
            except Exception:
                bridge_available = False

        time.sleep(sample_interval_ms / 1000.0)
        elapsed = time.monotonic() - start_time

    # ═══ Fase 3: Verificação de erros ═══
    errors_detected = False
    error_details: list[dict[str, Any]] = []

    if bridge_available:
        try:
            from tools.playtest_ops import capture_runtime_errors
            err_result = capture_runtime_errors()
            if err_result.get("status") == "success":
                runtime_info = err_result.get("runtime_info", {})
                if isinstance(runtime_info, dict):
                    err_list = runtime_info.get("errors", [])
                    if err_list:
                        errors_detected = True
                        error_details = err_list
        except Exception:
            pass

    # ═══ Fase 4: Node count final ═══
    node_count_final = 0
    if bridge_available:
        try:
            from tools.runtime_ui import game_performance
            final_perf = game_performance()
            if final_perf.get("status") == "success":
                data = final_perf.get("result", final_perf)
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        pass
                if isinstance(data, dict):
                    node_count_final = int(data.get("nodes", 0))
        except Exception:
            pass

    # ═══ Compilação do relatório ═══
    fps_min = min(fps_samples) if fps_samples else 0.0
    fps_avg = sum(fps_samples) / len(fps_samples) if fps_samples else 0.0
    fps_below = fps_min < fps_threshold

    node_avg = sum(node_counts) / len(node_counts) if node_counts else 0
    mem_avg = sum(mem_samples) / len(mem_samples) if mem_samples else 0.0

    passed = not fps_below and not errors_detected and spawn_errors == 0

    return {
        "status": "success",
        "report": {
            "passed": passed,
            "duration_seconds": round(elapsed, 1),
            "random_seed": random_seed,
            "bridge_available": bridge_available,
            # ── Spawn ──
            "spawn_requested": spawn_count,
            "spawn_succeeded": spawn_count - spawn_errors,
            "spawn_errors": spawn_errors,
            # ── Performance ──
            "fps_min": round(fps_min, 1),
            "fps_avg": round(fps_avg, 1),
            "fps_threshold": fps_threshold,
            "fps_below_threshold": fps_below,
            "fps_sample_count": len(fps_samples),
            "node_count_avg": round(node_avg, 1),
            "node_count_final": node_count_final,
            "memory_static_mb_avg": round(mem_avg, 1),
            # ── Input ──
            "input_actions_used": input_actions,
            "input_events_injected": input_count,
            # ── Erros ──
            "errors_detected": errors_detected,
            "error_details": error_details,
        },
    }


def _check_bridge_available() -> bool:
    """Verifica se o game bridge está acessível (timeout curto, 1 tentativa)."""
    try:
        from tools.game_bridge import connect as gb_connect, is_connected as gb_connected
        if gb_connected():
            return True
        result = gb_connect(retries=1, backoff=0.1)
        return result.get("status") == "success"
    except Exception:
        return False


def _action_to_keycode(action: str, rng: random.Random) -> int:
    """Mapeia nome de ação do InputMap para keycode. Usa seed para
    variação determinística dentro da ação."""
    # Mapeamento comum Godot
    keycode_map = {
        "move_left": 65,     # KEY_A
        "move_right": 68,    # KEY_D
        "move_up": 87,       # KEY_W
        "move_down": 83,     # KEY_S
        "jump": 32,          # KEY_SPACE
        "attack": 74,        # KEY_J
        "interact": 69,      # KEY_E
        "ui_accept": 32,     # KEY_SPACE / ENTER
        "ui_cancel": 16777217,  # KEY_ESCAPE
        "ui_up": 16777232,
        "ui_down": 16777233,
        "ui_left": 16777234,
        "ui_right": 16777235,
        "pause": 16777217,   # KEY_ESCAPE
        "reload": 82,        # KEY_R
        "sprint": 16777237,  # KEY_SHIFT
        "crouch": 16777236,  # KEY_CTRL
    }
    return keycode_map.get(action, 65)  # default: KEY_A
