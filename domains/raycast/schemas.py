"""domains/raycast/schemas.py"""
INPUT_SCHEMAS = {"raycast": {"type": "object", "properties": {"scene_path": {"type": "string"}}, "required": ["scene_path"]}, "shapecast": {"type": "object", "properties": {"scene_path": {"type": "string"}}, "required": ["scene_path"]}}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
