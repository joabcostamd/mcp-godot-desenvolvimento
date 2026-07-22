"""domains/godot/examples.py"""

EXAMPLES = {
    "run_project": {"project_path": ".", "godot_executable": "/path/to/godot"},
    "stop_project": {"pid": 12345},
    "wait_bridge": {"timeout_sec": 10},
    "exec_gdscript": {"code": 'print("hello")'},
    "runtime_info": {},
}
