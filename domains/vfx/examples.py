"""domains/vfx/examples.py — Exemplos de uso do domínio vfx (F5.6)."""

EXAMPLES = {
    "create_particles": {
        "scene_path": "scenes/game.tscn",
        "parent_node_path": ".",
        "amount": 100,
        "lifetime": 0.8,
    },
    "config_particles": {
        "scene_path": "scenes/game.tscn",
        "node_path": "./Explosion",
        "preset": "explosion",
    },
    "create_particles_3d": {
        "scene_path": "scenes/game.tscn",
        "parent_node_path": ".",
        "preset": "fire",
    },
    "screen_flash": {
        "scene_path": "scenes/game.tscn",
        "color": "#ff0000",
        "duration": 0.2,
    },
    "world_env": {
        "scene_path": "scenes/game.tscn",
        "background_color": "#1a1a2e",
        "glow_enabled": True,
        "glow_intensity": 0.8,
    },
}
