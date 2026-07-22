"""domains/screenshot/handlers.py — F6.4."""
def capture_game_screenshot(*, wait_frames: int = 10, scene_path: str | None = None, resolution_width: int = 640, resolution_height: int = 360) -> dict:
    from tools.runtime_ops import capture_game_screenshot as _impl; return _impl(wait_frames=wait_frames, scene_path=scene_path, resolution_width=resolution_width, resolution_height=resolution_height)
def take_screenshot() -> dict:
    from tools.runtime_ops import take_screenshot as _impl; return _impl()
def auto_screenshot(*, count: int = 5, delay_between: float = 2.0, save_dir: str = "screenshots") -> dict:
    from tools.deploy_ops import auto_screenshot as _impl; return _impl(count=count, delay_between=delay_between, save_dir=save_dir)
__all__ = ["capture_game_screenshot", "take_screenshot", "auto_screenshot"]
