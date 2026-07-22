"""domains/screenshot/manifest.py — F6.4."""
from registry.types import DomainManifest, OpSpec, Phase; from . import handlers
MANIFEST = DomainManifest(domain="screenshot", tool_name="screenshot_manage", title="Screenshots", namespace="project", version="1.0.0",
    description="Gerencia screenshots: capturar do jogo, do editor e em lote automático.", phases=[Phase.POLIMENTO, Phase.PRONTO_PARA_LANCAR],
    annotations={"destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    ops=[OpSpec("capture_game", handlers.capture_game_screenshot, "Screenshot do jogo", {"wait_frames": {"type": "integer", "required": False}}, [{}]),
         OpSpec("capture_editor", handlers.take_screenshot, "Screenshot do editor", {}, [{}]),
         OpSpec("auto_capture", handlers.auto_screenshot, "Lote automático", {"count": {"type": "integer", "required": False}}, [{"count": 5}])],
    tags=["screenshot", "captura"])
