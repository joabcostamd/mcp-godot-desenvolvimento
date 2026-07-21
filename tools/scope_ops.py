"""scope_ops.py — Primeiro nao bem feito + Disclosure IA (Fatias 3.I + 3.J).

Rollup scope_manage(op=validate_idea|disclosure).
3.I: Transforma "nao da" em contraproposta com versao reduzida.
3.J: Gera disclosure de conteudo IA para publicacao (exigencia Steam).
"""


def _op_validate_idea(params: dict) -> dict:
    """Valida uma ideia de jogo e oferece contraproposta em vez de 'nao'.

    Campos em params:
        idea: str — descricao da ideia do usuario
    """
    idea = params.get("idea", "").strip()
    if not idea:
        return {"status": "error", "message": "Campo 'idea' e obrigatorio."}

    idea_lower = idea.lower()

    # Detecta escopos inviaveis
    huge_terms = ["mmo", "open world", "mundo aberto", "multiplayer massivo",
                   "rpg de 100 horas", "sandbox infinito"]
    is_huge = any(t in idea_lower for t in huge_terms)

    if is_huge:
        return {
            "status": "success",
            "decision": "contraproposta",
            "original": idea,
            "why_not": (
                f"'{idea}' e um projeto de 2+ anos para um estudio completo. "
                "Mas da para fazer uma versao incrivel em 2 semanas."
            ),
            "counter_offer": (
                "Versao de 2 semanas: pegue o nucleo da ideia (o loop de 30 segundos) "
                "e implemente so ele. Ex: em vez de 'MMO open world', faca "
                "'arena de combate single-player com 3 inimigos diferentes'. "
                "O que acha?"
            ),
            "suggestion": "Se aceitar a contraproposta, use quickstart_manage op=run com a versao reduzida.",
        }

    # Ideias viaveis — encoraja
    return {
        "status": "success",
        "decision": "viavel",
        "original": idea,
        "message": (
            f"'{idea}' e uma ideia de escopo viavel! "
            "Va em frente. Use quickstart_manage op=run para comecar."
        ),
    }


def _op_disclosure(params: dict) -> dict:  # noqa: ARG001
    """Gera disclosure de uso de IA para publicacao (Steam, itch.io).

    A Steam exige declarar uso de IA generativa na publicacao.
    Sem essa declaracao, o jogo pode ser rejeitado.
    """
    return {
        "status": "success",
        "disclosure": {
            "title": "Declaracao de Uso de IA Generativa",
            "sections": {
                "pre_generated": (
                    "Este jogo foi desenvolvido com auxilio de ferramentas de IA "
                    "generativa (MCP Godot Agent + DeepSeek V4) para geracao de "
                    "codigo GDScript, cenas Godot e comportamentos de jogo. "
                    "Todo o conteudo gerado por IA foi revisado e validado por "
                    "um desenvolvedor humano antes da publicacao."
                ),
                "live_generated": (
                    "Este jogo NAO gera conteudo por IA em tempo real durante "
                    "a execucao. Todo o conteudo e pre-gerado e estatico."
                ),
            },
            "steam_section": (
                "Na pagina da Steamworks, na secao 'Content Survey', "
                "marque 'Yes' para 'AI-Generated Content', subsecao "
                "'Pre-Generated: Any kind of content created with AI tools'. "
                "Cole o texto acima na descricao."
            ),
            "itch_io_section": (
                "No itch.io, adicione a tag 'AI-Generated' e inclua "
                "a declaracao na descricao do jogo."
            ),
        },
        "message": "Disclosure de IA gerado. Use na publicacao do seu jogo.",
    }


_SCOPE_OPS = {"validate_idea": _op_validate_idea, "disclosure": _op_disclosure}


def scope_manage(op: str, params: dict | None = None) -> dict:
    if op not in _SCOPE_OPS:
        return {"status": "error", "message": f"Operacao '{op}' desconhecida.", "available_ops": list(_SCOPE_OPS.keys())}
    return _SCOPE_OPS[op](params or {})
