"""core/intent_router.py — Intent Router (Etapa A4).

Roteia linguagem natural (PT-BR ou EN) para chamadas de ferramenta.
Pipeline: classify → route → extract → invoke.

Meta: `godot(action="criar inimigo com patrulha")` — 1 chamada resolve tudo.

Arquitetura:
    1. INTENT_PATTERNS: ~100 regras regex mapeando NL → (tool, op, param_extractors)
    2. classify_intent(): match contra padrões, retorna best match com score
    3. route_intent(): resolve (tool_name, op, params) do match
    4. invoke_intent(): chama o handler real via _smart_call
    5. godot_handler(): entry point único — action: str → resultado
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Callable

logger = logging.getLogger("mcp-godot.intent_router")

# ══════════════════════════════════════════════════════════════
# Intent Pattern: (regex, tool_name, op, param_map, score_bonus)
#
# param_map: dict mapping regex group names → param names
#   ou Callable[[re.Match], dict] para extração customizada
# ══════════════════════════════════════════════════════════════

IntentRule = tuple[str, str, str, dict[str, str] | Callable | None, int]

# ── Helpers para construção de padrões ──

def _opt(pt: str, en: str) -> str:
    """Grupo opcional PT|EN."""
    return f"(?:{pt}|{en})"

def _grp(name: str, pt: str, en: str) -> str:
    """Grupo nomeado que captura PT ou EN."""
    return f"(?P<{name}>{pt}|{en})"

def _name(pt: str = r'["\']?([\w\sà-ú\-]+)["\']?', en: str = r'["\']?([\w\s\-]+)["\']?') -> str:
    """Captura um nome/identificador."""
    return f"(?P<name>{pt if 'à' in pt else en})"

def _path() -> str:
    """Captura um caminho de arquivo."""
    return r'(?P<path>res://[\w/\-_.]+)'

def _type() -> str:
    """Captura um tipo de nó."""
    return r'(?P<node_type>[A-Z]\w*(?:2D|3D)?)'


# ══════════════════════════════════════════════════════════════
# INTENT PATTERNS (~100 regras PT + EN)
# Ordem importa: patterns mais específicos PRIMEIRO
# ══════════════════════════════════════════════════════════════

INTENT_PATTERNS: list[IntentRule] = [
    # ─────────────── CENA (scene_manage) ───────────────
    # Ordem: padrões mais específicos PRIMEIRO (type + name antes de name-only)
    (
        r'(?:criar|cria|create|make)\s+(?:uma\s+|a\s+)?(?:cena|scene)\s+(?P<root_type>\w+)\s+(?:chamada|nomeada|com\snome\s+|named\s+)?(?P<name>[\w\sà-ú]+)',
        "scene_manage", "create",
        {"name": "name", "root_type": "root_type"}, 3
    ),
    (
        r'(?:criar|cria|create|make)\s+(?:uma\s+|a\s+)?(?:nova\s+|new\s+)?(?:cena|scene)\s+(?:chamada|nomeada|com\snome\s+|named\s+)?(?P<name>[\w\sà-ú]+?)(?:\s+(?:do\s+tipo|of\s+type|type)\s+(?P<root_type>\w+))?\s*$',
        "scene_manage", "create",
        {"name": "name", "root_type": "root_type"}, 2
    ),
    (
        r'(?:carregar|carregue|load|open)\s+(?:a\s+)?(?:árvore|arvore|tree|estrutura)\s+(?:da\s+)?(?:cena|scene)\s+(?P<name>[\w\sà-ú/_.]+)',
        "scene_manage", "load_tree",
        {"name": "name"}, 1
    ),
    (
        r'(?:instanciar|instancie|instance)\s+(?:a\s+)?(?:cena|scene)\s+(?P<name>[\w\sà-ú/_.]+)',
        "scene_manage", "instance",
        {"name": "name"}, 1
    ),
    # Fallback: "criar cena" sem detalhes → scene_manage.create genérico
    (
        r'(?:criar|cria|create|make)\s+(?:uma\s+|a\s+)?(?:nova\s+|new\s+)?(?:cena|scene)\s*$',
        "scene_manage", "create",
        {}, 0
    ),

    # ─────────────── NÓ (node_manage) ───────────────
    (
        r'(?:adicionar|adicione|add|create)\s+(?:um\s+)?(?:nó|no|node)\s+(?:do\s+tipo\s+)?(?P<node_type>[A-Z]\w*(?:2D|3D)?)(?:\s+(?:chamado|nomeado|com\s+nome\s+)?(?P<name>[\w\sà-ú]+))?(?:\s+(?:em|na|no|na\s+cena|em\s+cena)\s+(?P<scene_path>[\w/_.à-ú]+))?',
        "node_manage", "create",
        {"node_type": "node_type", "name": "name", "scene_path": "scene_path"}, 3
    ),
    (
        r'(?:remover|remova|delete|remove)\s+(?:o\s+)?(?:nó|no|node)\s+(?P<name>[\w\sà-ú/_.]+)',
        "node_manage", "delete",
        {"name": "name"}, 2
    ),
    (
        r'(?:definir|defina|set|configurar|configure)\s+(?:a\s+)?propriedade\s+(?P<prop>\w+)\s+(?:de|do|da|no|em)\s+(?P<name>[\w\sà-ú/_.]+)\s+(?:para|como|com\s+valor\s+)?(?P<value>.+)',
        "node_manage", "set_property",
        {"prop": "prop", "name": "name", "value": "value"}, 2
    ),
    (
        r'(?:conectar|conecte|connect)\s+(?:o\s+)?sinal\s+(?P<signal>\w+)\s+(?:de|do|da)\s+(?P<from_node>[\w\sà-ú/_.]+)\s+(?:ao|para|a|no|em)\s+(?P<to_node>[\w\sà-ú/_.]+)',
        "node_manage", "connect_signal",
        {"signal": "signal", "from_node": "from_node", "to_node": "to_node"}, 2
    ),
    (
        r'(?:listar|liste|list)\s+(?:os\s+)?sinais\s+(?:de|do|da)\s+(?P<name>[\w\sà-ú/_.]+)',
        "node_manage", "list_signals",
        {"name": "name"}, 1
    ),

    # ─────────────── SCRIPT (script_manage) ───────────────
    (
        r'(?:gerar|gere|generate|create)\s+(?:um\s+|a\s+)?(?:script|gdscript|código|codigo)\s+(?:para\s+|for\s+)?(?P<name>[\w\sà-ú]+?)(?:\s+(?:do\s+tipo\s+|of\s+type\s+)?(?P<template>\w+))?\s*$',
        "script_manage", "generate",
        {"name": "name", "template": "template"}, 2
    ),
    # EN word order: "generate player script" (verb + name + script)
    (
        r'(?:gerar|gere|generate|create)\s+(?P<name>[\w\sà-ú]+?)\s+(?:script|gdscript|código|codigo)\s*$',
        "script_manage", "generate",
        {"name": "name"}, 2
    ),
    (
        r'(?:anexar|anexe|attach)\s+(?:o\s+)?script\s+(?P<name>[\w\sà-ú/_.]+)\s+(?:ao|no|em)\s+(?P<target>[\w\sà-ú/_.]+)',
        "script_manage", "attach",
        {"name": "name", "target": "target"}, 2
    ),
    (
        r'(?:validar|valide|validate)\s+(?:o\s+)?(?:script|sintaxe|código|codigo)\s+(?P<name>[\w\sà-ú/_.]+)',
        "script_manage", "validate",
        {"name": "name"}, 1
    ),
    (
        r'(?:adicionar|adicione|add)\s+(?:uma\s+)?(?:variável|variavel|variable)\s+(?P<var_name>\w+)\s+(?:ao|no|em)\s+(?P<name>[\w\sà-ú/_.]+)',
        "script_manage", "add_var",
        {"var_name": "var_name", "name": "name"}, 2
    ),

    # ─────────────── ARQUIVO (file_manage + read/write) ───────────────
    (
        r'(?:ler|leia|read)\s+(?:o\s+)?(?:arquivo|file)\s+(?P<name>[\w\sà-ú/_.]+)',
        "read_file", "",
        {"name": "name"}, 1
    ),
    (
        r'(?:escrever|escreva|write)\s+(?:no|em|o)\s+(?:arquivo|file)\s+(?P<name>[\w\sà-ú/_.]+)',
        "write_file", "",
        {"name": "name"}, 1
    ),
    (
        r'(?:deletar|delete|remover|remove)\s+(?:o\s+)?(?:arquivo|file)\s+(?P<name>[\w\sà-ú/_.]+)',
        "file_manage", "delete",
        {"name": "name"}, 1
    ),
    (
        r'(?:inspecionar|inspecione|inspect|listar|liste|list)\s+(?:o\s+)?(?:projeto|project|arquivos|files)',
        "file_manage", "inspect",
        {}, 1
    ),

    # ─────────────── PROJETO (project_manage) ───────────────
    (
        r'(?:criar|cria|create|make)\s+(?:um\s+)?(?:novo\s+)?projeto\s+(?:godot\s+)?(?P<name>[\w\sà-ú]+)',
        "project_manage", "create",
        {"name": "name"}, 2
    ),
    (
        r'(?:definir|defina|set)\s+(?:o\s+)?projeto\s+(?:ativo|atual|active|current)\s+(?:como\s+)?(?P<name>[\w\sà-ú/_.]+)',
        "project_manage", "set_active",
        {"name": "name"}, 1
    ),
    (
        r'(?:definir|defina|set)\s+(?:a\s+)?cena\s+(?:principal|main)\s+(?:como\s+)?(?P<name>[\w\sà-ú/_.]+)',
        "project_manage", "set_main_scene",
        {"name": "name"}, 1
    ),

    # ─────────────── ASSETS ───────────────
    (
        r'(?:importar|importe|import)\s+(?:uma\s+)?(?:textura|texture|imagem|image)\s+(?P<name>[\w\sà-ú/_.]+)',
        "asset_manage", "import_texture",
        {"name": "name"}, 1
    ),
    (
        r'(?:importar|importe|import)\s+(?:um\s+)?(?:áudio|audio|som|sound)\s+(?P<name>[\w\sà-ú/_.]+)',
        "asset_manage", "import_audio",
        {"name": "name"}, 1
    ),
    (
        r'(?:gerar|gere|generate)\s+(?:um\s+)?(?:placeholder|place holder|sprite\s+placeholder)\s+(?:para\s+)?(?P<name>[\w\sà-ú]+)',
        "asset_manage", "placeholder_sprite",
        {"name": "name"}, 1
    ),
    (
        r'(?:gerar|gere|generate)\s+(?:uma\s+)?(?:paleta|palette|palheta)\s+(?:de\s+cores\s+)?(?P<name>[\w\sà-ú]+)',
        "asset_manage", "palette",
        {"name": "name"}, 1
    ),
    (
        r'(?:gerar|gere|generate)\s+(?:um\s+)?(?:fundo|background|bg)\s+(?:em\s+)?(?:gradiente|gradient)\s+(?P<name>[\w\sà-ú]+)',
        "asset_manage", "bg_gradient",
        {"name": "name"}, 1
    ),

    # ─────────────── FÍSICA (physics_manage) ───────────────
    (
        r'(?:adicionar|adicione|add)\s+(?:uma\s+|a\s+)?(?:colisão|colisao|collision|collider)\s+(?:em|no|na|para|ao|to)\s+(?P<name>[\w\sà-ú]+)',
        "physics_manage", "add_collision",
        {"name": "name"}, 2
    ),
    (
        r'(?:definir|defina|set)\s+(?:as\s+)?(?:camadas|layers|máscara|mascara|mask)\s+(?:de\s+)?(?:colisão|colisao|collision)\s+(?:de|do|da|para|em)\s+(?P<name>[\w\sà-ú]+)',
        "physics_manage", "set_layers",
        {"name": "name"}, 1
    ),

    # ─────────────── UI ───────────────
    (
        r'(?:criar|cria|create|make)\s+(?:um\s+)?(?:menu\s+principal|main\s+menu)',
        "ui_manage", "main_menu",
        {}, 2
    ),
    (
        r'(?:criar|cria|create|make)\s+(?:um\s+)?(?:hud|heads.up.display)',
        "ui_manage", "hud",
        {}, 2
    ),
    (
        r'(?:criar|cria|create|make)\s+(?:um\s+)?(?:menu\s+de\s+pausa|pause\s+menu)',
        "ui_manage", "pause_menu",
        {}, 2
    ),
    (
        r'(?:criar|cria|create|make)\s+(?:uma\s+)?(?:barra\s+de\s+vida|health\s+bar)',
        "ui_manage", "health_bar",
        {}, 2
    ),
    (
        r'(?:criar|cria|create|make)\s+(?:uma\s+)?(?:tela\s+de\s+carregamento|loading\s+screen)',
        "ui_manage", "loading_screen",
        {}, 2
    ),

    # ─────────────── RUNTIME ───────────────
    (
        r'(?:compilar|compile|build)\s+(?:o\s+)?(?:projeto|project|jogo|game)',
        "runtime_manage", "compile",
        {}, 1
    ),
    (
        r'(?:rodar|rode|run|executar|execute|iniciar|inicie|start|launch)\s+(?:o\s+|a\s+|the\s+)?(?:projeto|project|jogo|game)',
        "runtime_manage", "run",
        {}, 2
    ),
    (
        r'(?:parar|pare|stop)\s+(?:o\s+|a\s+|the\s+)?(?:projeto|project|jogo|game)',
        "runtime_manage", "stop",
        {}, 1
    ),
    (
        r'(?:reiniciar|reinicia|restart)\s+(?:o\s+|a\s+|the\s+)?(?:projeto|project|jogo|game)',
        "runtime_manage", "restart",
        {}, 1
    ),
    (
        r'(?:abrir|abra|open|launch)\s+(?:o\s+)?(?:editor|godot)',
        "runtime_manage", "launch_editor",
        {}, 1
    ),

    # ─────────────── CÂMERA ───────────────
    (
        r'(?:configurar|configure|setup)\s+(?:a\s+)?(?:câmera|camera|cam)\s+(?:2d|2D)',
        "camera_manage", "setup_2d",
        {}, 1
    ),
    (
        r'(?:a\s+)?(?:câmera|camera|cam)\s+(?:segue|seguir|follow|siga)\s+(?:o\s+)?(?P<name>[\w\sà-ú]+)',
        "camera_manage", "follow",
        {"name": "name"}, 2
    ),
    (
        r'(?:adicionar|adicione|add)\s+(?:shake|tremor|tremer)\s+(?:na|a|à)\s+(?:câmera|camera|cam)',
        "camera_manage", "shake",
        {}, 1
    ),

    # ─────────────── ANIMAÇÃO ───────────────
    (
        r'(?:criar|cria|create)\s+(?:uma\s+)?(?:animação|animacao|animation)\s+(?:chamada\s+)?(?P<name>[\w\sà-ú]+)',
        "anim_manage", "create_clip",
        {"name": "name"}, 2
    ),
    (
        r'(?:criar|cria|create)\s+(?:um\s+)?(?:animation\s*player|player\s+de\s+anima[cç][aã]o)',
        "anim_manage", "create_player",
        {}, 1
    ),

    # ─────────────── ÁUDIO ───────────────
    (
        r'(?:gerar|gere|generate)\s+(?:um\s+)?(?:som|sfx|áudio|audio|efeito\s+sonoro)\s+(?:para\s+)?(?P<name>[\w\sà-ú]+)',
        "audio_manage", "generate_sfx_batch",
        {"name": "name"}, 1
    ),
    (
        r'(?:configurar|configure|setup)\s+(?:o\s+)?(?:áudio|audio|bus|barramento)\s+(?P<name>[\w\sà-ú]+)',
        "audio_manage", "config_bus",
        {"name": "name"}, 1
    ),

    # ─────────────── TILEMAP ───────────────
    (
        r'(?:criar|cria|create)\s+(?:um\s+)?(?:tileset|tile\s*set)',
        "tilemap_manage", "create_tileset",
        {}, 1
    ),
    (
        r'(?:criar|cria|create)\s+(?:uma\s+)?(?:camada|layer)\s+(?:de\s+)?(?:tilemap|tile\s*map)',
        "tilemap_manage", "create_layer",
        {}, 1
    ),
    (
        r'(?:pintar|pinte|paint)\s+(?:uma\s+)?(?:célula|celula|cell|tile)\s+(?:em|no|na)\s+(?P<x>\d+)\s*[,x]\s*(?P<y>\d+)',
        "tilemap_manage", "paint_cell",
        {"x": "x", "y": "y"}, 1
    ),

    # ─────────────── INIMIGO / ENTIDADE ───────────────
    (
        r'(?:criar|cria|create|make)\s+(?:um\s+)?(?:inimigo|enemy|monstro|monster)\s+(?:com\s+)?(?P<behavior>patrulha|patrol|chase|persegui[cç][aã]o|idle|parado)',
        "create_entity", "",
        {"name": "enemy", "entity_type": "enemy", "behavior": "behavior"}, 3
    ),
    (
        r'(?:criar|cria|create|make)\s+(?:um\s+)?(?:jogador|player|heroi|herói)',
        "create_entity", "",
        {"name": "player", "entity_type": "player"}, 2
    ),
    (
        r'(?:criar|cria|create|make)\s+(?:um\s+)?(?:item|coletável|coletavel|collectible|powerup)\s+(?P<name>[\w\sà-ú]+)',
        "create_entity", "",
        {"name": "name", "entity_type": "item"}, 2
    ),
    (
        r'(?:criar|cria|create|make)\s+(?:um\s+)?(?:projétil|projetil|projectile|bala|bullet)\s+(?P<name>[\w\sà-ú]+)',
        "create_entity", "",
        {"name": "name", "entity_type": "projectile"}, 2
    ),

    # ─────────────── SISTEMA DE ARMAS ───────────────
    (
        r'(?:criar|cria|create)\s+(?:um\s+)?(?:sistema\s+de\s+)?(?:arma|gun|weapon)\s+(?P<name>[\w\sà-ú]+)',
        "create_gun_system", "",
        {"name": "name"}, 2
    ),

    # ─────────────── EXPORTAÇÃO ───────────────
    (
        r'(?:exportar|exporte|export|build)\s+(?:o\s+)?(?:projeto|project|jogo|game)',
        "export_manage", "build",
        {}, 1
    ),
    (
        r'(?:listar|liste|list)\s+(?:os\s+)?(?:presets|perfis)\s+(?:de\s+)?(?:exportação|exportacao|export)',
        "export_manage", "list_presets",
        {}, 1
    ),

    # ─────────────── GIT / SEGURANÇA ───────────────
    (
        r'(?:salvar|save|criar|create)\s+(?:um\s+)?(?:checkpoint|ponto\s+de\s+restaura[cç][aã]o|backup)',
        "safety_manage", "checkpoint",
        {}, 1
    ),
    (
        r'(?:desfazer|desfaça|undo|revert)\s+(?:a\s+)?(?:última|ultima|last)\s+(?:ação|acao|action|mudança|mudanca|change)',
        "safety_manage", "undo",
        {}, 1
    ),

    # ─────────────── DEBUG ───────────────
    (
        r'(?:ver|veja|show|exibir|exiba)\s+(?:a\s+)?(?:performance|perf|desempenho|fps)',
        "debug_manage", "perf_stats",
        {}, 1
    ),
    (
        r'(?:mostrar|exibir|show)\s+(?:as\s+)?(?:colisões|colisoes|collisions)',
        "debug_manage", "collision_debug",
        {}, 1
    ),

    # ─────────────── TESTES ───────────────
    (
        r'(?:rodar|rode|run|executar|execute)\s+(?:os\s+)?(?:testes|tests|gut)',
        "run_gut_tests", "",
        {}, 1
    ),
    (
        r'(?:verificar|verifique|check|assert)\s+(?:se\s+)?(?:o\s+)?(?:nó|no|node)\s+(?P<name>[\w\sà-ú/_.]+)\s+(?:existe|exists)',
        "test_manage", "assert_node",
        {"name": "name"}, 1
    ),

    # ─────────────── CONSULTA ───────────────
    (
        r'(?:o\s+que\s+(?:é|eh|são|sao)|what\s+(?:is|are)|explique|explain|descreva|describe)\s+(?:a\s+)?(?:classe|class)\s+(?P<name>[A-Z]\w*(?:2D|3D)?)',
        "query_classdb", "",
        {"name": "class_name"}, 1
    ),
    (
        r'(?:buscar|busque|search|find|procurar|procure)\s+(?:a\s+)?(?:classe|class)\s+(?P<name>\w+)',
        "search_classdb", "",
        {"name": "query"}, 1
    ),
    (
        r'(?:quais|que|what)\s+(?:são|sao|are)\s+(?:os\s+)?(?:tipos\s+de\s+)?(?:nós|nos|nodes)\s+(?:válidos|validos|valid|disponíveis|disponiveis|available)',
        "list_valid_node_types", "",
        {}, 1
    ),

    # ─────────────── NAVEGAÇÃO ───────────────
    (
        r'(?:criar|cria|create)\s+(?:uma\s+)?(?:região|regiao|region)\s+(?:de\s+)?(?:navegação|navegacao|navigation)',
        "navigation_manage", "create_region",
        {}, 1
    ),
    (
        r'(?:criar|cria|create)\s+(?:um\s+)?(?:agente|agent)\s+(?:de\s+)?(?:navegação|navegacao|navigation)',
        "navigation_manage", "create_agent",
        {}, 1
    ),

    # ─────────────── DIÁLOGO ───────────────
    (
        r'(?:criar|cria|create)\s+(?:um\s+)?(?:sistema\s+de\s+)?(?:diálogo|dialogo|dialogue|dialog)',
        "dialogue_manage", "create_system",
        {}, 2
    ),

    # ─────────────── INVENTÁRIO ───────────────
    (
        r'(?:criar|cria|create)\s+(?:um\s+)?(?:sistema\s+de\s+)?(?:inventário|inventario|inventory)',
        "inventory_manage", "create_system",
        {}, 2
    ),

    # ─────────────── GAME STATE ───────────────
    (
        r'(?:criar|cria|create)\s+(?:um\s+)?(?:sistema\s+de\s+)?(?:save|salvamento|game\s*state)',
        "gamestate_manage", "create_save",
        {}, 1
    ),
    (
        r'(?:criar|cria|create)\s+(?:uma\s+)?(?:máquina|maquina|machine)\s+(?:de\s+)?(?:estados|states|fsm|state\s*machine)',
        "gamestate_manage", "create_fsm",
        {}, 1
    ),

    # ─────────────── GAME BRIDGE ───────────────
    (
        r'(?:pausar|pause)\s+(?:o\s+)?jogo',
        "game_bridge_manage", "pause",
        {}, 1
    ),
    (
        r'(?:despausar|despause|unpause|continuar|continue|resume)\s+(?:o\s+)?jogo',
        "game_bridge_manage", "pause",
        {}, 1
    ),

    # ─────────────── FEEDBACK GENÉRICO ───────────────
    (
        r'(?:analisar|analise|analyze)\s+(?:o\s+)?(?:projeto|project|jogo|game)',
        "analysis_manage", "structure",
        {}, 1
    ),
    (
        r'(?:sugerir|sugira|suggest)\s+(?:próximos|proximos|next)\s+(?:passos|steps)',
        "analysis_manage", "next_steps",
        {}, 1
    ),
    (
        r'(?:estimar|estime|estimate)\s+(?:o\s+)?(?:escopo|scope)\s+(?:do\s+)?(?:projeto|project|jogo|game)',
        "analysis_manage", "estimate_scope",
        {}, 1
    ),
]


# ══════════════════════════════════════════════════════════════
# Pipeline: classify → route → extract
# ══════════════════════════════════════════════════════════════

def classify_intent(action: str) -> dict[str, Any]:
    """Classifica uma ação em linguagem natural contra os padrões.

    Args:
        action: Texto em PT-BR ou EN descrevendo a ação desejada.

    Returns:
        {
            "matched": bool,
            "tool": str,          # nome da tool
            "op": str,            # operação (vazio se tool não é rollup)
            "params": dict,       # parâmetros extraídos
            "confidence": float,  # 0.0–1.0
            "pattern": str,       # regex que deu match (para debug)
        }
    """
    action_lower = action.lower().strip()

    best_match = None
    best_score = -1

    for pattern, tool, op, param_map, bonus in INTENT_PATTERNS:
        match = re.search(pattern, action_lower, re.IGNORECASE)
        if not match:
            match = re.search(pattern, action, re.IGNORECASE)
        if not match:
            continue

        # Score: comprimento do match / comprimento do input + bônus
        match_len = match.end() - match.start()
        score = (match_len / max(len(action), 1)) * 5 + bonus

        if score > best_score:
            best_score = score
            best_match = (pattern, tool, op, param_map, match)

    if best_match is None:
        return {"matched": False, "tool": "", "op": "", "params": {}, "confidence": 0.0, "pattern": ""}

    _, tool, op, param_map, match = best_match

    # Extrair parâmetros
    params = _extract_params(match, param_map)

    # Confidence: score normalizado para 0.0–1.0
    confidence = min(best_score / 10.0, 1.0)

    return {
        "matched": True,
        "tool": tool,
        "op": op,
        "params": params,
        "confidence": round(confidence, 2),
        "pattern": best_match[0],
    }


def _extract_params(match: re.Match, param_map: dict[str, str] | Callable | None) -> dict[str, Any]:
    """Extrai parâmetros do match da regex.

    Dois modos, diferenciados pela presença da chave nos grupos da regex:

    1. EXTRACT mode (chave É um grupo nomeado):
       param_map = {regex_group: param_name}
       → extrai valor do match, armazena como param_name.
       Ex: {"behavior": "behavior"} → params["behavior"] = "patrol"

    2. STATIC mode (chave NÃO é um grupo nomeado):
       param_map = {param_name: default_value}
       → injeta o valor como default estático.
       Ex: {"entity_type": "enemy"} → params["entity_type"] = "enemy"

    Args:
        match: Objeto Match da regex.
        param_map: Mapeamento híbrido (grupo→param ou param→default).

    Returns:
        Dict de parâmetros prontos para passar ao handler.
    """
    if param_map is None:
        return {}

    if callable(param_map):
        return param_map(match)

    regex_groups = set(match.groupdict().keys()) if match.groupdict() else set()
    params: dict[str, Any] = {}

    for map_key, map_val in param_map.items():
        if map_key in regex_groups:
            # ── EXTRACT mode: map_key = regex_group, map_val = param_name ──
            try:
                value = match.group(map_key)
                if value:
                    value = value.strip().strip('"\'').strip()
                    value = _translate_value(map_val, value)
                    params[map_val] = value
            except (IndexError, AttributeError):
                pass
        else:
            # ── STATIC mode: map_key = param_name, map_val = default_value ──
            params[map_key] = _translate_value(map_key, map_val)

    return params


def _translate_value(param_name: str, value: str) -> str:
    """Traduz valores PT→EN para parâmetros de enum conhecidos."""
    translations = {
        "behavior": {
            "patrulha": "patrol", "patrol": "patrol",
            "perseguição": "chase", "perseguicao": "chase", "chase": "chase",
            "parado": "idle", "idle": "idle",
            "nenhum": "none", "none": "none",
        },
        "entity_type": {
            "inimigo": "enemy", "enemy": "enemy", "monstro": "enemy", "monster": "enemy",
            "jogador": "player", "player": "player", "heroi": "player", "herói": "player",
            "item": "item", "coletável": "item", "coletavel": "item", "collectible": "item",
            "projétil": "projectile", "projetil": "projectile", "projectile": "projectile",
            "bala": "projectile", "bullet": "projectile",
            "torre": "tower", "tower": "tower",
            "npc": "npc",
        },
        "root_type": {
            "node2d": "Node2D", "node 2d": "Node2D",
            "characterbody2d": "CharacterBody2D",
            "staticbody2d": "StaticBody2D",
            "rigidbody2d": "RigidBody2D",
            "area2d": "Area2D",
            "control": "Control",
            "node": "Node",
        },
    }

    if param_name in translations:
        return translations[param_name].get(value.lower(), value)
    return value


# ══════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════

def route_intent(action: str) -> dict[str, Any]:
    """Pipeline completo: classifica + extrai parâmetros.

    Args:
        action: Texto em PT-BR ou EN descrevendo a ação.

    Returns:
        Resultado da classificação + parâmetros extraídos.
    """
    result = classify_intent(action)

    if not result["matched"]:
        # Fallback: sugerir busca no catálogo
        return {
            "status": "unmatched",
            "message": f"Não entendi: '{action}'. Use tool_catalog para buscar ferramentas.",
            "suggestion": {
                "tool": "tool_catalog",
                "params": {"query": action, "limit": 5},
            },
        }

    return {
        "status": "matched",
        "tool": result["tool"],
        "op": result["op"],
        "params": result["params"],
        "confidence": result["confidence"],
    }


def invoke_intent(tool_name: str, op: str = "", params: dict | None = None) -> dict[str, Any]:
    """Invoca uma ferramenta pelo nome, resolvendo via _smart_call.

    Args:
        tool_name: Nome da tool (ex: 'scene_manage').
        op: Operação do rollup (vazio para tools atômicas).
        params: Parâmetros da tool.

    Returns:
        Resultado da invocação da tool.
    """
    from server import _build_handlers, _smart_call

    handlers = _build_handlers()
    handler = handlers.get(tool_name)
    if handler is None:
        return {"status": "error", "message": f"Tool '{tool_name}' não encontrada."}

    # Construir arguments
    args: dict[str, Any] = {}
    if op:
        args["op"] = op
        args["params"] = params or {}
    else:
        args = params or {}

    try:
        result = _smart_call(handler, args)
        if isinstance(result, dict):
            result.setdefault("status", "success")
        return result
    except Exception as e:
        logger.exception("Erro ao invocar %s/%s", tool_name, op)
        return {"status": "error", "message": str(e)}
