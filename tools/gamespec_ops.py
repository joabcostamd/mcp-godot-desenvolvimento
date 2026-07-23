"""
tools/gamespec_ops.py — Operações de GameSpec (sota_1.5 + sota_1.6).

sota_1.6: check_conflicts() — verifica conflitos ANTES de anexar behavior.
sota_1.5: validate_gamespec(), compile_gamespec() — DSL do jogo (futuro).

Fonte: SOTA_01_FUNDACAO_CEREBRO.md, seção sota_1.6.
"""

import json
import os
import glob
import threading
from typing import Any, List, Dict, Optional, Tuple

# Raiz do repositório (2 níveis acima de tools/)
_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

# Cache em memória das fichas de behavior (thread-safe)
_BEHAVIOR_CACHE: Optional[Dict[str, Dict[str, Any]]] = None
_CACHE_LOCK = threading.Lock()


def _carregar_fichas() -> Dict[str, Dict[str, Any]]:
    """Carrega todos os behavior.json em cache. Thread-safe. Usa path absoluto via __file__."""
    global _BEHAVIOR_CACHE
    if _BEHAVIOR_CACHE is not None:
        return _BEHAVIOR_CACHE

    with _CACHE_LOCK:
        # Double-check dentro do lock
        if _BEHAVIOR_CACHE is not None:
            return _BEHAVIOR_CACHE

        fichas: Dict[str, Dict[str, Any]] = {}
        pattern = os.path.join(_REPO_ROOT, "behaviors", "*", "behavior.json")
        for path in sorted(glob.glob(pattern)):
            name = os.path.basename(os.path.dirname(path))
            if name.startswith("_"):
                continue
            try:
                with open(path, encoding="utf-8") as f:
                    fichas[name] = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                import sys
                print(f"[AVISO] Behavior '{name}' ignorado: {e}", file=sys.stderr)
                continue

        _BEHAVIOR_CACHE = fichas
        return fichas


def invalidar_cache() -> None:
    """Força recarga do cache de fichas na próxima chamada."""
    global _BEHAVIOR_CACHE
    with _CACHE_LOCK:
        _BEHAVIOR_CACHE = None


# ═══════════════════════════════════════════════════════════════
# sota_1.6 — Matriz de conflito executável
# ═══════════════════════════════════════════════════════════════

def check_conflicts(
    behavior_novo: str,
    behaviors_existentes: List[str],
) -> Tuple[bool, str]:
    """
    Verifica se behavior_novo conflita com algum behavior já presente.

    Args:
        behavior_novo: Nome do behavior a ser anexado.
        behaviors_existentes: Lista de behaviors já na entidade.

    Returns:
        (ok, mensagem) — ok=True se não há conflito.
        Se ok=False, mensagem contém explicação em PT e alternativa via combina_bem.
    """
    fichas = _carregar_fichas()

    # ── Validação: behavior_novo existe ──
    if behavior_novo not in fichas:
        return False, (
            f"Behavior '{behavior_novo}' não encontrado na biblioteca. "
            f"Verifique o nome ou rode tool_catalog para listar os disponíveis."
        )

    ficha_novo = fichas[behavior_novo]
    conflicts_do_novo = ficha_novo.get("conflicts", [])
    if not isinstance(conflicts_do_novo, list):
        conflicts_do_novo = []

    # ── Verifica conflitos declarados ──
    for existente in behaviors_existentes:
        if existente not in fichas:
            continue  # behavior inexistente na biblioteca — ignora

        ficha_existente = fichas[existente]
        conflicts_do_existente = ficha_existente.get("conflicts", [])
        if not isinstance(conflicts_do_existente, list):
            conflicts_do_existente = []

        # bidirecional: A conflita com B OU B conflita com A
        if existente in conflicts_do_novo or behavior_novo in conflicts_do_existente:
            alternativa = _sugerir_alternativa(behavior_novo, ficha_novo)
            return False, (
                f"Conflito: '{behavior_novo}' não pode ser anexado porque "
                f"conflita com '{existente}' já presente na entidade."
                + (f"\nAlternativa: '{alternativa}' combina bem com '{behavior_novo}'."
                   if alternativa else "")
            )

    return True, ""


def _sugerir_alternativa(behavior: str, ficha: dict) -> str:
    """Sugere um behavior alternativo a partir de combina_bem, que também não conflita."""
    combina = ficha.get("combina_bem", [])
    if not isinstance(combina, list) or not combina:
        return ""
    conflicts = ficha.get("conflicts", [])
    if not isinstance(conflicts, list):
        conflicts = []
    # Pula alternativas que também conflitam
    for alt in combina:
        if alt not in conflicts:
            return alt
    # Se todas conflitam, retorna a primeira mesmo assim
    return combina[0]


def listar_conflitos_do_projeto(
    behaviors_no_projeto: List[str],
) -> List[Tuple[str, str, str]]:
    """
    Lista todos os conflitos entre behaviors de um projeto.

    Returns:
        Lista de (behavior_a, behavior_b, motivo).
    """
    fichas = _carregar_fichas()
    conflitos: List[Tuple[str, str, str]] = []

    for i, a in enumerate(behaviors_no_projeto):
        for b in behaviors_no_projeto[i + 1:]:
            if a not in fichas or b not in fichas:
                continue
            fa, fb = fichas[a], fichas[b]
            if b in fa.get("conflicts", []) or a in fb.get("conflicts", []):
                conflitos.append((a, b, "conflito declarado nas fichas"))

    return conflitos


# ═══════════════════════════════════════════════════════════════
# sota_1.5 — GameSpec v0 (stubs, implementação completa depois)
# ═══════════════════════════════════════════════════════════════

GAMESPEC_SCHEMA_VERSION = "0.1.0"


def validate_gamespec(gamespec_path: str) -> Tuple[bool, List[str]]:
    """
    Valida um gamespec.json contra o schema e referências cruzadas.

    Returns:
        (ok, erros). ok=True se válido.
    """
    # Stub — implementação completa em sota_1.5
    if not os.path.exists(gamespec_path):
        return False, [f"Arquivo não encontrado: {gamespec_path}"]

    try:
        with open(gamespec_path, encoding="utf-8") as f:
            json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"JSON inválido: {e}"]

    return True, []


def compile_gamespec(gamespec_path: str, project_root: str) -> Tuple[bool, str]:
    """
    Compila um gamespec.json nas cenas do projeto Godot.

    Raises:
        NotImplementedError: Esta função é um stub para implementação em sota_1.5.
    """
    raise NotImplementedError(
        "compile_gamespec() ainda não implementado — previsto para sota_1.5. "
        f"Gamespec: {gamespec_path}"
    )
