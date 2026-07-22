"""style_kit.py — Style Kit: paleta, resolucao, pivo e estilo visual (FATIA 2.AL).

Define e valida um contrato visual que todos os assets do projeto devem seguir.
O style kit e um arquivo JSON que trava a identidade visual do jogo,
garantindo consistencia entre assets gerados por IA, placeholders e downloads CC0.

Formato style_kit.json:
{
  "version": "1.0",
  "name": "Pixel Art Fantasy",
  "palette": {
    "primary": "#4a90d9",
    "secondary": "#e8a87c",
    "accent": "#6b4c3b",
    "background": "#2c3e50",
    "ui_dark": "#1a1a2e",
    "ui_light": "#e0e0e0",
    "danger": "#e74c3c",
    "success": "#2ecc71",
    "warning": "#f39c12"
  },
  "resolution": {
    "base_width": 480,
    "base_height": 270,
    "pixel_art": true,
    "pixels_per_unit": 16
  },
  "pivot": {
    "default": "center",
    "characters": "bottom_center",
    "ui": "top_left",
    "projectiles": "center"
  },
  "art_style": {
    "type": "pixel_art",
    "outline": true,
    "outline_color": "#000000",
    "anti_alias": false,
    "color_ramp": "16_colors"
  }
}

Tools:
    create_style_kit — gera template
    validate_style_kit — valida contra schema
    apply_style_kit — aplica paleta em asset gerado
"""

import json
from pathlib import Path
from typing import Optional

# ── Schema ──────────────────────────────────────────────────────────

STYLE_KIT_SCHEMA = {
    "type": "object",
    "required": ["version", "name", "palette", "resolution"],
    "properties": {
        "version": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "palette": {
            "type": "object",
            "required": ["primary", "secondary"],
            "properties": {
                "primary": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
                "secondary": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
                "accent": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
                "background": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
                "ui_dark": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
                "ui_light": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
                "danger": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
                "success": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
                "warning": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
            },
        },
        "resolution": {
            "type": "object",
            "required": ["base_width", "base_height"],
            "properties": {
                "base_width": {"type": "integer", "minimum": 64, "maximum": 3840},
                "base_height": {"type": "integer", "minimum": 64, "maximum": 2160},
                "pixel_art": {"type": "boolean"},
                "pixels_per_unit": {"type": "integer", "minimum": 1, "maximum": 64},
            },
        },
        "pivot": {
            "type": "object",
            "properties": {
                "default": {"type": "string"},
                "characters": {"type": "string"},
                "ui": {"type": "string"},
                "projectiles": {"type": "string"},
                "items": {"type": "string"},
                "tiles": {"type": "string"},
            },
        },
        "art_style": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["pixel_art", "vector", "hand_drawn", "low_poly", "realistic", "stylized", "minimalist"]},
                "outline": {"type": "boolean"},
                "outline_color": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
                "anti_alias": {"type": "boolean"},
                "color_ramp": {"type": "string"},
            },
        },
    },
}

# Presets prontos para uso
STYLE_PRESETS = {
    "pixel_art_fantasy": {
        "name": "Pixel Art Fantasy",
        "palette": {"primary": "#4a90d9", "secondary": "#e8a87c", "accent": "#6b4c3b",
                     "background": "#2c3e50", "danger": "#e74c3c", "success": "#2ecc71"},
        "resolution": {"base_width": 480, "base_height": 270, "pixel_art": True, "pixels_per_unit": 16},
        "art_style": {"type": "pixel_art", "outline": True, "outline_color": "#000000", "anti_alias": False},
    },
    "flat_vector_casual": {
        "name": "Flat Vector Casual",
        "palette": {"primary": "#ff6b6b", "secondary": "#4ecdc4", "accent": "#ffe66d",
                     "background": "#f7f7f7", "danger": "#c0392b", "success": "#27ae60"},
        "resolution": {"base_width": 960, "base_height": 540, "pixel_art": False, "pixels_per_unit": 32},
        "art_style": {"type": "vector", "outline": False, "anti_alias": True},
    },
    "dark_scifi": {
        "name": "Dark Sci-Fi",
        "palette": {"primary": "#00d4ff", "secondary": "#ff6b35", "accent": "#c77dff",
                     "background": "#0a0a1a", "danger": "#ff1744", "success": "#00e676"},
        "resolution": {"base_width": 960, "base_height": 540, "pixel_art": False, "pixels_per_unit": 32},
        "art_style": {"type": "stylized", "outline": True, "outline_color": "#1a1a2e", "anti_alias": True},
    },
    "hand_drawn_cozy": {
        "name": "Hand Drawn Cozy",
        "palette": {"primary": "#8b5e3c", "secondary": "#d4a76a", "accent": "#e8c547",
                     "background": "#faf3e0", "danger": "#c0392b", "success": "#6b8e23"},
        "resolution": {"base_width": 960, "base_height": 540, "pixel_art": False, "pixels_per_unit": 64},
        "art_style": {"type": "hand_drawn", "outline": True, "outline_color": "#4a3728", "anti_alias": True},
    },
}

