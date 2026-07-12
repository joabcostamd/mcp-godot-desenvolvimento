"""set_auto_dismiss — Liga/desliga o fechamento automático de diálogos
modais durante testes automatizados, via Runtime Bridge (TCP 8790).

Feature: Grupo C — Auto-dismiss de diálogo modal.
"""

from runtime_bridge_client import send_bridge_command, BridgeUnavailable


def set_auto_dismiss(
    enabled: bool = True,
    action: str = "hide",
    check_interval_ms: int = 500,
) -> dict:
    """Ativa/desativa o auto-dismiss de AcceptDialog/ConfirmationDialog
    durante o jogo rodando. Use antes de testes longos automatizados
    (run_stress_test, run_scripted_tests) para não travar em popups.

    Args:
        enabled: True para ativar, False para desativar.
        action: "confirm" (emite confirmed), "cancel" (emite canceled), "hide" (só esconde).
        check_interval_ms: Intervalo entre verificações em ms.
    """
    if action not in ("confirm", "cancel", "hide"):
        return {"status": "error", "message": f"action inválida: '{action}'. Use confirm/cancel/hide."}

    try:
        result = send_bridge_command({
            "cmd": "custom",
            "name": "set_auto_dismiss",
            "args": {
                "enabled": enabled,
                "action": action,
                "check_interval_ms": check_interval_ms,
            },
        })
        return {"status": "success", **result}
    except BridgeUnavailable:
        return {
            "status": "error",
            "message": "Jogo não está rodando em debug — auto-dismiss requer o jogo ativo via godot_run_project.",
        }
