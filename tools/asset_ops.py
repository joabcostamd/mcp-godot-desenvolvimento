"""asset_ops — Operações de importação de assets (texturas, áudio).

Fase 2: import_texture, import_sprite_sheet, import_audio.
Fatia 3.8: presets de import por categoria (pixel, 3d, ui).
Fatia 3.13: license_audit — gate de licença no import.
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

from tools.project_ops import _get_active_project, _check_path_traversal
from tools.scene_ops import _run_compile_test


# ── Fatia 3.8: Presets de import ──────────────────────────

IMPORT_PRESETS = {
    "pixel": {
        "compress/mode": "0",           # Lossless
        "mipmaps/generate": "false",
        "process/fix_alpha_border": "false",
        "roughness/mode": "0",
    },
    "3d": {
        "compress/mode": "2",           # VRAM Compressed
        "mipmaps/generate": "true",
        "detect_3d/compress_to": "1",   # BC1/BC3
    },
    "ui": {
        "compress/mode": "0",           # Lossless
        "mipmaps/generate": "false",
        "process/fix_alpha_border": "true",
        "roughness/mode": "0",
    },
}

CATEGORY_TO_PRESET = {
    "pixel": "pixel", "pixel_art": "pixel", "pixelart": "pixel",
    "3d": "3d", "realistic": "3d", "realista": "3d", "low_poly": "3d",
    "ui": "ui", "hud": "ui", "menu": "ui", "icon": "ui", "icone": "ui",
}


def _detect_preset(category: str) -> str | None:
    """Mapeia uma categoria para o nome do preset."""
    cat = category.strip().lower().replace(" ", "_").replace("-", "_")
    return CATEGORY_TO_PRESET.get(cat)


def _apply_import_preset(target_res_path: str, preset_name: str) -> dict:
    """Cria/atualiza o arquivo .import com as configuracoes do preset.

    Godot 4 cria <arquivo>.import ao lado do asset com parametros de importacao.
    Esta funcao grava o .import com as configuracoes corretas para o preset.

    Args:
        target_res_path: Caminho relativo da textura (ex: 'assets/sprites/player.png').
        preset_name: Nome do preset ('pixel', '3d', 'ui').

    Returns:
        {"status": "success", "preset": str} ou {"status": "error"}
    """
    preset = IMPORT_PRESETS.get(preset_name)
    if not preset:
        return {"status": "error", "message": f"Preset '{preset_name}' invalido. Validos: {list(IMPORT_PRESETS.keys())}"}

    proj = _get_active_project()
    import_path = proj / (target_res_path + ".import")

    # Monta conteudo do .import no formato Godot 4
    params = "\n".join(f"{k}={v}" for k, v in preset.items())
    content = f"""[remap]

importer="texture"
type="CompressedTexture2D"

[deps]

source_file="res://{target_res_path}"
dest_files=[]

[params]

{params}
"""
    import_path.parent.mkdir(parents=True, exist_ok=True)
    import_path.write_text(content, encoding="utf-8")

    return {"status": "success", "preset": preset_name}


def import_texture(source_path: str, target_res_path: str, category: str = "") -> dict:
    """Importa uma textura para o projeto com preset automatico (Fatia 3.8).

    Args:
        source_path: Caminho absoluto do arquivo fonte (fora do projeto).
        target_res_path: Caminho relativo no projeto (ex: 'assets/sprites/player.png').
        category: Categoria do asset ('pixel', '3d', 'ui', etc). Usado para aplicar
                  o preset de import correto automaticamente.

    Returns:
        {"status": "success", "res_path": str, "preset": str|None}
    """
    proj = _get_active_project()

    violation = _check_path_traversal(target_res_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    src = Path(source_path)
    dst = proj / target_res_path

    if not src.exists():
        return {"status": "error", "message": f"Arquivo fonte '{source_path}' não encontrado."}

    if src.suffix.lower() not in (".png", ".jpg", ".jpeg", ".bmp", ".svg"):
        return {"status": "error", "message": f"Formato '{src.suffix}' não suportado. Use PNG, JPG, BMP ou SVG."}

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

    # ── Fatia 3.8: Aplicar preset de import ─────────────────
    preset_applied = None
    if category:
        preset_name = _detect_preset(category)
        if preset_name:
            pr = _apply_import_preset(target_res_path, preset_name)
            if pr["status"] == "success":
                preset_applied = preset_name

    # Marca para reimport pendente (executado em compile_test/run_game)
    from tools.runtime_ops import mark_pending_compile
    mark_pending_compile()

    result = {"status": "success", "res_path": target_res_path}
    if preset_applied:
        result["preset"] = preset_applied
    return result


def import_sprite_sheet(
    source_path: str, target_res_path: str,
    frame_width: int, frame_height: int,
    target_scene_path: str, target_node_path: str,
    animations: list[dict],
    category: str = "",
) -> dict:
    """Importa uma sprite sheet e configura animações em um AnimatedSprite2D.

    Args:
        source_path: Caminho absoluto da sprite sheet.
        target_res_path: Caminho no projeto para a textura.
        frame_width: Largura de cada frame.
        frame_height: Altura de cada frame.
        target_scene_path: Cena com o AnimatedSprite2D.
        target_node_path: Nó AnimatedSprite2D.
        animations: Lista de {"name": str, "frame_indices": [int], "fps": float}.

    Returns:
        {"status": "success", "sprite_frames_path": str}
    """
    proj = _get_active_project()

    violation = _check_path_traversal(target_res_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    violation2 = _check_path_traversal(target_scene_path, proj)
    if violation2:
        return {"status": "error", "message": violation2}

    # Importa textura primeiro
    r = import_texture(source_path, target_res_path, category=category)
    if r["status"] != "success":
        return r

    # Cria SpriteFrames (.tres)
    sf_name = Path(target_res_path).stem + "_frames"
    sf_path = str(Path(target_res_path).with_suffix(".tres"))

    sf_content = f"""[gd_resource type="SpriteFrames" load_steps=2 format=2]

