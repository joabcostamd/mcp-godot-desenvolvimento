"""domains/config/schemas.py"""
INPUT_SCHEMAS = {"input_action": {"type": "object", "properties": {"action_name": {"type": "string"}}, "required": ["action_name"]}, "autoload": {"type": "object", "properties": {"script_path": {"type": "string"}}, "required": ["script_path"]}}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
