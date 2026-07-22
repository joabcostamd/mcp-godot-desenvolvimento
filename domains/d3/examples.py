"""domains/d3/examples.py — Exemplos de uso do domínio d3 (F5.15)."""

EXAMPLES = {
    "create_light": {"scene_path": "scenes/game.tscn", "light_type": "omni", "energy": 2.0},
    "create_csg": {"scene_path": "scenes/game.tscn", "shape_type": "box", "dimensions": [2, 1, 2]},
    "config_material": {"scene_path": "scenes/game.tscn", "node_path": "./Mesh", "preset": "metal"},
    "create_particles": {"scene_path": "scenes/game.tscn", "preset": "fire"},
}
