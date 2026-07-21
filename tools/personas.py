"""personas.py — Personas de playtest automatizado (Fatia 3.B).

Define 3 personas fixas que jogam o jogo via runtime bridge:
- apressado: avanca sempre, pressiona botoes rapidamente
- cauteloso: espera, evita risco, testa cada botao
- explorador: testa limites, anda para todos os cantos

Cada persona e uma sequencia de inputs enviados ao jogo via bridge.
"""

# ── Mapeamento de acoes → keycodes Godot 4 ─────────────────────────

KEY_MAP: dict[str, int] = {
    "ui_up": 4194320,
    "ui_down": 4194321,
    "ui_left": 4194318,
    "ui_right": 4194319,
    "ui_accept": 4194306,   # ENTER
    "ui_cancel": 4194305,   # ESCAPE
    "space": 32,
    "w": 87,
    "a": 65,
    "s": 83,
    "d": 68,
}

# ── Personas ────────────────────────────────────────────────────────

PERSONAS: dict[str, dict] = {
    "apressado": {
        "name": "Apressado",
        "description": (
            "Avanca sempre, pressiona botoes rapidamente, nao le texto. "
            "Tende a morrer mais, mas completa rapido se sobreviver."
        ),
        "strategy": "rush",
        "inputs": [
            # Skip intro / menu
            {"action": "ui_accept", "hold_ms": 100, "wait_ms": 500},
            {"action": "ui_accept", "hold_ms": 100, "wait_ms": 300},
            # Move para direita agressivamente
            {"action": "ui_right", "hold_ms": 2000, "wait_ms": 200},
            {"action": "space", "hold_ms": 100, "wait_ms": 300},
            {"action": "ui_right", "hold_ms": 1500, "wait_ms": 200},
            {"action": "space", "hold_ms": 100, "wait_ms": 200},
            {"action": "ui_right", "hold_ms": 1000, "wait_ms": 200},
            {"action": "ui_up", "hold_ms": 300, "wait_ms": 200},
            {"action": "space", "hold_ms": 100, "wait_ms": 200},
            {"action": "ui_right", "hold_ms": 3000, "wait_ms": 200},
        ],
    },
    "cauteloso": {
        "name": "Cauteloso",
        "description": (
            "Espera, evita risco, le dialogos, testa cada botao antes de avancar. "
            "Demora mais, mas morre menos."
        ),
        "strategy": "careful",
        "inputs": [
            # Espera na intro
            {"action": "ui_accept", "hold_ms": 100, "wait_ms": 2000},
            # Move devagar
            {"action": "ui_right", "hold_ms": 500, "wait_ms": 1000},
            {"action": "ui_right", "hold_ms": 300, "wait_ms": 800},
            {"action": "space", "hold_ms": 100, "wait_ms": 1500},
            {"action": "ui_right", "hold_ms": 400, "wait_ms": 1000},
            {"action": "ui_right", "hold_ms": 300, "wait_ms": 800},
            {"action": "ui_up", "hold_ms": 200, "wait_ms": 600},
            {"action": "ui_right", "hold_ms": 500, "wait_ms": 1000},
            {"action": "space", "hold_ms": 100, "wait_ms": 1200},
            {"action": "ui_right", "hold_ms": 400, "wait_ms": 1000},
        ],
    },
    "explorador": {
        "name": "Explorador",
        "description": (
            "Testa os limites do cenario, anda para todos os cantos, "
            "aperta tudo. Cobre mais area mas demora muito."
        ),
        "strategy": "explore",
        "inputs": [
            # Explora menus
            {"action": "ui_accept", "hold_ms": 100, "wait_ms": 300},
            {"action": "ui_cancel", "hold_ms": 100, "wait_ms": 300},
            {"action": "ui_accept", "hold_ms": 100, "wait_ms": 500},
            # Anda para direita
            {"action": "ui_right", "hold_ms": 800, "wait_ms": 300},
            # Volta para esquerda (testa limites)
            {"action": "ui_left", "hold_ms": 400, "wait_ms": 300},
            # Anda para direita de novo
            {"action": "ui_right", "hold_ms": 1000, "wait_ms": 300},
            # Pula / sobe
            {"action": "ui_up", "hold_ms": 300, "wait_ms": 300},
            {"action": "space", "hold_ms": 100, "wait_ms": 300},
            # Anda para esquerda
            {"action": "ui_left", "hold_ms": 500, "wait_ms": 300},
            # Abaixa
            {"action": "ui_down", "hold_ms": 300, "wait_ms": 300},
            # Direita + pula
            {"action": "ui_right", "hold_ms": 1200, "wait_ms": 200},
            {"action": "ui_up", "hold_ms": 400, "wait_ms": 200},
            {"action": "space", "hold_ms": 100, "wait_ms": 300},
            # Continua explorando
            {"action": "ui_right", "hold_ms": 600, "wait_ms": 300},
            {"action": "ui_left", "hold_ms": 300, "wait_ms": 300},
            {"action": "ui_right", "hold_ms": 800, "wait_ms": 300},
        ],
    },
}


def list_personas() -> dict:
    """Lista todas as personas disponiveis com descricao.

    Returns:
        {"status": "success", "personas": [...]}
    """
    result = []
    for pid, pdata in PERSONAS.items():
        result.append({
            "id": pid,
            "name": pdata["name"],
            "description": pdata["description"],
            "strategy": pdata["strategy"],
            "input_count": len(pdata["inputs"]),
        })
    return {"status": "success", "personas": result}


def get_persona(persona_id: str) -> dict | None:
    """Retorna a definicao de uma persona ou None se nao existir."""
    return PERSONAS.get(persona_id)
