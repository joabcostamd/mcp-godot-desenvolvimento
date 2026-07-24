"""
Definições de tools em QUARENTENA — FASE 1 (2026-07-23).

Estas tools foram removidas do wire (tools/list) porque nunca foram
exercitadas por um jogo real. Continuam invocáveis via invoke_by_name
(fallback para QUARENTENA_HANDLERS neste arquivo).

Critério de saída da quarentena:
    Um jogo real precisou da capacidade + teste passa + tool volta ao wire.
"""

from mcp.types import Tool

# Tools movidas de core/tool_definitions.py em 2026-07-23
QUARENTENA_TOOL_DEFS: list[Tool] = []

# Handlers de fallback — invoke_by_name usa este dicionário quando
# o handler não está em _build_handlers() (tools removidas do wire).
# Cada handler faz lazy import do módulo original para evitar
# dependência circular no startup do servidor.
QUARENTENA_HANDLERS: dict[str, object] = {}

# ── capsule_generate_store_image ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="capsule_generate_store_image",
            description=(
                "Gera imagem de capsula para loja (Steam). "
                "Suporta 6 tamanhos: header (920x430), small (231x87), "
                "main (616x353), vertical (374x448), hero (3840x1240), logo (1280x720). "
                "Use para criar assets de marketing da pagina da loja. "
                "Exemplo: {'size': 'header', 'title': 'Meu Jogo', 'style': 'scifi'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "size": {"type": "string", "enum": ["header", "small", "main", "vertical", "hero", "logo"], "description": "Tamanho da capsula Steam."},
                    "title": {"type": "string", "description": "Titulo do jogo."},
                    "style": {"type": "string", "description": "Estilo visual."},
                    "background_color": {"type": "string", "description": "Cor de fundo em hex. Default: '#1a1a2e'."},
                },
                "required": [],
            },
        ),
)

# ── cloud_save_configure ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="cloud_save_configure",
            description=(
                "Configura sistema de Cloud Save (Steam Auto-Cloud ou local). "
                "Gera CloudSaveManager GDScript com save/load automático em user://. "
                "Use para persistir progresso do jogador na nuvem. "
                "Pre-condicoes: projeto ativo. "
                "Exemplo: {'save_slots': 3, 'auto_save_interval_sec': 60}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "save_slots": {"type": "integer", "description": "Numero de slots de save. Default: 3."},
                    "auto_save_interval_sec": {"type": "integer", "description": "Intervalo de auto-save em segundos. Default: 60."},
                    "cloud_provider": {"type": "string", "enum": ["steam", "local"], "description": "Provedor de cloud. Default: 'local'."},
                },
                "required": [],
            },
        ),
)

# ── community_manage ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="community_manage",
            description=(
                "👥 Ferramentas de comunidade (Gaps ONDA 4). "
                "changelog: gera CHANGELOG.md padrao Keep a Changelog. "
                "release_notes: gera notas de release para GitHub Releases. "
                "roadmap_public: gera ROADMAP.md publico. "
                "badge: retorna snippet do badge 'Made with MCP Godot Agent'. "
                "Exemplo: {\"op\": \"badge\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "op": {
                        "type": "string",
                        "description": "Operacao: 'changelog', 'release_notes', 'roadmap_public' ou 'badge'.",
                        "enum": ["changelog", "release_notes", "roadmap_public", "badge"],
                    },
                    "params": {
                        "type": "object",
                        "description": "Parametros. version (string): versao para release_notes.",
                    },
                },
                "required": [],
            },
        ),
)

# ── cutscene_add_camera_shot ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="cutscene_add_camera_shot",
            description=(
                "Adiciona um shot de camera a uma cutscene. "
                "Define alvo, transicao (cut, fade, dissolve, zoom, pan) e duracao. "
                "Use dentro de cutscene_create_timeline ou para editar timeline existente. "
                "Exemplo: {'target': 'Player', 'transition': 'fade', 'duration': 2.0}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Alvo da camera (node path ou nome)."},
                    "transition": {"type": "string", "enum": ["cut", "fade", "dissolve", "zoom_in", "zoom_out", "pan_left", "pan_right", "pan_up", "pan_down"], "description": "Tipo de transicao."},
                    "duration": {"type": "number", "description": "Duracao em segundos."},
                    "time_sec": {"type": "number", "description": "Timestamp de inicio do shot."},
                },
                "required": [],
            },
        ),
)

