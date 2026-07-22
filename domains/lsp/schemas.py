"""domains/lsp/schemas.py — Schemas de input/output do domínio lsp (F5.10)."""

INPUT_SCHEMAS = {
    "connect": {"type": "object", "properties": {"project_root": {"type": "string"}}, "required": []},
    "disconnect": {"type": "object", "properties": {}, "required": []},
    "sync": {"type": "object", "properties": {"file_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["file_path"]},
    "definition": {"type": "object", "properties": {"file_path": {"type": "string"}, "line": {"type": "integer"}, "character": {"type": "integer"}}, "required": ["file_path", "line", "character"]},
    "references": {"type": "object", "properties": {"file_path": {"type": "string"}, "line": {"type": "integer"}, "character": {"type": "integer"}}, "required": ["file_path", "line", "character"]},
    "hover": {"type": "object", "properties": {"file_path": {"type": "string"}, "line": {"type": "integer"}, "character": {"type": "integer"}}, "required": ["file_path", "line", "character"]},
    "symbols": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]},
    "rename": {"type": "object", "properties": {"file_path": {"type": "string"}, "line": {"type": "integer"}, "character": {"type": "integer"}, "new_name": {"type": "string"}}, "required": ["file_path", "line", "character", "new_name"]},
    "diagnostics": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]},
}

OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}, "message": {"type": "string"}}}
