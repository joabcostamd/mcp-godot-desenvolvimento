"""project_map.py — Project Map JSON/HTML (Fase 2C / B4).

Gera mapa estruturado do projeto Godot: cenas, scripts, funções,
sinais, conexões. Inspirado no FunplayAI.

Tool: project_map — gera JSON + HTML do projeto.
"""

import json
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent


def generate_project_map(
    project_path: str | None = None,
    format: str = "json",
    output_path: str | None = None,
) -> dict:
    """Gera mapa estruturado do projeto Godot.

    Args:
        project_path: Caminho do projeto (auto-detecta se None).
        format: "json" (dict), "html" (arquivo HTML), "both".
        output_path: Onde salvar o HTML. Default: project_path/project_map.html.

    Returns:
        dict com mapa do projeto.
    """
    # Detecta projeto
    if not project_path:
        try:
            from tools.project_ops import get_project_settings
            settings = get_project_settings()
            project_path = settings.get("project_path", "")
        except Exception:
            pass

    if not project_path:
        return {"status": "error", "message": "Nenhum projeto ativo. Passe project_path ou use project_manage set_active."}

    proj = Path(project_path)
    if not proj.exists():
        return {"status": "error", "message": f"Projeto não encontrado: {project_path}"}

    # Coleta dados
    pmap = {
        "project": proj.name,
        "path": str(proj),
        "generated_at": datetime.now().isoformat(),
        "scenes": _scan_scenes(proj),
        "scripts": _scan_scripts(proj),
        "assets": _scan_assets(proj),
        "structure": _scan_structure(proj),
    }

    # Estatísticas
    pmap["stats"] = {
        "total_scenes": len(pmap["scenes"]),
        "total_scripts": len(pmap["scripts"]),
        "total_functions": sum(s.get("function_count", 0) for s in pmap["scripts"]),
        "total_textures": pmap["assets"].get("textures", 0),
        "total_audio": pmap["assets"].get("audio", 0),
    }

    result = {"status": "success", "map": pmap}

    # Gera HTML se solicitado
    if format in ("html", "both"):
        html_path = output_path or str(proj / "project_map.html")
        _generate_html(pmap, html_path)
        result["html_path"] = html_path

    return result


def _scan_scenes(proj: Path) -> list[dict]:
    """Escaneia cenas .tscn."""
    scenes = []
    for tscn in proj.rglob("*.tscn"):
        if "addons" in str(tscn) or ".godot" in str(tscn):
            continue
        info = {
            "name": tscn.name,
            "path": str(tscn.relative_to(proj)),
            "size_kb": round(tscn.stat().st_size / 1024, 1),
        }
        # Tenta extrair nó raiz
        try:
            content = tscn.read_text(encoding="utf-8", errors="ignore")
            root_match = re.search(r'\[node name="([^"]+)" type="([^"]+)"', content)
            if root_match:
                info["root_node"] = root_match.group(1)
                info["root_type"] = root_match.group(2)
            # Conta scripts anexados
            info["attached_scripts"] = len(re.findall(r'script = ExtResource\("(\d+)"\)', content))
        except Exception:
            pass
        scenes.append(info)
    return sorted(scenes, key=lambda s: s["name"])


def _scan_scripts(proj: Path) -> list[dict]:
    """Escaneia scripts .gd."""
    scripts = []
    for gd in proj.rglob("*.gd"):
        if "addons" in str(gd) or ".godot" in str(gd):
            continue
        info = {
            "name": gd.name,
            "path": str(gd.relative_to(proj)),
            "size_kb": round(gd.stat().st_size / 1024, 1),
        }
        # Analisa conteúdo
        try:
            content = gd.read_text(encoding="utf-8", errors="ignore")
            info["lines"] = len(content.splitlines())
            info["extends"] = _extract_extends(content)
            info["class_name"] = _extract_class_name(content)
            funcs = re.findall(r'func\s+(\w+)', content)
            info["functions"] = funcs
            info["function_count"] = len(funcs)
            signals = re.findall(r'signal\s+(\w+)', content)
            info["signals"] = signals
            info["signal_count"] = len(signals)
        except Exception:
            info["lines"] = 0
            info["functions"] = []
            info["function_count"] = 0
        scripts.append(info)
    return sorted(scripts, key=lambda s: s["name"])