# ── cutscene_add_dialogue_event ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="cutscene_add_dialogue_event",
            description=(
                "Adiciona evento de dialogo a uma cutscene. "
                "Define falante, texto e duracao da exibicao. "
                "Use para inserir falas de NPCs ou narrador na timeline. "
                "Exemplo: {'speaker': 'Narrador', 'text': 'Era uma vez...', 'duration': 3.0}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "speaker": {"type": "string", "description": "Nome do falante."},
                    "text": {"type": "string", "description": "Texto do dialogo."},
                    "duration": {"type": "number", "description": "Duracao da exibicao em segundos."},
                    "time_sec": {"type": "number", "description": "Timestamp de inicio na timeline."},
                },
                "required": [],
            },
        ),
)

# ── cutscene_create_timeline ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="cutscene_create_timeline",
            description=(
                "Cria linha do tempo de cutscene com eventos sequenciais. "
                "Suporta shots de camera, dialogo, audio, animacao e esperas. "
                "Gera script GDScript com orquestracao de eventos. "
                "Use para criar cinematicas e cenas scriptadas. "
                "Exemplo: {'cutscene_name': 'intro', 'events': [{...}]}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "cutscene_name": {"type": "string", "description": "Nome da cutscene."},
                    "events": {"type": "array", "items": {"type": "object"}, "description": "Lista de eventos [{type, time_sec, params}]."},
                    "apply_to_project": {"type": "boolean", "description": "Salvar script no projeto. Default: false."},
                },
                "required": [],
            },
        ),
)

# ── mod_manifest_generate ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="mod_manifest_generate",
            description=(
                "Gera manifesto de mod (mod.json) para projetos Godot. "
                "Define nome, versao, dependencias e arquivos do mod. "
                "Use para criar sistema de modding no jogo. "
                "Pre-condicoes: nenhuma. "
                "Exemplo: {'mod_name': 'novas_armas', 'mod_version': '1.0.0', 'mod_author': 'Joab'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "mod_name": {"type": "string", "description": "Nome do mod."},
                    "mod_version": {"type": "string", "description": "Versao semver (ex: '1.0.0')."},
                    "mod_author": {"type": "string", "description": "Autor do mod."},
                    "mod_description": {"type": "string", "description": "Descricao do mod."},
                    "dependencies": {"type": "array", "items": {"type": "string"}, "description": "Mods requeridos."},
                    "target_game_version": {"type": "string", "description": "Versao do jogo compativel."},
                    "files": {"type": "array", "items": {"type": "string"}, "description": "Arquivos do mod."},
                },
                "required": [],
            },
        ),
)

# ── onboarding_check_first_experience ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="onboarding_check_first_experience",
            description=(
                "Verifica qualidade da primeira experiencia do jogador (FTUE). "
                "Avalia clareza do tutorial, tempo ate primeira acao, "
                "complexidade inicial, frustracao potencial. "
                "Use para garantir que novos jogadores nao desistem. "
                "Exemplo: {} (sem argumentos)."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
)

# ── onboarding_create_guided_tour ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="onboarding_create_guided_tour",
            description=(
                "Cria tour guiado pela UI do jogo. "
                "Sequencia de destaques que mostram cada elemento da interface. "
                "Use para primeira experiencia do jogador (FTUE). "
                "Exemplo: {'ui_elements': ['HUD/HealthBar', 'HUD/MiniMap', 'HUD/Inventory'], 'tour_name': 'primeira_partida'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "ui_elements": {"type": "array", "items": {"type": "string"}, "description": "Lista de node paths da UI."},
                    "tour_name": {"type": "string", "description": "Nome do tour. Default: 'guided_tour'."},
                    "apply_to_project": {"type": "boolean", "description": "Salvar script no projeto. Default: true."},
                },
                "required": [],
            },
        ),
)

# ── onboarding_create_tutorial_step ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="onboarding_create_tutorial_step",
            description=(
                "Cria passo de tutorial interativo com highlight e instrucao. "
                "Gera script GDScript que destaca no da UI, mostra texto e aguarda acao. "
                "Use para ensinar o jogador a jogar. "
                "Exemplo: {'steps': [{'target_node': 'HUD/Joystick', 'instruction': 'Use para mover', 'required_action': 'move'}]}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "steps": {"type": "array", "items": {"type": "object"}, "description": "Lista de passos [{target_node, instruction, required_action, highlight}]."},
                    "tutorial_name": {"type": "string", "description": "Nome do tutorial. Default: 'tutorial'."},
                    "apply_to_project": {"type": "boolean", "description": "Salvar script no projeto. Default: false."},
                },
                "required": [],
            },
        ),
)

