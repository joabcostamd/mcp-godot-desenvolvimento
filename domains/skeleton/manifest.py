"""domains/skeleton/manifest.py — Manifesto do domínio skeleton (F5.8).

Migração concluída em 2026-07-21.
"""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="skeleton",
    tool_name="skeleton_manage",
    title="Gerenciar Esqueleto 2D",
    namespace="project",
    version="1.0.0",
    description=(
        "Gerencia esqueletos 2D (Skeleton2D): consultar ossos, obter/definir poses, criar ossos e cadeias IK.\n"
        "QUANDO USAR: para rigging, animação esqueletal, posicionamento de ossos e IK.\n"
        "QUANDO NÃO USAR: para animação em si (use anim_manage), para física (use physics_manage).\n"
        "PRÉ-CONDIÇÕES: cena com Skeleton3D deve existir no projeto.\n"
        "ERRO COMUM: skeleton_path inválido — use o caminho completo do nó na cena."
    ),
    phases=[Phase.DESIGN, Phase.CONTEUDO],
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
    ops=[
        OpSpec(
            name="get_info",
            fn=handlers.get_skeleton_info,
            summary="Obtém informações completas de um Skeleton3D (ossos, IK chains)",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo (.tscn)"},
                "skeleton_path": {"type": "string", "required": True, "description": "Caminho do nó Skeleton3D (ex: Player/Armature)"},
            },
            examples=[{"scene_path": "scenes/player.tscn", "skeleton_path": "Player/Armature/Skeleton3D"}],
            rollback=None,
        ),
        OpSpec(
            name="list_bones",
            fn=handlers.list_bones,
            summary="Lista todos os ossos de um Skeleton3D com seus índices",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo (.tscn)"},
                "skeleton_path": {"type": "string", "required": True, "description": "Caminho do nó Skeleton3D"},
            },
            examples=[{"scene_path": "scenes/player.tscn", "skeleton_path": "Player/Armature"}],
            rollback=None,
        ),
        OpSpec(
            name="get_pose",
            fn=handlers.get_bone_pose,
            summary="Obtém a pose atual (posição/rotação/escala) de um osso",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "skeleton_path": {"type": "string", "required": True, "description": "Caminho do Skeleton3D"},
                "bone_name": {"type": "string", "required": True, "description": "Nome do osso"},
            },
            examples=[{"scene_path": "scenes/player.tscn", "skeleton_path": "Player/Armature", "bone_name": "UpperArm_L"}],
            rollback=None,
        ),
        OpSpec(
            name="set_pose",
            fn=handlers.set_bone_pose,
            summary="Define a pose (posição/rotação/escala) de um osso",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "skeleton_path": {"type": "string", "required": True, "description": "Caminho do Skeleton3D"},
                "bone_name": {"type": "string", "required": True, "description": "Nome do osso"},
                "position": {"type": "array", "required": False, "description": "[x, y, z]"},
                "rotation": {"type": "array", "required": False, "description": "[x, y, z] em radianos"},
                "scale": {"type": "array", "required": False, "description": "[x, y, z]"},
            },
            examples=[{"scene_path": "scenes/player.tscn", "skeleton_path": "Player/Armature", "bone_name": "UpperArm_L", "rotation": [0, 0, 1.57]}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="create_bone",
            fn=handlers.create_bone,
            summary="Cria um novo osso num Skeleton3D existente",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "skeleton_path": {"type": "string", "required": True, "description": "Caminho do Skeleton3D"},
                "bone_name": {"type": "string", "required": True, "description": "Nome do novo osso"},
                "parent_bone": {"type": "string", "required": False, "description": "Nome ou índice do osso pai (-1 = raiz)"},
                "position": {"type": "array", "required": False, "description": "[x, y, z] posição inicial"},
                "rotation": {"type": "array", "required": False, "description": "[x, y, z] rotação inicial"},
            },
            examples=[{"scene_path": "scenes/player.tscn", "skeleton_path": "Player/Armature", "bone_name": "Weapon_Bone", "parent_bone": "UpperArm_R"}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="create_ik",
            fn=handlers.create_ik_chain,
            summary="Cria/Configura chain SkeletonIK3D vinculada a um osso",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "skeleton_path": {"type": "string", "required": True, "description": "Caminho do Skeleton3D"},
                "bone_name": {"type": "string", "required": True, "description": "Nome do osso alvo do IK"},
                "target_node_path": {"type": "string", "required": False, "description": "Caminho do nó alvo"},
                "chain_length": {"type": "integer", "required": False, "description": "Comprimento da chain (default 2)"},
                "iterations": {"type": "integer", "required": False, "description": "Iterações do solver (default 10)"},
            },
            examples=[{"scene_path": "scenes/player.tscn", "skeleton_path": "Player/Armature", "bone_name": "UpperArm_R", "chain_length": 2, "iterations": 10}],
            rollback="safety_manage(op=undo)",
        ),
    ],
    tags=["skeleton", "2D", "animação", "bones"],
)
