"""analyze_signal_flow — Detecção de conexões de sinal órfãs no projeto.

Cruza as conexões declaradas em .tscn (seção [connection]) contra os
métodos de fato existentes nos scripts de destino, e os sinais declarados
via signal contra as conexões existentes.

Feature: Grupo C — Análise de fluxo de sinal órfão.
"""

import re
from pathlib import Path


def analyze_signal_flow(
    project_path: str | None = None,
    scene_path: str | None = None,
) -> dict:
    """Analisa conexões de sinal no projeto (ou numa cena específica).

    Returns:
        dict com broken_connections, unconnected_signals, total_scanned.
    """
    proj = _resolve_project(project_path)
    if isinstance(proj, dict) and proj.get("status") == "error":
        return proj

    if scene_path:
        scene_file = Path(scene_path)
        if not scene_file.is_absolute():
            scene_file = proj / scene_path
        if not scene_file.exists():
            return {"status": "error", "message": f"Cena não encontrada: {scene_path}"}
        scene_files = [scene_file]
    else:
        scene_files = [f for f in proj.rglob("*.tscn") if not _should_skip(f)]

    broken_connections: list[dict] = []
    all_connected_signals: set[str] = set()

    for scene_file in scene_files:
        try:
            content = scene_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        node_scripts = _map_nodes_to_scripts(content)

        for conn in re.finditer(
            r'\[connection\s+signal="([^"]+)"\s+from="([^"]+)"\s+to="([^"]+)"\s+method="([^"]+)"',
            content,
        ):
            signal_name, from_node, to_node, method_name = conn.groups()
            target_script = node_scripts.get(to_node)

            if target_script is None:
                continue

            all_connected_signals.add(f"{target_script}::{method_name}")

            script_full_path = proj / target_script if not Path(target_script).is_absolute() else Path(target_script)
            script_methods = _get_script_methods(script_full_path)
            if script_methods is None:
                continue

            if method_name not in script_methods:
                broken_connections.append({
                    "scene": str(scene_file.relative_to(proj)).replace("\\", "/"),
                    "signal": signal_name,
                    "from_node": from_node,
                    "to_node": to_node,
                    "expected_method": method_name,
                    "target_script": target_script,
                    "reason": f"Método '{method_name}' não existe em '{target_script}'",
                })

    unconnected_signals: list[dict] = []
    for script_file in proj.rglob("*.gd"):
        if _should_skip(script_file):
            continue
        try:
            content = script_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel_script = str(script_file.relative_to(proj)).replace("\\", "/")
        declared = re.findall(r'^signal\s+(\w+)', content, re.MULTILINE)
        for sig_name in declared:
            has_any_connection = any(
                k.startswith(f"{rel_script}::") for k in all_connected_signals
            )
            if not has_any_connection:
                unconnected_signals.append({"script": rel_script, "signal": sig_name})

    return {
        "status": "success",
        "broken_connections": broken_connections,
        "unconnected_signals": unconnected_signals,
        "total_scenes_scanned": len(scene_files),
        "message": (
            f"{len(broken_connections)} conexão(ões) quebrada(s), "
            f"{len(unconnected_signals)} sinal(is) possivelmente não conectado(s)."
        ),
    }


def _map_nodes_to_scripts(content: str) -> dict[str, str]:
    """Mapeia node_path para o caminho relativo do script anexado."""
    ext_resources: dict[str, str] = {}
    for m in re.finditer(
        r'\[ext_resource\s+type="Script"[^\]]*path="res://([^"]+)"[^\]]*id="([^"]+)"',
        content,
    ):
        path, res_id = m.groups()
        ext_resources[res_id] = path

    node_scripts: dict[str, str] = {}
    node_blocks = re.split(r'(?=\[node\s)', content)
    for block in node_blocks:
        name_match = re.search(r'\[node\s+name="([^"]+)"', block)
        if not name_match:
            continue
        node_name = name_match.group(1)
        parent_match = re.search(r'parent="([^"]+)"', block)
        if parent_match:
            parent = parent_match.group(1)
            node_path = f"{parent}/{node_name}" if parent != "." else node_name
        else:
            node_path = "."

        script_match = re.search(r'script\s*=\s*ExtResource\("([^"]+)"\)', block)
        if script_match:
            res_id = script_match.group(1)
            if res_id in ext_resources:
                node_scripts[node_path] = ext_resources[res_id]

    return node_scripts


def _get_script_methods(script_path: Path) -> set[str] | None:
    """Lista os métodos declarados num script .gd via regex."""
    if not script_path.exists():
        return None
    try:
        content = script_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    return set(re.findall(r'^func\s+(\w+)\s*\(', content, re.MULTILINE))


def _resolve_project(project_path: str | None = None) -> Path:
    """Resolve o caminho do projeto."""
    if project_path:
        p = Path(project_path)
        if p.exists():
            return p
        return {"status": "error", "message": f"Projeto não encontrado: {project_path}"}
    try:
        from tools.project_ops import _get_active_project
        return Path(_get_active_project())
    except Exception:
        return {"status": "error", "message": "Nenhum projeto ativo definido."}


def _should_skip(path: Path) -> bool:
    """Verifica se o path deve ser ignorado."""
    path_str = str(path).replace("\\", "/")
    for excl in ["addons/", ".godot/", ".git/", "_backups/", "build/", ".mcp_"]:
        if excl in path_str:
            return True
    return False
