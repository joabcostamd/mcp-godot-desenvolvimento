"""domains/tilemap/schemas.py"""
INPUT_SCHEMAS = {
    "create_tileset": {"type": "object", "properties": {"scene_path": {"type": "string"}, "texture_path": {"type": "string"}}, "required": ["scene_path", "texture_path"]},
    "create_layer": {"type": "object", "properties": {"scene_path": {"type": "string"}}, "required": ["scene_path"]},
    "paint_cell": {"type": "object", "properties": {"scene_path": {"type": "string"}, "cell_x": {"type": "integer"}, "cell_y": {"type": "integer"}}, "required": ["scene_path", "cell_x", "cell_y"]},
    "generate_from_noise": {"type": "object", "properties": {"scene_path": {"type": "string"}}, "required": ["scene_path"]},
}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
