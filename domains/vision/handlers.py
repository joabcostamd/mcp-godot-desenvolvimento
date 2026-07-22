"""domains/vision/handlers.py"""
def compare_screenshots(*, baseline_path: str, current_path: str, threshold: float = 0.05) -> dict:
    from tools.runtime_ops import compare_screenshots as _impl; return _impl(baseline_path, current_path, threshold)
def detect_empty_screen(*, screenshot_path: str) -> dict:
    from tools.runtime_ops import detect_empty_screen as _impl; return _impl(screenshot_path)
def detect_offscreen_elements(*, scene_path: str) -> dict:
    from tools.scene_ops import detect_offscreen_elements as _impl; return _impl(scene_path)
def visual_regression(*, baseline_dir: str, current_dir: str) -> dict:
    from tools.runtime_ops import visual_regression as _impl; return _impl(baseline_dir, current_dir)
__all__ = ["compare_screenshots", "detect_empty_screen", "detect_offscreen_elements", "visual_regression"]
