"""audit_save_compatibility.py — Compatibilidade de Save (Bloco 2.2).

Detecta:
  (a) Divergência entre chaves escritas e lidas no código de save.
  (b) Ausência de lógica de migração por versão.
  (c) Chaves órfãs/faltantes ao testar contra um arquivo de save real.

Ferramenta SOMENTE LEITURA — não modifica nenhum arquivo.
"""

import json
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


def _find_save_manager(proj: Path) -> tuple[str | None, Path | None]:
    """Localiza o script de save (autoload ou padrão de nome).

    Returns:
        (nome_autoload | None, Path do script | None)
    """
    # 1. Tentar via autoloads registrados
    pg = proj / "project.godot"
    if pg.exists():
        try:
            content = pg.read_text(encoding="utf-8")
        except Exception:
            content = ""
        in_autoload = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped == "[autoload]":
                in_autoload = True
                continue
            if in_autoload:
                if stripped.startswith("[") and stripped.endswith("]"):
                    break
                m = re.match(r'(\w+)\s*=\s*"\*?([^"]+)"', stripped)
                if m:
                    name = m.group(1)
                    script_path = m.group(2)
                    if "save" in name.lower() or "save" in script_path.lower():
                        script_rel = script_path[6:] if script_path.startswith("res://") else script_path
                        script_abs = proj / script_rel
                        if script_abs.exists():
                            return name, script_abs

    # 2. Buscar por padrão de nome
    for pattern in ("**/*save_manager*.gd", "**/*save*.gd", "**/save*.gd"):
        for f in proj.glob(pattern):
            if _should_skip(f):
                continue
            # Verificar se parece um save manager (contém serialize/deserialize)
            try:
                content = f.read_text(encoding="utf-8")
            except Exception:
                continue
            if "serialize" in content.lower() and ("fileaccess" in content.lower() or "store_string" in content.lower()):
                return None, f

    return None, None


def _extract_function_body(content: str, func_names: list[str]) -> str | None:
    """Extrai o corpo de uma função GDScript pelo nome.

    Procura por 'func nome_da_funcao(' e extrai até o próximo 'func ' no mesmo
    nível de indentação ou fim do arquivo.
    Retorna o texto do corpo da função ou None se não encontrada.
    """
    for fname in func_names:
        # Encontra o início da função (suporta -> ReturnType:)
        pattern = rf'(?:^|\n)\s*func\s+{re.escape(fname)}\s*\([^)]*\)(?:\s*->\s*\w+)?\s*:'
        m = re.search(pattern, content)
        if not m:
            continue
        start = m.end()
        # Encontra o fim: próximo 'func ' no nível 0 de indentação, ou fim do arquivo
        remaining = content[start:]
        next_func = re.search(r'(?:^|\n)func\s+\w+\s*\(', remaining)
        if next_func:
            body = remaining[:next_func.start()]
        else:
            body = remaining
        return body
    return None


def _extract_write_keys(content: str) -> set[str]:
    """Extrai chaves que o código ESCREVE no save.

    Escopo: apenas a função _serialize_state() ou save_game().
    Detecta:
      - Chaves de dicionário literal: "key": value
      - Atribuição direta: data["key"] = value
    """
    body = _extract_function_body(content, ["_serialize_state", "save_game", "save"])
    if body is None:
        # Fallback: arquivo inteiro
        body = content

    keys: set[str] = set()
    # Chaves em dicionário literal { "key": val }
    for m in re.finditer(r'"(\w+)"\s*:', body):
        keys.add(m.group(1))
    # data["key"] = (escrita)
    for m in re.finditer(r'\["(\w+)"\]\s*=', body):
        keys.add(m.group(1))
    return keys


def _extract_read_keys(content: str) -> set[str]:
    """Extrai chaves que o código LÊ do save.

    Escopo: apenas a função _deserialize_state() ou load_game().
    Detecta APENAS .get("key") — este é o padrão de leitura confiável.
    NÃO usa data["key"] porque é ambíguo (pode ser array literal).
    """
    body = _extract_function_body(content, ["_deserialize_state", "load_game", "load"])
    if body is None:
        body = content

    keys: set[str] = set()
    for m in re.finditer(r'\.get\s*\(\s*"(\w+)"', body):
        keys.add(m.group(1))
    return keys


def _has_version_migration(content: str) -> bool:
    """Verifica se o código contém lógica CONDICIONAL de migração por versão.

    Detecta estruturas reais de controle de fluxo:
      - if version < N / if version > N / if version != N
      - match version:
      - if save_version ...
    NÃO detecta menções em comentários ou strings.
    """
    body = _extract_function_body(content, ["_deserialize_state", "load_game", "load"])
    if body is None:
        body = content
    patterns = [
        r'if\s+.*\bversion\b\s*[<>!=]',        # if version < 2
        r'match\s+.*\bversion\b',                # match version:
        r'if\s+.*\bsave_version\b',              # if save_version
        r'if\s+.*\bdata_version\b',              # if data_version
        r'if\s+.*\bschema_version\b',            # if schema_version
    ]
    for pat in patterns:
        if re.search(pat, body, re.IGNORECASE):
            return True
    return False


