"""domains/file/schemas.py"""
INPUT_SCHEMAS = {"delete": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}, "move": {"type": "object", "properties": {"source_path": {"type": "string"}, "dest_path": {"type": "string"}}, "required": ["source_path", "dest_path"]}, "inspect": {"type": "object", "properties": {}, "required": []}}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
