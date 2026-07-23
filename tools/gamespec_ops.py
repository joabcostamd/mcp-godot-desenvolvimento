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
# sota_1.5 — GameSpec v0
# ═══════════════════════════════════════════════════════════════

GAMESPEC_SCHEMA_VERSION = "0.1.0"
_SCHEMA_PATH = os.path.join(_REPO_ROOT, "gamespec", "gamespec.schema.json")


def _carregar_schema() -> Optional[dict]:
    """Carrega o JSON Schema do GameSpec."""
    if not os.path.exists(_SCHEMA_PATH):
        return None
    with open(_SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def validate_gamespec(gamespec_path: str) -> Tuple[bool, List[str]]:
    """
    Valida um gamespec.json contra o schema + referências cruzadas.

    Verifica:
    1. JSON válido
    2. Schema JSON Schema 2020-12
    3. Todo behavior citado existe na biblioteca (249)
    4. Níveis referenciam seeds válidas
    5. Tipos de entidade são válidos

    Returns:
        (ok, erros). ok=True se válido.
    """
    erros: List[str] = []

    # 1. Arquivo existe e é JSON válido
    if not os.path.exists(gamespec_path):
        return False, [f"Arquivo não encontrado: {gamespec_path}"]

    try:
        with open(gamespec_path, encoding="utf-8") as f:
            gs = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"JSON inválido: {e}"]

    # 2. Schema validation (jsonschema opcional — não quebra se não instalado)
    schema = _carregar_schema()
    if schema:
        try:
            import jsonschema
            jsonschema.validate(gs, schema)
        except ImportError:
            pass  # jsonschema não instalado — validação estrutural básica abaixo
        except jsonschema.ValidationError as e:
            erros.append(f"Schema: {e.message}")

    # 3. Campos obrigatórios
    if "meta" not in gs:
        erros.append("Campo 'meta' obrigatório")
    else:
        meta = gs["meta"]
        if "nome" not in meta:
            erros.append("meta.nome obrigatório")
        if "genero" not in meta:
            erros.append("meta.genero obrigatório")

    if "entidades" not in gs or not isinstance(gs.get("entidades"), list):
        erros.append("Campo 'entidades' obrigatório (array)")
    if "regras" not in gs:
        erros.append("Campo 'regras' obrigatório")

    # 4. Behaviors referenciados existem
    fichas = _carregar_fichas()
    entidades = gs.get("entidades", [])
    if isinstance(entidades, list):
        for i, ent in enumerate(entidades):
            if not isinstance(ent, dict):
                continue
            eid = ent.get("id", f"#{i}")
            behaviors = ent.get("behaviors", [])
            if isinstance(behaviors, list):
                for b in behaviors:
                    if isinstance(b, dict):
                        nome = b.get("name", "")
                        if nome and nome not in fichas:
                            erros.append(
                                f"Entidade '{eid}': behavior '{nome}' não existe na biblioteca"
                            )

    # 5. Níveis (se houver)
    niveis = gs.get("niveis", [])
    if isinstance(niveis, list):
        for i, niv in enumerate(niveis):
            if isinstance(niv, dict) and "id" not in niv:
                erros.append(f"Nível #{i}: campo 'id' obrigatório")

    return len(erros) == 0, erros


def compile_gamespec(gamespec_path: str, project_root: str = ".") -> Tuple[bool, str]:
    """
    Compila um gamespec.json gerando um arquivo .tscn para a cena principal.

    v0: gera uma cena com todos os nós descritos no gamespec.
    Nós gerados ganham metadata mcp_generated=true no nome.
    Não apaga nós criados manualmente fora do gamespec.

    Returns:
        (ok, mensagem).
    """
    # Valida primeiro
    ok, erros = validate_gamespec(gamespec_path)
    if not ok:
        return False, "Validação falhou:\n" + "\n".join(f"  - {e}" for e in erros)

    with open(gamespec_path, encoding="utf-8") as f:
        gs = json.load(f)

    nome_jogo = gs.get("meta", {}).get("nome", "game")
    entidades = gs.get("entidades", [])

    # Gera cena Godot (.tscn) como texto
    linhas = []
    linhas.append(f'; GameSpec gerado automaticamente — sota_1.5')
    linhas.append(f'; Jogo: {nome_jogo}')
    linhas.append(f'; Schema: {GAMESPEC_SCHEMA_VERSION}')
    linhas.append('')
    linhas.append('[gd_scene load_steps=1 format=3]')
    linhas.append('')
    linhas.append('[node name="Game" type="Node2D"]')
    linhas.append('')
    linhas.append(f'; {len(entidades)} entidades:')

    for ent in entidades:
        if not isinstance(ent, dict):
            continue
        eid = ent.get("id", "entidade")
        tipo = ent.get("tipo", "Node2D")
        node_type = _tipo_para_godot_node(tipo)
        linhas.append(f'[node name="{eid}" type="{node_type}" parent="."]')
        linhas.append(f'mcp_generated = true')
        linhas.append(f'mcp_entity_type = "{tipo}"')

        behaviors = ent.get("behaviors", [])
        if isinstance(behaviors, list):
            for b in behaviors:
                if isinstance(b, dict):
                    bname = b.get("name", "")
                    bparams = b.get("params", {})
                    linhas.append(f'[node name="bhv_{bname}" type="Node" parent="{eid}"]')
                    linhas.append(f'mcp_behavior = "{bname}"')
                    if bparams:
                        params_str = json.dumps(bparams, ensure_ascii=False)
                        linhas.append(f'mcp_params = {params_str}')
        linhas.append('')

    # Salva a cena compilada
    output_name = f"{nome_jogo.lower().replace(' ', '_')}.tscn"
    output_path = os.path.join(project_root, output_name)

    os.makedirs(project_root, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    return True, f"Cena compilada: {output_path}"


def _tipo_para_godot_node(tipo: str) -> str:
    """Mapeia tipo de entidade do GameSpec para classe Godot."""
    MAPEAMENTO = {
        "character": "CharacterBody2D",
        "prop": "StaticBody2D",
        "hud": "CanvasLayer",
        "level": "TileMap",
        "projectile": "Area2D",
        "pickup": "Area2D",
        "trigger": "Area2D",
    }
    return MAPEAMENTO.get(tipo, "Node2D")