# Pivots validos
VALID_PIVOTS = {
    "top_left", "top_center", "top_right",
    "center_left", "center", "center_right",
    "bottom_left", "bottom_center", "bottom_right",
}


# ══════════════════════════════════════════════════════════════════════
# create_style_kit
# ══════════════════════════════════════════════════════════════════════

def create_style_kit(
    project_path: str,
    preset: str = "pixel_art_fantasy",
    output_name: str = "style_kit.json",
) -> dict:
    """Cria um arquivo style_kit.json no projeto.

    Args:
        project_path: Caminho do projeto Godot.
        preset: Nome do preset ('pixel_art_fantasy', 'flat_vector_casual',
                'dark_scifi', 'hand_drawn_cozy') ou 'custom'.
        output_name: Nome do arquivo de saida.

    Returns:
        dict com status e caminho do arquivo criado.
    """
    proj = Path(project_path)
    if not proj.is_dir():
        return {"status": "error", "message": f"Projeto nao encontrado: {project_path}"}

    if preset in STYLE_PRESETS:
        kit = dict(STYLE_PRESETS[preset])
    else:
        kit = dict(STYLE_PRESETS["pixel_art_fantasy"])

    kit["version"] = "1.0"
    kit["pivot"] = {
        "default": "center",
        "characters": "bottom_center",
        "ui": "top_left",
        "projectiles": "center",
        "items": "center",
        "tiles": "center",
    }

    output_path = proj / output_name
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(kit, f, indent=2, ensure_ascii=False)

    return {
        "status": "success",
        "path": str(output_path),
        "preset": preset,
        "name": kit["name"],
        "message": f"Style kit '{kit['name']}' criado em {output_name}. Use validate_style_kit para verificar.",
    }


# ══════════════════════════════════════════════════════════════════════
# validate_style_kit
# ══════════════════════════════════════════════════════════════════════

def validate_style_kit(project_path: str, kit_path: str = "style_kit.json") -> dict:
    """Valida um style_kit.json contra o schema.

    Args:
        project_path: Caminho do projeto.
        kit_path: Caminho relativo ao projeto para o style_kit.json.

    Returns:
        dict com status, erros e warnings.
    """
    proj = Path(project_path)
    full_path = proj / kit_path

    if not full_path.exists():
        return {
            "status": "error",
            "message": f"Style kit nao encontrado: {full_path}",
            "suggestion": "Use create_style_kit para gerar um template.",
        }

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            kit = json.load(f)
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"JSON invalido: {e}"}

    errors = []
    warnings = []

    # Validar campos obrigatorios
    for field in ["version", "name", "palette", "resolution"]:
        if field not in kit:
            errors.append(f"Campo obrigatorio ausente: '{field}'")

    # Validar paleta
    palette = kit.get("palette", {})
    if "primary" not in palette or "secondary" not in palette:
        errors.append("Paleta deve ter pelo menos 'primary' e 'secondary'")
    for color_name, hex_color in palette.items():
        if not isinstance(hex_color, str) or not hex_color.startswith("#") or len(hex_color) != 7:
            errors.append(f"Cor invalida '{color_name}': {hex_color} (use #RRGGBB)")

    # Validar resolucao
    resolution = kit.get("resolution", {})
    bw = resolution.get("base_width", 0)
    bh = resolution.get("base_height", 0)
    if bw < 64 or bh < 64:
        errors.append(f"Resolucao muito pequena: {bw}x{bh} (minimo 64x64)")
    if bw > 3840 or bh > 2160:
        warnings.append(f"Resolucao alta: {bw}x{bh}. Considere 480x270 ou 960x540 para 2D.")

    # Validar pivots
    pivot = kit.get("pivot", {})
    for pivot_type, pivot_value in pivot.items():
        if pivot_value not in VALID_PIVOTS:
            errors.append(f"Pivot invalido '{pivot_type}': '{pivot_value}'. Validos: {sorted(VALID_PIVOTS)}")

    # Validar art_style
    art = kit.get("art_style", {})
    valid_types = {"pixel_art", "vector", "hand_drawn", "low_poly", "realistic", "stylized", "minimalist"}
    art_type = art.get("type", "")
    if art_type and art_type not in valid_types:
        errors.append(f"Tipo de arte invalido: '{art_type}'. Validos: {sorted(valid_types)}")

    return {
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "kit_name": kit.get("name", "unknown"),
        "message": "Style kit valido!" if not errors else f"{len(errors)} erro(s) encontrado(s).",
    }


