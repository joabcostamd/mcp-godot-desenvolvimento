"""refs_ops.py — Validacao de Referencias e Find Usages (PATCH 15).

Valida referencias cruzadas no projeto Godot e encontra usos de recursos.
NAO requer Godot rodando — opera estaticamente nos arquivos do projeto.

Tools:
    validate_project_refs — valida todas as referencias (TSCN + GDScript)
    find_usages         — encontra todos os usos de um recurso/alvo
"""

import re
from pathlib import Path

from tools.project_ops import _get_active_project


# ══════════════════════════════════════════════════════════════════════
# TSCN Parser (resolve IDs de ext_resource)
# ══════════════════════════════════════════════════════════════════════

def _parse_tscn_ext_resources(content: str) -> dict[str, str]:
    """Extrai mapeamento id -> path dos [ext_resource] de um .tscn.

    Suporta ordem arbitraria dos atributos (type/path/id/uid).

    Returns:
        {"1": "res://scripts/player.gd", "2": "res://assets/icon.png", ...}
    """
    id_map: dict[str, str] = {}
    # Extrai cada bloco [ext_resource ...] individualmente e parseia atributos
    for block_m in re.finditer(r'\[ext_resource\s+(.*?)\]', content):
        attrs = block_m.group(1)
        path = None
        ext_id = None
        for attr_m in re.finditer(r'(\w+)="([^"]*)"', attrs):
            key = attr_m.group(1)
            val = attr_m.group(2)
            if key == "path":
                path = val
            elif key == "id":
                ext_id = val
        if path and ext_id:
            id_map[ext_id] = path
    return id_map


def _parse_tscn_sub_resources(content: str) -> dict[str, dict]:
    """Extrai [sub_resource] com seus IDs e propriedades.

    Returns:
        {"SubResource_1": {"type": "GDScript", "script": "res://x.gd", ...}}
    """
    sub_map: dict[str, dict] = {}
    pattern = r'\[sub_resource\s+type="([^"]*)"\s*id="([^"]+)"\]\n((?:[^\[].*\n?)*)'
    for m in re.finditer(pattern, content):
        sub_type = m.group(1)
        sub_id = m.group(2)
        props_block = m.group(3)
        props: dict[str, str] = {"_type": sub_type}
        for prop_m in re.finditer(r'(\w+(?:\/\w+)*)\s*=\s*(.+)', props_block):
            key = prop_m.group(1).strip()
            val = prop_m.group(2).strip().strip('"')
            props[key] = val
        sub_map[sub_id] = props
    return sub_map


def _parse_tscn_node_refs(content: str) -> list[dict]:
    """Extrai referencias nos nodes: script, texturas, cenas instanciadas.

    Returns:
        [{"node": "Player", "ref_type": "script", "ref_value": "ExtResource(\"1\")"}, ...]
    """
    refs: list[dict] = []
    node_pattern = r'\[node\s+name="([^"]*)"[^\]]*\](?:\n(?:[^\[].*\n?)*)'
    for node_m in re.finditer(node_pattern, content):
        node_name = node_m.group(1)
        node_body = node_m.group(0)

        # script = ExtResource("N")
        for sm in re.finditer(r'script\s*=\s*ExtResource\("(\d+)"\)', node_body):
            refs.append({"node": node_name, "ref_type": "script", "ref_value": f'ExtResource("{sm.group(1)}")'})

        # texture = ExtResource("N")
        for tm in re.finditer(r'(?:texture|icon|normal_map)\s*=\s*ExtResource\("(\d+)"\)', node_body):
            refs.append({"node": node_name, "ref_type": "texture", "ref_value": f'ExtResource("{tm.group(1)}")'})

        # mesh = ExtResource("N") ou shape = ExtResource("N")
        for mm in re.finditer(r'(?:mesh|shape|material)\s*=\s*ExtResource\("(\d+)"\)', node_body):
            refs.append({"node": node_name, "ref_type": mm.group(0).split("=")[0].strip(),
                         "ref_value": f'ExtResource("{mm.group(1)}")'})

        # SubResource("N")
        for srm in re.finditer(r'(?:script|texture|mesh|shape)\s*=\s*SubResource\("([^"]+)"\)', node_body):
            refs.append({"node": node_name, "ref_type": srm.group(0).split("=")[0].strip(),
                         "ref_value": f'SubResource("{srm.group(1)}")'})

        # scene = "res://..." (instancia de cena)
        for scm in re.finditer(r'(?:scene)\s*=\s*"res://([^"]+)"', node_body):
            refs.append({"node": node_name, "ref_type": "scene_instance",
                         "ref_value": f'res://{scm.group(1)}'})

    return refs


# ══════════════════════════════════════════════════════════════════════
# validate_project_refs
# ══════════════════════════════════════════════════════════════════════

