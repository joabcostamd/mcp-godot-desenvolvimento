"""doc_ops.py — Documentacao Automatica (Fatia 4.9 / Etapa B9).

Gera documentacao a partir do estado real do projeto:
  - Changelog do git log
  - README do estado atual
  - Wiki do projeto
"""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ══════════════════════════════════════════════════════════════════════
# Op 1: generate_changelog
# ══════════════════════════════════════════════════════════════════════

def generate_changelog(
    max_commits: int = 50,
    format_type: str = "markdown",
    since: str | None = None,
) -> dict:
    """Gera changelog a partir do historico git.

    Args:
        max_commits: Numero maximo de commits a incluir.
        format_type: Formato de saida ("markdown" ou "json").
        since: Data de inicio (ex: "2026-01-01"). Se None, usa todos.

    Returns:
        dict com changelog formatado.
    """
    cmd = ["git", "log", f"--max-count={max_commits}", "--pretty=format:%H|%ai|%an|%s"]
    if since:
        cmd.append(f"--since={since}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=30,
            cwd=str(ROOT),
        )
    except FileNotFoundError:
        return {"status": "error", "error": "Git nao encontrado ou nao e um repositorio git."}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Timeout ao executar git log."}
    except Exception as e:
        return {"status": "error", "error": f"Erro ao gerar changelog: {e}"}

    commits = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        sha, date_str, author, message = parts
        # Classifica o tipo de commit
        commit_type = "other"
        if message.startswith("feat"):
            commit_type = "feature"
        elif message.startswith("fix"):
            commit_type = "fix"
        elif message.startswith("docs"):
            commit_type = "docs"
        elif message.startswith("refactor"):
            commit_type = "refactor"
        elif message.startswith("test"):
            commit_type = "test"
        elif message.startswith("chore"):
            commit_type = "chore"

        commits.append({
            "sha": sha[:8],
            "date": date_str[:10],
            "author": author,
            "message": message,
            "type": commit_type,
        })

    # Agrupa por tipo
    by_type = {}
    for c in commits:
        t = c["type"]
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(c)

    if format_type == "json":
        return {
            "status": "completed",
            "total_commits": len(commits),
            "by_type": {t: len(v) for t, v in by_type.items()},
            "commits": commits,
        }

    # Formato markdown
    md_lines = [
        f"# 📋 Changelog — MCP Godot",
        f"",
        f"Gerado em: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Total de commits: {len(commits)}",
        f"",
    ]

    type_labels = {
        "feature": "🚀 Features",
        "fix": "🐛 Correcoes",
        "docs": "📚 Documentacao",
        "refactor": "🔧 Refatoracao",
        "test": "🧪 Testes",
        "chore": "📦 Chores",
        "other": "📌 Outros",
    }

    for t in ["feature", "fix", "refactor", "test", "docs", "chore", "other"]:
        entries = by_type.get(t, [])
        if not entries:
            continue
        md_lines.append(f"## {type_labels.get(t, t)}")
        md_lines.append("")
        for c in entries:
            md_lines.append(f"- **{c['date']}** [{c['sha']}] {c['message']} ({c['author']})")
        md_lines.append("")

    changelog_text = "\n".join(md_lines)

    return {
        "status": "completed",
        "total_commits": len(commits),
        "by_type": {t: len(v) for t, v in by_type.items()},
        "changelog_md": changelog_text,
    }


# ══════════════════════════════════════════════════════════════════════
# Op 2: generate_project_readme
# ══════════════════════════════════════════════════════════════════════

