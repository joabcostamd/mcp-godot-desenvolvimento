"""domains/camera/handlers.py — Handlers do domínio camera (F5.4)."""
from tools.devsolo_ops import setup_camera_2d as _s2d, setup_camera_follow as _follow, setup_camera_shake as _shake

def setup_camera_2d(*, scene_path: str, parent_node_path: str = ".", limits: dict | None = None, drag_horizontal: float = 0.0, drag_vertical: float = 0.0, zoom: list[float] | None = None, smoothing_enabled: bool = True, smoothing_speed: float = 5.0, current: bool = True) -> dict:
    """Adiciona e configura Camera2D."""
    return _s2d(scene_path=scene_path, parent_node_path=parent_node_path, limits=limits, drag_horizontal=drag_horizontal, drag_vertical=drag_vertical, zoom=zoom, smoothing_enabled=smoothing_enabled, smoothing_speed=smoothing_speed, current=current)

def setup_camera_follow(*, scene_path: str, camera_node_path: str, target_node_path: str, smoothing: float = 5.0, offset_x: float = 0.0, offset_y: float = 0.0, deadzone_width: float = 0.0, deadzone_height: float = 0.0) -> dict:
    """Faz câmera seguir nó alvo."""
    return _follow(scene_path=scene_path, camera_node_path=camera_node_path, target_node_path=target_node_path, smoothing=smoothing, offset_x=offset_x, offset_y=offset_y, deadzone_width=deadzone_width, deadzone_height=deadzone_height)

def setup_camera_shake(*, scene_path: str, camera_node_path: str, max_amplitude: float = 20.0, decay_rate: float = 2.0) -> dict:
    """Adiciona screen shake à câmera."""
    return _shake(scene_path=scene_path, camera_node_path=camera_node_path, max_amplitude=max_amplitude, decay_rate=decay_rate)

__all__ = ["setup_camera_2d", "setup_camera_follow", "setup_camera_shake"]
