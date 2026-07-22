"""domains/godot/manifest.py — Manifesto do domínio godot (F5.11)."""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="godot",
    tool_name="godot_manage",
    title="Gerenciar Execução Godot",
    namespace="project",
    version="1.0.0",
    description=(
        "Gerencia a execução do Godot: rodar/parar projeto, executar GDScript, "
        "obter runtime info, esperar bridge.\n"
        "QUANDO USAR: para controlar o ciclo de vida do jogo durante prototipagem.\n"
        "QUANDO NÃO USAR: para editar cenas (use scene_manage), para debug (use debug_manage).\n"
        "PRÉ-CONDIÇÕES: Godot instalado, projeto configurado, bridge ativo na porta 8790.\n"
        "ERRO COMUM: bridge não responde — o jogo precisa estar rodando com o addon mcp_runtime_bridge."
    ),
    phases=[Phase.PROTOTIPO],
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[
        OpSpec(name="run_project", fn=handlers.run_project, summary="Lança o projeto Godot como processo separado",
               schema={"project_path": {"type": "string", "required": True}, "godot_executable": {"type": "string", "required": True}},
               examples=[{"project_path": ".", "godot_executable": "/path/to/godot"}], rollback=None),
        OpSpec(name="stop_project", fn=handlers.stop_project, summary="Para o processo Godot pelo PID",
               schema={"pid": {"type": "integer", "required": True}},
               examples=[{"pid": 12345}], rollback=None),
        OpSpec(name="wait_bridge", fn=handlers.wait_bridge, summary="Espera o bridge do Godot responder (timeout configurável)",
               schema={"timeout_sec": {"type": "number", "required": False}},
               examples=[{"timeout_sec": 10}], rollback=None),
        OpSpec(name="exec_gdscript", fn=handlers.exec_gdscript, summary="Executa código GDScript no jogo rodando via bridge",
               schema={"code": {"type": "string", "required": True, "description": "Código GDScript a executar"}},
               examples=[{"code": 'print("hello")'}], rollback=None),
        OpSpec(name="runtime_info", fn=handlers.runtime_info, summary="Obtém FPS, draw calls, memória do jogo rodando",
               schema={}, examples=[{}], rollback=None),
    ],
    tags=["godot", "runtime", "execução", "prototipo"],
)
