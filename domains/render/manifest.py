"""domains/render/manifest.py — Manifesto do domínio render (F5.7).

Migração concluída em 2026-07-21.
"""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="render",
    tool_name="render_manage",
    title="Gerenciar Renderização",
    namespace="project",
    version="1.0.0",
    description=(
        "Gerencia renderização: consultar configs, anti-aliasing, scaling e qualidade gráfica.\n"
        "QUANDO USAR: para ajustar performance visual, configurar MSAA/FXAA/TAA, modo de scaling.\n"
        "QUANDO NÃO USAR: para shaders (use shader_manage), ambiente visual (use vfx_manage).\n"
        "PRÉ-CONDIÇÕES: project.godot deve existir no projeto ativo.\n"
        "ERRO COMUM: project.godot não encontrado — verifique se há um projeto ativo com set_active_project."
    ),
    phases=[Phase.DESIGN, Phase.CONTEUDO],
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    ops=[
        OpSpec(
            name="get",
            fn=handlers.get_render_settings,
            summary="Obtém as configurações atuais de rendering do projeto",
            schema={
                "project_path": {"type": "string", "required": False, "description": "Caminho do projeto (usa ativo se None)"},
            },
            examples=[{}],
            rollback=None,
        ),
        OpSpec(
            name="set_aa",
            fn=handlers.set_antialiasing,
            summary="Configura antialiasing: MSAA (disabled/2x/4x/8x), FXAA, TAA",
            schema={
                "project_path": {"type": "string", "required": False, "description": "Caminho do projeto"},
                "msaa": {"type": "string", "required": False, "description": "disabled, 2x, 4x ou 8x"},
                "fxaa": {"type": "boolean", "required": False, "description": "Habilitar FXAA"},
                "taa": {"type": "boolean", "required": False, "description": "Habilitar TAA"},
                "screen_space_aa": {"type": "string", "required": False, "description": "Modo SSAA do Godot"},
            },
            examples=[{"msaa": "4x", "fxaa": True}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="set_scale",
            fn=handlers.set_scaling_mode,
            summary="Configura modo de scaling e stretch da janela",
            schema={
                "project_path": {"type": "string", "required": False, "description": "Caminho do projeto"},
                "mode": {"type": "string", "required": False, "description": "2d, viewport ou canvas_items"},
                "scale": {"type": "number", "required": False, "description": "Fator de escala (ex: 2.0)"},
                "stretch_mode": {"type": "string", "required": False, "description": "disabled, 2d ou viewport"},
                "stretch_aspect": {"type": "string", "required": False, "description": "ignore, keep, keep_width, keep_height, expand"},
            },
            examples=[{"mode": "2d", "stretch_mode": "viewport", "stretch_aspect": "keep"}],
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="set_quality",
            fn=handlers.set_render_quality,
            summary="Configura qualidade de rendering por preset (low/balanced/high/ultra)",
            schema={
                "project_path": {"type": "string", "required": False, "description": "Caminho do projeto"},
                "preset": {"type": "string", "required": False, "description": "low, balanced, high ou ultra"},
                "shadows": {"type": "string", "required": False, "description": "Tamanho do shadow map (1024/2048/4096)"},
                "gi": {"type": "string", "required": False, "description": "Qualidade GI (low/high)"},
                "reflections": {"type": "string", "required": False, "description": "Qualidade reflexos (low/medium/high)"},
                "particles": {"type": "string", "required": False, "description": "Multiplicador de partículas"},
            },
            examples=[{"preset": "high"}],
            rollback="safety_manage(op=undo)",
        ),
    ],
    tags=["render", "gráfico", "qualidade"],
)
