"""community_ops.py — Ferramentas de comunidade (Gaps ONDA 4).

Rollup community_manage(op=changelog|release_notes|roadmap_public|badge).
Ferramentas para manter a comunidade informada e engajada.

Ops:
  - changelog: Gera CHANGELOG.md formatado a partir dos commits desde a ultima tag.
  - release_notes: Gera notas de release para GitHub Releases.
  - roadmap_public: Gera ROADMAP.md publico a partir do .roadmap_progress.json.
  - badge: Retorna o snippet Markdown para o badge "Made with MCP Godot Agent".

Uso:
    community_manage op=changelog
    community_manage op=release_notes
    community_manage op=roadmap_public
    community_manage op=badge
"""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ── Changelog ────────────────────────────────────────────────────────

def _get_commits_since_last_tag() -> list[dict]:
    """Retorna lista de commits desde a ultima tag, ordenados por data."""
    try:
        # Pega a ultima tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        last_tag = result.stdout.strip()
    except Exception:
        last_tag = None

    if last_tag:
        log_range = f"{last_tag}..HEAD"
    else:
        log_range = "HEAD"

    try:
        result = subprocess.run(
            ["git", "log", log_range, "--pretty=format:%h|%s|%an|%ai", "--no-merges"],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        lines = result.stdout.strip().split("\n")
    except Exception:
        return []

    commits = []
    for line in lines:
        if not line:
            continue
        parts = line.split("|", 3)
        if len(parts) >= 4:
            commits.append({
                "hash": parts[0],
                "message": parts[1],
                "author": parts[2],
                "date": parts[3],
            })

    return commits


def _classify_commit(msg: str) -> str:
    """Classifica commit por tipo convencional."""
    msg_lower = msg.lower()
    if "!" in msg[:20] or msg_lower.startswith("breaking"):
        return "breaking"
    elif msg_lower.startswith("feat"):
        return "added"
    elif msg_lower.startswith("fix"):
        return "fixed"
    elif msg_lower.startswith("docs"):
        return "docs"
    elif msg_lower.startswith("test"):
        return "tests"
    elif msg_lower.startswith("refactor"):
        return "changed"
    elif msg_lower.startswith("perf"):
        return "perf"
    else:
        return "changed"


def _generate_changelog() -> dict:
    """Gera CHANGELOG.md padrao Keep a Changelog."""
    commits = _get_commits_since_last_tag()

    if not commits:
        return {
            "status": "success",
            "message": "Nenhum commit encontrado desde a ultima tag.",
            "changelog": "",
        }

    # Agrupa por tipo
    groups: dict[str, list[str]] = {
        "added": [],
        "fixed": [],
        "changed": [],
        "docs": [],
        "tests": [],
        "perf": [],
        "breaking": [],
    }

    type_labels = {
        "added": "Adicionado",
        "fixed": "Corrigido",
        "changed": "Modificado",
        "docs": "Documentacao",
        "tests": "Testes",
        "perf": "Performance",
        "breaking": "⚠️ Breaking Changes",
    }

    for c in commits:
        category = _classify_commit(c["message"])
        entry = f"- {c['message']} ({c['hash']})"
        groups[category].append(entry)

    # Monta o changelog
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# Changelog",
        "",
        "Todas as mudancas notaveis deste projeto sao documentadas neste arquivo.",
        "",
        f"## [Unreleased] — {today}",
        "",
    ]

    for key in ["added", "fixed", "changed", "docs", "tests", "perf", "breaking"]:
        if groups[key]:
            lines.append(f"### {type_labels[key]}")
            lines.extend(groups[key])
            lines.append("")

    changelog_text = "\n".join(lines)

    # Salva no arquivo
    changelog_path = ROOT / "CHANGELOG.md"
    existing = ""
    if changelog_path.exists():
        existing = changelog_path.read_text(encoding="utf-8")
        # Substitui a secao [Unreleased] se existir
        if "## [Unreleased]" in existing:
            # Mantem o resto do arquivo, substitui so o topo
            idx = existing.find("## [Unreleased]")
            end_idx = existing.find("\n## ", idx + 1)
            if end_idx == -1:
                end_idx = len(existing)
            existing = existing[:idx] + changelog_text.split("---", 1)[-1].strip() + "\n\n" + existing[end_idx:]
            changelog_path.write_text(existing, encoding="utf-8")
        else:
            # Insere no topo depois do titulo
            new_content = existing.replace("# Changelog\n", f"# Changelog\n\n{changelog_text}\n")
            changelog_path.write_text(new_content, encoding="utf-8")
    else:
        changelog_path.write_text(changelog_text, encoding="utf-8")

    return {
        "status": "success",
        "total_commits": len(commits),
        "groups": {k: len(v) for k, v in groups.items() if v},
        "changelog_path": str(changelog_path),
    }


# ── Release Notes ────────────────────────────────────────────────────

