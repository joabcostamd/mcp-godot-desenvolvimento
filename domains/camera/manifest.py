"""domains/camera/manifest.py — Manifesto do domínio camera (F5.4)."""
from registry.types import DomainManifest, OpSpec, Phase

MANIFEST = DomainManifest(
    name="camera",
    description="Câmera 2D: configurar, seguir alvo, screen shake.",
    version="1.0.0",
    phases=[Phase.DESIGN, Phase.PROTOTIPO],
    ops=[
        OpSpec(
            name="setup_camera_2d",
            description="Adiciona Camera2D com limites, zoom, drag e suavização.",
            handler="domains.camera.handlers.setup_camera_2d",
            params=["scene_path", "parent_node_path", "limits", "drag_horizontal", "drag_vertical", "zoom", "smoothing_enabled", "smoothing_speed", "current"],
            required=["scene_path"],
        ),
        OpSpec(
            name="setup_camera_follow",
            description="Faz câmera seguir nó alvo com suavização.",
            handler="domains.camera.handlers.setup_camera_follow",
            params=["scene_path", "camera_node_path", "target_node_path", "smoothing", "offset_x", "offset_y", "deadzone_width", "deadzone_height"],
            required=["scene_path", "camera_node_path", "target_node_path"],
        ),
        OpSpec(
            name="setup_camera_shake",
            description="Adiciona screen shake à câmera.",
            handler="domains.camera.handlers.setup_camera_shake",
            params=["scene_path", "camera_node_path", "max_amplitude", "decay_rate"],
            required=["scene_path", "camera_node_path"],
        ),
    ],
    aliases={
        "setup_camera_2d": "camera_manage",
        "setup_camera_follow": "camera_manage",
        "setup_camera_shake": "camera_manage",
    },
)
