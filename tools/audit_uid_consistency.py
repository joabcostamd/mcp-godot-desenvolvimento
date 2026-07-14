"""audit_uid_consistency.py — Auditoria de Consistência de UID (Bloco 2.1).

Detecta:
  (a) UID declarado em [gd_scene] / [gd_resource] diferente do UID real
      no arquivo .uid companheiro (Godot 4.4+).
  (b) Recursos sem arquivo .uid quando o projeto usa config_version >= 6.
  (c) UIDs duplicados — dois arquivos diferentes com o mesmo UID (crítico).

Ferramenta SOMENTE LEITURA — não modifica nenhum arquivo.
"""

import re
import struct
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


def _get_config_version(proj: Path) -> int:
    """Lê config_version do project.godot."""
    pg = proj / "project.godot"
    if not pg.exists():
        return 0
    try:
        content = pg.read_text(encoding="utf-8")
    except Exception:
        return 0
    m = re.search(r'config_version\s*=\s*(\d+)', content)
    return int(m.group(1)) if m else 0


def _extract_declared_uids(proj: Path) -> dict[str, str]:
    """Varre .tscn e .tres e retorna dict {path_relativo: uid_declarado}.

    Extrai o uid do header [gd_scene ... uid="uid://..."] ou
    [gd_resource ... uid="uid://..."].
    """
    declared: dict[str, str] = {}
    for pattern in ("*.tscn", "*.tres"):
        for f in proj.rglob(pattern):
            if _should_skip(f):
                continue
            try:
                content = f.read_text(encoding="utf-8")
            except Exception:
                continue
            m = re.search(r'\[gd_(?:scene|resource)\s+[^\]]*uid="(uid://[^"]+)"', content)
            if m:
                rel = str(f.relative_to(proj)).replace("\\", "/")
                declared[rel] = m.group(1)
    return declared


def _read_uid_file(uid_path: Path) -> str | None:
    """Lê um arquivo .uid e retorna o UID (formato texto simples)."""
    if not uid_path.exists():
        return None
    try:
        content = uid_path.read_text(encoding="utf-8").strip()
        if content.startswith("uid://"):
            return content
        return None
    except Exception:
        return None


def _parse_uid_cache(proj: Path) -> dict[str, str] | None:
    """Tenta parsear .godot/uid_cache.bin e retorna dict {path: uid}.

    Formato binário (Godot 4.x):
      - big-endian int32: número de entradas
      - para cada entrada:
        - 8 bytes: ID (uint64 big-endian)
        - string: path (length-prefixed com uint32)
    Retorna None se não for parseável.
    """
    cache_path = proj / ".godot" / "uid_cache.bin"
    if not cache_path.exists():
        return None
    try:
        data = cache_path.read_bytes()
        if len(data) < 4:
            return None
        count = struct.unpack(">I", data[0:4])[0]
        offset = 4
        result: dict[str, str] = {}
        for _ in range(count):
            if offset + 8 > len(data):
                break
            uid_int = struct.unpack(">Q", data[offset:offset + 8])[0]
            offset += 8
            if offset + 4 > len(data):
                break
            path_len = struct.unpack(">I", data[offset:offset + 4])[0]
            offset += 4
            if offset + path_len > len(data):
                break
            path_bytes = data[offset:offset + path_len]
            offset += path_len
            try:
                path_str = path_bytes.decode("utf-8")
            except UnicodeDecodeError:
                continue
            uid_str = f"uid://{uid_int:016x}"
            result[path_str] = uid_str
        return result if result else None
    except Exception:
        return None


def _uid_to_res_path(raw_path: str) -> str | None:
    """Normaliza path do uid_cache para formato res:// relativo."""
    if raw_path.startswith("res://"):
        return raw_path[6:]
    return raw_path


# ── Função principal ─────────────────────────────────────────────────

