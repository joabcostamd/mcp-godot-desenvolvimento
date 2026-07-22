"""domains/playtest/handlers.py"""
def self_play(*, duration: float = 30.0, scene_path: str = "") -> dict:
    from tools.playtest_ops import self_play as _impl; return _impl(duration=duration, scene_path=scene_path)
def regression_from_recording(*, recording_path: str) -> dict:
    from tools.playtest_ops import regression_from_recording as _impl; return _impl(recording_path)
def difficulty_curve(*, metrics: dict | None = None) -> dict:
    from tools.playtest_ops import difficulty_curve as _impl; return _impl(metrics)
__all__ = ["self_play", "regression_from_recording", "difficulty_curve"]