def validate_project_refs(project_path: str | None = None, full_report: bool = False) -> dict:
    """Valida TODAS as referencias cruzadas no projeto Godot.

    Verifica:
    - ext_resource: IDs que nao tem [ext_resource] correspondente
    - ext_resource: paths que apontam para arquivos inexistentes
    - sub_resource: IDs referenciados mas nao definidos
    - GDScript: preload/load/ResourceLoader.load com paths quebrados
    - GDScript: change_scene_to_file com cenas inexistentes
    - Nodes: script/textura/mesh apontando para recursos quebrados

    Args:
        project_path: Caminho do projeto (opcional, usa projeto ativo).
        full_report: Se True, retorna TODOS os resultados (sem truncar).

    Returns:
        {"status": "success", "errors": [...], "warnings": [...], "summary": {...}}
    """
    proj = _resolve_project(project_path)
    if not proj:
        return {"status": "error", "message": "Projeto nao encontrado."}

    errors: list[dict] = []
    warnings: list[dict] = []
    files_scanned = 0

    # ── Coleta todos os paths existentes ──
    existing = _collect_existing_files(proj)

    # ── Varre .tscn ──
    for tscn in sorted(proj.glob("**/*.tscn")):
        if _should_skip(tscn):
            continue
        rel = str(tscn.relative_to(proj))
        try:
            content = tscn.read_text(encoding="utf-8")
        except Exception:
            continue
        files_scanned += 1

        # 1. Mapeia ext_resource IDs → paths
        ext_map = _parse_tscn_ext_resources(content)

        # 2. Valida cada ext_resource
        for ext_id, ref_path in ext_map.items():
            # Normaliza: remove res://
            clean = ref_path.replace("res://", "")
            if clean not in existing:
                errors.append({
                    "file": rel,
                    "type": "ext_resource_broken_path",
                    "ext_id": ext_id,
                    "reference": ref_path,
                    "message": f"ext_resource id={ext_id}: path '{ref_path}' nao encontrado no disco.",
                })

        # 3. Valida que ExtResource("N") tem [ext_resource id="N"]
        all_ext_refs = set()
        for m in re.finditer(r'ExtResource\("(\d+)"\)', content):
            all_ext_refs.add(m.group(1))
        for ref_id in all_ext_refs:
            if ref_id not in ext_map:
                errors.append({
                    "file": rel,
                    "type": "ext_resource_missing_def",
                    "ext_id": ref_id,
                    "reference": f'ExtResource("{ref_id}")',
                    "message": f"ExtResource(\"{ref_id}\") usado mas [ext_resource id=\"{ref_id}\"] nao existe.",
                })

        # 4. Valida sub_resources
        sub_map = _parse_tscn_sub_resources(content)
        for m in re.finditer(r'SubResource\("([^"]+)"\)', content):
            sub_id = m.group(1)
            if sub_id not in sub_map:
                errors.append({
                    "file": rel,
                    "type": "sub_resource_missing",
                    "sub_id": sub_id,
                    "message": f"SubResource(\"{sub_id}\") usado mas [sub_resource id=\"{sub_id}\"] nao existe.",
                })

        # 5. Valida referencias nos nodes
        node_refs = _parse_tscn_node_refs(content)
        for nref in node_refs:
            ref_val = nref["ref_value"]
            if ref_val.startswith("ExtResource"):
                ext_id = ref_val.split('"')[1]
                if ext_id not in ext_map:
                    errors.append({
                        "file": rel,
                        "type": "node_ref_broken",
                        "node": nref["node"],
                        "ref_type": nref["ref_type"],
                        "reference": ref_val,
                        "message": f"Node '{nref['node']}': {nref['ref_type']}={ref_val} — ext_resource id={ext_id} nao definido.",
                    })
                elif ext_id in ext_map:
                    clean = ext_map[ext_id].replace("res://", "")
                    if clean not in existing:
                        errors.append({
                            "file": rel,
                            "type": "node_ref_broken_path",
                            "node": nref["node"],
                            "ref_type": nref["ref_type"],
                            "reference": ext_map[ext_id],
                            "message": f"Node '{nref['node']}': {nref['ref_type']}={ref_val} — path '{ext_map[ext_id]}' nao encontrado.",
                        })
            elif ref_val.startswith("res://"):
                clean = ref_val.replace("res://", "")
                if clean not in existing:
                    errors.append({
                        "file": rel,
                        "type": "node_ref_broken_path",
                        "node": nref["node"],
                        "ref_type": nref["ref_type"],
                        "reference": ref_val,
                        "message": f"Node '{nref['node']}': {nref['ref_type']}={ref_val} — cena nao encontrada.",
                    })
            elif ref_val.startswith("SubResource"):
                sub_id = ref_val.split('"')[1]
                if sub_id not in sub_map:
                    errors.append({
                        "file": rel,
                        "type": "node_ref_broken_sub",
                        "node": nref["node"],
                        "ref_type": nref["ref_type"],
                        "reference": ref_val,
                        "message": f"Node '{nref['node']}': {nref['ref_type']}={ref_val} — sub_resource nao definido.",
                    })

    # ── Varre .gd ──
    for gd_file in sorted(proj.glob("**/*.gd")):
        if _should_skip(gd_file):
            continue
        rel = str(gd_file.relative_to(proj))
        try:
            content = gd_file.read_text(encoding="utf-8")
        except Exception:
            continue
        files_scanned += 1

        # preload("res://...")
        for m in re.finditer(r'preload\s*\(\s*"res://([^"]+)"', content):
            ref = m.group(1)
            if ref not in existing:
                errors.append({
                    "file": rel,
                    "type": "gdscript_preload",
                    "reference": f'res://{ref}',
                    "message": f"preload('res://{ref}') — recurso nao encontrado.",
                })

        # load("res://...") — bare load() e self.load() (nao ResourceLoader.load)
        for m in re.finditer(r'(?<!ResourceLoader\.)load\s*\(\s*"res://([^"]+)"', content):
            ref = m.group(1)
            if ref not in existing:
                errors.append({
                    "file": rel,
                    "type": "gdscript_load",
                    "reference": f'res://{ref}',
                    "message": f"load('res://{ref}') — recurso nao encontrado.",
                })

        # ResourceLoader.load("res://...")
        for m in re.finditer(r'ResourceLoader\.load\s*\(\s*"res://([^"]+)"', content):
            ref = m.group(1)
            if ref not in existing:
                errors.append({
                    "file": rel,
                    "type": "gdscript_resourceloader",
                    "reference": f'res://{ref}',
                    "message": f"ResourceLoader.load('res://{ref}') — recurso nao encontrado.",
                })

        # change_scene_to_file("res://...")
        for m in re.finditer(r'change_scene_to_file\s*\(\s*"res://([^"]+)"', content):
            ref = m.group(1)
            if ref not in existing:
                errors.append({
                    "file": rel,
                    "type": "gdscript_change_scene",
                    "reference": f'res://{ref}',
                    "message": f"change_scene_to_file('res://{ref}') — cena nao encontrada.",
                })

        # class_name duplicado (warning)
        class_names_found: list[str] = []
        for m in re.finditer(r'class_name\s+(\w+)', content):
            class_names_found.append(m.group(1))
        if len(class_names_found) > 1:
            warnings.append({
                "file": rel,
                "type": "gdscript_dup_class_name",
                "message": f"Multiplos class_name no mesmo arquivo: {class_names_found}. Apenas o primeiro sera usado.",
            })

    # ── Sumario ──
    error_count = len(errors)
    warning_count = len(warnings)
    max_results = None if full_report else 100

    return {
        "status": "success",
        "project": str(proj),
        "total_files_scanned": files_scanned,
        "summary": {
            "errors": error_count,
            "warnings": warning_count,
            "verdict": "LIMPO — nenhuma referencia quebrada." if error_count == 0
                       else f"{error_count} referencia(s) quebrada(s) encontrada(s).",
        },
        "errors": errors[:max_results] if max_results else errors,
        "warnings": warnings[:max_results] if max_results else warnings,
        "truncated": max_results is not None and (error_count > max_results or warning_count > max_results),
    }


