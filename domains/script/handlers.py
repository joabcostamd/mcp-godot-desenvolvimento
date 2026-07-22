"""domains/script/handlers.py"""
def generate_gdscript(*, class_name: str = "NewScript", extends: str = "Node", template: str = "default") -> dict:
    from tools.script_ops import generate_gdscript as _impl; return _impl(class_name, extends, template)
def attach_script(*, scene_path: str, node_path: str, script_path: str) -> dict:
    from tools.script_ops import attach_script as _impl; return _impl(scene_path, node_path, script_path)
def detach_script(*, scene_path: str, node_path: str) -> dict:
    from tools.script_ops import detach_script as _impl; return _impl(scene_path, node_path)
def validate_gdscript_syntax(*, script_path: str) -> dict:
    from tools.script_ops import validate_gdscript_syntax as _impl; return _impl(script_path)
def add_script_variable(*, scene_path: str, node_path: str, var_name: str, var_type: str = "Variant", default_value=None) -> dict:
    from tools.script_ops import add_script_variable as _impl; return _impl(scene_path, node_path, var_name, var_type, default_value)
def add_script_signal(*, scene_path: str, node_path: str, signal_name: str, params: list[str] | None = None) -> dict:
    from tools.script_ops import add_script_signal as _impl; return _impl(scene_path, node_path, signal_name, params)
__all__ = ["generate_gdscript", "attach_script", "detach_script", "validate_gdscript_syntax", "add_script_variable", "add_script_signal"]
