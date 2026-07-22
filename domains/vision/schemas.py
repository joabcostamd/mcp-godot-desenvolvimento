"""domains/vision/schemas.py"""
INPUT_SCHEMAS = {k: {"type": "object", "properties": {}, "required": []} for k in ["compare", "detect_empty", "detect_offscreen", "regression"]}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
