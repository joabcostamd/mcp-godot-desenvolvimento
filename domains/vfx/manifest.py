"""domains/vfx/manifest.py — Manifesto do domínio vfx (F5.6).

Migração concluída em 2026-07-21.
"""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="vfx",
    tool_name="vfx_manage",
    title="Gerenciar VFX",
    namespace="project",
    version="1.0.0",
    description=(
        "Gerencia efeitos visuais: criar e configurar partículas 2D/3D, screen flash e ambiente.\n"
        "QUANDO USAR: para adicionar partículas, flash de tela, névoa, glow e ambiente visual.\n"
        "QUANDO NÃO USAR: para shaders (use shader_manage), iluminação (use lights em breve).\n"
        "PRÉ-CONDIÇÕES: cena alvo e nó pai devem existir no projeto.\n"
        "ERRO COMUM: cena não encontrada — verifique se o caminho da cena está correto."
    ),
    phases=[Phase.PROTOTIPO, Phase.CONTEUDO],
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
    ops=[
        OpSpec(
            name="create_particles",
            fn=handlers.create_particles_2d,
            summary="Cria GPUParticles2D com ParticleProcessMaterial em uma cena",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "parent_node_path": {"type": "string", "required": True, "description": "Nó pai"},
                "node_name": {"type": "string", "required": False, "description": "Nome do nó (default: Particles)"},
                "amount": {"type": "integer", "required": False, "description": "Quantidade de partículas"},
                "lifetime": {"type": "number", "required": False, "description": "Tempo de vida em segundos"},
                "explosiveness": {"type": "number", "required": False, "description": "Explosividade (0-1)"},
                "direction": {"type": "string", "required": False, "description": "Direção em formato 'x,y,z'"},
                "spread": {"type": "number", "required": False, "description": "Ângulo de dispersão"},
                "gravity": {"type": "string", "required": False, "description": "Gravidade em formato 'x,y,z'"},
            },
            examples=[{"scene_path": "scenes/game.tscn", "parent_node_path": ".", "amount": 100, "lifetime": 0.8}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="config_particles",
            fn=handlers.configure_particles_2d,
            summary="Configura partículas 2D com presets visuais (explosion, smoke, rain, fire)",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "node_path": {"type": "string", "required": True, "description": "Caminho do GPUParticles2D"},
                "amount": {"type": "integer", "required": False, "description": "Quantidade (default 50)"},
                "lifetime": {"type": "number", "required": False, "description": "Tempo de vida (default 1.0)"},
                "explosiveness": {"type": "number", "required": False, "description": "0=contínuo, 1=todas de uma vez"},
                "emitting": {"type": "boolean", "required": False, "description": "Se está emitindo (default true)"},
                "one_shot": {"type": "boolean", "required": False, "description": "Emitir uma vez e parar"},
                "preset": {"type": "string", "required": False, "description": "explosion, smoke, sparkle, rain, fire, custom"},
            },
            examples=[{"scene_path": "scenes/game.tscn", "node_path": "./Explosion", "preset": "explosion"}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="create_particles_3d",
            fn=handlers.create_particles_3d,
            summary="Cria partículas 3D com predefinição visual (fire, smoke, sparkles)",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "parent_node_path": {"type": "string", "required": False, "description": "Nó pai"},
                "node_name": {"type": "string", "required": False, "description": "Nome do nó (default: GPUParticles3D)"},
                "preset": {"type": "string", "required": False, "description": "fire, smoke, sparkles, custom"},
            },
            examples=[{"scene_path": "scenes/game.tscn", "parent_node_path": ".", "preset": "fire"}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="screen_flash",
            fn=handlers.setup_screen_flash,
            summary="Cria efeito de flash de tela (ex: ao tomar dano, transição)",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "parent_node_path": {"type": "string", "required": False, "description": "Nó pai"},
                "color": {"type": "string", "required": False, "description": "Cor do flash (hex, default #ffffff)"},
                "duration": {"type": "number", "required": False, "description": "Duração em segundos (default 0.15)"},
                "fade_out": {"type": "number", "required": False, "description": "Tempo de fade out (default 0.1)"},
            },
            examples=[{"scene_path": "scenes/game.tscn", "color": "#ff0000", "duration": 0.2}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="world_env",
            fn=handlers.setup_world_environment,
            summary="Configura ambiente visual (fundo, luz ambiente, glow, névoa)",
            schema={
                "scene_path": {"type": "string", "required": True, "description": "Cena alvo"},
                "parent_node_path": {"type": "string", "required": False, "description": "Nó pai"},
                "background_mode": {"type": "string", "required": False, "description": "color, sky ou canvas"},
                "background_color": {"type": "string", "required": False, "description": "Cor de fundo (hex, default #1a1a2e)"},
                "ambient_light_color": {"type": "string", "required": False, "description": "Cor da luz ambiente (hex)"},
                "ambient_light_energy": {"type": "number", "required": False, "description": "Intensidade da luz ambiente"},
                "glow_enabled": {"type": "boolean", "required": False, "description": "Ativar glow/bloom"},
                "glow_intensity": {"type": "number", "required": False, "description": "Intensidade do glow"},
                "fog_enabled": {"type": "boolean", "required": False, "description": "Ativar névoa"},
                "fog_density": {"type": "number", "required": False, "description": "Densidade da névoa"},
                "fog_color": {"type": "string", "required": False, "description": "Cor da névoa (hex)"},
            },
            examples=[{"scene_path": "scenes/game.tscn", "background_color": "#1a1a2e", "glow_enabled": True, "glow_intensity": 0.8}],
            rollback="safety_manage(op=undo)",
        ),
    ],
    tags=["vfx", "partículas", "luz", "ambiente"],
)
