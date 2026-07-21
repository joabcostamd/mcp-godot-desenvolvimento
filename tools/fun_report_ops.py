"""fun_report_ops.py — Relatorio de qualidade do jogo (Fatia 3.D).

Rollup fun_report_manage(op=generate).
Consolida dados das 3 camadas de playtest em um diagnostico
com 4 sinais e modos de falha nomeados.

Os 4 sinais:
  1. Taxa de aprovacao — % que completa
  2. Tentativas ate vencer — media e desvio
  3. Variedade de estrategia — acoes distintas usadas
  4. Escalada — comparacao inicio vs fim

Os 4 modos de falha do core loop:
  - Sem escalada (repeticao sem progressao)
  - Sem escolha real (estrategia degenerada)
  - Recompensa distante demais (frustrante)
  - Pico de dificuldade escondido (desvio alto)

Uso:
    fun_report_manage op=generate
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ── Constantes ──────────────────────────────────────────────────────

# Thresholds para os 4 sinais
APPROVAL_TOO_HIGH = 0.95     # >95% = facil demais
APPROVAL_TOO_LOW = 0.20      # <20% = frustrante
STRATEGY_DEGENERATE_MAX = 2  # <=2 acoes distintas = degenerada
VARIANCE_HIGH_FACTOR = 2.0   # desvio > 2x media = pico escondido


# ── Analise dos 4 sinais ────────────────────────────────────────────

def _analyze_approval(persona_results: list[dict], agent_result: dict | None) -> dict:
    """Calcula taxa de aprovacao: % de personas/agentes que completaram."""
    completed = 0
    total = 0

    for p in persona_results:
        total += 1
        if p.get("result", {}).get("completed", False):
            completed += 1

    if agent_result and agent_result.get("status") == "success":
        total += 1
        if agent_result.get("errors", 1) == 0:
            completed += 1

    if total == 0:
        return {"rate": None, "completed": 0, "total": 0, "status": "no_data"}

    rate = completed / total

    if rate >= APPROVAL_TOO_HIGH:
        status = "too_easy"
    elif rate <= APPROVAL_TOO_LOW:
        status = "too_hard"
    else:
        status = "balanced"

    return {
        "rate": round(rate, 2),
        "completed": completed,
        "total": total,
        "status": status,
    }


def _analyze_attempts(persona_results: list[dict]) -> dict:
    """Calcula tentativas ate vencer: media e desvio padrao."""
    times = []
    for p in persona_results:
        t = p.get("result", {}).get("total_time_s", 0)
        if t > 0:
            times.append(t)

    if not times:
        return {"mean_s": None, "std_s": None, "samples": 0, "status": "no_data"}

    mean = sum(times) / len(times)
    variance = sum((t - mean) ** 2 for t in times) / len(times)
    std = variance ** 0.5

    if std > mean * VARIANCE_HIGH_FACTOR:
        status = "high_variance"
    else:
        status = "consistent"

    return {
        "mean_s": round(mean, 1),
        "std_s": round(std, 1),
        "samples": len(times),
        "status": status,
    }


def _analyze_strategy(persona_results: list[dict], agent_result: dict | None) -> dict:
    """Analisa variedade de estrategia: acoes distintas usadas."""
    all_actions: set[str] = set()

    for p in persona_results:
        for step in p.get("inputs", []):
            all_actions.add(step.get("action", ""))

    if agent_result:
        for h in agent_result.get("history", []):
            all_actions.add(h.get("action", ""))

    distinct = len(all_actions)

    if distinct == 0:
        return {"distinct_actions": 0, "actions": [], "status": "no_data"}

    if distinct <= STRATEGY_DEGENERATE_MAX:
        status = "degenerate"
    elif distinct <= 4:
        status = "limited"
    else:
        status = "varied"

    return {
        "distinct_actions": distinct,
        "actions": sorted(all_actions),
        "status": status,
    }


def _analyze_escalation(smoke_result: dict | None) -> dict:
    """Analisa escalada: compara metricas de inicio vs fim (se disponivel)."""
    if not smoke_result:
        return {"status": "no_data", "note": "Rode smoke test para dados de escalada."}

    metrics = smoke_result.get("metrics", {})
    initial = metrics.get("initial", {})
    final = metrics.get("final", {})

    if not initial or not final:
        return {"status": "no_data"}

    fps_initial = initial.get("fps", 0)
    fps_final = final.get("fps", 0)
    fps_drop = fps_initial - fps_final

    if fps_drop > 20:
        status = "degrading"
    elif abs(fps_drop) < 5:
        status = "flat"
    else:
        status = "normal"

    return {
        "fps_initial": fps_initial,
        "fps_final": fps_final,
        "fps_drop": round(fps_drop, 1),
        "status": status,
    }


# ── Diagnostico: sinais → modo de falha ────────────────────────────

def _diagnose_failure_mode(
    approval: dict,
    attempts: dict,
    strategy: dict,
    escalation: dict,
) -> list[dict]:
    """Mapeia os 4 sinais para modos de falha nomeados."""
    failures: list[dict] = []

    # 1. Sem escalada
    if escalation.get("status") == "flat":
        failures.append({
            "mode": "sem_escalada",
            "label": "Sem escalada",
            "detail": "As metricas nao mudam do inicio ao fim — o jogo nao progride.",
            "severity": "warning",
        })
    elif escalation.get("status") == "degrading":
        failures.append({
            "mode": "degradacao",
            "label": "Degradacao de performance",
            "detail": f"FPS caiu {escalation.get('fps_drop', 0)} pontos — "
                      "o jogo fica mais pesado com o tempo.",
            "severity": "warning",
        })

    # 2. Estrategia degenerada
    if strategy.get("status") == "degenerate":
        failures.append({
            "mode": "estrategia_degenerada",
            "label": "Estrategia degenerada",
            "detail": f"Apenas {strategy.get('distinct_actions', 0)} acoes distintas usadas. "
                      "Uma unica estrategia domina — o jogador nao tem escolha real.",
            "severity": "warning",
        })

    # 3. Recompensa distante / frustrante
    if approval.get("status") == "too_hard":
        failures.append({
            "mode": "recompensa_distante",
            "label": "Recompensa distante demais",
            "detail": f"Apenas {approval.get('rate', 0):.0%} completaram. "
                      "O jogo esta frustrante para novos jogadores.",
            "severity": "error",
        })

    # 4. Pico de dificuldade escondido
    if attempts.get("status") == "high_variance":
        failures.append({
            "mode": "pico_escondido",
            "label": "Pico de dificuldade escondido",
            "detail": f"Tempo para completar varia muito "
                      f"(media {attempts.get('mean_s', 0)}s, desvio {attempts.get('std_s', 0)}s). "
                      "Ha um ponto de dificuldade que alguns passam rapido e outros travam.",
            "severity": "warning",
        })

    # 5. Facil demais
    if approval.get("status") == "too_easy":
        failures.append({
            "mode": "falta_desafio",
            "label": "Falta desafio",
            "detail": f"{approval.get('rate', 0):.0%} de aprovacao — "
                      "o jogo pode estar facil demais para engajar.",
            "severity": "info",
        })

    return failures


# ── Geracao do relatorio ────────────────────────────────────────────

def _generate_recommendations(failures: list[dict]) -> list[str]:
    """Gera recomendacoes acionaveis baseadas nos modos de falha."""
    recs: list[str] = []

    for f in failures:
        mode = f["mode"]
        if mode == "sem_escalada":
            recs.append("Adicione novos elementos a cada fase: inimigos diferentes, "
                        "mecanicas novas, ou aumento gradual de velocidade.")
        elif mode == "estrategia_degenerada":
            recs.append("Ofereca mais opcoes ao jogador: power-ups, rotas alternativas, "
                        "ou inimigos que exigem estrategias diferentes.")
        elif mode == "recompensa_distante":
            recs.append("Reduza a dificuldade inicial. Adicione um tutorial ou "
                        "fase de aquecimento. A primeira vitoria deve vir rapido.")
        elif mode == "pico_escondido":
            recs.append("Identifique o ponto de dificuldade (use agent_run para "
                        "encontrar onde as personas travam) e suavize a curva.")
        elif mode == "falta_desafio":
            recs.append("Aumente a dificuldade gradualmente. Adicione inimigos "
                        "mais rapidos, menos recursos, ou tempo limite.")
        elif mode == "degradacao":
            recs.append("Otimize a cena: reduza draw calls, use object pooling, "
                        "ou limite o numero de objetos simultaneos.")

    if not recs:
        recs.append("Continue iterando! Rode playtest_manage op=persona_run "
                     "para mais dados, ou agent_run para teste adaptativo.")

    return recs


def _op_generate(params: dict) -> dict:  # noqa: ARG001
    """Gera o fun_report: relatorio de qualidade com 4 sinais.

    Consolida dados de smoke, persona_run e agent_run (se disponiveis)
    em um diagnostico legivel com modos de falha nomeados.

    NAO requer jogo rodando — analisa dados ja coletados.
    """
    # Coleta dados disponiveis (todos opcionais)
    smoke = params.get("smoke_result", None)
    personas = params.get("persona_results", [])
    agent = params.get("agent_result", None)

    if not isinstance(personas, list):
        personas = []

    # Calcula os 4 sinais
    approval = _analyze_approval(personas, agent)
    attempts = _analyze_attempts(personas)
    strategy = _analyze_strategy(personas, agent)
    escalation = _analyze_escalation(smoke)

    # Diagnostico
    failures = _diagnose_failure_mode(approval, attempts, strategy, escalation)
    recommendations = _generate_recommendations(failures)

    # Determina status geral
    has_data = (
        approval["status"] != "no_data"
        or escalation["status"] != "no_data"
    )

    if not has_data:
        return {
            "status": "success",
            "message": (
                "Nenhum dado de playtest disponivel. "
                "Rode playtest_manage op=smoke ou op=persona_run primeiro."
            ),
            "signals": {
                "approval": approval,
                "attempts": attempts,
                "strategy": strategy,
                "escalation": escalation,
            },
            "failures": [],
            "recommendations": [
                "Rode playtest_manage op=smoke para metricas basicas.",
                "Rode playtest_manage op=persona_run persona=apressado para dados de jogabilidade.",
                "Rode playtest_manage op=agent_run steps=5 para teste adaptativo.",
            ],
            "sample_size_note": "Sem dados.",
        }

    # Monta sumario em portugues simples
    summary_parts = []

    if approval["status"] != "no_data":
        emoji = "✅" if approval["status"] == "balanced" else "⚠️"
        summary_parts.append(
            f"{emoji} Aprovacao: {approval['completed']}/{approval['total']} "
            f"({approval['rate']:.0%})"
        )

    if attempts["status"] != "no_data":
        summary_parts.append(
            f"⏱ Tempo medio: {attempts['mean_s']}s"
        )

    if strategy["status"] != "no_data":
        summary_parts.append(
            f"🎯 Estrategias: {strategy['distinct_actions']} acoes distintas"
        )

    if escalation["status"] != "no_data" and escalation["status"] != "flat":
        summary_parts.append(
            f"📊 FPS: {escalation['fps_initial']}→{escalation['fps_final']}"
        )

    has_failures = len(failures) > 0
    overall = "warn" if has_failures else "pass"

    return {
        "status": "success",
        "overall": overall,
        "summary": " | ".join(summary_parts) if summary_parts else "Analise concluida.",
        "signals": {
            "approval": approval,
            "attempts": attempts,
            "strategy": strategy,
            "escalation": escalation,
        },
        "failures": failures,
        "failure_count": len(failures),
        "recommendations": recommendations,
        "sample_size_note": (
            f"Amostra: {approval['total']} personas/agentes. "
            "Playtest humano continua necessario para validacao final."
        ),
        "disclaimer": (
            "Este relatorio mede indicios de engajamento, nao diversao. "
            "Playtest humano continua necessario."
        ),
    }


# ── Rollup ──────────────────────────────────────────────────────────

_FUN_REPORT_OPS = {
    "generate": _op_generate,
}


def fun_report_manage(op: str, params: dict | None = None) -> dict:
    """Gerencia o relatorio de qualidade do jogo (fun_report).

    Args:
        op: Operacao ('generate').
        params: Parametros (resultados de playtest opcionais).

    Returns:
        dict com relatorio completo.
    """
    if op not in _FUN_REPORT_OPS:
        from difflib import get_close_matches
        suggestions = get_close_matches(op, list(_FUN_REPORT_OPS.keys()), n=3)
        return {
            "status": "error",
            "message": f"Operacao '{op}' desconhecida.",
            "available_ops": list(_FUN_REPORT_OPS.keys()),
            "suggestions": suggestions,
        }

    return _FUN_REPORT_OPS[op](params or {})
