"""scene_ops — Operações de criação e manipulação de cenas (.tscn).

Fase 1: create_scene, load_scene_tree, add_node, delete_node,
set_node_property, get_node_property.
Fase 4: create_tileset, create_tilemap_layer, paint_tilemap_cell,
create_animation, create_animation_player, create_ui_scene, add_control_node.
"""

import re
import subprocess
from pathlib import Path
from typing import Any

import godot_parser as gp

from tools.classdb import is_valid_node_type, is_valid_property, suggest_similar_node_type, get_godot_bin, get_config, list_signals
from tools.project_ops import _get_active_project, _check_path_traversal
from tools.safety import checkpoint, push_undo


# ── Bridge Mode Helper ──────────────────────────────────────────────

def _editor_bridge_available() -> bool:
    """Verifica se o editor bridge está conectado (Modo Direto)."""
    try:
        from tools.bridge import is_editor_connected
        return is_editor_connected()
    except Exception:
        return False


def _addon_bridge_available() -> bool:
    """Verifica se o addon bridge está conectado (Modo Addon)."""
    try:
        from tools.addon_bridge import get_bridge
        return get_bridge().is_editor_open()
    except Exception:
        return False


def _should_use_bridge() -> bool:
    """Dispatch gate: True se qualquer bridge está disponível.

    Prioridade: editor bridge → addon bridge → headless.
    """
    try:
        from tools.bridge import should_use_bridge
        return should_use_bridge()
    except Exception:
        return _editor_bridge_available() or _addon_bridge_available()


def _game_bridge_available() -> bool:
    """Verifica se o game bridge está conectado (Runtime Modo Direto)."""
    try:
        from tools.game_bridge import is_connected
        return is_connected()
    except Exception:
        return False


def _get_open_scene_path() -> str:
    """Retorna o caminho da cena aberta no editor, ou vazio."""
    try:
        from tools.editor_bridge import get_scene_tree_in_editor
        r = get_scene_tree_in_editor()
        if isinstance(r, dict):
            return r.get("scene", "")
    except Exception:
        pass
    return ""


def _resolve_scene_path_from_vibe() -> str | None:
    """Resolve scene_path do Vibe Coding Mode ou ExecutionContext (Etapa A2).

    Ordem de precedência:
    1. Vibe Coding Mode (se ativo com scene_path definido)
    2. ExecutionContext.active_scene (injetado automaticamente pelo call_tool)
    3. None — o chamador deve retornar erro amigável

    Returns:
        str com o caminho da cena ou None se não disponível.
    """
    # ── 1. Vibe Coding Mode ──
    try:
        from tools.vibe_ops import get_vibe_context
        ctx = get_vibe_context()
        vibe = ctx.get("vibe_coding", {})
        if vibe.get("enabled") and vibe.get("scene_path"):
            return vibe["scene_path"]
    except Exception:
        pass

    # ── 2. ExecutionContext (Etapa A2) ──
    try:
        from core.context import get_execution_context
        exec_ctx = get_execution_context()
        if exec_ctx is not None and exec_ctx.active_scene:
            return exec_ctx.active_scene
    except Exception:
        pass

    return None


def _ensure_scene_open(scene_path: str, proj) -> bool:
    """Garante que a cena correta está aberta no editor. GAP #12.

    Se o editor está conectado mas a cena aberta não é a desejada,
    tenta abrir a cena correta automaticamente.

    Returns:
        True se a cena está aberta (ou foi aberta com sucesso).
    """
    if not _editor_bridge_available():
        return False
    open_scene = _get_open_scene_path()
    if open_scene and (scene_path in open_scene or open_scene.endswith(scene_path)):
        return True  # Já está aberta
    # Tenta abrir a cena correta
    try:
        from tools.editor_bridge import open_scene_in_editor
        res_path = "res://" + scene_path if not scene_path.startswith("res://") else scene_path
        r = open_scene_in_editor(res_path)
        return r.get("status") == "success"
    except Exception:
        return False


# ── Helpers ─────────────────────────────────────────────────────────

def _resolve_scene_path(path: str, project_root: Path) -> Path:
    """Resolve caminho de cena para path absoluto."""
    return project_root / path


def _validate_node_type(node_type: str) -> dict | None:
    """Valida tipo de nó contra ClassDB.

    Returns:
        None se válido, dict de erro se inválido.
    """
    if not is_valid_node_type(node_type):
        suggestions = suggest_similar_node_type(node_type)
        return {
            "status": "error",
            "message": (
                f"Tipo de nó inválido: '{node_type}'. "
                f"Em Godot 4, use os tipos corretos (ex: 'Sprite2D' em vez de 'Sprite'). "
                f"Tipos próximos válidos: {suggestions}."
            ),
            "suggestions": suggestions,
        }
    return None


def _run_compile_test(project_root: Path) -> dict:
    """Executa compile_test no projeto e retorna erros encontrados."""
    godot = get_godot_bin()
    cfg = get_config()
    timeout = cfg.get("timeouts", {}).get("compile", 60)
    try:
        result = subprocess.run(
            [godot, "--headless", "--editor", "--quit", "--path", str(project_root)],
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
        errors = []
        for line in (result.stdout + "\n" + result.stderr).splitlines():
            if any(kw in line for kw in ("ERROR", "SCRIPT ERROR", "Parse Error", "error:")):
                errors.append(line.strip())
        return {"status": "success", "errors": errors}
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Timeout ao rodar compile_test."}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao rodar compile_test: {e}"}


# ── Cache de parsing .tscn (evita re-parsear a mesma cena) ──
_tscn_cache: dict[str, tuple[float, list[str], list[dict]]] = {}
_MAX_CACHE_SIZE = 12


