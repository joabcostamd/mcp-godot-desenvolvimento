"""domains/tilemap/manifest.py — Manifesto do domínio tilemap (F5.18)."""
from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="tilemap", tool_name="tilemap_manage", title="Gerenciar Tilemap", namespace="project", version="1.0.0",
    description=("Gerencia tilemaps: criar tileset, camadas, pintar células e gerar terreno procedural.\n"
        "QUANDO USAR: para mapas 2D baseados em grid, terreno procedural e level design.\n"
        "QUANDO NÃO USAR: para cenas sem tilemap (use scene_manage/node_manage).\n"
        "PRÉ-CONDIÇÕES: textura fonte para tileset, cena alvo deve existir.\n"
        "ERRO COMUM: tileset não encontrado — verifique o caminho da textura."),
    phases=[Phase.DESIGN, Phase.CONTEUDO],
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[
        OpSpec(name="create_tileset", fn=handlers.create_tileset, summary="Cria um TileSet a partir de uma textura",
               schema={"scene_path": {"type": "string", "required": True}, "texture_path": {"type": "string", "required": True}, "tile_size": {"type": "integer", "required": False}},
               examples=[{"scene_path": "scenes/game.tscn", "texture_path": "res://assets/tiles.png", "tile_size": 16}], rollback="safety_manage(op=undo)"),
        OpSpec(name="create_layer", fn=handlers.create_tilemap_layer, summary="Cria uma camada TileMapLayer",
               schema={"scene_path": {"type": "string", "required": True}, "tileset_path": {"type": "string", "required": False}},
               examples=[{"scene_path": "scenes/game.tscn"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="paint_cell", fn=handlers.paint_tilemap_cell, summary="Pinta uma célula do tilemap",
               schema={"scene_path": {"type": "string", "required": True}, "layer_path": {"type": "string", "required": True}, "cell_x": {"type": "integer", "required": True}, "cell_y": {"type": "integer", "required": True}},
               examples=[{"scene_path": "scenes/game.tscn", "layer_path": "./TileMapLayer", "cell_x": 5, "cell_y": 3}], rollback="safety_manage(op=undo)"),
        OpSpec(name="generate_from_noise", fn=handlers.generate_tilemap_from_noise, summary="Gera tilemap procedural com Perlin noise",
               schema={"scene_path": {"type": "string", "required": True}, "width": {"type": "integer", "required": False}, "height": {"type": "integer", "required": False}},
               examples=[{"scene_path": "scenes/game.tscn", "width": 64, "height": 64, "seed": 42}], rollback="safety_manage(op=undo)"),
    ],
    tags=["tilemap", "2D", "procedural", "grid"],
)
