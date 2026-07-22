"""domains/debug/schemas.py — Schemas de input/output do domínio debug (F5.9)."""

INPUT_SCHEMAS = {
    "perf_stats": {"type": "object", "properties": {}, "required": []},
    "collision_debug": {"type": "object", "properties": {"enabled": {"type": "boolean"}}, "required": []},
    "nav_debug": {"type": "object", "properties": {"enabled": {"type": "boolean"}}, "required": []},
    "perf_regression": {"type": "object", "properties": {"args": {"type": "object"}}, "required": []},
    "set_breakpoint": {
        "type": "object",
        "properties": {
            "script_path": {"type": "string"},
            "line": {"type": "integer"},
            "condition": {"type": "string"},
        },
        "required": ["script_path", "line"],
    },
    "status": {"type": "object", "properties": {}, "required": []},
    "step": {"type": "object", "properties": {"step_type": {"type": "string"}}, "required": []},
    "get_stack": {"type": "object", "properties": {}, "required": []},
    "get_vars": {"type": "object", "properties": {"variable_name": {"type": "string"}}, "required": []},
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string"},
        "message": {"type": "string"},
    },
}
