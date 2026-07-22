"""domains/game_bridge/handlers.py — F5.26."""
def game_call_method(*, node_path: str, method: str, args: list | None = None) -> dict:
    from tools.runtime_rich import game_call_method as _impl; return _impl(node_path, method, args)
def game_spawn_node(*, scene_path: str, parent_path: str = ".", node_name: str = "") -> dict:
    from tools.runtime_rich import game_spawn_node as _impl; return _impl(scene_path, parent_path, node_name)
def game_raycast(*, from_pos: list, to_pos: list, collision_mask: int = 1) -> dict:
    from tools.runtime_rich import game_raycast as _impl; return _impl(from_pos, to_pos, collision_mask)
def game_get_camera() -> dict:
    from tools.runtime_rich import game_get_camera as _impl; return _impl()
def game_find_by_class(*, class_name: str) -> dict:
    from tools.runtime_rich import game_find_nodes_by_class as _impl; return _impl(class_name)
def game_await_signal(*, node_path: str, signal_name: str, timeout: float = 5.0) -> dict:
    from tools.runtime_rich import game_await_signal as _impl; return _impl(node_path, signal_name, timeout)
def game_pause(*, paused: bool = True) -> dict:
    from tools.runtime_rich import game_pause as _impl; return _impl(paused)
def game_play_animation(*, node_path: str, anim_name: str) -> dict:
    from tools.runtime_rich import game_play_animation as _impl; return _impl(node_path, anim_name)
def game_performance() -> dict:
    from tools.runtime_ui import game_performance as _impl; return _impl()
def game_window(*, mode: str = "windowed", width: int = 1280, height: int = 720) -> dict:
    from tools.runtime_ui import game_window as _impl; return _impl(mode, width, height)
def game_input_state() -> dict:
    from tools.runtime_ui import game_input_state as _impl; return _impl()
def game_http_request(*, url: str, method: str = "GET", headers: dict | None = None, body: str = "") -> dict:
    from tools.networking_ops import game_http_request as _impl; return _impl(url, method, headers, body)
def game_multiplayer(*, action: str = "status", **kwargs) -> dict:
    from tools.networking_ops import game_multiplayer as _impl; return _impl(action, **kwargs)
def game_serialize_state(*, include_scenes: bool = False) -> dict:
    from tools.recording_ops import game_serialize_state as _impl; return _impl(include_scenes)
__all__ = ["game_call_method", "game_spawn_node", "game_raycast", "game_get_camera", "game_find_by_class", "game_await_signal", "game_pause", "game_play_animation", "game_performance", "game_window", "game_input_state", "game_http_request", "game_multiplayer", "game_serialize_state"]
