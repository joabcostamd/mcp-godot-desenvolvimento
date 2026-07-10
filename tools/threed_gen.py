"""threed_gen.py — Geracao de assets 3D (GRATIS + opcao paga).

⚠️💰 AVISO DE CUSTO:
- Opcao GRATUITA: placeholder 3D procedural (formas basicas)
- Opcao PAGA: Hyper3D Rodin API (~$0.05/modelo) — so se API key configurada
- SEMPRE tente a gratuita primeiro.
"""

import base64
import json
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    from PIL import Image
    _HAS_PILLOW = True
except ImportError:
    _HAS_PILLOW = False


def generate_3d_placeholder(name: str, shape: str = "box", color: str = "#4488cc",
                            size: float = 1.0, save_path: str | None = None) -> dict:
    """Gera placeholder 3D procedural (GRATIS — Pillow + NumPy).

    Args:
        name: Nome do asset.
        shape: Forma: box, sphere, cylinder, cone, torus, pyramid.
        color: Cor em hex (#RRGGBB).
        size: Escala (1.0 = tamanho padrao).
        save_path: Caminho para salvar preview PNG (auto se None).

    Returns:
        {"status": "success", "saved_to": str, "preview_base64": str,
         "godot_scene_code": str, "cost": "GRATIS"}
    """
    from tools.project_ops import _get_active_project, _check_path_traversal
    proj = _get_active_project()

    if not save_path:
        save_path = f"assets/3d/{name}.png"

    violation = _check_path_traversal(save_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    # Gerar preview 2D com Pillow
    if _HAS_PILLOW:
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)

        if shape == "box":
            draw.rectangle([20, 20, 108, 108], fill=rgb + (200,), outline=(255, 255, 255, 100))
        elif shape == "sphere":
            draw.ellipse([20, 20, 108, 108], fill=rgb + (200,), outline=(255, 255, 255, 100))
        elif shape == "cylinder":
            draw.rectangle([20, 40, 108, 88], fill=rgb + (200,))
            draw.ellipse([20, 20, 108, 60], fill=rgb + (180,))
        elif shape == "cone":
            draw.polygon([(64, 20), (20, 108), (108, 108)], fill=rgb + (200,))
        elif shape == "pyramid":
            mid = 64
            draw.polygon([(mid, 20), (20, 108), (108, 108)], fill=rgb + (200,))
        else:
            draw.ellipse([20, 20, 108, 108], fill=rgb + (200,))

        full = proj / save_path
        full.parent.mkdir(parents=True, exist_ok=True)
        img.save(full, "PNG")

        buf = BytesIO()
        img.save(buf, "PNG")
        preview_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    else:
        preview_b64 = ""
        full = proj / save_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(f"# Placeholder 3D: {name} ({shape})\n", encoding="utf-8")

    # Gerar código de cena Godot 3D
    godot_scene = f'''[gd_scene load_steps=1 format=3 uid="uid://{name.lower()}"]

[sub_resource type="BoxMesh" id="1"]
size = Vector3({size}, {size}, {size})

[node name="{name}" type="MeshInstance3D"]
mesh = SubResource("1")
material_override = null

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("2")

[sub_resource type="BoxShape3D" id="2"]
size = Vector3({size}, {size}, {size})
'''

    return {"status": "success", "saved_to": save_path, "preview_base64": preview_b64,
            "godot_scene_code": godot_scene, "shape": shape, "color": color, "cost": "GRATIS",
            "message": f"Placeholder 3D '{name}' ({shape}) gerado. Copie o godot_scene_code para um .tscn."}


def generate_3d_asset(description: str, category: str = "prop",
                      style: str = "scifi", save_path: str | None = None) -> dict:
    """Gera asset 3D via API (⚠️💰) ou placeholder GRATIS.

    ⚠️💰 CUSTO: Hyper3D Rodin API (~$0.05/modelo) se HYPER3D_API_KEY configurada.
    SEM custo se API key nao configurada (usa placeholder GRATIS).

    Args:
        description: Descricao do asset 3D ("crate de metal scifi").
        category: prop, character, vehicle, building, weapon.
        style: scifi, fantasy, modern, realistic.
        save_path: Caminho para salvar (auto se None).

    Returns:
        {"status": "success", "cost": "GRATIS"|"API_$0.05", ...}
    """
    import os

    api_key = os.environ.get("HYPER3D_API_KEY", "")

    if not api_key:
        # Gratuito — usa placeholder
        shape_map = {"prop": "box", "character": "cylinder", "vehicle": "box",
                     "building": "pyramid", "weapon": "cone"}
        color_map = {"scifi": "#4488cc", "fantasy": "#cc8844", "modern": "#888888", "realistic": "#666644"}

        r = generate_3d_placeholder(
            name=description[:20].replace(" ", "_"),
            shape=shape_map.get(category, "box"),
            color=color_map.get(style, "#4488cc"),
            save_path=save_path,
        )
        r["cost"] = "GRATIS"
        r["message"] = f"Placeholder 3D gerado (GRATIS). Configure HYPER3D_API_KEY para assets realistas (~$0.05)."
        return r

    # ⚠️💰 API paga — Hyper3D Rodin
    try:
        import requests
        resp = requests.post("https://api.hyper3d.ai/v1/generate", headers={"Authorization": f"Bearer {api_key}"},
                             json={"prompt": f"{description}, {style} style, game-ready low-poly",
                                   "category": category, "format": "glb"}, timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            model_url = data.get("model_url", "")
            if model_url:
                from tools.project_ops import _get_active_project
                proj = _get_active_project()
                if not save_path:
                    save_path = f"assets/3d/{description[:20].replace(' ', '_')}.glb"
                full = proj / save_path
                full.parent.mkdir(parents=True, exist_ok=True)
                model_resp = requests.get(model_url, timeout=60)
                full.write_bytes(model_resp.content)
                return {"status": "success", "saved_to": save_path, "cost": "API_$0.05",
                        "generator": "Hyper3D Rodin", "message": f"Asset 3D gerado via Hyper3D API (~$0.05)."}
    except Exception:
        pass

    # Fallback GRATIS
    r = generate_3d_placeholder(name=description[:20].replace(" ", "_"), save_path=save_path)
    r["cost"] = "GRATIS (API falhou)"
    return r
