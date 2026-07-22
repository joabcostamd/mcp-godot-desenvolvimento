"""domains/tilemap/examples.py"""
EXAMPLES = {
    "create_tileset": {"scene_path": "scenes/game.tscn", "texture_path": "res://assets/tiles.png", "tile_size": 16},
    "create_layer": {"scene_path": "scenes/game.tscn"},
    "paint_cell": {"scene_path": "scenes/game.tscn", "layer_path": "./TileMapLayer", "cell_x": 5, "cell_y": 3},
    "generate_from_noise": {"scene_path": "scenes/game.tscn", "width": 64, "height": 64, "seed": 42},
}
