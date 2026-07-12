"""project_brief_ops.py — Project Brief Persistente (Feature 5).

Armazena caracteristicas fundamentais do projeto para que ferramentas
como create_entity possam usar como fallback quando parametros nao sao
passados explicitamente.

Persistencia: <project_root>/.mcp_project_brief.json (por projeto).
NAO usa config global do MCP.

Tools:
    - set_project_brief: define/sobrescreve o brief
    - get_project_brief: retorna o brief atual
    - update_project_brief: atualiza campos especificos
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Valores validos para validacao
VALID_PLATFORMS = {"pc", "mobile", "web"}


# ===================================================================
# Validacao compartilhada
# ===================================================================

def _validate_genre(genre: str) -> str | None:
    """Valida um genero contra GAME_PATTERNS + ALIAS_MAP.

    Retorna o nome canonico se valido, ou None se invalido.
    Normaliza para lowercase + underscores (ex: "Tower Defense" -> "tower_defense").
    """
    try:
        from resources.game_patterns import GAME_PATTERNS

        ALIAS_MAP = {
            "rpg": "rpg_turn_based",
            "shooter": "top_down_shooter",
            "puzzle": "puzzle_match3",
            "roguelike": "roguelike_dungeon_crawler",
        }

        # Normaliza: lowercase, espaços → underscores
        normalized = genre.lower().strip().replace(" ", "_").replace("-", "_")
        canonical = ALIAS_MAP.get(normalized, normalized)
        if canonical in GAME_PATTERNS:
            return canonical
    except Exception:
        pass
    return None


def _validate_platform(platform: str) -> bool:
    """Valida target_platform contra lista fixa."""
    return platform in VALID_PLATFORMS


# ===================================================================
# Persistencia
# ===================================================================

def _get_brief_path() -> Path | None:
    """Retorna o caminho do arquivo de brief do projeto ativo."""
    try:
        from tools.project_ops import _get_active_project
        proj = _get_active_project()
        if proj and proj.exists():
            return proj / ".mcp_project_brief.json"
    except Exception:
        pass
    return None


def _load_brief_state() -> dict:
    """Carrega o brief do projeto ativo. Retorna dict vazio se nao existir."""
    brief_path = _get_brief_path()
    if not brief_path or not brief_path.exists():
        return {}
    try:
        with open(brief_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_brief_state(state: dict) -> None:
    """Salva o brief no projeto ativo.

    ATENCAO: quem chama deve segurar BRIEF_STATE_LOCK.
    Esta funcao NAO adquire o lock internamente para evitar deadlock.
    """
    brief_path = _get_brief_path()
    if not brief_path:
        return
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    with open(brief_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ===================================================================
# API Publica
# ===================================================================

def set_project_brief(
    genre: str | None = None,
    art_style: str | None = None,
    tone: str | None = None,
    target_platform: str | None = None,
    force: bool = False,
) -> dict:
    """Define/sobrescreve o project brief do projeto ativo.

    Args:
        genre: Genero do jogo (17 generos via GAME_PATTERNS). Validado.
        art_style: Estilo visual (ex: scifi, fantasia, cartoon, pixel, minimalista).
        tone: Tom do jogo (ex: estrategico, casual, sombrio, epico, humorado).
        target_platform: Plataforma alvo (pc, mobile, web). Validado.
        force: Obrigatorio True se ja existir brief. Evita sobrescrita acidental.

    Returns:
        {"status": "success", "brief": {...}} ou {"status": "error", "message": str}
    """
    from tools.config_lock import BRIEF_STATE_LOCK

    # Valida que pelo menos um campo foi informado
    if all(v is None for v in (genre, art_style, tone, target_platform)):
        return {
            "status": "error",
            "message": "Nenhum campo informado. Informe pelo menos um: genre, art_style, tone, target_platform.",
        }

    # Valida genre
    canonical_genre = None
    if genre is not None:
        canonical_genre = _validate_genre(genre)
        if canonical_genre is None:
            try:
                from resources.game_patterns import GAME_PATTERNS
                valid = sorted(GAME_PATTERNS.keys())
            except Exception:
                valid = ["(erro ao carregar GAME_PATTERNS)"]
            return {
                "status": "error",
                "message": f"Genero '{genre}' invalido. Generos validos: {', '.join(valid)}.",
            }

    # Valida target_platform
    if target_platform is not None and not _validate_platform(target_platform):
        return {
            "status": "error",
            "message": f"Plataforma '{target_platform}' invalida. Validas: {', '.join(sorted(VALID_PLATFORMS))}.",
        }

    with BRIEF_STATE_LOCK:
        existing = _load_brief_state()

        # Verifica force se ja existe brief
        if existing and not force:
            return {
                "status": "error",
                "message": (
                    "Ja existe um project brief. Use force=True para sobrescrever "
                    "completamente ou update_project_brief para alterar campos especificos."
                ),
            }

        # Constroi novo brief (sobrescrita total)
        brief = {}
        if canonical_genre:
            brief["genre"] = canonical_genre
        if art_style is not None:
            brief["art_style"] = art_style
        if tone is not None:
            brief["tone"] = tone
        if target_platform is not None:
            brief["target_platform"] = target_platform

        _save_brief_state(brief)

    return {"status": "success", "brief": brief}


def update_project_brief(
    genre: str | None = None,
    art_style: str | None = None,
    tone: str | None = None,
    target_platform: str | None = None,
) -> dict:
    """Atualiza campos especificos do brief sem sobrescrever os demais.

    Campos nao informados (None) mantem o valor atual.
    Nunca exige force — e update parcial por definicao.

    Args:
        genre: Genero do jogo. Validado contra GAME_PATTERNS.
        art_style: Estilo visual.
        tone: Tom do jogo.
        target_platform: Plataforma alvo. Validado contra lista fixa.

    Returns:
        {"status": "success", "brief": {...}} ou {"status": "error", "message": str}
    """
    from tools.config_lock import BRIEF_STATE_LOCK

    # Valida genre (compartilhado com set_project_brief)
    canonical_genre = None
    if genre is not None:
        canonical_genre = _validate_genre(genre)
        if canonical_genre is None:
            try:
                from resources.game_patterns import GAME_PATTERNS
                valid = sorted(GAME_PATTERNS.keys())
            except Exception:
                valid = ["(erro ao carregar GAME_PATTERNS)"]
            return {
                "status": "error",
                "message": f"Genero '{genre}' invalido. Generos validos: {', '.join(valid)}.",
            }

    # Valida target_platform (compartilhado com set_project_brief)
    if target_platform is not None and not _validate_platform(target_platform):
        return {
            "status": "error",
            "message": f"Plataforma '{target_platform}' invalida. Validas: {', '.join(sorted(VALID_PLATFORMS))}.",
        }

    with BRIEF_STATE_LOCK:
        brief = _load_brief_state()

        if canonical_genre:
            brief["genre"] = canonical_genre
        if art_style is not None:
            brief["art_style"] = art_style
        if tone is not None:
            brief["tone"] = tone
        if target_platform is not None:
            brief["target_platform"] = target_platform

        _save_brief_state(brief)

    return {"status": "success", "brief": brief}


def get_project_brief() -> dict:
    """Retorna o project brief atual do projeto ativo.

    Se nunca foi configurado, retorna brief=null e configured=False.

    Usa BRIEF_STATE_LOCK para evitar leitura parcial durante escrita concorrente.

    Returns:
        {"status": "success", "brief": {...} | null, "configured": bool}
    """
    from tools.config_lock import BRIEF_STATE_LOCK

    with BRIEF_STATE_LOCK:
        brief = _load_brief_state()

    if not brief:
        return {"status": "success", "brief": None, "configured": False}

    return {"status": "success", "brief": brief, "configured": True}
