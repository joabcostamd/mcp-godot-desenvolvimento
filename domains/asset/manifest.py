"""domains/asset/manifest.py"""
from registry.types import DomainManifest, OpSpec, Phase; from . import handlers
MANIFEST = DomainManifest(domain="asset", tool_name="asset_manage", title="Assets", namespace="project", version="1.0.0",
    description="Gerencia assets: importar texturas/spritesheets/áudio, placeholders, paletas, validação e licenças.",
    phases=[Phase.DESIGN, Phase.PROTOTIPO, Phase.CONTEUDO], annotations={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[OpSpec("import_texture", handlers.import_texture, "Importa textura", {"file_path": {"type": "string", "required": True}}, [{"file_path": "assets/player.png"}]),
         OpSpec("import_spritesheet", handlers.import_sprite_sheet, "Importa spritesheet", {"file_path": {"type": "string", "required": True}, "tile_width": {"type": "integer", "required": True}, "tile_height": {"type": "integer", "required": True}}, [{"file_path": "assets/player_ss.png", "tile_width": 64, "tile_height": 64}]),
         OpSpec("import_audio", handlers.import_audio, "Importa áudio", {"file_path": {"type": "string", "required": True}}, [{"file_path": "assets/explosion.wav"}]),
         OpSpec("placeholder_sprite", handlers.generate_placeholder_sprite, "Gera sprite placeholder", {}, [{}]),
         OpSpec("placeholder_atlas", handlers.generate_placeholder_texture_atlas, "Gera atlas placeholder", {}, [{}]),
         OpSpec("bg_gradient", handlers.generate_background_gradient, "Gera fundo gradiente", {}, [{}]),
         OpSpec("tileset_colors", handlers.generate_tileset_from_colors, "Gera tileset de cores", {}, [{}]),
         OpSpec("palette", handlers.suggest_color_palette, "Sugere paleta", {"theme": {"type": "string", "required": False}}, [{"theme": "fantasy"}]),
         OpSpec("validate_game_ready", handlers.validate_asset_game_ready, "Valida asset game-ready", {"asset_path": {"type": "string", "required": True}}, [{"asset_path": "assets/player.png"}]),
         OpSpec("sprite_animation", handlers.generate_sprite_animation, "Gera animação sprite", {"sprite_name": {"type": "string", "required": True}}, [{"sprite_name": "player_run", "frame_count": 4}]),
         OpSpec("license_audit", handlers.audit_asset_license, "Audita licença", {"asset_path": {"type": "string", "required": True}}, [{"asset_path": "assets/player.png"}])],
    tags=["asset", "textura", "áudio", "placeholder"])
