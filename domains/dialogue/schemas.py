"""domains/dialogue/schemas.py"""
INPUT_SCHEMAS = {"create_system": {"type": "object", "properties": {"scene_path": {"type": "string"}}, "required": ["scene_path"]}, "add_node": {"type": "object", "properties": {"scene_path": {"type": "string"}}, "required": ["scene_path"]}, "create_ui": {"type": "object", "properties": {"scene_path": {"type": "string"}}, "required": ["scene_path"]}}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
