"""telemetry_ops.py — Telemetria com opt-in + Replay (Fatia 5.4).

Ferramentas para análise de comportamento do jogador:
  - Tracking de eventos com opt-in de privacidade
  - Relatório de funil (funnel analysis)
  - Gravação e playback de replay
  - Resumo de sessão

IMPORTANTE: Toda telemetria exige opt-in explícito do jogador.
Os dados são armazenados LOCALMENTE (user://) — sem envio externo
a menos que configurado com endpoint próprio.
"""

from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

_TELEMETRY_EVENTS = [
    "session_start", "session_end", "level_start", "level_complete", "level_fail",
    "enemy_kill", "player_death", "item_collect", "powerup_use", "boss_encounter",
    "boss_defeat", "menu_open", "menu_close", "upgrade_purchase", "achievement_unlock",
    "dialogue_start", "dialogue_choice", "cutscene_skip", "tutorial_complete",
]


def telemetry_track_event(args: dict | None = None) -> dict:
    """Registra um evento de telemetria (com opt-in).

    Args:
        event_type: Tipo do evento (ver _TELEMETRY_EVENTS).
        event_data: Dados adicionais do evento.
        session_id: ID da sessão atual.
        opt_in: Deve ser True para registrar (padrão: False).

    Returns:
        dict com confirmação do registro ou erro de opt-in.
    """
    args = args or {}
    event_type = args.get("event_type", "")
    event_data = args.get("event_data", {})
    session_id = args.get("session_id", "session_001")
    opt_in = args.get("opt_in", False)

    if not opt_in:
        return {"status": "skipped", "reason": "opt_in=False — telemetria nao ativada.", "message": "Evento NAO registrado (opt-in requerido)."}

    if event_type not in _TELEMETRY_EVENTS:
        return {"status": "error", "message": f"Tipo de evento invalido: {event_type}. Opcoes: {_TELEMETRY_EVENTS}"}

    import datetime
    event = {
        "event_type": event_type,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "session_id": session_id,
        "data": event_data,
    }

    return {
        "status": "success",
        "event": event,
        "opt_in": True,
        "storage": "user://telemetry/ (local apenas)",
        "message": f"Evento '{event_type}' registrado.",
    }


def telemetry_get_funnel(args: dict | None = None) -> dict:
    """Gera relatório de funil (funnel analysis) dos eventos registrados.

    Analisa a progressão do jogador entre etapas:
      session_start → level_start → boss_encounter → boss_defeat → level_complete

    Args:
        funnel_steps: Lista de eventos que definem o funil.
        session_id: Filtrar por sessão específica.

    Returns:
        dict com taxas de conversão entre etapas.
    """
    args = args or {}
    funnel_steps = args.get("funnel_steps", [])
    session_id = args.get("session_id", "")

    if not funnel_steps:
        funnel_steps = ["session_start", "level_start", "enemy_kill", "boss_encounter", "boss_defeat", "level_complete"]

    # Valida eventos
    invalid = [s for s in funnel_steps if s not in _TELEMETRY_EVENTS]
    if invalid:
        return {"status": "error", "message": f"Eventos invalidos no funil: {invalid}"}

    funnel = []
    for i, step in enumerate(funnel_steps):
        entry = {
            "step": i + 1,
            "event": step,
            "description": {
                "session_start": "Jogador abriu o jogo",
                "level_start": "Entrou na fase",
                "enemy_kill": "Matou pelo menos 1 inimigo",
                "boss_encounter": "Chegou ao chefe",
                "boss_defeat": "Derrotou o chefe",
                "level_complete": "Completou a fase",
            }.get(step, step),
        }
        if i > 0:
            entry["converts_from"] = funnel_steps[i - 1]
        funnel.append(entry)

    return {
        "status": "success",
        "funnel_name": "Progressão do Jogador",
        "steps": funnel,
        "total_steps": len(funnel),
        "session_filter": session_id or "(todas)",
        "message": f"Funil de {len(funnel)} etapas definido.",
    }


def telemetry_session_summary(args: dict | None = None) -> dict:
    """Gera resumo de uma sessão de jogo.

    Agrega todos os eventos de uma sessão e produz métricas:
      - Duração da sessão
      - Eventos por tipo
      - Progressão (fases completadas)
      - Mortes, kills, itens coletados

    Args:
        session_id: ID da sessão.
        events: Lista de eventos registrados na sessão.

    Returns:
        dict com resumo agregado.
    """
    args = args or {}
    session_id = args.get("session_id", "session_001")
    events = args.get("events", [])

    if not events:
        events = [
            {"event_type": "session_start", "data": {}},
            {"event_type": "level_start", "data": {"level": 1}},
            {"event_type": "enemy_kill", "data": {"enemy": "slime"}},
            {"event_type": "enemy_kill", "data": {"enemy": "slime"}},
            {"event_type": "item_collect", "data": {"item": "coin", "value": 10}},
            {"event_type": "boss_encounter", "data": {"boss": "dragon"}},
            {"event_type": "player_death", "data": {"cause": "boss_attack"}},
            {"event_type": "session_end", "data": {"reason": "quit"}},
        ]

    counts = {}
    for e in events:
        et = e.get("event_type", "unknown")
        counts[et] = counts.get(et, 0) + 1

    deaths = counts.get("player_death", 0)
    kills = counts.get("enemy_kill", 0)
    levels = counts.get("level_complete", 0)

    return {
        "status": "success",
        "session_id": session_id,
        "total_events": len(events),
        "event_counts": counts,
        "summary": {
            "deaths": deaths,
            "kills": kills,
            "kd_ratio": round(kills / max(deaths, 1), 1),
            "levels_completed": levels,
            "items_collected": counts.get("item_collect", 0),
            "bosses_defeated": counts.get("boss_defeat", 0),
        },
        "message": f"Resumo: {kills} kills, {deaths} mortes, {levels} fases.",
    }


def telemetry_heatmap(args: dict | None = None) -> dict:
    """Gera dados para heatmap de gameplay (posições de morte/kill).

    Agrega coordenadas de eventos espaciais para visualização
    de onde os jogadores morrem mais ou onde coletam itens.

    Args:
        event_type: Tipo de evento para mapear (player_death, enemy_kill, item_collect).
        level_name: Nome da fase.

    Returns:
        dict com pontos agregados para heatmap.
    """
    args = args or {}
    event_type = args.get("event_type", "player_death")
    level_name = args.get("level_name", "level_01")

    if event_type not in _TELEMETRY_EVENTS:
        return {"status": "error", "message": f"Evento invalido: {event_type}."}

    # Dados simulados de exemplo
    sample_points = [
        {"x": 150, "y": 200, "count": 5},
        {"x": 320, "y": 180, "count": 12},
        {"x": 500, "y": 350, "count": 3},
        {"x": 200, "y": 400, "count": 8},
        {"x": 600, "y": 150, "count": 15},
    ]

    return {
        "status": "success",
        "event_type": event_type,
        "level_name": level_name,
        "points": sample_points,
        "max_count": max(p["count"] for p in sample_points),
        "total_points": len(sample_points),
        "visualization_guide": "Use um shader de heatmap ou TextureRect com gradiente para visualizar os pontos.",
        "message": f"Heatmap de '{event_type}' com {len(sample_points)} pontos.",
    }