def _scan_assets(proj: Path) -> dict:
    """Conta assets por tipo."""
    assets = {"textures": 0, "audio": 0, "models": 0, "fonts": 0, "shaders": 0}
    for f in proj.rglob("*"):
        if "addons" in str(f) or ".godot" in str(f):
            continue
        ext = f.suffix.lower()
        if ext in (".png", ".jpg", ".jpeg", ".svg", ".webp", ".bmp"):
            assets["textures"] += 1
        elif ext in (".wav", ".ogg", ".mp3", ".flac"):
            assets["audio"] += 1
        elif ext in (".glb", ".gltf", ".obj"):
            assets["models"] += 1
        elif ext in (".ttf", ".otf", ".woff", ".woff2"):
            assets["fonts"] += 1
        elif ext in (".gdshader", ".tres"):
            assets["shaders"] += 1
    return assets


def _scan_structure(proj: Path) -> list[str]:
    """Top-level da estrutura de pastas."""
    top_dirs = []
    for item in sorted(proj.iterdir()):
        if item.name.startswith(".") or item.name == "addons":
            continue
        if item.is_dir():
            count = len(list(item.rglob("*")))
            top_dirs.append(f"{item.name}/ ({count} arquivos)")
        else:
            top_dirs.append(item.name)
    return top_dirs


def _extract_extends(content: str) -> str:
    m = re.search(r'extends\s+(\w+)', content)
    return m.group(1) if m else ""


def _extract_class_name(content: str) -> str:
    m = re.search(r'class_name\s+(\w+)', content)
    return m.group(1) if m else ""


def _generate_html(pmap: dict, output_path: str) -> None:
    """Gera visualização HTML do project map."""

    # Scripts cards
    scripts_html = ""
    for s in pmap['scripts']:
        funcs = s.get('functions', [])[:15]
        fn_tags = " ".join(f"<span class='fn'>{f}()</span>" for f in funcs)
        more = " ..." if s.get('function_count', 0) > 15 else ""
        scripts_html += (
            f"<div class='card'><strong>{s['name']}</strong> "
            f"<small>({s['path']}, {s['lines']} linhas)</small><br>"
            f"extends {s.get('extends', '?')}<br>"
            f"{fn_tags}{more}</div>\n"
        )

    # Scenes table
    scenes_html = ""
    for s in pmap['scenes']:
        scenes_html += (
            f"<tr><td>{s['name']}</td><td>{s['path']}</td>"
            f"<td>{s.get('root_type','?')}</td><td>{s.get('attached_scripts',0)}</td>"
            f"<td>{s['size_kb']}</td></tr>\n"
        )

    html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Project Map — {pmap['project']}</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 20px auto; padding: 0 20px; background: #1a1a2e; color: #e0e0e0; }}
h1 {{ color: #7b68ee; }}
h2 {{ color: #9370db; border-bottom: 1px solid #333; padding-bottom: 5px; }}
.card {{ background: #16213e; border-radius: 8px; padding: 15px; margin: 10px 0; }}
.stat {{ display: inline-block; background: #0f3460; border-radius: 6px; padding: 10px 20px; margin: 5px; text-align: center; }}
.stat .num {{ font-size: 28px; font-weight: bold; color: #7b68ee; }}
.stat .label {{ font-size: 12px; color: #999; }}
table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
th {{ text-align: left; padding: 8px; background: #0f3460; }}
td {{ padding: 8px; border-bottom: 1px solid #333; }}
.fn {{ background: #1a3a5c; border-radius: 4px; padding: 2px 6px; margin: 2px; display: inline-block; font-size: 12px; font-family: monospace; }}
</style>
</head>
<body>
<h1>🗺️ Project Map — {pmap['project']}</h1>
<p>Gerado em: {pmap['generated_at']}</p>

<div>
<div class="stat"><div class="num">{pmap['stats']['total_scenes']}</div><div class="label">Cenas</div></div>
<div class="stat"><div class="num">{pmap['stats']['total_scripts']}</div><div class="label">Scripts</div></div>
<div class="stat"><div class="num">{pmap['stats']['total_functions']}</div><div class="label">Funções</div></div>
<div class="stat"><div class="num">{pmap['assets']['textures']}</div><div class="label">Texturas</div></div>
<div class="stat"><div class="num">{pmap['assets']['audio']}</div><div class="label">Áudios</div></div>
</div>

<h2>📁 Estrutura</h2>
<div class="card"><ul>{"".join(f"<li>{d}</li>" for d in pmap['structure'])}</ul></div>

<h2>🎬 Cenas ({pmap['stats']['total_scenes']})</h2>
<table>
<tr><th>Nome</th><th>Path</th><th>Raiz</th><th>Scripts</th><th>KB</th></tr>
{scenes_html}
</table>

<h2>📜 Scripts ({pmap['stats']['total_scripts']})</h2>
{scripts_html}
</body></html>"""

    Path(output_path).write_text(html, encoding="utf-8")
