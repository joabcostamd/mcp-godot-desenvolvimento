"""domains/dialogue/manifest.py — F5.19."""
from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="dialogue", tool_name="dialogue_manage", title="Gerenciar Diálogos", namespace="project", version="1.0.0",
    description=("Gerencia diálogos: criar sistema, adicionar nós de fala e interface.\n"
        "QUANDO USAR: para NPCs, cutscenes e interações com personagens.\n"
        "QUANDO NÃO USAR: para UI genérica (use ui_manage).\n"
        "PRÉ-CONDIÇÕES: cena alvo deve existir.\n"
        "ERRO COMUM: sistema de diálogo não encontrado — crie primeiro com create_system."),
    phases=[Phase.DESIGN, Phase.CONTEUDO],
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[
        OpSpec(name="create_system", fn=handlers.create_dialogue_system, summary="Cria sistema de diálogo completo na cena",
               schema={"scene_path": {"type": "string", "required": True}}, examples=[{"scene_path": "scenes/game.tscn"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="add_node", fn=handlers.add_dialogue_node, summary="Adiciona um nó de diálogo (speaker + texto)",
               schema={"scene_path": {"type": "string", "required": True}, "speaker": {"type": "string", "required": False}, "text": {"type": "string", "required": False}},
               examples=[{"scene_path": "scenes/game.tscn", "speaker": "NPC", "text": "Olá, aventureiro!"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="create_ui", fn=handlers.create_dialogue_ui, summary="Cria a interface de diálogo (caixa de texto)",
               schema={"scene_path": {"type": "string", "required": True}}, examples=[{"scene_path": "scenes/game.tscn"}], rollback="safety_manage(op=undo)"),
    ],
    tags=["diálogo", "npc", "rpg", "narrativa"],
)
