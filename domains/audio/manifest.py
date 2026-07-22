"""domains/audio/manifest.py — Manifesto do domínio audio (F5.17)."""
from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="audio", tool_name="audio_manage", title="Gerenciar Áudio", namespace="project", version="1.0.0",
    description=(
        "Gerencia áudio: configurar buses, adicionar efeitos, rotear e criar players espaciais.\n"
        "QUANDO USAR: para mixagem, efeitos sonoros, roteamento e áudio 3D.\n"
        "QUANDO NÃO USAR: para gerar SFX (use generate_audio_sfx), para música (use music_manage).\n"
        "PRÉ-CONDIÇÕES: projeto Godot ativo.\n"
        "ERRO COMUM: bus não encontrado — use o nome exato do bus no AudioServer."
    ),
    phases=[Phase.DESIGN, Phase.PROTOTIPO],
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[
        OpSpec(name="configure_bus", fn=handlers.configure_audio_bus, summary="Configura um bus de áudio (volume, mute, solo)",
               schema={"bus_name": {"type": "string", "required": False}, "volume_db": {"type": "number", "required": False}},
               examples=[{"bus_name": "SFX", "volume_db": -6.0}], rollback="safety_manage(op=undo)"),
        OpSpec(name="add_effect", fn=handlers.add_audio_effect, summary="Adiciona efeito de áudio a um bus (reverb, delay, etc.)",
               schema={"bus_name": {"type": "string", "required": False}, "effect_type": {"type": "string", "required": False}},
               examples=[{"bus_name": "Master", "effect_type": "reverb"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="route_bus", fn=handlers.route_audio_bus, summary="Roteia áudio de um bus para outro",
               schema={"source_bus": {"type": "string", "required": True}, "target_bus": {"type": "string", "required": True}},
               examples=[{"source_bus": "SFX", "target_bus": "Master"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="spatial_player", fn=handlers.create_spatial_audio_player, summary="Cria AudioStreamPlayer3D com som espacial",
               schema={"scene_path": {"type": "string", "required": True}, "stream_path": {"type": "string", "required": False}},
               examples=[{"scene_path": "scenes/game.tscn", "stream_path": "res://audio/explosion.wav"}], rollback="safety_manage(op=undo)"),
    ],
    tags=["áudio", "sfx", "mixagem", "3D"],
)
