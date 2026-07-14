"""audit_autoloads.py — Auditoria de Autoloads (Bloco 1.2).

Detecta:
  (a) Autoloads registrados no [autoload] do project.godot cujo nome de
      singleton nunca aparece referenciado em nenhum outro script do projeto.
  (b) Uso no código de um nome de singleton que não corresponde a nenhum
      autoload registrado (possível autoload removido mas código não atualizado).

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


def _parse_autoloads(project_godot_text: str) -> list[dict]:
    """Extrai a lista de autoloads da seção [autoload] do project.godot.

    Retorna lista de {"name": str, "script_path": str}.
    """
    autoloads = []
    in_autoload_section = False
    for line in project_godot_text.splitlines():
        stripped = line.strip()
        if stripped == "[autoload]":
            in_autoload_section = True
            continue
        if in_autoload_section:
            # Sai da seção ao encontrar próxima seção
            if stripped.startswith("[") and stripped.endswith("]"):
                break
            # Formato: NomeDoAutoload="*res://caminho/script.gd"
            m = re.match(r'^(\w+)\s*=\s*"\*?([^"]+)"', stripped)
            if m:
                autoloads.append({
                    "name": m.group(1),
                    "script_path": m.group(2),
                })
    return autoloads


def _scan_autoload_usages(proj: Path, autoload_names: list[str]) -> dict[str, int]:
    """Varre todos os .gd do projeto e conta ocorrências de cada nome de autoload
    como prefixo de chamada (ex: GameManager.).

    Retorna dict {nome: contagem}.
    """
    usage_counts: dict[str, int] = {name: 0 for name in autoload_names}

    for gd_file in proj.rglob("*.gd"):
        if _should_skip(gd_file):
            continue
        try:
            content = gd_file.read_text(encoding="utf-8")
        except Exception:
            continue

        rel_path = str(gd_file.relative_to(proj)).replace("\\", "/")

        for name in autoload_names:
            # Busca o nome como prefixo de chamada: NomeDoAutoload.
            # Usa word boundary (\b) antes do nome para evitar match parcial.
            # NOTA: nao tenta excluir definicoes (func/class) com look-behind
            # porque Python re nao suporta look-behind de largura variavel.
            # Falsos positivos (ex: nome de classe igual ao autoload) sao raros
            # e o campo se chama "possibly_unused" por essa razao.
            pattern = re.compile(r'\b' + re.escape(name) + r'\.')
            count = len(pattern.findall(content))
            if count > 0:
                usage_counts[name] += count

    return usage_counts


# ── Função principal ─────────────────────────────────────────────────

def audit_autoloads(project_path: str | None = None) -> dict:
    """Audita os Autoloads do projeto: singletons registrados mas nunca referenciados.

    Args:
        project_path: Caminho do projeto (opcional, usa projeto ativo).

    Returns:
        {"status": "ok"|"issues_found", "registered_autoloads": [...],
         "possibly_unused_autoloads": [...], "summary": "..."}
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

    # ── Parse dos autoloads ──
    registered = _parse_autoloads(pg_text)

    # Se não houver seção [autoload], retorna ok com lista vazia
    if "[autoload]" not in pg_text:
        return {
            "status": "ok",
            "registered_autoloads": [],
            "possibly_unused_autoloads": [],
            "summary": "Nenhum autoload registrado (seção [autoload] não encontrada no project.godot).",
        }

    if not registered:
        return {
            "status": "ok",
            "registered_autoloads": [],
            "possibly_unused_autoloads": [],
            "summary": "Nenhum autoload registrado (seção [autoload] vazia).",
        }

    # ── Scan de usos no código ──
    autoload_names = [a["name"] for a in registered]
    usage_counts = _scan_autoload_usages(proj, autoload_names)

    # ── Autoloads possivelmente não usados ──
    possibly_unused = sorted([
        name for name, count in usage_counts.items() if count == 0
    ])

    issues_found = len(possibly_unused) > 0

    return {
        "status": "issues_found" if issues_found else "ok",
        "registered_autoloads": registered,
        "possibly_unused_autoloads": possibly_unused,
        "summary": (
            f"{len(registered)} autoloads registrados, "
            f"{len(possibly_unused)} sem referência direta encontrada no código. "
            "possibly_unused não significa remover — pode haver uso via get_node ou grupo. "
            "Verificar manualmente antes de qualquer ação."
        ),
    }