def audit_uid_consistency(project_path: str | None = None) -> dict:
    """Audita a consistência de UIDs no projeto.

    Args:
        project_path: Caminho do projeto (opcional, usa projeto ativo).

    Returns:
        dict com status, mismatched_uid, missing_uid_file, duplicate_uid, unresolved.
    """
    proj = _resolve_project(project_path)
    if proj is None:
        return {"status": "error", "message": "Projeto não encontrado. Configure com set_active_project."}
    if not proj.exists():
        return {"status": "error", "message": f"Projeto não encontrado: {proj}"}

    pg_path = proj / "project.godot"
    if not pg_path.exists():
        return {"status": "error", "message": f"project.godot não encontrado em: {proj}"}

    config_ver = _get_config_version(proj)

    # ── 1. Coletar UIDs declarados ──
    declared = _extract_declared_uids(proj)
    total_refs = len(declared)

    # ── 2. Verificar arquivos .uid ──
    mismatched: list[dict] = []
    missing_uid_file: list[str] = []
    duplicate_uid: list[dict] = []
    unresolved: list[str] = []

    # Mapa uid -> lista de arquivos (para detectar duplicados)
    uid_to_files: dict[str, list[str]] = {}
    for rel_path, uid in declared.items():
        uid_to_files.setdefault(uid, []).append(rel_path)

    # Verificar duplicados entre declarados
    for uid, files in uid_to_files.items():
        if len(files) > 1:
            duplicate_uid.append({"uid": uid, "files": sorted(files)})

    # Verificar .uid files e mismatches
    for rel_path, declared_uid in declared.items():
        abs_path = proj / rel_path
        uid_file = Path(str(abs_path) + ".uid")

        if uid_file.exists():
            actual_uid = _read_uid_file(uid_file)
            if actual_uid and actual_uid != declared_uid:
                mismatched.append({
                    "file": f"res://{rel_path}",
                    "referenced_uid": declared_uid,
                    "actual_uid": actual_uid,
                    "referenced_from": f"res://{rel_path}",
                })
            # Registrar UID real para verificar duplicados cross-file
            if actual_uid:
                uid_to_files.setdefault(actual_uid, []).append(f"res://{rel_path}")
        else:
            # Só reporta missing se config_version >= 6
            if config_ver >= 6:
                missing_uid_file.append(f"res://{rel_path}")

    # Verificar duplicados entre UIDs reais de .uid files
    seen_real: dict[str, list[str]] = {}
    for rel_path in declared:
        abs_path = proj / rel_path
        uid_file = Path(str(abs_path) + ".uid")
        if uid_file.exists():
            actual = _read_uid_file(uid_file)
            if actual:
                seen_real.setdefault(actual, []).append(f"res://{rel_path}")
    for uid, files in seen_real.items():
        if len(files) > 1:
            # Evitar duplicar com duplicate_uid já registrado
            already = any(d["uid"] == uid for d in duplicate_uid)
            if not already:
                duplicate_uid.append({"uid": uid, "files": sorted(files)})

    # ── 3. Tentar parsear uid_cache.bin ──
    cache = _parse_uid_cache(proj)
    if cache is None and (proj / ".godot" / "uid_cache.bin").exists():
        unresolved.append(
            "res://.godot/uid_cache.bin (arquivo binário não parseável — "
            "formato pode ter mudado nesta versão do Godot)"
        )

    # ── 4. Montar resultado ──
    issues_found = bool(mismatched or missing_uid_file or duplicate_uid)

    summary_parts = [f"{total_refs} UIDs declarados verificados"]
    if mismatched:
        summary_parts.append(f"{len(mismatched)} com divergência")
    if missing_uid_file:
        summary_parts.append(f"{len(missing_uid_file)} sem arquivo .uid")
    if duplicate_uid:
        summary_parts.append(f"{len(duplicate_uid)} UIDs duplicados")
    if unresolved:
        summary_parts.append(f"{len(unresolved)} não resolvidos")
    if not issues_found:
        summary_parts.append("nenhum problema encontrado")

    return {
        "status": "issues_found" if issues_found else "ok",
        "total_uid_refs_checked": total_refs,
        "mismatched_uid": mismatched,
        "missing_uid_file": missing_uid_file,
        "duplicate_uid": duplicate_uid,
        "unresolved": unresolved,
        "note": (
            "Esta ferramenta audita consistência de UID declarado vs UID real de arquivo. "
            "NÃO corrige nada — divergência de UID pode ser resolvida reimportando o recurso "
            f"no editor Godot. config_version={config_ver}: "
            + ("projeto usa sistema de .uid files (Godot 4.4+)." if config_ver >= 6
               else "projeto usa sistema antigo (pré-4.4). Ausência de .uid files é esperada.")
        ),
        "summary": ", ".join(summary_parts) + ".",
    }
