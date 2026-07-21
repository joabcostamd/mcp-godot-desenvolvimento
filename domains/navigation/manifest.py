"""domains/navigation/manifest.py — Manifesto do domínio navigation (F5.5)."""
from registry.types import DomainManifest, OpSpec, Phase

MANIFEST = DomainManifest(
    name="navigation",
    description="Navegação 2D: região, agente com pathfinding, bake de polígono.",
    version="1.0.0",
    phases=[Phase.DESIGN, Phase.PROTOTIPO],
    ops=[
        OpSpec(
            name="create_navigation_region_2d",
            description="Cria região de navegação 2D com polígono.",
            handler="domains.navigation.handlers.create_navigation_region_2d",
            params=["scene_path", "parent_node_path", "polygon_vertices", "region_name"],
            required=["scene_path"],
        ),
        OpSpec(
            name="create_navigation_agent_2d",
            description="Adiciona NavigationAgent2D com perseguição e pathfinding.",
            handler="domains.navigation.handlers.create_navigation_agent_2d",
            params=["scene_path", "parent_node_path", "agent_name", "target_node_path", "speed", "avoidance_enabled"],
            required=["scene_path", "parent_node_path"],
        ),
        OpSpec(
            name="bake_navigation_polygon",
            description="Gera NavigationPolygon a partir de TileMapLayer.",
            handler="domains.navigation.handlers.bake_navigation_polygon",
            params=["scene_path", "tilemap_layer_path", "navigation_region_path", "walkable_tiles"],
            required=["scene_path", "tilemap_layer_path", "navigation_region_path"],
        ),
    ],
    aliases={
        "create_navigation_region_2d": "navigation_manage",
        "create_navigation_agent_2d": "navigation_manage",
        "bake_navigation_polygon": "navigation_manage",
    },
)
