"""vfx_ops — Operações de efeitos visuais (partículas, screen flash, ambiente).

Funções extraídas dos handlers inline de server.py para reuso em rollups.
"""

from pathlib import Path
from tools.scene_ops import add_node, set_node_property


def create_particles_2d(
    scene_path: str,
    parent_node_path: str,
    node_name: str = "Particles",
    amount: int | None = None,
    lifetime: float | None = None,
    explosiveness: float | None = None,
    direction: str | None = None,
    spread: float | None = None,
    gravity: str | None = None,
) -> dict:
    """Cria GPUParticles2D com ParticleProcessMaterial em uma cena.

    Args:
        scene_path: Caminho da cena.
        parent_node_path: Path do nó pai.
        node_name: Nome do nó de partículas (default: "Particles").
        amount: Quantidade de partículas.
        lifetime: Tempo de vida em segundos.
        explosiveness: Explosividade (0-1).
        direction: Direção em formato "x,y,z".
        spread: Ângulo de dispersão.
        gravity: Gravidade em formato "x,y,z".

    Returns:
        dict com status e detalhes.
    """
    r = add_node(scene_path, parent_node_path, node_name, "GPUParticles2D")
    if r["status"] != "success":
        return r

    # Configura propriedades comuns
    props = {}
    if amount is not None:
        props["amount"] = amount
    if lifetime is not None:
        props["lifetime"] = lifetime
    if explosiveness is not None:
        props["explosiveness"] = explosiveness
    for k, v in props.items():
        set_node_property(scene_path, f"./{node_name}", k, v)

    # Cria ParticleProcessMaterial
    mat_line = '[sub_resource type="ParticleProcessMaterial" id="1"]\n'
    if direction is not None:
        mat_line += f'direction = Vector3({direction})\n'
    if spread is not None:
        mat_line += f'spread = {spread}\n'
    if gravity is not None:
        mat_line += f'gravity = Vector3({gravity})\n'

    # Escreve no .tscn
    try:
        from tools.project_ops import get_project_settings
        settings = get_project_settings()
        proj = settings.get("project_path", ".")
    except Exception:
        proj = "."

    full = Path(proj) / scene_path if proj else Path(scene_path)
    if full.exists():
        content = full.read_text(encoding="utf-8")
        content = content.replace("[gd_scene", f"{mat_line}\n[gd_scene")
        content = content.replace(
            f'[node name="{node_name}" type="GPUParticles2D"',
            f'[node name="{node_name}" type="GPUParticles2D"\nprocess_material = SubResource("1")'
        )
        full.write_text(content, encoding="utf-8")

    return {
        "status": "success",
        "node_path": r.get("node_path", ""),
        "note": "Partículas configuradas. Use run_game para ver o efeito.",
    }
