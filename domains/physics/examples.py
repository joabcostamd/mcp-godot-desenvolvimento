"""domains/physics/examples.py — Exemplos de uso do domínio physics (F5.1)."""

EXAMPLES = {
    "add_collision": {
        "scene_path": "scenes/player.tscn",
        "parent_node_path": ".",
        "shape_type": "rectangle",
        "dimensions": {"width": 64, "height": 64},
    },
    "set_layer_mask": {
        "scene_path": "scenes/player.tscn",
        "node_path": "./Player",
        "layer": 1,
        "mask": 3,
    },
    "set_material": {
        "scene_path": "scenes/player.tscn",
        "node_path": "./Player",
        "friction": 0.8,
        "bounce": 0.2,
    },
    "create_joint": {
        "scene_path": "scenes/game.tscn",
        "node_a_path": "./Door",
        "node_b_path": "./Wall",
        "joint_type": "pin",
    },
    "add_raycast": {
        "scene_path": "scenes/player.tscn",
        "parent_node_path": ".",
        "target_position": "Vector2(100, 0)",
        "collision_mask": 2,
    },
    "add_shapecast": {
        "scene_path": "scenes/player.tscn",
        "parent_node_path": ".",
        "shape_type": "rectangle",
        "shape_size": "Vector2(32, 32)",
    },
}
