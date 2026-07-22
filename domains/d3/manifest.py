"""domains/d3/manifest.py — Manifesto do domínio d3 (F5.15)."""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="d3",
    tool_name="d3_manage",
    title="Gerenciar 3D",
    namespace="project",
    version="1.0.0",
    description=(
        "Gerencia 3D: criar luzes, geometria CSG para blockout, configurar materiais PBR e partículas.\n"
        "QUANDO USAR: para prototipagem 3D rápida, iluminação de cena, materiais e efeitos.\n"
        "QUANDO NÃO USAR: para cenas 2D (use scene_manage/node_manage), para shaders (use shader_manage).\n"
        "PRÉ-CONDIÇÕES: cena 3D deve existir no projeto.\n"
        "ERRO COMUM: cena não encontrada — verifique o caminho da cena .tscn."
    ),
    phases=[Phase.DESIGN, Phase.CONTEUDO],
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[
        OpSpec(name="create_light", fn=handlers.create_light_3d, summary="Cria luz 3D (Omni, Spot, Directional)",
               schema={"scene_path": {"type": "string", "required": True}, "parent_node_path": {"type": "string", "required": False},
                       "light_type": {"type": "string", "required": False, "description": "omni, spot ou directional"},
                       "color": {"type": "string", "required": False}, "energy": {"type": "number", "required": False},
                       "shadows": {"type": "boolean", "required": False}},
               examples=[{"scene_path": "scenes/game.tscn", "light_type": "omni", "energy": 2.0}], rollback="safety_manage(op=undo)"),
        OpSpec(name="create_csg", fn=handlers.create_csg_shape, summary="Cria geometria CSG 3D (box, sphere, cylinder) para blockout",
               schema={"scene_path": {"type": "string", "required": True}, "shape_type": {"type": "string", "required": False, "description": "box, sphere ou cylinder"},
                       "dimensions": {"type": "array", "required": False}},
               examples=[{"scene_path": "scenes/game.tscn", "shape_type": "box", "dimensions": [2, 1, 2]}], rollback="safety_manage(op=undo)"),
        OpSpec(name="config_material", fn=handlers.configure_standard_material_3d, summary="Configura StandardMaterial3D com presets (metal, wood, plastic, glass, emissive)",
               schema={"scene_path": {"type": "string", "required": True}, "node_path": {"type": "string", "required": True},
                       "preset": {"type": "string", "required": False, "description": "metal, wood, plastic, glass, emissive, custom"},
                       "albedo_color": {"type": "string", "required": False}, "metallic": {"type": "number", "required": False},
                       "roughness": {"type": "number", "required": False}},
               examples=[{"scene_path": "scenes/game.tscn", "node_path": "./Mesh", "preset": "metal"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="create_particles", fn=handlers.create_particles_3d, summary="Cria partículas 3D com predefinição (fire, smoke, sparkles)",
               schema={"scene_path": {"type": "string", "required": True}, "preset": {"type": "string", "required": False, "description": "fire, smoke, sparkles, custom"}},
               examples=[{"scene_path": "scenes/game.tscn", "preset": "fire"}], rollback="safety_manage(op=undo)"),
    ],
    tags=["3D", "luz", "material", "partículas"],
)
