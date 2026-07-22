"""domains/asset/schemas.py"""
INPUT_SCHEMAS = {k: {"type": "object", "properties": {}, "required": []} for k in ["import_texture","import_spritesheet","import_audio","placeholder_sprite","placeholder_atlas","bg_gradient","tileset_colors","palette","validate_game_ready","sprite_animation","license_audit"]}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
