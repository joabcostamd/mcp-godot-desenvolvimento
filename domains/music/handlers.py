"""domains/music/handlers.py"""
def generate_music(*, prompt: str = "", duration: float = 30.0, genre: str = "ambient") -> dict:
    from tools.music_ops import generate_music as _impl; return _impl(prompt=prompt, duration=duration, genre=genre)
def make_seamless_loop(*, file_path: str, crossfade_ms: int = 50) -> dict:
    from tools.music_ops import make_seamless_loop as _impl; return _impl(file_path, crossfade_ms)
def place_and_normalize(*, scene_path: str, audio_path: str, parent_node_path: str = ".", target_db: float = -14.0) -> dict:
    from tools.music_ops import place_and_normalize as _impl; return _impl(scene_path, audio_path, parent_node_path, target_db)
def bind_to_event(*, scene_path: str, audio_path: str, event_name: str, fade_in: float = 0.5) -> dict:
    from tools.music_ops import bind_to_event as _impl; return _impl(scene_path, audio_path, event_name, fade_in)
__all__ = ["generate_music", "make_seamless_loop", "place_and_normalize", "bind_to_event"]
