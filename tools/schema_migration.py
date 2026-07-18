"""schema_migration.py — Migração de Schema de Estado (Fatia 0.10).

Gerencia versionamento de arquivos .mcp_*_state.json por projeto.
Quando uma feature nova adiciona campos ao estado, a migração é feita
automaticamente ao carregar — sem perder dados existentes.

Uso:
    from tools.schema_migration import load_state_with_migration, save_state_with_version

    data, migrated = load_state_with_migration("meu_arquivo.json", project_root)
    # migrated = True se houve migração
    # data contém schema_version já atualizado

    save_state_with_version("meu_arquivo.json", data, project_root)
    # Salva com schema_version injetado

Regra (Fatia 0.10):
    - Toda persistência de estado por projeto deve usar estes helpers.
    - schema_version é independente por arquivo.
    - Nunca sobrescrever estado sem schema_version.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("mcp-godot.schema_migration")

# ── Versões atuais por arquivo de estado ────────────────────────────
# Incrementar quando o schema de um arquivo mudar.
STATE_SCHEMA_VERSIONS: dict[str, int] = {
    ".mcp_phase_state.json": 1,
    ".mcp_governor_state.json": 1,
    ".mcp_milestones.json": 1,
    ".mcp_project_brief.json": 1,
    ".mcp_vibe_state.json": 1,
}

# ── Registro de migrações: (arquivo, versão_de) → função ───────────
# A função recebe data: dict e retorna data: dict (modificado).
# Versão '0' = estado sem schema_version.
MIGRATIONS: dict[tuple[str, int], Any] = {
    # Quando adicionar uma migração, use:
    # (".mcp_phase_state.json", 1): _migrate_phase_v1_to_v2,
}


# Futuras migrações exemplo (descomentar quando necessárias):
# def _migrate_phase_v1_to_v2(data: dict) -> dict:
#     """Adiciona campo 'schema_version' ao estado de fase."""
#     data["new_field"] = data.get("new_field", "default_value")
#     return data


def _get_actual_version(data: dict) -> int:
    """Retorna a versão real do schema no dicionário.

    0 = sem schema_version (estado pré-0.10)
    """
    return data.get("schema_version", 0)


def _apply_migrations(file_name: str, data: dict,
                      target_version: int) -> tuple[dict, bool]:
    """Aplica migrações em cadeia de 0 até target_version.

    Args:
        file_name: Nome do arquivo (ex: ".mcp_phase_state.json").
        data: Dicionário de dados carregado.
        target_version: Versão alvo (STATE_SCHEMA_VERSIONS[file_name]).

    Returns:
        (data migrado, houve migração?)
    """
    current = _get_actual_version(data)
    was_migrated = False

    while current < target_version:
        next_ver = current + 1
        key = (file_name, current)
        was_migrated = True  # Qualquer incremento de versão é migração
        migrator = MIGRATIONS.get(key)
        if migrator:
            try:
                data = migrator(data)
                logger.info(f"Migração {file_name}: v{current} → v{next_ver}")
            except Exception as e:
                logger.warning(
                    f"Migração {file_name} v{current}→v{next_ver} falhou: {e}"
                    f" — Prosseguindo sem migrar."
                )
                was_migrated = False
                break
        # Avança para próxima versão (mesmo sem migrador, para tracking)
        data["schema_version"] = next_ver
        current = next_ver

    return data, was_migrated


def load_state_with_migration(
    file_name: str,
    project_root: Path,
) -> tuple[dict, bool]:
    """Carrega estado de arquivo aplicando migrações automaticamente.

    Args:
        file_name: Nome do arquivo de estado (ex: ".mcp_phase_state.json").
        project_root: Raiz do projeto ativo (Path absoluto).

    Returns:
        (data: dict, was_migrated: bool)
        data sempre tem schema_version = versão atual.
        was_migrated = True se houve migração (salvar depois).
    """
    file_path = project_root / file_name
    data: dict = {}

    if file_path.exists():
        try:
            raw = file_path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
            logger.warning(f"Erro ao ler {file_name}: {e} — iniciando estado vazio.")
            data = {}
    else:
        data = {}

    # Aplica migrações
    target = STATE_SCHEMA_VERSIONS.get(file_name, 1)
    data, was_migrated = _apply_migrations(file_name, data, target)

    # Garante schema_version presente
    data["schema_version"] = target

    return data, was_migrated


def save_state_with_version(
    file_name: str,
    data: dict,
    project_root: Path,
) -> Path:
    """Salva estado com schema_version injetado.

    Args:
        file_name: Nome do arquivo de estado.
        data: Dicionário de dados.
        project_root: Raiz do projeto ativo.

    Returns:
        Path do arquivo salvo.
    """
    target = STATE_SCHEMA_VERSIONS.get(file_name, 1)
    data["schema_version"] = target

    file_path = project_root / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )

    return file_path