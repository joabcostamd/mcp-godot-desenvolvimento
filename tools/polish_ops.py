"""polish_ops.py — Polimento e qualidade final (Gaps G5-G10).

Rollup polish_manage(op=version_diff|record_gif|accessibility|productivity|test_report).

G5: Comparacao entre versoes (fun_report diff)
G6: GIF automatico de gameplay
G7: Relatorio de acessibilidade
G8: Metricas de produtividade
G9: Auto-documentacao de testes
G10: Diff visual entre versoes
"""

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent


# ── G5: Comparacao entre versoes ───────────────────────────────────

def _op_version_diff(params: dict) -> dict:
    """Compara qualidade entre duas versoes salvas (usa version_history).

    Campos em params:
        version_id_a: str — ID da primeira versao
        version_id_b: str — ID da segunda versao (default: atual)
    """
    version_id_a = params.get("version_id_a", "").strip()
    version_id_b = params.get("version_id_b", "").strip()

    if not version_id_a:
        return {"status": "error", "message": "Campo 'version_id_a' obrigatorio."}

    try:
        from tools.version_history_ops import version_history_manage
        versions = version_history_manage(op="list")
        all_versions = {v["version_id"]: v for v in versions.get("versions", [])}

        va = all_versions.get(version_id_a)
        vb = all_versions.get(version_id_b) if version_id_b else {"description": "versao atual", "timestamp": datetime.now(timezone.utc).isoformat()}

        if not va:
            return {"status": "error", "message": f"Versao A '{version_id_a}' nao encontrada."}

        return {
            "status": "success",
            "version_a": {"id": version_id_a, "description": va.get("description", ""), "date": va.get("timestamp", "")},
            "version_b": {"id": version_id_b or "atual", "description": vb.get("description", ""), "date": vb.get("timestamp", "")},
            "recommendation": (
                "Para comparacao completa, rode fun_report_manage op=generate em cada versao "
                "e compare os sinais manualmente. Este diff mostra apenas metadados."
            ),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── G6: GIF automatico ─────────────────────────────────────────────

def _op_record_gif(params: dict) -> dict:
    """Grava screenshots sequenciais durante gameplay para gerar GIF.

    Campos em params:
        duration: int (default 10) — segundos de captura
        fps: int (default 5) — frames por segundo
    """
    duration = params.get("duration", 10)
    fps = params.get("fps", 5)

    if not isinstance(duration, (int, float)) or duration < 1:
        return {"status": "error", "message": "Duracao invalida."}

    duration = int(duration)
    fps = int(fps)
    total_frames = duration * fps

    try:
        from runtime_bridge_client import send_bridge_command
        frames: list[str] = []

        for i in range(total_frames):
            result = send_bridge_command({"cmd": "screenshot"}, timeout=5.0)
            if result.get("ok"):
                frames.append(result.get("image_base64", ""))
            import time
            time.sleep(1.0 / fps)

        return {
            "status": "success",
            "frames_captured": len(frames),
            "total_expected": total_frames,
            "duration_s": duration,
            "fps": fps,
            "frames_base64": frames[:50],  # limita para nao explodir resposta
            "note": (
                f"Capturados {len(frames)}/{total_frames} frames. "
                "Use uma ferramenta externa (ffmpeg, ezgif.com) para converter em GIF. "
                f"Comando ffmpeg: ffmpeg -framerate {fps} -i frame_%d.png output.gif"
            ),
        }
    except Exception as e:
        return {"status": "error", "message": f"Jogo nao esta rodando ou bridge indisponivel: {e}"}


# ── G7: Acessibilidade ─────────────────────────────────────────────

def _op_accessibility(params: dict) -> dict:  # noqa: ARG001
    """Relatorio de acessibilidade basica do projeto.

    Verifica: contraste, fontes, area de toque.
    Essencial para publico nao-programador.
    """
    checks = [
        {
            "check": "Tamanho minimo de fonte",
            "status": "manual",
            "recommendation": "Use fonte >= 14px para legibilidade. Verifique no tema do Godot.",
        },
        {
            "check": "Contraste de texto",
            "status": "manual",
            "recommendation": "Texto claro em fundo escuro ou vice-versa. Use contraste >= 4.5:1.",
        },
        {
            "check": "Area de toque (mobile)",
            "status": "manual",
            "recommendation": "Botoes devem ter pelo menos 44x44px para toque confortavel.",
        },
        {
            "check": "Legendas e audio",
            "status": "manual",
            "recommendation": "Todo dialogo deve ter legenda. Efeitos sonoros devem ter indicacao visual.",
        },
        {
            "check": "Daltonismo",
            "status": "manual",
            "recommendation": "Nao use apenas cor para transmitir informacao. Adicione icones ou texto.",
        },
    ]

    return {
        "status": "success",
        "checks": checks,
        "passed_auto": 0,
        "total": len(checks),
        "message": (
            "Relatorio de acessibilidade gerado. "
            f"{len(checks)} verificacoes — todas requerem inspecao manual. "
            "Acessibilidade e essencial para publico nao-programador."
        ),
    }


# ── G8: Metricas de produtividade ──────────────────────────────────

def _op_productivity(params: dict) -> dict:  # noqa: ARG001
    """Metricas de produtividade do desenvolvedor.

    Mede: tempo em cada fase, iteracoes, taxa de correcao.
    """
    try:
        from tools.phase_ops import get_phase_history
        history = get_phase_history()
        advances = history.get("total_advances", 0)
        current = history.get("current_phase", "desconhecida")
    except Exception:
        advances = 0
        current = "desconhecida"

    return {
        "status": "success",
        "metrics": {
            "phase_advances": advances,
            "current_phase": current,
        },
        "interpretation": (
            f"Voce avancou {advances} vezes de fase e esta em '{current}'. "
            "Cada avanco representa um marco de qualidade atingido. "
            "Continue iterando — jogos sao feitos de iteracoes, nao de genialidade."
        ),
        "tip": (
            "Dica de produtividade: limite sessoes a 2h com pausas. "
            "A qualidade das decisoes cai significativamente apos 4h seguidas."
        ),
    }


# ── G9: Auto-documentacao de testes ────────────────────────────────

def _op_test_report(params: dict) -> dict:  # noqa: ARG001
    """Gera relatorio de teste formatado em markdown."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    report = f"""## Relatorio de Teste — {now}

### Resumo
- **Data:** {now}
- **Ferramenta:** MCP Godot Agent v3.x
- **Tipo:** Teste automatizado

### Resultados
| Teste | Status | Detalhes |
|-------|--------|----------|
| Smoke | ⬜ Nao executado | Rode playtest_manage op=smoke |
| Personas | ⬜ Nao executado | Rode playtest_manage op=persona_run |
| Agente LLM | ⬜ Nao executado | Rode playtest_manage op=agent_run |
| Fun Report | ⬜ Nao executado | Rode fun_report_manage op=generate |

### Conclusao
Testes pendentes. Execute a suite completa:
`playtest_manage op=full_suite`

---
*Relatorio gerado automaticamente pelo MCP Godot Agent.*
"""

    return {
        "status": "success",
        "report_markdown": report,
        "message": "Relatorio de teste gerado em markdown. Cole no seu README ou registro de testes.",
    }


# ── G10: Diff visual entre versoes ─────────────────────────────────

def _op_visual_diff(params: dict) -> dict:
    """Compara screenshots entre duas versoes.

    Campos em params:
        version_id_a: str — versao anterior
        version_id_b: str — versao atual (default: current)
    """
    version_id_a = params.get("version_id_a", "").strip()
    version_id_b = params.get("version_id_b", "").strip()

    if not version_id_a:
        return {"status": "error", "message": "Campo 'version_id_a' obrigatorio."}

    try:
        from tools.version_history_ops import version_history_manage
        versions = version_history_manage(op="list")
        all_versions = {v["version_id"]: v for v in versions.get("versions", [])}

        va = all_versions.get(version_id_a)
        if not va:
            return {"status": "error", "message": f"Versao '{version_id_a}' nao encontrada."}

        has_screenshot_a = va.get("has_screenshot", False)
        has_screenshot_b = False

        if version_id_b:
            vb = all_versions.get(version_id_b)
            has_screenshot_b = vb.get("has_screenshot", False) if vb else False

        return {
            "status": "success",
            "version_a": {"id": version_id_a, "has_screenshot": has_screenshot_a, "path": va.get("screenshot_path", "")},
            "version_b": {"id": version_id_b or "atual", "has_screenshot": has_screenshot_b},
            "can_compare": has_screenshot_a and (has_screenshot_b or not version_id_b),
            "message": (
                "Screenshots disponiveis para comparacao."
                if has_screenshot_a else
                "Versao A nao tem screenshot. Capture com version_history_manage op=screenshot."
            ),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


_POLISH_OPS = {
    "version_diff": _op_version_diff,
    "record_gif": _op_record_gif,
    "accessibility": _op_accessibility,
    "productivity": _op_productivity,
    "test_report": _op_test_report,
    "visual_diff": _op_visual_diff,
}


def polish_manage(op: str, params: dict | None = None) -> dict:
    if op not in _POLISH_OPS:
        return {"status": "error", "message": f"Operacao '{op}' desconhecida.", "available_ops": list(_POLISH_OPS.keys())}
    return _POLISH_OPS[op](params or {})
