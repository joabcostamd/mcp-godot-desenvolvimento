"""domains/audio/examples.py"""
EXAMPLES = {
    "configure_bus": {"bus_name": "SFX", "volume_db": -6.0},
    "add_effect": {"bus_name": "Master", "effect_type": "reverb"},
    "route_bus": {"source_bus": "SFX", "target_bus": "Master"},
    "spatial_player": {"scene_path": "scenes/game.tscn", "stream_path": "res://audio/explosion.wav"},
}