def _generate_release_notes(version: str | None = None) -> dict:
    """Gera notas de release para GitHub Releases."""
    commits = _get_commits_since_last_tag()

    if not commits:
        return {
            "status": "error",
            "message": "Nenhum commit encontrado. Rode changelog primeiro.",
        }

    if version is None:
        version = datetime.now(timezone.utc).strftime("v%Y.%m.%d")

    # Agrupa por tipo
    features = []
    fixes = []
    other = []

    for c in commits:
        cat = _classify_commit(c["message"])
        entry = f"- {c['message']} ({c['hash']})"
        if cat == "added":
            features.append(entry)
        elif cat == "fixed":
            fixes.append(entry)
        else:
            other.append(entry)

    lines = [
        f"## {version}",
        "",
    ]

    if features:
        lines.append("### 🚀 Novas funcionalidades")
        lines.extend(features)
        lines.append("")

    if fixes:
        lines.append("### 🐛 Correções")
        lines.extend(fixes)
        lines.append("")

    if other:
        lines.append("### 📝 Outras mudanças")
        lines.extend(other)
        lines.append("")

    lines.append(f"**Total:** {len(commits)} commits desde a ultima tag.")
    lines.append("")
    lines.append("---")
    lines.append("*Gerado automaticamente pelo `community_manage op=release_notes`.*")

    notes_text = "\n".join(lines)

    return {
        "status": "success",
        "version": version,
        "total_commits": len(commits),
        "features": len(features),
        "fixes": len(fixes),
        "release_notes": notes_text,
    }


# ── Roadmap Publico ──────────────────────────────────────────────────

def _generate_roadmap_public() -> dict:
    """Gera ROADMAP.md publico a partir do .roadmap_progress.json."""
    progress_path = ROOT / ".roadmap_progress.json"
    if not progress_path.exists():
        return {"status": "error", "message": ".roadmap_progress.json nao encontrado."}

    progress = json.loads(progress_path.read_text(encoding="utf-8"))

    # Mapeia ondas e fatias
    lines = [
        "# 🗺️ Roadmap — MCP Godot Agent",
        "",
        "> Atualizado automaticamente pelo `community_manage op=roadmap_public`.",
        f"> Ultima atualizacao: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Progresso por Onda",
        "",
    ]

    # Extrai fatias do progresso
    fatias = {}
    for key, value in progress.items():
        if key.startswith("fatia_"):
            fatias[key] = value

    # Agrupa por onda
    ondas: dict[str, list[dict]] = {}
    for key, value in sorted(fatias.items()):
        # Extrai numero da onda (ex: fatia_1.A -> 1)
        parts = key.replace("fatia_", "").split(".")
        onda = parts[0] if parts else "?"
        if onda not in ondas:
            ondas[onda] = []
        ondas[onda].append({"id": key, **value})

    status_icons = {
        "concluida": "✅",
        "em_andamento": "🔄",
        "bloqueada": "🔒",
        "escalada": "⚠️",
    }

    for onda in sorted(ondas.keys()):
        items = ondas[onda]
        concluidas = sum(1 for i in items if i.get("status") == "concluida")
        total = len(items)
        pct = round(concluidas / total * 100) if total > 0 else 0

        lines.append(f"### ONDA {onda} — {concluidas}/{total} ({pct}%)")
        lines.append("")
        lines.append("| Fatia | Status | Data | Resultado |")
        lines.append("|---|---|---|---|")
        for item in items:
            icon = status_icons.get(item.get("status", ""), "❓")
            resultado = (item.get("resultado", "") or "")[:80]
            data = item.get("data", "—")
            lines.append(f"| {item['id']} | {icon} | {data} | {resultado} |")
        lines.append("")

    roadmap_text = "\n".join(lines)

    # Salva
    roadmap_path = ROOT / "ROADMAP.md"
    roadmap_path.write_text(roadmap_text, encoding="utf-8")

    return {
        "status": "success",
        "ondas": len(ondas),
        "total_fatias": len(fatias),
        "concluidas": sum(1 for f in fatias.values() if f.get("status") == "concluida"),
        "roadmap_path": str(roadmap_path),
    }


# ── Badge ────────────────────────────────────────────────────────────

def _get_badge_snippet() -> dict:
    """Retorna snippet Markdown para o badge 'Made with MCP Godot Agent'."""
    badge_url = (
        "https://raw.githubusercontent.com/joabcostamd/"
        "mcp-godot-desenvolvimento/main/assets/badge.svg"
    )
    repo_url = "https://github.com/joabcostamd/mcp-godot-desenvolvimento"

    markdown = f"[![Made with MCP Godot Agent]({badge_url})]({repo_url})"
    html = (
        f'<a href="{repo_url}">'
        f'<img src="{badge_url}" alt="Made with MCP Godot Agent" width="240" height="40">'
        f'</a>'
    )

    return {
        "status": "success",
        "badge_url": badge_url,
        "repo_url": repo_url,
        "markdown": markdown,
        "html": html,
        "instructions": (
            "Copie o snippet Markdown abaixo e cole no README.md do seu projeto "
            "para mostrar que foi feito com MCP Godot Agent:"
        ),
    }


# ── Rollup ────────────────────────────────────────────────────────────

def community_manage(op: str, params: dict | None = None) -> dict:
    """Rollup community_manage — ferramentas de comunidade.

    Args:
        op: Operacao: 'changelog', 'release_notes', 'roadmap_public', 'badge'.
        params: Dicionario com parametros.
            - version (str): Versao para release_notes. Default: data atual.

    Returns:
        dict com "status" ("success" ou "error").
    """
    if params is None:
        params = {}

    if op == "changelog":
        return _generate_changelog()

    elif op == "release_notes":
        version = params.get("version")
        return _generate_release_notes(version=version)

    elif op == "roadmap_public":
        return _generate_roadmap_public()

    elif op == "badge":
        return _get_badge_snippet()

    else:
        return {
            "status": "error",
            "message": f"Operacao '{op}' desconhecida. Use: changelog, release_notes, roadmap_public, badge.",
        }
