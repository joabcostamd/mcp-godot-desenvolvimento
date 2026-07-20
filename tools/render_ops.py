"""render_ops — Camada 6.7: Render Settings.

Configurações de rendering: MSAA, FXAA, TAA, scaling, qualidade.
"""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def get_render_settings(
    project_path: str | None = None,
) -> dict:
    """Obtém as configurações de rendering do projeto (project.godot).
    
    Args:
        project_path: Caminho do projeto (usa default se None)
    
    Returns:
        dict com configurações atuais de rendering
    """
    try:
        from tools.project_ops import _get_active_project
        proj = Path(project_path) if project_path else Path(_get_active_project())
        
        if not proj.exists():
            proj = proj / "project.godot"
        if proj.is_dir():
            proj = proj / "project.godot"
        
        if not proj.exists():
            return {"ok": False, "error": f"project.godot não encontrado em: {proj}"}
        
        content = proj.read_text(encoding="utf-8")
        
        # Extrai configurações de rendering
        import re
        render_section = ""
        in_render = False
        for line in content.split('\n'):
            if line.strip().startswith('[rendering]'):
                in_render = True
                continue
            if in_render and line.strip().startswith('['):
                in_render = False
                continue
            if in_render:
                render_section += line + '\n'
        
        # Parse das configs
        settings = {}
        for match in re.finditer(r'(\w+/[\w_]+)\s*=\s*(.+)', render_section):
            key = match.group(1)
            value = match.group(2).strip().strip('"')
            settings[key] = value
        
        return {
            "ok": True,
            "project": str(proj),
            "settings": settings,
            "setting_count": len(settings),
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao ler render settings: {e}"}


def set_antialiasing(
    project_path: str | None = None,
    msaa: str | None = None,
    fxaa: bool | None = None,
    taa: bool | None = None,
    screen_space_aa: str | None = None,
) -> dict:
    """Configura antialiasing no project.godot.
    
    Args:
        project_path: Caminho do projeto
        msaa: "disabled", "2x", "4x", "8x"
        fxaa: Habilita/desabilita FXAA
        taa: Habilita/desabilita TAA
        screen_space_aa: Modo SSAA do Godot
    
    Returns:
        dict com mudanças aplicadas
    """
    try:
        from tools.project_ops import _get_active_project
        proj = Path(project_path) if project_path else Path(_get_active_project())
        
        if proj.is_dir():
            proj = proj / "project.godot"
        
        if not proj.exists():
            return {"ok": False, "error": f"project.godot não encontrado"}
        
        content = proj.read_text(encoding="utf-8")
        changes = []
        
        # Mapeamento de configs
        configs = {}
        if msaa is not None:
            msaa_map = {"disabled": "0", "2x": "1", "4x": "2", "8x": "3"}
            configs["rendering/anti_aliasing/quality/msaa_3d"] = msaa_map.get(msaa, msaa)
            changes.append(f"msaa={msaa}")
        
        if fxaa is not None:
            configs["rendering/anti_aliasing/quality/screen_space_aa"] = (
                "1" if fxaa else "0"
            )
            changes.append(f"fxaa={fxaa}")
        
        if taa is not None:
            configs["rendering/anti_aliasing/quality/use_taa"] = "true" if taa else "false"
            changes.append(f"taa={taa}")
        
        if screen_space_aa is not None:
            configs["rendering/anti_aliasing/screen_space_aa"] = screen_space_aa
            changes.append(f"screen_space_aa={screen_space_aa}")
        
        import re
        
        for key, value in configs.items():
            pattern = rf'^{re.escape(key)}\s*=.*$'
            replacement = f'{key} = {value}'
            
            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            else:
                # Adiciona na seção [rendering]
                if '[rendering]' in content:
                    content = content.replace('[rendering]', f'[rendering]\n{replacement}')
                else:
                    content += f'\n[rendering]\n{replacement}\n'
        
        proj.write_text(content, encoding="utf-8")
        
        return {
            "ok": True,
            "changes": changes,
            "message": f"Antialiasing configurado: {', '.join(changes)}",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao configurar antialiasing: {e}"}


def set_scaling_mode(
    project_path: str | None = None,
    mode: str | None = None,
    scale: float | None = None,
    stretch_mode: str | None = None,
    stretch_aspect: str | None = None,
) -> dict:
    """Configura o modo de scaling/resolução da janela.
    
    Args:
        project_path: Caminho do projeto
        mode: "2d", "viewport", "canvas_items"
        scale: Fator de escala (ex: 2.0)
        stretch_mode: "disabled", "2d", "viewport"
        stretch_aspect: "ignore", "keep", "keep_width", "keep_height", "expand"
    
    Returns:
        dict com mudanças aplicadas
    """
    try:
        from tools.project_ops import _get_active_project
        proj = Path(project_path) if project_path else Path(_get_active_project())
        
        if proj.is_dir():
            proj = proj / "project.godot"
        
        if not proj.exists():
            return {"ok": False, "error": f"project.godot não encontrado"}
        
        content = proj.read_text(encoding="utf-8")
        changes = []
        
        configs = {}
        if mode is not None:
            configs["rendering/renderer/rendering_method"] = mode
            changes.append(f"mode={mode}")
        
        if scale is not None:
            configs["display/window/stretch/scale"] = str(scale)
            changes.append(f"scale={scale}")
        
        if stretch_mode is not None:
            configs["display/window/stretch/mode"] = stretch_mode
            changes.append(f"stretch_mode={stretch_mode}")
        
        if stretch_aspect is not None:
            configs["display/window/stretch/aspect"] = stretch_aspect
            changes.append(f"stretch_aspect={stretch_aspect}")
        
        import re
        
        for key, value in configs.items():
            pattern = rf'^{re.escape(key)}\s*=.*$'
            replacement = f'{key} = {value}'
            
            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            else:
                section = key.split('/')[0]
                section_header = f'[{section}]'
                if section_header in content:
                    content = content.replace(section_header, f'{section_header}\n{replacement}')
                else:
                    content += f'\n{section_header}\n{replacement}\n'
        
        proj.write_text(content, encoding="utf-8")
        
        return {
            "ok": True,
            "changes": changes,
            "message": f"Scaling configurado: {', '.join(changes)}",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao configurar scaling: {e}"}


def set_render_quality(
    project_path: str | None = None,
    preset: str = "balanced",
    shadows: str | None = None,
    gi: str | None = None,
    reflections: str | None = None,
    particles: str | None = None,
) -> dict:
    """Configura qualidade de rendering por preset ou manualmente.
    
    Args:
        project_path: Caminho do projeto
        preset: "low", "balanced", "high", "ultra"
        shadows: Tamanho do shadow map (ex: "1024", "2048", "4096")
        gi: Qualidade de GI ("low", "high")
        reflections: Qualidade de reflexos ("low", "medium", "high")
        particles: Quantidade de partículas (multiplicador)
    
    Returns:
        dict com configurações aplicadas
    """
    try:
        from tools.project_ops import _get_active_project
        proj = Path(project_path) if project_path else Path(_get_active_project())
        
        if proj.is_dir():
            proj = proj / "project.godot"
        
        if not proj.exists():
            return {"ok": False, "error": f"project.godot não encontrado"}
        
        presets = {
            "low": {
                "rendering/renderer/rendering_method": "mobile",
                "rendering/anti_aliasing/quality/msaa_3d": "0",
                "rendering/shadows/shadows_enabled": "false",
                "rendering/reflections/sky_reflections/enabled": "false",
                "rendering/environment/gi/use_half_resolution": "true",
                "rendering/limits/rendering/max_renderable_elements": "32768",
            },
            "balanced": {
                "rendering/renderer/rendering_method": "forward_plus",
                "rendering/anti_aliasing/quality/msaa_3d": "1",
                "rendering/shadows/shadows_enabled": "true",
                "rendering/reflections/sky_reflections/enabled": "true",
                "rendering/environment/gi/use_half_resolution": "true",
                "rendering/limits/rendering/max_renderable_elements": "65536",
            },
            "high": {
                "rendering/renderer/rendering_method": "forward_plus",
                "rendering/anti_aliasing/quality/msaa_3d": "2",
                "rendering/shadows/shadows_enabled": "true",
                "rendering/reflections/sky_reflections/enabled": "true",
                "rendering/environment/gi/use_half_resolution": "false",
                "rendering/limits/rendering/max_renderable_elements": "131072",
            },
            "ultra": {
                "rendering/renderer/rendering_method": "forward_plus",
                "rendering/anti_aliasing/quality/msaa_3d": "3",
                "rendering/shadows/shadows_enabled": "true",
                "rendering/reflections/sky_reflections/enabled": "true",
                "rendering/environment/gi/use_half_resolution": "false",
                "rendering/limits/rendering/max_renderable_elements": "262144",
            },
        }
        
        import re
        content = proj.read_text(encoding="utf-8")
        configs = presets.get(preset, presets["balanced"])
        
        # Override com valores manuais
        if shadows is not None:
            configs["rendering/shadows/directional_shadow/size"] = shadows
        if gi is not None:
            configs["rendering/environment/gi/use_half_resolution"] = "true" if gi == "low" else "false"
        if reflections is not None:
            configs["rendering/reflections/sky_reflections/enabled"] = "true" if reflections != "low" else "false"
        if particles is not None:
            configs["rendering/limits/particles/max_particles"] = str(int(float(particles) * 10000))
        
        for key, value in configs.items():
            pattern = rf'^{re.escape(key)}\s*=.*$'
            replacement = f'{key} = {value}'
            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            else:
                section_header = f'[rendering]'
                if section_header in content:
                    content = content.replace(section_header, f'{section_header}\n{replacement}')
                else:
                    content += f'\n{section_header}\n{replacement}\n'
        
        proj.write_text(content, encoding="utf-8")
        
        return {
            "ok": True,
            "preset": preset,
            "config_count": len(configs),
            "message": f"Qualidade de rendering definida como '{preset}' ({len(configs)} configurações)",
        }
    except Exception as e:
        return {"ok": False, "error": f"Erro ao configurar qualidade: {e}"}
