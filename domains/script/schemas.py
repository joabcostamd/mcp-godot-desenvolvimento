"""domains/script/schemas.py"""
INPUT_SCHEMAS = {k: {"type": "object", "properties": {}, "required": []} for k in ["generate", "attach", "detach", "validate", "add_var", "add_signal"]}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
