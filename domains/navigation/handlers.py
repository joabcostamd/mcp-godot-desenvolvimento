"""domains/navigation/handlers.py — Handlers do domínio navigation (F5.5)."""
from tools.devsolo_ops import create_navigation_region_2d as _region, create_navigation_agent_2d as _agent, bake_navigation_polygon as _bake

def create_navigation_region_2d(*, scene_path: str, parent_node_path: str = ".", polygon_vertices: list[list[float]] | None = None, region_name: str = "NavigationRegion2D") -> dict:
    """Cria região de navegação 2D."""
    return _region(scene_path=scene_path, parent_node_path=parent_node_path, polygon_vertices=polygon_vertices, region_name=region_name)

def create_navigation_agent_2d(*, scene_path: str, parent_node_path: str, agent_name: str = "NavigationAgent2D", target_node_path: str = "root/Player", speed: float = 200.0, avoidance_enabled: bool = True) -> dict:
    """Adiciona NavigationAgent2D com perseguição."""
    return _agent(scene_path=scene_path, parent_node_path=parent_node_path, agent_name=agent_name, target_node_path=target_node_path, speed=speed, avoidance_enabled=avoidance_enabled)

def bake_navigation_polygon(*, scene_path: str, tilemap_layer_path: str, navigation_region_path: str, walkable_tiles: list[int] | None = None) -> dict:
    """Gera NavigationPolygon de TileMapLayer."""
    return _bake(scene_path=scene_path, tilemap_layer_path=tilemap_layer_path, navigation_region_path=navigation_region_path, walkable_tiles=walkable_tiles)

__all__ = ["create_navigation_region_2d", "create_navigation_agent_2d", "bake_navigation_polygon"]
