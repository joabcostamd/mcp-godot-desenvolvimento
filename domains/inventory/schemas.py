"""domains/inventory/schemas.py"""
INPUT_SCHEMAS = {"create_system": {"type": "object", "properties": {"scene_path": {"type": "string"}}, "required": ["scene_path"]}, "define_item": {"type": "object", "properties": {"scene_path": {"type": "string"}, "item_id": {"type": "string"}}, "required": ["scene_path", "item_id"]}, "create_ui": {"type": "object", "properties": {"scene_path": {"type": "string"}}, "required": ["scene_path"]}}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
