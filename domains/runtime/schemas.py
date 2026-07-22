"""domains/runtime/schemas.py — Schemas do domínio runtime (F5.13)."""

INPUT_SCHEMAS = {
    "compile": {"type": "object", "properties": {}, "required": []},
    "run": {"type": "object", "properties": {"scene_path": {"type": "string"}, "wait_for_bridge": {"type": "boolean"}}, "required": []},
    "stop": {"type": "object", "properties": {}, "required": []},
    "restart": {"type": "object", "properties": {"project_path": {"type": "string"}}, "required": []},
    "launch_editor": {"type": "object", "properties": {"scene_path": {"type": "string"}}, "required": []},
    "close_editor": {"type": "object", "properties": {}, "required": []},
}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}, "message": {"type": "string"}}}