# ── publish_manage ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="publish_manage",
            description=(
                "📦 Publicacao na AssetLib oficial do Godot (ONDA 4 — Fatia 4.A). "
                "Empacota addons em .zip pronto para submissao na godotengine.org/asset-library. "
                "Operacoes: package (gera .zip), validate (valida estrutura), "
                "metadata (gera JSON de metadados), preview (pre-visualiza sem gerar .zip). "
                "NAO faz upload automatico — o humano faz upload no site. "
                "Exemplo: {\"op\": \"package\", \"params\": {\"addon\": \"mcp_addon\"}}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "op": {
                        "type": "string",
                        "description": "Operacao: 'package', 'validate', 'metadata' ou 'preview'.",
                        "enum": ["package", "validate", "metadata", "preview"],
                    },
                    "params": {
                        "type": "object",
                        "description": (
                            "Parametros da operacao. Campos comuns: "
                            "addon (string, default 'mcp_addon'): qual addon empacotar. "
                            "include_license (bool, default true): incluir LICENSE no .zip "
                            "(apenas op='package')."
                        ),
                    },
                },
                "required": [],
            },
        ),
)

# ── remote_balance_config ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="remote_balance_config",
            description=(
                "Gerencia configuracao de balance remoto para ajustes pos-lancamento. "
                "Permite exportar, validar ou gerar template de balance JSON. "
                "Atualizavel sem patch (via arquivo remoto ou CDN). "
                "Use para ajustar numeros do jogo apos o lancamento. "
                "Exemplo: {'action': 'export', 'config': {'enemy_health_mult': 1.2}}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["export", "template", "validate"], "description": "Acao: export, template ou validate."},
                    "config": {"type": "object", "description": "Configuracao de balance (para validate)."},
                },
                "required": [],
            },
        ),
)

# ── telemetry_get_funnel ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="telemetry_get_funnel",
            description=(
                "Gera analise de funil (funnel analysis) dos eventos de telemetria. "
                "Mostra taxas de conversao entre etapas do jogo. "
                "Use para identificar onde jogadores desistem. "
                "Exemplo: {'funnel_steps': ['level_start', 'boss_encounter', 'level_complete']}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "funnel_steps": {"type": "array", "items": {"type": "string"}, "description": "Etapas do funil (eventos)."},
                    "session_id": {"type": "string", "description": "Filtrar por sessao especifica."},
                },
                "required": [],
            },
        ),
)

# ── telemetry_heatmap ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="telemetry_heatmap",
            description=(
                "Gera mapa de calor (heatmap) de eventos de jogo. "
                "Mostra onde jogadores morrem, coletam itens ou encontram bosses. "
                "Use para balanceamento de nivel e posicionamento de elementos. "
                "Exemplo: {'event_type': 'player_death', 'level': 'level_1'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "event_type": {"type": "string", "description": "Tipo de evento para heatmap."},
                    "level": {"type": "string", "description": "Nivel/fase para filtrar."},
                    "resolution": {"type": "integer", "description": "Resolucao do grid de calor. Default: 32."},
                },
                "required": [],
            },
        ),
)

# ── telemetry_session_summary ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="telemetry_session_summary",
            description=(
                "Resumo da sessao de jogo: tempo total, eventos, mortes, kills, itens. "
                "Use para analise pos-jogo ou debug de balanceamento. "
                "Exemplo: {'session_id': 'session_001'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "ID da sessao."},
                },
                "required": [],
            },
        ),
)

# ── telemetry_track_event ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="telemetry_track_event",
            description=(
                "Registra evento de telemetria COM opt-in explicito do jogador. "
                "Suporta 19 tipos de eventos: session, level, enemy, item, boss, menu, etc. "
                "Dados armazenados LOCALMENTE (user://) — sem envio externo. "
                "Pre-condicoes: opt_in=True obrigatorio. "
                "Exemplo: {'event_type': 'level_complete', 'opt_in': True}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "event_type": {"type": "string", "description": "Tipo do evento (ver doc para lista completa)."},
                    "event_data": {"type": "object", "description": "Dados adicionais do evento."},
                    "session_id": {"type": "string", "description": "ID da sessao atual."},
                    "opt_in": {"type": "boolean", "description": "Deve ser True para registrar. Default: False."},
                },
                "required": [],
            },
        ),
)

# ── trailer_capture_clip ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="trailer_capture_clip",
            description=(
                "Captura clipe de gameplay para trailer. "
                "Suporta specs por plataforma: Steam (1080p60), itch.io (720p30), YouTube. "
                "Inclui instrucoes de montagem com FFmpeg. "
                "Use para marketing e loja do jogo. "
                "Exemplo: {'target': 'steam', 'duration_sec': 30}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Cena a capturar."},
                    "duration_sec": {"type": "integer", "description": "Duracao em segundos. Default: 30."},
                    "target": {"type": "string", "enum": ["steam", "itch", "youtube"], "description": "Plataforma alvo."},
                    "action_sequence": {"type": "array", "items": {"type": "object"}, "description": "Inputs automatizados."},
                },
                "required": [],
            },
        ),
)

