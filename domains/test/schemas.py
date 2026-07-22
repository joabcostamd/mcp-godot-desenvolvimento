"""domains/test/schemas.py — Schemas do domínio test (F5.14)."""

INPUT_SCHEMAS = {
    "assert_node": {"type": "object", "properties": {"scene_path": {"type": "string"}, "node_path": {"type": "string"}, "node_type": {"type": "string"}}, "required": ["scene_path", "node_path"]},
    "stress_test": {"type": "object", "properties": {"spawn_count": {"type": "integer"}, "duration_seconds": {"type": "integer"}}, "required": []},
    "coverage_report": {"type": "object", "properties": {"args": {"type": "object"}}, "required": []},
    "generate_test_cases": {"type": "object", "properties": {"args": {"type": "object"}}, "required": []},
    "canary": {"type": "object", "properties": {"args": {"type": "object"}}, "required": []},
    "gut": {"type": "object", "properties": {"project_path": {"type": "string"}, "test_dir": {"type": "string"}, "timeout": {"type": "integer"}}, "required": []},
    "scripted": {"type": "object", "properties": {"args": {"type": "object"}}, "required": []},
    "smoke": {"type": "object", "properties": {"args": {"type": "object"}}, "required": []},
    "regression": {"type": "object", "properties": {"args": {"type": "object"}}, "required": []},
    "verify_pipeline": {"type": "object", "properties": {"timeout_compile": {"type": "integer"}, "timeout_gut": {"type": "integer"}}, "required": []},
}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}, "message": {"type": "string"}}}
