"""domains/tilemap/handlers.py — Handlers do domínio tilemap (F5.18)."""
from typing import Any

def create_tileset(*, scene_path: str, texture_path: str, tile_size: int = 16, tileset_name: str = "Tileset") -> dict:
    """Cria um TileSet a partir de uma textura."""
    from tools.scene_ops import create_tileset as _impl
    return _impl(scene_path, texture_path, tile_size, tileset_name)

def create_tilemap_layer(*, scene_path: str, tileset_path: str = "", layer_name: str = "TileMapLayer") -> dict:
    """Cria uma camada TileMapLayer na cena."""
    from tools.scene_ops import create_tilemap_layer as _impl
    return _impl(scene_path, tileset_path, layer_name)

def paint_tilemap_cell(*, scene_path: str, layer_path: str, cell_x: int, cell_y: int, tile_id: int = 0) -> dict:
    """Pinta uma célula do tilemap."""
    from tools.scene_ops import paint_tilemap_cell as _impl
    return _impl(scene_path, layer_path, cell_x, cell_y, tile_id)

def generate_tilemap_from_noise(*, scene_path: str, width: int = 32, height: int = 32, seed: int = 0, tileset_path: str = "") -> dict:
    """Gera tilemap procedural com Perlin noise."""
    from tools.devsolo_ops import generate_tilemap_from_noise as _impl
    return _impl(scene_path=scene_path, width=width, height=height, seed=seed, tileset_path=tileset_path)

__all__ = ["create_tileset", "create_tilemap_layer", "paint_tilemap_cell", "generate_tilemap_from_noise"]
