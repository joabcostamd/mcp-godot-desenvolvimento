"""domains/runtime/manifest.py — Manifesto do domínio runtime (F5.13)."""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="runtime",
    tool_name="runtime_manage",
    title="Gerenciar Runtime",
    namespace="project",
    version="1.0.0",
    description=(
        "Gerencia execução do Godot: compilar, rodar, parar, reiniciar, abrir/fechar editor.\n"
        "QUANDO USAR: para controlar o ciclo de vida do jogo e editor durante desenvolvimento.\n"
        "QUANDO NÃO USAR: para debug (use debug_manage), para executar GDScript (use godot_manage).\n"
        "PRÉ-CONDIÇÕES: Godot instalado, projeto ativo configurado com set_active_project.\n"
        "ERRO COMUM: projeto não encontrado — verifique se o projeto ativo tem project.godot."
    ),
    phases=[Phase.PROTOTIPO],
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[
        OpSpec(name="compile", fn=handlers.compile_test, summary="Executa compile_test no projeto ativo (--headless --quit)",
               schema={}, examples=[{}], rollback=None),
        OpSpec(name="run", fn=handlers.run_game, summary="Inicia o jogo como subprocesso (não bloqueante)",
               schema={"scene_path": {"type": "string", "required": False, "description": "Cena opcional"}, "wait_for_bridge": {"type": "boolean", "required": False, "description": "Aguardar bridge (default true)"}},
               examples=[{"wait_for_bridge": True}], rollback=None),
        OpSpec(name="stop", fn=handlers.stop_game, summary="Encerra o jogo em execução e retorna tail do console",
               schema={}, examples=[{}], rollback=None),
        OpSpec(name="restart", fn=handlers.smart_restart, summary="Reinício inteligente: stop → copia addon → compila → inicia → conecta bridge",
               schema={"project_path": {"type": "string", "required": False, "description": "Caminho do projeto"}},
               examples=[{}], rollback=None),
        OpSpec(name="launch_editor", fn=handlers.launch_editor, summary="Abre o editor Godot com o addon mcp_addon instalado",
               schema={"scene_path": {"type": "string", "required": False, "description": "Cena opcional para abrir"}},
               examples=[{}], rollback=None),
        OpSpec(name="close_editor", fn=handlers.close_editor, summary="Fecha o editor Godot",
               schema={}, examples=[{}], rollback=None),
    ],
    tags=["runtime", "godot", "execução"],
)
