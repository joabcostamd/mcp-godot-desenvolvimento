"""domains/playtest/schemas.py"""
INPUT_SCHEMAS = {k: {"type": "object", "properties": {}, "required": []} for k in ["self_play", "regression", "difficulty"]}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
