"""perf_ops.py — Diagnostico de performance do jogo (GRATIS, sem API).

Analisa FPS, draw calls, uso de memoria e sugere otimizacoes.
Conecta no Godot via bridge TCP para coletar dados reais.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ══════════════════════════════════════════════════════════════
# TOOL 1: profile_frame
# ══════════════════════════════════════════════════════════════

def profile_frame(sample_frames: int = 60) -> dict:
    """Analisa performance do jogo rodando e sugere otimizacoes.

    Args:
        sample_frames: Quantos frames amostrar (mais = mais preciso).

    Returns:
        {"status": "success", "fps": {"avg": 58.3}, "grade": "B"}
    """
    import statistics
    import time

    try:
        from tools.game_bridge import _send_game_command
    except ImportError:
        return {"status": "error", "message": "Game bridge indisponivel. O jogo esta rodando?"}

    fps_samples = []
    draw_calls = 0
    memory_mb = 0
    nodes_count = 0

    for i in range(min(sample_frames, 120)):
        try:
            result = _send_game_command("eval", {"code": "return Engine.get_frames_per_second()"})
            if result.get("result"):
                fps_samples.append(float(result["result"]))

            if i == 0:
                dc_result = _send_game_command("eval", {
                    "code": "return RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME)"
                })
                if dc_result.get("result"):
                    draw_calls = int(dc_result["result"])

                nodes_result = _send_game_command("eval", {
                    "code": "return get_tree().get_node_count()"
                })
                if nodes_result.get("result"):
                    nodes_count = int(nodes_result["result"])

                mem_result = _send_game_command("eval", {
                    "code": "return OS.get_static_memory_usage() / 1048576.0"
                })
                if mem_result.get("result"):
                    memory_mb = round(float(mem_result["result"]), 1)
        except Exception:
            pass

        time.sleep(1.0 / max(fps_samples[-1] if fps_samples else 60, 1))

    if not fps_samples:
        return {"status": "error", "message": "Nao foi possivel coletar FPS. O jogo esta rodando?"}

    avg_fps = round(statistics.mean(fps_samples), 1)
    min_fps = round(min(fps_samples), 1)
    max_fps = round(max(fps_samples), 1)

    suggestions = []

    if avg_fps < 30:
        suggestions.append({"severity": "critical", "category": "fps",
            "problem": f"FPS medio muito baixo: {avg_fps}",
            "solution": "Reduza particulas, desative sombras, use LOD, reduza resolucao de texturas"})
    elif avg_fps < 55:
        suggestions.append({"severity": "warning", "category": "fps",
            "problem": f"FPS medio abaixo do ideal: {avg_fps}",
            "solution": "Use VisibilityNotifier2D para desativar nos fora da tela"})

    if min_fps < avg_fps * 0.5:
        suggestions.append({"severity": "warning", "category": "fps",
            "problem": f"Quedas de FPS detectadas (min={min_fps}, avg={avg_fps})",
            "solution": "Verifique loops pesados ou carregamento sincrono de assets"})

    if draw_calls > 500:
        suggestions.append({"severity": "critical", "category": "draw_calls",
            "problem": f"Muitos draw calls: {draw_calls}",
            "solution": "Agrupe sprites em atlas, use TileMapLayer, use batching"})
    elif draw_calls > 100:
        suggestions.append({"severity": "warning", "category": "draw_calls",
            "problem": f"Draw calls elevados: {draw_calls}",
            "solution": "Use atlas de texturas e reduza sprites individuais"})

    if nodes_count > 1000:
        suggestions.append({"severity": "warning", "category": "scene_tree",
            "problem": f"Mais de 1000 nos na cena: {nodes_count}",
            "solution": "Use ObjectPool para inimigos/projeteis, remova nos inativos"})

    if memory_mb > 500:
        suggestions.append({"severity": "warning", "category": "memory",
            "problem": f"Uso de memoria elevado: {memory_mb}MB",
            "solution": "Verifique vazamentos, texturas nao liberadas, ResourceLoader com cache"})

    if avg_fps >= 55 and draw_calls < 100 and memory_mb < 300:
        grade = "A"
    elif avg_fps >= 40 and draw_calls < 300:
        grade = "B"
    elif avg_fps >= 25:
        grade = "C"
    else:
        grade = "D"

    return {
        "status": "success",
        "fps": {"avg": avg_fps, "min": min_fps, "max": max_fps},
        "draw_calls": draw_calls,
        "nodes_count": nodes_count,
        "memory_mb": memory_mb,
        "suggestions": suggestions,
        "grade": grade,
        "samples": len(fps_samples),
        "message": f"Performance nota {grade}: {avg_fps} FPS, {draw_calls} draw calls, {memory_mb}MB RAM. {len(suggestions)} sugestoes.",
    }


# ══════════════════════════════════════════════════════════════
# TOOL 2: profile_memory
# ══════════════════════════════════════════════════════════════

def profile_memory(track_objects: bool = True) -> dict:
    """Analisa uso de memoria do jogo e detecta possiveis vazamentos.

    Args:
        track_objects: Se True, conta objetos por tipo (mais lento).

    Returns:
        {"status": "success", "memory": {"static_mb": 45}, "suggestions": [...]}
    """
    try:
        from tools.game_bridge import _send_game_command
    except ImportError:
        return {"status": "error", "message": "Game bridge indisponivel."}

    result = {"status": "success", "memory": {}, "objects": {}, "suggestions": []}

    try:
        r = _send_game_command("eval", {"code": "return OS.get_static_memory_usage() / 1048576.0"})
        if r.get("result"):
            result["memory"]["static_mb"] = round(float(r["result"]), 1)

        r = _send_game_command("eval", {
            "code": "return Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0"
        })
        if r.get("result"):
            result["memory"]["video_mb"] = round(float(r["result"]), 1)

        if track_objects:
            r = _send_game_command("eval", {"code": "return get_tree().get_node_count()"})
            if r.get("result"):
                result["objects"]["total_nodes"] = int(r["result"])

        static_mb = result["memory"].get("static_mb", 0)
        video_mb = result["memory"].get("video_mb", 0)

        if static_mb > 200:
            result["suggestions"].append({
                "severity": "warning",
                "problem": f"Memoria estatica alta: {static_mb}MB",
                "solution": "Reduza texturas grandes, use compressao VRAM, libere recursos nao usados",
            })
        if video_mb > 500:
            result["suggestions"].append({
                "severity": "warning",
                "problem": f"Memoria de video alta: {video_mb}MB",
                "solution": "Use texturas menores, atlas, e compressao",
            })
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Erro ao coletar metricas: {e}. O jogo esta rodando?"

    return result
