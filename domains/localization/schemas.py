"""domains/localization/schemas.py"""
INPUT_SCHEMAS = {k: {"type": "object", "properties": {}, "required": []} for k in ["find_missing", "detect_overflow", "check_contrast"]}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
