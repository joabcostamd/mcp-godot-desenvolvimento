"""domains/export/schemas.py"""
INPUT_SCHEMAS = {"list_presets": {"type": "object", "properties": {}, "required": []}, "validate_templates": {"type": "object", "properties": {}, "required": []}, "build": {"type": "object", "properties": {"preset": {"type": "string"}}, "required": []}}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
