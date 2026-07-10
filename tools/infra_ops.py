"""infra_ops.py — Infraestrutura Avançada (Fase C).

Browser Visualizer, Resource Dependency Graph, CI Generator,
Export Matrix, C# Support, Reflection Tools, Asset Library.

Inspirado no wangdiandao/godot-devtool + beckettlab.

Tools: generate_ci_snippet, export_matrix, resource_dependency_graph,
       build_csharp, find_classes, describe_object
"""

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ── CI Generator ─────────────────────────────────────────────────────

def generate_ci_snippet(project_path: str = "", target_platforms: str = "windows,linux,macos") -> dict:
    """Gera GitHub Actions / GitLab CI para exportação Godot."""
    platforms = [p.strip() for p in target_platforms.split(",")]

    github = f"""# GitHub Actions — Godot Export
name: Export Godot Project
on: [push, workflow_dispatch]
jobs:
  export:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        platform: [{", ".join(platforms)}]
    steps:
      - uses: actions/checkout@v4
      - name: Export {{{{ matrix.platform }}}}
        run: |
          godot --headless --path {project_path or '${{ github.workspace }}'} --export-release "{{{{ matrix.platform }}}}" """

    gitlab = f"""# GitLab CI — Godot Export
export:
  image: barichello/godot-ci:4.7
  script:
    - godot --headless --path {project_path or '$CI_PROJECT_DIR'} --export-release "{{{{ matrix.platform }}}}" 
  artifacts:
    paths:
      - build/"""

    return {
        "status": "success",
        "github_actions": github,
        "gitlab_ci": gitlab,
        "platforms": platforms,
    }


# ── Export Matrix ────────────────────────────────────────────────────

def export_matrix(project_path: str = "") -> dict:
    """Matriz de exportação: targets, templates, CI steps."""
    try:
        from tools.export_ops import list_export_presets
        presets_result = list_export_presets()
    except Exception:
        presets_result = {"status": "error", "message": "Não foi possível listar presets"}

    matrix = {
        "platforms": {
            "windows": {"extension": ".exe", "template": "Windows Desktop", "arch": "x86_64"},
            "linux": {"extension": ".x86_64", "template": "Linux/X11", "arch": "x86_64"},
            "macos": {"extension": ".zip", "template": "macOS", "arch": "universal"},
            "web": {"extension": ".html", "template": "Web", "arch": "wasm"},
            "android": {"extension": ".apk", "template": "Android", "arch": "arm64"},
        },
        "presets": presets_result,
        "ci_readiness": {
            "has_git": Path(project_path or ".").joinpath(".git").exists(),
            "has_project": Path(project_path or ".").joinpath("project.godot").exists(),
        },
    }

    return {"status": "success", "export_matrix": matrix}


# ── Resource Dependency Graph ────────────────────────────────────────

def resource_dependency_graph(project_path: str = "") -> dict:
    """Constrói grafo de dependências de recursos."""
    proj = Path(project_path) if project_path else Path(".")
    if not proj.exists():
        return {"status": "error", "message": "Projeto não encontrado"}

    deps = {}
    orphans = []

    # Escaneia todos os .tscn e .tres
    for ext in ("*.tscn", "*.tres"):
        for f in proj.rglob(ext):
            if "addons" in str(f) or ".godot" in str(f):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                refs = []
                for line in content.splitlines():
                    if "res://" in line:
                        import re
                        found = re.findall(r'res://[^"\'\s]+', line)
                        refs.extend(found)
                if refs:
                    deps[str(f.relative_to(proj))] = refs
                else:
                    orphans.append(str(f.relative_to(proj)))
            except Exception:
                pass

    return {
        "status": "success",
        "dependencies": deps,
        "total_with_deps": len(deps),
        "orphans_no_refs": len(orphans),
        "orphans": orphans[:20],
    }


# ── C# Support ───────────────────────────────────────────────────────

def build_csharp(project_path: str = "") -> dict:
    """Executa dotnet build e retorna erros estruturados."""
    import subprocess

    proj = Path(project_path) if project_path else Path(".")
    csproj = list(proj.glob("*.csproj"))
    if not csproj:
        return {"status": "error", "message": "Nenhum .csproj encontrado. Projeto C# não detectado."}

    try:
        result = subprocess.run(
            ["dotnet", "build", str(csproj[0])],
            capture_output=True, text=True, timeout=60, cwd=str(proj),
        )

        errors = []
        for line in result.stdout.splitlines() + result.stderr.splitlines():
            if "error CS" in line:
                # Parse: file(line,col): error CSXXXX: message
                import re
                m = re.match(r'(.+?)\((\d+),(\d+)\):\s*error\s+(CS\d+):\s*(.+)', line)
                if m:
                    errors.append({
                        "file": m.group(1),
                        "line": int(m.group(2)),
                        "col": int(m.group(3)),
                        "code": m.group(4),
                        "message": m.group(5),
                    })

        return {
            "status": "success" if result.returncode == 0 else "build_failed",
            "exit_code": result.returncode,
            "errors": errors[:20] or None,
            "error_count": len(errors),
        }
    except FileNotFoundError:
        return {"status": "error", "message": ".NET SDK não encontrado. Instale dotnet 8.0+."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── Reflection Tools ─────────────────────────────────────────────────

def find_classes(query: str = "", limit: int = 30, api_type: str = "") -> dict:
    """Busca classes na ClassDB por nome parcial (reflection-first).
    
    Similar ao beckettlab: find_classes, find_methods.
    """
    from tools.classdb import _class_index, search_classdb
    return search_classdb(query, limit)


def describe_object(node_path: str, scene_path: str = "") -> dict:
    """Descreve um objeto por reflection: propriedades, métodos, sinais.
    
    Inspirado no beckettlab: describe_object.
    """
    try:
        from tools.scene_ops import load_scene_tree
        tree = load_scene_tree(scene_path) if scene_path else {"nodes": []}
        nodes = tree.get("nodes", [])

        # Encontra o nó
        target = None
        for n in nodes:
            if node_path in n.get("path", "") or node_path in n.get("name", ""):
                target = n
                break

        if not target:
            return {"status": "error", "message": f"Nó '{node_path}' não encontrado"}

        node_type = target.get("type", "Node")

        # Busca na ClassDB
        from tools.classdb import query_classdb
        class_info = query_classdb(node_type, section="all", include_inherited=False, limit=20)

        return {
            "status": "success",
            "node": {"name": target.get("name"), "type": node_type, "path": target.get("path")},
            "class_info": class_info.get("class", {}),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
