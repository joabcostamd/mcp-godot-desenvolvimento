"""domains/asset/handlers.py"""
def import_texture(*, file_path: str, project_path: str | None = None) -> dict:
    from tools.asset_ops import import_texture as _impl; return _impl(file_path, project_path)
def import_sprite_sheet(*, file_path: str, tile_width: int, tile_height: int, project_path: str | None = None) -> dict:
    from tools.asset_ops import import_sprite_sheet as _impl; return _impl(file_path, tile_width, tile_height, project_path)
def import_audio(*, file_path: str, project_path: str | None = None) -> dict:
    from tools.asset_ops import import_audio as _impl; return _impl(file_path, project_path)
def validate_asset_game_ready(*, asset_path: str) -> dict:
    from tools.asset_ops import validate_asset_game_ready as _impl; return _impl(asset_path)
def audit_asset_license(*, asset_path: str) -> dict:
    from tools.asset_ops import audit_asset_license as _impl; return _impl(asset_path)
def generate_placeholder_sprite(*, width: int = 64, height: int = 64, color: str = "#ff0000") -> dict:
    from tools.placeholder_ops import generate_placeholder_sprite as _impl; return _impl(width, height, color)
def generate_placeholder_texture_atlas(*, tile_w: int = 16, tile_h: int = 16, cols: int = 8, rows: int = 8) -> dict:
    from tools.placeholder_ops import generate_placeholder_texture_atlas as _impl; return _impl(tile_w, tile_h, cols, rows)
def generate_background_gradient(*, width: int = 1920, height: int = 1080, top_color: str = "#1a1a2e", bottom_color: str = "#16213e") -> dict:
    from tools.placeholder_ops import generate_background_gradient as _impl; return _impl(width, height, top_color, bottom_color)
def generate_tileset_from_colors(*, colors: list[str] | None = None) -> dict:
    from tools.placeholder_ops import generate_tileset_from_colors as _impl; return _impl(colors)
def suggest_color_palette(*, theme: str = "fantasy") -> dict:
    from tools.placeholder_ops import suggest_color_palette as _impl; return _impl(theme)
def generate_sprite_animation(*, sprite_name: str, frame_count: int = 4, width: int = 64, height: int = 64) -> dict:
    from tools.art_ops import generate_sprite_animation as _impl; return _impl(sprite_name, frame_count, width, height)
__all__ = ["import_texture", "import_sprite_sheet", "import_audio", "validate_asset_game_ready", "audit_asset_license", "generate_placeholder_sprite", "generate_placeholder_texture_atlas", "generate_background_gradient", "generate_tileset_from_colors", "suggest_color_palette", "generate_sprite_animation"]
