"""teacher_ops.py — Modo professor (Fatia 3.H).

Rollup teacher_manage(op=explain).
Explica em 3 linhas o que foi feito e por que, reduzindo dependencia da IA.
"""


def _op_explain(params: dict) -> dict:
    """Explica de forma didatica o que foi feito na ultima operacao.

    Campos em params:
        context: str — descricao do que foi feito
        phase: str — fase atual do projeto (opcional)
    """
    context = params.get("context", "").strip()
    phase = params.get("phase", "desconhecida")

    if not context:
        return {
            "status": "error",
            "message": "Campo 'context' e obrigatorio. Descreva o que foi feito.",
        }

    # Gera explicacao didatica em 3 partes
    return {
        "status": "success",
        "explanation": {
            "o_que": f"Voce acabou de {context}.",
            "por_que": (
                f"Na fase '{phase}', isso ajuda a construir as bases do seu jogo. "
                "Cada passo feito agora evita retrabalho depois."
            ),
            "proximo": (
                "O proximo passo natural e testar o que foi feito: "
                "rode o jogo (F5) e veja se tudo funciona como esperado."
            ),
        },
        "message": (
            f"📚 Modo professor: Voce fez: {context}. "
            "Isso e importante porque cada peca construida agora evita retrabalho. "
            "Proximo passo: teste o que fez!"
        ),
        "learning_tip": (
            "Dica: tente explicar para outra pessoa o que voce acabou de fazer. "
            "Se conseguir explicar em 1 minuto, voce realmente entendeu."
        ),
    }


_TEACHER_OPS = {"explain": _op_explain}


def teacher_manage(op: str, params: dict | None = None) -> dict:
    if op not in _TEACHER_OPS:
        return {"status": "error", "message": f"Operacao '{op}' desconhecida.", "available_ops": list(_TEACHER_OPS.keys())}
    return _TEACHER_OPS[op](params or {})