[ext_resource type="Texture2D" path="res://{target_res_path}" id="1_texture"]

[resource]
animations = [
"""
    for anim in animations:
        name = anim["name"]
        fps = anim.get("fps", 10.0)
        indices = anim.get("frame_indices", [0])
        sf_content += f'{{\n"frames": [\n'
        for idx in indices:
            row = idx // (1 if frame_width == 0 else 1)  # simplificado
            sf_content += (
                f'ExtResource("1_texture"), '
                f'Rect2({(idx % (1 if frame_width == 0 else 1)) * frame_width}, '
                f'{row * frame_height}, {frame_width}, {frame_height}),\n'
            )
        sf_content += f'],\n"loop": true,\n"name": "{name}",\n"speed": {fps}\n}},\n'
    sf_content += "]\n"

    sf_full = proj / sf_path
    sf_full.write_text(sf_content, encoding="utf-8")

    # Configura o AnimatedSprite2D
    from tools.scene_ops import set_node_property as _set_prop
    _set_prop(target_scene_path, target_node_path, "sprite_frames", f'ExtResource("{sf_path}")')

    from tools.runtime_ops import mark_pending_compile
    mark_pending_compile()

    return {"status": "success", "sprite_frames_path": sf_path}


def import_audio(source_path: str, target_res_path: str) -> dict:
    """Importa um arquivo de áudio para o projeto.

    Args:
        source_path: Caminho absoluto do arquivo fonte.
        target_res_path: Caminho relativo no projeto.

    Returns:
        {"status": "success", "res_path": str}
    """
    proj = _get_active_project()

    violation = _check_path_traversal(target_res_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    src = Path(source_path)
    dst = proj / target_res_path

    if not src.exists():
        return {"status": "error", "message": f"Arquivo fonte '{source_path}' não encontrado."}

    if src.suffix.lower() not in (".wav", ".ogg", ".mp3"):
        return {"status": "error", "message": f"Formato '{src.suffix}' não suportado. Use WAV, OGG ou MP3."}

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

    from tools.runtime_ops import mark_pending_compile
    mark_pending_compile()

    return {"status": "success", "res_path": target_res_path}


# ── GAP #10: Preview de Assets ────────────────────────────────────────

def preview_asset(asset_path: str) -> dict:
    """Retorna preview de um asset como base64. GAP #10.

    Texturas: retorna PNG/JPEG base64 diretamente.
    Audio: retorna metadados (duracao, sample rate, canais).
    Cenas: retorna a arvore de nos.

    Args:
        asset_path: Caminho relativo do asset no projeto.

    Returns:
        {"status": "success", "type": "texture"|"audio"|"scene", "preview": ...}
    """
    import base64

    proj = _get_active_project()
    full_path = proj / asset_path

    if not full_path.exists():
        return {"status": "error", "message": f"Asset '{asset_path}' nao encontrado."}

    suffix = full_path.suffix.lower()

    if suffix in (".png", ".jpg", ".jpeg", ".bmp", ".webp"):
        img_data = full_path.read_bytes()
        b64 = base64.b64encode(img_data).decode("ascii")
        return {"status": "success", "type": "texture", "format": suffix.lstrip("."),
                "size_bytes": len(img_data), "image_base64": b64}

    if suffix in (".wav", ".ogg", ".mp3"):
        info = {"format": suffix.lstrip("."), "size_bytes": full_path.stat().st_size}
        if suffix == ".wav":
            try:
                import struct
                data = full_path.read_bytes()
                if data[:4] == b"RIFF" and len(data) > 40:
                    channels = struct.unpack_from("<H", data, 22)[0]
                    sample_rate = struct.unpack_from("<I", data, 24)[0]
                    bits = struct.unpack_from("<H", data, 34)[0]
                    duration = (len(data) - 44) / (sample_rate * channels * bits / 8)
                    info.update({"channels": channels, "sample_rate": sample_rate,
                                 "bits_per_sample": bits, "duration_sec": round(duration, 2)})
            except Exception:
                pass
        return {"status": "success", "type": "audio", "preview": info}

    if suffix == ".tscn":
        from tools.scene_ops import load_scene_tree
        return load_scene_tree(asset_path)

    return {"status": "error", "message": f"Preview nao suportado para '{suffix}'."}


# ═══════════════════════════════════════════════════════════════════════
# FATIA 3.5 — validate_asset_game_ready (op do rollup asset_manage)
# ═══════════════════════════════════════════════════════════════════════

# Orçamentos de polycount por plataforma (conservador)
_POLYCOUNT_BUDGETS = {
    "mobile_low":   {"character": 1000, "prop": 500,  "environment": 5000},
    "mobile_high":  {"character": 2000, "prop": 1000, "environment": 10000},
    "desktop_mid":  {"character": 8000, "prop": 3000, "environment": 20000},
    "desktop_high": {"character": 20000,"prop": 8000, "environment": 50000},
    "console":      {"character": 20000,"prop": 8000, "environment": 50000},
}

# Resolução máxima de textura por plataforma (pixels no lado maior)
_IMAGE_RESOLUTION_BUDGETS = {
    "mobile_low":   512,
    "mobile_high":  1024,
    "desktop_mid":  2048,
    "desktop_high": 4096,
    "console":      4096,
}

# Tipos de nó de colisão a detectar no .tscn
_COLLISION_NODE_TYPES = {
    "CollisionShape2D", "CollisionShape3D",
    "StaticBody2D", "StaticBody3D",
    "RigidBody2D", "RigidBody3D",
    "CharacterBody2D", "CharacterBody3D",
    "Area2D", "Area3D",
}

# Tipos de nó indicando rig
_RIG_INDICATORS = {"Skeleton3D", "Skeleton2D", "BoneAttachment3D"}


def validate_asset_game_ready(args: dict | None = None) -> dict:
    """Valida se um asset importado atende aos critérios game-ready.

    Verifica 5 critérios: escala, colisão, material, polycount, rig.
    Usa 3 camadas de inspeção: Python offline → .import → Runtime Bridge.

    Args:
        asset_path: Caminho do asset no projeto (ex: 'res://assets/player.glb').
        asset_type: 'character'|'environment'|'prop'|'ui'|'auto' (default: 'auto').
        platform: 'mobile_low'|'mobile_high'|'desktop_mid'|'desktop_high'|'console'
                  (default: 'desktop_mid').

    Returns:
        dict com status, checks por categoria, all_pass, game_ready, issues, suggestions.
    """
    if args is None:
        args = {}

    asset_path = args.get("asset_path", "")
    asset_type = args.get("asset_type", "auto")
    platform = args.get("platform", "desktop_mid")

    # ── Validação de entrada ──────────────────────────────────────────
    if not asset_path:
        return {"status": "error", "message": "asset_path é obrigatório."}

    proj = _get_active_project()

    # Resolve caminho: aceita res:// ou relativo
    if asset_path.startswith("res://"):
        rel_path = asset_path[6:]
    else:
        rel_path = asset_path.lstrip("/")

    full_path = proj / rel_path

    if not full_path.exists():
        return {
            "status": "error",
            "asset_path": asset_path,
            "message": f"Asset não encontrado: {full_path}",
        }

    if platform not in _POLYCOUNT_BUDGETS:
        return {
            "status": "error",
            "asset_path": asset_path,
            "message": f"Plataforma inválida: '{platform}'. Use: {list(_POLYCOUNT_BUDGETS.keys())}",
        }

    valid_types = {"auto", "character", "environment", "prop", "ui"}
    if asset_type not in valid_types:
        return {
            "status": "error",
            "asset_path": asset_path,
            "message": f"asset_type inválido: '{asset_type}'. Use: {list(valid_types)}",
        }

    # ── Camada 1: Inspeção offline (Python) ───────────────────────────
    suffix = full_path.suffix.lower()
    glb_info = {}
    image_info = {}
    tscn_info = {"nodes": []}
    method = "file_only"

    if suffix in (".glb", ".gltf"):
        glb_info = _parse_glb_info(str(full_path))
    elif suffix in (".png", ".jpg", ".jpeg", ".bmp", ".webp"):
        image_info = _parse_image_info(str(full_path))
    elif suffix == ".tscn":
        tscn_info = _parse_tscn_for_validation(str(full_path), proj)

    # ── Camada 2: Parse do .import ────────────────────────────────────
    import_info = _parse_import_file(str(full_path))

    # ── Detecção automática de asset_type ─────────────────────────────
    if asset_type == "auto":
        asset_type = _detect_asset_type(suffix, glb_info, tscn_info)
    # Normaliza environment → usa mesmo budget que environment
    display_type = asset_type

    # ── Camada 3: Runtime Bridge (opcional) ───────────────────────────
    bridge_info = _inspect_via_bridge(rel_path, proj)
    if bridge_info:
        method = "hybrid"
        # Merge: bridge info complementa (não sobrescreve) o offline
        if not glb_info and bridge_info.get("glb_info"):
            glb_info = bridge_info["glb_info"]
        if bridge_info.get("tscn_nodes"):
            tscn_info["nodes"].extend(bridge_info["tscn_nodes"])

    # ── 5 Checks ──────────────────────────────────────────────────────
    scale_check = _check_scale(glb_info, import_info, tscn_info)
    collision_check = _check_collision(tscn_info, asset_type)
    material_check = _check_material(glb_info, import_info, tscn_info, suffix)
    polycount_check = _check_polycount(glb_info, image_info, platform, asset_type)
    rig_check = _check_rig(glb_info, tscn_info, asset_type)

    checks = {
        "scale": scale_check,
        "collision": collision_check,
        "material": material_check,
        "polycount": polycount_check,
        "rig": rig_check,
    }

    # ── Consolidação ──────────────────────────────────────────────────
    all_pass = all(
        c.get("pass", True) or not c.get("applicable", True)
        for c in checks.values()
    )
    issues = []
    suggestions = []

    for name, check in checks.items():
        if not check.get("pass", True) and check.get("applicable", True):
            issues.append(check.get("message", f"Falha em {name}"))
        if check.get("suggestion"):
            suggestions.append(check["suggestion"])

    status = "success" if all_pass else "warning"

    return {
        "status": status,
        "asset_path": asset_path,
        "asset_type": display_type,
        "platform": platform,
        "checks": checks,
        "all_pass": all_pass,
        "game_ready": all_pass,
        "issues": issues,
        "suggestions": suggestions,
        "method": method,
        "message": (
            "✅ Asset game-ready: todos os checks passaram."
            if all_pass
            else f"⚠️ Asset NÃO está game-ready: {len(issues)} de 5 checks falharam."
        ),
    }


# ── Funções auxiliares ──────────────────────────────────────────────────

def _parse_glb_info(file_path: str) -> dict:
    """Parse offline de GLB/glTF com pygltflib.

    Returns:
        dict com: triangles, vertices, materials, has_skin, has_skeleton,
                  bounding_box {min: [x,y,z], max: [x,y,z]}, node_count, mesh_count.
        dict vazio se o parse falhar.
    """
    try:
        import pygltflib
        gltf = pygltflib.GLTF2().load(file_path)

        total_triangles = 0
        total_vertices = 0
        mesh_count = len(gltf.meshes or [])

        for mesh in (gltf.meshes or []):
            for primitive in (mesh.primitives or []):
                # Conta triângulos via indices
                if primitive.indices is not None:
                    accessor = gltf.accessors[primitive.indices]
                    total_triangles += accessor.count // 3
                # Conta vértices via POSITION
                if primitive.attributes and hasattr(primitive.attributes, 'POSITION') and primitive.attributes.POSITION is not None:
                    pos_accessor = gltf.accessors[primitive.attributes.POSITION]
                    total_vertices += pos_accessor.count
                elif primitive.indices is not None:
                    # Fallback: se tem indices mas não POSITION explícito, estima
                    accessor = gltf.accessors[primitive.indices]
                    total_vertices += accessor.count

        # Materiais
        material_count = len(gltf.materials or [])
        material_names = [m.name or f"material_{i}" for i, m in enumerate(gltf.materials or [])]

        # Rig: skins
        has_skin = len(gltf.skins or []) > 0
        skin_joints = sum(len(s.joints) for s in (gltf.skins or []))

        # Bounding box (min/max dos vértices)
        bbox_min = [float("inf")] * 3
        bbox_max = [float("-inf")] * 3

        for mesh in (gltf.meshes or []):
            for primitive in (mesh.primitives or []):
                if primitive.attributes and hasattr(primitive.attributes, 'POSITION') and primitive.attributes.POSITION is not None:
                    pos_acc = gltf.accessors[primitive.attributes.POSITION]
                    # Tenta ler buffer de vértices
                    try:
                        if hasattr(pos_acc, 'min') and pos_acc.min is not None:
                            for i in range(3):
                                bbox_min[i] = min(bbox_min[i], pos_acc.min[i])
                                bbox_max[i] = max(bbox_max[i], pos_acc.max[i])
                    except Exception:
                        pass

        # Se não conseguiu bounding box, usa defaults
        if bbox_min[0] == float("inf"):
            bbox_min = [0.0, 0.0, 0.0]
            bbox_max = [1.0, 1.0, 1.0]

        return {
            "triangles": total_triangles,
            "vertices": total_vertices,
            "material_count": material_count,
            "material_names": material_names,
            "has_skin": has_skin,
            "skin_joints": skin_joints,
            "mesh_count": mesh_count,
            "node_count": len(gltf.nodes or []),
            "bounding_box": {
                "min": bbox_min,
                "max": bbox_max,
            },
            "size": {
                "x": bbox_max[0] - bbox_min[0],
                "y": bbox_max[1] - bbox_min[1],
                "z": bbox_max[2] - bbox_min[2],
            },
        }
    except Exception as e:
        return {"error": str(e)}


def _parse_image_info(file_path: str) -> dict:
    """Parse de imagem com Pillow.

    Returns:
        dict com: width, height, mode, format, size_bytes.
        dict vazio se falhar.
    """
    try:
        from PIL import Image
        img = Image.open(file_path)
        w, h = img.size
        return {
            "width": w,
            "height": h,
            "max_dimension": max(w, h),
            "mode": img.mode,
            "format": img.format,
            "size_bytes": Path(file_path).stat().st_size,
        }
    except Exception:
        return {}


def _parse_tscn_for_validation(tscn_path: str, proj: Path) -> dict:
    """Parse de .tscn focado em validação: nós de colisão, rig, material.

    Reusa _parse_tscn_content de scene_ops.py se disponível.
    """
    result = {"nodes": [], "has_collision": False, "has_rig": False, "has_material_override": False}

    try:
        from tools.scene_ops import _parse_tscn_content
        _, parsed_nodes = _parse_tscn_content(tscn_path, proj)
    except Exception:
        # Fallback: parse manual com regex
        content = Path(tscn_path).read_text(encoding="utf-8", errors="replace")
        parsed_nodes = []
        for m in __import__("re").finditer(
            r'\[node\s+name="([^"]*)"(?:\s+type="([^"]*)")?(?:\s+parent="([^"]*)")?',
            content,
        ):
            parsed_nodes.append({
                "name": m.group(1),
                "type": m.group(2) or "Node",
                "parent": m.group(3) or ".",
            })

    for node in parsed_nodes:
        node_type = node.get("type", "")
        result["nodes"].append({"name": node.get("name", ""), "type": node_type})

        if node_type in _COLLISION_NODE_TYPES:
            result["has_collision"] = True
        if node_type in _RIG_INDICATORS or node_type == "ImporterMeshInstance3D":
            result["has_rig"] = True
        # Verifica material_override no corpo do nó
        props = node.get("properties", {})
        if "material_override" in props or "surface_material_override" in props:
            result["has_material_override"] = True

    # Verificação extra: busca por skeleton_path no conteúdo bruto
    if not result["has_rig"]:
        try:
            content = Path(tscn_path).read_text(encoding="utf-8", errors="replace")
            if 'skeleton_path = NodePath("../Skeleton3D")' in content or 'skeleton_path = NodePath("' in content:
                result["has_rig"] = True
        except Exception:
            pass

    return result


def _parse_import_file(asset_path: str) -> dict:
    """Parse do arquivo .import do Godot (formato INI-like).

    Returns:
        dict com sections [remap], [deps], [params].
        dict vazio se o .import não existir.
    """
    import_path = asset_path + ".import"
    import_file = Path(import_path)
    result = {}

    if not import_file.exists():
        return result

    try:
        import configparser
        cp = configparser.ConfigParser()
        cp.read(str(import_file), encoding="utf-8")

        for section in cp.sections():
            result[section] = dict(cp.items(section))

        # Extrai campos chave dos params
        params = result.get("params", {})
        if "meshes/import_scale" in params:
            result["import_scale"] = float(params["meshes/import_scale"])
        if "meshes/compress" in params:
            result["mesh_compress"] = params["meshes/compress"]
        if "meshes/generate_lods" in params:
            result["generate_lods"] = params["meshes/generate_lods"].lower() == "true"
        if "skins/use_named_skins" in params:
            result["use_named_skins"] = params["skins/use_named_skins"].lower() == "true"
        if "animation/import" in params:
            result["animation_import"] = params["animation/import"].lower() == "true"

        # Importer type
        if "importer" in params:
            result["importer_type"] = params["importer"]

    except Exception:
        pass

    return result


def _inspect_via_bridge(rel_path: str, proj: Path) -> dict | None:
    """Tenta inspecionar o asset via Runtime Bridge (GDScript).

    Returns:
        dict com glb_info, tscn_nodes se o bridge estiver disponível.
        None se o bridge não estiver disponível.
    """
    try:
        from tools.bridge import dispatch_operation

        # GDScript para inspecionar o asset
        gdscript = f'''
var result = {{}}
var res = load("res://{rel_path}")
if res is PackedScene:
    var instance = res.instantiate()
    var nodes = []
    _inspect_node(instance, nodes)
    result["tscn_nodes"] = nodes
    result["node_count"] = nodes.size()
    instance.queue_free()
return JSON.stringify(result)
'''
        response = dispatch_operation("execute_gdscript", {"code": gdscript})
        if response and response.get("status") == "success":
            import json
            return json.loads(response.get("result", "{}"))
    except Exception:
        pass

    return None


def _detect_asset_type(suffix: str, glb_info: dict, tscn_info: dict) -> str:
    """Detecta automaticamente o tipo de asset."""
    # GLB com rig → character
    if glb_info and glb_info.get("has_skin"):
        return "character"
    if tscn_info.get("has_rig"):
        return "character"

    # GLB sem rig → environment ou prop (baseado em tamanho)
    if glb_info:
        bbox = glb_info.get("bounding_box", {})
        size = bbox.get("size", {"x": 1, "y": 1, "z": 1})
        max_dim = max(size.get("x", 1), size.get("y", 1), size.get("z", 1))
        if max_dim > 10.0:
            return "environment"
        return "prop"

    # TSCN → analisa tipos de nós
    if tscn_info.get("nodes"):
        node_types = {n.get("type", "") for n in tscn_info["nodes"]}
        if node_types & {"Control", "TextureRect", "Button", "Label", "Panel"}:
            return "ui"
        if node_types & {"TileMap", "TileMapLayer", "NavigationRegion3D"}:
            return "environment"
        if node_types & {"CharacterBody2D", "CharacterBody3D", "AnimatedSprite2D", "AnimatedSprite3D"}:
            return "character"

    # Imagem → ui por padrão
    if suffix in (".png", ".jpg", ".jpeg", ".bmp", ".webp"):
        return "ui"

    return "prop"


def _check_scale(glb_info: dict, import_info: dict, tscn_info: dict) -> dict:
    """Verifica se a escala do asset é plausível (0.01–100.0 unidades Godot)."""
    MIN_SCALE = 0.01
    MAX_SCALE = 100.0
    scale_value = 1.0
    source = "default"

    # Prioridade 1: .import params
    if import_info.get("import_scale") is not None:
        scale_value = import_info["import_scale"]
        source = ".import file"

    # Prioridade 2: bounding box do GLB
    elif glb_info and glb_info.get("size"):
        size = glb_info["size"]
        # Usa a maior dimensão como referência
        max_dim = max(size.get("x", 1), size.get("y", 1), size.get("z", 1))
        scale_value = max_dim
        source = "GLB bounding box"

    if scale_value < MIN_SCALE:
        return {
            "pass": False,
            "applicable": True,
            "value": scale_value,
            "unit": "godot_units",
            "source": source,
            "message": f"Escala muito pequena ({scale_value:.6f}). Mínimo: {MIN_SCALE}",
            "suggestion": f"Aumente o Root Scale no import para ≥ {MIN_SCALE}",
        }
    elif scale_value > MAX_SCALE:
        return {
            "pass": False,
            "applicable": True,
            "value": scale_value,
            "unit": "godot_units",
            "source": source,
            "message": f"Escala muito grande ({scale_value:.1f}). Máximo: {MAX_SCALE}",
            "suggestion": f"Reduza o Root Scale no import para ≤ {MAX_SCALE} ou normalize no Blender",
        }
    else:
        return {
            "pass": True,
            "applicable": True,
            "value": scale_value,
            "unit": "godot_units",
            "source": source,
            "message": f"Escala dentro do range plausível ({MIN_SCALE}–{MAX_SCALE})",
        }


def _check_collision(tscn_info: dict, asset_type: str) -> dict:
    """Verifica presença de colisão no asset."""
    # Tipos que precisam de colisão
    if asset_type in ("character", "environment"):
        applicable = True
    elif asset_type == "prop":
        applicable = True  # recomendado, mas não obrigatório
    else:
        return {"pass": True, "applicable": False, "message": "Colisão não se aplica a assets de UI."}

    has_collision = tscn_info.get("has_collision", False)

    if has_collision:
        return {
            "pass": True,
            "applicable": True,
            "message": "Colisão detectada (CollisionShape/StaticBody/RigidBody presente).",
        }

    if asset_type == "character":
        return {
            "pass": False,
            "applicable": True,
            "message": "Nenhum nó de colisão encontrado. Personagem precisa de CollisionShape + CharacterBody/StaticBody.",
            "suggestion": "Adicione um CollisionShape2D/3D ao corpo do personagem.",
        }
    elif asset_type == "environment":
        return {
            "pass": False,
            "applicable": True,
            "message": "Nenhum nó de colisão encontrado. Ambiente precisa de StaticBody + CollisionShape.",
            "suggestion": "Adicione um StaticBody3D com CollisionShape3D à cena.",
        }
    else:
        # prop: recomendado mas não bloqueia
        return {
            "pass": True,
            "applicable": True,
            "message": "Nenhum nó de colisão encontrado. Props geralmente têm colisão (recomendado).",
            "suggestion": "Considere adicionar um StaticBody com CollisionShape.",
        }


def _check_material(glb_info: dict, import_info: dict, tscn_info: dict, suffix: str) -> dict:
    """Verifica compatibilidade de materiais."""
    # Apenas para assets 3D
    if suffix not in (".glb", ".gltf"):
        return {"pass": True, "applicable": False, "message": "Verificação de material aplica-se apenas a modelos 3D."}

    material_count = glb_info.get("material_count", 0)
    material_names = glb_info.get("material_names", [])

    if material_count == 0:
        return {
            "pass": False,
            "applicable": True,
            "materials_found": 0,
            "message": "Nenhum material encontrado no modelo 3D.",
            "suggestion": "Adicione pelo menos um StandardMaterial3D ao modelo no Blender/software 3D.",
        }

    # Verifica materiais suspeitos (nomes que indicam shader problemático)
    incompatible = []
    for name in material_names:
        if name.lower().startswith("shader") or "custom" in name.lower():
            incompatible.append(name)

    if incompatible:
        return {
            "pass": False,
            "applicable": True,
            "materials_found": material_count,
            "incompatible": incompatible,
            "message": f"{len(incompatible)} material(is) potencialmente incompatível(is): {', '.join(incompatible)}. Prefira StandardMaterial3D ou ORMMaterial3D.",
            "suggestion": "Substitua ShaderMaterial por StandardMaterial3D para compatibilidade com a luz da cena.",
        }

    return {
        "pass": True,
        "applicable": True,
        "materials_found": material_count,
        "incompatible": [],
        "message": f"{material_count} material(is) encontrado(s) — compatível(is) com o pipeline PBR do Godot.",
    }


def _check_polycount(glb_info: dict, image_info: dict, platform: str, asset_type: str) -> dict:
    """Verifica polycount/resolução contra o orçamento da plataforma."""
    budgets = _POLYCOUNT_BUDGETS.get(platform, _POLYCOUNT_BUDGETS["desktop_mid"])
    budget = budgets.get(asset_type, budgets.get("prop", 5000))

    # Caso GLB/3D
    if glb_info and glb_info.get("triangles", 0) > 0:
        triangles = glb_info["triangles"]
        vertices = glb_info.get("vertices", triangles * 3)
        if triangles <= budget:
            pct = (triangles / budget) * 100 if budget > 0 else 0
            return {
                "pass": True,
                "applicable": True,
                "triangles": triangles,
                "vertices": vertices,
                "budget": budget,
                "platform": platform,
                "message": f"{triangles:,}/{budget:,} tris ({pct:.1f}%) — dentro do orçamento.",
            }
        else:
            pct = (triangles / budget) * 100 if budget > 0 else 0
            return {
                "pass": False,
                "applicable": True,
                "triangles": triangles,
                "vertices": vertices,
                "budget": budget,
                "platform": platform,
                "message": f"{triangles:,}/{budget:,} tris ({pct:.1f}%) — EXCEDE o orçamento de {platform}.",
                "suggestion": f"Reduza o polycount para ≤ {budget:,} tris (decimate no Blender ou use LODs).",
            }

    # Caso imagem/2D
    if image_info and image_info.get("max_dimension", 0) > 0:
        max_dim = image_info["max_dimension"]
        img_budget = _IMAGE_RESOLUTION_BUDGETS.get(platform, 2048)
        if max_dim <= img_budget:
            return {
                "pass": True,
                "applicable": True,
                "max_dimension": max_dim,
                "budget": img_budget,
                "platform": platform,
                "message": f"Resolução {image_info.get('width',0)}×{image_info.get('height',0)}px — dentro do orçamento ({img_budget}px).",
            }
        else:
            return {
                "pass": False,
                "applicable": True,
                "max_dimension": max_dim,
                "budget": img_budget,
                "platform": platform,
                "message": f"Resolução {image_info.get('width',0)}×{image_info.get('height',0)}px — EXCEDE o orçamento de {img_budget}px.",
                "suggestion": f"Redimensione a textura para ≤ {img_budget}px no lado maior.",
            }

    # Sem dados → não aplica
    return {"pass": True, "applicable": False, "message": "Sem dados de polycount/resolução para verificar."}


def _check_rig(glb_info: dict, tscn_info: dict, asset_type: str) -> dict:
    """Verifica presença de rig (Skeleton + Skin) para personagens."""
    if asset_type != "character":
        return {"pass": True, "applicable": False, "message": "Rig só é obrigatório para personagens."}

    has_skin = glb_info.get("has_skin", False)
    skin_joints = glb_info.get("skin_joints", 0)
    has_rig_tscn = tscn_info.get("has_rig", False)

    if has_skin:
        return {
            "pass": True,
            "applicable": True,
            "bones": skin_joints,
            "has_skin": True,
            "message": f"Skeleton3D com {skin_joints} bones + Skin weights detectado.",
        }

    if has_rig_tscn:
        return {
            "pass": True,
            "applicable": True,
            "has_skin": False,
            "message": "Skeleton3D detectado na cena importada.",
        }

    return {
        "pass": False,
        "applicable": True,
        "has_skin": False,
        "bones": 0,
        "message": "Nenhum rig/Skeleton detectado. Personagem precisa de rig para animação.",
        "suggestion": "Adicione um Armature + Skin no Blender/software 3D antes de exportar o GLB.",
    }

# ── Fatia 3.7: Pipeline de arte travado ──────────────────

def run_art_pipeline(
    description: str,
    category: str = "torre",
    style: str = "scifi",
    save_dir: str | None = None,
) -> dict:
    """Pipeline completo de arte com gate de validacao (Fatia 3.7).

    Orquestra 5 etapas sequenciais com trava no final:
    1. generate_game_art     — gera arte (com style_lock do brief)
    2. remove_background     — remove fundo
    3. optimize_sprite       — otimiza
    4. import_texture        — importa com preset da categoria (Fatia 3.8)
    5. validate_asset_game_ready — GATE: se falhar, bloqueia e reporta

    Args:
        description: Descricao em linguagem natural do asset.
        category: Categoria (torre, inimigo, personagem, bioma, etc).
        style: Estilo visual (scifi, fantasia, pixel, etc).
        save_dir: Diretorio para salvar (opcional).

    Returns:
        {"status": "success", "pipeline": [...], "asset_path": str}
        ou {"status": "error", "stage": str, "message": str, "pipeline": [...]}
    """
    pipeline_log = []
    asset_path = None

    def _log(stage: str, result: dict):
        pipeline_log.append({"stage": stage, "status": result.get("status", "?"), "detail": str(result)[:200]})

    # ── Etapa 1: Gerar arte ──────────────────────────
    try:
        from tools.art_ops import generate_game_art
        gen = generate_game_art(description=description, category=category, style=style, save_dir=save_dir)
        _log("1.generate", gen)
        if gen.get("status") != "success":
            return {"status": "error", "stage": "1.generate", "message": gen.get("message", "Falha na geracao"), "pipeline": pipeline_log}
        # Extrai caminho do asset gerado
        asset_path = gen.get("sprite_sheet", "") or gen.get("res_path", "")
        if not asset_path:
            return {"status": "error", "stage": "1.generate", "message": "Geracao OK mas sem caminho de asset", "pipeline": pipeline_log}
    except Exception as e:
        _log("1.generate", {"status": "error", "message": str(e)})
        return {"status": "error", "stage": "1.generate", "message": f"Excecao: {e}", "pipeline": pipeline_log}

    # ── Etapa 2: Remover fundo ────────────────────────
    try:
        from tools.art_postprocess import remove_background
        bg = remove_background(image_path=asset_path)
        _log("2.remove_background", bg)
        if bg.get("status") == "success":
            asset_path = bg.get("output_path", asset_path)
    except Exception as e:
        _log("2.remove_background", {"status": "warning", "message": f"rembg pode nao estar instalado: {e}"})
        # remove_background e opcional — continua sem ele

    # ── Etapa 3: Otimizar sprite ──────────────────────
    try:
        from tools.art_postprocess import optimize_sprite
        opt = optimize_sprite(image_path=asset_path)
        _log("3.optimize", opt)
    except Exception as e:
        _log("3.optimize", {"status": "warning", "message": str(e)})

    # ── Etapa 4: Importar com preset ──────────────────
    try:
        res_path = f"assets/{category}/{Path(asset_path).name}" if asset_path else f"assets/{category}/generated.png"
        imp = import_texture(source_path=asset_path, target_res_path=res_path, category=category)
        _log("4.import", imp)
        if imp.get("status") != "success":
            return {"status": "error", "stage": "4.import", "message": imp.get("message", "Falha no import"), "pipeline": pipeline_log}
        asset_path = res_path
    except Exception as e:
        _log("4.import", {"status": "error", "message": str(e)})
        return {"status": "error", "stage": "4.import", "message": f"Excecao: {e}", "pipeline": pipeline_log}

    # ── Etapa 5: GATE — validar game-ready ────────────
    try:
        val = validate_asset_game_ready({"res_path": asset_path, "category": category})
        _log("5.validate", val)
        if val.get("status") not in ("success", "ok", "valid"):
            return {
                "status": "error",
                "stage": "5.validate",
                "message": f"Asset nao passou na validacao game-ready: {val.get('message', val.get('summary', 'Ver detalhes'))}",
                "validation": val,
                "pipeline": pipeline_log,
            }
    except Exception as e:
        _log("5.validate", {"status": "error", "message": str(e)})
        return {"status": "error", "stage": "5.validate", "message": f"Excecao na validacao: {e}", "pipeline": pipeline_log}

    # ── Sucesso ───────────────────────────────────────
    return {
        "status": "success",
        "asset_path": asset_path,
        "pipeline": pipeline_log,
        "message": f"Pipeline arte concluido: {len(pipeline_log)} etapas, asset em {asset_path}",
    }


def audit_asset_license(
    asset_path: str,
    license_str: str = "",
    project_license: str = "commercial",
) -> dict:
    """Audita a licença de um asset e registra rastreabilidade.

    Gate automático: classifica licenças como pass (compatível),
    warn (requer atribuição) ou block (incompatível). Registra
    no arquivo asset_licenses.json para rastreabilidade futura.

    Args:
        asset_path: Caminho relativo do asset no projeto.
        license_str: Identificador da licença (CC0, MIT, CC-BY, CC-BY-SA,
                     CC-BY-NC, GPL, proprietary, BSD, MPL, Unlicense, etc.).
        project_license: Tipo de licença do projeto (commercial, open_source,
                         personal).

    Returns:
        {"status": "success", "gate": "pass"|"warn"|"block",
         "license": str, "category": str, "reason": str}
    """
    proj = _get_active_project()

    # ── Validar asset_path contra path traversal ────────────
    violation = _check_path_traversal(asset_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    # ── Validar project_license ─────────────────────────────
    VALID_PROJECT = {"commercial", "open_source", "personal"}
    if project_license not in VALID_PROJECT:
        return {
            "status": "error",
            "message": f"project_license '{project_license}' inválida. Use: {sorted(VALID_PROJECT)}.",
        }

    # ── Mapa de compatibilidade ─────────────────────────────
    LICENSE_COMPAT = {
        "CC0": {"category": "public_domain", "commercial": "pass", "open_source": "pass", "personal": "pass"},
        "CC0 1.0": {"category": "public_domain", "commercial": "pass", "open_source": "pass", "personal": "pass"},
        "PD": {"category": "public_domain", "commercial": "pass", "open_source": "pass", "personal": "pass"},
        "Unlicense": {"category": "public_domain", "commercial": "pass", "open_source": "pass", "personal": "pass"},
        "MIT": {"category": "permissive", "commercial": "pass", "open_source": "pass", "personal": "pass"},
        "Apache 2.0": {"category": "permissive", "commercial": "pass", "open_source": "pass", "personal": "pass"},
        "BSD": {"category": "permissive", "commercial": "pass", "open_source": "pass", "personal": "pass"},
        "BSD 2-Clause": {"category": "permissive", "commercial": "pass", "open_source": "pass", "personal": "pass"},
        "BSD 3-Clause": {"category": "permissive", "commercial": "pass", "open_source": "pass", "personal": "pass"},
        "MPL 2.0": {"category": "weak_copyleft", "commercial": "pass", "open_source": "pass", "personal": "pass"},
        "CC-BY": {"category": "attribution", "commercial": "warn", "open_source": "pass", "personal": "pass"},
        "CC-BY 4.0": {"category": "attribution", "commercial": "warn", "open_source": "pass", "personal": "pass"},
        "CC-BY-SA": {"category": "copyleft", "commercial": "warn", "open_source": "warn", "personal": "pass"},
        "CC-BY-SA 4.0": {"category": "copyleft", "commercial": "warn", "open_source": "warn", "personal": "pass"},
        "GPL": {"category": "copyleft", "commercial": "warn", "open_source": "pass", "personal": "pass"},
        "GPL 3.0": {"category": "copyleft", "commercial": "warn", "open_source": "pass", "personal": "pass"},
        "CC-BY-NC": {"category": "non_commercial", "commercial": "block", "open_source": "warn", "personal": "pass"},
        "CC-BY-NC 4.0": {"category": "non_commercial", "commercial": "block", "open_source": "warn", "personal": "pass"},
        "CC-BY-NC-SA": {"category": "non_commercial", "commercial": "block", "open_source": "warn", "personal": "pass"},
        "CC-BY-ND": {"category": "no_derivatives", "commercial": "warn", "open_source": "warn", "personal": "pass"},
        "proprietary": {"category": "proprietary", "commercial": "block", "open_source": "block", "personal": "warn"},
        "all_rights_reserved": {"category": "proprietary", "commercial": "block", "open_source": "block", "personal": "warn"},
        "unity_asset_store": {"category": "proprietary", "commercial": "warn", "open_source": "block", "personal": "warn"},
    }

    # ── Normalizar licença ─────────────────────────────────
    if not license_str or not license_str.strip():
        return {
            "status": "error",
            "message": "Informe a licença do asset. Ex: CC0, MIT, CC-BY, proprietary.",
            "sugestoes": sorted(LICENSE_COMPAT.keys()),
        }

    # Normalizar: remover hífens, underscores, múltiplos espaços
    license_norm = license_str.strip()
    license_search = re.sub(r'[-_\s]+', ' ', license_norm).strip()

    # Busca: exata → normalizada → fuzzy (prefixo ou substring, min 3 chars)
    compat = LICENSE_COMPAT.get(license_norm) or LICENSE_COMPAT.get(license_search)
    if not compat:
        lower = license_search.lower()
        for key, val in LICENSE_COMPAT.items():
            key_lower = key.lower()
            key_norm = re.sub(r'[-_\s]+', ' ', key_lower).strip()
            if key_norm == lower or (len(lower) >= 3 and (key_norm.startswith(lower) or lower.startswith(key_norm))):
                compat = val
                license_norm = key
                break

    if not compat:
        return {
            "status": "error",
            "gate": "block",
            "message": f"Licença '{license_str}' não reconhecida. Use uma das licenças conhecidas ou verifique manualmente.",
            "sugestoes": sorted(LICENSE_COMPAT.keys()),
        }

    gate = compat.get(project_license, "warn")
    category = compat.get("category", "unknown")

    # ── Motivo do gate ─────────────────────────────────────
    reasons = {
        "pass": f"Licença {license_norm} ({category}) compatível com projeto {project_license}.",
        "warn": f"Licença {license_norm} ({category}) requer atenção para projeto {project_license}. Verifique obrigações de atribuição/copyleft.",
        "block": f"Licença {license_norm} ({category}) INCOMPATÍVEL com projeto {project_license}. NÃO use este asset sem autorização explícita.",
    }

    # ── Registrar no manifesto ─────────────────────────────
    manifest_path = proj / "asset_licenses.json"
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}

    if "assets" not in manifest:
        manifest["assets"] = {}
    manifest["assets"][asset_path] = {
        "license": license_norm,
        "category": category,
        "gate": gate,
        "project_license": project_license,
        "audited_at": datetime.now().isoformat(),
    }
    manifest["updated_at"] = datetime.now().isoformat()

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint(str(manifest_path.relative_to(proj)), proj)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "status": "success",
        "gate": gate,
        "license": license_norm,
        "category": category,
        "asset_path": asset_path,
        "reason": reasons.get(gate, f"Classificação: {gate}"),
        "manifest": str(manifest_path.relative_to(proj)) if manifest_path.is_relative_to(proj) else str(manifest_path),
    }