# ── trailer_render_sequence ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="trailer_render_sequence",
            description=(
                "Define sequencia de cenas para renderizacao de trailer. "
                "Planeja storyboard: quais cenas, ordem, duracao, acoes. "
                "Valida duracao total contra limite da plataforma. "
                "Use para planejar o trailer antes de capturar. "
                "Exemplo: {'shots': [{'scene': 'menu', 'duration_sec': 5}, ...]}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "shots": {"type": "array", "items": {"type": "object"}, "description": "Lista de cenas [{scene, duration_sec, description, inputs}]."},
                    "target": {"type": "string", "enum": ["steam", "itch", "youtube"], "description": "Plataforma alvo."},
                },
                "required": [],
            },
        ),
)

# ── validate_mod_compatibility ──
QUARENTENA_TOOL_DEFS.append(
        Tool(
            name="validate_mod_compatibility",
            description=(
                "Valida compatibilidade entre mods e jogo base. "
                "Verifica versao, dependencias, conflitos de arquivos e scripts de entrada. "
                "Use antes de carregar mods no jogo. "
                "Exemplo: {'mod_manifest': {...}, 'game_version': '1.0.0'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "mod_manifest": {"type": "object", "description": "Manifesto do mod (dict)."},
                    "game_version": {"type": "string", "description": "Versao atual do jogo."},
                    "loaded_mods": {"type": "array", "items": {"type": "object"}, "description": "Mods ja carregados."},
                },
                "required": [],
            },
        ),
)

# ── Handlers de fallback para invoke_by_name ────────────────────
# Cada handler faz lazy import do módulo original.

def _make_lazy_handler(module_path, func_name):
    def _handler(args):
        import importlib
        mod = importlib.import_module(module_path)
        func = getattr(mod, func_name)
        return func(args)
    return _handler

def _make_manage_handler(module_path, func_name, default_op='preview'):
    def _handler(args):
        import importlib
        mod = importlib.import_module(module_path)
        func = getattr(mod, func_name)
        op = args.get('op', default_op)
        params = args.get('params', {})
        return func(op=op, params=params)
    return _handler

QUARENTENA_HANDLERS = {
    'cloud_save_configure': _make_lazy_handler('tools.achievement_ops', 'cloud_save_configure'),
    'mod_manifest_generate': _make_lazy_handler('tools.mod_ops', 'mod_manifest_generate'),
    'validate_mod_compatibility': _make_lazy_handler('tools.mod_ops', 'validate_mod_compatibility'),
    'cutscene_create_timeline': _make_lazy_handler('tools.cutscene_ops', 'cutscene_create_timeline'),
    'cutscene_add_camera_shot': _make_lazy_handler('tools.cutscene_ops', 'cutscene_add_camera_shot'),
    'cutscene_add_dialogue_event': _make_lazy_handler('tools.cutscene_ops', 'cutscene_add_dialogue_event'),
    'telemetry_track_event': _make_lazy_handler('tools.telemetry_ops', 'telemetry_track_event'),
    'telemetry_get_funnel': _make_lazy_handler('tools.telemetry_ops', 'telemetry_get_funnel'),
    'telemetry_session_summary': _make_lazy_handler('tools.telemetry_ops', 'telemetry_session_summary'),
    'telemetry_heatmap': _make_lazy_handler('tools.telemetry_ops', 'telemetry_heatmap'),
    'remote_balance_config': _make_lazy_handler('tools.adaptive_ops', 'remote_balance_config'),
    'trailer_capture_clip': _make_lazy_handler('tools.trailer_ops', 'trailer_capture_clip'),
    'trailer_render_sequence': _make_lazy_handler('tools.trailer_ops', 'trailer_render_sequence'),
    'capsule_generate_store_image': _make_lazy_handler('tools.trailer_ops', 'capsule_generate_store_image'),
    'onboarding_create_tutorial_step': _make_lazy_handler('tools.onboarding_ops', 'onboarding_create_tutorial_step'),
    'onboarding_create_guided_tour': _make_lazy_handler('tools.onboarding_ops', 'onboarding_create_guided_tour'),
    'onboarding_check_first_experience': _make_lazy_handler('tools.onboarding_ops', 'onboarding_check_first_experience'),
    'publish_manage': _make_manage_handler('tools.publish_ops', 'publish_manage', 'preview'),
    'community_manage': _make_manage_handler('tools.community_ops', 'community_manage', 'badge'),
}
