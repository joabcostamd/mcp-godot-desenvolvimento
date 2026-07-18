"""kill_switch.py — Kill Switch por Feature (Fatia 0.12).

Sistema de feature flags que permite desligar features individuais
independente do filtro de fase. Segundo eixo de controle.

Uso:
    from tools.kill_switch import disable_feature, enable_feature,
        is_feature_enabled, get_disabled_tools

    disable_feature("idempotency_audit")  # desliga feature
    enable_feature("idempotency_audit")   # religa
    is_feature_enabled("idempotency_audit")  # True/False
    get_disabled_tools()  # set de tool names a filtrar
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("mcp-godot.kill_switch")

# ── Registro: feature → tools MCP que ela expõe ─────────────────────
# Features de infraestrutura (sem tools visíveis) têm set() vazio.
# Toda feature nova das camadas seguintes DEVE adicionar entrada aqui.
FEATURE_TOOLS: dict[str, set[str]] = {
    # Fatias concluídas da Camada 0
    "idempotency_audit": {"audit_tool_idempotency"},
    "budget_gate": set(),          # CI apenas
    "contract_snapshot": set(),    # CI apenas
    "loopback_bind": set(),        # Infra de bind de rede
    "git_safety": set(),           # Infra de checkpoint git
    "secret_scan": set(),          # Infra de scan de segredo
    "governor": set(),             # Infra de governador (0.14)
    # Fatias 0.11+ (adicionar conforme forem implementadas)
    "kill_switch": set(),          # Esta própria feature
}


def _get_project_root() -> Path | None:
    """Retorna a raiz do projeto ativo ou None."""
    try:
        from tools.project_ops import _get_active_project
        proj = _get_active_project()
        if proj:
            return Path(proj)
    except Exception:
        pass
    return None


def _get_state_path() -> Path | None:
    """Retorna o caminho do arquivo de estado do kill switch."""
    root = _get_project_root()
    if root is None:
        return None
    return root / ".mcp_kill_switch.json"


def _load_state() -> dict[str, bool]:
    """Carrega o estado do killed switch do disco.

    Returns:
        {feature_name: desligada (True) ou ligada (False)}
        Features não listadas são consideradas ligadas.
    """
    state_path = _get_state_path()
    if state_path is None or not state_path.exists():
        return {}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        logger.warning("Falha ao ler kill_switch state")
        return {}


def _save_state(state: dict[str, bool]) -> None:
    """Salva estado do kill switch em disco."""
    state_path = _get_state_path()
    if state_path is None:
        return
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:
        logger.exception("Falha ao salvar kill_switch state")


def is_feature_enabled(feature_name: str) -> bool:
    """Verifica se uma feature está habilitada.

    Args:
        feature_name: Nome da feature (chave em FEATURE_TOOLS).

    Returns:
        True se habilitada (default), False se desabilitada.
    """
    state = _load_state()
    return not state.get(feature_name, False)


def disable_feature(feature_name: str) -> dict:
    """Desabilita uma feature (suas tools somem de _tool_defs()).

    Args:
        feature_name: Nome da feature (chave em FEATURE_TOOLS).

    Returns:
        dict com status, feature, message.
    """
    if feature_name not in FEATURE_TOOLS:
        return {
            "status": "error",
            "feature": feature_name,
            "message": f"Feature '{feature_name}' desconhecida. "
                       f"Features válidas: {', '.join(sorted(FEATURE_TOOLS.keys()))}",
        }

    state = _load_state()
    state[feature_name] = True  # True = desligada
    _save_state(state)

    tools_affected = FEATURE_TOOLS[feature_name]
    if tools_affected:
        _schedule_cache_invalidation()

    return {
        "status": "success",
        "feature": feature_name,
        "enabled": False,
        "tools_removed": sorted(tools_affected) if tools_affected else [],
        "message": f"Feature '{feature_name}' desabilitada.{' Tools removidas: ' + ', '.join(sorted(tools_affected)) if tools_affected else ''}",
    }


def enable_feature(feature_name: str) -> dict:
    """Reabilita uma feature (suas tools reaparecem em _tool_defs())."""
    if feature_name not in FEATURE_TOOLS:
        return {
            "status": "error",
            "feature": feature_name,
            "message": f"Feature '{feature_name}' desconhecida. "
                       f"Features válidas: {', '.join(sorted(FEATURE_TOOLS.keys()))}",
        }

    state = _load_state()
    state.pop(feature_name, None)  # Remove do estado = ligada
    _save_state(state)

    tools_affected = FEATURE_TOOLS[feature_name]
    if tools_affected:
        _schedule_cache_invalidation()

    return {
        "status": "success",
        "feature": feature_name,
        "enabled": True,
        "tools_restored": sorted(tools_affected) if tools_affected else [],
        "message": f"Feature '{feature_name}' reabilitada.",
    }


def get_disabled_tools() -> set[str]:
    """Retorna o conjunto de tools MCP a serem ocultadas.

    União de todas as tools de features desabilitadas.
    """
    state = _load_state()
    disabled_tools: set[str] = set()
    for feature_name, disabled in state.items():
        if disabled:
            tools = FEATURE_TOOLS.get(feature_name, set())
            disabled_tools.update(tools)
    return disabled_tools


def list_features() -> dict:
    """Lista todas as features com seu estado atual."""
    state = _load_state()
    result = {}
    for name in sorted(FEATURE_TOOLS.keys()):
        enabled = not state.get(name, False)
        result[name] = {
            "enabled": enabled,
            "tools": sorted(FEATURE_TOOLS[name]) if FEATURE_TOOLS[name] else [],
        }
    return result


def _schedule_cache_invalidation() -> None:
    """Invalida caches das ferramentas para que o filtro se aplique."""
    try:
        import server as _srv
        _srv._invalidate_tool_caches()
    except Exception:
        pass


# ── MCP Tools (expostas como op em safety_manage ou standalone) ────
# NÃO adicionar tools MCP de topo — estas funções são chamadas
# internamente ou expostas como ops de rollup.