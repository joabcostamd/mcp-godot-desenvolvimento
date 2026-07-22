"""domains/godot/schemas.py"""

INPUT_SCHEMAS = {
    "run_project": {"type": "object", "properties": {"project_path": {"type": "string"}, "godot_executable": {"type": "string"}}, "required": ["project_path", "godot_executable"]},
    "stop_project": {"type": "object", "properties": {"pid": {"type": "integer"}}, "required": ["pid"]},
    "wait_bridge": {"type": "object", "properties": {"timeout_sec": {"type": "number"}}, "required": []},
    "exec_gdscript": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]},
    "runtime_info": {"type": "object", "properties": {}, "required": []},
}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}, "message": {"type": "string"}}}
