"""domains/anim/examples.py"""
EXAMPLES = {
    "create_player": {"scene_path": "scenes/game.tscn"},
    "create_clip": {"scene_path": "scenes/game.tscn", "anim_name": "idle", "length": 1.0, "loop": True},
    "create_tween": {"scene_path": "scenes/game.tscn", "node_path": "./Sprite", "property_name": "modulate", "target_value": "Color(1,0,0,1)", "duration": 0.5},
    "chain_tweens": {"scene_path": "scenes/game.tscn", "tweens": [{"node": "./Sprite", "prop": "position:x", "to": 100, "dur": 0.3}]},
}
