"""domains/node/schemas.py"""
INPUT_SCHEMAS = {k: {"type": "object", "properties": {"scene_path": {"type": "string"}}, "required": ["scene_path"]} for k in ["create", "delete", "set_property", "get_property", "reparent", "connect_signal", "list_signals"]}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
