"""_meta_tool.py — Factory de Domain Rollups (Fase 2A / C1).

Colapsa múltiplas tools de um mesmo domínio em uma única tool
<domain>_manage com parâmetro `op` (Literal enum) + `params` dict.

Baseado no padrão hi-godot/godot-ai (`src/godot_ai/tools/_meta_tool.py`).
Estado atual: ~272 definicoes brutas em core/tool_definitions.py, 236 visiveis
apos filtros de fase (189 depreciadas, 80 aliases), ~40 rollups _manage ativos.

Exemplo de uso:
    from _meta_tool import create_manage_tool

    tool_def, handler = create_manage_tool(
        tool_name="scene_manage",
        description="Gerencia cenas Godot (.tscn).",
        ops={
            "create": create_scene,
            "save": save_scene,
            "open": open_scene,
        },
        tool_hints={"destructiveHint": True},
    )
    # Adicione tool_def em _tool_defs() e handler em _build_handlers()
"""

import difflib
from typing import Callable

from mcp.types import Tool


# ── Hints válidos (C4) ─────────────────────────────────────────────

_VALID_HINTS = {"readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"}


# ── Factory Principal ───────────────────────────────────────────────

def create_manage_tool(
    *,
    tool_name: str,
    description: str,
    ops: dict[str, Callable[..., dict]],
    tool_hints: dict[str, bool] | None = None,
    title: str | None = None,
    tags: list[str] | None = None,
) -> tuple[Tool, Callable[[dict], dict]]:
    """Cria uma tool <domain>_manage que despacha por `op` name.

    Args:
        tool_name: Nome da tool (ex: "scene_manage").
        description: Descrição base para a IA (as operações são
                     listadas automaticamente no final).
        ops: Dicionário {nome_do_op: função_handler}.
             Cada função recebe **params (os campos dentro de
             `params`) e retorna um dict com pelo menos "status".
        tool_hints: Opcional. Dict com até 4 hints:
                    {"readOnlyHint", "destructiveHint",
                     "idempotentHint", "openWorldHint"}.
        title: Título amigável (ex: "Gerenciar Cenas").
        tags: Lista de tags para anotações (ex: ["cena", "godot"]).

    Returns:
        Tuple de (Tool definition, handler function).
        - Tool definition: objeto `mcp.types.Tool` pronto para
          ser incluído na lista de _tool_defs().
        - Handler function: função `(args: dict) -> dict` pronta
          para ser incluída no dicionário de _build_handlers().

    O parâmetro `op` é validado contra a lista de operações.
    Se o op não for encontrado, o handler retorna sugestões
    usando difflib.get_close_matches.
    """

    op_names = list(ops.keys())

    # ── Extrai descrições das docstrings ────────────────────────
    op_descriptions: dict[str, str] = {}
    for op_name, fn in ops.items():
        doc = (fn.__doc__ or "").strip()
        first_line = doc.split("\n")[0].rstrip(".")
        op_descriptions[op_name] = first_line if first_line else f"Executa '{op_name}'"

    # ── Monta descrição completa ────────────────────────────────
    ops_list = "\n".join(
        f"- **{name}**: {desc}" for name, desc in op_descriptions.items()
    )
    full_description = (
        f"{description}\n\n"
        f"Operações disponíveis (use o parâmetro `op`):\n"
        f"{ops_list}\n\n"
        f"Passe os argumentos da operação dentro do dicionário `params`. "
        f"Se errar o nome do `op`, o sistema sugere automaticamente "
        f"as operações mais próximas."
    )

    # ── Schema de input ─────────────────────────────────────────
    input_schema = {
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "enum": op_names,
                "description": (
                    f"Operação a executar. Valores válidos: "
                    f"{', '.join(op_names)}."
                ),
            },
            "params": {
                "type": "object",
                "description": (
                    "Parâmetros da operação. Cada op espera campos "
                    "específicos — consulte a descrição da tool para "
                    "saber quais campos são necessários para cada op."
                ),
                "additionalProperties": True,
            },
        },
        "required": ["op"],
        "additionalProperties": False,
    }

    # ── Cria definição da tool ──────────────────────────────────
    tool_def = Tool(
        name=tool_name,
        description=full_description,
        inputSchema=input_schema,
    )

    # ── Aplica hints DENTRO de annotations (spec MCP) ───────────
    from mcp.types import ToolAnnotations

    # Constrói ToolAnnotations com os hints fornecidos + defaults seguros
    ann_kwargs: dict = {}
    if tool_hints:
        for hint_name, hint_value in tool_hints.items():
            if hint_name not in _VALID_HINTS:
                raise ValueError(
                    f"Hint inválido: '{hint_name}'. "
                    f"Hints válidos: {sorted(_VALID_HINTS)}"
                )
            ann_kwargs[hint_name] = hint_value

    # Preenche defaults para hints não fornecidos (spec: readOnly=false, destructive=true)
    for hint_name in _VALID_HINTS:
        if hint_name not in ann_kwargs:
            # Defaults spec: readOnlyHint=False, destructiveHint=True,
            # idempotentHint=False, openWorldHint=True
            if hint_name == "destructiveHint":
                ann_kwargs[hint_name] = True
            elif hint_name == "openWorldHint":
                ann_kwargs[hint_name] = True
            else:
                ann_kwargs[hint_name] = False

    tool_def.annotations = ToolAnnotations(**ann_kwargs)

    # ── Aplica título ──────────────────────────────────────────
    if title:
        tool_def.title = title

    # ── Tags: armazenadas em meta (NÃO em annotations — campo fora da spec) ──
    if tags:
        tool_def.meta = {"tags": tags}

    # ── Handler (delega para build_manage_handler) ──────────────
    def handler(args: dict) -> dict:
        """Despacha `op` para a função correspondente.

        Args:
            args: Dicionário com as chaves:
                  - op (str): Nome da operação.
                  - params (dict, opcional): Parâmetros da operação.

        Returns:
            dict com pelo menos "status" ("success" ou "error").
        """
        return build_manage_handler(args, ops)

    return tool_def, handler


