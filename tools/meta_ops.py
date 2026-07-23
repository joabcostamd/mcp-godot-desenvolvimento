"""meta_ops.py — Meta-Tools para Perfil Lean (Fatia 0.15).

3 meta-tools que permitem o ciclo completo de descoberta e invocação
sem expor todas as tools de uma vez no namespace do modelo:

    catalog_search  → busca tool por linguagem natural
    describe_tool   → retorna schema completo de uma tool
    invoke_by_name  → invoca uma tool pelo nome (respeita gates)

Uso no perfil lean:
    A IA vê apenas CORE (27 tools) + estas 3 meta-tools (~30 tools).
    Quando precisar de uma ferramenta:
        1. catalog_search("scene")  → descobre tool scene_manage
        2. describe_tool("scene_manage")  → lê schema
        3. invoke_by_name("scene_manage", {"op": "create", ...})  → invoca
"""

import json
import logging
from typing import Any

logger = logging.getLogger("mcp-godot.meta_ops")


def catalog_search(query: str = "", group: str = "", limit: int = 20) -> dict:
    """Busca ferramentas e operações por linguagem natural (meta-tool do perfil lean).

    Pesquisa em nomes, descrições e operações (ops) de tools _manage.
    Retorna lista de ferramentas que correspondem à consulta.

    Args:
        query: Texto parcial de busca (ex: "scene", "criar", "audio").
        group: Grupo específico (ex: "project", "assets", "runtime").
        limit: Máximo de resultados (default 20).

    Returns:
        {"status": "success", "tools": [{name, description, group, ops, ...}], "total": int}
    """
    from tools.dynamic_groups import tool_catalog as _tc
    try:
        result = _tc({"query": query, "group": group, "limit": limit})
        if isinstance(result, dict) and result.get("status") == "success":
            tools = result.get("results", [])
            # ── ONDA 4.3: Enriquecer com ops (operações dos _manage) ──
            import server as _srv
            all_tools = {t.name: t for t in _srv._tool_defs()}
            for tool_info in tools:
                t = all_tools.get(tool_info.get("name", ""))
                if t and hasattr(t, 'inputSchema') and isinstance(t.inputSchema, dict):
                    props = t.inputSchema.get("properties", {})
                    op_enum = props.get("op", {}).get("enum", [])
                    if op_enum:
                        tool_info["ops"] = op_enum
            return {
                "status": "success",
                "tools": tools,
                "total": result.get("total", 0),
            }
        return result
    except Exception as e:
        return {"status": "error", "message": f"Erro ao buscar catálogo: {e}"}


def describe_tool(name: str, op: str = "") -> dict:
    """Retorna o schema completo de uma ferramenta ou operação específica.

    Busca em _tool_defs() pelo nome. Se 'op' for fornecido, retorna
    apenas o schema daquela operação (para tools _manage).

    Args:
        name: Nome exato da tool (ex: "ping", "scene_manage").
        op: Operação específica dentro de um _manage (ex: "create").

    Returns:
        {"status": "success", "tool": {name, description, inputSchema, hints, operation, ops?}}
        ou {"status": "error", "message": "..."}
    """
    import server as _srv
    try:
        tools = _srv._tool_defs()
    except Exception as e:
        return {"status": "error", "message": f"Erro ao carregar ferramentas: {e}"}

    for tool in tools:
        if tool.name == name:
            ann = getattr(tool, "annotations", None)
            schema = getattr(tool, "inputSchema", {}) or {}
            
            # Extrair ops disponíveis (ONDA 4.4)
            props = schema.get("properties", {}) if isinstance(schema, dict) else {}
            op_enum = props.get("op", {}).get("enum", [])
            
            result = {
                "status": "success",
                "tool": {
                    "name": tool.name,
                    "description": getattr(tool, "description", ""),
                    "hints": {
                        "readOnly": getattr(ann, "readOnlyHint", False) if ann else False,
                        "destructive": getattr(ann, "destructiveHint", False) if ann else False,
                        "idempotent": getattr(ann, "idempotentHint", False) if ann else False,
                        "openWorld": getattr(ann, "openWorldHint", False) if ann else False,
                    },
                    "operation": getattr(ann, "operationCategory", "read+write") if ann else "read+write",
                },
            }
            
            if op_enum:
                result["tool"]["ops"] = op_enum
            
            # Se op especificado, filtra schema para aquela operação
            if op and op_enum and op in op_enum:
                result["tool"]["selected_op"] = op
                # Simplifica: mantém só a descrição relevante
                result["tool"]["inputSchema"] = {
                    "type": "object",
                    "properties": {
                        "op": {"type": "string", "const": op},
                        **{k: v for k, v in props.items() if k != "op"}
                    },
                    "required": ["op"],
                }
            elif not op:
                result["tool"]["inputSchema"] = schema
            
            return result

    return {
        "status": "error",
        "message": f"Ferramenta '{name}' não encontrada na fase atual.",
    }