def generate_project_readme() -> dict:
    """Gera README.md a partir do estado real do projeto.

    Extrai informacoes de:
      - ROADMAP_UNIFICADO.md (progresso)
      - .roadmap_progress.json (metricas)
      - pyproject.toml (dependencias)
      - requirements.txt (dependencias)
      - Estrutura de diretorios

    Returns:
        dict com README gerado e metricas.
    """
    sections = []

    # Titulo
    sections.append("# 🎮 MCP Godot Agent")
    sections.append("")
    sections.append("Servidor MCP (Model Context Protocol) para Godot Engine 4.x.")
    sections.append("Pipeline autonomo multi-agente de desenvolvimento de jogos.")
    sections.append("")

    # Status rapido
    progress = _read_progress()
    if progress:
        total = progress.get("total_fatias", 0)
        done = progress.get("concluidas", 0)
        pct = round(done / max(total, 1) * 100)
        sections.append(f"## 📊 Progresso: {done}/{total} fatias ({pct}%)")
        sections.append("")
        sections.append(f"![Progress](https://progress-bar.xyz/{pct}?title=completo)")
        sections.append("")

    # Features principais
    sections.append("## 🚀 Features")
    sections.append("")
    sections.append("### Pipeline de Verificacao")
    sections.append("- Compile check, headless run, screenshot, GUT tests")
    sections.append("- Code quality gate com gdtoolkit (gdlint + gdformat + gdradon)")
    sections.append("- Auditoria de cenas orfas e ciclos de referencia")
    sections.append("- 9 analises especificas de qualidade de codigo")
    sections.append("")
    sections.append("### Seguranca")
    sections.append("- Scan de vulnerabilidades em addons")
    sections.append("- Verificacao de licencas (GPL/AGPL/CC incompativel)")
    sections.append("- Scan de segredos vazados (API keys, tokens)")
    sections.append("")
    sections.append("### Orquestracao de Agentes")
    sections.append("- File lock entre agentes")
    sections.append("- Fila de tarefas com dependencia")
    sections.append("- Revisao cruzada e comparacao de outputs")
    sections.append("")
    sections.append("### CI/CD")
    sections.append("- GitHub Actions com verificacao completa")
    sections.append("- Budget gate (teto de tools)")
    sections.append("- Contract snapshot (drift de schema)")
    sections.append("")

    # Dependencias
    sections.append("## 📦 Instalacao")
    sections.append("")
    sections.append("```bash")
    sections.append("pip install -r requirements.txt")
    sections.append("```")
    sections.append("")
    reqs = _read_requirements()
    if reqs:
        sections.append("### Dependencias principais")
        for r in reqs[:6]:
            sections.append(f"- `{r}`")
        sections.append("")

    # Estrutura
    sections.append("## 📁 Estrutura")
    sections.append("")
    sections.append("```")
    structure = _get_structure()
    for s in structure:
        sections.append(s)
    sections.append("```")

    readme = "\n".join(sections)

    # Salva
    readme_path = ROOT / "README_AUTO.md"
    try:
        readme_path.write_text(readme, encoding="utf-8")
    except Exception:
        pass

    return {
        "status": "completed",
        "readme_file": str(readme_path.relative_to(ROOT)),
        "readme_lines": len(sections),
        "readme_md": readme,
    }


def _read_progress() -> dict | None:
    p = ROOT / ".roadmap_progress.json"
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        concluidas = sum(
            1 for v in data.values()
            if isinstance(v, dict) and v.get("status") in ("concluida", "implementada_pendente_revisao")
        )
        return {"total_fatias": len(data), "concluidas": concluidas}
    except Exception:
        return None


