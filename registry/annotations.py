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


# ── ONDA 2.2: Validação strict (campos extra) ─────────────────

# Campos oficiais da spec MCP ToolAnnotations
_MCP_SPEC_FIELDS = {"readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint", "title"}


def list_extra_fields(tool: Tool) -> list[str]:
    """Lista campos nas annotations que não são da spec MCP.

    Campos como 'tags', 'operationCategory', 'deferLoading' são
    extensões do projeto — não são erro, mas devem ser documentados.
    """
    ann = tool.annotations
    if ann is None or not isinstance(ann, ToolAnnotations):
        return []
    # Pega campos setados via __setattr__ (model_extra do Pydantic)
    extra = getattr(ann, 'model_extra', None) or {}
    # Filtra internos do Pydantic
    return sorted(k for k in extra if not k.startswith('model_') and k not in _MCP_SPEC_FIELDS)


def audit_extra_fields(tools: list[Tool]) -> dict[str, list[str]]:
    """Audita campos extra nas annotations de todas as tools.

    Returns:
        Dict {tool_name: [campos_extra]}. Vazio = todas conformes à spec.
    """
    result: dict[str, list[str]] = {}
    for tool in tools:
        extra = list_extra_fields(tool)
        if extra:
            result[tool.name] = extra
    return result