# ── Helpers de Conveniência ─────────────────────────────────────────

def register_manage_tool(
    tool_defs_list: list[Tool],
    handlers_dict: dict[str, Callable[[dict], dict]],
    *,
    tool_name: str,
    description: str,
    ops: dict[str, Callable[..., dict]],
    tool_hints: dict[str, bool] | None = None,
    title: str | None = None,
    tags: list[str] | None = None,
) -> None:
    """Registra uma manage tool in-place nas listas do server.

    Helper de conveniência que cria a tool com create_manage_tool()
    e já adiciona nas listas de tool_defs e handlers.

    Args:
        tool_defs_list: Lista de Tool definitions (modificada in-place).
        handlers_dict: Dicionário de handlers (modificado in-place).
        tool_name: Nome da tool.
        description: Descrição base.
        ops: Handlers por operação.
        tool_hints: Hints opcionais.
        title: Título amigável opcional.
        tags: Tags opcionais.
    """
    tool_def, handler = create_manage_tool(
        tool_name=tool_name,
        description=description,
        ops=ops,
        tool_hints=tool_hints,
        title=title,
        tags=tags,
    )
    tool_defs_list.append(tool_def)
    handlers_dict[tool_name] = handler


# ── Função de Build Auxiliar ────────────────────────────────────────

def build_manage_handler(args: dict, ops: dict[str, Callable[..., dict]]) -> dict:
    """Handler genérico para manage tools — lógica central de dispatch.

    Usado tanto pelo handler interno de create_manage_tool() quanto
    standalone para ferramentas que precisam de lógica adicional
    antes/depois do dispatch.

    Args:
        args: Dicionário com 'op' (str) e 'params' (dict, opcional).
        ops: Dicionário {nome_do_op: função_handler}.

    Returns:
        dict com pelo menos "status" ("success" ou "error").
    """
    op = args.get("op", "")
    params: dict = args.get("params") or {}
    op_names = list(ops.keys())

    # ── Validação do op ─────────────────────────────────────
    if op not in ops:
        suggestions = difflib.get_close_matches(op, op_names, n=3, cutoff=0.4)
        return {
            "status": "error",
            "message": (
                f"Operação desconhecida: '{op}'."
                + (
                    f" Você quis dizer: {suggestions}?"
                    if suggestions
                    else f" Valores válidos: {op_names}"
                )
            ),
            "suggestions": suggestions,
            "valid_ops": op_names,
        }

    # ── Execução ─────────────────────────────────────────────
    try:
        result = ops[op](**params)
        # Garante status sem modificar o dict original (evita efeito colateral)
        if isinstance(result, dict):
            if "status" not in result:
                result = dict(result, status="success")
        else:
            result = {"status": "success", "data": result}
        return result
    except TypeError as e:
        return {
            "status": "error",
            "message": (
                f"Parâmetros inválidos para '{op}': {e}. "
                f"Verifique os campos esperados dentro de `params`."
            ),
            "op": op,
            "error_detail": str(e),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao executar '{op}': {e}",
            "op": op,
            "error_detail": str(e),
        }
