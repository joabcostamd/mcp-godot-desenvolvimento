"""physics_ops — Operações de física e colisão.

Fase 2: add_collision_shape, set_collision_layer_mask.
"""

from pathlib import Path
from typing import Any

from tools.classdb import get_class_hierarchy
from tools.project_ops import _get_active_project, _check_path_traversal
from tools.scene_ops import _parse_tscn_content, _find_node_in_parsed, set_node_property
from tools.safety import checkpoint


def add_collision_shape(
    scene_path: str, parent_node_path: str,
    shape_type: str, dimensions: dict | str
) -> dict:
    """Adiciona um CollisionShape2D/3D com um shape a um nó de física.

    Args:
        scene_path: Cena alvo.
        parent_node_path: Nó pai (deve ser CollisionObject2D/3D).
        shape_type: "rectangle", "circle", ou "capsule".
        dimensions: Dimensões do shape.
                    Dict: {"width": 64, "height": 64} ou {"radius": 32}.
                    String: "64,64" (largura,altura) ou "32" (raio).

    Returns:
        {"status": "success", "collision_node_path": str}
    """
    proj = _get_active_project()

    # ── Normaliza dimensions: aceita string "largura,altura" ──────────
    if isinstance(dimensions, str):
        parts = [p.strip() for p in dimensions.split(",")]
        if len(parts) == 1:
            try:
                dimensions = {"radius": float(parts[0])}
            except ValueError:
                return {"status": "error", "message": f"Dimensão inválida: '{dimensions}'. Use 'largura,altura' (ex: '64,64') ou um número para raio (ex: '32')."}
        elif len(parts) == 2:
            try:
                dimensions = {"width": float(parts[0]), "height": float(parts[1])}
            except ValueError:
                return {"status": "error", "message": f"Dimensões inválidas: '{dimensions}'. Use números como '64,64'."}
        else:
            return {"status": "error", "message": f"Formato de dimensões inválido: '{dimensions}'. Use 'largura,altura' ou um número."}

    violation = _check_path_traversal(scene_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    lines, nodes = _parse_tscn_content(full_path)

    parent_node = _find_node_in_parsed(nodes, parent_node_path)
    if not parent_node:
        return {"status": "error", "message": f"Pai '{parent_node_path}' não encontrado."}

    # Verifica que o pai herda de CollisionObject2D ou CollisionObject3D
    parent_type = parent_node.get("type", "")
    if parent_type:
        hierarchy = get_class_hierarchy(parent_type)
        if not any(c in ("CollisionObject2D", "CollisionObject3D") for c in hierarchy):
            return {
                "status": "error",
                "message": f"O nó '{parent_node_path}' (tipo '{parent_type}') não é um CollisionObject. "
                           f"Adicione a collision shape a um CharacterBody2D, Area2D, RigidBody2D, etc.",
            }

    # Determina 2D ou 3D
    is_3d = "3D" in parent_type if parent_type else False
    shape_node_type = "CollisionShape3D" if is_3d else "CollisionShape2D"

    # Determina nome
    shape_name = "CollisionShape"

    checkpoint(scene_path, proj)

    # Constrói SubResource do shape
    shape_map = {
        "rectangle": "RectangleShape2D" if not is_3d else "BoxShape3D",
        "circle": "CircleShape2D" if not is_3d else "SphereShape3D",
        "capsule": "CapsuleShape2D" if not is_3d else "CapsuleShape3D",
    }
    shape_class = shape_map.get(shape_type)
    if not shape_class:
        return {
            "status": "error",
            "message": f"Tipo de shape '{shape_type}' inválido. Use 'rectangle', 'circle', ou 'capsule'.",
        }

    # Encontra próximo ID de SubResource
    content_str = "".join(lines)
    import re
    existing_subs = re.findall(r'SubResource\("(\d+)"\)', content_str)
    next_sub_id = max([int(i) for i in existing_subs] + [0]) + 1

    # Constrói propriedades do shape
    shape_props = ""
    if shape_type == "rectangle":
        w = dimensions.get("width", dimensions.get("size", 64))
        h = dimensions.get("height", dimensions.get("size", 64))
        if is_3d:
            shape_props = f"size = Vector3({w/2}, {h/2}, {w/2})"
        else:
            shape_props = f"size = Vector2({w}, {h})"
    elif shape_type == "circle":
        r = dimensions.get("radius", 32)
        shape_props = f"radius = {r}"
    elif shape_type == "capsule":
        r = dimensions.get("radius", 16)
        h = dimensions.get("height", 32)
        shape_props = f"radius = {r}\nheight = {h}"

    # Insere SubResource antes do nó
    sub_resource = (
        f'[sub_resource type="{shape_class}" id="{next_sub_id}"]\n'
        f'{shape_props}\n'
    )

    # Encontra posição de inserção (após gd_scene, antes do primeiro nó)
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("[gd_scene"):
            insert_pos = i + 1
            break

    lines.insert(insert_pos, sub_resource + "\n")

    # Atualiza load_steps
    for i, line in enumerate(lines):
        if line.strip().startswith("[gd_scene"):
            current_steps = re.search(r'load_steps=(\d+)', line)
            if current_steps:
                new_steps = int(current_steps.group(1)) + 1
                lines[i] = re.sub(r'load_steps=\d+', f'load_steps={new_steps}', line)
            break

    # Adiciona nó CollisionShape
    parent_name = parent_node["name"]
    insert_line = parent_node["line_end"]
    for i in range(parent_node["line_start"], len(lines)):
        if lines[i].strip().startswith("[node ") and i > parent_node["line_start"]:
            break
        insert_line = i + 1

    parent_attr = f' parent="{parent_name}"' if parent_name else ""
    collision_node_line = (
        f'[node name="{shape_name}" type="{shape_node_type}"{parent_attr}]\n'
        f'shape = SubResource("{next_sub_id}")\n'
    )

    # Ajusta offsets de linha (simplificado — insere no final do pai)
    lines.insert(insert_line, collision_node_line)

    full_path.write_text("".join(lines), encoding="utf-8")

    return {"status": "success", "collision_node_path": f"{scene_path}::{shape_name}"}


def set_collision_layer_mask(
    scene_path: str, node_path: str, layer_bits: list[int], mask_bits: list[int]
) -> dict:
    """Configura collision_layer e collision_mask de um nó.

    Args:
        scene_path: Cena alvo.
        node_path: Nó com colisão.
        layer_bits: Bits de layer (1-32).
        mask_bits: Bits de mask (1-32).

    Returns:
        {"status": "success", "layer_value": int, "mask_value": int}
    """
    def bits_to_int(bits) -> int:
        """Converte bits (int único ou lista de ints) para máscara."""
        if isinstance(bits, int):
            return 1 << (bits - 1) if 1 <= bits <= 32 else 0
        return sum(1 << (b - 1) for b in bits if 1 <= b <= 32)

    layer_val = bits_to_int(layer_bits)
    mask_val = bits_to_int(mask_bits)

    # Usa set_node_property para cada propriedade
    r1 = set_node_property(scene_path, node_path, "collision_layer", layer_val)
    r2 = set_node_property(scene_path, node_path, "collision_mask", mask_val)

    if r1["status"] != "success" or r2["status"] != "success":
        return {
            "status": "error",
            "message": "Falha ao configurar collision_layer/mask.",
        }

    return {"status": "success", "layer_value": layer_val, "mask_value": mask_val}


# ── Onda 5: Physics Material ────────────────────────────────────────

def set_physics_material(
    scene_path: str,
    node_path: str,
    bounce: float | None = None,
    friction: float | None = None,
    absorb: float | None = None,
    rough: bool | None = None,
) -> dict:
    """Configura um PhysicsMaterial com bounce, friction e absorb em um nó.

    Cria um novo PhysicsMaterial como SubResource e atribui ao nó.
    Funciona com qualquer CollisionObject2D/3D (CharacterBody, RigidBody, etc.).

    Args:
        scene_path: Cena alvo.
        node_path: Nó de física (CharacterBody2D, RigidBody2D, Area2D, etc.).
        bounce: Elasticidade (0.0 = sem bounce, 1.0 = bounce perfeito).
        friction: Atrito (0.0 = sem atrito, 1.0 = atrito máximo).
        absorb: Absorção de velocidade (0.0 = sem absorção).
        rough: Se true, usa atrito áspero.

    Returns:
        {"status": "success", "physics_material": dict}
    """
    proj = _get_active_project()
    full_path = proj / scene_path

    violation = _check_path_traversal(scene_path, proj) if '_check_path_traversal' in dir() else None
    if violation:
        return {"status": "error", "message": violation}

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    lines, nodes = _parse_tscn_content(full_path)
    target = _find_node_in_parsed(nodes, node_path)
    if not target:
        return {"status": "error", "message": f"Nó '{node_path}' não encontrado."}

    checkpoint(scene_path, proj)

    # Determina se é 2D ou 3D
    node_type = target.get("type", "")
    is_3d = "3D" in node_type
    mat_class = "PhysicsMaterial"  # Godot 4 usa PhysicsMaterial unificado

    # Encontra próximo SubResource ID
    content_str = "".join(lines)
    import re
    existing = re.findall(r'SubResource\("(\d+)"\)', content_str)
    sub_id = max([int(i) for i in existing] + [0]) + 1

    # Constrói material
    props = []
    if bounce is not None:
        props.append(f"bounce = {bounce}")
    if friction is not None:
        props.append(f"friction = {friction}")
    if absorb is not None:
        props.append(f"absorb = {absorb}")
    if rough is not None:
        props.append(f"rough = {'true' if rough else 'false'}")

    sub_block = f"""[sub_resource type="{mat_class}" id="{sub_id}"]
{"\n".join(props)}
"""

    # Insere SubResource
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("[gd_scene"):
            insert_pos = i + 1
            break
    lines.insert(insert_pos, sub_block + "\n")

    # Atualiza load_steps
    for i, line in enumerate(lines):
        if line.strip().startswith("[gd_scene"):
            m = re.search(r'load_steps=(\d+)', line)
            if m:
                lines[i] = re.sub(r'load_steps=\d+', f'load_steps={int(m.group(1))+1}', line)
            break

    # Atribui physics_material_override ao nó
    insert_at = target["line_start"] + 1
    lines.insert(insert_at, f'physics_material_override = SubResource("{sub_id}")\n')

    full_path.write_text("".join(lines), encoding="utf-8")

    return {
        "status": "success",
        "physics_material": {
            "sub_resource_id": sub_id,
            "bounce": bounce,
            "friction": friction,
            "absorb": absorb,
            "rough": rough,
        },
    }


def create_joint_2d(
    scene_path: str,
    node_a_path: str,
    node_b_path: str,
    joint_type: str = "pin",
    softness: float = 0.0,
    bias: float = 0.0,
) -> dict:
    """Cria uma junta 2D (PinJoint2D) entre dois nós.

    Args:
        scene_path: Cena alvo.
        node_a_path: Primeiro nó.
        node_b_path: Segundo nó.
        joint_type: "pin" (ponto fixo) ou "groove" (trilho).
        softness: Suavidade da junta (0=rígida).
        bias: Viés de correção.

    Returns:
        {"status": "success", "joint_node_path": str}
    """
    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    lines, nodes = _parse_tscn_content(full_path)

    node_a = _find_node_in_parsed(nodes, node_a_path)
    node_b = _find_node_in_parsed(nodes, node_b_path)
    if not node_a:
        return {"status": "error", "message": f"Nó A '{node_a_path}' não encontrado."}
    if not node_b:
        return {"status": "error", "message": f"Nó B '{node_b_path}' não encontrado."}

    checkpoint(scene_path, proj)

    # Determina tipo
    godot_type = "PinJoint2D" if joint_type == "pin" else "GrooveJoint2D"
    joint_name = f"Joint_{node_a['name']}_{node_b['name']}"

    # Insere após o último nó (joint fica na raiz por simplicidade)
    last_node_line = max(n["line_end"] for n in nodes)
    joint_line = (
        f'\n[node name="{joint_name}" type="{godot_type}"]\n'
        f'node_a = NodePath("../{node_a["name"]}")\n'
        f'node_b = NodePath("../{node_b["name"]}")\n'
    )
    if softness != 0.0:
        joint_line += f"softness = {softness}\n"
    if bias != 0.0:
        joint_line += f"bias = {bias}\n"

    lines.insert(last_node_line, joint_line)
    full_path.write_text("".join(lines), encoding="utf-8")

    return {"status": "success", "joint_node_path": f"{scene_path}::{joint_name}",
            "joint_type": godot_type}

