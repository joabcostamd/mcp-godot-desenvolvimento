"""domains/config/handlers.py — F5.23."""
def configure_input_action(*, action_name: str, key: str = "", joypad_button: int | None = None, deadzone: float = 0.5) -> dict:
    from tools.project_ops import configure_input_action as _impl; return _impl(action_name, key, joypad_button, deadzone)
def configure_autoload(*, script_path: str, singleton_name: str = "") -> dict:
    from tools.project_ops import configure_autoload as _impl; return _impl(script_path, singleton_name)
__all__ = ["configure_input_action", "configure_autoload"]
