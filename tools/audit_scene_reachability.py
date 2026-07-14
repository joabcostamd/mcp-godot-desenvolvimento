"""audit_scene_reachability.py — Alcançabilidade de Cena (Bloco 1.3).

Partindo da cena raiz (run/main_scene do project.godot), constrói o grafo de
alcançabilidade e lista toda cena .tscn do projeto que NUNCA aparece nesse grafo
— ou seja, existe no projeto mas não há caminho de código/cena até ela a partir
do ponto de entrada do jogo.

Diferente de find_unused_resources: esta ferramenta cobre APENAS cenas .tscn.
find_unused_resources cobre assets (png/wav/glb/ttf). Não há sobreposição.

Ferramenta SOMENTE LEITURA — não modifica nenhum arquivo.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── Helpers ──────────────────────────────────────────────────────────

def _resolve_project(project_path: str | None) -> Path | None:
    """Resolve o caminho do projeto: explícito ou via active project."""
    if project_path:
        return Path(project_path)
    try:
        from tools.project_ops import _get_active_project
        return _get_active_project()
    except Exception:
        return None


def _should_skip(path: Path) -> bool:
    """Verifica se um path deve ser pulado (addons, .godot, etc.)."""
    skip_dirs = {".godot", ".mcp_backups", "addons", ".git", "__pycache__"}
    return any(skip in path.parts for skip in skip_dirs)


def _get_main_scene(proj: Path) -> str | None:
    """Lê run/main_scene do project.godot."""
    pg = proj / "project.godot"
    if not pg.exists():
        return None
    try:
        content = pg.read_text(encoding="utf-8")
    except Exception:
        return None
    m = re.search(r'run/main_scene\s*=\s*"([^"]*)"', content)
    return m.group(1) if m else None


def _parse_tscn_ext_resources(content: str) -> dict[str, str]:
    """Extrai mapeamento id -> path dos [ext_resource] em um .tscn.

    Retorna dict {id: path} apenas para recursos do tipo PackedScene.
    """
    resources = {}
    # [ext_resource type="PackedScene" id="1_abc" path="res://scenes/foo.tscn"]
    pattern = re.compile(
        r'\[ext_resource\s+type="PackedScene"[^\]]*?\bid\s*=\s*"([^"]+)"[^\]]*?path\s*=\s*"([^"]+)"',
        re.DOTALL,
    )
    for match in pattern.finditer(content):
        resources[match.group(1)] = match.group(2)

    # Também captura quando os atributos estão em ordem trocada
    pattern2 = re.compile(
        r'\[ext_resource\s+path\s*=\s*"([^"]+)"[^\]]*?type\s*=\s*"PackedScene"[^\]]*?\bid\s*=\s*"([^"]+)"',
        re.DOTALL,
    )
    for match in pattern2.finditer(content):
        resources[match.group(2)] = match.group(1)

    return resources


def _parse_tscn_scene_instances(content: str) -> list[str]:
    """Extrai cenas filhas instanciadas dentro do .tscn via ExtResource.

    Formato: [node ... instance=ExtResource("id")] onde o ext_resource é PackedScene.
    Retorna lista de paths de cena.
    """
    instances = []
    # Captura todas as instâncias de ExtResource
    pattern = re.compile(r'instance\s*=\s*ExtResource\s*\(\s*"([^"]+)"\s*\)')
    for match in pattern.finditer(content):
        instances.append(match.group(1))
    return instances


def _extract_scene_refs_from_gd(content: str, file_rel: str = "") -> tuple[list[str], list[dict]]:
    """Extrai referências a cenas .tscn em código GDScript.

    Detecta:
      - preload("res://...tscn") / load("res://...tscn")
      - get_tree().change_scene_to_file("res://...tscn")
      - change_scene_to_file("res://...tscn")
      - SceneTree.change_scene_to_file (qualificador completo)
      - get_tree().change_scene_to_packed(<var>) — se <var> vier de
        preload/load de .tscn identificável estaticamente na mesma função

    Retorna (resolved_refs, unresolved_refs) onde:
      - resolved_refs: lista de paths "res://..." resolvidos estaticamente
      - unresolved_refs: lista de {"file": ..., "line": ..., "raw_expression": ...}
    """
    resolved: list[str] = []
    unresolved: list[dict] = []

    def _line_of(pos: int) -> int:
        return content[:pos].count("\n") + 1

    # ── Padrão 1: preload/load com string literal ──
    for m in re.finditer(r'(?:preload|load)\s*\(\s*"([^"]+\.tscn)"', content):
        resolved.append(m.group(1))

    # ── Padrão 2: change_scene_to_file com string literal ──
    # get_tree().change_scene_to_file("res://...")
    # change_scene_to_file("res://...")
    # SceneTree.change_scene_to_file (estático, mesmo padrão)
    for m in re.finditer(r'(?:get_tree\s*\(\s*\)|SceneTree)\s*\.\s*change_scene_to_file\s*\(\s*"([^"]+\.tscn)"', content):
        resolved.append(m.group(1))

    # change_scene_to_file("res://...") sem prefixo get_tree()
    for m in re.finditer(r'(?<!\.)\bchange_scene_to_file\s*\(\s*"([^"]+\.tscn)"', content):
        resolved.append(m.group(1))

    # ── Padrão 3: change_scene_to_file com string montada (dinâmica) ──
    # get_tree().change_scene_to_file(var)
    # get_tree().change_scene_to_file("res://" + var + ".tscn")
    # NOTA: o regex usa [^)]* para capturar só até o fecha-parênteses
    dyn_patterns = [
        re.compile(r'(?:get_tree\s*\(\s*\)|SceneTree)\s*\.\s*change_scene_to_file\s*\(\s*([^)]*)\)'),
        re.compile(r'(?<!\.)\bchange_scene_to_file\s*\(\s*([^)]*)\)'),
    ]
    for pat in dyn_patterns:
        for m in pat.finditer(content):
            expr = m.group(1).strip()
            # Se for string literal "res://...tscn" → já foi capturado acima, pular
            if re.match(r'^"[^"]*\.tscn"$', expr):
                continue
            # Se é só uma variável simples sem concatenação → dinâmico
            if re.match(r'^[a-zA-Z_]\w*$', expr):
                unresolved.append({
                    "file": f"res://{file_rel}" if file_rel else "(inline)",
                    "line": _line_of(m.start()),
                    "raw_expression": f"change_scene_to_file({expr})",
                })
            # Se contém concatenação com + → dinâmico
            elif "+" in expr:
                unresolved.append({
                    "file": f"res://{file_rel}" if file_rel else "(inline)",
                    "line": _line_of(m.start()),
                    "raw_expression": f"change_scene_to_file({expr})",
                })

    # ── Padrão 4: change_scene_to_packed ──
    # get_tree().change_scene_to_packed(preloaded_scene)
    # Tenta resolver se a variável vem de preload/load na mesma função
    for m in re.finditer(
        r'(?:get_tree\s*\(\s*\)|SceneTree)\s*\.\s*change_scene_to_packed\s*\(\s*(\w+)\s*\)',
        content,
    ):
        var_name = m.group(1)
        line = _line_of(m.start())
        # Buscar definição da variável na mesma função (preload/load)
        var_def = re.search(
            rf'(?:var|const)\s+{re.escape(var_name)}\s*[:=]\s*(?:preload|load)\s*\(\s*"([^"]+\.tscn)"',
            content,
        )
        if var_def:
            resolved.append(var_def.group(1))
        else:
            unresolved.append({
                "file": f"res://{file_rel}" if file_rel else "(inline)",
                "line": line,
                "raw_expression": f"change_scene_to_packed({var_name})",
            })

    # ── Deduplicar mantendo ordem ──
    seen = set()
    resolved_dedup = []
    for r in resolved:
        if r not in seen:
            seen.add(r)
            resolved_dedup.append(r)

    return resolved_dedup, unresolved


def _global_prescan_change_scene(proj: Path) -> dict[str, list[str]]:
    """Pré-escaneia TODOS os .gd do projeto em busca de change_scene_to_file.

    Retorna dict mapeando script_rel_path -> lista de cenas alvo (paths relativos).
    Isso cobre casos onde o script NÃO está anexado a um nó de cena visitada
    (ex: autoloads, scripts utilitários).
    """
    scene_refs: dict[str, list[str]] = {}

    for gd_file in proj.rglob("*.gd"):
        if _should_skip(gd_file):
            continue
        try:
            content = gd_file.read_text(encoding="utf-8")
        except Exception:
            continue

        rel = str(gd_file.relative_to(proj)).replace("\\", "/")
        resolved, _ = _extract_scene_refs_from_gd(content, rel)

        if resolved:
            scene_refs[rel] = resolved

    return scene_refs


def _resolve_res_path(res_path: str, proj: Path) -> str | None:
    """Converte res://path para path relativo ao projeto. Retorna None se inválido."""
    if res_path.startswith("res://"):
        return res_path[6:]  # remove "res://"
    return res_path


