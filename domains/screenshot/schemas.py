"""domains/screenshot/schemas.py"""
INPUT_SCHEMAS = {k: {"type": "object", "properties": {}, "required": []} for k in ["capture_game", "capture_editor", "auto_capture"]}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