# ══════════════════════════════════════════════════════════════════════
# find_usages
# ══════════════════════════════════════════════════════════════════════

def find_usages(
    target: str,
    project_path: str | None = None,
    search_type: str = "auto",
    max_results: int = 50,
) -> dict:
    """Encontra TODOS os usos de um recurso/alvo no projeto.

    Busca estatica (nao requer LSP nem Godot aberto). Funciona em:
    - .tscn: ExtResource("N") onde N aponta para o target
    - .tscn: scene = "res://target" (instancias de cena)
    - .gd: preload/load/ResourceLoader.load apontando para o target
    - .gd: change_scene_to_file apontando para o target

    Args:
        target: Nome do arquivo ou path parcial (ex: "player.gd", "scripts/player.gd").
        project_path: Caminho do projeto (opcional).
        search_type: "auto" (detecta), "script", "scene", "texture", "any".
        max_results: Limite de resultados (default 50).

    Returns:
        {"status": "success", "target": str, "usages": [...], "total": int}
    """
    proj = _resolve_project(project_path)
    if not proj:
        return {"status": "error", "message": "Projeto nao encontrado."}

    # Valida search_type
    valid_types = {"auto", "script", "scene", "texture", "any"}
    if search_type not in valid_types:
        return {"status": "error", "message": f"search_type invalido: '{search_type}'. Use: {sorted(valid_types)}."}

    # Normaliza target: remove res:// se presente
    target_clean = target.replace("res://", "").replace("\\", "/")
    usages: list[dict] = []

    # ── Constrói mapeamento: ext_resource id → path ──
    # Para cada .tscn, mapeia qual ID aponta para o target
    # Depois busca ExtResource("N") nos nodes e em outros TSCN

    # ── Varre .tscn ──
    for tscn in sorted(proj.glob("**/*.tscn")):
        if _should_skip(tscn):
            continue
        rel = str(tscn.relative_to(proj))
        try:
            content = tscn.read_text(encoding="utf-8")
        except Exception:
            continue

        ext_map = _parse_tscn_ext_resources(content)

        # Se o target for um script/scene, encontra o ext_resource ID
        target_ids: list[str] = []
        for ext_id, ref_path in ext_map.items():
            clean = ref_path.replace("res://", "")
            if _matches_target(clean, target_clean, search_type):
                target_ids.append(ext_id)

        # Busca usos nos nodes
        node_refs = _parse_tscn_node_refs(content)
        for nref in node_refs:
            ref_val = nref["ref_value"]
            if ref_val.startswith("ExtResource"):
                ext_id = ref_val.split('"')[1]
                if ext_id in target_ids:
                    usages.append({
                        "file": rel,
                        "location": f"node '{nref['node']}'",
                        "ref_type": nref["ref_type"],
                        "reference": ref_val,
                        "resolved_path": ext_map.get(ext_id, "?"),
                    })
            elif ref_val.startswith("res://"):
                clean = ref_val.replace("res://", "")
                if _matches_target(clean, target_clean, search_type):
                    usages.append({
                        "file": rel,
                        "location": f"node '{nref['node']}'",
                        "ref_type": nref["ref_type"],
                        "reference": ref_val,
                    })

    # ── Varre .gd ──
    for gd_file in sorted(proj.glob("**/*.gd")):
        if _should_skip(gd_file):
            continue
        rel = str(gd_file.relative_to(proj))
        try:
            content = gd_file.read_text(encoding="utf-8")
        except Exception:
            continue

        patterns = [
            (r'preload\s*\(\s*"res://([^"]+)"', "preload"),
            (r'(?<!ResourceLoader\.)load\s*\(\s*"res://([^"]+)"', "load"),
            (r'ResourceLoader\.load\s*\(\s*"res://([^"]+)"', "ResourceLoader.load"),
            (r'change_scene_to_file\s*\(\s*"res://([^"]+)"', "change_scene_to_file"),
        ]

        for pattern, ref_type in patterns:
            for m in re.finditer(pattern, content):
                ref = m.group(1)
                if _matches_target(ref, target_clean, search_type):
                    # Pega o numero da linha
                    line_num = content[:m.start()].count("\n") + 1
                    usages.append({
                        "file": rel,
                        "location": f"linha {line_num}",
                        "ref_type": ref_type,
                        "reference": f'res://{ref}',
                    })

    # ── Limita resultados ──
    total = len(usages)
    usages = usages[:max_results]

    return {
        "status": "success",
        "target": target,
        "total": total,
        "usages": usages,
        "truncated": total > max_results,
        "note": f"{total} uso(s) encontrado(s) para '{target}'." if total > 0
                else f"Nenhum uso encontrado para '{target}'. Verifique se o nome do arquivo esta correto.",
    }


# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════

def _resolve_project(project_path: str | None) -> Path | None:
    """Resolve o caminho do projeto."""
    if project_path:
        proj = Path(project_path)
        if proj.exists():
            return proj
    try:
        return _get_active_project()
    except Exception:
        return None


def _collect_existing_files(proj: Path) -> set[str]:
    """Coleta todos os paths relativos de arquivos existentes no projeto."""
    existing: set[str] = set()
    for f in proj.rglob("*"):
        if f.is_file() and not _should_skip(f):
            existing.add(str(f.relative_to(proj)).replace("\\", "/"))
    return existing


def _should_skip(path: Path) -> bool:
    """Verifica se um path deve ser pulado."""
    skip_dirs = {".godot", ".mcp_backups", "addons", ".git", "__pycache__"}
    return any(skip in path.parts for skip in skip_dirs)


def _matches_target(ref: str, target: str, search_type: str) -> bool:
    """Verifica se uma referencia corresponde ao target.

    Args:
        ref: Path relativo da referencia (sem res://).
        target: Target de busca.
        search_type: "auto", "script", "scene", "texture", "any".
    """
    if search_type == "any":
        return target in ref

    if search_type == "script" and not ref.endswith(".gd"):
        return False
    if search_type == "scene" and not ref.endswith(".tscn"):
        return False
    if search_type == "texture" and not (ref.endswith(".png") or ref.endswith(".jpg") or ref.endswith(".svg")):
        return False

    # auto: match parcial no nome do arquivo
    return target in ref
