"""model_routing.py — Roteamento de Modelo por Tarefa (FATIA 2.AR).

Decide qual modelo de IA usar baseado na complexidade da tarefa.
Tarefa simples → modelo barato/rapido. Diagnostico/auditoria → modelo bom.

Estrategia:
  - Classifica a tarefa por tipo (geracao, analise, critica, meta)
  - Atribui nivel de complexidade (1-5)
  - Sugere o modelo apropriado

Fonte: Pesquisa em tecnicas de model routing (RouteLLM, 2024)
e classificacao de tarefas MCP.
"""

from enum import Enum
from typing import Any


class TaskComplexity(Enum):
    TRIVIAL = 1    # Ping, status, leitura simples
    SIMPLE = 2     # Busca, listagem, validacao
    MODERATE = 3   # Geracao de codigo, edicao
    COMPLEX = 4    # Diagnostico, auditoria, refatoracao
    CRITICAL = 5   # Seguranca, deploy, migracao


# Mapeamento tool → complexidade
_TOOL_COMPLEXITY = {
    # Trivial
    "ping": 1, "health_check": 1, "self_test": 1,
    "read_file": 1, "get_node_property": 1, "list_valid_node_types": 1,
    "take_screenshot": 1, "capture_game_screenshot": 1,
    # Simple
    "search_classdb": 2, "query_classdb": 2, "find_usages": 2,
    "tool_catalog": 2, "tool_groups": 2, "discover_behaviors": 2,
    "validate_gdscript_syntax": 2, "compile_test": 2,
    # Moderate
    "generate_gdscript": 3, "safe_write_gdscript": 3, "write_file": 3,
    "create_scene": 3, "add_node": 3, "set_node_property": 3,
    "script_manage": 3, "scene_manage": 3,
    "generate_game_art": 3, "generate_audio_sfx": 3,
    # Complex
    "audit_input_map": 4, "audit_autoloads": 4, "analyze_signal_flow": 4,
    "validate_project_refs": 4, "run_verification_pipeline": 4,
    "run_stress_test": 4, "run_gut_tests": 4,
    "auditar": 4, "capture_proof": 4,
    # Critical
    "configure_security": 5, "deploy_itch": 5, "build_export": 5,
    "setup_mcp_config": 5, "install_mcp_addon": 5,
}


def classify_task(tool_name: str, description: str = "") -> dict:
    """Classifica a complexidade de uma tarefa.

    Args:
        tool_name: Nome da tool a ser chamada.
        description: Descricao adicional da tarefa.

    Returns:
        dict com nivel de complexidade e modelo sugerido.
    """
    complexity = _TOOL_COMPLEXITY.get(tool_name, 3)  # Default: moderate

    # Ajusta baseado em palavras-chave na descricao
    desc_lower = description.lower()
    if any(kw in desc_lower for kw in ["auditar", "auditoria", "diagnostico", "debug"]):
        complexity = max(complexity, 4)
    if any(kw in desc_lower for kw in ["seguranca", "security", "producao", "deploy"]):
        complexity = max(complexity, 5)

    model = _suggest_model(complexity)

    return {
        "tool": tool_name,
        "complexity": complexity,
        "complexity_label": TaskComplexity(complexity).name,
        "suggested_model": model,
        "message": f"Tarefa {TaskComplexity(complexity).name}. Sugestao: {model}.",
    }


def _suggest_model(complexity: int) -> str:
    if complexity <= 2:
        return "flash (rapido/barato)"
    elif complexity == 3:
        return "pro (balanceado)"
    else:
        return "pro/max (alta qualidade)"


def estimate_cost(tool_calls: list[str]) -> dict:
    """Estima custo total de uma sequencia de chamadas.

    Args:
        tool_calls: Lista de nomes de tools.

    Returns:
        dict com estimativas.
    """
    total = 0
    breakdown = {"trivial": 0, "simple": 0, "moderate": 0, "complex": 0, "critical": 0}

    for tool in tool_calls:
        c = _TOOL_COMPLEXITY.get(tool, 3)
        total += c
        breakdown[TaskComplexity(c).name.lower()] += 1

    return {
        "total_calls": len(tool_calls),
        "complexity_score": total,
        "breakdown": breakdown,
        "suggested_model": _suggest_model(max(_TOOL_COMPLEXITY.get(t, 3) for t in tool_calls)),
    }
