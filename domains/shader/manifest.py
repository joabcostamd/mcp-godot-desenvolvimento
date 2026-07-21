"""domains/shader/manifest.py — Manifesto do domínio shader (F5.3)."""
from registry.types import DomainManifest, OpSpec, Phase

MANIFEST = DomainManifest(
    name="shader",
    description="Efeitos visuais: gerar, ler, editar e aplicar shaders 2D.",
    version="1.0.0",
    phases=[Phase.PROTOTIPO],
    ops=[
        OpSpec(
            name="generate_shader_2d",
            description="Gera e aplica shader 2D a partir de template (glow, dissolve, outline, water, wind, grayscale, shockwave).",
            handler="domains.shader.handlers.generate_shader_2d",
            params=["scene_path", "node_path", "template", "uniforms", "shader_name"],
            required=["scene_path", "node_path", "template"],
        ),
        OpSpec(
            name="apply_shader_to_node",
            description="Aplica shader existente a um nó.",
            handler="domains.shader.handlers.apply_shader_to_node",
            params=["scene_path", "node_path", "shader_template", "uniforms"],
            required=["scene_path", "node_path"],
        ),
        OpSpec(
            name="read_shader",
            description="Lê conteúdo de arquivo .gdshader.",
            handler="domains.shader.handlers.read_shader",
            params=["shader_path"],
            required=["shader_path"],
        ),
        OpSpec(
            name="edit_shader",
            description="Edita .gdshader com validação.",
            handler="domains.shader.handlers.edit_shader",
            params=["shader_path", "edits"],
            required=["shader_path", "edits"],
        ),
        OpSpec(
            name="get_shader_params",
            description="Extrai uniforms de um shader.",
            handler="domains.shader.handlers.get_shader_params",
            params=["shader_path"],
            required=["shader_path"],
        ),
    ],
    aliases={
        "generate_shader_2d": "shader_manage",
        "apply_shader_to_node": "shader_manage",
        "read_shader": "shader_manage",
        "edit_shader": "shader_manage",
        "get_shader_params": "shader_manage",
    },
)