def _has_version_field(content: str) -> bool:
    """Verifica se o save inclui um campo de versão."""
    version_keys = {"version", "save_version", "data_version", "schema_version"}
    write_keys = _extract_write_keys(content)
    return bool(write_keys & version_keys)


# ── Função principal ─────────────────────────────────────────────────

def audit_save_compatibility(
    project_path: str | None = None,
    save_file_path: str | None = None,
) -> dict:
    """Audita a compatibilidade de save no projeto.

    Args:
        project_path: Caminho do projeto (opcional, usa projeto ativo).
        save_file_path: Caminho de um arquivo de save real para testar (opcional).

    Returns:
        dict com status, save_manager_script, write_read_key_mismatch, etc.
    """
    proj = _resolve_project(project_path)
    if proj is None:
        return {"status": "error", "message": "Projeto não encontrado. Configure com set_active_project."}
    if not proj.exists():
        return {"status": "error", "message": f"Projeto não encontrado: {proj}"}

    # ── 1. Localizar SaveManager ──
    autoload_name, script_path = _find_save_manager(proj)
    if script_path is None:
        return {
            "status": "ambiguous",
            "save_manager_script": None,
            "has_version_field": False,
            "has_migration_logic": False,
            "write_read_key_mismatch": [],
            "tested_against_file": None,
            "missing_key_in_save": [],
            "orphaned_key_in_save": [],
            "note": (
                "Esta ferramenta faz análise estática de código, não roda o jogo. "
                "Não foi possível localizar um script de save (procurei por autoloads "
                "com 'save' no nome e por padrão *save*.gd)."
            ),
            "summary": "Nenhum script de save encontrado no projeto.",
        }

    script_rel = str(script_path.relative_to(proj)).replace("\\", "/")
    try:
        content = script_path.read_text(encoding="utf-8")
    except Exception as e:
        return {"status": "error", "message": f"Erro ao ler script de save: {e}"}

    # ── 2. Extrair chaves de escrita e leitura ──
    write_keys = _extract_write_keys(content)
    read_keys = _extract_read_keys(content)

    # ── 3. Detectar divergências ──
    mismatch: list[dict] = []
    written_not_read = write_keys - read_keys
    read_not_written = read_keys - write_keys

    for key in sorted(written_not_read):
        mismatch.append({"key": key, "issue": "escrito mas nunca lido"})
    for key in sorted(read_not_written):
        mismatch.append({"key": key, "issue": "lido mas nunca escrito"})

    # ── 4. Verificar versionamento ──
    has_version = _has_version_field(content)
    has_migration = _has_version_migration(content)

    # ── 5. Testar contra save file (se fornecido) ──
    missing_in_save: list[str] = []
    orphaned_in_save: list[str] = []
    tested_file: str | None = None

    if save_file_path:
        save_path = Path(save_file_path)
        if not save_path.is_absolute():
            save_path = proj / save_path
        if save_path.exists():
            tested_file = str(save_path)
            try:
                save_data = json.loads(save_path.read_text(encoding="utf-8"))
                if isinstance(save_data, dict):
                    save_keys = set(save_data.keys())
                    missing_in_save = sorted(read_keys - save_keys)
                    orphaned_in_save = sorted(save_keys - read_keys)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Erro ao ler arquivo de save: {e}",
                    "save_manager_script": f"res://{script_rel}",
                }
        else:
            return {
                "status": "error",
                "message": f"Arquivo de save não encontrado: {save_file_path}",
                "save_manager_script": f"res://{script_rel}",
            }

    # ── 6. Montar resultado ──
    issues_found = bool(mismatch or missing_in_save or orphaned_in_save)
    if not has_migration and has_version:
        issues_found = True  # aviso importante

    summary_parts = []
    if autoload_name:
        summary_parts.append(f"SaveManager: {autoload_name}")
    else:
        summary_parts.append(f"Script: res://{script_rel}")
    if mismatch:
        summary_parts.append(f"{len(mismatch)} divergências escrita/leitura")
    if has_version and not has_migration:
        summary_parts.append("campo version existe mas sem lógica de migração")
    if missing_in_save:
        summary_parts.append(f"{len(missing_in_save)} chaves ausentes no save")
    if orphaned_in_save:
        summary_parts.append(f"{len(orphaned_in_save)} chaves órfãs no save")
    if not issues_found:
        summary_parts.append("nenhum problema encontrado")

    return {
        "status": "issues_found" if issues_found else "ok",
        "save_manager_script": f"res://{script_rel}",
        "has_version_field": has_version,
        "has_migration_logic": has_migration,
        "write_read_key_mismatch": mismatch,
        "tested_against_file": tested_file,
        "missing_key_in_save": missing_in_save,
        "orphaned_key_in_save": orphaned_in_save,
        "note": (
            "Esta ferramenta faz análise estática de código, não roda o jogo. "
            "Não garante que a lógica de migração (se existir) funcione corretamente "
            "em runtime — só detecta ausência ou presença dela."
        ),
        "summary": ", ".join(summary_parts) + ".",
    }
