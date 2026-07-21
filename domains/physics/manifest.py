"""domains/physics/manifest.py — Manifesto do domínio physics (F5.1).

Migração concluída em 2026-07-21.
"""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="physics",
    tool_name="physics_manage",
    title="Gerenciar Física",
    namespace="project",
    version="1.0.0",
    description=(
        "Gerencia física 2D: collision shapes, layers, materiais, juntas, raycasts e shapecasts.\n"
        "QUANDO USAR: para configurar colisão, física de objetos e detecção de linha de visão.\n"
        "QUANDO NÃO USAR: para criar nós físicos em si (use node_manage para CharacterBody2D, etc).\n"
        "PRÉ-CONDIÇÕES: cena alvo e nó pai devem existir no projeto.\n"
        "ERRO COMUM: tipo de shape inválido — use 'rectangle', 'circle' ou 'capsule'."
    ),
    phases=[Phase.DESIGN, Phase.PROTOTIPO],
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    ops=[
        OpSpec(
            name="add_collision",
            fn=handlers.add_collision_shape,
            summary="Adiciona CollisionShape2D/3D com shape a um nó de física",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "parent_node_path": {"type": "string", "required": True, "description": "Nó pai (CollisionObject2D/3D)"},
                "shape_type": {"type": "string", "required": True, "description": "rectangle, circle ou capsule"},
                "dimensions": {"type": "object", "required": True, "description": "Dimensões do shape"},
            },
            examples=[{"scene_path": "scenes/player.tscn", "parent_node_path": ".", "shape_type": "rectangle", "dimensions": {"width": 64, "height": 64}}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="set_layer_mask",
            fn=handlers.set_collision_layer_mask,
            summary="Configura layer e máscara de colisão de um nó",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "node_path": {"type": "string", "required": True, "description": "Nó alvo"},
                "layer": {"type": "integer", "required": False, "description": "Layer de colisão (1-32)"},
                "mask": {"type": "integer", "required": False, "description": "Máscara de colisão (1-32)"},
            },
            examples=[{"scene_path": "scenes/player.tscn", "node_path": "./Player", "layer": 1, "mask": 3}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="set_material",
            fn=handlers.set_physics_material,
            summary="Define PhysicsMaterial com atrito e ricochete",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "node_path": {"type": "string", "required": True, "description": "Nó alvo (com physics_material_override)"},
                "friction": {"type": "number", "required": False, "description": "Atrito (default 0.5)"},
                "bounce": {"type": "number", "required": False, "description": "Ricochete (default 0.0)"},
                "rough": {"type": "boolean", "required": False, "description": "Superfície rugosa (default false)"},
                "absorbent": {"type": "boolean", "required": False, "description": "Superfície absorvente (default false)"},
            },
            examples=[{"scene_path": "scenes/player.tscn", "node_path": "./Player", "friction": 0.8, "bounce": 0.2}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="create_joint",
            fn=handlers.create_joint_2d,
            summary="Cria junta 2D (PinJoint2D/GrooveJoint2D) entre dois nós",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "node_a_path": {"type": "string", "required": True, "description": "Nó A"},
                "node_b_path": {"type": "string", "required": True, "description": "Nó B"},
                "joint_type": {"type": "string", "required": False, "description": "pin ou groove (default pin)"},
                "softness": {"type": "number", "required": False, "description": "Suavidade"},
                "bias": {"type": "number", "required": False, "description": "Bias"},
            },
            examples=[{"scene_path": "scenes/game.tscn", "node_a_path": "./Door", "node_b_path": "./Wall", "joint_type": "pin"}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="add_raycast",
            fn=handlers.add_raycast_2d,
            summary="Adiciona RayCast2D para detecção de linha de visão",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "parent_node_path": {"type": "string", "required": True, "description": "Nó pai"},
                "target_position": {"type": "string", "required": False, "description": "Posição alvo (ex: 'Vector2(100, 0)')"},
                "collision_mask": {"type": "integer", "required": False, "description": "Máscara de colisão (default 1)"},
                "enabled": {"type": "boolean", "required": False, "description": "Ativo (default true)"},
                "node_name": {"type": "string", "required": False, "description": "Nome do nó"},
            },
            examples=[{"scene_path": "scenes/player.tscn", "parent_node_path": ".", "target_position": "Vector2(100, 0)", "collision_mask": 2}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="add_shapecast",
            fn=handlers.add_shapecast_2d,
            summary="Adiciona ShapeCast2D para detecção de área",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "parent_node_path": {"type": "string", "required": True, "description": "Nó pai"},
                "shape_type": {"type": "string", "required": False, "description": "rectangle, circle ou capsule"},
                "shape_size": {"type": "string", "required": False, "description": "Tamanho (ex: 'Vector2(32, 32)')"},
                "target_position": {"type": "string", "required": False, "description": "Posição alvo"},
                "collision_mask": {"type": "integer", "required": False, "description": "Máscara (default 1)"},
                "node_name": {"type": "string", "required": False, "description": "Nome do nó"},
            },
            examples=[{"scene_path": "scenes/player.tscn", "parent_node_path": ".", "shape_type": "rectangle", "shape_size": "Vector2(32, 32)"}],
            rollback="safety_manage(op=undo)",
        ),
    ],
    aliases=["create_joint_2d", "add_raycast_2d", "add_shapecast_2d",
             "add_collision_shape", "set_collision_layer_mask", "set_physics_material"],
    tags=["física", "colisão", "raycast", "joint", "physics"],
)