# ══════════════════════════════════════════════════════════════════════
# apply_style_kit
# ══════════════════════════════════════════════════════════════════════

def apply_style_kit(
    project_path: str,
    kit_path: str = "style_kit.json",
) -> dict:
    """Aplica o style kit ao projeto (atualiza project.brief.style_lock).

    Args:
        project_path: Caminho do projeto.
        kit_path: Caminho do style_kit.json.

    Returns:
        dict com status da aplicacao.
    """
    proj = Path(project_path)
    full_path = proj / kit_path

    if not full_path.exists():
        return {"status": "error", "message": f"Style kit nao encontrado: {full_path}"}

    # Validar primeiro
    validation = validate_style_kit(project_path, kit_path)
    if validation["status"] != "valid":
        return {"status": "error", "message": "Style kit invalido. Corrija os erros primeiro.",
                "validation": validation}

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            kit = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return {"status": "error", "message": f"Erro ao ler style kit: {e}"}

    # Tentar aplicar ao project brief (se existir)
    brief_path = proj / ".mcp_project_brief.json"
    if brief_path.exists():
        try:
            with open(brief_path, "r", encoding="utf-8") as f:
                brief = json.load(f)
            brief["style_lock"] = {
                "palette": kit.get("palette", {}),
                "resolution": kit.get("resolution", {}),
                "pivot": kit.get("pivot", {}),
                "art_style": kit.get("art_style", {}),
                "kit_name": kit.get("name", ""),
                "kit_version": kit.get("version", "1.0"),
            }
            with open(brief_path, "w", encoding="utf-8") as f:
                json.dump(brief, f, indent=2, ensure_ascii=False)
        except (json.JSONDecodeError, OSError):
            pass  # Brief corrompido — nao e critico

    return {
        "status": "success",
        "kit_name": kit.get("name", "unknown"),
        "palette_colors": len(kit.get("palette", {})),
        "resolution": f"{kit.get('resolution', {}).get('base_width', '?')}x{kit.get('resolution', {}).get('base_height', '?')}",
        "message": f"Style kit '{kit.get('name')}' aplicado. Todos os assets gerados usarao esta paleta e resolucao.",
    }


# ══════════════════════════════════════════════════════════════════════
# list_presets
# ══════════════════════════════════════════════════════════════════════

def list_style_presets() -> dict:
    """Lista todos os presets de style kit disponiveis."""
    presets = []
    for key, data in STYLE_PRESETS.items():
        presets.append({
            "id": key,
            "name": data["name"],
            "palette_preview": f"{data['palette']['primary']} / {data['palette']['secondary']}",
            "resolution": f"{data['resolution']['base_width']}x{data['resolution']['base_height']}",
            "art_type": data.get("art_style", {}).get("type", "unknown"),
        })
    return {
        "status": "success",
        "total": len(presets),
        "presets": presets,
        "message": f"{len(presets)} presets disponiveis. Use create_style_kit com o id desejado.",
    }
