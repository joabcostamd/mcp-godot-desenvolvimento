"""asset_ops — Operações de importação de assets (texturas, áudio).

Fase 2: import_texture, import_sprite_sheet, import_audio.
"""

import shutil
from pathlib import Path

from tools.project_ops import _get_active_project, _check_path_traversal
from tools.scene_ops import _run_compile_test


def import_texture(source_path: str, target_res_path: str) -> dict:
    """Importa uma textura para o projeto.

    Args:
        source_path: Caminho absoluto do arquivo fonte (fora do projeto).
        target_res_path: Caminho relativo no projeto (ex: 'assets/sprites/player.png').

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

    if src.suffix.lower() not in (".png", ".jpg", ".jpeg", ".bmp", ".svg"):
        return {"status": "error", "message": f"Formato '{src.suffix}' não suportado. Use PNG, JPG, BMP ou SVG."}

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

    # Marca para reimport pendente (executado em compile_test/run_game)
    from tools.runtime_ops import mark_pending_compile
    mark_pending_compile()

    return {"status": "success", "res_path": target_res_path}


def import_sprite_sheet(
    source_path: str, target_res_path: str,
    frame_width: int, frame_height: int,
    target_scene_path: str, target_node_path: str,
    animations: list[dict]
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
    r = import_texture(source_path, target_res_path)
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

