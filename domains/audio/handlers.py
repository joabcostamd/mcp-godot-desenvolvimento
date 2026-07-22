"""domains/audio/handlers.py — Handlers do domínio audio (F5.17)."""
from typing import Any

def configure_audio_bus(*, bus_name: str = "Master", volume_db: float = 0.0, mute: bool = False, solo: bool = False) -> dict:
    """Configura um bus de áudio (volume, mute, solo)."""
    from tools.devsolo_ops import configure_audio_bus as _impl
    return _impl(bus_name=bus_name, volume_db=volume_db, mute=mute, solo=solo)

def add_audio_effect(*, bus_name: str = "Master", effect_type: str = "reverb", effect_params: dict | None = None) -> dict:
    """Adiciona efeito de áudio a um bus (reverb, delay, distortion, etc.)."""
    from tools.devsolo_ops import add_audio_effect as _impl
    return _impl(bus_name=bus_name, effect_type=effect_type, effect_params=effect_params)

def route_audio_bus(*, source_bus: str, target_bus: str, send_amount: float = 1.0) -> dict:
    """Roteia áudio de um bus para outro."""
    from tools.devsolo_ops import route_audio_bus as _impl
    return _impl(source_bus=source_bus, target_bus=target_bus, send_amount=send_amount)

def create_spatial_audio_player(*, scene_path: str, parent_node_path: str = ".", node_name: str = "AudioStreamPlayer3D", stream_path: str = "", autoplay: bool = False) -> dict:
    """Cria AudioStreamPlayer3D com som espacial."""
    from tools.devsolo_ops import create_spatial_audio_player as _impl
    return _impl(scene_path=scene_path, parent_node_path=parent_node_path, node_name=node_name, stream_path=stream_path, autoplay=autoplay)

__all__ = ["configure_audio_bus", "add_audio_effect", "route_audio_bus", "create_spatial_audio_player"]
