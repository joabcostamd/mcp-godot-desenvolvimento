"""domains/music/schemas.py"""
INPUT_SCHEMAS = {k: {"type": "object", "properties": {}, "required": []} for k in ["generate", "seamless_loop", "place_and_normalize", "bind_to_event"]}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
