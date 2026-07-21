"""domains/shader/handlers.py — Handlers do domínio shader (F5.3)."""
from tools.devsolo_ops import generate_shader_2d as _gen, apply_shader_to_node as _apply
from tools.shader_editor_ops import read_shader as _read, edit_shader as _edit, get_shader_params as _params

def generate_shader_2d(*, scene_path: str, node_path: str, template: str = "glow", uniforms: dict | None = None, shader_name: str = "") -> dict:
    """Gera e aplica shader 2D a partir de template."""
    return _gen(scene_path=scene_path, node_path=node_path, template=template, uniforms=uniforms, shader_name=shader_name)

def apply_shader_to_node(*, scene_path: str, node_path: str, shader_template: str = "glow", uniforms: dict | None = None) -> dict:
    """Aplica shader existente a um nó."""
    return _apply(scene_path=scene_path, node_path=node_path, shader_template=shader_template, uniforms=uniforms)

def read_shader(*, shader_path: str) -> dict:
    """Lê arquivo .gdshader."""
    return _read(shader_path)

def edit_shader(*, shader_path: str, edits: dict) -> dict:
    """Edita shader .gdshader."""
    return _edit(shader_path, edits)

def get_shader_params(*, shader_path: str) -> dict:
    """Obtém parâmetros/uniforms de um shader."""
    return _params(shader_path)

__all__ = ["generate_shader_2d", "apply_shader_to_node", "read_shader", "edit_shader", "get_shader_params"]
