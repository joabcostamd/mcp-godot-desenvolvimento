"""skeleton_ops — Camada 6.1: Skeleton IK / Bone Pose.

Operações de esqueleto 3D: get/set bone pose, IK chains, list bones.
Liga ao auto-rig de arte (Camada 3) e animação de personagem.
"""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def _read_scene(scene_path: str) -> str:
    """Lê o conteúdo de uma cena .tscn."""
    path = Path(scene_path)
    if not path.exists():
        raise FileNotFoundError(f"Cena não encontrada: {scene_path}")
    return path.read_text(encoding="utf-8")


def _write_scene(scene_path: str, content: str) -> None:
    """Escreve conteúdo em uma cena .tscn."""
    path = Path(scene_path)
    path.write_text(content, encoding="utf-8")


def _find_skeleton_node(scene_content: str, skeleton_path: str) -> dict | None:
    """Encontra um nó Skeleton3D numa cena e retorna seus dados."""
    import re
    
    # Escapa o path para uso em regex
    escaped = re.escape(skeleton_path)
    
    # Busca pelo nó
    node_pattern = rf'\[node\s+name="({escaped.split("/")[-1]})"[^\]]*type="Skeleton3D"[^\]]*\]'
    match = re.search(node_pattern, scene_content)
    
    if not match:
        return None
    
    # Extrai o bloco do nó
    node_start = match.start()
    # Encontra o fim do bloco (próximo [node] ou fim do texto)
    next_node = re.search(r'\n\[node\b', scene_content[node_start + 1:])
    node_end = node_start + 1 + next_node.start() if next_node else len(scene_content)
    
    node_block = scene_content[node_start:node_end]
    
    return {
        "name": match.group(1),
        "block": node_block,
        "start": node_start,
        "end": node_end,
    }


def get_bone_pose(
    scene_path: str,
    skeleton_path: str,
    bone_name: str,
) -> dict:
    """Obtém a pose atual (transform) de um osso específico num Skeleton3D.
    
    Args:
        scene_path: Caminho da cena .tscn
        skeleton_path: Caminho do nó Skeleton3D na cena (ex: "Player/Armature/Skeleton3D")
        bone_name: Nome do osso
    
    Returns:
        dict com bone_name, position, rotation, scale, rest_pose
    """
    try:
        content = _read_scene(scene_path)
        skeleton = _find_skeleton_node(content, skeleton_path)
        
        if not skeleton:
            return {"ok": False, "error": f"Skeleton3D não encontrado em: {skeleton_path}"}
        
        # Busca bone pose no bloco do skeleton
        import re
        # Padrão: bones/X/position = Vector3(...), bones/X/rotation = Quaternion(...)
        bone_idx = None
        bone_pattern = rf'bones/(\d+)/name\s*=\s*"{re.escape(bone_name)}"'
        bone_match = re.search(bone_pattern, skeleton["block"])
        
        if not bone_match:
            return {"ok": False, "error": f"Osso '{bone_name}' não encontrado no skeleton"}
        
        bone_idx = bone_match.group(1)
        
        # Extrai transform
        pos = re.search(rf'bones/{bone_idx}/position\s*=\s*(\S+)', skeleton["block"])
        rot = re.search(rf'bones/{bone_idx}/rotation\s*=\s*(\S+)', skeleton["block"])
        scl = re.search(rf'bones/{bone_idx}/scale\s*=\s*(\S+)', skeleton["block"])
        rest = re.search(rf'bones/{bone_idx}/rest\s*=\s*(\S+)', skeleton["block"])
        
        return {
            "ok": True,
            "bone_name": bone_name,
            "bone_index": int(bone_idx),
            "position": pos.group(1) if pos else "Vector3(0, 0, 0)",
            "rotation": rot.group(1) if rot else "Quaternion(0, 0, 0, 1)",
            "scale": scl.group(1) if scl else "Vector3(1, 1, 1)",
            "rest_pose": rest.group(1) if rest else None,
        }
    except FileNotFoundError as e:
        return {"ok": False, "error": str(e)}
    except Exception as e:
        return {"ok": False, "error": f"Erro ao obter bone pose: {e}"}