def _scene_to_rel_path(scene_abs: Path, proj: Path) -> str | None:
    """Converte path absoluto de cena para path relativo estilo res://."""
    try:
        rel = str(scene_abs.relative_to(proj)).replace("\\", "/")
        return rel
    except ValueError:
        return None


# ── Função principal ─────────────────────────────────────────────────

def audit_scene_reachability(project_path: str | None = None, root_scene: str | None = None) -> dict:
    """Audita a alcançabilidade de cenas a partir da cena raiz.

    Constrói o grafo de cenas alcançáveis via BFS a partir da cena raiz e lista
    todas as cenas .tscn do projeto que NÃO são alcançáveis.

    Args:
        project_path: Caminho do projeto (opcional, usa projeto ativo).
        root_scene: Cena raiz (opcional, usa run/main_scene do project.godot).

    Returns:
        {"status": "ok"|"issues_found"|"ambiguous", "root_scene": "...",
         "total_scenes_in_project": N, "reachable_scenes": N,
         "unreachable_scenes": [...], "summary": "..."}
    """
    # ── Resolver projeto ──
    proj = _resolve_project(project_path)
    if proj is None:
        return {"status": "error", "message": "Projeto não encontrado. Configure com set_active_project."}
    if not proj.exists():
        return {"status": "error", "message": f"Projeto não encontrado: {proj}"}

    pg_path = proj / "project.godot"
    if not pg_path.exists():
        return {"status": "error", "message": f"project.godot não encontrado em: {proj}"}

    # ── Resolver cena raiz ──
    if root_scene is None:
        root_scene = _get_main_scene(proj)

    if root_scene is None:
        return {
            "status": "ambiguous",
            "root_scene": None,
            "total_scenes_in_project": 0,
            "reachable_scenes": 0,
            "unreachable_scenes": [],
            "summary": (
                "Cena raiz não definida. Defina run/main_scene no project.godot "
                "ou passe o parâmetro root_scene explicitamente."
            ),
        }

    # ── Normalizar root_scene para path relativo (sem res://) ──
    root_rel = _resolve_res_path(root_scene, proj)
    if root_rel is None:
        return {"status": "error", "message": f"Cena raiz inválida: {root_scene}"}

    root_abs = proj / root_rel
    if not root_abs.exists():
        return {
            "status": "error",
            "message": f"Cena raiz não encontrada no disco: {root_rel}",
        }

    # ── Coletar todas as cenas .tscn do projeto ──
    all_scenes: dict[str, Path] = {}  # rel_path -> Path absoluto
    for tscn_file in proj.rglob("*.tscn"):
        if _should_skip(tscn_file):
            continue
        rel = _scene_to_rel_path(tscn_file, proj)
        if rel:
            all_scenes[rel] = tscn_file

    total_scenes = len(all_scenes)

    # ── Pré-scan global: change_scene_to_file em TODOS os .gd ──
    global_change_refs = _global_prescan_change_scene(proj)
    dynamic_unresolved: list[dict] = []

    # ── BFS a partir da cena raiz ──
    visited: set[str] = set()  # paths relativos de cenas visitadas
    queue: list[str] = [root_rel]

    # Cache: conteúdo de .tscn já lido (evita reler)
    tscn_cache: dict[str, str] = {}

    # Cache: scripts anexados a nós de cada cena (para buscar load/preload/change_scene)
    # Mapeamento: cena_rel -> set de scripts associados
    scene_scripts: dict[str, set[str]] = {}

    # Coletor de unresolved dinâmicos (para não duplicar)
    unresolved_keys: set[tuple] = set()

    while queue:
        current_rel = queue.pop(0)
        if current_rel in visited:
            continue
        visited.add(current_rel)

        current_abs = proj / current_rel
        if not current_abs.exists():
            continue

        # ── 0. Verificar pré-scan global: mudança de cena a partir DE qualquer script ──
        # Se algum script referencia esta cena via change_scene_to_file,
        # as cenas que ELE referencia também são alcançáveis
        # (já são cobertas pelo pré-scan abaixo, mas garantimos aqui também)

        # Ler conteúdo da cena
        if current_rel not in tscn_cache:
            try:
                tscn_cache[current_rel] = current_abs.read_text(encoding="utf-8")
            except Exception:
                continue
        content = tscn_cache[current_rel]

        # 1. Extrair cenas filhas instanciadas via ExtResource (PackedScene)
        ext_resources = _parse_tscn_ext_resources(content)
        scene_instance_ids = _parse_tscn_scene_instances(content)

        for ext_id in scene_instance_ids:
            if ext_id in ext_resources:
                child_path = ext_resources[ext_id]
                child_rel = _resolve_res_path(child_path, proj)
                if child_rel and child_rel not in visited:
                    queue.append(child_rel)

        # 2. Extrair scripts anexados a nós desta cena
        if current_rel not in scene_scripts:
            scene_scripts[current_rel] = set()

        # Scripts via ext_resource type="Script"
        script_resources = re.findall(
            r'\[ext_resource\s+type="Script"[^\]]*?path\s*=\s*"([^"]+)"',
            content,
        )
        for script_path in script_resources:
            script_rel = _resolve_res_path(script_path, proj)
            if script_rel:
                scene_scripts[current_rel].add(script_rel)

        # Scripts inline: script = ExtResource("id") nos nodes
        node_scripts = re.findall(
            r'script\s*=\s*ExtResource\s*\(\s*"([^"]+)"\s*\)',
            content,
        )
        for ext_id in node_scripts:
            m = re.search(
                rf'\[ext_resource\s+id\s*=\s*"{re.escape(ext_id)}"[^\]]*?path\s*=\s*"([^"]+)"',
                content,
            )
            if m:
                script_rel = _resolve_res_path(m.group(1), proj)
                if script_rel:
                    scene_scripts[current_rel].add(script_rel)

        # 3. Ler scripts e extrair referências a cenas (load/preload/change_scene)
        for script_rel in scene_scripts.get(current_rel, set()):
            script_abs = proj / script_rel
            if not script_abs.exists():
                continue
            try:
                gd_content = script_abs.read_text(encoding="utf-8")
            except Exception:
                continue
            resolved, unresolved = _extract_scene_refs_from_gd(gd_content, script_rel)
            for ref in resolved:
                child_rel = _resolve_res_path(ref, proj)
                if child_rel and child_rel not in visited:
                    queue.append(child_rel)
            for u in unresolved:
                key = (u["file"], u["line"], u["raw_expression"])
                if key not in unresolved_keys:
                    unresolved_keys.add(key)
                    dynamic_unresolved.append(u)

        # 4. Também puxar refs do pré-scan global para scripts desta cena
        for script_rel in scene_scripts.get(current_rel, set()):
            if script_rel in global_change_refs:
                for ref in global_change_refs[script_rel]:
                    child_rel = _resolve_res_path(ref, proj)
                    if child_rel and child_rel not in visited:
                        queue.append(child_rel)

    # ── Segunda passada: aplicar pré-scan global para TODOS os scripts ──
    # Scripts que não estão anexados a nenhuma cena visitada mas que contêm
    # change_scene_to_file para cenas já visitadas — as cenas que ELES referenciam
    # também são alcançáveis (ex: autoload que faz change_scene_to_file para game.tscn)
    for script_rel, refs in global_change_refs.items():
        for ref in refs:
            child_rel = _resolve_res_path(ref, proj)
            if child_rel and child_rel not in visited:
                # Verificar se este script é referenciado por alguma cena visitada
                # ou se a cena alvo é referenciada a partir de uma cena visitada
                # (já coberto pelo passo 4 acima)
                # Aqui cobrimos o caso: autoload/script global referencia cena
                # que por sua vez referencia outras cenas
                visited.add(child_rel)  # marca como alcançável
                # Não fazemos BFS a partir dela (scripts podem não estar anexados)
                # Mas marcamos como alcançável

    # ── Cenas não visitadas = órfãs ──
    unreachable = sorted(set(all_scenes.keys()) - visited)

    issues_found = len(unreachable) > 0

    return {
        "status": "issues_found" if issues_found else "ok",
        "root_scene": f"res://{root_rel}",
        "total_scenes_in_project": total_scenes,
        "reachable_scenes": len(visited),
        "unreachable_scenes": [f"res://{s}" for s in unreachable],
        "dynamic_scene_refs_unresolved": dynamic_unresolved,
        "summary": (
            f"{total_scenes} cenas no projeto, "
            f"{len(visited)} alcançáveis a partir da raiz, "
            f"{len(unreachable)} órfãs."
            + (f" {len(dynamic_unresolved)} referências dinâmicas não resolvidas."
               if dynamic_unresolved else "")
        ),
    }
