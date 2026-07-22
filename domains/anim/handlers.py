"""domains/anim/handlers.py — Handlers do domínio anim (F5.16).

Wrappers keyword-only (*). NÃO conhecem MCP, Tool, nem annotations.
"""

from typing import Any


def create_animation_player(*, scene_path: str, parent_node_path: str = ".", player_name: str = "AnimationPlayer") -> dict:
    """Cria um nó AnimationPlayer na cena."""
    from tools.scene_ops import create_animation_player as _impl
    return _impl(scene_path, parent_node_path, player_name)


def create_animation(*, scene_path: str, anim_name: str, length: float = 1.0, loop: bool = False, player_path: str = ".") -> dict:
    """Cria um clipe de animação no AnimationPlayer."""
    from tools.scene_ops import create_animation as _impl
    return _impl(scene_path, anim_name, length, loop, player_path)


def create_tween_animation(*, scene_path: str, node_path: str, property_name: str, target_value, duration: float = 0.5, easing: str = "linear") -> dict:
    """Cria animação Tween em um nó."""
    from tools.devsolo_ops import create_tween_animation as _impl
    return _impl(scene_path=scene_path, node_path=node_path, property_name=property_name, target_value=target_value, duration=duration, easing=easing)


def chain_tweens(*, scene_path: str, tweens: list[dict]) -> dict:
    """Encadeia múltiplos tweens em sequência."""
    from tools.devsolo_ops import chain_tweens as _impl
    return _impl(scene_path=scene_path, tweens=tweens)


__all__ = ["create_animation_player", "create_animation", "create_tween_animation", "chain_tweens"]