def set_bone_pose(
    scene_path: str,
    skeleton_path: str,
    bone_name: str,
    position: list[float] | None = None,
    rotation: list[float] | None = None,
    scale: list[float] | None = None,
) -> dict:
    """Define a pose (transform) de um osso num Skeleton3D.
    
    Args:
        scene_path: Caminho da cena .tscn
        skeleton_path: Caminho do nó Skeleton3D
        bone_name: Nome do osso
        position: [x, y, z] — posição
        rotation: [x, y, z, w] — quaternion
        scale: [x, y, z] — escala
    
    Returns:
        dict com status da operação
    """
    try:
        content = _read_scene(scene_path)
        skeleton = _find_skeleton_node(content, skeleton_path)
        
        if not skeleton:
            return {"ok": False, "error": f"Skeleton3D não encontrado em: {skeleton_path}"}
        
        import re
        bone_pattern = rf'bones/(\d+)/name\s*=\s*"{re.escape(bone_name)}"'
        bone_match = re.search(bone_pattern, skeleton["block"])
        
        if not bone_match:
            return {"ok": False, "error": f"Osso '{bone_name}' não encontrado"}
        
        bone_idx = bone_match.group(1)
        block = skeleton["block"]
        changes = []
        
        if position is not None and len(position) >= 3:
            new_pos = f"Vector3({position[0]}, {position[1]}, {position[2]})"
            pos_pattern = rf'(bones/{bone_idx}/position\s*=\s*)\S+'
            if re.search(pos_pattern, block):
                block = re.sub(pos_pattern, rf'\g<1>{new_pos}', block)
            else:
                block += f'\nbones/{bone_idx}/position = {new_pos}'
            changes.append("position")
        
        if rotation is not None and len(rotation) >= 4:
            new_rot = f"Quaternion({rotation[0]}, {rotation[1]}, {rotation[2]}, {rotation[3]})"
            rot_pattern = rf'(bones/{bone_idx}/rotation\s*=\s*)\S+'
            if re.search(rot_pattern, block):
                block = re.sub(rot_pattern, rf'\g<1>{new_rot}', block)
            else:
                block += f'\nbones/{bone_idx}/rotation = {new_rot}'
            changes.append("rotation")
        
        if scale is not None and len(scale) >= 3:
            new_scl = f"Vector3({scale[0]}, {scale[1]}, {scale[2]})"
            scl_pattern = rf'(bones/{bone_idx}/scale\s*=\s*)\S+'
            if re.search(scl_pattern, block):
                block = re.sub(scl_pattern, rf'\g<1>{new_scl}', block)
            else:
                block += f'\nbones/{bone_idx}/scale = {new_scl}'
            changes.append("scale")
        
        # Aplica a alteração
        new_content = content[:skeleton["start"]] + block + content[skeleton["end"]:]
        _write_scene(scene_path, new_content)
        
        return {
            "ok": True,
            "bone_name": bone_name,
            "changes": changes,
            "message": f"Pose do osso '{bone_name}' atualizada: {', '.join(changes)}",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao definir bone pose: {e}"}


def list_bones(
    scene_path: str,
    skeleton_path: str,
) -> dict:
    """Lista todos os ossos de um Skeleton3D com seus índices.
    
    Args:
        scene_path: Caminho da cena .tscn
        skeleton_path: Caminho do nó Skeleton3D
    
    Returns:
        dict com lista de ossos e contagem
    """
    try:
        content = _read_scene(scene_path)
        skeleton = _find_skeleton_node(content, skeleton_path)
        
        if not skeleton:
            return {"ok": False, "error": f"Skeleton3D não encontrado em: {skeleton_path}"}
        
        import re
        bones = []
        for match in re.finditer(r'bones/(\d+)/name\s*=\s*"([^"]+)"', skeleton["block"]):
            idx = match.group(1)
            name = match.group(2)
            
            # Pega o parent
            parent_match = re.search(rf'bones/{idx}/parent\s*=\s*(\d+)', skeleton["block"])
            parent = int(parent_match.group(1)) if parent_match else -1
            
            # Pega posição
            pos_match = re.search(rf'bones/{idx}/position\s*=\s*(\S+)', skeleton["block"])
            position = pos_match.group(1) if pos_match else "Vector3(0, 0, 0)"
            
            bones.append({
                "index": int(idx),
                "name": name,
                "parent": parent,
                "position": position,
            })
        
        return {
            "ok": True,
            "skeleton_path": skeleton_path,
            "bone_count": len(bones),
            "bones": bones,
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao listar bones: {e}"}


def create_bone(
    scene_path: str,
    skeleton_path: str,
    bone_name: str,
    parent_bone: str | int = -1,
    position: list[float] | None = None,
    rotation: list[float] | None = None,
) -> dict:
    """Cria um novo osso num Skeleton3D existente.
    
    Args:
        scene_path: Caminho da cena .tscn
        skeleton_path: Caminho do nó Skeleton3D
        bone_name: Nome do novo osso
        parent_bone: Nome ou índice do osso pai (-1 = raiz)
        position: [x, y, z] — posição inicial
        rotation: [x, y, z, w] — rotação inicial (quaternion)
    
    Returns:
        dict com status e índice do novo osso
    """
    try:
        content = _read_scene(scene_path)
        skeleton = _find_skeleton_node(content, skeleton_path)
        
        if not skeleton:
            return {"ok": False, "error": f"Skeleton3D não encontrado em: {skeleton_path}"}
        
        import re
        
        # Encontra o maior índice de osso existente
        max_idx = -1
        for match in re.finditer(r'bones/(\d+)/', skeleton["block"]):
            idx = int(match.group(1))
            if idx > max_idx:
                max_idx = idx
        
        new_idx = max_idx + 1
        block = skeleton["block"]
        
        # Resolve parent
        parent_idx = -1
        if isinstance(parent_bone, str) and parent_bone:
            parent_match = re.search(rf'bones/(\d+)/name\s*=\s*"{re.escape(parent_bone)}"', block)
            if parent_match:
                parent_idx = int(parent_match.group(1))
        elif isinstance(parent_bone, int):
            parent_idx = parent_bone
        
        pos = position if position else [0.0, 0.0, 0.0]
        rot = rotation if rotation else [0.0, 0.0, 0.0, 1.0]
        
        new_bone_lines = [
            f'bones/{new_idx}/name = "{bone_name}"',
            f'bones/{new_idx}/parent = {parent_idx}',
            f'bones/{new_idx}/position = Vector3({pos[0]}, {pos[1]}, {pos[2]})',
            f'bones/{new_idx}/rotation = Quaternion({rot[0]}, {rot[1]}, {rot[2]}, {rot[3]})',
            f'bones/{new_idx}/scale = Vector3(1, 1, 1)',
            f'bones/{new_idx}/rest = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)',
            f'bones/{new_idx}/enabled = true',
        ]
        
        # Insere antes do fim do bloco
        insert_pos = skeleton["end"]
        # Encontra a última linha antes do próximo [node]
        last_line = content.rfind('\n', skeleton["start"], insert_pos)
        if last_line == -1:
            last_line = insert_pos
        
        bone_text = '\n' + '\n'.join(new_bone_lines)
        new_content = content[:insert_pos] + bone_text + content[insert_pos:]
        
        _write_scene(scene_path, new_content)
        
        return {
            "ok": True,
            "bone_name": bone_name,
            "bone_index": new_idx,
            "parent": parent_idx,
            "position": pos,
            "message": f"Osso '{bone_name}' criado com índice {new_idx}",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao criar osso: {e}"}


def create_ik_chain(
    scene_path: str,
    skeleton_path: str,
    bone_name: str,
    target_node_path: str = "",
    chain_length: int = 2,
    iterations: int = 10,
) -> dict:
    """Cria/Configura uma chain SkeletonIK3D vinculada a um osso.
    
    Cria um nó SkeletonIK3D como filho do Skeleton, configurado
    para controlar a chain IK a partir do osso especificado.
    
    Args:
        scene_path: Caminho da cena .tscn
        skeleton_path: Caminho do nó Skeleton3D
        bone_name: Nome do osso alvo (ponta da chain IK)
        target_node_path: Path para o nó alvo do IK (ex: "../Target")
        chain_length: Número de ossos na chain (default: 2)
        iterations: Número de iterações do solver (default: 10)
    
    Returns:
        dict com status da operação
    """
    try:
        content = _read_scene(scene_path)
        skeleton = _find_skeleton_node(content, skeleton_path)
        
        if not skeleton:
            return {"ok": False, "error": f"Skeleton3D não encontrado em: {skeleton_path}"}
        
        import re
        
        # Verifica se o osso existe
        bone_pattern = rf'bones/(\d+)/name\s*=\s*"{re.escape(bone_name)}"'
        if not re.search(bone_pattern, skeleton["block"]):
            return {"ok": False, "error": f"Osso '{bone_name}' não encontrado no skeleton"}
        
        # Cria o nó SkeletonIK3D
        skeleton_name = skeleton["name"]
        ik_name = f"SkeletonIK3D_{bone_name}"
        
        # Gera UID único
        import uuid
        uid = str(uuid.uuid4()).replace("-", "")[:16]
        
        ik_node = (
            f'\n[node name="{ik_name}" type="SkeletonIK3D" parent="{skeleton_name}"]\n'
            f'root_bone = "{bone_name}"\n'
            f'chain_length = {chain_length}\n'
            f'iterations = {iterations}\n'
        )
        
        if target_node_path:
            ik_node += f'target = NodePath("{target_node_path}")\n'
        
        ik_node += (
            f'use_magnet = false\n'
            f'_import_path = NodePath("")\n'
            f'unique_name_in_owner = false\n'
            f'uid = "uid://{uid}"\n'
        )
        
        # Insere após o nó skeleton
        insert_pos = skeleton["end"]
        new_content = content[:insert_pos] + ik_node + content[insert_pos:]
        
        _write_scene(scene_path, new_content)
        
        return {
            "ok": True,
            "ik_node_name": ik_name,
            "bone_name": bone_name,
            "chain_length": chain_length,
            "iterations": iterations,
            "message": f"SkeletonIK3D '{ik_name}' criado para osso '{bone_name}'",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao criar IK chain: {e}"}


def get_skeleton_info(
    scene_path: str,
    skeleton_path: str,
) -> dict:
    """Obtém informações completas de um Skeleton3D.
    
    Args:
        scene_path: Caminho da cena .tscn
        skeleton_path: Caminho do nó Skeleton3D
    
    Returns:
        dict com bone_count, bones, ik_chains, anim_players
    """
    try:
        content = _read_scene(scene_path)
        skeleton = _find_skeleton_node(content, skeleton_path)
        
        if not skeleton:
            return {"ok": False, "error": f"Skeleton3D não encontrado em: {skeleton_path}"}
        
        import re
        
        # Lista bones
        bones = []
        for match in re.finditer(r'bones/(\d+)/name\s*=\s*"([^"]+)"', skeleton["block"]):
            idx = match.group(1)
            name = match.group(2)
            parent_match = re.search(rf'bones/{idx}/parent\s*=\s*(\d+)', skeleton["block"])
            parent = int(parent_match.group(1)) if parent_match else -1
            bones.append({"index": int(idx), "name": name, "parent": parent})
        
        # Procura SkeletonIK3D filhos
        skeleton_name = skeleton["name"]
        ik_chains = []
        for match in re.finditer(
            rf'\[node\s+name="([^"]*)"[^\]]*type="SkeletonIK3D"[^\]]*parent="{re.escape(skeleton_name)}"[^\]]*\]'
            r'([\s\S]*?)(?=\n\[node\b|\Z)',
            content
        ):
            ik_name = match.group(1)
            ik_block = match.group(2)
            root_bone = re.search(r'root_bone\s*=\s*"([^"]*)"', ik_block)
            chain_len = re.search(r'chain_length\s*=\s*(\d+)', ik_block)
            ik_chains.append({
                "name": ik_name,
                "root_bone": root_bone.group(1) if root_bone else "",
                "chain_length": int(chain_len.group(1)) if chain_len else 2,
            })
        
        return {
            "ok": True,
            "skeleton_name": skeleton_name,
            "skeleton_path": skeleton_path,
            "bone_count": len(bones),
            "bones": bones,
            "ik_chains": ik_chains,
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao obter info do skeleton: {e}"}
