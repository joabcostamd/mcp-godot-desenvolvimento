"""decision_engine.py — Decide automaticamente quando gerar arte/audio (Onda 7)."""

from tools.project_state import get_state

_SPRITE_TRIGGERS = ["personagem", "inimigo", "jogador", "player", "boss", "torre", "defesa", "npc", "monstro",
    "item", "coletavel", "moeda", "power-up", "projetil", "tiro", "portal", "porta", "sprite", "arte", "visual",
    "animacao", "animado", "icone", "textura", "imagem", "cenario", "background"]

_AUDIO_TRIGGERS = ["som", "audio", "sfx", "musica", "efeito sonoro", "explosao", "tiro", "pulo", "dano", "morte",
    "vitoria", "derrota", "ambiente", "trilha", "batida", "passos", "impacto", "recarga", "alerta"]

_NO_ASSET_TRIGGERS = ["corrige", "arruma", "bug", "erro", "ajusta", "muda", "altera", "troca", "modifica",
    "muda valor", "balanceia", "dificuldade", "velocidade", "debug", "console", "compila", "testa", "commit",
    "salva", "git", "refatora", "limpa", "otimiza", "renomeia", "move", "copia", "documenta"]

_NODE_NEEDS_SPRITE = ["CharacterBody2D", "StaticBody2D", "RigidBody2D", "Area2D", "Sprite2D", "AnimatedSprite2D"]


def classify_intent(user_message: str) -> dict:
    msg = user_message.lower()
    if any(t in msg for t in _NO_ASSET_TRIGGERS):
        return {"needs_sprite": False, "needs_audio": False, "category": "no_assets"}
    ns = any(t in msg for t in _SPRITE_TRIGGERS)
    na = any(t in msg for t in _AUDIO_TRIGGERS)
    if ns and na: cat = "full_creation"
    elif ns: cat = "visual_only"
    elif na: cat = "audio_only"
    elif any(w in msg for w in ["cria", "criar", "adiciona", "faz", "novo"]): cat = "create_entity"
    else: cat = "modify_behavior"
    return {"needs_sprite": ns, "needs_audio": na, "category": cat}


def decide_art(entity_name: str, entity_type: str = "Node") -> dict:
    state = get_state()
    if state.project_root is None:
        return {"should_generate": False, "generator": "none", "reason": "Projeto nao configurado"}
    if state.has_sprite_for(entity_name):
        return {"should_generate": False, "generator": "none", "reason": "Sprite ja existe"}
    if entity_type in _NODE_NEEDS_SPRITE:
        gen = "placeholder" if state.get_stage() in ("vazio", "prototipo") else "flux"
        return {"should_generate": True, "generator": gen, "reason": f"{'Prototipo' if gen=='placeholder' else 'Desenvolvimento'} — {gen}"}
    return {"should_generate": False, "generator": "none", "reason": "Nao essencial"}


def decide_audio(action_name: str) -> dict:
    state = get_state()
    if state.project_root is None:
        return {"should_generate": False, "sfx_type": "none", "reason": "Projeto nao configurado"}
    if state.has_audio_for(action_name):
        return {"should_generate": False, "sfx_type": "none", "reason": "Audio ja existe"}
    mapping = {"shoot":"gunshot","fire":"laser","atirar":"gunshot","jump":"jump","pulo":"jump","attack":"hit",
               "atacar":"hit","damage":"damage","dano":"damage","die":"explosion","morte":"explosion",
               "collect":"coin","coletar":"coin","explode":"explosion","click":"ui_click","powerup":"powerup",
               "spawn":"magic","magic":"magic"}
    for w, sfx in mapping.items():
        if w in action_name.lower():
            return {"should_generate": True, "sfx_type": sfx, "reason": f"Acao '{action_name}' -> SFX '{sfx}'"}
    return {"should_generate": False, "sfx_type": "none", "reason": "Nenhuma acao mapeada"}


def suggest_next(entity_name: str) -> list[str]:
    state = get_state()
    suggestions = []
    if not state.has_sprite_for(entity_name):
        suggestions.append(f"Gerar sprite para '{entity_name}'?")
    if not state.has_audio_for(entity_name):
        suggestions.append(f"Gerar SFX para '{entity_name}'?")
    return suggestions[:2]