# B3 FIX: Deduplica ext_resource e propriedades antes de escrever .tscn
def _deduplicate_tscn_lines(lines: list[str]) -> list[str]:
    """Remove ext_resource duplicados e propriedades duplicadas por nó.

    Evita corrupção como 3x 'script = ExtResource(...)' no mesmo nó.
    """
    # Passo 1: Remove ext_resource duplicados (mantém o primeiro por path)
    seen_resources: dict[str, str] = {}  # path -> id
    deduped: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[ext_resource"):
            # Extrai path e id
            path_m = re.search(r'path="([^"]*)"', stripped)
            id_m = re.search(r'id="([^"]*)"', stripped)
            if path_m:
                rpath = path_m.group(1)
                if rpath in seen_resources:
                    # Substitui referências ao ID antigo pelo ID mantido
                    old_id = id_m.group(1) if id_m else ""
                    kept_id = seen_resources[rpath]
                    if old_id and old_id != kept_id:
                        for j in range(len(deduped)):
                            deduped[j] = deduped[j].replace(f'ExtResource("{old_id}")', f'ExtResource("{kept_id}")')
                        for j in range(len(lines)):
                            if j > lines.index(line):
                                lines[j] = lines[j].replace(f'ExtResource("{old_id}")', f'ExtResource("{kept_id}")')
                    continue  # pula este ext_resource duplicado
                elif id_m:
                    seen_resources[rpath] = id_m.group(1)
        deduped.append(line)

    # Passo 2: Remove propriedades duplicadas no mesmo nó
    result: list[str] = []
    current_node_start = -1
    seen_props: set[str] = set()
    i = 0
    while i < len(deduped):
        line = deduped[i]
        stripped = line.strip()
        if stripped.startswith("[node "):
            # Novo nó: reseta seen_props
            current_node_start = i
            seen_props = set()
            result.append(line)
        elif "=" in stripped and not stripped.startswith("[") and not stripped.startswith(";"):
            prop_name = stripped.split("=")[0].strip()
            if prop_name in seen_props:
                # Propriedade duplicada: substitui a anterior
                for j in range(len(result) - 1, -1, -1):
                    if result[j].strip().startswith(f"{prop_name}=") or result[j].strip().startswith(f"{prop_name} ="):
                        result[j] = line
                        break
            else:
                seen_props.add(prop_name)
                result.append(line)
        else:
            result.append(line)
        i += 1

    # Passo 3: Corrige load_steps (conta resources únicos)
    resource_count = sum(1 for l in result if l.strip().startswith("[ext_resource"))
    for j in range(len(result)):
        if result[j].strip().startswith("[gd_scene"):
            result[j] = re.sub(r'load_steps=\d+', f'load_steps={1 + resource_count}', result[j])
            break

    return result


def _parse_tscn_content(filepath: Path) -> tuple[list[str], list[dict]]:
    """Parseia conteúdo raw de .tscn em linhas e nós (com cache por mtime)."""
    key = str(filepath.resolve())
    mtime = filepath.stat().st_mtime if filepath.exists() else 0.0

    if key in _tscn_cache:
        cached_mtime, cached_lines, cached_nodes = _tscn_cache[key]
        if cached_mtime == mtime:
            return cached_lines, cached_nodes

    lines = filepath.read_text(encoding="utf-8").splitlines(keepends=True)
    nodes = []
    current_node = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        node_match = re.match(r'\[node\s+name="([^"]*)"(?:\s+type="([^"]*)")?(?:\s+parent="([^"]*)")?', stripped)
        if node_match:
            if current_node:
                current_node["line_end"] = i
                nodes.append(current_node)
            current_node = {
                "name": node_match.group(1),
                "type": node_match.group(2) or "",
                "parent": node_match.group(3) or "",
                "line_start": i,
                "line_end": i + 1,
                "properties": {},
            }
        elif current_node and "=" in stripped and not stripped.startswith("[") and not stripped.startswith(";"):
            key_prop, _, value = stripped.partition("=")
            current_node["properties"][key_prop.strip()] = value.strip()

    if current_node:
        current_node["line_end"] = len(lines)
        nodes.append(current_node)

    if len(_tscn_cache) >= _MAX_CACHE_SIZE:
        _tscn_cache.pop(next(iter(_tscn_cache)))
    _tscn_cache[key] = (mtime, lines, nodes)

    return lines, nodes


def _find_node_in_parsed(nodes: list[dict], node_path: str) -> dict | None:
    """Encontra um nó por path (ex: '.' ou './Child' ou './Child/Grandchild')."""
    if node_path == ".":
        # Raiz: nó sem parent ou com parent vazio
        for n in nodes:
            if not n.get("parent"):
                return n
        return nodes[0] if nodes else None

    # Remove './' prefix
    path = node_path.lstrip("./")
    parts = path.split("/")
    if not parts:
        return None

    # Encontra a raiz primeiro
    root = None
    for n in nodes:
        if not n.get("parent"):
            root = n
            break
    if not root:
        return None

    current = root
    for part in parts:
        found = None
        for n in nodes:
            parent = n.get("parent") or ""
            # Godot .tscn usa parent="." para indicar "filho da raiz"
            matches_parent = (
                parent == current["name"]
                or (parent == "." and current is root)
            )
            if matches_parent and n["name"] == part:
                found = n
                break
        if not found:
            return None
        current = found
    return current


def _list_node_paths_from_parsed(nodes: list[dict]) -> list[str]:
    """Extrai todos os node_paths de uma lista de nós parseados."""
    paths = []
    for n in nodes:
        name = n.get("name", "")
        parent = n.get("parent", "")
        if parent and parent != ".":
            paths.append(f"{parent}/{name}")
        else:
            paths.append(name if name else ".")
    return paths


# ── API Pública ─────────────────────────────────────────────────────

def create_scene(name: str, root_type: str, path: str) -> dict:
    """Cria uma nova cena (.tscn) com um nó raiz.

    Idempotente (Fatia 0.13): se a cena já existe, retorna sucesso
    com {"idempotent": True} — não cria duplicata nem sobrescreve.

    Args:
        name: Nome do nó raiz (ex: "Main").
        root_type: Tipo do nó raiz (ex: "Node2D"). Validado contra ClassDB.
        path: Caminho relativo ao projeto (ex: "scenes/main.tscn").

    Returns:
        {"status": "success", "path": str, "idempotent": bool|None}
        ou {"status": "error", "message": str}
    """
    proj = _get_active_project()

    violation = _check_path_traversal(path, proj)
    if violation:
        return {"status": "error", "message": violation}

    # Valida tipo
    err = _validate_node_type(root_type)
    if err:
        return err

    full_path = proj / path
    if full_path.exists():
        return {
            "status": "success",
            "path": path,
            "idempotent": True,
            "note": f"Cena '{path}' já existia. Use delete_file primeiro se quiser substituir.",
        }

    full_path.parent.mkdir(parents=True, exist_ok=True)

    # Constrói .tscn
    content = f"""[gd_scene load_steps=2 format=2]

[node name="{name}" type="{root_type}"]
"""
    full_path.write_text(content, encoding="utf-8")

    # ── Auto-config: definir run/main_scene se ainda nao existe ──
    try:
        godot_file = proj / "project.godot"
        if godot_file.exists():
            cfg_text = godot_file.read_text(encoding="utf-8")
            if "run/main_scene" not in cfg_text:
                # Adiciona run/main_scene na secao [application]
                if "[application]" in cfg_text:
                    cfg_text = cfg_text.replace(
                        "[application]",
                        "[application]\n\nrun/main_scene=\"%s\"" % path,
                    )
                    godot_file.write_text(cfg_text, encoding="utf-8")
    except Exception:
        pass  # falha nao-critica: o projeto funciona sem isso, so da alerta

    # Marca para compilação pendente (executada em compile_test/run_game)
    from tools.runtime_ops import mark_pending_compile
    mark_pending_compile()

    return {"status": "success", "path": path}


def load_scene_tree(scene_path: str | None = None, max_depth: int | None = None) -> dict:
    """Carrega a árvore de nós de uma cena.

    Args:
        scene_path: Caminho relativo da cena. Se omitido, usa Vibe Coding Mode.
        max_depth: Profundidade máxima (None = sem limite).

    Returns:
        {"status": "success", "tree": {"name", "type", "properties": {}, "children": [...]}}
        ou {"status": "error", "message": str}
    """
    if scene_path is None:
        scene_path = _resolve_scene_path_from_vibe()
        if scene_path is None:
            return {"status": "error", "message": "scene_path nao informado e Vibe Coding Mode nao esta ativo. Informe scene_path ou ative vibe_coding_mode com uma cena definida."}
    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {
            "status": "error",
            "message": f"Cena '{scene_path}' não encontrada. Use create_scene para criar.",
        }

    try:
        scene = gp.load(str(full_path))
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao parsear cena: {e}",
        }

    # Constrói árvore a partir dos nós
    nodes_list = scene.get_nodes()
    raw_nodes = []
    for n in nodes_list:
        node_dict = {
            "name": n.name,
            "type": n.type or "",
            "parent": n.parent or "",
            "properties": {},
        }
        if hasattr(n, "get"):
            for key in ["position", "scale", "rotation", "visible", "name",
                        "modulate", "texture", "region_enabled", "region_rect"]:
                try:
                    val = n.get(key)
                    if val is not None:
                        node_dict["properties"][key] = str(val)
                except Exception:
                    pass
        raw_nodes.append(node_dict)

    # Monta árvore — abordagem iterativa sem recursão bugada
    # Cria lookup por nome
    node_map = {n["name"]: {**n, "children": []} for n in raw_nodes}

    # Encontra raiz
    root = None
    for n in raw_nodes:
        if not n["parent"]:
            root = node_map[n["name"]]
            break
    if not root and raw_nodes:
        root = node_map[raw_nodes[0]["name"]]

    # Conecta filhos aos pais
    for n in raw_nodes:
        if n["parent"] and n["parent"] in node_map:
            parent = node_map[n["parent"]]
            child = node_map[n["name"]]
            if child not in parent["children"]:
                parent["children"].append(child)

    # ── Poda por max_depth (Onda 2) ────────────────────────────────
    if max_depth is not None and root:
        _prune_tree_depth(root, max_depth, 0)

    tree = root if root else {"name": "", "type": "", "children": []}
    return {"status": "success", "tree": tree}


