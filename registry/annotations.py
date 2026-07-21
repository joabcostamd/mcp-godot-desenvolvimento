"""registry/annotations.py — Valida e constrói ToolAnnotations (Fase 2.2).

Garante que toda tool tenha anotações conformes à spec MCP:
apenas os 5 campos oficiais de ToolAnnotations.
"""

from __future__ import annotations

from mcp.types import ToolAnnotations, Tool


def validate_annotations(tool: Tool) -> list[str]:
    """Valida as anotações de uma tool contra a spec.

    Returns:
        Lista de problemas encontrados (vazia = tool conforme).
    """
    problems: list[str] = []

    ann = tool.annotations
    if ann is None:
        problems.append(f"{tool.name}: annotations é None")
        return problems

    # Verifica tipo
    if not isinstance(ann, ToolAnnotations):
        problems.append(
            f"{tool.name}: annotations é {type(ann).__name__}, "
            f"deveria ser ToolAnnotations"
        )
        return problems

    # Verifica hints obrigatórios
    for hint in ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"):
        if getattr(ann, hint, None) is None:
            problems.append(f"{tool.name}: {hint} não definido")

    return problems


def create_annotations(
    read_only: bool = False,
    destructive: bool = True,
    idempotent: bool = False,
    open_world: bool = False,
) -> ToolAnnotations:
    """Cria ToolAnnotations com valores explícitos (sem campos extras)."""
    return ToolAnnotations(
        readOnlyHint=read_only,
        destructiveHint=destructive,
        idempotentHint=idempotent,
        openWorldHint=open_world,
    )


# Validação em lote
def validate_all(tools: list[Tool]) -> dict[str, list[str]]:
    """Valida anotações de todas as tools.

    Returns:
        Dict {tool_name: [problemas]}. Vazio = todas conformes.
    """
    result: dict[str, list[str]] = {}
    for tool in tools:
        problems = validate_annotations(tool)
        if problems:
            result[tool.name] = problems
    return result
