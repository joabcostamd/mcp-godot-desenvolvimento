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


# ══════════════════════════════════════════════════════════════════════
# CAMADA 6.3 — JOINTS & BODY CONFIG
# ══════════════════════════════════════════════════════════════════════

def create_physics_joint(
    scene_path: str,
    parent_node_path: str,
    joint_type: str,
    joint_name: str = "",
    node_a: str = "",
    node_b: str = "",
    stiffness: float = 0.0,
    damping: float = 0.0,
    bias: float = 0.0,
    disable_collision: bool = True,
) -> dict:
    """Cria um joint físico entre dois corpos (Pin, Spring, Hinge, etc.).
    
    Args:
        scene_path: Caminho da cena .tscn
        parent_node_path: Nó pai
        joint_type: Tipo de joint ("PinJoint2D", "DampedSpringJoint2D",
            "GrooveJoint2D", "HingeJoint2D", "ConeJoint2D", "SliderJoint2D")
        joint_name: Nome do nó (auto-gerado se vazio)
        node_a: Path para o nó A
        node_b: Path para o nó B
        stiffness: Rigidez da mola (DampedSpring)
        damping: Amortecimento (DampedSpring)
        bias: Bias de restituição
        disable_collision: Desabilita colisão entre A e B
    
    Returns:
        dict com status e caminho do nó
    """
    try:
        valid_joints = {
            "PinJoint2D", "DampedSpringJoint2D", "GrooveJoint2D",
            "HingeJoint2D", "ConeJoint2D", "SliderJoint2D",
            "PinJoint3D", "HingeJoint3D", "ConeJoint3D", "SliderJoint3D",
            "Generic6DOFJoint3D",
        }
        if joint_type not in valid_joints:
            return {
                "ok": False,
                "error": f"Tipo '{joint_type}' não suportado. Use: {', '.join(sorted(valid_joints))}",
            }
        
        import uuid as _uuid
        
        name = joint_name or f"{joint_type}_{node_a.replace('/', '_')}"
        
        content = Path(scene_path).read_text(encoding='utf-8')
        uid = _uuid.uuid4().hex[:16]
        
        node_block = f'''
[node name="{name}" type="{joint_type}" parent="{parent_node_path}"]
disable_collision = {str(disable_collision).lower()}
'''
        if node_a:
            node_block += f'node_a = NodePath("{node_a}")\n'
        if node_b:
            node_block += f'node_b = NodePath("{node_b}")\n'
        if stiffness:
            node_block += f'stiffness = {stiffness}\n'
        if damping:
            node_block += f'damping = {damping}\n'
        if bias:
            node_block += f'bias = {bias}\n'
        
        node_block += f'_import_path = NodePath("")\nunique_name_in_owner = false\nuid = "uid://{uid}"\n'
        
        insert_pos = content.rfind('\n')
        new_content = content[:insert_pos] + node_block + content[insert_pos:]
        Path(scene_path).write_text(new_content, encoding='utf-8')
        
        return {
            "ok": True,
            "joint_type": joint_type,
            "joint_name": name,
            "node_a": node_a,
            "node_b": node_b,
            "message": f"Joint {joint_type} '{name}' criado entre '{node_a}' e '{node_b}'",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao criar joint: {e}"}


def configure_physics_body(
    scene_path: str,
    node_path: str,
    mass: float | None = None,
    friction: float | None = None,
    bounce: float | None = None,
    gravity_scale: float | None = None,
    linear_damp: float | None = None,
    angular_damp: float | None = None,
    freeze: bool | None = None,
    freeze_mode: str | None = None,
) -> dict:
    """Configura propriedades físicas de um corpo (RigidBody2D/3D, CharacterBody).
    
    Args:
        scene_path: Caminho da cena .tscn
        node_path: Caminho do nó na cena
        mass: Massa do corpo (kg)
        friction: Atrito
        bounce: Restituição (bounciness)
        gravity_scale: Escala de gravidade
        linear_damp: Amortecimento linear
        angular_damp: Amortecimento angular
        freeze: Congela o corpo
        freeze_mode: "static" ou "kinematic"
    
    Returns:
        dict com mudanças aplicadas
    """
    try:
        import re
        content = Path(scene_path).read_text(encoding="utf-8")
        
        node_name = node_path.split("/")[-1]
        node_pattern = rf'\[node\s+name="{re.escape(node_name)}"[^\]]*\]'
        match = re.search(node_pattern, content)
        
        if not match:
            return {"ok": False, "error": f"Nó '{node_name}' não encontrado na cena"}
        
        node_start = match.start()
        next_node = re.search(r'\n\[node\b', content[node_start + 1:])
        node_end = node_start + 1 + next_node.start() if next_node else len(content)
        node_block = content[node_start:node_end]
        changes = []
        
        props = {}
        if mass is not None:
            props["mass"] = str(mass)
            changes.append(f"mass={mass}")
        if friction is not None:
            props["friction"] = str(friction)
            changes.append(f"friction={friction}")
        if bounce is not None:
            props["bounce"] = str(bounce)
            changes.append(f"bounce={bounce}")
        if gravity_scale is not None:
            props["gravity_scale"] = str(gravity_scale)
            changes.append(f"gravity_scale={gravity_scale}")
        if linear_damp is not None:
            props["linear_damp"] = str(linear_damp)
            changes.append(f"linear_damp={linear_damp}")
        if angular_damp is not None:
            props["angular_damp"] = str(angular_damp)
            changes.append(f"angular_damp={angular_damp}")
        if freeze is not None:
            props["freeze"] = str(freeze).lower()
            changes.append(f"freeze={freeze}")
        if freeze_mode is not None:
            props["freeze_mode"] = freeze_mode
            changes.append(f"freeze_mode={freeze_mode}")
        
        for key, value in props.items():
            pattern = rf'{re.escape(key)}\s*=\s*\S+'
            replacement = f'{key} = {value}'
            if re.search(pattern, node_block):
                node_block = re.sub(pattern, replacement, node_block)
            else:
                node_block = node_block.rstrip() + f'\n{replacement}'
        
        new_content = content[:node_start] + node_block + content[node_end:]
        Path(scene_path).write_text(new_content, encoding="utf-8")
        
        return {
            "ok": True,
            "node_path": node_path,
            "changes": changes,
            "message": f"Física configurada em '{node_name}': {', '.join(changes)}",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao configurar corpo físico: {e}"}


def query_area_overlap(
    scene_path: str,
    area_path: str,
    query_type: str = "bodies",
) -> dict:
    """Verifica corpos/áreas sobrepostos a uma Area2D/Area3D.
    
    NOTA: Esta operação só funciona em runtime (jogo rodando).
    Fornece o código GDScript para executar a query.
    
    Args:
        scene_path: Caminho da cena
        area_path: Caminho do nó Area2D/Area3D
        query_type: "bodies" ou "areas"
    
    Returns:
        dict com código GDScript pronto para runtime
    """
    try:
        import re
        content = Path(scene_path).read_text(encoding="utf-8")
        
        area_name = area_path.split("/")[-1]
        area_pattern = rf'\[node\s+name="{re.escape(area_name)}"[^\]]*type="(Area\w+)"[^\]]*\]'
        area_match = re.search(area_pattern, content)
        
        if not area_match:
            return {"ok": False, "error": f"Area '{area_name}' não encontrada"}
        
        area_type = area_match.group(1)
        is_3d = "3D" in area_type
        
        query_method = f"get_overlapping_{query_type}"
        
        gdscript = f'''# Runtime Query: {area_type} ({area_name})
# Execute via execute_gdscript_runtime

var area = get_node("{area_path}")
var overlapping = area.{query_method}()
print("[Query] {area_name} overlapping {query_type}: ", overlapping.size())
for body in overlapping:
    print("  - ", body.name)
return overlapping.size()
'''
        
        return {
            "ok": True,
            "area_type": area_type,
            "query_type": query_type,
            "gdscript": gdscript,
            "message": f"Query de overlap para {area_type} '{area_name}' — use execute_gdscript_runtime com o código acima",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao preparar query: {e}"}


def raycast_query(
    scene_path: str,
    raycast_path: str,
) -> dict:
    """Prepara código para executar raycast em runtime.
    
    Args:
        scene_path: Caminho da cena
        raycast_path: Caminho do nó RayCast2D/3D
    
    Returns:
        dict com código GDScript
    """
    try:
        ray_name = raycast_path.split("/")[-1]
        
        gdscript = f'''var ray = get_node("{raycast_path}")
ray.force_raycast_update()
if ray.is_colliding():
    var collider = ray.get_collider()
    var point = ray.get_collision_point()
    var normal = ray.get_collision_normal()
    print("[RayCast] Colidiu com: ", collider.name)
    print("  Ponto: ", point)
    print("  Normal: ", normal)
    return {{"collider": collider.name, "point": str(point), "normal": str(normal)}}
else:
    print("[RayCast] Nenhuma colisão")
    return {{"collider": null}}
'''
        
        return {
            "ok": True,
            "raycast_path": raycast_path,
            "gdscript": gdscript,
            "message": f"Código de raycast pronto para '{ray_name}' — use execute_gdscript_runtime",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao preparar raycast: {e}"}

