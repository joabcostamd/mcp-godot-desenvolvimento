"""domains/render/schemas.py — Schemas de input/output do domínio render (F5.7)."""

INPUT_SCHEMAS = {
    "get": {
        "type": "object",
        "properties": {
            "project_path": {"type": "string", "description": "Caminho do projeto"},
        },
        "required": [],
    },
    "set_aa": {
        "type": "object",
        "properties": {
            "project_path": {"type": "string", "description": "Caminho do projeto"},
            "msaa": {"type": "string", "description": "disabled, 2x, 4x ou 8x"},
            "fxaa": {"type": "boolean", "description": "Habilitar FXAA"},
            "taa": {"type": "boolean", "description": "Habilitar TAA"},
            "screen_space_aa": {"type": "string", "description": "Modo SSAA"},
        },
        "required": [],
    },
    "set_scale": {
        "type": "object",
        "properties": {
            "project_path": {"type": "string", "description": "Caminho do projeto"},
            "mode": {"type": "string", "description": "2d, viewport ou canvas_items"},
            "scale": {"type": "number", "description": "Fator de escala"},
            "stretch_mode": {"type": "string", "description": "disabled, 2d ou viewport"},
            "stretch_aspect": {"type": "string", "description": "ignore, keep, keep_width, keep_height, expand"},
        },
        "required": [],
    },
    "set_quality": {
        "type": "object",
        "properties": {
            "project_path": {"type": "string", "description": "Caminho do projeto"},
            "preset": {"type": "string", "description": "low, balanced, high ou ultra"},
            "shadows": {"type": "string", "description": "Tamanho shadow map"},
            "gi": {"type": "string", "description": "Qualidade GI"},
            "reflections": {"type": "string", "description": "Qualidade reflexos"},
            "particles": {"type": "string", "description": "Multiplicador partículas"},
        },
        "required": [],
    },
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "ok": {"type": "boolean"},
        "error": {"type": "string"},
    },
}
