"""hook_stop.py — Hook Stop da Feature 7.

Bloqueia encerramento de sessao se houver gate falho ativo no projeto.
Formato EARS obrigatorio para liberar encerramento com gate falho.

Uso:
    python tools/hook_stop.py '<json_input>'

JSON de entrada:
    {"stop_hook_active": false, "session_id": "..."}

Exit codes:
    0 — encerramento permitido (gate limpo ou stop_hook_active=true)
    2 — encerramento BLOQUEADO (gate falho ativo, requer correcao)
"""

import json
import sys
from pathlib import Path

GATE_MARKER = ".mcp_gate_failed"


def _run_reachability_audit_on_stop(proj: Path) -> None:
    """Executa auditoria de alcançabilidade no encerramento da sessão.
    Não bloqueia — apenas imprime aviso se houver cenas órfãs."""
    try:
        from tools.audit_scene_reachability import audit_scene_reachability
        result = audit_scene_reachability(project_path=str(proj))
        if result.get("status") == "issues_found":
            unreachable = result.get("unreachable_scenes", [])
            if unreachable:
                print()
                print("-" * 70)
                print("  AUDITORIA DE ALCANÇABILIDADE")
                print(f"  {len(unreachable)} cena(s) órfã(s) detectada(s):")
                for scene in unreachable[:10]:  # máximo 10 para não poluir
                    print(f"    • {scene}")
                if len(unreachable) > 10:
                    print(f"    ... e mais {len(unreachable) - 10} cenas.")
                print(f"  Rode audit_scene_reachability para detalhes completos.")
                print("-" * 70)
        elif result.get("status") == "ambiguous":
            pass  # Sem main_scene definida — não é erro
    except Exception:
        pass  # Falha na auditoria não bloqueia encerramento


def _get_active_project() -> Path | None:
    """Resolve o projeto ativo via project_ops."""
    try:
        from tools.project_ops import _get_active_project
        proj = _get_active_project()
        if proj and proj.exists():
            return proj
    except Exception:
        pass
    return None


def main() -> int:
    # ── Parse JSON de entrada ──
    input_str = sys.argv[1] if len(sys.argv) > 1 else "{}"
    try:
        data = json.loads(input_str)
    except json.JSONDecodeError:
        data = {}

    # ── Guarda anti-loop: stop_hook_active=true → sai imediatamente ──
    if data.get("stop_hook_active") is True:
        return 0

    # ── Resolver projeto ativo ──
    proj = _get_active_project()
    if not proj:
        # Sem projeto ativo definido → nada a verificar
        return 0

    # ── Verificar marcador de gate falho ──
    marker_path = proj / GATE_MARKER
    if not marker_path.exists():
        # ── Auditoria de alcançabilidade (NÃO bloqueante) ──
        _run_reachability_audit_on_stop(proj)
        return 0

    # ── Gate falho ativo: ler razao e bloquear ──
    reason = ""
    try:
        reason = marker_path.read_text(encoding="utf-8").strip()
    except Exception:
        reason = "(erro ao ler marcador)"

    print("=" * 70)
    print("  GATE DE VERIFICACAO FALHOU — ENCERRAMENTO BLOQUEADO")
    print("=" * 70)
    print(f"  Projeto: {proj}")
    print(f"  Marcador: {marker_path}")
    print(f"  Motivo:   {reason}")
    print()
    print("  Antes de encerrar a sessao, corrija o problema e rode:")
    print(f"    Remove-Item '{marker_path}'")
    print()
    print("  Ou, se o risco for aceito, registre o relatorio EARS abaixo")
    print("  e remova o marcador manualmente:")
    print()
    print("  WHEN <tool> executed ON <file>,")
    print("  THE SYSTEM <passed|failed> IN <check_type>,")
    print("  SHALL <consequence> IF <risk_condition>.")
    print()
    print("  Exemplo:")
    print("  WHEN _validate_gdscript_post_write executed ON scenes/enemy.gd,")
    print("  THE SYSTEM failed IN syntax_check,")
    print("  SHALL crash at runtime IF the script is loaded without fixing line 15.")
    print("=" * 70)

    return 2


if __name__ == "__main__":
    sys.exit(main())
