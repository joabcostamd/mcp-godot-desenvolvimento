"""domains/scene/schemas.py"""
INPUT_SCHEMAS = {"create": {"type": "object", "properties": {"scene_name": {"type": "string"}}, "required": ["scene_name"]}, "load_tree": {"type": "object", "properties": {"scene_path": {"type": "string"}}, "required": ["scene_path"]}, "instance": {"type": "object", "properties": {"scene_path": {"type": "string"}, "parent_node_path": {"type": "string"}, "instance_path": {"type": "string"}}, "required": ["scene_path", "parent_node_path", "instance_path"]}}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