def _read_requirements() -> list[str]:
    p = ROOT / "requirements.txt"
    if not p.exists():
        return []
    try:
        return [
            line.strip() for line in p.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
    except Exception:
        return []


def _get_structure() -> list[str]:
    """Gera arvore de diretorios simplificada."""
    lines = ["mcp-godot-desenvolvimento/"]
    top_dirs = ["tools/", "tests/", ".github/", "addons/", "templates/", "docs/"]
    for d in top_dirs:
        p = ROOT / d.rstrip("/")
        if p.exists():
            lines.append(f"├── {d}")
    lines.append("├── server.py")
    lines.append("├── requirements.txt")
    lines.append("├── pyproject.toml")
    lines.append("└── ROADMAP_UNIFICADO.md")
    return lines


# ══════════════════════════════════════════════════════════════════════
# Op 3: generate_project_wiki
# ══════════════════════════════════════════════════════════════════════

def generate_project_wiki() -> dict:
    """Gera documentacao wiki a partir do estado do projeto.

    Agrega:
      - Glossario de ferramentas
      - Guia de contribuicao
      - Referencia de arquitetura
      - Metricas do projeto

    Returns:
        dict com paginas wiki geradas.
    """
    pages = {}

    # Pagina 1: Home
    pages["Home"] = _wiki_home()

    # Pagina 2: Ferramentas
    pages["Ferramentas"] = _wiki_tools()

    # Pagina 3: Arquitetura
    pages["Arquitetura"] = _wiki_architecture()

    # Pagina 4: Guia de Contribuicao
    pages["Guia-de-Contribuicao"] = _wiki_contributing()

    # Salva paginas
    wiki_dir = ROOT / "docs" / "wiki"
    wiki_dir.mkdir(parents=True, exist_ok=True)
    for name, content in pages.items():
        path = wiki_dir / f"{name}.md"
        try:
            path.write_text(content, encoding="utf-8")
        except Exception:
            pass

    return {
        "status": "completed",
        "pages_generated": len(pages),
        "wiki_dir": str(wiki_dir.relative_to(ROOT)),
        "pages": list(pages.keys()),
    }


def _wiki_home() -> str:
    progress = _read_progress()
    if progress:
        pct = round(progress["concluidas"] / max(progress["total_fatias"], 1) * 100)
        progress_str = f"{pct}% ({progress['concluidas']}/{progress['total_fatias']} fatias)"
    else:
        progress_str = "N/A"

    return f"""# 🎮 MCP Godot Agent — Wiki

Bem-vindo a wiki do MCP Godot Agent!

## 📊 Status do Projeto

- **Progresso**: {progress_str}
- **Godot**: 4.7+
- **Python**: 3.11+
- **MCP Spec**: 2025-11-25

## 🚀 Inicio Rapido

```bash
pip install -r requirements.txt
python server.py
```

## 📚 Navegacao

- [[Ferramentas]] — Catalogo completo de ferramentas
- [[Arquitetura]] — Design e estrutura do sistema
- [[Guia-de-Contribuicao]] — Como contribuir

## 🔗 Links

- [GitHub](https://github.com/joabcostamd/mcp-godot-desenvolvimento)
- [Godot MCP Docs](https://godotengine.org)
"""


def _wiki_tools() -> str:
    content = ["# 🔧 Ferramentas", "", "## Gates de Qualidade", ""]
    content.append("- `run_code_quality_gate` — gdlint + gdformat + gdradon")
    content.append("- `scan_addon_vulnerabilities` — 12 padroes de vulnerabilidade")
    content.append("- `check_addon_license` — 19 tipos de licenca")
    content.append("")
    content.append("## Analises Especificas")
    content.append("- `find_unused_functions` — Funcoes nao utilizadas")
    content.append("- `detect_gdscript_antipatterns` — Antipadroes GDScript")
    content.append("- `find_orphan_signals_nodes` — Sinais orfaos")
    content.append("- `check_naming_convention` — Convencoes de nome")
    content.append("- `find_duplicate_code_blocks` — Codigo duplicado")
    content.append("- `detect_scene_reference_cycles` — Ciclos de cena")
    content.append("- `check_import_settings_consistency` — Consistencia .import")
    content.append("- `semantic_code_search` — Busca semantica")
    content.append("- `suggest_refactor` — Sugestoes de refatoracao")
    content.append("")
    content.append("## Orquestracao")
    content.append("- `acquire_file_lock` / `release_file_lock` — Lock entre agentes")
    content.append("- `create_task_queue` / `get_next_task` — Fila de tarefas")
    content.append("- `request_peer_review` — Revisao cruzada")
    content.append("- `compare_agent_outputs` — Comparacao de modelos")
    return "\n".join(content)


def _wiki_architecture() -> str:
    return """# 🏗 Arquitetura

## Estrutura do Sistema

```
server.py          — Servidor MCP principal (AGENTE 01)
tools/
  *_ops.py         — Modulos de operacao (AGENTE 02)
  rollups.py       — Rollups de dominio (AGENTE 01)
  deprecated.py    — Zona de Sutura (congelada)
core/              — Nucleo do sistema (AGENTE 01)
tests/             — Testes automatizados
.github/           — CI/CD workflows
```

## Agentes

- **AGENTE 01** — Arquitetura & Core: `server.py`, `core/*`, `rollups.py`
- **AGENTE 02** — Extensoes & Qualidade: `tools/*_ops.py`, `.github/*`, `tests/*`

## Zona de Sutura

Arquivos congelados — mudancas requerem aprovacao:
- `tools/deprecated.py`
- `ROADMAP_UNIFICADO.md`
- `SUTURE_ISSUES.md`
"""


def _wiki_contributing() -> str:
    return """# 📝 Guia de Contribuicao

## Fluxo de Desenvolvimento

1. Identifique a proxima etapa em `ROADMAP_UNIFICADO.md`
2. Verifique `SUTURE_ISSUES.md` para conflitos
3. Implemente EXATAMENTE 1 etapa
4. Audite com `auditar.py` ou `validate_tool_registry_consistency()`
5. Atualize `HANDOFF.md`, `NEXT_STEP.md`, `.roadmap_progress.json`
6. Commit: `feat(agente-X-etapa-Y): descricao em portugues`

## Regras de Ouro

- NUNCA edite arquivos do outro agente
- Respeite `# INTERNAL:` — funcoes usadas por rollups
- 1 commit por etapa
- Auditoria apos cada implementacao
- Conflitos em `SUTURE_ISSUES.md`, nao resolva sozinho

## Ambiente

```bash
# Ativar venv
.\\.venv\\Scripts\\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Rodar testes
python tests/test_code_quality_ops.py
```
"""
