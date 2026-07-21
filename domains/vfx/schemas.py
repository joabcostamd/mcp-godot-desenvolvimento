"""domains/vfx/schemas.py — Schemas de input/output do domínio vfx (F5.6)."""

INPUT_SCHEMAS = {
    "create_particles": {
        "type": "object",
        "properties": {
            "scene_path": {"type": "string", "description": "Cena alvo"},
            "parent_node_path": {"type": "string", "description": "Nó pai"},
            "node_name": {"type": "string", "description": "Nome do nó"},
            "amount": {"type": "integer", "description": "Quantidade de partículas"},
            "lifetime": {"type": "number", "description": "Tempo de vida"},
            "explosiveness": {"type": "number", "description": "Explosividade (0-1)"},
            "direction": {"type": "string", "description": "Direção (x,y,z)"},
            "spread": {"type": "number", "description": "Ângulo de dispersão"},
            "gravity": {"type": "string", "description": "Gravidade (x,y,z)"},
        },
        "required": ["scene_path", "parent_node_path"],
    },
    "config_particles": {
        "type": "object",
        "properties": {
            "scene_path": {"type": "string", "description": "Cena alvo"},
            "node_path": {"type": "string", "description": "Caminho do GPUParticles2D"},
            "amount": {"type": "integer", "description": "Quantidade"},
            "lifetime": {"type": "number", "description": "Tempo de vida"},
            "explosiveness": {"type": "number", "description": "Explosividade"},
            "emitting": {"type": "boolean", "description": "Emitindo"},
            "one_shot": {"type": "boolean", "description": "Disparo único"},
            "preset": {"type": "string", "description": "explosion, smoke, sparkle, rain, fire, custom"},
        },
        "required": ["scene_path", "node_path"],
    },
    "create_particles_3d": {
        "type": "object",
        "properties": {
            "scene_path": {"type": "string", "description": "Cena alvo"},
            "parent_node_path": {"type": "string", "description": "Nó pai"},
            "node_name": {"type": "string", "description": "Nome do nó"},
            "preset": {"type": "string", "description": "fire, smoke, sparkles, custom"},
        },
        "required": ["scene_path"],
    },
    "screen_flash": {
        "type": "object",
        "properties": {
            "scene_path": {"type": "string", "description": "Cena alvo"},
            "parent_node_path": {"type": "string", "description": "Nó pai"},
            "color": {"type": "string", "description": "Cor do flash (hex)"},
            "duration": {"type": "number", "description": "Duração em segundos"},
            "fade_out": {"type": "number", "description": "Tempo de fade out"},
        },
        "required": ["scene_path"],
    },
    "world_env": {
        "type": "object",
        "properties": {
            "scene_path": {"type": "string", "description": "Cena alvo"},
            "parent_node_path": {"type": "string", "description": "Nó pai"},
            "background_mode": {"type": "string", "description": "color, sky ou canvas"},
            "background_color": {"type": "string", "description": "Cor de fundo (hex)"},
            "ambient_light_color": {"type": "string", "description": "Cor da luz ambiente (hex)"},
            "ambient_light_energy": {"type": "number", "description": "Intensidade"},
            "glow_enabled": {"type": "boolean", "description": "Ativar glow"},
            "glow_intensity": {"type": "number", "description": "Intensidade do glow"},
            "fog_enabled": {"type": "boolean", "description": "Ativar névoa"},
            "fog_density": {"type": "number", "description": "Densidade da névoa"},
            "fog_color": {"type": "string", "description": "Cor da névoa (hex)"},
        },
        "required": ["scene_path"],
    },
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["success", "error"]},
        "message": {"type": "string"},
    },
}
