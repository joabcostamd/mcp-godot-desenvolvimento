"""domains/skeleton/handlers.py — Handlers do domínio skeleton (F5.8).

Wrappers keyword-only (*) que delegam para tools/skeleton_ops.py.
NÃO conhecem MCP, Tool, nem annotations.
"""

from typing import Any


def get_skeleton_info(*, scene_path: str, skeleton_path: str) -> dict:
    """Obtém informações completas de um Skeleton3D (ossos, IK chains)."""
    from tools.skeleton_ops import get_skeleton_info as _impl
    return _impl(scene_path=scene_path, skeleton_path=skeleton_path)


def list_bones(*, scene_path: str, skeleton_path: str) -> dict:
    """Lista todos os ossos de um Skeleton3D com seus índices."""
    from tools.skeleton_ops import list_bones as _impl
    return _impl(scene_path=scene_path, skeleton_path=skeleton_path)


def get_bone_pose(*, scene_path: str, skeleton_path: str, bone_name: str) -> dict:
    """Obtém a pose atual (transform) de um osso específico."""
    from tools.skeleton_ops import get_bone_pose as _impl
    return _impl(scene_path=scene_path, skeleton_path=skeleton_path, bone_name=bone_name)


def set_bone_pose(
    *,
    scene_path: str,
    skeleton_path: str,
    bone_name: str,
    position: list[float] | None = None,
    rotation: list[float] | None = None,
    scale: list[float] | None = None,
) -> dict:
    """Define a pose (posição/rotação/escala) de um osso."""
    from tools.skeleton_ops import set_bone_pose as _impl
    return _impl(
        scene_path=scene_path,
        skeleton_path=skeleton_path,
        bone_name=bone_name,
        position=position,
        rotation=rotation,
        scale=scale,
    )


def create_bone(
    *,
    scene_path: str,
    skeleton_path: str,
    bone_name: str,
    parent_bone: str | int = -1,
    position: list[float] | None = None,
    rotation: list[float] | None = None,
) -> dict:
    """Cria um novo osso num Skeleton3D existente."""
    from tools.skeleton_ops import create_bone as _impl
    return _impl(
        scene_path=scene_path,
        skeleton_path=skeleton_path,
        bone_name=bone_name,
        parent_bone=parent_bone,
        position=position,
        rotation=rotation,
    )


def create_ik_chain(
    *,
    scene_path: str,
    skeleton_path: str,
    bone_name: str,
    target_node_path: str = "",
    chain_length: int = 2,
    iterations: int = 10,
) -> dict:
    """Cria/Configura chain SkeletonIK3D vinculada a um osso."""
    from tools.skeleton_ops import create_ik_chain as _impl
    return _impl(
        scene_path=scene_path,
        skeleton_path=skeleton_path,
        bone_name=bone_name,
        target_node_path=target_node_path,
        chain_length=chain_length,
        iterations=iterations,
    )


__all__ = [
    "get_skeleton_info",
    "list_bones",
    "get_bone_pose",
    "set_bone_pose",
    "create_bone",
    "create_ik_chain",
]
