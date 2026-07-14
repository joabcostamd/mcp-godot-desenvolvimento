"""audit_input_map.py — Auditoria de Input Map (Bloco 1.1).

Detecta:
  (a) Ações declaradas no [input] do project.godot mas nunca referenciadas
      em código GDScript (Input.is_action_* / get_axis / get_vector).
  (b) Chamadas a Input.is_action_* no código que referenciam uma ação
      NÃO declarada no Input Map (erro silencioso comum).

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


def _parse_input_actions(project_godot_text: str) -> list[str]:
    """Extrai a lista de ações declaradas na seção [input] do project.godot.

    Exclui ações nativas do engine que começam com 'ui_'.
    """
    actions = []
    in_input_section = False
    for line in project_godot_text.splitlines():
        stripped = line.strip()
        if stripped == "[input]":
            in_input_section = True
            continue
        if in_input_section:
            # Sai da seção ao encontrar próxima seção
            if stripped.startswith("[") and stripped.endswith("]"):
                break
            # Linhas de ação: nome_da_acao={...}
            m = re.match(r'^(\S+)\s*=\s*\{', stripped)
            if m:
                action_name = m.group(1)
                # Excluir ações nativas do engine (ui_*)
                if not action_name.startswith("ui_"):
                    actions.append(action_name)
    return actions


# Padrões de leitura de input em GDScript
_INPUT_USAGE_PATTERNS = [
    # is_action_pressed("acao")
    re.compile(r'Input\.is_action_pressed\s*\(\s*["\']([^"\']+)["\']'),
    # is_action_just_pressed("acao")
    re.compile(r'Input\.is_action_just_pressed\s*\(\s*["\']([^"\']+)["\']'),
    # is_action_just_released("acao")
    re.compile(r'Input\.is_action_just_released\s*\(\s*["\']([^"\']+)["\']'),
    # is_action("acao") — is_action sem sufixo (menos comum, mas válido)
    re.compile(r'Input\.is_action\s*\(\s*["\']([^"\']+)["\']'),
    # get_axis("neg", "pos")
    re.compile(r'Input\.get_axis\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']'),
    # get_vector("neg_x", "pos_x", "neg_y", "pos_y")
    re.compile(r'Input\.get_vector\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']'),
]


def _scan_input_usages(proj: Path) -> tuple[set[str], list[dict]]:
    """Varre todos os .gd do projeto e retorna:
    - set de ações usadas
    - lista de ações usadas mas NÃO encontradas no input map (preenchida depois)
    Retorna (used_actions, all_references).
    """
    used_actions: set[str] = set()
    all_references: list[dict] = []

    for gd_file in proj.rglob("*.gd"):
        if _should_skip(gd_file):
            continue
        try:
            content = gd_file.read_text(encoding="utf-8")
        except Exception:
            continue

        rel_path = str(gd_file.relative_to(proj)).replace("\\", "/")

        for pattern in _INPUT_USAGE_PATTERNS:
            for match in pattern.finditer(content):
                # Extrai todos os grupos capturados (nomes de ação)
                groups = match.groups()
                for action_name in groups:
                    if action_name and not action_name.startswith("ui_"):
                        used_actions.add(action_name)
                        # Calcula número da linha
                        line_num = content[:match.start()].count("\n") + 1
                        all_references.append({
                            "action": action_name,
                            "file": f"res://{rel_path}",
                            "line": line_num,
                        })

    return used_actions, all_references


# ── Função principal ─────────────────────────────────────────────────

def audit_input_map(project_path: str | None = None) -> dict:
    """Audita o Input Map do projeto: ações não usadas e ações referenciadas mas não declaradas.

    Args:
        project_path: Caminho do projeto (opcional, usa projeto ativo).

    Returns:
        {"status": "ok"|"issues_found", "declared_actions": [...],
         "unused_actions": [...], "undeclared_actions_referenced": [...],
         "summary": "..."}
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

    try:
        pg_text = pg_path.read_text(encoding="utf-8")
    except Exception as e:
        return {"status": "error", "message": f"Erro ao ler project.godot: {e}"}

    # ── Parse das ações declaradas ──
    declared_actions = _parse_input_actions(pg_text)

    # Se não houver seção [input], retorna ok com lista vazia
    if "[input]" not in pg_text:
        return {
            "status": "ok",
            "declared_actions": [],
            "unused_actions": [],
            "undeclared_actions_referenced": [],
            "summary": "Nenhuma ação declarada no Input Map (seção [input] não encontrada).",
            "note": (
                "Esta ferramenta audita apenas ações nomeadas do Input Map "
                "(Input.is_action_*). NÃO detecta uso de tecla direta sem Input Map "
                "(Input.is_key_pressed, Input.is_physical_key_pressed). "
                "Se o projeto usa esse padrão, esta auditoria não tem visibilidade sobre ele."
            ),
        }

    # ── Scan de usos no código ──
    used_actions, all_references = _scan_input_usages(proj)

    # ── Cruzamento ──
    unused_actions = sorted(set(declared_actions) - used_actions)
    undeclared = [ref for ref in all_references if ref["action"] not in set(declared_actions)]

    # Deduplicar undeclared (mesma ação referenciada em múltiplos arquivos)
    seen = set()
    undeclared_deduped = []
    for ref in undeclared:
        key = (ref["action"], ref["file"], ref["line"])
        if key not in seen:
            seen.add(key)
            undeclared_deduped.append(ref)

    issues_found = len(unused_actions) > 0 or len(undeclared_deduped) > 0

    summary_parts = [f"{len(declared_actions)} ações declaradas"]
    if unused_actions:
        summary_parts.append(f"{len(unused_actions)} nunca usadas")
    if undeclared_deduped:
        summary_parts.append(f"{len(undeclared_deduped)} referenciadas sem existir no Input Map")
    if not issues_found:
        summary_parts.append("nenhum problema encontrado")

    return {
        "status": "issues_found" if issues_found else "ok",
        "declared_actions": sorted(declared_actions),
        "unused_actions": unused_actions,
        "undeclared_actions_referenced": undeclared_deduped,
        "summary": ", ".join(summary_parts) + ".",
        "note": (
            "Esta ferramenta audita apenas ações nomeadas do Input Map "
            "(Input.is_action_*). NÃO detecta uso de tecla direta sem Input Map "
            "(Input.is_key_pressed, Input.is_physical_key_pressed). "
            "Se o projeto usa esse padrão, esta auditoria não tem visibilidade sobre ele."
        ),
    }
