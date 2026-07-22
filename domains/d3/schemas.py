"""domains/d3/schemas.py — Schemas do domínio d3 (F5.15)."""

INPUT_SCHEMAS = {
    "create_light": {"type": "object", "properties": {"scene_path": {"type": "string"}, "light_type": {"type": "string"}, "energy": {"type": "number"}}, "required": ["scene_path"]},
    "create_csg": {"type": "object", "properties": {"scene_path": {"type": "string"}, "shape_type": {"type": "string"}, "dimensions": {"type": "array"}}, "required": ["scene_path"]},
    "config_material": {"type": "object", "properties": {"scene_path": {"type": "string"}, "node_path": {"type": "string"}, "preset": {"type": "string"}}, "required": ["scene_path", "node_path"]},
    "create_particles": {"type": "object", "properties": {"scene_path": {"type": "string"}, "preset": {"type": "string"}}, "required": ["scene_path"]},
}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}, "message": {"type": "string"}}}
