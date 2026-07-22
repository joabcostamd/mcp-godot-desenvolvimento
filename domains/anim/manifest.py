"""domains/anim/manifest.py — Manifesto do domínio anim (F5.16)."""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="anim", tool_name="anim_manage", title="Gerenciar Animações", namespace="project", version="1.0.0",
    description=(
        "Gerencia animações: AnimationPlayer, clipes, tweens e encadeamento.\n"
        "QUANDO USAR: para criar animações de propriedades, tweens e players.\n"
        "QUANDO NÃO USAR: para animação esqueletal (use skeleton_manage).\n"
        "PRÉ-CONDIÇÕES: cena alvo deve existir.\n"
        "ERRO COMUM: nó alvo não encontrado — verifique o node_path."
    ),
    phases=[Phase.PROTOTIPO],
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[
        OpSpec(name="create_player", fn=handlers.create_animation_player, summary="Cria um nó AnimationPlayer na cena",
               schema={"scene_path": {"type": "string", "required": True}, "parent_node_path": {"type": "string", "required": False}},
               examples=[{"scene_path": "scenes/game.tscn"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="create_clip", fn=handlers.create_animation, summary="Cria um clipe de animação no AnimationPlayer",
               schema={"scene_path": {"type": "string", "required": True}, "anim_name": {"type": "string", "required": True}, "length": {"type": "number", "required": False}, "loop": {"type": "boolean", "required": False}},
               examples=[{"scene_path": "scenes/game.tscn", "anim_name": "idle", "length": 1.0, "loop": True}], rollback="safety_manage(op=undo)"),
        OpSpec(name="create_tween", fn=handlers.create_tween_animation, summary="Cria animação Tween em um nó",
               schema={"scene_path": {"type": "string", "required": True}, "node_path": {"type": "string", "required": True}, "property_name": {"type": "string", "required": True}, "target_value": {}, "duration": {"type": "number", "required": False}},
               examples=[{"scene_path": "scenes/game.tscn", "node_path": "./Sprite", "property_name": "modulate", "target_value": "Color(1,0,0,1)", "duration": 0.5}], rollback="safety_manage(op=undo)"),
        OpSpec(name="chain_tweens", fn=handlers.chain_tweens, summary="Encadeia múltiplos tweens em sequência",
               schema={"scene_path": {"type": "string", "required": True}, "tweens": {"type": "array", "required": True}},
               examples=[{"scene_path": "scenes/game.tscn", "tweens": [{"node": "./Sprite", "prop": "position:x", "to": 100, "dur": 0.3}]}], rollback="safety_manage(op=undo)"),
    ],
    tags=["animação", "tween", "godot"],
)