def _prune_tree_depth(node: dict, max_depth: int, current_depth: int) -> None:
    """Recursivamente substitui filhos por placeholder quando excede max_depth."""
    if current_depth >= max_depth:
        count = len(node.get("children", []))
        if count > 0:
            node["children"] = [{
                "name": f"... ({count} nós podados)",
                "type": "_truncated",
                "children": [],
                "properties": {},
                "note": f"Use max_depth > {max_depth} ou None para ver todos os {count} descendentes."
            }]
        return
    for child in node.get("children", []):
        _prune_tree_depth(child, max_depth, current_depth + 1)

    tree = root if root else {"name": "", "type": "", "children": []}
    return {"status": "success", "tree": tree}


def add_node(scene_path: str | None = None, parent_node_path: str = ".", node_name: str = "", node_type: str = "Node") -> dict:
    """Adiciona um nó a uma cena existente.

    Args:
        scene_path: Caminho relativo da cena.
        parent_node_path: Path do nó pai ("." = raiz).
        node_name: Nome do novo nó.
        node_type: Tipo do nó (validado contra ClassDB).

    Returns:
        {"status": "success", "node_path": str}
        ou {"status": "error", "message": str}
    """
    if scene_path is None:
        scene_path = _resolve_scene_path_from_vibe()
        if scene_path is None:
            return {"status": "error", "message": "scene_path nao informado e Vibe Coding Mode nao esta ativo. Informe scene_path ou ative vibe_coding_mode com uma cena definida."}
    # ── Modo Direto: cria nó em TEMPO REAL ──────────────────
    # Prioridade: 1) Editor Bridge (auto-abre cena se necessário)
    #             2) Game Bridge (jogo rodando)
    #             3) Arquivo (fallback)
    if _editor_bridge_available() and _ensure_scene_open(scene_path, None):
        from tools.editor_bridge import create_node_in_editor
        return create_node_in_editor(parent_node_path, node_name, node_type)

    # ── Game Bridge: cria nó no jogo rodando ─────────────────
    if _game_bridge_available():
        from tools.game_bridge import _send as gb_send
        result = gb_send("create_node", {
            "parent_path": parent_node_path,
            "node_name": node_name,
            "node_type": node_type,
        })
        if result.get("status") == "success":
            result["mode"] = "game_bridge"
            result["note"] = "Nó criado no jogo rodando (não persiste no .tscn)."
            return result

    proj = _get_active_project()

    violation = _check_path_traversal(scene_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    full_path = proj / scene_path

    if not full_path.exists():
        return {
            "status": "error",
            "message": f"Cena '{scene_path}' não encontrada. Use create_scene primeiro.",
        }

    # Valida tipo
    err = _validate_node_type(node_type)
    if err:
        return err

    # Parseia
    lines, nodes = _parse_tscn_content(full_path)

    # Encontra pai
    parent_node = _find_node_in_parsed(nodes, parent_node_path)
    if not parent_node:
        return {
            "status": "error",
            "message": f"Nó pai '{parent_node_path}' não encontrado na cena. "
                       f"Use load_scene_tree para ver a árvore de nós.",
        }

    # Verifica se nó com mesmo nome já existe sob o pai (idempotente: retorna sucesso)
    for n in nodes:
        if n.get("parent") == parent_node["name"] and n["name"] == node_name:
            return {
                "status": "success",
                "node_path": f"{scene_path}::{node_name}",
                "idempotent": True,
                "note": f"Nó '{node_name}' já existia sob '{parent_node_path}'. Nada foi alterado.",
            }

    # Checkpoint
    checkpoint(scene_path, proj)

    # Encontra a última linha que pertence ao escopo do pai
    parent_name = parent_node["name"]
    insert_line = parent_node["line_end"]
    for i in range(parent_node["line_start"], len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("[node ") and i > parent_node["line_start"]:
            break
        insert_line = i + 1

    # Insere
    parent_attr = f' parent="{parent_name}"' if parent_name else ""
    new_node_lines = [
        f'[node name="{node_name}" type="{node_type}"{parent_attr}]\n',
    ]
    for i, line in enumerate(new_node_lines):
        lines.insert(insert_line + i, line)

# B3 FIX: Deduplica antes de escrever
    lines = _deduplicate_tscn_lines(lines)
    full_path.write_text("".join(lines), encoding="utf-8")

    # Invalida cache para que load_scene_tree veja a mudança
    _tscn_cache.pop(str(full_path), None)

    # Marca para compilação pendente
    from tools.runtime_ops import mark_pending_compile
    mark_pending_compile()

    return {"status": "success", "node_path": f"{scene_path}::{node_name}"}


def delete_node(scene_path: str | None = None, node_path: str = "") -> dict:
    """Remove um nó de uma cena.

    Args:
        scene_path: Caminho relativo da cena.
        node_path: Path do nó a remover (não pode ser a raiz ".").

    Returns:
        {"status": "success", "backup_id": str}
        ou {"status": "error", "message": str}
    """
    if scene_path is None:
        scene_path = _resolve_scene_path_from_vibe()
        if scene_path is None:
            return {"status": "error", "message": "scene_path nao informado e Vibe Coding Mode nao esta ativo. Informe scene_path ou ative vibe_coding_mode com uma cena definida."}
    # ── Modo Direto ──────────────────────────────────────────
    # Prioridade: 1) Editor Bridge  2) Game Bridge  3) Arquivo
    if _editor_bridge_available() and _ensure_scene_open(scene_path, None):
        from tools.editor_bridge import delete_node_in_editor
        return delete_node_in_editor(node_path)

    if _game_bridge_available():
        from tools.game_bridge import _send as gb_send
        result = gb_send("delete_node", {"node_path": node_path})
        if result.get("status") == "success":
            result["mode"] = "game_bridge"
            result["note"] = "Nó removido do jogo rodando."
            return result

    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {
            "status": "error",
            "message": f"Cena '{scene_path}' não encontrada.",
        }

    if node_path == ".":
        return {
            "status": "error",
            "message": "Não é permitido deletar o nó raiz. Use delete_file para remover a cena inteira.",
        }

    lines, nodes = _parse_tscn_content(full_path)

    target = _find_node_in_parsed(nodes, node_path)
    if not target:
        # Idempotente: se já foi removido, retorna sucesso
        return {
            "status": "success",
            "idempotent": True,
            "note": f"Nó '{node_path}' já não existia na cena (provavelmente já foi removido). Nada foi alterado.",
        }

    # Encontra todos os descendentes (nós cujo parent é o target ou descendente)
    names_to_delete = {target["name"]}
    changed = True
    while changed:
        changed = False
        for n in nodes:
            if n.get("parent") in names_to_delete and n["name"] not in names_to_delete:
                names_to_delete.add(n["name"])
                changed = True

    # Remove linhas dos nós a deletar
    nodes_to_remove = [n for n in nodes if n["name"] in names_to_delete]
    nodes_to_remove.sort(key=lambda n: n["line_start"], reverse=True)

    backup_id = checkpoint(scene_path, proj)

    for n in nodes_to_remove:
        del lines[n["line_start"]:n["line_end"]]

    full_path.write_text("".join(lines), encoding="utf-8")

    # Invalida cache
    _tscn_cache.pop(str(full_path), None)

    from tools.runtime_ops import mark_pending_compile
    mark_pending_compile()

    return {"status": "success", "backup_id": backup_id or "unknown"}


def set_node_property(scene_path: str | None = None, node_path: str = "", property_name: str = "", value: Any = None) -> dict:
    """Define uma propriedade de um nó em uma cena.

    Modo Direto: muda em TEMPO REAL no editor se bridge conectado.
    """
    if scene_path is None:
        scene_path = _resolve_scene_path_from_vibe()
        if scene_path is None:
            return {"status": "error", "message": "scene_path nao informado e Vibe Coding Mode nao esta ativo. Informe scene_path ou ative vibe_coding_mode com uma cena definida."}
    # ── Modo Direto ──────────────────────────────────────────
    # Prioridade: 1) Editor Bridge  2) Game Bridge  3) Arquivo
    if _editor_bridge_available() and _ensure_scene_open(scene_path, None):
        from tools.editor_bridge import set_node_property_in_editor
        return set_node_property_in_editor(node_path, property_name, value)

    if _game_bridge_available():
        from tools.game_bridge import _send as gb_send
        result = gb_send("set_node_property", {
            "node_path": node_path,
            "property_name": property_name,
            "value": str(value),
        })
        if result.get("status") == "success":
            result["mode"] = "game_bridge"
            result["note"] = "Propriedade alterada no jogo rodando."
            return result

    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {
            "status": "error",
            "message": f"Cena '{scene_path}' não encontrada.",
        }

    lines, nodes = _parse_tscn_content(full_path)

    target = _find_node_in_parsed(nodes, node_path)
    if not target:
        return {
            "status": "error",
            "message": f"Nó '{node_path}' não encontrado na cena.",
        }

    # Valida propriedade se o tipo do nó for conhecido
    if target.get("type") and not is_valid_property(target["type"], property_name):
        # Não bloqueia — pode ser propriedade de script anexado
        pass

    # Serializa valor
    val_str = _serialize_godot_value(value)

    # Verifica se a propriedade já existe
    prop_found = False
    for i in range(target["line_start"], target["line_end"]):
        stripped = lines[i].strip()
        if stripped.startswith(f"{property_name}=") or stripped.startswith(f"{property_name} ="):
            lines[i] = f"{property_name} = {val_str}\n"
            prop_found = True
            break

    if not prop_found:
        # Insere após a linha do nó
        insert_at = target["line_start"] + 1
        lines.insert(insert_at, f"{property_name} = {val_str}\n")
        # Atualiza line_end de todos os nós afetados
        for n in nodes:
            if n["line_start"] >= insert_at:
                n["line_start"] += 1
                n["line_end"] += 1

    checkpoint(scene_path, proj)
    # B3 FIX: Deduplica antes de escrever
    lines = _deduplicate_tscn_lines(lines)

    full_path.write_text("".join(lines), encoding="utf-8")

    # Invalida cache para que load_scene_tree veja a mudança
    _tscn_cache.pop(str(full_path), None)

    # Marca para compilação pendente
    from tools.runtime_ops import mark_pending_compile
    mark_pending_compile()

    return {"status": "success"}


def get_node_property(scene_path: str | None = None, node_path: str = "", property_name: str = "", property: str | None = None) -> dict:
    """Lê uma propriedade de um nó. Modo Direto se editor aberto."""
    # Alias: 'property' aceito como sinônimo de 'property_name' para compatibilidade com rollup node_manage
    if property is not None and not property_name:
        property_name = property
    if scene_path is None:
        scene_path = _resolve_scene_path_from_vibe()
        if scene_path is None:
            return {"status": "error", "message": "scene_path nao informado e Vibe Coding Mode nao esta ativo. Informe scene_path ou ative vibe_coding_mode com uma cena definida."}
    # ── Modo Direto ──────────────────────────────────────────
    # Prioridade: 1) Editor Bridge  2) Game Bridge  3) Arquivo
    if _editor_bridge_available() and _ensure_scene_open(scene_path, None):
        from tools.editor_bridge import get_node_property_in_editor
        return get_node_property_in_editor(node_path, property_name)

    if _game_bridge_available():
        from tools.game_bridge import _send as gb_send
        result = gb_send("get_node_property", {
            "node_path": node_path,
            "property_name": property_name,
        })
        if result.get("status") == "success":
            result["mode"] = "game_bridge"
            return result

    proj = _get_active_project()

    violation = _check_path_traversal(scene_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    full_path = proj / scene_path

    if not full_path.exists():
        return {
            "status": "error",
            "message": f"Cena '{scene_path}' não encontrada.",
        }

    _, nodes = _parse_tscn_content(full_path)

    target = _find_node_in_parsed(nodes, node_path)
    if not target:
        from tools.fuzzy_suggest import not_found_error
        all_paths = _list_node_paths_from_parsed(nodes)
        return not_found_error("nó", node_path, all_paths)

    value = target["properties"].get(property_name)
    if value is None:
        return {
            "status": "success",
            "value": None,
            "note": "Propriedade não está definida explicitamente no arquivo (usando default da classe).",
        }

    return {"status": "success", "value": value}


# ── Serialização de valores Godot ───────────────────────────────────

def _serialize_godot_value(value: Any) -> str:
    """Serializa um valor Python para representação em .tscn."""
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        if re.match(r'^(Vector[234]|Color|Rect[234]|Transform[23]D|AABB|Plane|Quaternion|Basis|Projection)\(', value):
            return value
        if value.startswith("ExtResource(") or value.startswith("SubResource("):
            return value
        return f'"{value}"'
    elif value is None:
        return "null"
    else:
        return str(value)


# ── Fase 2: Extensões de cena ──────────────────────────────────────

def reparent_node(scene_path: str | None = None, node_path: str = "", new_parent_path: str = ".") -> dict:
    """Move um nó para um novo pai na mesma cena.

    Args:
        scene_path: Caminho relativo da cena.
        node_path: Path do nó a mover.
        new_parent_path: Path do novo pai.

    Returns:
        {"status": "success", "new_node_path": str}
    """
    if scene_path is None:
        scene_path = _resolve_scene_path_from_vibe()
        if scene_path is None:
            return {"status": "error", "message": "scene_path nao informado e Vibe Coding Mode nao esta ativo. Informe scene_path ou ative vibe_coding_mode com uma cena definida."}
    proj = _get_active_project()

    violation = _check_path_traversal(scene_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    lines, nodes = _parse_tscn_content(full_path)

    target = _find_node_in_parsed(nodes, node_path)
    if not target:
        return {"status": "error", "message": f"Nó '{node_path}' não encontrado."}

    new_parent = _find_node_in_parsed(nodes, new_parent_path)
    if not new_parent:
        return {"status": "error", "message": f"Novo pai '{new_parent_path}' não encontrado."}

    if node_path == ".":
        return {"status": "error", "message": "Não é permitido mover o nó raiz."}

    parent_name = new_parent["name"] if new_parent_path != "." else ""
    new_parent_ref = f' parent="{parent_name}"' if parent_name else ""

    # Altera a linha do nó para atualizar o parent
    checkpoint(scene_path, proj)
    old_line = lines[target["line_start"]]
    if 'parent="' in old_line:
        lines[target["line_start"]] = re.sub(r'parent="[^"]*"', f'parent="{parent_name}"', old_line)
    elif new_parent_ref:
        # Adiciona parent ao final da linha
        lines[target["line_start"]] = old_line.rstrip()[:-1] + new_parent_ref + "]\n"

    full_path.write_text("".join(lines), encoding="utf-8")
    _run_compile_test(proj)

    return {"status": "success", "new_node_path": f"{scene_path}::{target['name']}"}


def instance_scene_as_child(
    scene_path: str | None = None, parent_node_path: str = ".", instanced_scene_path: str = "", instance_name: str | None = None
) -> dict:
    """Instancia uma cena como filha de um nó (sub-cena / prefab).

    Args:
        scene_path: Cena onde instanciar.
        parent_node_path: Nó pai.
        instanced_scene_path: Cena a instanciar.
        instance_name: Nome da instância (opcional).

    Returns:
        {"status": "success", "node_path": str}
    """
    if scene_path is None:
        scene_path = _resolve_scene_path_from_vibe()
        if scene_path is None:
            return {"status": "error", "message": "scene_path nao informado e Vibe Coding Mode nao esta ativo. Informe scene_path ou ative vibe_coding_mode com uma cena definida."}
    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    instanced_full = proj / instanced_scene_path
    if not instanced_full.exists():
        return {"status": "error", "message": f"Cena a instanciar '{instanced_scene_path}' não encontrada."}

    lines, nodes = _parse_tscn_content(full_path)

    parent_node = _find_node_in_parsed(nodes, parent_node_path)
    if not parent_node:
        return {"status": "error", "message": f"Pai '{parent_node_path}' não encontrado."}

    checkpoint(scene_path, proj)

    # Encontra o próximo ID de recurso
    content_str = "".join(lines)
    existing_ids = re.findall(r'ExtResource\("(\d+)_', content_str)
    next_id = max([int(i) for i in existing_ids] + [0]) + 1
    ext_res_id = f'{next_id}_{Path(instanced_scene_path).stem}'

    name = instance_name or Path(instanced_scene_path).stem

    # Insere ext_resource antes do primeiro nó
    ext_line = f'[ext_resource type="PackedScene" path="res://{instanced_scene_path}" id="{ext_res_id}"]\n'
    first_node_idx = next(i for i, l in enumerate(lines) if l.strip().startswith("[node "))
    lines.insert(first_node_idx, ext_line)

    # Ajusta load_steps
    for i, l in enumerate(lines):
        if l.strip().startswith("[gd_scene"):
            current_steps = re.search(r'load_steps=(\d+)', l)
            if current_steps:
                new_steps = int(current_steps.group(1)) + 1
                lines[i] = re.sub(r'load_steps=\d+', f'load_steps={new_steps}', l)
            break

    # Insere nó instanciado após último filho do pai
    parent_name = parent_node["name"]
    insert_line = parent_node["line_end"]
    for i in range(parent_node["line_start"], len(lines)):
        if lines[i].strip().startswith("[node ") and i > parent_node["line_start"]:
            break
        insert_line = i + 1

    parent_attr = f' parent="{parent_name}"' if parent_name else ""
    instance_line = f'[node name="{name}"{parent_attr} instance=ExtResource("{ext_res_id}")]\n'
    lines.insert(insert_line, instance_line)

    full_path.write_text("".join(lines), encoding="utf-8")

    from tools.runtime_ops import mark_pending_compile
    mark_pending_compile()

    return {"status": "success", "node_path": f"{scene_path}::{name}"}


def connect_signal(
    scene_path: str | None = None, from_node_path: str = "", signal_name: str = "",
    to_node_path: str = "", method_name: str = ""
) -> dict:
    """Conecta um sinal de um nó a um método de outro nó.

    Args:
        scene_path: Cena alvo.
        from_node_path: Nó emissor do sinal.
        signal_name: Nome do sinal.
        to_node_path: Nó receptor.
        method_name: Método no nó receptor.

    Returns:
        {"status": "success"}
    """
    if scene_path is None:
        scene_path = _resolve_scene_path_from_vibe()
        if scene_path is None:
            return {"status": "error", "message": "scene_path nao informado e Vibe Coding Mode nao esta ativo. Informe scene_path ou ative vibe_coding_mode com uma cena definida."}
    proj = _get_active_project()

    violation = _check_path_traversal(scene_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    lines, nodes = _parse_tscn_content(full_path)

    from_node = _find_node_in_parsed(nodes, from_node_path)
    to_node = _find_node_in_parsed(nodes, to_node_path)

    if not from_node:
        return {"status": "error", "message": f"Nó emissor '{from_node_path}' não encontrado."}
    if not to_node:
        return {"status": "error", "message": f"Nó receptor '{to_node_path}' não encontrado."}

    # Valida sinal contra ClassDB se o tipo for conhecido
    if from_node.get("type"):
        valid_signals = [s["name"] for s in list_signals(from_node["type"])]
        if valid_signals and signal_name not in valid_signals:
            # Aviso: pode ser sinal de script
            pass

    checkpoint(scene_path, proj)

    # Constrói bloco de conexão
    from_name = from_node["name"]
    to_name = to_node["name"]
    connection = (
        f'[connection signal="{signal_name}" from="{from_name}" '
        f'to="{to_name}" method="{method_name}"]\n'
    )

    # Insere no final do arquivo
    lines.append(connection)
    full_path.write_text("".join(lines), encoding="utf-8")

    warning = ""
    if from_node.get("type"):
        valid_signals = [s["name"] for s in list_signals(from_node["type"])]
        if valid_signals and signal_name not in valid_signals:
            warning = f"Sinal '{signal_name}' não é nativo de {from_node['type']}. Pode ser de script."

    return {"status": "success", "warning": warning or None}


def list_signals_for_node(scene_path: str | None = None, node_path: str | None = None,
                          node_type: str | None = None) -> dict:
    """Lista sinais disponíveis para um tipo de nó ou nó em cena.

    Args:
        node_type: Tipo de nó (ex: 'Area2D') — lista sinais nativos.
        scene_path + node_path: Nó em cena — inclui sinais de script.

    Returns:
        {"status": "success", "signals": [{"name": str, "args": [...]}]}
    """
    signals = []

    if node_type:
        signals = list_signals(node_type)
    elif scene_path and node_path:
        proj = _get_active_project()
        full_path = proj / scene_path
        if not full_path.exists():
            return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}
        _, nodes = _parse_tscn_content(full_path)
        target = _find_node_in_parsed(nodes, node_path)
        if not target:
            from tools.fuzzy_suggest import not_found_error
            all_paths = _list_node_paths_from_parsed(nodes)
            return not_found_error("nó", node_path, all_paths)
        if target.get("type"):
            signals = list_signals(target["type"])
    else:
        return {"status": "error", "message": "Forneça node_type ou scene_path+node_path."}

    return {"status": "success", "signals": signals}


# ── Fase 4: Tilemap ────────────────────────────────────────────────

def create_tileset(tileset_name: str, save_path: str, tile_width: int = 16, tile_height: int = 16) -> dict:
    """Cria um TileSet (.tres) vazio.

    Args:
        tileset_name: Nome do recurso.
        save_path: Caminho relativo (ex: 'assets/tiles/ground_tiles.tres').
        tile_width: Largura do tile.
        tile_height: Altura do tile.

    Returns:
        {"status": "success", "path": str}
    """
    proj = _get_active_project()

    violation = _check_path_traversal(save_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    full_path = proj / save_path

    if full_path.exists():
        return {"status": "error", "message": f"TileSet '{save_path}' já existe."}

    full_path.parent.mkdir(parents=True, exist_ok=True)

    content = f"""[gd_resource type="TileSet" load_steps=1 format=2]

[resource]
tile_size = Vector2i({tile_width}, {tile_height})
"""
    full_path.write_text(content, encoding="utf-8")

    from tools.runtime_ops import mark_pending_compile
    mark_pending_compile()
    return {"status": "success", "path": save_path}


def create_tilemap_layer(scene_path: str, parent_node_path: str, layer_name: str,
                         tileset_path: str) -> dict:
    """Adiciona uma TileMapLayer a uma cena.

    Args:
        scene_path: Cena alvo.
        parent_node_path: Nó pai.
        layer_name: Nome da camada.
        tileset_path: Caminho do TileSet .tres.

    Returns:
        {"status": "success", "node_path": str}
    """
    if scene_path is None:
        scene_path = _resolve_scene_path_from_vibe()
        if scene_path is None:
            return {"status": "error", "message": "scene_path nao informado e Vibe Coding Mode nao esta ativo. Informe scene_path ou ative vibe_coding_mode com uma cena definida."}
    proj = _get_active_project()

    violation = _check_path_traversal(scene_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    tileset_full = proj / tileset_path
    if not tileset_full.exists():
        return {"status": "error", "message": f"TileSet '{tileset_path}' não encontrado. Use create_tileset primeiro."}

    lines, nodes = _parse_tscn_content(full_path)
    parent_node = _find_node_in_parsed(nodes, parent_node_path)
    if not parent_node:
        return {"status": "error", "message": f"Pai '{parent_node_path}' não encontrado."}

    checkpoint(scene_path, proj)

    # Adiciona ext_resource para o tileset
    content_str = "".join(lines)
    existing_ids = re.findall(r'ExtResource\("(\d+)_', content_str)
    next_id = max([int(i) for i in existing_ids] + [0]) + 1
    ext_res_id = f'{next_id}_tileset'

    ext_line = f'[ext_resource type="TileSet" path="res://{tileset_path}" id="{ext_res_id}"]\n'
    first_node_idx = next(i for i, l in enumerate(lines) if l.strip().startswith("[node "))
    lines.insert(first_node_idx, ext_line)

    # Atualiza load_steps
    for i, l in enumerate(lines):
        if l.strip().startswith("[gd_scene"):
            current_steps = re.search(r'load_steps=(\d+)', l)
            if current_steps:
                lines[i] = re.sub(r'load_steps=\d+', f'load_steps={int(current_steps.group(1))+1}', l)
            break

    # Adiciona nó TileMapLayer
    parent_name = parent_node["name"]
    insert_line = parent_node["line_end"]
    for i in range(parent_node["line_start"], len(lines)):
        if lines[i].strip().startswith("[node ") and i > parent_node["line_start"]:
            break
        insert_line = i + 1

    parent_attr = f' parent="{parent_name}"' if parent_name else ""
    tilemap_line = (
        f'[node name="{layer_name}" type="TileMapLayer"{parent_attr}]\n'
        f'tile_map_data = PackedByteArray()\n'
        f'tile_set = ExtResource("{ext_res_id}")\n'
    )
    lines.insert(insert_line, tilemap_line)

    full_path.write_text("".join(lines), encoding="utf-8")

    from tools.runtime_ops import mark_pending_compile
    mark_pending_compile()

    return {"status": "success", "node_path": f"{scene_path}::{layer_name}"}


def paint_tilemap_cell(scene_path: str | None = None, layer_node_path: str = "",
                       cell_x: int = 0, cell_y: int = 0, source_id: int = 0,
                       atlas_coords_x: int = 0, atlas_coords_y: int = 0) -> dict:
    """Pinta uma célula em uma TileMapLayer no formato PackedByteArray do Godot 4.

    O formato de cada célula no PackedByteArray (12 bytes):
      uint16 x, uint16 y, int32 source_id, uint16 atlas_x, uint16 atlas_y

    Args:
        scene_path: Cena alvo (opcional — resolve via Vibe/ExecutionContext).
        layer_node_path: Path da TileMapLayer.
        cell_x, cell_y: Coordenadas da célula.
        source_id: ID da fonte no tileset.
        atlas_coords_x, atlas_coords_y: Coordenadas no atlas.

    Returns:
        {"status": "success", "cell": [int, int]}
    """
    import struct

    # ── Resolver scene_path (Etapa A2) ──
    if scene_path is None:
        scene_path = _resolve_scene_path_from_vibe()
    if scene_path is None:
        return {"status": "error", "message": "scene_path não informado e nenhum contexto ativo (Vibe/ExecutionContext)."}

    proj = _get_active_project()

    violation = _check_path_traversal(scene_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    lines, nodes = _parse_tscn_content(full_path)
    target = _find_node_in_parsed(nodes, layer_node_path)
    if not target:
        return {"status": "error", "message": f"TileMapLayer '{layer_node_path}' não encontrada. Use create_tilemap_layer primeiro."}

    checkpoint(scene_path, proj)

    # ── Localiza e modifica tile_map_data ───────────────────────
    data_line_idx = -1
    for i in range(target["line_start"], target["line_end"]):
        if "tile_map_data" in lines[i]:
            data_line_idx = i
            break

    # Extrai bytes existentes
    old_bytes = []
    if data_line_idx >= 0:
        match = re.search(r'PackedByteArray\(([^)]*)\)', lines[data_line_idx])
        if match:
            raw = match.group(1)
            if raw.strip():
                old_bytes = [int(x.strip()) for x in raw.split(",") if x.strip()]

    # Cada célula = 12 bytes (uint16 x, uint16 y, int32 source, uint16 ax, uint16 ay)
    CELL_SIZE = 12
    cells = []
    for i in range(0, len(old_bytes), CELL_SIZE):
        if i + CELL_SIZE <= len(old_bytes):
            chunk = bytes(old_bytes[i:i + CELL_SIZE])
            x = struct.unpack('<H', chunk[0:2])[0]
            y = struct.unpack('<H', chunk[2:4])[0]
            sid = struct.unpack('<i', chunk[4:8])[0]
            ax = struct.unpack('<H', chunk[8:10])[0]
            ay = struct.unpack('<H', chunk[10:12])[0]
            cells.append({"x": x, "y": y, "source_id": sid, "atlas_x": ax, "atlas_y": ay})

    # Atualiza ou adiciona célula
    found = False
    for c in cells:
        if c["x"] == cell_x and c["y"] == cell_y:
            c["source_id"] = source_id
            c["atlas_x"] = atlas_coords_x
            c["atlas_y"] = atlas_coords_y
            found = True
            break
    if not found:
        cells.append({"x": cell_x, "y": cell_y, "source_id": source_id,
                       "atlas_x": atlas_coords_x, "atlas_y": atlas_coords_y})

    # Reconstrói PackedByteArray
    new_bytes = []
    for c in cells:
        new_bytes.extend(struct.pack('<HHiHH',
                          c["x"], c["y"], c["source_id"],
                          c["atlas_x"], c["atlas_y"]))

    byte_str = ", ".join(str(b) for b in new_bytes)
    new_data_line = f'tile_map_data = PackedByteArray({byte_str})\n'

    if data_line_idx >= 0:
        lines[data_line_idx] = new_data_line
    else:
        # Insere após a última propriedade do nó
        insert_at = target["line_end"]
        lines.insert(insert_at, new_data_line)

    full_path.write_text("".join(lines), encoding="utf-8")

    return {"status": "success", "cell": [cell_x, cell_y],
            "total_cells": len(cells)}


# ── Fase 4: Animação ───────────────────────────────────────────────

def create_animation(scene_path: str, anim_player_path: str,
                     anim_name: str, track_path: str, track_type: str,
                     keyframes: list[dict], fps: float = 10.0) -> dict:
    """Adiciona uma animação a um AnimationPlayer.

    Args:
        scene_path: Cena alvo.
        anim_player_path: Path do AnimationPlayer.
        anim_name: Nome da animação (ex: 'idle', 'walk').
        track_path: Path da propriedade a animar (ex: './Sprite:frame').
        track_type: Tipo da track ('value' para propriedades, 'method' para chamadas).
        keyframes: Lista de {"time": float, "value": str}.
        fps: Frames por segundo.

    Returns:
        {"status": "success", "animation": str}
    """
    if scene_path is None:
        scene_path = _resolve_scene_path_from_vibe()
        if scene_path is None:
            return {"status": "error", "message": "scene_path nao informado e Vibe Coding Mode nao esta ativo. Informe scene_path ou ative vibe_coding_mode com uma cena definida."}
    proj = _get_active_project()

    violation = _check_path_traversal(scene_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    lines, nodes = _parse_tscn_content(full_path)
    target = _find_node_in_parsed(nodes, anim_player_path)
    if not target:
        return {"status": "error", "message": f"AnimationPlayer '{anim_player_path}' não encontrado. Use create_animation_player primeiro."}

    checkpoint(scene_path, proj)

    # Constrói biblioteca de animação como SubResource
    content_str = "".join(lines)
    existing_subs = re.findall(r'SubResource\("(\d+)"\)', content_str)
    next_sub = max([int(i) for i in existing_subs] + [0]) + 1

    # AnimationLibrary
    lib_id = next_sub
    next_sub += 1
    anim_id = next_sub

    # Constrói SubResources
    sub_block = f"""[sub_resource type="AnimationLibrary" id="{lib_id}"]
"""
    sub_block += f'_data = {{"{anim_name}": SubResource("{anim_id}")}}\n'

    # Animation
    length = max((kf.get("time", 0) for kf in keyframes), default=1.0) + 0.1
    sub_block += f'\n[sub_resource type="Animation" id="{anim_id}"]\n'
    sub_block += f'resource_name = "{anim_name}"\n'
    sub_block += f'length = {length}\n'
    sub_block += f'loop_mode = 1\n'
    sub_block += f'step = {1.0/fps}\n'
    sub_block += f'tracks = [{{\n'
    sub_block += f'"type": "{track_type}",\n'
    sub_block += f'"path": NodePath("{track_path}"),\n'
    sub_block += f'"interp": 1,\n'
    sub_block += f'"loop_wrap": true,\n'
    sub_block += f'"keys": {{\n'
    for kf in keyframes:
        sub_block += f'"times": PackedFloat32Array({kf["time"]}),\n'
        sub_block += f'"transitions": PackedFloat32Array(1),\n'
        sub_block += f'"values": [{kf["value"]}],\n'
    sub_block += '}\n}]\n'

    # Insere SubResources antes do primeiro nó
    first_node = next(i for i, l in enumerate(lines) if l.strip().startswith("[node "))
    # Insere em ordem reversa
    for block_line in reversed(sub_block.splitlines(True)):
        lines.insert(first_node, block_line)

    # Atualiza load_steps
    for i, l in enumerate(lines):
        if l.strip().startswith("[gd_scene"):
            current_steps = re.search(r'load_steps=(\d+)', l)
            if current_steps:
                lines[i] = re.sub(r'load_steps=\d+', f'load_steps={int(current_steps.group(1))+2}', l)
            break

    # Atualiza referência no AnimationPlayer
    for i in range(target["line_start"], target["line_end"]):
        if "libraries" in lines[i]:
            lines[i] = f'libraries = SubResource("{lib_id}")\n'
            break
    else:
        insert_at = target["line_start"] + 1
        lines.insert(insert_at, f'libraries = SubResource("{lib_id}")\n')

    full_path.write_text("".join(lines), encoding="utf-8")

    from tools.runtime_ops import mark_pending_compile
    mark_pending_compile()

    return {"status": "success", "animation": anim_name}


def create_animation_player(scene_path: str, parent_node_path: str,
                            player_name: str = "AnimationPlayer") -> dict:
    """Adiciona um nó AnimationPlayer a uma cena.

    Args:
        scene_path: Cena alvo.
        parent_node_path: Nó pai.
        player_name: Nome do nó.

    Returns:
        {"status": "success", "node_path": str}
    """
    return add_node(scene_path, parent_node_path, player_name, "AnimationPlayer")


# ── Fase 4: UI ─────────────────────────────────────────────────────

def create_ui_scene(name: str, path: str) -> dict:
    """Cria uma cena de UI com CanvasLayer + Control como raiz.

    Args:
        name: Nome do nó raiz.
        path: Caminho relativo (ex: 'scenes/ui_main.tscn').

    Returns:
        {"status": "success", "path": str}
    """
    proj = _get_active_project()
    full_path = proj / path

    if full_path.exists():
        return {"status": "error", "message": f"Cena '{path}' já existe."}

    full_path.parent.mkdir(parents=True, exist_ok=True)

    # Cria cena com CanvasLayer → Control
    content = f"""[gd_scene load_steps=2 format=2]

[node name="{name}" type="CanvasLayer"]

[node name="UIContainer" type="Control" parent="."]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
"""
    full_path.write_text(content, encoding="utf-8")

    from tools.runtime_ops import mark_pending_compile
    mark_pending_compile()

    return {"status": "success", "path": path}


def add_control_node(scene_path: str, parent_node_path: str,
                     node_name: str, node_type: str,
                     properties: dict | None = None) -> dict:
    """Adiciona um nó de UI (Label, Button, etc.) a uma cena.

    Args:
        scene_path: Cena alvo.
        parent_node_path: Nó pai.
        node_name: Nome do nó.
        node_type: Tipo (Label, Button, Panel, HBoxContainer, etc.).
        properties: Propriedades adicionais (opcional).

    Returns:
        {"status": "success", "node_path": str}
    """
    result = add_node(scene_path, parent_node_path, node_name, node_type)
    if result["status"] != "success":
        return result

    if properties:
        for key, value in properties.items():
            set_node_property(scene_path, f"./{node_name}", key, value)

    return {"status": "success", "node_path": f"{scene_path}::{node_name}"}


# ── Onda 1: Visão — Análise de cena ─────────────────────────────────

def detect_offscreen_elements(
    scene_path: str | None = None,
    viewport_width: int = 1280,
    viewport_height: int = 720,
    margin: int = 50,
) -> dict:
    """Detecta nós que estão fora da área visível da viewport.

    Analisa o .tscn e verifica a posição de cada nó. Nós com position
    fora dos limites [0-margin, viewport_width+margin] × [0-margin,
    viewport_height+margin] são reportados.

    Útil para diagnosticar: "por que o inimigo não aparece?", "onde
    está o player spawnando?"

    Args:
        scene_path: Caminho da cena a analisar (opcional — resolve via Vibe/ExecutionContext).
        viewport_width: Largura da viewport (default 1280).
        viewport_height: Altura da viewport (default 720).
        margin: Margem de tolerância em pixels (default 50).

    Returns:
        dict com elementos fora da tela.
    """
    # ── Resolver scene_path (Etapa A2) ──
    if scene_path is None:
        scene_path = _resolve_scene_path_from_vibe()
    if scene_path is None:
        return {"status": "error", "message": "scene_path não informado e nenhum contexto ativo (Vibe/ExecutionContext)."}

    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    lines, nodes = _parse_tscn_content(full_path)

    offscreen = []
    total_with_position = 0

    for node in nodes:
        props = node.get("properties", {})

        # Procura position no formato Godot: position = Vector2(x, y)
        pos_str = props.get("position")
        if not pos_str:
            continue

        # Parse Vector2(x, y) ou (x, y)
        match = re.match(
            r'Vector2[234]?\s*\(\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\)',
            str(pos_str)
        )
        if not match:
            # Tenta (x, y) simples
            match = re.match(
                r'\(\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\)',
                str(pos_str)
            )
        if not match:
            continue

        x = float(match.group(1))
        y = float(match.group(2))
        total_with_position += 1

        is_offscreen = False
        reason = ""

        if x < -margin:
            is_offscreen = True
            reason = f"X={x} está {abs(x + margin):.0f}px à esquerda da viewport (limite: -{margin})"
        elif x > viewport_width + margin:
            is_offscreen = True
            reason = f"X={x} está {x - viewport_width - margin:.0f}px à direita da viewport (limite: {viewport_width + margin})"
        elif y < -margin:
            is_offscreen = True
            reason = f"Y={y} está {abs(y + margin):.0f}px acima da viewport (limite: -{margin})"
        elif y > viewport_height + margin:
            is_offscreen = True
            reason = f"Y={y} está {y - viewport_height - margin:.0f}px abaixo da viewport (limite: {viewport_height + margin})"

        if is_offscreen:
            offscreen.append({
                "node_name": node.get("name", "?"),
                "node_type": node.get("type", "?"),
                "position": [x, y],
                "reason": reason,
            })

    return {
        "status": "success",
        "offscreen": offscreen,
        "total_nodes_with_position": total_with_position,
        "viewport": [viewport_width, viewport_height],
        "note": f"{len(offscreen)} de {total_with_position} nós com position estão fora da viewport." if offscreen
                else "Todos os nós com position estão dentro da viewport.",
    }

