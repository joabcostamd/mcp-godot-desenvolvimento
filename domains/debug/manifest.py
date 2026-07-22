"""domains/debug/manifest.py — Manifesto do domínio debug (F5.9).

Migração concluída em 2026-07-21.
"""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="debug",
    tool_name="debug_manage",
    title="Gerenciar Debug",
    namespace="project",
    version="1.0.0",
    description=(
        "Gerencia debug: performance, visualização de colisões/navegação, breakpoints, stack e variáveis.\n"
        "QUANDO USAR: para diagnosticar performance, depurar código com breakpoints, inspecionar variáveis.\n"
        "QUANDO NÃO USAR: para testes automatizados (use test_manage), para profiling (use profile_frame).\n"
        "PRÉ-CONDIÇÕES: para debugger, o jogo deve rodar com --debug (porta 6006).\n"
        "ERRO COMUM: debugger indisponível — rode o jogo com F5 (Play Debug) ou godot --debug."
    ),
    phases=[Phase.POLIMENTO],
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
    ops=[
        OpSpec(
            name="perf_stats",
            fn=handlers.get_performance_stats,
            summary="Obtém estatísticas de performance (FPS, memória, draw calls)",
            schema={},
            examples=[{}],
            rollback=None,
        ),
        OpSpec(
            name="collision_debug",
            fn=handlers.enable_debug_collisions,
            summary="Ativa/desativa visualização de debug de colisões",
            schema={
                "enabled": {"type": "boolean", "required": False, "description": "Ativar (true) ou desativar (false)"},
            },
            examples=[{"enabled": True}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="nav_debug",
            fn=handlers.enable_debug_navigation,
            summary="Ativa/desativa visualização de debug de navegação",
            schema={
                "enabled": {"type": "boolean", "required": False, "description": "Ativar ou desativar"},
            },
            examples=[{"enabled": True}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="perf_regression",
            fn=handlers.perf_regression_track,
            summary="Registra métricas de performance para detecção de regressão",
            schema={
                "args": {"type": "object", "required": False, "description": "Parâmetros de tracking"},
            },
            examples=[{}],
            rollback=None,
        ),
        OpSpec(
            name="set_breakpoint",
            fn=handlers.debugger_set_breakpoint,
            summary="Define um breakpoint em um script (requer debugger na porta 6006)",
            schema={
                "script_path": {"type": "string", "required": True, "description": "Caminho do script (ex: res://scripts/player.gd)"},
                "line": {"type": "integer", "required": True, "description": "Número da linha"},
                "condition": {"type": "string", "required": False, "description": "Condição opcional (ex: health < 10)"},
            },
            examples=[{"script_path": "res://scripts/player.gd", "line": 42}],
            rollback=None,
        ),
        OpSpec(
            name="status",
            fn=handlers.debugger_status,
            summary="Verifica estado do debugger (disponível, host, porta 6006)",
            schema={},
            examples=[{}],
            rollback=None,
        ),
        OpSpec(
            name="step",
            fn=handlers.debugger_step,
            summary="Avança execução: over (próxima linha), into (entrar função), out (sair)",
            schema={
                "step_type": {"type": "string", "required": False, "description": "over, into ou out"},
            },
            examples=[{"step_type": "over"}],
            rollback=None,
        ),
        OpSpec(
            name="get_stack",
            fn=handlers.debugger_get_stack,
            summary="Obtém stack trace atual do debugger",
            schema={},
            examples=[{}],
            rollback=None,
        ),
        OpSpec(
            name="get_vars",
            fn=handlers.debugger_get_variables,
            summary="Inspeciona variáveis no escopo atual do debugger",
            schema={
                "variable_name": {"type": "string", "required": False, "description": "Nome da variável (None = todas)"},
            },
            examples=[{"variable_name": "health"}],
            rollback=None,
        ),
    ],
    tags=["debug", "diagnóstico", "visualização", "debugger"],
)
