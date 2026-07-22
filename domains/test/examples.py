"""domains/test/examples.py — Exemplos de uso do domínio test (F5.14)."""

EXAMPLES = {
    "assert_node": {"scene_path": "scenes/game.tscn", "node_path": "./Player"},
    "stress_test": {"spawn_count": 100, "duration_seconds": 5},
    "coverage_report": {},
    "generate_test_cases": {},
    "canary": {},
    "gut": {"test_dir": "res://tests", "timeout": 60},
    "scripted": {},
    "smoke": {},
    "regression": {},
    "verify_pipeline": {"timeout_compile": 30, "timeout_gut": 120},
}
