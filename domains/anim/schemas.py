"""domains/anim/schemas.py"""
INPUT_SCHEMAS = {
    "create_player": {"type": "object", "properties": {"scene_path": {"type": "string"}}, "required": ["scene_path"]},
    "create_clip": {"type": "object", "properties": {"scene_path": {"type": "string"}, "anim_name": {"type": "string"}}, "required": ["scene_path", "anim_name"]},
    "create_tween": {"type": "object", "properties": {"scene_path": {"type": "string"}, "node_path": {"type": "string"}, "property_name": {"type": "string"}}, "required": ["scene_path", "node_path", "property_name"]},
    "chain_tweens": {"type": "object", "properties": {"scene_path": {"type": "string"}, "tweens": {"type": "array"}}, "required": ["scene_path", "tweens"]},
}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