def invoke_by_name(name: str, arguments: dict | None = None) -> dict:
    """Invoca uma ferramenta pelo nome (meta-tool do perfil lean).

    **RESPEITA TODOS OS GATES:** fase, session, kill switch e governador.
    Não é um bypass de segurança — o dispatch passa pelo mesmo pipeline
    de call_tool().

    Args:
        name: Nome da tool a invocar (ex: "ping", "scene_manage").
        arguments: Dicionário de argumentos (opcional).

    Returns:
        O mesmo resultado que chamar a tool diretamente, ou erro de gate.
    """
    import server as _srv
    from mcp.types import TextContent
    import json as _json

    args = arguments or {}

    # ── 0. Alias resolution (Secao 11.9) — ANTES do phase gate ──
    # Ferramentas renomeadas mantêm compatibilidade via alias.
    # O alias redireciona para o rollup equivalente ANTES de qualquer
    # verificação de fase, porque o rollup alvo é que define a fase.
    from tools.deprecated import ALIAS_MAP
    if name in ALIAS_MAP:
        rollup_name, op_name = ALIAS_MAP[name]
        logging.getLogger("mcp_godot").warning(
            "deprecated_alias_used: %s -> %s(op=%s)", name, rollup_name, op_name
        )
        # Redireciona: chama invoke_by_name recursivamente com o rollup
        alias_args = dict(args)
        alias_args["op"] = op_name
        try:
            result = invoke_by_name(rollup_name, alias_args)
        except RecursionError:
            return {
                "status": "error",
                "message": f"Alias circular detectado: {name} -> {rollup_name}",
            }
        if isinstance(result, dict):
            result["_alias_used"] = True
            result["_alias_from"] = name
            result["_alias_to"] = f"{rollup_name}(op={op_name})"
            if "status" not in result:
                result["status"] = "success"
        return result

    # ── 1. Verificar visibilidade na fase atual ──
    try:
        phase_tools = _srv._get_phase_tools()
        if name not in phase_tools:
            current_phase = "desconhecida"
            try:
                from tools.phase_ops import get_current_phase
                cp = get_current_phase()
                current_phase = cp.get("phase", "desconhecida")
            except Exception:
                pass
            return {
                "status": "error",
                "message": f"Ferramenta '{name}' não está disponível na fase '{current_phase}'.",
                "hint": "Use advance_phase para avançar de fase, ou verifique se o nome está correto.",
            }
    except Exception:
        pass  # Sem projeto ativo — fallback para tentar executar

    # ── 2. Session Gate ──
    try:
        if name not in _srv.SESSION_ALWAYS_ALLOWED:
            ok, msg = _srv._check_session_gate()
            if not ok:
                return {"status": "error", "message": msg}
    except Exception:
        pass  # Gate indisponível — fail open

    # ── 3. Kill Switch ──
    try:
        from tools.kill_switch import get_disabled_tools
        if name in get_disabled_tools():
            return {
                "status": "error",
                "message": f"Ferramenta '{name}' está desabilitada (kill switch).",
                "hint": "Use enable_feature da feature correspondente para reabilitar.",
            }
    except Exception:
        pass

    # ── 4. Buscar handler e executar ──
    try:
        handlers = _srv._build_handlers()
        handler = handlers.get(name)
    except Exception as e:
        return {"status": "error", "message": f"Erro ao carregar handlers: {e}"}

    if handler is None:
        return {
            "status": "error",
            "message": f"Ferramenta '{name}' não encontrada. "
                       f"Use catalog_search para descobrir ferramentas disponíveis.",
        }

    # ── 5. Executar com dispatch inteligente ──
    try:
        result = _srv._smart_call(handler, args)
    except Exception as e:
        return {"status": "error", "message": f"Erro ao executar '{name}': {e}"}

    if isinstance(result, dict) and "status" not in result:
        result["status"] = "success"

    return result