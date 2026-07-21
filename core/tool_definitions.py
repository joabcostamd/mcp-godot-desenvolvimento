"""core/tool_definitions.py - Raw Tool Definitions (Etapa A5).

Contem APENAS a lista bruta de objetos Tool().
Extraido de server.py:_tool_defs() para reduzir tamanho.
"""

from __future__ import annotations

from mcp.types import Tool


def _raw_tool_defs() -> list[Tool]:
    """Retorna a lista bruta de ferramentas (SEM filtros)."""
    return [
        Tool(
            name="ping",
            description=(
                "Verifica se o servidor godot-mcp-agent está funcional e conectado. "
                "Use esta tool no início de cada sessão para confirmar que o MCP está vivo. "
                "Quando usar: primeira chamada da sessão, ou quando suspeitar que o servidor caiu. "
                "Quando NÃO usar: durante fluxo normal de criação de jogos (desnecessário). "
                "Pré-condições: nenhuma — o servidor só precisa estar em execução. "
                "Exemplo de input: {} (chamada sem argumentos). "
                "Erro mais comum: timeout ou conexão recusada — significa que o servidor não está rodando; "
                "verifique se server.py está em execução no terminal."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="budget_manage",
            description=(
                "Gerencia o orcamento de tokens da sessao (Fatia 1.D). "
                "Mostra custo estimado em reais (BRL), define teto e zera contador. "
                "Precos baseados em DeepSeek V4 (~R$0.003/1K input, ~R$0.010/1K output). "
                "Valores sao ESTIMATIVAS — custo real pode variar. "
                "Quando usar: verificar gastos, definir orcamento maximo. "
                "Operacoes: status (ver custo), set_limit (definir teto em R$), reset (zerar). "
                "Exemplo: {\"op\": \"status\"} retorna custo, percentual, avisos."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "op": {
                        "type": "string",
                        "description": "Operacao: 'status', 'set_limit' ou 'reset'.",
                        "enum": ["status", "set_limit", "reset"],
                    },
                    "limit_brl": {
                        "type": "number",
                        "description": "Valor do teto em reais (para op='set_limit'). Ex: 5.00.",
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Se True, ignora confirmacoes.",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="mcp_telemetry_manage",
            description=(
                "Gerencia a telemetria opt-in do MCP (Fatia 1.P). "
                "Rastreia uso do MCP como ferramenta: quais tools sao chamadas, em qual fase, "
                "quanto tempo levam, quais falham. Telemetria 100% LOCAL — NADA sai da sua maquina. "
                "Consentimento explicito: DESLIGADO por padrao. "
                "Quando usar: ativar telemetria (op=enable), ver metricas (op=status), "
                "exportar relatorio (op=export), desativar (op=disable), apagar dados (op=reset). "
                "Exemplo: {\"op\": \"enable\"} ativa a coleta de dados de uso."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "op": {
                        "type": "string",
                        "description": "Operacao: 'status', 'enable', 'disable', 'export' ou 'reset'.",
                        "enum": ["status", "enable", "disable", "export", "reset"],
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="godot",
            description=(
                "🎯 INTENT ROUTER — A MELHOR FERRAMENTA DO MCP. "
                "Descreva o que você quer fazer em linguagem natural (PT-BR ou EN) "
                "e o sistema automaticamente encontra e chama a ferramenta correta. "
                "Exemplos: 'criar cena Node2D chamada Level1', "
                "'adicionar inimigo com patrulha', 'gerar script do player', "
                "'rodar o jogo', 'criar menu principal', 'importar textura'. "
                "Quando NÃO usar: se você já sabe exatamente qual tool usar "
                "(ex: ping, health_check). "
                "Pré-condições: projeto ativo definido (bootstrap_godot_mcp). "
                "Exemplo de input: {\"action\": \"criar inimigo com patrulha\"}. "
                "Erro mais comum: frase muito vaga — seja específico sobre o que quer criar ou fazer."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "O que você quer fazer? Descreva em PT-BR ou EN. Ex: 'criar cena', 'adicionar nó Sprite2D', 'rodar o jogo'."
                    },
                },
                "required": ["action"],
            },
        ),
        Tool(
            name="validate_mcp_registry",
            description=(
                "Ferramenta de diagnóstico: valida a consistência entre as 3 fontes "
                "de verdade do registro de tools (definições Tool(), handlers, e "
                "TOOLSETS/PHASE_TOOLSETS). Retorna relatório JSON com 3 categorias: "
                "tools sem handler (não implementadas), handlers sem Tool() "
                "(código morto/inacessível), e tools funcionais não categorizadas "
                "em nenhuma fase. NÃO requer parâmetros. "
                "Quando usar: para auditar a saúde do registro de tools, "
                "especialmente após adicionar/remover tools ou modificar fases."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="validate_godot_version",
            description=(
                "Verifica se a versão do Godot instalada é 4.7.x. "
                "Use no início da primeira sessão com um novo projeto, ou quando suspeitar "
                "que o Godot foi atualizado. "
                "Quando NÃO usar: durante o ciclo normal de criação de jogo após a primeira validação. "
                "Pré-condições: config.json deve ter godot_path válido. "
                "Exemplo de input: {} (sem argumentos). "
                "Erro mais comum: Godot não encontrado no path — verifique config.json."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="read_file",
            description=(
                "Lê o conteúdo de um arquivo do projeto (.gd, .tscn, .tres, etc.). "
                "Use para examinar scripts, cenas ou qualquer arquivo de texto do projeto. "
                "Quando NÃO usar: para listar arquivos (use inspect_project). "
                "Pré-condições: o arquivo deve existir no projeto. "
                "Exemplo de input: {\"path\": \"scripts/player.gd\"}. "
                "Erro mais comum: arquivo não encontrado — use inspect_project para listar arquivos disponíveis."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho relativo ao projeto."},
                    "start_line": {"type": "integer", "description": "Linha inicial (1-indexed, opcional)."},
                    "end_line": {"type": "integer", "description": "Linha final inclusiva (opcional)."},
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="write_file",
            description=(
                "Cria ou modifica um arquivo no projeto. "
                "Use para criar scripts GDScript, editar cenas manualmente, ou qualquer escrita de arquivo. "
                "Quando NÃO usar: para criar cenas estruturadas (use create_scene + add_node). "
                "Pré-condições: o diretório pai deve existir (criado automaticamente). "
                "Exemplo de input: {\"path\": \"scripts/player.gd\", \"content\": \"extends CharacterBody2D\", \"mode\": \"create\"}. "
                "Erro mais comum: mode='create' com arquivo existente — use mode='overwrite' ou delete_file antes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho relativo ao projeto."},
                    "content": {"type": "string", "description": "Conteúdo a escrever."},
                    "mode": {"type": "string", "enum": ["create", "overwrite", "append"], "description": "Modo: create (só se não existir), overwrite (substitui), append (adiciona)."},
                },
                "required": ["path", "content"],
            },
        ),
        # ── Fase 2: ClassDB ──
        Tool(
            name="query_classdb",
            description=(
                "Consulta informações COMPLETAS de uma classe na ClassDB do Godot com "
                "PAGINAÇÃO, FILTROS e DETALHES. Retorna propriedades (com tipo, descrição, default), "
                "métodos (com args, retorno, descrição), sinais, enums e constantes. "
                "Use para descobrir TUDO sobre qualquer classe do Godot 4.7. "
                "Parâmetros de filtro: 'section' escolhe a seção (properties, methods, signals, enums, constants, all), "
                "'include_inherited' inclui membros da classe pai, 'offset' e 'limit' controlam paginação. "
                "QUANDO USAR: para consultar uma classe específica com riqueza de detalhes. "
                "QUANDO NÃO USAR: para listar tipos de nó (use list_valid_node_types) ou buscar por nome parcial (use search_classdb). "
                "Exemplo: {'class_name': 'CharacterBody2D', 'section': 'methods', 'limit': 10}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {"type": "string", "description": "Nome da classe (ex: 'Node2D', 'CharacterBody2D'). Case-sensitive."},
                    "section": {
                        "type": "string",
                        "enum": ["all", "properties", "methods", "signals", "enums", "constants"],
                        "description": "Seção a retornar. 'all' retorna todas. Default: 'all'."
                    },
                    "include_inherited": {
                        "type": "boolean",
                        "description": "Incluir membros herdados da classe pai. Default: false."
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Offset para paginação. Default: 0."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Máximo de itens por seção. Default: 50."
                    },
                },
                "required": ["class_name"],
            },
        ),
        Tool(
            name="search_classdb",
            description=(
                "🔍 Busca classes na ClassDB do Godot por nome PARCIAL. "
                "Diferente de query_classdb (que exige nome exato), esta tool faz busca fuzzy: "
                "'Body' encontra CharacterBody2D, StaticBody2D, RigidBody3D, etc. "
                "Use para descobrir classes quando você não sabe o nome exato. "
                "QUANDO USAR: 'tem alguma classe de luz?', 'quais classes têm Body no nome?'. "
                "QUANDO NÃO USAR: se já sabe o nome exato (use query_classdb). "
                "Exemplo: {'query': 'Light', 'limit': 10}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Texto parcial para buscar (ex: 'Body', 'Light', 'Camera'). Case-insensitive."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Máximo de resultados. Default: 20."
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="download_asset",
            description=(
                "Baixa assets GRATUITOS (CC0) de APIs publicas. "
                "Fontes: Poly Haven (texturas PBR, HDRIs, modelos 3D), Kenney (sprites, tilesets, UI, audio), "
                "AmbientCG (materiais PBR). Use para prototipagem rapida. "
                "Exemplo: {'source': 'polyhaven', 'query': 'metal', 'category': 'textures'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "enum": ["polyhaven", "kenney", "ambientcg"]},
                    "query": {"type": "string"},
                    "category": {"type": "string"},
                    "asset_id": {"type": "string"},
                    "resolution": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "required": ["source", "query"],
            },
        ),
        Tool(
            name="import_downloaded_asset",
            description=(
                "Importa um asset baixado para o projeto Godot ativo. "
                "Use APOS download_asset. "
                "Exemplo: {'asset_path': 'C:/.../gdm_assets/...', 'target_dir': 'assets/textures'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_path": {"type": "string"},
                    "target_dir": {"type": "string"},
                },
                "required": ["asset_path"],
            },
        ),
        Tool(
            name="workflow_snapshot",
            description=(
                "Salva snapshot do estado atual do projeto no workflow log. "
                "Use ANTES de operações grandes para ter ponto de restauração."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "project_path": {"type": "string"},
                },
                "required": [],
            },
        ),
        Tool(
            name="workflow_handoff",
            description=(
                "Prepara resumo para proxima sessao. Use no FINAL de cada sessao."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "next_steps": {"type": "array", "items": {"type": "string"}},
                    "notes": {"type": "string"},
                },
                "required": [],
            },
        ),
        Tool(
            name="project_map",
            description="Gera mapa do projeto: cenas, scripts, funcoes, assets. Formatos: json ou html.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string"},
                    "format": {"type": "string", "enum": ["json", "html", "both"]},
                },
                "required": [],
            },
        ),
        Tool(name="configure_security", description="Configura token de seguranca para o addon MCP.",
            inputSchema={"type":"object","properties":{"generate_token":{"type":"boolean"},"allow_remote":{"type":"boolean"}},"required":[]}),
        Tool(name="security_status", description="Verifica configuracao de seguranca atual.",
            inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="run_gut_tests", description="Executa testes GUT via Godot headless. Ex: {'test_dir': 'res://tests'}.",
            inputSchema={"type":"object","properties":{"project_path":{"type":"string"},"test_dir":{"type":"string"},"timeout":{"type":"integer"}},"required":[]}),
        Tool(name="assert_node_exists", description="Verifica se no existe na cena. Ex: {'scene_path':'...','node_path':'./Player'}.",
            inputSchema={"type":"object","properties":{"scene_path":{"type":"string"},"node_path":{"type":"string"},"node_type":{"type":"string"}},"required":["scene_path","node_path"]}),
        Tool(name="simulate_input_sequence", description="Simula sequencia de inputs. Ex: {'actions':[{'type':'key','key':32}]}.",
            inputSchema={"type":"object","properties":{"actions":{"type":"array","items":{"type":"object"}},"delay_ms":{"type":"integer"}},"required":["actions"]}),
        Tool(name="vibe_coding_mode", description="Ativa/desativa Vibe Coding Mode. Foco automatico na cena configurada.",
            inputSchema={"type":"object","properties":{"enabled":{"type":"boolean"},"scene_path":{"type":"string"},"focus_node":{"type":"string"}},"required":[]}),
        Tool(name="get_vibe_context", description="Retorna contexto atual do Vibe Coding Mode.",
            inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="game_http_request", description="HTTP request no jogo. Ex: {'url':'https://api.ex.com','method':'GET'}.",
            inputSchema={"type":"object","properties":{"url":{"type":"string"},"method":{"type":"string"},"headers":{"type":"object"},"body":{"type":"string"}},"required":["url"]}),
        Tool(name="game_multiplayer", description="Multiplayer ENet. Ex: {'action':'create_server','port':9090}.",
            inputSchema={"type":"object","properties":{"action":{"type":"string","enum":["create_server","create_client","disconnect","status"]},"port":{"type":"integer"},"address":{"type":"string"}},"required":["action"]}),
        Tool(name="set_safety_policy", description="Configura politica de seguranca (allowlist/blocklist).",
            inputSchema={"type":"object","properties":{"enabled":{"type":"boolean"},"allowlist":{"type":"array","items":{"type":"string"}},"blocklist":{"type":"array","items":{"type":"string"}},"confirm_destructive":{"type":"boolean"}},"required":[]}),
        Tool(name="get_audit_log", description="Historico de auditoria das acoes da IA.",
            inputSchema={"type":"object","properties":{"limit":{"type":"integer"}},"required":[]}),
        Tool(name="get_audit_replay", description="Replay do historico de auditoria.",
            inputSchema={"type":"object","properties":{"steps":{"type":"integer"}},"required":[]}),
        Tool(name="safe_write_gdscript", description="Escreve .gd COM validacao. Recusa codigo invalido! Ex: {'file_path':'res://x.gd','content':'...'}.",
            inputSchema={"type":"object","properties":{"file_path":{"type":"string"},"content":{"type":"string"},"project_path":{"type":"string"},"strict":{"type":"boolean"}},"required":["file_path","content"]}),
        Tool(name="tool_catalog", description="Catalogo de tools por grupo. Ex: {'query':'scene','group':'core'}.",
            inputSchema={"type":"object","properties":{"query":{"type":"string"},"group":{"type":"string"},"limit":{"type":"integer"}},"required":[]}),
        Tool(name="tool_groups", description="Gerencia grupos dinamicos de tools. Ex: {'action':'activate','group':'art'}.",
            inputSchema={"type":"object","properties":{"action":{"type":"string","enum":["list","activate","deactivate"]},"group":{"type":"string"}},"required":["action"]}),
        # ── Meta-tools (Fatia 0.15) — descoberta e invocação dinâmica ──
        Tool(
            name="catalog_search",
            description=(
                "Busca ferramentas por linguagem natural (português ou inglês). "
                "Use para DESCOBRIR qual tool resolve seu problema. "
                "Ex: {'query': 'criar cena'} → retorna scene_manage e ferramentas relacionadas. "
                "Ex: {'query': 'audio', 'namespace': 'assets'} → filtra por namespace."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "O que você quer fazer? (PT ou EN)"},
                    "namespace": {"type": "string", "enum": ["project", "assets", "runtime", "analysis", "orchestration"], "description": "Filtrar por namespace semântico."},
                    "limit": {"type": "integer", "description": "Máximo de resultados (default 20)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="describe_tool",
            description=(
                "Retorna o schema COMPLETO de uma ferramenta específica: descrição, "
                "parâmetros, hints (readOnly, destructive, idempotent, openWorld) "
                "e categoria de operação. Use DEPOIS de catalog_search, quando já "
                "souber qual tool usar. Ex: {'name': 'scene_manage'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome exato da tool (ex: 'scene_manage', 'ping')."},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="invoke_by_name",
            description=(
                "Invoca uma ferramenta pelo nome, passando os argumentos como dict. "
                "RESPEITA todos os gates (fase, session, kill switch, governador). "
                "Use como alternativa quando souber exatamente qual tool e quais "
                "parâmetros usar. Ex: {'name': 'ping', 'arguments': {}}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome exato da tool a invocar."},
                    "arguments": {"type": "object", "description": "Argumentos da tool como dict."},
                },
                "required": ["name"],
            },
        ),
        Tool(name="game_serialize_state", description="Salva/restaura estado completo do jogo como JSON.",
            inputSchema={"type":"object","properties":{"action":{"type":"string","enum":["save","load"]},"file_name":{"type":"string"}},"required":["action"]}),
        Tool(name="start_recording", description="Inicia gravacao de sessao (inputs/estados).",
            inputSchema={"type":"object","properties":{"session_name":{"type":"string"}},"required":[]}),
        Tool(name="stop_recording", description="Para gravacao e retorna resumo.",
            inputSchema={"type":"object","properties":{"session_name":{"type":"string"}},"required":["session_name"]}),
        Tool(name="game_call_method", description="Chama metodo em no no jogo rodando.",
            inputSchema={"type":"object","properties":{"node_path":{"type":"string"},"method":{"type":"string"},"args":{"type":"array"}},"required":["node_path","method"]}),
        Tool(name="game_spawn_node", description="Cria no dinamicamente no jogo.",
            inputSchema={"type":"object","properties":{"parent_path":{"type":"string"},"node_type":{"type":"string"},"node_name":{"type":"string"},"properties":{"type":"object"}},"required":["parent_path","node_type"]}),
        Tool(name="game_raycast", description="Ray cast 2D/3D no jogo.",
            inputSchema={"type":"object","properties":{"origin_x":{"type":"number"},"origin_y":{"type":"number"},"target_x":{"type":"number"},"target_y":{"type":"number"},"collision_mask":{"type":"integer"},"mode":{"type":"string"}},"required":["origin_x","origin_y","target_x","target_y"]}),
        Tool(name="game_get_camera", description="Obtem posicao da camera ativa.",
            inputSchema={"type":"object","properties":{"mode":{"type":"string"}},"required":[]}),
        Tool(name="game_play_animation", description="Controla AnimationPlayer no jogo.",
            inputSchema={"type":"object","properties":{"node_path":{"type":"string"},"action":{"type":"string"},"animation_name":{"type":"string"}},"required":["node_path","action"]}),
        Tool(name="game_find_nodes_by_class", description="Encontra nos por classe no jogo.",
            inputSchema={"type":"object","properties":{"class_name":{"type":"string"},"limit":{"type":"integer"}},"required":["class_name"]}),
        Tool(name="game_await_signal", description="Espera sinal com timeout.",
            inputSchema={"type":"object","properties":{"node_path":{"type":"string"},"signal_name":{"type":"string"},"timeout_ms":{"type":"integer"}},"required":["node_path","signal_name"]}),
        Tool(name="game_pause", description="Pausa/despausa o jogo.",
            inputSchema={"type":"object","properties":{"action":{"type":"string","enum":["toggle","pause","unpause"]}},"required":[]}),
        Tool(name="game_performance", description="Metricas: FPS, memoria, objetos, draw calls.",
            inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="game_window", description="Controle de janela: size, fullscreen, title.",
            inputSchema={"type":"object","properties":{"action":{"type":"string"},"width":{"type":"integer"},"height":{"type":"integer"},"fullscreen":{"type":"boolean"},"title":{"type":"string"}},"required":[]}),
        Tool(name="game_input_state", description="Estado de input: teclas, mouse, gamepad.",
            inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="generate_ci_snippet", description="Gera GitHub Actions / GitLab CI para export.",
            inputSchema={"type":"object","properties":{"project_path":{"type":"string"},"target_platforms":{"type":"string"}},"required":[]}),
        Tool(name="resource_dependency_graph", description="Grafo de dependencias de recursos.",
            inputSchema={"type":"object","properties":{"project_path":{"type":"string"}},"required":[]}),
        Tool(name="build_csharp", description="Compila projeto C# e retorna erros estruturados.",
            inputSchema={"type":"object","properties":{"project_path":{"type":"string"}},"required":[]}),
        Tool(name="debugger_set_breakpoint", description="Define breakpoint. Ex: {'script_path':'res://player.gd','line':42}.",
            inputSchema={"type":"object","properties":{"script_path":{"type":"string"},"line":{"type":"integer"},"condition":{"type":"string"}},"required":["script_path","line"]}),
        Tool(name="debugger_status", description="Verifica estado do debugger do Godot (porta 6006).",
            inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="debugger_step", description="Avança uma linha no debugger. Ex: {'step_type':'over'}.",
            inputSchema={"type":"object","properties":{"step_type":{"type":"string","enum":["over","into","out"]}},"required":[]}),
        Tool(name="debugger_get_stack", description="Obtem stack trace atual do debugger.",
            inputSchema={"type":"object","properties":{},"required":[]}),
        Tool(name="debugger_get_variables", description="Inspeciona variaveis no escopo do debugger. Ex: {'variable_name':'health'}.",
            inputSchema={"type":"object","properties":{"variable_name":{"type":"string","description":"Nome da variavel (null = todas)."}},"required":[]}),
        Tool(
            name="list_valid_node_types",
            description=(
                "Lista todos os tipos de nó que podem ser usados em cenas (classes que herdam de Node). "
                "Use para descobrir quais tipos de nó existem no Godot 4.7. "
                "Quando NÃO usar: para consultar uma classe específica (use query_classdb). "
                "Pré-condições: nenhuma. "
                "Exemplo de input: {} (sem argumentos). "
                "Erro mais comum: retorna centenas de tipos — é esperado."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        # ── Fase 2: Cenas extendidas ──
        # ── Fase 2: Scripts ──
        # ── Fase 2: Física ──
        # ── Fase 2: Assets ──
        # ── Fase 2: Input e Autoload ──
        Tool(
            name="install_mcp_addon",
            description=(
                "Instala o addon MCP no projeto Godot ativo e ativa o plugin do editor. "
                "O QUE FAZ: copia os arquivos do addon (mcp_addon.gd, plugin.cfg) "
                "para addons/mcp_addon/ no projeto e adiciona o plugin em editor_plugins no project.godot. "
                "Também instala o runtime bridge (mcp_runtime_bridge/) para debug runtime. "
                "QUANDO USAR: sempre que criar um projeto novo com create_project, antes de usar "
                "ferramentas que precisam do editor (screenshots, run_game, etc). "
                "Também use se o projeto foi movido ou o addon foi removido acidentalmente. "
                "Após instalar, reinicie o editor Godot para ativar o plugin. "
                "O dock 'MCP Addon' aparecerá no painel direito do editor (3 tabs). "
                "NÃO requer parâmetros se já houver um projeto ativo (set_active_project)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Caminho do projeto Godot. Opcional se já usou set_active_project. Ex: 'C:/meu_jogo'"
                    }
                },
                "required": []
            },
        ),
        Tool(
            name="bootstrap_godot_mcp",
            description=(
                "🚀 BOOTSTRAP AUTOMÁTICO: conecta VS Code → MCP → Godot em UMA chamada. "
                "Substitui 12+ passos manuais (validar, configurar, abrir Godot, esperar LSP, "
                "esperar addon, conectar tudo). A IA agêntica deve chamar ESTA tool primeiro, "
                "sempre que iniciar uma sessão de desenvolvimento Godot. "
                "QUANDO USAR: primeira tool de toda sessão Godot. "
                "QUANDO NÃO USAR: se já rodou bootstrap nesta sessão (use health_check para verificar). "
                "Exemplo: {'target': 'full'} para bootstrap completo com auto-detecção. "
                "Use target='validate_only' para só checar o ambiente sem abrir Godot. "
                "Use target='connect_only' se Godot já estiver aberto."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "enum": ["full", "connect_only", "validate_only"],
                        "description": "full=tudo, connect_only=só conexão (Godot já aberto), validate_only=só checar ambiente"
                    },
                    "project_path": {
                        "type": "string",
                        "description": "Caminho do projeto Godot. Auto-detecta se omitido."
                    },
                    "godot_path": {
                        "type": "string",
                        "description": "Caminho do executável Godot. Auto-detecta do config.json se omitido."
                    },
                    "launch_editor": {
                        "type": "boolean",
                        "description": "Abrir Godot Editor se não estiver aberto. Default: true."
                    },
                    "timeout_godot": {
                        "type": "integer",
                        "description": "Segundos máximos esperando Godot abrir (default 30)."
                    },
                    "timeout_addon": {
                        "type": "integer",
                        "description": "Segundos máximos esperando addon iniciar (default 15)."
                    },
                },
                "required": []
            },
        ),
        Tool(
            name="godot_keep_alive",
            description="Garante que o Godot Editor esta aberto. Se nao estiver, abre. "
                        "NAO fecha o Godot em hipotese alguma. Chame no inicio de toda sessao. "
                        "Use quando suspeitar que o Godot foi fechado.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho do projeto (auto se omitido)."},
                    "godot_path": {"type": "string", "description": "Caminho do Godot (auto se omitido)."},
                },
                "required": []
            },
        ),
        # ── Fase 2: Runtime ──
        # ── Fase 3: Editor ao vivo ──
        Tool(
            name="take_screenshot",
            description=(
                "Captura uma screenshot do viewport 2D do editor Godot. "
                "Use para VER o estado atual do jogo sem precisar abri-lo manualmente. "
                "A imagem é retornada em base64 para análise pela IA. "
                "Quando NÃO usar: se o editor não estiver aberto (use launch_editor antes). "
                "Pré-condições: editor deve estar aberto com addon conectado. "
                "Exemplo de input: {}. "
                "Erro mais comum: editor não aberto ou viewport 2D indisponível."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="read_console_output",
            description=(
                "Lê as últimas linhas do console do editor Godot. "
                "Use para diagnosticar erros de runtime, warnings, ou ver prints de debug. "
                "Quando NÃO usar: se o editor não estiver aberto (retorna console offline). "
                "Pré-condições: editor aberto para console em tempo real; offline retorna buffer do subprocess. "
                "Exemplo de input: {} ou {\"since_timestamp\": 1234567890.0}. "
                "Erro mais comum: retorna vazio — o console pode não ter capturado nada ainda."
            ),
            inputSchema={
                "type": "object",
                "properties": {"since_timestamp": {"type": "number"}},
                "required": [],
            },
        ),
        # ── Fase 4: Tilemap ──
        # ── Fase 4: Animação ──
        # ── Fase 4: UI ──
        # ── Fase 5: Export, Segurança ──
        # ── Bloco 4: Proof Ledger ──
        Tool(
            name="capture_proof",
            description=(
                "Coleta MECANICAMENTE a evidência de uma tarefa concluída e grava "
                "num arquivo assinado por hash SHA-256. NENHUM texto vem da IA — "
                "tudo é output literal capturado via subprocess (git diff, git status, "
                "conteúdo de arquivos, testes). "
                "Use ao final de cada tarefa para gerar prova auditável. "
                "Pré-condições: projeto deve ser um repositório git. "
                "Exemplo de input: {\"task_id\": \"bloco4-capture-proof\"}. "
                "Erro mais comum: project_path não existe."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Identificador curto da tarefa."},
                    "project_path": {"type": "string", "description": "Caminho do repositório. Default: raiz do MCP."},
                    "run_tests": {"type": "boolean", "description": "Se roda regression_test como parte da prova. Default: true."},
                    "extra_commands": {"type": "array", "items": {"type": "string"}, "description": "Comandos extras cujo stdout/stderr capturar. Máx 5."},
                },
                "required": ["task_id"],
            },
        ),
        Tool(
            name="verify_proof",
            description=(
                "Verifica se uma prova é válida E se corresponde ao estado ATUAL do código "
                "(ou seja: se o código não mudou depois que a prova foi coletada). "
                "Use para validar provas antes de commits ou auditorias. "
                "Pré-condições: capture_proof deve ter sido executado antes. "
                "Exemplo de input: {\"task_id\": \"bloco4\"}. "
                "Erro mais comum: prova não encontrada — retorna 'missing'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Se passado, verifica a prova mais recente desse task_id."},
                    "project_path": {"type": "string", "description": "Caminho do repositório. Default: raiz do MCP."},
                    "max_age_minutes": {"type": "integer", "description": "Prova mais velha que isso é obsoleta. Default: 60."},
                },
                "required": [],
            },
        ),
        # ── Game Bridge (runtime) ──
        Tool(
            name="inject_input_event",
            description=(
                "Injeta um evento de input (mouse/teclado) no jogo EM EXECUÇÃO. "
                "Use para simular cliques, teclas, ou movimento de mouse durante o jogo. "
                "Quando NÃO usar: se o jogo não estiver rodando (use run_game primeiro). "
                "Pré-condições: jogo rodando com autoload GameBridge instalado. "
                "Exemplo de input: {\"event_type\": \"key\", \"event_data\": {\"keycode\": 32, \"pressed\": true}}. "
                "Erro mais comum: bridge não instalado — use write_file + configure_autoload para instalar."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "event_type": {"type": "string", "enum": ["key", "mouse_button", "mouse_motion"]},
                    "event_data": {"type": "object"},
                },
                "required": ["event_type", "event_data"],
            },
        ),
        Tool(
            name="execute_gdscript_runtime",
            description=(
                "Executa código GDScript arbitrário no jogo em execução e retorna o valor. "
                "Use para consultar estado do jogo, modificar nós, ou testar lógica em tempo real. "
                "Aceita expressões ('2+2') e statements ('get_node(...).position.x = 100'). "
                "Quando NÃO usar: se o jogo não estiver rodando. "
                "Pré-condições: jogo rodando com autoload GameBridge instalado. "
                "Exemplo de input: {\"code\": \"get_node('/root/Main/Player').position\"}. "
                "Erro mais comum: código inválido — retorna erro de compilação GDScript."
            ),
            inputSchema={
                "type": "object",
                "properties": {"code": {"type": "string", "description": "Código GDScript a executar."}},
                "required": ["code"],
            },
        ),
        Tool(
            name="watch_signal",
            description=(
                "Observa um sinal de um nó por N segundos e retorna se disparou. "
                "Use para verificar se um evento ocorreu (ex: inimigo morreu, animação terminou). "
                "Verifica imediatamente se o nó e sinal existem — erro instantâneo se não. "
                "Quando NÃO usar: se o jogo não estiver rodando. "
                "Pré-condições: jogo rodando com autoload GameBridge instalado. "
                "Exemplo de input: {\"node_path\": \"/root/Main/Player\", \"signal_name\": \"health_changed\", \"timeout\": 3.0}. "
                "Erro mais comum: nó ou sinal não encontrado — erro retornado imediatamente, sem esperar timeout."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node_path": {"type": "string"},
                    "signal_name": {"type": "string"},
                    "timeout": {"type": "number", "description": "Segundos de espera (default 5)."},
                },
                "required": ["node_path", "signal_name"],
            },
        ),
        # ── Onda 1: Visão (Screenshots) ──
        Tool(
            name="capture_game_screenshot",
            description=(
                "Captura uma screenshot do jogo em execução usando janela off-screen. "
                "Use para VER o estado atual do jogo sem abrir o Godot — a IA pode analisar "
                "a imagem e ajustar o que for necessário. "
                "Quando usar: após criar/modificar cenas, para validar visualmente o resultado. "
                "Quando NÃO usar: se o jogo não compila (use compile_test primeiro). "
                "Pré-condições: projeto deve compilar sem erros, main_scene deve estar definida. "
                "Exemplo de input: {} (usa defaults: 30 frames, 1280x720). "
                "Erro mais comum: screenshot preta — verifique se há câmera na cena."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "wait_frames": {"type": "integer", "description": "Frames de espera antes da captura (default 30)."},
                    "scene_path": {"type": "string", "description": "Cena específica (opcional)."},
                    "resolution_width": {"type": "integer", "description": "Largura (default 1280)."},
                    "resolution_height": {"type": "integer", "description": "Altura (default 720)."},
                },
                "required": [],
            },
        ),
        # ── Onda 1: Visão (Análise) ──
        # ── Onda 2: Batch Operations ──
        Tool(
            name="add_nodes_batch",
            description=(
                "Adiciona múltiplos nós a uma cena em UMA OPERAÇÃO. "
                "Muito mais rápido que chamar add_node repetidamente. "
                "Use para criar vários filhos de uma vez (ex: 50 tiles, 10 inimigos). "
                "Quando usar: sempre que precisar adicionar 3+ nós na mesma cena. "
                "Quando NÃO usar: para 1-2 nós (use add_node). "
                "Pré-condições: cena e nó pai devem existir. "
                "Exemplo: {\"scene_path\": \"scenes/main.tscn\", \"nodes\": ["
                "{\"parent_node_path\": \".\", \"node_name\": \"Enemy1\", \"node_type\": \"CharacterBody2D\"}, ...]}. "
                "Erro mais comum: nome duplicado — retorna erro no item específico."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "nodes": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["scene_path", "nodes"],
            },
        ),
        Tool(
            name="set_properties_batch",
            description=(
                "Define múltiplas propriedades em UMA OPERAÇÃO. "
                "Muito mais rápido que chamar set_node_property repetidamente. "
                "Use para configurar vários nós de uma vez (ex: posições, cores, tamanhos). "
                "Quando usar: sempre que precisar definir 3+ propriedades na mesma cena. "
                "Pré-condições: cena e nós devem existir. "
                "Exemplo: {\"scene_path\": \"scenes/main.tscn\", \"properties\": ["
                "{\"node_path\": \"./Player\", \"property_name\": \"position\", \"value\": \"Vector2(100,200)\"}, ...]}. "
                "Erro mais comum: nó não encontrado — retorna erro no item específico."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "properties": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["scene_path", "properties"],
            },
        ),
        Tool(
            name="batch_atomic_edit",
            description=(
                "⚛️ Edição ATÔMICA em lote com ROLLBACK automático. "
                "Executa múltiplas operações (criar nó, definir propriedade, deletar, "
                "reparentar, duplicar, conectar sinal) em UMA ação. "
                "Se QUALQUER operação falhar, TODAS as anteriores são DESFEITAS. "
                "Modo addon (Godot aberto): UndoRedo nativo — 1 Ctrl+Z desfaz tudo. "
                "Modo file-based (Godot fechado): snapshot .tscn + restore se erro. "
                "QUANDO USAR: SEMPRE que for fazer 2+ operações que precisam ser atômicas. "
                "QUANDO NÃO USAR: para 1 operação isolada (use node_manage direto). "
                "Exemplo: [{\"op\": \"create_node\", \"params\": {\"parent\": \".\", \"type\": \"Sprite2D\", \"name\": \"Icon\"}}, "
                "{\"op\": \"set_property\", \"params\": {\"node\": \"./Icon\", \"prop\": \"position\", \"value\": \"Vector2(100,200)\"}}]. "
                "Ops válidas: create_node, delete_node, set_property, reparent_node, duplicate_node, connect_signal."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "operations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "op": {
                                    "type": "string",
                                    "enum": ["create_node", "delete_node", "set_property", "reparent_node", "duplicate_node", "connect_signal"],
                                },
                                "params": {"type": "object"},
                            },
                            "required": ["op"],
                        },
                        "description": "Lista de operações atômicas. Se uma falhar, todas são desfeitas."
                    },
                    "scene_path": {
                        "type": "string",
                        "description": "Caminho da cena .tscn. Obrigatório para file-based. Opcional se addon conectado."
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["auto", "addon", "file"],
                        "description": "auto=detecta addon, addon=força WebSocket, file=força file-based."
                    },
                },
                "required": ["operations"],
            },
        ),
        # ── Onda 3: Assets Procedurais ──
        Tool(
            name="generate_audio_sfx",
            description=(
                "Gera um efeito sonoro WAV por sintese procedural com 23 tipos. "
                "Suporta: beep, jump, laser, explosion, collect, hit, "
                "coin, ui_click, ui_hover, ui_error, ui_notification, "
                "wind, rain, footsteps, gunshot, engine, electricity, "
                "magic, powerup, damage, door, fire, water, string. "
                "Use para sons de pulo, tiro, coleta, explosao, UI, ambiente "
                "e muito mais — sem assets externos. "
                "Pre-condicoes: nenhuma (usa NumPy + SciPy + wave nativos). "
                "Exemplo: {\"name\": \"magic_spell\", \"sfx_type\": \"magic\", \"duration\": 0.5, \"style\": \"fantasia\"}. "
                "Erro mais comum: tipo invalido — use um dos 23 tipos suportados."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "sfx_type": {"type": "string", "enum": [
                        "beep", "jump", "laser", "explosion", "collect", "hit",
                        "coin", "ui_click", "ui_hover", "ui_error", "ui_notification",
                        "wind", "rain", "footsteps", "gunshot", "engine", "electricity",
                        "magic", "powerup", "damage", "door", "fire", "water", "string"
                    ]},
                    "duration": {"type": "number"},
                    "frequency": {"type": "number"},
                    "sample_rate": {"type": "integer"},
                    "style": {"type": "string", "enum": ["scifi", "fantasia", "retro", "realista"]},
                    "save_path": {"type": "string"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="generate_voice",
            description=(
                "Gera narracao/fala a partir de texto (TTS). "
                "Usa Kokoro TTS local (82M params, Apache 2.0, offline) ou "
                "Edge TTS gratuito como fallback. "
                "Ideal para dialogos de NPCs, narracao, voice acting. "
                "Suporta pt-BR via Edge TTS (Antonio, Francisca)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Texto para converter em fala (max 500 chars)"},
                    "voice": {"type": "string", "description": "Voz: af_heart, af_bella, am_adam, pt-BR-AntonioNeural..."},
                    "speed": {"type": "number", "description": "Velocidade (0.5 lento a 2.0 rapido)"},
                    "language": {"type": "string", "enum": ["pt", "en", "ja", "zh", "kr", "fr"],
                                "description": "Idioma do texto"},
                    "save_path": {"type": "string", "description": "Caminho no projeto (auto se None)"},
                },
                "required": ["text"],
            },
        ),
        # ── Onda 12: Arte IA ──
        Tool(
            name="generate_game_art",
            description=(
                "Gera arte de jogo a partir de descricao em linguagem natural usando IA "
                "(ChatGPT/DALL-E via navegador headless). Gera QUALQUER artefato: torres, "
                "inimigos, personagens, biomas, tiles, icones, HUD, VFX, tudo. "
                "Sprite sheets com multiplos frames para animacao automatica. "
                "Cache inteligente: mesma descricao = reusa arte (zero custo). "
                "Use para criar assets visuais completos sem sair do chat. "
                "Quando usar: SEMPRE que precisar de arte nova no jogo. "
                "Quando NAO usar: para placeholder rapido (use generate_placeholder_sprite). "
                "Pré-condicoes: projeto ativo, ChatGPT logado (primeira vez). "
                "Categorias: torre, inimigo, personagem, bioma, tile, icone, hud, vfx, fundo, projetil, ui. "
                "Estilos: scifi, fantasia, cartoon, realista, pixel, minimalista. "
                "Animacoes: idle, fire, walk, run, death, attack, spawn, hit. "
                "Grid automatico: 4 frames = 2x2, 6 frames = 3x2, etc. "
                "Exemplo: {\"description\": \"torre railgun com trilhos eletromagneticos azuis\", "
                "\"category\": \"torre\", \"style\": \"scifi\", \"frames\": 6, \"anim_type\": \"fire\"}. "
                "Retorna lista de frames recortados e prontos para apply_game_art."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Descricao da arte em portugues (ex: 'torre laser com cristal flutuante')."},
                    "category": {"type": "string", "enum": ["torre", "inimigo", "personagem", "bioma", "tile", "icone", "hud", "vfx", "fundo", "projetil", "ui"], "description": "Categoria do artefato."},
                    "style": {"type": "string", "enum": ["scifi", "fantasia", "cartoon", "realista", "pixel", "minimalista"], "description": "Estilo visual."},
                    "anim_type": {"type": "string", "enum": ["idle", "fire", "walk", "run", "death", "attack", "spawn", "hit"], "description": "Tipo de animacao."},
                    "frames": {"type": "integer", "description": "Quantidade de frames (4-16). Se omitido, usa padrao por animacao."},
                    "grid_cols": {"type": "integer", "description": "Colunas do grid (opcional, calculado automaticamente)."},
                    "grid_rows": {"type": "integer", "description": "Linhas do grid (opcional, calculado automaticamente)."},
                    "width": {"type": "integer", "description": "Largura por frame em pixels."},
                    "height": {"type": "integer", "description": "Altura por frame em pixels."},
                    "save_dir": {"type": "string", "description": "Diretorio relativo no projeto (ex: 'assets/sprites/towers/')."},
                    "ip_force": {"type": "boolean", "description": "Forca geracao mesmo com alerta de propriedade intelectual."},
                    "ip_reason": {"type": "string", "description": "Justificativa para ignorar alerta de PI (obrigatorio com ip_force=True)."},
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="apply_game_art",
            description=(
                "Aplica arte gerada (frames recortados) num AnimatedSprite2D do Godot. "
                "Importa frames, cria SpriteFrames .tres, configura animacao com FPS e loop. "
                "Use SEMPRE apos generate_game_art para colocar a arte no jogo. "
                "Quando usar: apos generate_game_art retornar os frames. "
                "Pré-condicoes: generate_game_art concluido, cena e no existirem. "
                "Exemplo: {\"frame_paths\": [\"assets/sprites/towers/railgun_f1.png\", ...], "
                "\"scene_path\": \"scenes/main.tscn\", \"node_path\": \"Grid/Towers/Torre_0\", "
                "\"anim_name\": \"fire\", \"fps\": 10, \"loop\": true}. "
                "Erro mais comum: frame nao encontrado — verifique se generate_game_art rodou antes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "frame_paths": {"type": "array", "items": {"type": "string"}, "description": "Lista de caminhos relativos dos frames."},
                    "scene_path": {"type": "string", "description": "Caminho da cena .tscn."},
                    "node_path": {"type": "string", "description": "Caminho do no AnimatedSprite2D."},
                    "anim_name": {"type": "string", "description": "Nome da animacao (ex: 'idle', 'fire')."},
                    "fps": {"type": "number", "description": "Frames por segundo. Default: 10."},
                    "loop": {"type": "boolean", "description": "Se a animacao faz loop. Default: true."},
                },
                "required": ["frame_paths", "scene_path", "node_path"],
            },
        ),
        # ── Pacote C: Pipeline de Arte FLUX.2 + Pós-processamento ──
        Tool(
            name="generate_game_art_flux",
            description=(
                "Gera arte de jogo via FLUX.2 API (Black Forest Labs). "
                "Substitui o DALL-E/Playwright. Suporta: torre, inimigo, "
                "personagem, bioma, tile, icone, hud, vfx, fundo, projetil, ui. "
                "Cache automatico por hash do prompt. Fallback para Replicate "
                "e Pillow procedural se APIs offline. "
                "Use esta tool como PRIMEIRA OPCAO para gerar assets visuais. "
                "A tool generate_game_art (DALL-E) e o fallback legado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Descricao em portugues do que gerar"},
                    "category": {"type": "string", "enum": ["torre","inimigo","personagem","bioma","tile","icone","hud","vfx","fundo","projetil","ui"],
                                 "description": "Tipo de artefato"},
                    "style": {"type": "string", "enum": ["scifi","fantasia","cartoon","realista","pixel","minimalista"],
                              "description": "Estilo visual"},
                    "frames": {"type": "integer", "description": "Numero de frames (1 = imagem unica)"},
                    "width": {"type": "integer", "description": "Largura (auto por categoria se omitido)"},
                    "height": {"type": "integer", "description": "Altura (auto por categoria se omitido)"},
                    "save_path": {"type": "string", "description": "Caminho relativo no projeto Godot"},
                },
                "required": ["description", "category"],
            },
        ),
        Tool(
            name="remove_background",
            description=(
                "Remove o fundo de uma imagem usando IA (rembg/birefnet). "
                "Use para sprites gerados por IA que vieram com fundo. "
                "Suporta PNG, JPG, WebP. Retorna PNG com transparencia."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Caminho da imagem com fundo"},
                    "output_path": {"type": "string", "description": "Caminho de saida (auto: _nobg)"},
                },
                "required": ["image_path"],
            },
        ),
        Tool(
            name="optimize_sprite",
            description=(
                "Otimiza/compacta sprite PNG usando oxipng (lossless, 10-30% reducao). "
                "Use antes de exportar o jogo para reduzir tamanho final."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Caminho da imagem PNG a otimizar"},
                    "lossless": {"type": "boolean", "description": "True=oxipng sem perda, False=pngquant (default true)"},
                },
                "required": ["image_path"],
            },
        ),
        Tool(
            name="create_spritesheet",
            description=(
                "Cria sprite sheet a partir de frames individuais. "
                "Use para juntar frames de animacao em uma unica imagem."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "frame_paths": {"type": "array", "items": {"type": "string"}, "description": "Lista de caminhos dos frames"},
                    "output_path": {"type": "string", "description": "Caminho de saida da sprite sheet"},
                    "frame_width": {"type": "integer", "description": "Largura de cada frame (default 64)"},
                    "frame_height": {"type": "integer", "description": "Altura de cada frame (default 64)"},
                    "columns": {"type": "integer", "description": "Numero de colunas (default 4)"},
                    "gap": {"type": "integer", "description": "Espaco entre frames em px (default 0)"},
                },
                "required": ["frame_paths", "output_path"],
            },
        ),
        # ── Onda 4: IA Agêntica ──
        Tool(
            name="godot_class_ref",
            description="Consulta metodos, propriedades, sinais, enums e constantes nativos do Godot via ClassDB (extension_api.json). "
                        "Cobre APENAS classes nativas do engine; NAO retorna classes custom do projeto (class_name em scripts .gd). "
                        "Evita alucinacao de API desatualizada. Use antes de gerar codigo contra uma classe desconhecida.",
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {"type": "string", "description": "Nome exato da classe nativa (ex: Node2D, CharacterBody2D). Nao funciona com classes custom de projetos."},
                },
                "required": ["class_name"],
            },
        ),
        # ── Onda 5: Cobertura Godot ──
        Tool(
            name="create_animation_tree",
            description=(
                "Adiciona um nó AnimationTree a uma cena. "
                "Use para animações avançadas com blend trees e state machines. "
                "Superior ao AnimationPlayer para transições complexas. "
                "Quando usar: para personagens com múltiplas animações (idle→walk→jump). "
                "Pré-condições: cena e nó pai existentes. "
                "Exemplo: {\"scene_path\": \"scenes/player.tscn\", \"parent_node_path\": \".\"}. "
                "Erro mais comum: nó pai não encontrado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "player_name": {"type": "string"},
                    "root_type": {"type": "string"},
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="create_joint_2d",
            description=(
                "Cria uma junta 2D (PinJoint2D) conectando dois nós. "
                "Use para portas giratórias, pontes basculantes, cordas, alavancas. "
                "Suporta PinJoint2D (ponto fixo) e GrooveJoint2D (trilho). "
                "Quando usar: para objetos que precisam de conexão física entre si. "
                "Pré-condições: ambos os nós devem existir na cena. "
                "Exemplo: {\"scene_path\": \"...\", \"node_a_path\": \"./Door\", \"node_b_path\": \"./Wall\", \"joint_type\": \"pin\"}. "
                "Erro mais comum: um dos nós não encontrado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "node_a_path": {"type": "string"},
                    "node_b_path": {"type": "string"},
                    "joint_type": {"type": "string", "enum": ["pin", "groove"]},
                    "softness": {"type": "number"},
                    "bias": {"type": "number"},
                },
                "required": ["scene_path", "node_a_path", "node_b_path"],
            },
        ),
        Tool(
            name="import_3d_model",
            description=(
                "Importa um modelo 3D (.glb/.gltf) e opcionalmente cria cena com MeshInstance3D. "
                "Use para trazer modelos 3D para o projeto. "
                "Quando usar: se o usuário fornecer um arquivo .glb/.gltf. "
                "Pré-condições: arquivo fonte deve existir; Godot 4.7 suporta glTF 2.0. "
                "Exemplo: {\"source_path\": \"C:/models/character.glb\", \"target_res_path\": \"assets/models/character.glb\"}. "
                "Erro mais comum: formato não suportado — use .glb ou .gltf."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source_path": {"type": "string"},
                    "target_res_path": {"type": "string"},
                    "create_scene": {"type": "boolean"},
                    "scene_name": {"type": "string"},
                },
                "required": ["source_path", "target_res_path"],
            },
        ),
        Tool(
            name="create_particles_2d",
            description=(
                "Adiciona GPUParticles2D com ParticleProcessMaterial a uma cena. "
                "Use para efeitos visuais: explosão, fumaça, sparkles, chuva, neve. "
                "Configura amount, lifetime, explosiveness, direction, spread, gravity. "
                "Quando usar: para qualquer efeito de partícula em jogos 2D. "
                "Pré-condições: cena e nó pai existentes. "
                "Exemplo: {\"scene_path\": \"...\", \"parent_node_path\": \".\", \"amount\": 100, \"lifetime\": 1.5}. "
                "Erro mais comum: partículas não visíveis sem run_game."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "node_name": {"type": "string"},
                    "amount": {"type": "integer"},
                    "lifetime": {"type": "number"},
                    "explosiveness": {"type": "number"},
                    "direction": {"type": "string"},
                    "spread": {"type": "number"},
                    "gravity": {"type": "string"},
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="create_light_2d",
            description=(
                "Adiciona PointLight2D ou DirectionalLight2D a uma cena. "
                "Use para iluminação 2D: tochas, lanternas, luz ambiente. "
                "Configura cor, energia (intensidade) e alcance (range_z). "
                "Quando usar: para melhorar a atmosfera visual com iluminação. "
                "Pré-condições: cena e nó pai existentes. "
                "Exemplo: {\"scene_path\": \"...\", \"parent_node_path\": \".\", \"light_type\": \"point\", \"color\": \"Color(1,0.8,0.4,1)\", \"energy\": 1.5}. "
                "Erro mais comum: luz invisível — verifique cor e energia."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "node_name": {"type": "string"},
                    "light_type": {"type": "string", "enum": ["point", "directional"]},
                    "color": {"type": "string"},
                    "energy": {"type": "number"},
                    "range_z": {"type": "number"},
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="setup_camera_2d",
            description=(
                "Adiciona e configura uma Camera2D com limites, zoom, drag e suavização. "
                "Use ao criar qualquer cena 2D que precise de câmera. "
                "Quando NÃO usar: se a cena já tem câmera configurada. "
                "Pré-condições: cena deve existir. "
                "Exemplo: {\"scene_path\": \"scenes/game.tscn\", \"limits\": {\"left\": 0, \"top\": 0, \"right\": 2560, \"bottom\": 1440}, \"smoothing_enabled\": true}. "
                "Erro mais comum: cena não encontrada — verifique o caminho."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "limits": {"type": "object"},
                    "drag_horizontal": {"type": "number"},
                    "drag_vertical": {"type": "number"},
                    "zoom": {"type": "array", "items": {"type": "number"}},
                    "smoothing_enabled": {"type": "boolean"},
                    "smoothing_speed": {"type": "number"},
                    "current": {"type": "boolean"},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="create_navigation_region_2d",
            description=(
                "Cria região de navegação 2D com polígono. Define área onde personagens podem andar. "
                "Use ao criar mapa com pathfinding. "
                "Depois use create_navigation_agent_2d para personagens que navegam. "
                "Exemplo: {\"scene_path\": \"...\", \"polygon_vertices\": [[0,0],[1280,0],[1280,720],[0,720]]}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "polygon_vertices": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}},
                    "region_name": {"type": "string"},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="create_navigation_agent_2d",
            description=(
                "Adiciona NavigationAgent2D com script de perseguição. O nó pai DEVE ser CharacterBody2D. "
                "Gera script que persegue o alvo usando pathfinding da NavigationRegion. "
                "Use para inimigos que perseguem o player ou NPCs com destino. "
                "Pré-condições: NavigationRegion2D já deve existir na cena. "
                "Exemplo: {\"scene_path\": \"...\", \"parent_node_path\": \"./Enemy\", \"target_node_path\": \"./Player\", \"speed\": 150}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string"},
                    "parent_node_path": {"type": "string"},
                    "agent_name": {"type": "string"},
                    "target_node_path": {"type": "string"},
                    "speed": {"type": "number"},
                    "avoidance_enabled": {"type": "boolean"},
                },
                "required": ["scene_path", "parent_node_path", "target_node_path"],
            },
        ),
        Tool(
            name="generate_project_structure",
            description=(
                "Gera a estrutura completa de pastas e arquivos base para um projeto Godot. "
                "Cria pastas padronizadas (scenes, scripts, assets), scene principal com nodes basicos, "
                "scripts boilerplate e arquivos de configuracao (.gitignore, README). "
                "Quando usar: no INICIO de um novo projeto, antes de criar qualquer cena. "
                "Templates disponiveis: '2d', '3d', 'mobile'. "
                "Exemplo: {\"template\": \"2d\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "template": {"type": "string", "description": "Tipo: '2d', '3d', ou 'mobile'"},
                    "project_path": {"type": "string", "description": "Caminho do projeto (opcional)"},
                },
            },
        ),
        Tool(
            name="record_gameplay_gif",
            description=(
                "Grava a tela do jogo por N segundos e retorna um GIF animado em base64. "
                "Usa Godot --write-movie para capturar frames e PIL para compor GIF. "
                "Quando usar: para a IA 'ver' o resultado visual do jogo e decidir proximos passos. "
                "Fallback: se PIL nao estiver instalado, retorna frames PNG individuais. "
                "Exemplo: {\"duration\": 5, \"fps\": 10, \"resolution_width\": 480, \"resolution_height\": 270}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "duration": {"type": "integer", "description": "Duracao em segundos (max 30)"},
                    "fps": {"type": "integer", "description": "Frames por segundo (menor = arquivo menor)"},
                    "resolution_width": {"type": "integer", "description": "Largura em pixels"},
                    "resolution_height": {"type": "integer", "description": "Altura em pixels"},
                },
            },
        ),
        # ── Onda 9: Polimento Visual ──
        Tool(
            name="create_parallax_background",
            description=(
                "Cria um fundo com efeito parallax (ParallaxBackground + multiplas camadas). "
                "Use para dar profundidade a jogos 2D: ceu, montanhas, nuvens em velocidades diferentes. "
                "Quando NAO usar: para fundos estaticos (use generate_background_gradient). "
                "Pre-condicoes: cena deve existir; texturas das camadas devem estar no projeto. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'layers': [{'texture': 'assets/bg_far.png', 'scroll_scale_x': 0.2}]}. "
                "Erro mais comum: textura nao encontrada — importe com import_texture primeiro."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena onde adicionar o parallax."},
                    "layers": {"type": "array", "items": {"type": "object"}, "description": "Lista de camadas [{texture, scroll_scale_x, scroll_scale_y, mirroring_x, mirroring_y}]."},
                    "parent_node_path": {"type": "string", "description": "No pai (default '.' = raiz)."},
                    "bg_name": {"type": "string", "description": "Nome do no ParallaxBackground."},
                },
                "required": ["scene_path", "layers"],
            },
        ),
        Tool(
            name="add_parallax_layer",
            description=(
                "Adiciona uma camada a um ParallaxBackground existente. "
                "Use para adicionar mais camadas de profundidade a um cenario parallax. "
                "Quando NAO usar: se ainda nao criou o ParallaxBackground (use create_parallax_background). "
                "Pre-condicoes: ParallaxBackground deve existir na cena; textura deve existir. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'parallax_bg_path': './ParallaxBackground', 'texture_path': 'assets/bg_mid.png', 'scroll_scale_x': 0.5}. "
                "Erro mais comum: ParallaxBackground nao encontrado — verifique o node_path."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parallax_bg_path": {"type": "string", "description": "Path do ParallaxBackground."},
                    "texture_path": {"type": "string", "description": "Caminho da textura (ex: assets/bg.png)."},
                    "scroll_scale_x": {"type": "number", "description": "Escala de scroll horizontal (0=fixo, 1=normal, default 0.5)."},
                    "scroll_scale_y": {"type": "number", "description": "Escala de scroll vertical (default 0.5)."},
                    "mirroring_x": {"type": "number", "description": "Repeticoes horizontais (0=sem mirroring)."},
                    "mirroring_y": {"type": "number", "description": "Repeticoes verticais (0=sem mirroring)."},
                    "layer_name": {"type": "string", "description": "Nome do no da camada."},
                },
                "required": ["scene_path", "parallax_bg_path", "texture_path"],
            },
        ),
        Tool(
            name="configure_particles_2d",
            description=(
                "Configura particulas 2D (GPUParticles2D) com parametros de emissao. "
                "Use para efeitos visuais: explosao, fumaca, sparkles, chuva, neve. "
                "Suporta presets: explosion, fire, smoke, rain, snow, sparkles, custom. "
                "Quando NAO usar: se o no nao for GPUParticles2D. "
                "Pre-condicoes: no GPUParticles2D deve existir na cena. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'node_path': './Explosion', 'preset': 'explosion', 'amount': 100, 'lifetime': 1.5}. "
                "Erro mais comum: particulas nao visiveis sem run_game — compile_test nao mostra efeitos."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "node_path": {"type": "string", "description": "Path do no GPUParticles2D."},
                    "amount": {"type": "integer", "description": "Quantidade de particulas (default 50)."},
                    "lifetime": {"type": "number", "description": "Tempo de vida em segundos (default 1.0)."},
                    "explosiveness": {"type": "number", "description": "0=continuo, 1=explosao unica (default 0)."},
                    "emitting": {"type": "boolean", "description": "Se esta emitindo (default true)."},
                    "one_shot": {"type": "boolean", "description": "Emite uma vez e para (default false)."},
                    "preset": {"type": "string", "description": "Preset: explosion, fire, smoke, rain, snow, sparkles, custom."},
                },
                "required": ["scene_path", "node_path"],
            },
        ),
        Tool(
            name="create_particles_3d",
            description=(
                "Adiciona GPUParticles3D a uma cena 3D com presets visuais. "
                "Use para fogo, fumaca, ou outros efeitos de particula em jogos 3D. "
                "Suporta presets: fire, smoke, sparkles, dust, rain. "
                "Pre-condicoes: cena 3D deve existir. "
                "Exemplo: {'scene_path': 'scenes/level.tscn', 'preset': 'fire', 'node_name': 'FireEffect'}. "
                "Erro mais comum: particulas nao visiveis — verifique iluminacao e camera 3D."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "No pai (default '.' = raiz)."},
                    "node_name": {"type": "string", "description": "Nome do no (default 'GPUParticles3D')."},
                    "preset": {"type": "string", "description": "Preset: fire, smoke, sparkles, dust, rain."},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="generate_shader_2d",
            description=(
                "Gera um shader 2D a partir de templates pre-definidos. "
                "Use para efeitos visuais avancados: glow, dissolve, outline, water, wind. "
                "O shader e salvo como arquivo .gdshader e aplicado ao no. "
                "Pre-condicoes: no alvo deve existir na cena. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'node_path': './Player/Sprite', 'template': 'glow'}. "
                "Erro mais comum: shader nao visivel — compile_test nao renderiza shaders; use run_game."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "node_path": {"type": "string", "description": "Path do no alvo."},
                    "template": {"type": "string", "description": "Template: glow, dissolve, outline, water, wind, grayscale, shockwave."},
                    "uniforms": {"type": "object", "description": "Valores de uniforms do shader (opcional)."},
                    "shader_name": {"type": "string", "description": "Nome do arquivo .gdshader (opcional)."},
                },
                "required": ["scene_path", "node_path", "template"],
            },
        ),
        Tool(
            name="create_path_2d",
            description=(
                "Cria um Path2D com PathFollow2D para movimentacao controlada por curva. "
                "Use para plataformas moveis, rotas de camera, ou animacoes de trajetoria. "
                "Pre-condicoes: cena deve existir. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'waypoints': [Vector2(0,0), Vector2(200,100), Vector2(400,0)], 'closed': true}. "
                "Erro mais comum: waypoints vazios — forneca pelo menos 2 pontos."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "No pai (default '.')."},
                    "waypoints": {"type": "array", "items": {"type": "string"}, "description": "Lista de pontos Vector2 (ex: ['Vector2(0,0)', 'Vector2(100,100)'])."},
                    "path_name": {"type": "string", "description": "Nome do no Path2D (default 'Path2D')."},
                    "closed": {"type": "boolean", "description": "Se o caminho e fechado (loop, default false)."},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="create_patrol_route",
            description=(
                "Cria uma rota de patrulha com waypoints e script de movimento automatico. "
                "Use para inimigos que patrulham, NPCs andando, ou objetos moveis em rotas. "
                "Suporta ping-pong (vai e volta) e pausa em cada waypoint. "
                "Pre-condicoes: cena e no pai devem existir. "
                "Exemplo: {'scene_path': 'scenes/game.tscn', 'parent_node_path': './Enemy', 'waypoints': ['Vector2(0,0)', 'Vector2(300,0)'], 'speed': 80, 'ping_pong': true}. "
                "Erro mais comum: waypoints em formato invalido — use 'Vector2(x, y)'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "No pai que recebera o script de patrulha."},
                    "waypoints": {"type": "array", "items": {"type": "string"}, "description": "Lista de posicoes Vector2."},
                    "speed": {"type": "number", "description": "Velocidade de movimento (default 100)."},
                    "wait_time": {"type": "number", "description": "Tempo de espera em cada waypoint (default 1.0s)."},
                    "ping_pong": {"type": "boolean", "description": "Vai e volta em vez de reiniciar (default true)."},
                },
                "required": ["scene_path", "parent_node_path", "waypoints"],
            },
        ),
        # ── Onda 10: Genero-Especifico ──
        Tool(
            name="create_bullet_template",
            description=(
                "Cria uma cena de projetil (bullet) reutilizavel para sistemas de tiro. "
                "Use em shooters, tower defense, ou qualquer jogo com armas de projetil. "
                "Define velocidade, dano, tempo de vida, cor e tamanho do projetil. "
                "Pre-condicoes: projeto ativo. "
                "Exemplo: {'bullet_name': 'Laser', 'speed': 800, 'damage': 25, 'bullet_color': '#ff0000'}. "
                "Erro mais comum: bullet nao aparece — verifique collision layers."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "bullet_name": {"type": "string", "description": "Nome do projetil (default 'Bullet')."},
                    "speed": {"type": "number", "description": "Velocidade em px/s (default 500)."},
                    "damage": {"type": "number", "description": "Dano causado (default 10)."},
                    "lifetime": {"type": "number", "description": "Tempo de vida em segundos (default 3.0)."},
                    "bullet_color": {"type": "string", "description": "Cor em hex (default '#ffff00')."},
                    "bullet_size": {"type": "integer", "description": "Tamanho em px (default 8)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="create_gun_system",
            description=(
                "Cria um script de sistema de arma com fire rate, municao, reload e spread. "
                "Use para armas do player ou inimigos: pistola, metralhadora, shotgun. "
                "Inclui controle de municao maxima, recarga automatica e angulo de dispersao. "
                "Pre-condicoes: bullet scene deve existir (use create_bullet_template). "
                "Exemplo: {'script_path': 'scripts/player_gun.gd', 'fire_rate': 0.2, 'ammo_max': 30, 'spread_angle': 5.0}. "
                "Erro mais comum: bullet_scene_path invalido — crie o projetil primeiro."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {"type": "string", "description": "Caminho para salvar o script da arma."},
                    "bullet_scene_path": {"type": "string", "description": "Caminho da cena do projetil (default 'res://scenes/bullet.tscn')."},
                    "fire_rate": {"type": "number", "description": "Intervalo entre tiros em segundos (default 0.3)."},
                    "ammo_max": {"type": "integer", "description": "Municao maxima (default 30)."},
                    "spread_angle": {"type": "number", "description": "Angulo de dispersao em graus (default 0 = tiro perfeito)."},
                    "auto_reload": {"type": "boolean", "description": "Recarga automatica quando vazio (default true)."},
                    "reload_time": {"type": "number", "description": "Tempo de recarga em segundos (default 1.5)."},
                },
                "required": ["script_path"],
            },
        ),
        Tool(
            name="generate_dungeon_rooms",
            description=(
                "Gera um layout procedural de dungeon com salas e corredores. "
                "Use para roguelikes, RPGs, ou qualquer jogo com masmorras aleatorias. "
                "Retorna dados das salas (posicao, tamanho) para spawn de inimigos/tesouros. "
                "Pre-condicoes: nenhuma (ferramenta de design, gera dados). "
                "Exemplo: {'num_rooms': 10, 'min_size': 5, 'max_size': 12, 'map_width': 80, 'map_height': 60, 'seed': 123}. "
                "Erro mais comum: nenhum — sempre retorna dados de layout."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "num_rooms": {"type": "integer", "description": "Numero de salas (default 8)."},
                    "min_size": {"type": "integer", "description": "Tamanho minimo da sala (default 5)."},
                    "max_size": {"type": "integer", "description": "Tamanho maximo da sala (default 12)."},
                    "map_width": {"type": "integer", "description": "Largura do mapa (default 80)."},
                    "map_height": {"type": "integer", "description": "Altura do mapa (default 60)."},
                    "corridor_width": {"type": "integer", "description": "Largura dos corredores (default 2)."},
                    "seed": {"type": "integer", "description": "Seed para reproducibilidade (default 0)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="load_scene_async",
            description=(
                "Carrega uma cena de forma assincrona com tela de loading. "
                "Use para transicoes suaves entre fases ou areas grandes. "
                "Mostra progresso real de carregamento na loading screen. "
                "Pre-condicoes: loading screen deve existir (use create_loading_screen). "
                "Exemplo: {'target_scene': 'res://scenes/level_2.tscn', 'loading_scene': 'res://scenes/loading_screen.tscn'}. "
                "Erro mais comum: loading_scene nao encontrada — crie com create_loading_screen."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "target_scene": {"type": "string", "description": "Caminho da cena a carregar (ex: 'res://scenes/level.tscn')."},
                    "loading_scene": {"type": "string", "description": "Caminho da loading screen (default 'res://scenes/loading_screen.tscn')."},
                },
                "required": ["target_scene"],
            },
        ),
        # ── Onda 11: Complementos ──
        Tool(
            name="add_raycast_2d",
            description=(
                "Adiciona um RayCast2D a um no para deteccao de linha de visao. "
                "Use para: verificar se ha chao a frente, detectar obstaculos, mirar armas. "
                "Configura posicao alvo (target_position), collision_mask e enabled. "
                "Pre-condicoes: cena e no pai devem existir. "
                "Exemplo: {'scene_path': 'scenes/player.tscn', 'parent_node_path': '.', 'target_position': 'Vector2(100, 0)', 'collision_mask': 2}. "
                "Erro mais comum: raycast nao detecta nada — verifique collision_mask e layers."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "No pai que recebera o RayCast2D."},
                    "target_position": {"type": "string", "description": "Posicao alvo (ex: 'Vector2(100, 0)')."},
                    "collision_mask": {"type": "integer", "description": "Mascara de colisao (default 1)."},
                    "enabled": {"type": "boolean", "description": "Se esta ativo (default true)."},
                    "node_name": {"type": "string", "description": "Nome do no (default 'RayCast2D')."},
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="add_shapecast_2d",
            description=(
                "Adiciona um ShapeCast2D para deteccao de area em linha. "
                "Use para deteccao mais robusta que RayCast: ataques melee, sensores de chao largos. "
                "Suporta formas: rectangle, circle, capsule. "
                "Pre-condicoes: cena e no pai devem existir. "
                "Exemplo: {'scene_path': 'scenes/player.tscn', 'parent_node_path': '.', 'shape_type': 'rectangle', 'shape_size': 'Vector2(40, 10)'}. "
                "Erro mais comum: shape_size invalido — use 'Vector2(w, h)'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "No pai."},
                    "shape_type": {"type": "string", "description": "Forma: rectangle, circle, capsule (default 'rectangle')."},
                    "shape_size": {"type": "string", "description": "Tamanho (ex: 'Vector2(40, 10)')."},
                    "collision_mask": {"type": "integer", "description": "Mascara de colisao (default 1)."},
                    "node_name": {"type": "string", "description": "Nome do no (default 'ShapeCast2D')."},
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="setup_localization",
            description=(
                "Configura o sistema de traducao (i18n) do projeto. "
                "Use para jogos com suporte a multiplos idiomas (ex: PT-BR, EN, ES). "
                "Cria arquivos de traducao CSV e configura o TranslationServer. "
                "Pre-condicoes: projeto ativo. "
                "Exemplo: {'default_locale': 'pt_BR', 'additional_locales': ['en', 'es']}. "
                "Erro mais comum: traducoes nao aparecem — use add_translation_string para cada texto."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "default_locale": {"type": "string", "description": "Localidade padrao (default 'pt_BR')."},
                    "additional_locales": {"type": "array", "items": {"type": "string"}, "description": "Localidades adicionais (ex: ['en', 'es'])."},
                },
                "required": [],
            },
        ),
        Tool(
            name="add_translation_string",
            description=(
                "Adiciona uma string traduzida ao sistema de localizacao. "
                "Use para cada texto que aparece na UI: botoes, labels, dialogos. "
                "Forneca as traducoes como dicionario {locale: texto}. "
                "Pre-condicoes: setup_localization deve ter sido chamado. "
                "Exemplo: {'key': 'BTN_PLAY', 'translations': {'pt_BR': 'Jogar', 'en': 'Play', 'es': 'Jugar'}}. "
                "Erro mais comum: key duplicada — use keys unicas."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Chave da string (ex: 'BTN_PLAY', 'TXT_WELCOME')."},
                    "translations": {"type": "object", "description": "Dicionario {locale: texto}."},
                },
                "required": ["key", "translations"],
            },
        ),
        Tool(
            name="create_light_3d",
            description=(
                "Adiciona uma luz 3D (OmniLight3D, SpotLight3D ou DirectionalLight3D) a uma cena. "
                "Use para iluminar cenas 3D: tochas, lanternas, luz solar. "
                "Configura cor, energia (intensidade) e sombras. "
                "Pre-condicoes: cena 3D deve existir. "
                "Exemplo: {'scene_path': 'scenes/level.tscn', 'light_type': 'spot', 'color': '#ffaa44', 'energy': 2.0, 'shadows': true}. "
                "Erro mais comum: luz nao visivel — verifique cor e energia (valores baixos = escuro)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "No pai (default '.')."},
                    "light_type": {"type": "string", "description": "Tipo: omni, spot, directional (default 'omni')."},
                    "color": {"type": "string", "description": "Cor em hex (default '#ffffff')."},
                    "energy": {"type": "number", "description": "Intensidade (default 1.0)."},
                    "shadows": {"type": "boolean", "description": "Ativar sombras (default false)."},
                    "node_name": {"type": "string", "description": "Nome do no (vazio = auto)."},
                },
                "required": ["scene_path"],
            },
        ),
        Tool(
            name="configure_standard_material_3d",
            description=(
                "Aplica e configura um StandardMaterial3D a um MeshInstance3D. "
                "Use para definir aparencia de objetos 3D: cor, metallic, roughness. "
                "Suporta presets: metal, plastic, wood, stone, glass, emissive, custom. "
                "Pre-condicoes: no alvo deve ser MeshInstance3D. "
                "Exemplo: {'scene_path': 'scenes/level.tscn', 'node_path': './Cube', 'preset': 'metal'}. "
                "Erro mais comum: no nao e MeshInstance3D — verifique o tipo do no."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "node_path": {"type": "string", "description": "Path do MeshInstance3D."},
                    "preset": {"type": "string", "description": "Preset: metal, plastic, wood, stone, glass, emissive, custom."},
                },
                "required": ["scene_path", "node_path"],
            },
        ),
        Tool(
            name="configure_export_preset",
            description=(
                "Configura um preset de exportacao (Windows, Linux, macOS, Web, Android). "
                "Use antes de build_export para definir nome do app, versao, icone e empresa. "
                "Pre-condicoes: projeto ativo. "
                "Exemplo: {'preset_name': 'Windows Desktop', 'app_name': 'Meu Jogo', 'version': '1.0.0', 'company': 'MeuEstudio'}. "
                "Erro mais comum: preset_name invalido — use um dos presets suportados pelo Godot."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "preset_name": {"type": "string", "description": "Nome do preset (default 'Windows Desktop')."},
                    "app_name": {"type": "string", "description": "Nome do aplicativo."},
                    "version": {"type": "string", "description": "Versao (ex: '1.0.0')."},
                    "icon_path": {"type": "string", "description": "Caminho do icone .ico/.png."},
                    "company": {"type": "string", "description": "Nome da empresa/estudio."},
                },
                "required": [],
            },
        ),
        # ── Onda 7: Robustez (saude e autoteste) ──
        Tool(
            name="health_check",
            description=(
                "Verifica a saude de todos os componentes do MCP: config.json, Godot, ClassDB, templates, projeto ativo. "
                "Use no inicio de sessoes para diagnosticar problemas de configuracao. "
                "Retorna status de cada componente e veredito geral (saudavel ou nao). "
                "Pre-condicoes: nenhuma. "
                "Exemplo: {} (chamada sem argumentos). "
                "Erro mais comum: Godot nao encontrado — verifique godot_path no config.json."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="self_test",
            description=(
                "Executa uma suite de testes internos do MCP: ping, ClassDB, godot_parser, jinja2, Pillow. "
                "Use para verificar se todas as dependencias estao funcionais. "
                "Retorna resultados individuais e veredito geral (todos passaram ou nao). "
                "Pre-condicoes: nenhuma. "
                "Exemplo: {} (chamada sem argumentos). "
                "Erro mais comum: Pillow/Jinja2 nao instalados — algumas funcionalidades ficam limitadas."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        # ── PATCH 16: Asset Manifest ─────────────────────────
        Tool(
            name="import_asset_manifest",
            description=(
                "Importa TODOS os assets listados no asset_manifest.json do projeto. "
                "Suporta 5 fontes: generate (IA), placeholder (procedural), sfx (audio), "
                "import (arquivo local), download (CC0 da web). "
                "Use dry_run=True para validar o manifest sem importar. "
                "Pre-condicoes: asset_manifest.json na raiz do projeto. "
                "Exemplo: {} (processa o manifest padrao). "
                "Exemplo: {\"dry_run\": true} (apenas valida)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "manifest_path": {"type": "string", "description": "Caminho para o manifest (opcional)."},
                    "project_path": {"type": "string", "description": "Caminho do projeto (opcional)."},
                    "dry_run": {"type": "boolean", "description": "Apenas valida, nao importa (default: false)."},
                    "allow_paid_generation": {"type": "boolean", "description": "Permite source='generate' (pode custar $$). Default: false."},
                },
                "required": [],
            },
        ),
        Tool(
            name="create_asset_manifest",
            description=(
                "Gera um template de asset_manifest.json no projeto com exemplos. "
                "Use para iniciar a configuracao de assets em lote. "
                "Pre-condicoes: projeto ativo configurado. "
                "Exemplo: {} (cria template). "
                "Exemplo: {\"overwrite\": true} (sobrescreve existente)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho do projeto (opcional)."},
                    "overwrite": {"type": "boolean", "description": "Sobrescrever existente (default: false)."},
                },
                "required": [],
            },
        ),
        # ── PATCH 15: Validacao de Referencias ────────────────
        Tool(
            name="validate_project_refs",
            description=(
                "Valida TODAS as referencias cruzadas no projeto Godot: ext_resource, "
                "sub_resource, nodes (script/textura/mesh), preload/load/ResourceLoader.load. "
                "NAO requer Godot rodando — analise estatica dos arquivos. "
                "Retorna erros (quebrados) e warnings com localizacao exata. "
                "Use apos edicoes em lote para garantir integridade. "
                "Pre-condicoes: projeto ativo configurado. "
                "Exemplo: {\"full_report\": true} (relatorio completo sem truncar)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho do projeto (opcional)."},
                    "full_report": {"type": "boolean", "description": "Relatorio completo sem truncar (default: false)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="find_usages",
            description=(
                "Encontra TODOS os usos de um recurso/alvo no projeto (estatico, sem LSP). "
                "Busca em .tscn (ExtResource, scene instances) e .gd (preload/load). "
                "NAO requer Godot rodando. "
                "Use para rastrear dependencias antes de renomear ou deletar. "
                "Pre-condicoes: projeto ativo configurado. "
                "Exemplo: {\"target\": \"player.gd\"}. "
                "Exemplo: {\"target\": \"main_menu.tscn\", \"search_type\": \"scene\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Nome do arquivo ou path parcial (ex: player.gd)."},
                    "project_path": {"type": "string", "description": "Caminho do projeto (opcional)."},
                    "search_type": {"type": "string", "description": "auto, script, scene, texture, any (default: auto)."},
                    "max_results": {"type": "integer", "description": "Limite de resultados (default: 50)."},
                },
                "required": ["target"],
            },
        ),
        # ── Grupo C: Detecção de recursos não usados ───────────
        Tool(
            name="find_unused_resources",
            description=(
                "Encontra assets que existem no projeto mas nao sao referenciados "
                "por nenhum .tscn, .gd ou .tres (orfaos). "
                "Varre imagens, audio, modelos 3D, .tres e fontes. "
                "Use para limpar o projeto antes do lancamento. "
                "NAO requer Godot rodando — analise estatica de arquivos. "
                "Exemplo: {\"project_path\": \"C:\\\\...\\\\star-colony\"}. "
                "Exemplo: {\"asset_types\": [\"image\", \"audio\"]}. "
                "Erro mais comum: assets referenciados via codigo dinamico "
                "(string montada em runtime) podem ser falsos positivos."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho do projeto."},
                    "asset_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tipos: image, audio, model, resource, font (default: todos).",
                    },
                    "exclude_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Pastas a excluir (default: addons/, .godot/, .git/, _backups/, build/).",
                    },
                    "min_size_bytes": {"type": "integer", "description": "Tamanho minimo em bytes (default: 0)."},
                },
                "required": [],
            },
        ),
        # ── Grupo C: Análise de fluxo de sinal ─────────────────
        Tool(
            name="analyze_signal_flow",
            description=(
                "Analisa conexoes de sinal no projeto: detecta sinais conectados "
                "a metodos que nao existem mais (orfaos pos-refatoracao) e sinais "
                "declarados mas nunca conectados. "
                "NAO requer Godot rodando — analise estatica de .tscn e .gd. "
                "Use para limpar conexoes quebradas antes do lancamento. "
                "Exemplo: {\"project_path\": \"C:\\\\...\\\\star-colony\"}. "
                "Exemplo: {\"scene_path\": \"scenes/main.tscn\"}. "
                "Limitacao: nao detecta conexoes feitas via connect() em codigo."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho do projeto."},
                    "scene_path": {"type": "string", "description": "Caminho de uma cena especifica (opcional — default: varre todo o projeto)."},
                },
                "required": [],
            },
        ),
        # ── Bloco 1: Auditoria de Wiring ──
        Tool(
            name="audit_input_map",
            description=(
                "Audita o Input Map do projeto: lista acoes declaradas, "
                "acoes nao usadas e acoes referenciadas mas nao declaradas. "
                "NAO requer Godot rodando — analise estatica do project.godot. "
                "Exemplo: {\"project_path\": \"C:\\\\...\\\\projeto\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho do projeto."},
                },
                "required": [],
            },
        ),
        Tool(
            name="audit_autoloads",
            description=(
                "Audita os Autoloads do projeto: lista autoloads registrados "
                "e detecta autoloads possivelmente nao usados. "
                "NAO requer Godot rodando — analise estatica. "
                "Exemplo: {\"project_path\": \"C:\\\\...\\\\projeto\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho do projeto."},
                },
                "required": [],
            },
        ),
        Tool(
            name="audit_scene_reachability",
            description=(
                "Audita a alcançabilidade de cenas: partindo da cena principal, "
                "detecta cenas que nao sao referenciadas por nenhuma outra (orfas). "
                "NAO requer Godot rodando — analise estatica. "
                "Exemplo: {\"project_path\": \"C:\\\\...\\\\projeto\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho do projeto."},
                    "root_scene": {"type": "string", "description": "Cena raiz. Default: main_scene do project.godot."},
                },
                "required": [],
            },
        ),
        # ── Bloco 2: UID + Save Compatibility ──
        Tool(
            name="audit_uid_consistency",
            description=(
                "Audita a consistencia de UIDs no projeto: detecta UIDs duplicados, "
                "UIDs com mismatch entre .uid e .import, e UIDs nao resolvidos. "
                "NAO requer Godot rodando. "
                "Exemplo: {\"project_path\": \"C:\\\\...\\\\projeto\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho do projeto."},
                },
                "required": [],
            },
        ),
        Tool(
            name="audit_save_compatibility",
            description=(
                "Audita a compatibilidade de save: verifica se o SaveManager "
                "tem campo de versao e logica de migracao. Detecta chaves "
                "write/read inconsistentes e chaves orfas. "
                "NAO requer Godot rodando. "
                "Exemplo: {\"project_path\": \"C:\\\\...\\\\projeto\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho do projeto."},
                    "save_file_path": {"type": "string", "description": "Caminho de um save file para testar (opcional)."},
                },
                "required": [],
            },
        ),
        # ── Grupo C: Auto-dismiss ──────────────────────────────
        Tool(
            name="set_auto_dismiss",
            description=(
                "Liga/desliga o fechamento automatico de dialogos modais "
                "durante testes automatizados. Use antes de run_stress_test. "
                "Pre-condicoes: jogo rodando via godot_run_project."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean", "description": "Ativar (true) ou desativar."},
                    "action": {"type": "string", "description": "confirm, cancel ou hide (default: hide)."},
                    "check_interval_ms": {"type": "integer", "description": "Intervalo em ms (default: 500)."},
                },
                "required": [],
            },
        ),
        # ── Shader Editor ──────────────────────────────────────
        Tool(
            name="read_shader",
            description="Le o conteudo de um arquivo .gdshader existente.",
            inputSchema={
                "type": "object",
                "properties": {
                    "shader_path": {"type": "string"},
                    "project_path": {"type": "string"},
                },
                "required": ["shader_path"],
            },
        ),
        Tool(
            name="get_shader_params",
            description="Extrai as declaracoes uniform de um shader.",
            inputSchema={
                "type": "object",
                "properties": {
                    "shader_path": {"type": "string"},
                    "project_path": {"type": "string"},
                },
                "required": ["shader_path"],
            },
        ),
        Tool(
            name="edit_shader",
            description="Edita .gdshader com validacao antes de escrever.",
            inputSchema={
                "type": "object",
                "properties": {
                    "shader_path": {"type": "string"},
                    "new_code": {"type": "string"},
                    "project_path": {"type": "string"},
                    "validate": {"type": "boolean"},
                },
                "required": ["shader_path", "new_code"],
            },
        ),
        # ── PATCH 14: Testes Roteirizados ──────────────────────
        Tool(
            name="run_scripted_tests",
            description=(
                "Executa cenarios de teste roteirizados com input sintetico. "
                "NAO requer Godot rodando — testa as tools do MCP diretamente. "
                "Use para validar correcoes, smoke tests e regressao. "
                "Cada cenario define steps com tool/args/expect. "
                "Pre-condicoes: nenhuma. "
                "Exemplo: {} (executa smoke + regression padrao). "
                "Exemplo avancado: {\"scenarios\": [{\"name\":\"meu-teste\",\"steps\":[{\"tool\":\"ping\",\"args\":{},\"expect\":{\"status\":\"success\"}}]}]}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scenarios": {
                        "type": "array",
                        "description": "Lista de cenarios customizados (opcional).",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "steps": {
                                    "type": "array",
                                    "items": {"type": "object"}
                                }
                            }
                        }
                    },
                    "stop_on_failure": {"type": "boolean", "description": "Parar no primeiro cenario que falhar (default: false)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="smoke_test",
            description=(
                "Smoke test rapido: valida pipeline core do MCP (ping, ClassDB, validacao, config). "
                "NAO requer Godot rodando. Ideal para inicio de sessao. "
                "Retorna status de cada componente e veredito geral. "
                "Pre-condicoes: nenhuma. "
                "Exemplo: {} (chamada sem argumentos)."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="regression_test",
            description=(
                "Teste de regressao: valida correcoes dos GRUPOS 1 e 2 (write_file .gd, R2, GUT skipped). "
                "NAO requer Godot rodando. "
                "Retorna status de cada validacao e veredito geral. "
                "Pre-condicoes: nenhuma. "
                "Exemplo: {} (chamada sem argumentos)."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="dump_mcp_state",
            description=(
                "Captura snapshot completo do estado do MCP: config, tool counts, caches, imports, git. "
                "Util para debugging e comparacao entre maquinas. "
                "NAO requer Godot rodando. "
                "Pre-condicoes: nenhuma. "
                "Exemplo: {} (chamada sem argumentos)."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="estimate_tool_tokens",
            description=(
                "Estima o consumo de tokens do tools/list para cada perfil de ferramentas. "
                "Mede o tamanho do JSON que seria enviado no tools/list inicial "
                "e converte para tokens (~4 chars por token em JSON). "
                "QUANDO USAR: para decidir entre perfis (core=16 tools/~2K tokens, "
                "dev=31/~5K, full=189/~18K) ou verificar impacto de adicionar toolsets. "
                "NAO requer Godot rodando — é puramente analítico. "
                "Pre-condicoes: nenhuma. "
                "Exemplo: {\"profile\": \"dev\"}. "
                "Erro mais comum: perfil inválido — use core, dev ou full."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "profile": {
                        "type": "string",
                        "description": "Perfil a estimar: core (16 tools), dev (31), ou full (189, default)."
                    },
                },
                "required": [],
            },
        ),
        # ── LSP Bridge (Fase 2A / C3) ──────────────────────────
        Tool(
            name="gdscript_lsp_connect",
            description=(
                "Conecta ao Language Server do Godot na porta 6005. "
                "Use no início da sessão, após abrir o editor Godot com o projeto. "
                "Quando NÃO usar: se o editor não estiver aberto (a conexão falhará). "
                "Pré-condições: Godot editor ABERTO com o projeto carregado. "
                "Exemplo: {\"project_root\": \"C:/meu-jogo\"}. "
                "Erro mais comum: conexão recusada — verifique se o Godot está aberto."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_root": {"type": "string", "description": "Caminho raiz do projeto (opcional)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="gdscript_lsp_disconnect",
            description=(
                "Desconecta do Language Server do Godot. "
                "Use ao finalizar a sessão ou antes de fechar o editor."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="gdscript_references",
            description=(
                "Encontra todas as referências a um símbolo GDScript (variável, função, classe). "
                "Use para rastrear usos antes de renomear ou refatorar. "
                "Pré-condições: LSP conectado via gdscript_lsp_connect. "
                "Exemplo: {\"file_path\": \"scripts/player.gd\", \"line\": 10, \"character\": 5}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Caminho do arquivo .gd."},
                    "line": {"type": "integer", "description": "Linha (0-indexed)."},
                    "character": {"type": "integer", "description": "Posição do caractere (0-indexed)."},
                },
                "required": ["file_path", "line", "character"],
            },
        ),
        Tool(
            name="gdscript_definition",
            description=(
                "Navega para a definição de um símbolo GDScript. "
                "Use para encontrar onde uma variável, função ou classe foi declarada. "
                "Pré-condições: LSP conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Caminho do arquivo .gd."},
                    "line": {"type": "integer", "description": "Linha (0-indexed)."},
                    "character": {"type": "integer", "description": "Posição do caractere (0-indexed)."},
                },
                "required": ["file_path", "line", "character"],
            },
        ),
        Tool(
            name="gdscript_hover",
            description=(
                "Exibe tipo e documentação de um símbolo GDScript sob o cursor. "
                "Use para inspecionar tipo de variável ou assinatura de função. "
                "Pré-condições: LSP conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Caminho do arquivo .gd."},
                    "line": {"type": "integer", "description": "Linha (0-indexed)."},
                    "character": {"type": "integer", "description": "Posição do caractere (0-indexed)."},
                },
                "required": ["file_path", "line", "character"],
            },
        ),
        Tool(
            name="gdscript_symbols",
            description=(
                "Lista símbolos (funções, classes, variáveis) de um arquivo GDScript. "
                "Use para obter índice estrutural do código. "
                "Pré-condições: LSP conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Caminho do arquivo .gd."},
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="gdscript_rename",
            description=(
                "Renomeia um símbolo GDScript em TODO o projeto com segurança semântica. "
                "Diferente de grep/replace, o LSP entende escopo e não quebra referências. "
                "Quando NÃO usar: se não tiver certeza do escopo (use gdscript_references antes). "
                "Pré-condições: LSP conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Caminho do arquivo .gd."},
                    "line": {"type": "integer", "description": "Linha (0-indexed)."},
                    "character": {"type": "integer", "description": "Posição do caractere (0-indexed)."},
                    "new_name": {"type": "string", "description": "Novo nome para o símbolo."},
                },
                "required": ["file_path", "line", "character", "new_name"],
            },
        ),
        Tool(
            name="gdscript_diagnostics",
            description=(
                "Retorna erros e warnings do compilador GDScript via LSP. "
                "Mais preciso que validate_gdscript_syntax (tempo real, contextual). "
                "Pré-condições: LSP conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Caminho do arquivo .gd."},
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="gdscript_sync_file",
            description=(
                "Notifica o LSP sobre alterações em um arquivo GDScript. "
                "Use após write_file para manter o LSP sincronizado. "
                "Pré-condições: LSP conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Caminho do arquivo .gd."},
                    "content": {"type": "string", "description": "Conteúdo atualizado (se omitido, lê do disco)."},
                },
                "required": ["file_path"],
            },
        ),
        # ── Addon Bridge (Fase 2B / A2) ────────────────────────
        Tool(
            name="addon_connect",
            description=(
                "Conecta ao addon GDScript via WebSocket na porta 9082. "
                "Use após abrir o Godot com o addon MCP instalado. "
                "Pré-condições: Godot editor ABERTO com addon MCP ativo."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="addon_disconnect",
            description="Desconecta do addon GDScript.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="addon_is_available",
            description=(
                "Verifica se o addon GDScript está conectado e respondendo. "
                "Use para decidir entre modo editor (addon) ou file-based."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="addon_ping",
            description="Verifica se o addon GDScript está respondendo (ping/pong).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="addon_create_node",
            description=(
                "Cria um nó na cena atual do editor Godot com UndoRedo NATIVO (Ctrl+Z funciona). "
                "Use para adicionar nós visualmente no editor — é a versão ao vivo de node_manage.create. "
                "Quando NÃO usar: se o addon não estiver disponível (use node_manage.create para file-based). "
                "Pré-condições: addon conectado via addon_connect. "
                "Exemplo: {\"parent_path\": \"/root/Main\", \"node_type\": \"Sprite2D\", \"node_name\": \"Player\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "parent_path": {"type": "string", "description": "Path do nó pai (ex: /root/Main)."},
                    "node_type": {"type": "string", "description": "Tipo Godot (ex: Sprite2D)."},
                    "node_name": {"type": "string", "description": "Nome do novo nó."},
                    "properties": {"type": "object", "description": "Propriedades iniciais (opcional)."},
                    "scene_path": {"type": "string", "description": "Cena alvo (opcional)."},
                },
                "required": ["parent_path", "node_type", "node_name"],
            },
        ),
        Tool(
            name="addon_delete_node",
            description=(
                "Remove um nó da cena do editor com UndoRedo nativo. "
                "Pré-condições: addon conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {"node_path": {"type": "string", "description": "Path absoluto do nó."}},
                "required": ["node_path"],
            },
        ),
        Tool(
            name="addon_set_property",
            description=(
                "Define uma propriedade de nó no editor com UndoRedo nativo. "
                "Use para ajustar posição, escala, cor, etc. com feedback visual imediato. "
                "Pré-condições: addon conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node_path": {"type": "string", "description": "Path do nó."},
                    "property_name": {"type": "string", "description": "Nome da propriedade."},
                    "value": {"type": "string", "description": "Valor (tipos Godot serializados como JSON)."},
                },
                "required": ["node_path", "property_name", "value"],
            },
        ),
        Tool(
            name="addon_reparent_node",
            description=(
                "Move um nó para outro pai no editor com UndoRedo nativo. "
                "Pré-condições: addon conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node_path": {"type": "string", "description": "Path do nó a mover."},
                    "new_parent_path": {"type": "string", "description": "Path do novo pai."},
                },
                "required": ["node_path", "new_parent_path"],
            },
        ),
        Tool(
            name="addon_duplicate_node",
            description=(
                "Duplica um nó no editor com UndoRedo nativo. "
                "Pré-condições: addon conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node_path": {"type": "string", "description": "Path do nó a duplicar."},
                    "new_name": {"type": "string", "description": "Nome da cópia (opcional)."},
                },
                "required": ["node_path"],
            },
        ),
        Tool(
            name="addon_batch_edit",
            description=(
                "Executa MÚLTIPLAS operações no editor em UMA ação UndoRedo. "
                "1 Ctrl+Z desfaz TUDO. Ideal para criar estruturas complexas. "
                "Exemplo: [{\"method\": \"create_node\", \"params\": {...}}, ...]. "
                "Pré-condições: addon conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "operations": {
                        "type": "array",
                        "description": "Lista de operações [{method, params}, ...].",
                        "items": {"type": "object"},
                    },
                },
                "required": ["operations"],
            },
        ),
        Tool(
            name="addon_take_screenshot",
            description=(
                "Captura screenshot do viewport do editor Godot via addon. "
                "Alternativa ao take_screenshot (TCP bridge) — funciona via WebSocket. "
                "Pré-condições: addon conectado."
            ),
            inputSchema={
                "type": "object",
                "properties": {"viewport": {"type": "string", "description": "'editor' (padrão) ou path."}},
                "required": [],
            },
        ),
        Tool(
            name="addon_get_scene_tree",
            description=(
                "Obtém a árvore da cena atual do editor via addon. "
                "Retorna estrutura hierárquica completa com tipos e paths. "
                "Pré-condições: addon conectado."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        # ── Playtest (Fase 2B / A3+A4+A5) ──────────────────────
        Tool(
            name="freeze_game_clock",
            description="Congela o relogio do jogo. Use antes de step_game_time para playtesting deterministico.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="unfreeze_game_clock",
            description="Descongela o relogio do jogo (retoma execucao normal).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="step_game_time",
            description="Avanca o jogo em N ms e congela novamente. Ex: 500ms = meio segundo de jogo processado.",
            inputSchema={
                "type": "object",
                "properties": {"ms": {"type": "integer", "description": "Milissegundos (default: 16)."}},
                "required": [],
            },
        ),
        Tool(
            name="step_until",
            description="Avanca o jogo ate que uma condicao GDScript seja verdadeira. Com timeout.",
            inputSchema={
                "type": "object",
                "properties": {
                    "condition": {"type": "string", "description": "Expressao GDScript que retorna bool."},
                    "timeout_ms": {"type": "integer", "description": "Timeout em ms (default: 5000)."},
                },
                "required": ["condition"],
            },
        ),
        Tool(
            name="get_runtime_state_digest",
            description="Retorna estado do jogo como JSON: posicao, velocidade, grupos de todas as entidades.",
            inputSchema={
                "type": "object",
                "properties": {"groups": {"type": "array", "items": {"type": "string"}, "description": "Grupos a filtrar."}},
                "required": [],
            },
        ),
        Tool(
            name="capture_runtime_errors",
            description="Captura informacoes de runtime: FPS, contagem de objetos, estado da arvore.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        # ── Playtest Onda 3 (smoke test do jogo) ────────────────
        Tool(
            name="playtest_manage",
            description=(
                "🎮 Playtest automatizado do jogo (ONDA 3). "
                "Operacoes: smoke (teste de sanidade: FPS, crash, viewport) e "
                "persona_run (persona scriptada joga o jogo: apressado, cauteloso, explorador). "
                "Usa o runtime bridge (porta 8790) — requer jogo rodando em debug (F5 no Godot). "
                "Quando usar: validar que o jogo esta saudavel (smoke) ou testar "
                "jogabilidade com perfis diferentes de jogador (persona_run). "
                "Exemplo smoke: {\"op\": \"smoke\", \"duration\": 10, \"fps_threshold\": 30}. "
                "Exemplo persona: {\"op\": \"persona_run\", \"persona\": \"apressado\", \"duration\": 60}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "op": {
                        "type": "string",
                        "description": "Operacao: 'smoke', 'persona_run', 'agent_observe', 'agent_step', 'agent_run', 'gate_first_5min', 'gate_status' ou 'full_suite'.",
                        "enum": ["smoke", "persona_run", "agent_observe", "agent_step", "agent_run", "gate_first_5min", "gate_status", "full_suite"],
                    },
                    "duration": {
                        "type": "integer",
                        "description": "Segundos de duracao (smoke default: 10, persona default: 60).",
                    },
                    "fps_threshold": {
                        "type": "integer",
                        "description": "FPS minimo aceitavel (para op='smoke', default: 30).",
                    },
                    "persona": {
                        "type": "string",
                        "description": "ID da persona para op='persona_run': 'apressado', 'cauteloso' ou 'explorador'.",
                        "enum": ["apressado", "cauteloso", "explorador"],
                    },
                    "action": {
                        "type": "string",
                        "description": "Acao para op='agent_step': ui_right, ui_left, ui_up, ui_down, space, ui_accept, etc.",
                    },
                    "hold_ms": {
                        "type": "integer",
                        "description": "Milissegundos de hold para op='agent_step' (default: 200).",
                    },
                    "steps": {
                        "type": "integer",
                        "description": "Numero de passos para op='agent_run' (default: 5, max: 20).",
                    },
                    "model": {
                        "type": "string",
                        "description": "Modelo DeepSeek para op='agent_run': 'deepseek-v4-flash' (mais barato) ou 'deepseek-v4-pro'.",
                        "enum": ["deepseek-v4-flash", "deepseek-v4-pro"],
                    },
                },
                "required": [],
            },
        ),
        # ── Fun Report (ONDA 3 — Fatia 3.D) ──────────────────────
        Tool(
            name="fun_report_manage",
            description=(
                "📊 Relatorio de qualidade do jogo com 4 sinais (ONDA 3 — Fatia 3.D). "
                "Analisa taxa de aprovacao, tentativas, variedade de estrategia e escalada. "
                "Nomeia modos de falha do core loop (sem escalada, estrategia degenerada, "
                "recompensa distante, pico de dificuldade) em vez de dizer 'esta chato'. "
                "NAO requer jogo rodando — analisa dados ja coletados por smoke/persona/agent. "
                "Quando usar: apos rodar playtest, para obter diagnostico de qualidade. "
                "Operacoes: generate (gera relatorio completo com recomendacoes). "
                "Exemplo: {\"op\": \"generate\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "op": {
                        "type": "string",
                        "description": "Operacao: 'generate'.",
                        "enum": ["generate"],
                    },
                },
                "required": [],
            },
        ),
        # ── Complexity Gate (ONDA 3 — Fatia 3.F) ────────────────
        Tool(
            name="complexity_gate_manage",
            description=(
                "📏 Gate de divida de complexidade (ONDA 3 — Fatia 3.F). "
                "Mede scripts .gd e linhas de codigo por fase. "
                "Bloqueia avanco se complexidade crescer >50%% sem justificativa. "
                "Operacoes: baseline (salva snapshot), check (compara com baseline). "
                "Exemplo baseline: {\"op\": \"baseline\"}. "
                "Exemplo check: {\"op\": \"check\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "op": {
                        "type": "string",
                        "description": "Operacao: 'baseline' ou 'check'.",
                        "enum": ["baseline", "check"],
                    },
                },
                "required": [],
            },
        ),
        # ── Modo Professor (ONDA 3 — Fatia 3.H) ────────────────
        Tool(
            name="teacher_manage",
            description=(
                "📚 Modo professor (ONDA 3 — Fatia 3.H). "
                "Explica de forma didatica o que foi feito e por que. "
                "Reduz dependencia da IA ao ensinar o desenvolvedor. "
                "Operacoes: explain. "
                "Exemplo: {\"op\": \"explain\", \"context\": \"criar um inimigo com patrulha\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "op": {"type": "string", "description": "Operacao: 'explain'.", "enum": ["explain"]},
                    "context": {"type": "string", "description": "Descricao do que foi feito."},
                },
                "required": [],
            },
        ),
        # ── Scope + Disclosure + Reviewer (ONDA 3 — 3.I/3.J/3.K) ─
        Tool(
            name="scope_manage",
            description=(
                "🎯 Validador de escopo + Disclosure IA (ONDA 3 — 3.I + 3.J). "
                "validate_idea: transforma 'nao da' em contraproposta. "
                "disclosure: gera declaracao de uso de IA para Steam/itch.io. "
                "Exemplo validate: {\"op\": \"validate_idea\", \"idea\": \"MMO open world\"}. "
                "Exemplo disclosure: {\"op\": \"disclosure\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "op": {"type": "string", "enum": ["validate_idea", "disclosure"]},
                    "idea": {"type": "string", "description": "Ideia do usuario (para validate_idea)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="reviewer_manage",
            description=(
                "🔍 Modo revisor adversarial (ONDA 3 — 3.K). "
                "Ativa/desativa modo onde o agente audita em vez de implementar. "
                "Ataca evidencia fabricada com confianca. "
                "Operacoes: enable, disable, status. "
                "Exemplo: {\"op\": \"enable\", \"reason\": \"Auditar fatia 3.G\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "op": {"type": "string", "enum": ["enable", "disable", "status"]},
                    "reason": {"type": "string", "description": "Motivo da auditoria (para enable)."},
                },
                "required": [],
            },
        ),
        # ── Playtest Onda 1 (watch_state, godot_exec, effect_probe) ──
        Tool(
            name="watch_state_start",
            description="Comeca a observar propriedades de nos do jogo a cada step. "
                        "Use para monitorar HP, posicao, velocidade durante playtesting. "
                        "Depois colete com watch_state_collect().",
            inputSchema={
                "type": "object",
                "properties": {
                    "targets": {"type": "array", "items": {"type": "object"}},
                    "interval_steps": {"type": "integer"},
                },
                "required": ["targets"],
            },
        ),
        Tool(
            name="watch_state_collect",
            description="Coleta o historico de estados observados desde watch_state_start(). "
                        "Retorna array de snapshots com timestamp e valores das propriedades.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="godot_exec",
            description="Executa codigo GDScript DENTRO do jogo rodando. "
                        "Use para setup de cenarios de teste: spawnar inimigos, modificar estado. "
                        "Use 'return' para obter valores.",
            inputSchema={
                "type": "object",
                "properties": {"code": {"type": "string", "description": "Codigo GDScript a executar no jogo"}},
                "required": ["code"],
            },
        ),
        Tool(
            name="effect_probe",
            description="Verifica se uma acao no jogo produziu o efeito esperado. "
                        "Avalia expressao antes, executa acao, avalia depois, compara. "
                        "Ideal para testar: 'o dano reduziu o HP?', 'o pulo aumentou a posicao Y?'",
            inputSchema={
                "type": "object",
                "properties": {
                    "before": {"type": "string", "description": "Expressao GDScript antes da acao"},
                    "action": {"type": "string", "description": "Codigo GDScript da acao"},
                    "after": {"type": "string", "description": "Expressao GDScript depois da acao"},
                    "wait_ms": {"type": "integer", "description": "ms de espera entre acao e verificacao"},
                },
                "required": ["before", "action", "after"],
            },
        ),
        # ── Balance Onda 1 ──────────────────────────────────────
        Tool(
            name="balance_analyze",
            description="Analisa o balanceamento do jogo e sugere ajustes. "
                        "Calcula DPS necessario, verifica se o jogo eh 'vencivel', "
                        "detecta torres com custo-beneficio ruim, inimigos desbalanceados.",
            inputSchema={
                "type": "object",
                "properties": {
                    "game_type": {"type": "string", "enum": ["tower_defense", "rpg", "platformer", "shooter"]},
                    "towers": {"type": "array", "items": {"type": "object"}},
                    "enemies": {"type": "array", "items": {"type": "object"}},
                    "waves": {"type": "integer"},
                    "target_duration_minutes": {"type": "integer"},
                },
                "required": [],
            },
        ),
        Tool(
            name="wave_generate",
            description="Gera composicao de ondas para tower defense. "
                        "Curva de dificuldade (linear, exponential, staircase). "
                        "Chefoes a cada N waves. Use para planejar as waves do jogo.",
            inputSchema={
                "type": "object",
                "properties": {
                    "wave_count": {"type": "integer"},
                    "enemy_types": {"type": "array", "items": {"type": "object"}},
                    "difficulty_curve": {"type": "string", "enum": ["linear", "exponential", "staircase"]},
                    "boss_every": {"type": "integer"},
                },
                "required": [],
            },
        ),
        Tool(
            name="dps_calculator",
            description="Calcula DPS efetivo de uma torre/arma considerando criticos, "
                        "dano em area e dano continuo (DoT). Retorna Time-To-Kill para HPs de referencia.",
            inputSchema={
                "type": "object",
                "properties": {
                    "damage": {"type": "number"},
                    "fire_rate": {"type": "number"},
                    "crit_chance": {"type": "number"},
                    "crit_multiplier": {"type": "number"},
                    "aoe_radius": {"type": "number"},
                    "aoe_targets": {"type": "integer"},
                    "damage_over_time": {"type": "number"},
                    "dot_duration": {"type": "number"},
                },
                "required": ["damage", "fire_rate"],
            },
        ),
        Tool(
            name="loot_table_generate",
            description="Gera tabela de loot balanceada com chances de drop por raridade. "
                        "Suporta temas: scifi, fantasy, modern, post_apocalyptic.",
            inputSchema={
                "type": "object",
                "properties": {
                    "rarity_levels": {"type": "array", "items": {"type": "string"}},
                    "items_per_rarity": {"type": "integer"},
                    "game_theme": {"type": "string", "enum": ["scifi", "fantasy", "modern", "post_apocalyptic"]},
                },
                "required": [],
            },
        ),
        # ── GDD Generator (Onda 2) ──────────────────────────────
        Tool(
            name="gdd_generate",
            description="Gera Game Design Document (GDD) completo a partir de uma ideia. "
                        "Suporta: tower_defense, platformer, rpg, shooter, puzzle, roguelike. "
                        "Niveis de detalhe: brief (1 pagina) ou full (completo com historia, "
                        "monetizacao, marketing e roadmap). GRATIS — sem API externa.",
            inputSchema={
                "type": "object",
                "properties": {
                    "concept": {"type": "string", "description": "Ideia do jogo em uma frase"},
                    "game_type": {"type": "string", "enum": ["tower_defense","platformer","rpg","shooter","puzzle","roguelike"]},
                    "target_platform": {"type": "string", "enum": ["pc","mobile","web"]},
                    "detail_level": {"type": "string", "enum": ["brief","full"]},
                },
                "required": ["concept"],
            },
        ),
        # ── Behavior Trees (Onda 2) ─────────────────────────────
        Tool(
            name="behavior_tree_generate",
            description="Gera Behavior Tree completa em GDScript a partir de descricao em portugues. "
                        "Analisa texto como 'patrulha, detecta, persegue, ataca, foge' e gera codigo "
                        "com Selector/Sequence, acoes e condicoes. Zero custo — puro Python.",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Comportamento em portugues"},
                    "behavior_name": {"type": "string", "description": "Nome da classe (ex: EnemyAI)"},
                    "tree_type": {"type": "string", "enum": ["selector","sequence"]},
                    "save_path": {"type": "string"},
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="behavior_tree_list_templates",
            description="Lista templates de Behavior Tree disponiveis: patrol_chase_attack, "
                        "patrol_chase_attack_flee, guard_alert_chase, idle_wander_flee, boss_phases.",
            inputSchema={"type": "object", "properties": {}},
        ),
        # ── Performance Profiler (Onda 2) ───────────────────────
        Tool(
            name="profile_frame",
            description="Analisa performance do jogo rodando: FPS medio/min/max, draw calls, "
                        "uso de memoria e nos na cena. Sugere otimizacoes especificas. "
                        "Nota A (otimo) ate D (critico). GRATIS — sem API externa.",
            inputSchema={
                "type": "object",
                "properties": {"sample_frames": {"type": "integer", "description": "Frames para amostrar (default 60)"}},
                "required": [],
            },
        ),
        Tool(
            name="profile_memory",
            description="Analisa uso de memoria do jogo (estatica + video) e detecta objetos. "
                        "GRATIS — sem API externa.",
            inputSchema={
                "type": "object",
                "properties": {"track_objects": {"type": "boolean", "description": "Contar objetos por tipo"}},
                "required": [],
            },
        ),
        # ── Feature 10: Stress Test ─────────────────────────────
        Tool(
            name="run_stress_test",
            description=(
                "Teste de stress com carga e input aleatorio REPRODUTIVEL. "
                "Spawna N instancias de uma cena, injeta input aleatorio "
                "com seed explicita, e coleta FPS/memoria em intervalos. "
                "Use para validar performance sob carga antes do lancamento. "
                "Pre-condicoes: jogo rodando via godot_run_project. "
                "Exemplo: run_stress_test(spawn_scene_path='res://scenes/enemy.tscn', "
                "spawn_count=50, duration_seconds=10, input_actions=['move_left','jump'], "
                "random_seed=42, fps_threshold=30). "
                "Erro mais comum: bridge nao disponivel — inicie o jogo primeiro."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho do projeto."},
                    "spawn_scene_path": {"type": "string", "description": "Cena a instanciar em massa (ex: res://scenes/enemy.tscn)."},
                    "spawn_count": {"type": "integer", "description": "Quantidade de instancias (default: 10)."},
                    "duration_seconds": {"type": "integer", "description": "Duracao total do teste em segundos (default: 5)."},
                    "input_actions": {"type": "array", "items": {"type": "string"}, "description": "Acoes do InputMap a injetar aleatoriamente."},
                    "random_seed": {"type": "integer", "description": "Seed explicita para reproducibilidade (OBRIGATORIO)."},
                    "fps_threshold": {"type": "number", "description": "FPS minimo aceitavel — abaixo marca FALHOU (default: 30)."},
                    "sample_interval_ms": {"type": "integer", "description": "Intervalo entre amostras em ms (default: 500)."},
                },
                "required": ["spawn_scene_path", "random_seed"],
            },
        ),
        # ── Shader NL (Onda 3) ──────────────────────────────────
        Tool(
            name="shader_generate",
            description="Gera arquivo .gdshader a partir de descricao em portugues. "
                        "15 templates 2D: glow, dissolve, water, wind, hologram, forcefield, "
                        "outline, pixelate, chromatic_aberration, heat_distortion, toon, "
                        "grayscale, neon_pulse, frost, invisibility. GRATIS — sem API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Efeito visual desejado. Ex: 'holograma azul com scanlines'"},
                    "shader_type": {"type": "string", "enum": ["canvas_item","spatial","particles","sky"]},
                    "save_path": {"type": "string"},
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="shader_list_templates",
            description="Lista 15 templates de shader 2D disponiveis com palavras-chave.",
            inputSchema={"type": "object", "properties": {}},
        ),
        # ── World Generation (Onda 3) ───────────────────────────
        Tool(
            name="terrain_generate",
            description="Gera terreno procedural com biomas por altura/umidade. "
                        "Usa FastNoiseLite (built-in Godot). Retorna JSON com seed, "
                        "distribuicao de biomas e parametros de noise. GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {"type": "integer"}, "height": {"type": "integer"},
                    "seed": {"type": "integer"}, "biomes": {"type": "array", "items": {"type": "string"}},
                    "water_level": {"type": "number"}, "mountain_level": {"type": "number"},
                    "save_path": {"type": "string"},
                },
                "required": [],
            },
        ),
        Tool(
            name="dungeon_generate",
            description="Gera dungeon procedural com salas e corredores (algoritmo BSP). "
                        "Salas classificadas como combat, treasure, boss, start, empty. GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {
                    "rooms": {"type": "integer"}, "min_room_size": {"type": "integer"},
                    "max_room_size": {"type": "integer"}, "seed": {"type": "integer"},
                    "save_path": {"type": "string"},
                },
                "required": [],
            },
        ),
        Tool(
            name="world_describe",
            description="Analisa um mundo gerado e sugere melhorias e pontos de interesse. "
                        "Detecta biomas e recomenda elementos de gameplay.",
            inputSchema={
                "type": "object",
                "properties": {"terrain_path": {"type": "string"}},
                "required": [],
            },
        ),
        # ── 3D Asset Generation (Onda 3) ────────────────────────
        Tool(
            name="generate_3d_placeholder",
            description="Gera placeholder 3D procedural (box, sphere, cylinder, cone, pyramid). "
                        "Preview PNG + codigo de cena Godot .tscn. GRATIS — Pillow.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}, "shape": {"type": "string", "enum": ["box","sphere","cylinder","cone","pyramid"]},
                    "color": {"type": "string"}, "size": {"type": "number"}, "save_path": {"type": "string"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="generate_3d_asset",
            description="Gera asset 3D via API Hyper3D Rodin (⚠️💰 ~$0.05/modelo) ou placeholder GRATIS. "
                        "SEM custo se HYPER3D_API_KEY nao configurada. Categorias: prop, character, vehicle, building, weapon.",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string"}, "category": {"type": "string", "enum": ["prop","character","vehicle","building","weapon"]},
                    "style": {"type": "string", "enum": ["scifi","fantasy","modern","realistic"]}, "save_path": {"type": "string"},
                },
                "required": ["description"],
            },
        ),
        # ── Deploy + Marketplace (Onda 4 — FINAL) ────────────────
        Tool(
            name="deploy_itch",
            description="Exporta e envia o jogo para itch.io via butler CLI. "
                        "Suporta Windows, Linux, Web, macOS, Android. GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {"itch_username": {"type": "string"}, "itch_game": {"type": "string"},
                    "platforms": {"type": "array", "items": {"type": "string"}},
                    "version": {"type": "string"}, "dry_run": {"type": "boolean"}},
                "required": [],
            },
        ),
        Tool(
            name="release_checklist",
            description="Verifica se o projeto esta pronto para lancamento (nota 0-10): "
                        "project.godot, main scene, scripts, assets, audio, export presets, "
                        "gitignore, readme, license, tamanho. GRATIS.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_current_phase",
            description="Mostra em que fase do projeto o time esta "
                        "(IDEIA/DESIGN/PROTOTIPO/CONTEUDO/POLIMENTO/PRONTO_PARA_LANCAR) "
                        "e o que falta para avancar. GRATIS.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="advance_phase",
            description="Avanca o projeto para a proxima fase, SE o criterio "
                        "da fase atual foi cumprido. Use force=true so com motivo "
                        "explicito. GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {
                    "force": {"type": "boolean", "description": "Ignora criterios de transicao (obrigatorio informar reason)."},
                    "reason": {"type": "string", "description": "Justificativa para avanco forcado (obrigatorio se force=true)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="get_phase_history",
            description="Mostra o historico de mudancas de fase do projeto. GRATIS.",
            inputSchema={"type": "object", "properties": {}},
        ),
        # ── Feature 10: proximo passo obrigatorio ─────────────
        Tool(
            name="get_next_step",
            description=(
                "Retorna o PROXIMO PASSO OBRIGATORIO da sessao: fase atual, "
                "blockers, criterio para avancar, e acao sugerida. "
                "Inclui why_now (justificativa), do_not_do (o que EVITAR), "
                "e smallest_step (menor acao que avanca — util quando cansado). "
                "Use low_energy=true para focar apenas no menor passo possivel. "
                "DEVE ser chamada no inicio de TODA sessao antes de qualquer "
                "outra tool (exceto ping/health_check/setup). "
                "Grava o PID da sessao no marcador .mcp_session_started "
                "para liberar o gate de sessao. GRATIS."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "low_energy": {
                        "type": "boolean",
                        "description": "Se true, retorna apenas a menor acao possivel como passo sugerido. "
                                       "Util quando o desenvolvedor esta cansado e quer um passo trivial.",
                        "default": False,
                    }
                },
            },
        ),
        # ── Fatia 1.8: resume_session ──────────────────────────
        Tool(
            name="resume_session",
            description=(
                "Recuperacao de sessao: le o estado persistente do projeto "
                "(fase, milestone, roadmap de fatias) e devolve um resumo "
                "unificado de onde voce parou + qual o proximo passo. "
                "Use no inicio de sessao para retomar contexto sem precisar "
                "colar documentos manualmente. Combina get_next_step (fase) "
                "+ roadmap de fatias (.roadmap_progress.json) + milestone atual. "
                "Somente leitura — nao altera estado. GRATIS."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        # ── Feature 5: Project Brief ────────────────────────────
        Tool(
            name="set_project_brief",
            description=(
                "Define ou sobrescreve o project brief (genero, estilo de arte, tom, plataforma). "
                "Use no inicio do projeto para configurar caracteristicas fundamentais que "
                "ferramentas como create_entity usam como fallback. "
                "So aceita sobrescrever brief existente com force=True. "
                "Genero validado contra os 17 generos de GAME_PATTERNS. "
                "Exemplo: {\"genre\": \"tower_defense\", \"art_style\": \"scifi\", \"tone\": \"estrategico\", \"target_platform\": \"pc\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "genre": {"type": "string", "description": "Genero do jogo (17 validos: tower_defense, platformer, rpg_turn_based, etc.)."},
                    "art_style": {"type": "string", "description": "Estilo visual (scifi, fantasia, cartoon, pixel, minimalista)."},
                    "tone": {"type": "string", "description": "Tom do jogo (estrategico, casual, sombrio, epico, humorado, frenetico)."},
                    "target_platform": {"type": "string", "description": "Plataforma alvo (pc, mobile, web)."},
                    "force": {"type": "boolean", "description": "Obrigatorio True para sobrescrever brief existente."},
                    "ip_force": {"type": "boolean", "description": "Forca criacao mesmo com alerta de propriedade intelectual."},
                    "ip_reason": {"type": "string", "description": "Justificativa para ignorar alerta de PI (obrigatorio com ip_force=True)."},
                },
                "required": [],
            },
        ),
        Tool(
            name="get_project_brief",
            description=(
                "Retorna o project brief atual. "
                "Se nunca foi configurado, retorna brief=null e configured=False. "
                "Use para consultar as caracteristicas do projeto antes de criar entidades."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="update_project_brief",
            description=(
                "Atualiza campos especificos do project brief sem sobrescrever os demais. "
                "Use para ajustar uma caracteristica sem redefinir o brief inteiro. "
                "Nunca exige force (update parcial por definicao). "
                "Exemplo: {\"tone\": \"sombrio\"} — altera so o tom, mantendo genero, art_style e platform."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "genre": {"type": "string", "description": "Genero do jogo (validado contra GAME_PATTERNS)."},
                    "art_style": {"type": "string", "description": "Estilo visual."},
                    "tone": {"type": "string", "description": "Tom do jogo."},
                    "target_platform": {"type": "string", "description": "Plataforma alvo (pc, mobile, web)."},
                },
                "required": [],
            },
        ),
        # ── Fase 1 do Roadmap: Milestone Plan ────────────────────
        Tool(
            name="create_milestone_plan",
            description="Cria um plano de milestones (roteiro) baseado no genero e ideia do jogo. "
                        "Usa gdd_generate() + estimate_game_scope() para gerar milestones "
                        "distribuidos entre PROTOTIPO, CONTEUDO e POLIMENTO. GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {
                    "genero": {"type": "string", "description": "Genero do jogo (17 generos via GAME_PATTERNS). Default: tower_defense."},
                    "ideia": {"type": "string", "description": "Descricao da ideia do jogo."},
                    "num_milestones": {"type": "integer", "description": "Quantidade de milestones (default: 8)."},
                    "force": {"type": "boolean", "description": "Sobrescrever plano existente."},
                },
                "required": [],
            },
        ),
        Tool(
            name="advance_milestone",
            description="Conclui um milestone. Sem ID, avanca o proximo pendente automaticamente. GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {
                    "milestone_id": {"type": "string", "description": "ID do milestone a concluir. Se omitido, usa get_next_milestone()."},
                },
                "required": [],
            },
        ),
        Tool(
            name="get_milestone_plan",
            description="Mostra o plano completo de milestones + progresso (total, concluidos, pendentes, %). GRATIS.",
            inputSchema={"type": "object", "properties": {}},
        ),
        # ── Fatia 1.14: project_progress ─────────────────────
        Tool(
            name="project_progress",
            description="Termometro visual do milestone atual: barra de progresso ASCII, "
                        "percentual, mensagem motivacional e proximo milestone pendente. "
                        "Use para ver 'quanto falta' e manter motivacao. GRATIS.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="auto_screenshot",
            description="Gera screenshots automaticas do jogo rodando para loja (itch.io/Steam). GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {"count": {"type": "integer"}, "delay_between": {"type": "number"}, "save_dir": {"type": "string"}},
                "required": [],
            },
        ),
        Tool(
            name="marketplace_search",
            description="Busca assets em marketplaces gratuitos: Kenney.nl (CC0, 300+ packs), "
                        "Godot Asset Library, OpenGameArt, Poly Haven. GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {"query": {"type": "string"},
                    "source": {"type": "string", "enum": ["kenney","godot_assets","opengameart","polyhaven"]},
                    "category": {"type": "string"}},
                "required": [],
            },
        ),
        Tool(
            name="marketplace_download",
            description="Baixa asset gratuito do marketplace. Kenney.nl (ZIP direto, CC0). GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {"source": {"type": "string", "enum": ["kenney","godot_assets","polyhaven"]},
                    "slug": {"type": "string"}, "save_to": {"type": "string"}},
                "required": ["slug"],
            },
        ),
        # ── Juice (Onda 5) ─────────────────────────────────────
        Tool(
            name="juice_apply",
            description="Aplica tecnicas de game feel/polish profissional: coyote time, "
                        "input buffer, hit-stop, screen shake, squash & stretch, easing. "
                        "Presets: full, platformer, action, minimal. Gera script GDScript pronto. GRATIS.",
            inputSchema={
                "type": "object",
                "properties": {"preset": {"type": "string", "enum": ["full","platformer","action","minimal"]},
                              "save_to_script": {"type": "string"}},
                "required": [],
            },
        ),
        Tool(
            name="juice_list_presets",
            description="Lista presets de juice disponiveis com tecnicas incluidas.",
            inputSchema={"type": "object", "properties": {}},
        ),
        # ── Auto-Config (Fase 2C) ───────────────────────────────
        Tool(
            name="validate_mcp_environment",
            description="Verifica se o ambiente MCP esta pronto: Python, dependencias, server.py.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="setup_mcp_config",
            description="Gera arquivo de configuracao MCP para VS Code Copilot, Claude ou Cursor.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "enum": ["vscode", "claude", "cursor", "all"],
                               "description": "Cliente alvo (default: vscode)."},
                },
                "required": [],
            },
        ),
        # ── Pipeline Executor (Onda 7) ──────────────────────────
        Tool(
            name="create_entity",
            description="Cria uma entidade COMPLETA: cena + collider + script + sprite + audio. "
                        "Decide automaticamente o que gerar. Use para inimigos, players, NPCs, itens. "
                        "Exemplo: {'name': 'Slime', 'entity_type': 'enemy', 'behavior': 'patrol'}.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome da entidade (ex: Slime, Player, Turret)."},
                    "entity_type": {"type": "string", "enum": ["enemy", "player", "tower", "npc", "item", "projectile"],
                                    "description": "Tipo de entidade."},
                    "description": {"type": "string", "description": "Descricao do comportamento."},
                    "behavior": {"type": "string", "enum": ["patrol", "chase", "idle", "none"],
                                 "description": "Comportamento IA."},
                    "generate_art": {"type": "boolean", "description": "Forcar geracao de arte (null=auto)."},
                    "generate_audio": {"type": "boolean", "description": "Forcar geracao de audio (null=auto)."},
                    "art_style": {"type": "string", "enum": ["scifi", "fantasy", "pixel", "cartoon"],
                                  "description": "Estilo visual."},
                    "save_path": {"type": "string", "description": "Caminho para salvar a cena."},
                },
                "required": ["name"],
            },
        ),
        # ── Feature 6: Batch Entity Creation ──────────────────
        Tool(
            name="create_entities",
            description=(
                "Cria MULTIPLAS entidades em lote sequencial. "
                "Cada entidade passa pelo mesmo pipeline de create_entity "
                "(cena + collider + script + arte + audio + compile gate). "
                "Maximo 20 entidades por chamada. Execucao sequencial. "
                "Nomes duplicados no batch sao rejeitados antes da criacao. "
                "Se um item nao tiver 'name', falha so aquele item. "
                "Use stop_on_first_failure=True para parar na primeira falha. "
                "Exemplo: {'entities': [{'name': 'Slime'}, {'name': 'Bat', 'behavior': 'chase'}]}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "description": "Lista de specs de entidade (cada uma igual ao create_entity).",
                        "items": {"type": "object"},
                    },
                    "stop_on_first_failure": {
                        "type": "boolean",
                        "description": "Se True, para na primeira falha (default: False).",
                    },
                },
                "required": ["entities"],
            },
        ),
        Tool(
            name="project_status",
            description="Status completo do projeto: cenas, scripts, sprites, audio, assets faltantes, "
                        "sugestoes do que criar a seguir. Use para diagnosticar o estado do jogo.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        # ── Orquestrador Genius (Onda 7) ──────────────────────
        Tool(
            name="circuit_breaker_status",
            description="Status dos circuit breakers das APIs externas (FLUX, Replicate, Edge TTS). "
                        "Use para verificar se alguma API está temporariamente bloqueada.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        # ── PATCH 12: Runtime Bridge ──────────────────────────
        Tool(
            name="godot_screenshot",
            description="Captura screenshot do jogo rodando via MCPRuntimeBridge. Jogo precisa estar em execucao (debug).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="godot_runtime_info",
            description="FPS, draw calls, memoria estatica e tempo de fisica do jogo rodando agora.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="godot_custom_command",
            description="Chama comando customizado registrado no jogo (ex: get_puzzle_state).",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome do comando registrado no jogo."},
                    "args": {"type": "object", "description": "Argumentos do comando (opcional)."},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="godot_list_custom_commands",
            description="Lista comandos customizados registrados no bridge do jogo.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="godot_run_project",
            description="Lanca o jogo direto via CLI (godot --path <projeto>), sem abrir o editor. Retorna pid.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho absoluto da pasta do projeto."},
                    "godot_executable": {"type": "string", "description": "Caminho absoluto do executavel do Godot."},
                },
                "required": ["project_path", "godot_executable"],
            },
        ),
        Tool(
            name="godot_stop_project",
            description="Encerra um processo de jogo iniciado por godot_run_project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {"type": "integer", "description": "PID retornado por godot_run_project."},
                },
                "required": ["pid"],
            },
        ),
        Tool(
            name="godot_wait_for_bridge",
            description="Espera ate o MCPRuntimeBridge responder (polling de runtime_info).",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeout_sec": {"type": "integer", "description": "Timeout em segundos (default 10)."},
                },
                "required": [],
            },
        ),
        # ── Pipeline de Verificação (Item 1 do plano de evolução) ──
        Tool(
            name="run_verification_pipeline",
            description=(
                "Executa pipeline de verificacao completo em um projeto Godot: "
                "compilacao, execucao headless, screenshot e testes GUT. "
                "Retorna relatorio consolidado JSON com status de cada etapa. "
                "Use para validar integridade do projeto apos mudancas grandes. "
                "Quando NAO usar: para compilar um unico arquivo (use compile_test_incremental). "
                "Pre-requisitos: projeto Godot com project.godot valido. "
                "Exemplo: {'project_path': 'C:/meus-jogos/meu_pong'}. "
                "Se o projeto nao tiver run/main_scene definido, passe test_scene obrigatoriamente."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Caminho do projeto Godot. Se omitido, usa projeto ativo."},
                    "godot_path": {"type": "string", "description": "Caminho do executavel Godot. Se omitido, auto-detecta."},
                    "test_scene": {"type": "string", "description": "Cena para rodar headless (ex: 'res://scenes/main.tscn'). Se omitido, le run/main_scene do project.godot."},
                    "gut_test_dir": {"type": "string", "description": "Diretorio de testes GUT (default: 'res://tests')."},
                    "headless_frames": {"type": "integer", "description": "Quantos frames executar antes do screenshot (default: 30)."},
                    "timeout_compile": {"type": "integer", "description": "Timeout em segundos para compile check (default: 30)."},
                    "timeout_headless": {"type": "integer", "description": "Timeout em segundos para headless run (default: 60)."},
                    "timeout_gut": {"type": "integer", "description": "Timeout em segundos para GUT (default: 120)."},
                    "screenshot_dir": {"type": "string", "description": "Diretorio para screenshots. Default: <proj>/verification_screenshots/."},
                },
                "required": [],
            },
        ),
        # ── Camada 5 (Gameplay): Tools registradas 2026-07-19 ──
        Tool(
            name="create_achievement_system",
            description=(
                "Cria sistema de conquistas e Cloud Save para o projeto. "
                "Gera script GDScript com AchievementManager (Steamworks + offline) "
                "e CloudSaveManager com suporte a Steam Auto-Cloud. "
                "Use para adicionar conquistas e save na nuvem ao jogo. "
                "Pre-condicoes: projeto ativo. "
                "Exemplo: {'achievements': [{'id': 'first_kill', 'name': 'Primeiro Sangue'}]}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "achievements": {"type": "array", "items": {"type": "object"}, "description": "Lista de conquistas [{id, name, description, icon}]."},
                    "use_steam": {"type": "boolean", "description": "Usar Steamworks (requer GodotSteam). Default: false."},
                    "apply_to_project": {"type": "boolean", "description": "Salvar scripts no projeto. Default: true."},
                },
                "required": [],
            },
        ),
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
        Tool(
            name="validate_achievement_config",
            description=(
                "Valida configuracao de conquistas: IDs duplicados, nomes vazios, "
                "icones de conquista faltantes, requisitos nao atingiveis. "
                "Use antes de publicar para garantir que conquistas funcionam. "
                "Exemplo: {'achievements': [{'id': 'win', 'name': 'Vitoria'}]}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "achievements": {"type": "array", "items": {"type": "object"}, "description": "Lista de conquistas a validar."},
                },
                "required": [],
            },
        ),
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
        Tool(
            name="adaptive_difficulty_adjust",
            description=(
                "Analisa desempenho do jogador e sugere ajustes de dificuldade. "
                "Usa metricas (mortes, kills, tempo, dano, precisao) para recomendar "
                "mudancas em HP, dano, spawn rate e drops. "
                "Use para criar sistema de dificuldade adaptativa. "
                "Exemplo: {'player_metrics': {'deaths': 5, 'kills': 10}, 'current_difficulty': 'normal'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "player_metrics": {"type": "object", "description": "Metricas: {deaths, kills, time_per_level_sec, damage_taken, accuracy}."},
                    "current_difficulty": {"type": "string", "enum": ["easy", "normal", "hard"], "description": "Dificuldade atual."},
                    "target_win_rate": {"type": "number", "description": "Taxa de vitoria desejada (0.0-1.0). Default: 0.6."},
                },
                "required": [],
            },
        ),
        Tool(
            name="quest_generate",
            description=(
                "Gera quest procedural baseada em templates. "
                "Tipos: fetch, kill, boss, explore. "
                "Inclui titulo, objetivos, recompensas e dialogo de NPC. "
                "Use para criar missoes secundarias ou conteudo procedural. "
                "Exemplo: {'quest_type': 'fetch', 'difficulty': 'normal', 'npc_giver': 'Aldeao'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "quest_type": {"type": "string", "enum": ["fetch", "kill", "escort", "collect", "boss", "explore"], "description": "Tipo da quest."},
                    "difficulty": {"type": "string", "enum": ["easy", "normal", "hard"], "description": "Dificuldade."},
                    "level_range": {"type": "array", "items": {"type": "integer"}, "description": "Nivel recomendado [min, max]."},
                    "npc_giver": {"type": "string", "description": "Nome do NPC que da a quest."},
                },
                "required": [],
            },
        ),
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
        Tool(
            name="dialogue_generate_npc_lines",
            description=(
                "Gera linhas de dialogo para NPCs baseado em tipo e contexto. "
                "Suporta 8 personalidades (guarda, mercador, sabio, vilao, etc.) "
                "e 7 cenarios (greeting, quest, combat, fear, rumor). "
                "Use para criar dialogos variados e imersivos. "
                "Exemplo: {'npc_type': 'mercador', 'scenario': 'greeting', 'count': 3}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "npc_type": {"type": "string", "description": "Personalidade: guarda, mercador, sabio, aldeao, vilao, companheiro, crianca, anciao."},
                    "scenario": {"type": "string", "description": "Contexto: greeting, farewell, quest_give, quest_complete, combat_taunt, fear, rumor."},
                    "count": {"type": "integer", "description": "Quantas linhas gerar (max 10). Default: 3."},
                    "npc_name": {"type": "string", "description": "Nome do NPC para personalizar."},
                },
                "required": [],
            },
        ),
        Tool(
            name="dialogue_generate_personality",
            description=(
                "Gera perfil completo de personalidade para NPC. "
                "Define tracos, tom de fala, motivacoes e estilo de dialogo. "
                "Use para criar NPCs profundos e consistentes. "
                "Exemplo: {'npc_name': 'Mago Eldrin', 'role': 'mentor'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "npc_name": {"type": "string", "description": "Nome do NPC."},
                    "role": {"type": "string", "enum": ["guarda", "mercador", "mentor", "vilao", "aliado", "neutro"], "description": "Papel no jogo."},
                    "context": {"type": "string", "description": "Breve descricao do contexto do NPC."},
                },
                "required": [],
            },
        ),
        Tool(
            name="accessibility_apply_colorblind_filter",
            description=(
                "Aplica filtro de daltonismo ao projeto (shader fullscreen). "
                "Suporta 4 tipos: protanopia, deuteranopia, tritanopia, achromatopsia. "
                "Modos: simulate (como daltônico vê) ou correct (corrigir cores). "
                "Use para tornar o jogo acessivel a jogadores daltonicos. "
                "Exemplo: {'cb_type': 'protanopia', 'mode': 'correct'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "cb_type": {"type": "string", "enum": ["protanopia", "deuteranopia", "tritanopia", "achromatopsia"], "description": "Tipo de daltonismo."},
                    "mode": {"type": "string", "enum": ["simulate", "correct"], "description": "'simulate' ou 'correct'."},
                    "apply_to_project": {"type": "boolean", "description": "Criar shader no projeto. Default: false."},
                },
                "required": [],
            },
        ),
        Tool(
            name="accessibility_add_subtitles",
            description=(
                "Adiciona sistema de legendas/closed captions ao projeto. "
                "Gera script de UI que exibe legendas sincronizadas com audio. "
                "Use para dialogos, cutscenes e efeitos sonoros importantes. "
                "Exemplo: {'apply_to_project': True}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "apply_to_project": {"type": "boolean", "description": "Criar script no projeto. Default: true."},
                    "font_size": {"type": "integer", "description": "Tamanho da fonte. Default: 16."},
                    "background_alpha": {"type": "number", "description": "Opacidade do fundo (0-1). Default: 0.7."},
                },
                "required": [],
            },
        ),
        Tool(
            name="accessibility_remap_controls",
            description=(
                "Configura sistema de remapeamento de controles. "
                "Permite jogador redefinir teclas e botoes do joystick. "
                "Gera UI de configuracao e script de persistencia. "
                "Use para acessibilidade e conforto do jogador. "
                "Exemplo: {'apply_to_project': True}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "apply_to_project": {"type": "boolean", "description": "Criar script no projeto. Default: true."},
                    "input_actions": {"type": "array", "items": {"type": "string"}, "description": "Acoes remapeaveis. Default: move, jump, attack, interact."},
                },
                "required": [],
            },
        ),
        Tool(
            name="accessibility_audit_scene",
            description=(
                "Audita cena para problemas de acessibilidade. "
                "Verifica contraste de cores, tamanho de texto, navegacao sem mouse, "
                "informacao apenas por cor, legendas faltantes. "
                "Use para garantir que o jogo e acessivel. "
                "Exemplo: {'scene_path': 'scenes/main.tscn'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena a auditar."},
                },
                "required": [],
            },
        ),
        Tool(
            name="accessibility_certification_checklist",
            description=(
                "Checklist de certificacao de acessibilidade. "
                "Cobre requisitos Steam, console (TRC/TCR) e boas praticas. "
                "Retorna nota e itens pendentes por categoria. "
                "Use antes de publicar para garantir conformidade. "
                "Exemplo: {} (sem argumentos)."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
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


        Tool(
            name="skeleton_get_bone_pose",
            description=(
                "Obtém a pose (transform) de um osso específico num Skeleton3D. Quando usar: para inspecionar posição/rotação de um osso antes de animar. Pré-condições: cena com nó Skeleton3D e bones definidos. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "skeleton_path": {"type": "string", "description": "skeleton_path (str)"},
                    "bone_name": {"type": "string", "description": "bone_name (str)"}
                },
                "required": ["scene_path", "skeleton_path"],
            },
        ),
        Tool(
            name="skeleton_set_bone_pose",
            description=(
                "Define a pose (transform) de um osso num Skeleton3D. Quando usar: para posicionar ossos para animação ou correção de rig. Pré-condições: cena com Skeleton3D e osso existente. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "skeleton_path": {"type": "string", "description": "skeleton_path (str)"},
                    "bone_name": {"type": "string", "description": "bone_name (str)"},
                    "position": {"type": "string", "description": "position (list[float])"},
                    "rotation": {"type": "string", "description": "rotation (list[float])"},
                    "scale": {"type": "string", "description": "scale (list[float])"}
                },
                "required": ["scene_path", "skeleton_path"],
            },
        ),
        Tool(
            name="skeleton_list_bones",
            description=(
                "Lista todos os ossos de um Skeleton3D com índices, nomes e hierarquia. Quando usar: para conhecer a estrutura do esqueleto antes de criar animações ou IK. Pré-condições: cena com Skeleton3D. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "skeleton_path": {"type": "string", "description": "skeleton_path (str)"}
                },
                "required": ["scene_path", "skeleton_path"],
            },
        ),
        Tool(
            name="skeleton_create_bone",
            description=(
                "Cria um novo osso num Skeleton3D existente. Quando usar: para adicionar ossos extras a um rig (ex: osso de arma, acessório). Pré-condições: cena com Skeleton3D. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "skeleton_path": {"type": "string", "description": "skeleton_path (str)"},
                    "bone_name": {"type": "string", "description": "bone_name (str)"},
                    "parent_bone": {"type": "string", "description": "parent_bone (str|int)"},
                    "position": {"type": "string", "description": "position (list[float])"},
                    "rotation": {"type": "string", "description": "rotation (list[float])"}
                },
                "required": ["scene_path", "skeleton_path"],
            },
        ),
        Tool(
            name="skeleton_create_ik_chain",
            description=(
                "Cria/configura uma chain SkeletonIK3D vinculada a um osso. Quando usar: para adicionar IK procedural (ex: pés no chão, mão alcançando objeto). Pré-condições: Skeleton3D com osso alvo. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "skeleton_path": {"type": "string", "description": "skeleton_path (str)"},
                    "bone_name": {"type": "string", "description": "bone_name (str)"},
                    "target_node_path": {"type": "string", "description": "target_node_path (str)"},
                    "chain_length": {"type": "string", "description": "chain_length (int)"},
                    "iterations": {"type": "string", "description": "iterations (int)"}
                },
                "required": ["scene_path", "skeleton_path"],
            },
        ),
        Tool(
            name="skeleton_get_info",
            description=(
                "Obtém informações completas de um Skeleton3D: bones, IK chains, estrutura. Quando usar: visão geral do rig antes de modificações. Pré-condições: cena com Skeleton3D. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "skeleton_path": {"type": "string", "description": "skeleton_path (str)"}
                },
                "required": ["scene_path", "skeleton_path"],
            },
        ),
        Tool(
            name="csg_create_node",
            description=(
                "Cria nó CSG (Constructive Solid Geometry) para prototipagem 3D: box, sphere, cylinder, torus. Quando usar: para blockout/prototipagem rápida de níveis 3D sem modelos. Pré-condições: cena 3D. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "parent_node_path": {"type": "string", "description": "parent_node_path (str)"},
                    "csg_type": {"type": "string", "description": "csg_type (str)"},
                    "node_name": {"type": "string", "description": "node_name (str)"},
                    "operation": {"type": "string", "description": "operation (str)"},
                    "width": {"type": "string", "description": "width (float)"},
                    "height": {"type": "string", "description": "height (float)"},
                    "depth": {"type": "string", "description": "depth (float)"},
                    "radius": {"type": "string", "description": "radius (float)"},
                    "position": {"type": "string", "description": "position (list[float])"}
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="gi_create_node",
            description=(
                "Cria nó de Global Illumination (VoxelGI ou LightmapGI) para iluminação indireta 3D. Quando usar: para melhorar qualidade de iluminação em cenas 3D. Pré-condições: cena 3D. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "gi_type": {"type": "string", "description": "gi_type (str)"},
                    "parent_node_path": {"type": "string", "description": "parent_node_path (str)"},
                    "node_name": {"type": "string", "description": "node_name (str)"},
                    "subdiv": {"type": "string", "description": "subdiv (int)"},
                    "extents": {"type": "string", "description": "extents (list[float])"},
                    "bake_mode": {"type": "string", "description": "bake_mode (str)"}
                },
                "required": ["scene_path", "gi_type"],
            },
        ),
        Tool(
            name="scene_fx_create_node",
            description=(
                "Cria nó de efeito de cena: ReflectionProbe, Decal, FogVolume. Quando usar: para adicionar reflexos, decalques ou neblina volumétrica. Pré-condições: cena 3D. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "fx_type": {"type": "string", "description": "fx_type (str)"},
                    "parent_node_path": {"type": "string", "description": "parent_node_path (str)"},
                    "node_name": {"type": "string", "description": "node_name (str)"},
                    "properties": {"type": "string", "description": "properties (dict)"}
                },
                "required": ["scene_path", "fx_type"],
            },
        ),
        Tool(
            name="sky_create_procedural",
            description=(
                "Cria um céu procedural ou físico (Sky/PhysicalSky) numa cena 3D. Quando usar: para configurar o céu e iluminação ambiente. Pré-condições: cena 3D com WorldEnvironment ou direcional light. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "sky_type": {"type": "string", "description": "sky_type (str)"},
                    "parent_node_path": {"type": "string", "description": "parent_node_path (str)"},
                    "sun_color": {"type": "string", "description": "sun_color (str)"},
                    "ground_color": {"type": "string", "description": "ground_color (str)"},
                    "sky_energy": {"type": "string", "description": "sky_energy (float)"}
                },
                "required": ["scene_path", "sky_type"],
            },
        ),
        Tool(
            name="camera_configure_attributes",
            description=(
                "Configura atributos de câmera 3D: DOF, exposição, near/far, FOV. Quando usar: para ajustar profundidade de campo, exposição ou clipping da câmera. Pré-condições: nó Camera3D na cena. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "camera_path": {"type": "string", "description": "camera_path (str)"},
                    "dof_enabled": {"type": "string", "description": "dof_enabled (bool)"},
                    "dof_distance": {"type": "string", "description": "dof_distance (float)"},
                    "dof_blur": {"type": "string", "description": "dof_blur (float)"},
                    "exposure_enabled": {"type": "string", "description": "exposure_enabled (bool)"},
                    "exposure_value": {"type": "string", "description": "exposure_value (float)"},
                    "auto_exposure": {"type": "string", "description": "auto_exposure (bool)"},
                    "near": {"type": "string", "description": "near (float)"},
                    "far": {"type": "string", "description": "far (float)"},
                    "fov": {"type": "string", "description": "fov (float)"}
                },
                "required": ["scene_path", "camera_path"],
            },
        ),
        Tool(
            name="multimesh_create_instance",
            description=(
                "Cria um MultiMeshInstance3D para renderizar muitos objetos idênticos com performance. Quando usar: para árvores, pedras, grama — centenas de instâncias do mesmo mesh. Pré-condições: recurso mesh disponível. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "parent_node_path": {"type": "string", "description": "parent_node_path (str)"},
                    "mesh_resource": {"type": "string", "description": "mesh_resource (str)"},
                    "instance_count": {"type": "string", "description": "instance_count (int)"},
                    "node_name": {"type": "string", "description": "node_name (str)"}
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="physics_create_joint",
            description=(
                "Cria um joint físico entre dois corpos: PinJoint2D, Spring, Hinge, Cone, Slider. Quando usar: para conectar corpos rígidos (ex: portas, pontes, cordas, ragdolls). Pré-condições: dois RigidBody na cena. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "parent_node_path": {"type": "string", "description": "parent_node_path (str)"},
                    "joint_type": {"type": "string", "description": "joint_type (str)"},
                    "joint_name": {"type": "string", "description": "joint_name (str)"},
                    "node_a": {"type": "string", "description": "node_a (str)"},
                    "node_b": {"type": "string", "description": "node_b (str)"},
                    "stiffness": {"type": "string", "description": "stiffness (float)"},
                    "damping": {"type": "string", "description": "damping (float)"},
                    "bias": {"type": "string", "description": "bias (float)"},
                    "disable_collision": {"type": "string", "description": "disable_collision (bool)"}
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="physics_configure_body",
            description=(
                "Configura propriedades físicas de um corpo: massa, atrito, bounce, damping, freeze. Quando usar: para ajustar comportamento físico de RigidBody ou CharacterBody. Pré-condições: nó com física na cena. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "node_path": {"type": "string", "description": "node_path (str)"},
                    "mass": {"type": "string", "description": "mass (float)"},
                    "friction": {"type": "string", "description": "friction (float)"},
                    "bounce": {"type": "string", "description": "bounce (float)"},
                    "gravity_scale": {"type": "string", "description": "gravity_scale (float)"},
                    "linear_damp": {"type": "string", "description": "linear_damp (float)"},
                    "angular_damp": {"type": "string", "description": "angular_damp (float)"},
                    "freeze": {"type": "string", "description": "freeze (bool)"},
                    "freeze_mode": {"type": "string", "description": "freeze_mode (str)"}
                },
                "required": ["scene_path", "node_path"],
            },
        ),
        Tool(
            name="physics_query_area_overlap",
            description=(
                "Prepara código para verificar corpos/áreas sobrepostos a uma Area2D/Area3D em runtime. Quando usar: para detectar se algo entrou numa área de trigger. Pré-condições: nó Area2D/Area3D na cena. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "area_path": {"type": "string", "description": "area_path (str)"},
                    "query_type": {"type": "string", "description": "query_type (str)"}
                },
                "required": ["scene_path", "area_path"],
            },
        ),
        Tool(
            name="physics_raycast_query",
            description=(
                "Prepara código para executar raycast em runtime via nó RayCast2D/3D. Quando usar: para detectar colisões em linha reta (tiro, visão, ground check). Pré-condições: nó RayCast2D/3D na cena. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "raycast_path": {"type": "string", "description": "raycast_path (str)"}
                },
                "required": ["scene_path", "raycast_path"],
            },
        ),
        Tool(
            name="ui_create_widget",
            description=(
                "Cria widget de UI granular: Tree, ItemList, OptionButton, TabContainer, PopupMenu, ProgressBar, Slider, SpinBox, ColorPicker, LineEdit, TextEdit, RichTextLabel, etc. Quando usar: para construir interfaces complexas além do básico. Pré-condições: cena com raiz Control. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "parent_node_path": {"type": "string", "description": "parent_node_path (str)"},
                    "widget_type": {"type": "string", "description": "widget_type (str)"},
                    "widget_name": {"type": "string", "description": "widget_name (str)"},
                    "properties": {"type": "string", "description": "properties (dict)"}
                },
                "required": ["scene_path", "parent_node_path"],
            },
        ),
        Tool(
            name="ui_create_tab_with_content",
            description=(
                "Adiciona uma tab com conteúdo a um TabContainer existente. Quando usar: para criar interfaces com abas (configurações, inventário). Pré-condições: TabContainer na cena. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "tab_container_path": {"type": "string", "description": "tab_container_path (str)"},
                    "tab_title": {"type": "string", "description": "tab_title (str)"},
                    "content_type": {"type": "string", "description": "content_type (str)"},
                    "tab_name": {"type": "string", "description": "tab_name (str)"}
                },
                "required": ["scene_path", "tab_container_path"],
            },
        ),
        Tool(
            name="ui_configure_focus_nav",
            description=(
                "Configura navegação por foco entre widgets (gamepad/teclado). Quando usar: para navegação fluida em menus com controle ou teclado. Pré-condições: nós Control na cena. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "node_path": {"type": "string", "description": "node_path (str)"},
                    "focus_neighbor_top": {"type": "string", "description": "focus_neighbor_top (str)"},
                    "focus_neighbor_bottom": {"type": "string", "description": "focus_neighbor_bottom (str)"},
                    "focus_neighbor_left": {"type": "string", "description": "focus_neighbor_left (str)"},
                    "focus_neighbor_right": {"type": "string", "description": "focus_neighbor_right (str)"},
                    "focus_neighbor_next": {"type": "string", "description": "focus_neighbor_next (str)"},
                    "focus_neighbor_prev": {"type": "string", "description": "focus_neighbor_prev (str)"},
                    "focus_mode": {"type": "string", "description": "focus_mode (str)"}
                },
                "required": ["scene_path", "node_path"],
            },
        ),
        Tool(
            name="ui_set_tooltip",
            description=(
                "Define o texto de tooltip de um nó Control. Quando usar: para adicionar dicas de interface. Pré-condições: nó Control na cena. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "node_path": {"type": "string", "description": "node_path (str)"},
                    "tooltip_text": {"type": "string", "description": "tooltip_text (str)"}
                },
                "required": ["scene_path", "node_path"],
            },
        ),
        Tool(
            name="ui_set_anchor_preset",
            description=(
                "Define anchor preset de um nó Control para layout responsivo. Quando usar: para posicionar elementos UI que se adaptam a diferentes resoluções. Pré-condições: nó Control na cena. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "node_path": {"type": "string", "description": "node_path (str)"},
                    "preset": {"type": "string", "description": "preset (str)"}
                },
                "required": ["scene_path", "node_path"],
            },
        ),
        Tool(
            name="network_setup_multiplayer",
            description=(
                "Configura multiplayer peer (ENet ou WebSocket) gerando script de setup. Quando usar: para adicionar multiplayer ao jogo. Pré-condições: projeto Godot com cena. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "mode": {"type": "string", "description": "mode (str)"},
                    "port": {"type": "string", "description": "port (int)"},
                    "max_players": {"type": "string", "description": "max_players (int)"},
                    "server_address": {"type": "string", "description": "server_address (str)"}
                },
                "required": ["scene_path", "mode"],
            },
        ),
        Tool(
            name="network_create_rpc",
            description=(
                "Adiciona um método RPC (@rpc) a um script GDScript. Quando usar: para criar funções que rodam remotamente em multiplayer. Pré-condições: script .gd existente. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {"type": "string", "description": "script_path (str)"},
                    "method_name": {"type": "string", "description": "method_name (str)"},
                    "params": {"type": "string", "description": "params (list[str])"},
                    "rpc_mode": {"type": "string", "description": "rpc_mode (str)"},
                    "call_local": {"type": "string", "description": "call_local (bool)"},
                    "method_body": {"type": "string", "description": "method_body (str)"}
                },
                "required": ["script_path", "method_name"],
            },
        ),
        Tool(
            name="network_create_websocket",
            description=(
                "Adiciona código de WebSocket client a um script GDScript. Quando usar: para comunicação com servidores externos (APIs, chat, matchmaking). Pré-condições: script .gd existente. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {"type": "string", "description": "script_path (str)"},
                    "url": {"type": "string", "description": "url (str)"},
                    "protocols": {"type": "string", "description": "protocols (list[str])"}
                },
                "required": ["script_path", "url"],
            },
        ),
        Tool(
            name="network_configure_dedicated_server",
            description=(
                "Configura parâmetros de servidor dedicado para exportação. Quando usar: para preparar build headless de servidor. Pré-condições: projeto Godot. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "export_preset_name": {"type": "string", "description": "export_preset_name (str)"},
                    "port": {"type": "string", "description": "port (int)"},
                    "enable_upnp": {"type": "string", "description": "enable_upnp (bool)"}
                },
                "required": ["export_preset_name", "port"],
            },
        ),
        Tool(
            name="network_create_lobby",
            description=(
                "Cria sistema de lobby básico para multiplayer: salas, join/ready, transição. Quando usar: para implementar tela de espera antes de partida multiplayer. Pré-condições: projeto com cena. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "scene_path (str)"},
                    "max_players": {"type": "string", "description": "max_players (int)"},
                    "lobby_name": {"type": "string", "description": "lobby_name (str)"}
                },
                "required": ["scene_path", "max_players"],
            },
        ),
        Tool(
            name="runtime_connect_signal",
            description=(
                "Gera código GDScript para conectar sinais em runtime. Quando usar: para wiring dinâmico de callbacks (ex: botão criado em código). Pré-condições: nós existentes na cena. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source_node_path": {"type": "string", "description": "source_node_path (str)"},
                    "signal_name": {"type": "string", "description": "signal_name (str)"},
                    "target_node_path": {"type": "string", "description": "target_node_path (str)"},
                    "method_name": {"type": "string", "description": "method_name (str)"},
                    "flags": {"type": "string", "description": "flags (int)"}
                },
                "required": ["source_node_path", "signal_name"],
            },
        ),
        Tool(
            name="runtime_disconnect_signal",
            description=(
                "Gera código GDScript para desconectar sinais em runtime. Quando usar: para limpar conexões que não são mais necessárias. Pré-condições: sinal previamente conectado. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source_node_path": {"type": "string", "description": "source_node_path (str)"},
                    "signal_name": {"type": "string", "description": "signal_name (str)"},
                    "target_node_path": {"type": "string", "description": "target_node_path (str)"},
                    "method_name": {"type": "string", "description": "method_name (str)"}
                },
                "required": ["source_node_path", "signal_name"],
            },
        ),
        Tool(
            name="runtime_emit_signal",
            description=(
                "Gera código GDScript para emitir sinal em runtime. Quando usar: para disparar eventos customizados programaticamente. Pré-condições: script com signal definido. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node_path": {"type": "string", "description": "node_path (str)"},
                    "signal_name": {"type": "string", "description": "signal_name (str)"},
                    "args": {"type": "string", "description": "args (list)"}
                },
                "required": ["node_path", "signal_name"],
            },
        ),
        Tool(
            name="runtime_list_signals",
            description=(
                "Lista todos os sinais definidos e emitidos num script GDScript. Quando usar: para inspecionar a API de sinais de um script. Pré-condições: script .gd existente. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {"type": "string", "description": "script_path (str)"}
                },
                "required": ["script_path"],
            },
        ),
        Tool(
            name="runtime_watch_signal",
            description=(
                "Gera código para monitorar (watch) um sinal durante runtime com contagem e duração. Quando usar: para debugar frequência de sinais (ex: quantas vezes 'body_entered' dispara). Pré-condições: sinal existente. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "signal_name": {"type": "string", "description": "signal_name (str)"},
                    "node_path": {"type": "string", "description": "node_path (str)"},
                    "duration": {"type": "string", "description": "duration (float)"}
                },
                "required": ["signal_name", "node_path"],
            },
        ),
        Tool(
            name="render_get_settings",
            description=(
                "Obtém configurações atuais de rendering do project.godot. Quando usar: para auditar qualidade gráfica antes de modificar. Pré-condições: project.godot acessível. Exemplo: {} (sem argumentos — usa projeto ativo) "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "project_path (str)"}
                },
                "required": ["project_path"],
            },
        ),
        Tool(
            name="render_set_antialiasing",
            description=(
                "Configura antialiasing: MSAA (2x/4x/8x), FXAA, TAA. Quando usar: para melhorar qualidade de bordas ou performance. Pré-condições: project.godot acessível. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "project_path (str)"},
                    "msaa": {"type": "string", "description": "msaa (str)"},
                    "fxaa": {"type": "string", "description": "fxaa (bool)"},
                    "taa": {"type": "string", "description": "taa (bool)"},
                    "screen_space_aa": {"type": "string", "description": "screen_space_aa (str)"}
                },
                "required": ["project_path", "msaa"],
            },
        ),
        Tool(
            name="render_set_scaling",
            description=(
                "Configura modo de scaling/resolução: modo, escala, stretch. Quando usar: para configurar como o jogo se adapta a diferentes resoluções. Pré-condições: project.godot acessível. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "project_path (str)"},
                    "mode": {"type": "string", "description": "mode (str)"},
                    "scale": {"type": "string", "description": "scale (float)"},
                    "stretch_mode": {"type": "string", "description": "stretch_mode (str)"},
                    "stretch_aspect": {"type": "string", "description": "stretch_aspect (str)"}
                },
                "required": ["project_path", "mode"],
            },
        ),
        Tool(
            name="render_set_quality",
            description=(
                "Configura qualidade de rendering por preset (low/balanced/high/ultra) ou manual. Quando usar: para otimizar performance ou maximizar qualidade. Pré-condições: project.godot acessível. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "project_path (str)"},
                    "preset": {"type": "string", "description": "preset (str)"},
                    "shadows": {"type": "string", "description": "shadows (str)"},
                    "gi": {"type": "string", "description": "gi (str)"},
                    "reflections": {"type": "string", "description": "reflections (str)"},
                    "particles": {"type": "string", "description": "particles (str)"}
                },
                "required": ["project_path", "preset"],
            },
        ),
        Tool(
            name="csharp_scaffold_project",
            description=(
                "Cria/scaffolda um projeto C# Godot: .csproj, .sln, script exemplo. Quando usar: para iniciar desenvolvimento C# no Godot. Pré-condições: projeto Godot existente, .NET SDK instalado. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "project_path (str)"},
                    "dotnet_version": {"type": "string", "description": "dotnet_version (str)"},
                    "create_solution": {"type": "string", "description": "create_solution (bool)"}
                },
                "required": ["project_path", "dotnet_version"],
            },
        ),
        Tool(
            name="csharp_generate_script",
            description=(
                "Gera script C# a partir de templates: basic, player, enemy, pickup, ui. Quando usar: para criar rapidamente scripts C# com boilerplate. Pré-condições: projeto C# scaffoldado. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {"type": "string", "description": "script_path (str)"},
                    "class_name": {"type": "string", "description": "class_name (str)"},
                    "parent_class": {"type": "string", "description": "parent_class (str)"},
                    "namespace": {"type": "string", "description": "namespace (str)"},
                    "template": {"type": "string", "description": "template (str)"}
                },
                "required": ["script_path", "class_name"],
            },
        ),
        Tool(
            name="csharp_build_project",
            description=(
                "Compila o projeto C# do Godot via dotnet build. Quando usar: para verificar erros de compilação em scripts C#. Pré-condições: projeto C# scaffoldado, .NET SDK instalado. Exemplo: veja documentacao. "
                "Exemplo de input: veja documentação da tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "project_path (str)"},
                    "configuration": {"type": "string", "description": "configuration (str)"}
                },
                "required": ["project_path", "configuration"],
            },
        ),
        Tool(
            name="quickstart_manage",
            description=(
                "⚡ QUICK START: frase → jogo jogável em minutos. "
                "Recebe uma frase em linguagem natural descrevendo o jogo desejado, "
                "cria o projeto Godot completo com cena jogável (personagem + inimigo + colisão). "
                "Usa matching por palavras-chave para match automático com o blueprint mais próximo. "
                "Também suporta modo remix (clona jogo-semente) e vitrine de gêneros (lista frases prontas). "
                "Quando usar: primeira ferramenta após instalar o MCP, ou para começar um jogo novo. "
                "Operações: run (cria a partir da frase), remix (clona seed), showcase (vitrine de gêneros). "
                "Exemplo run: {\"op\": \"run\", \"phrase\": \"jogo de plataforma com herói que atira\"}. "
                "Exemplo remix: {\"op\": \"remix\", \"seed\": \"breakout\"}. "
                "Exemplo showcase: {\"op\": \"showcase\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "op": {
                        "type": "string",
                        "description": "Operação: 'run' para criar, 'remix' para clonar seed, 'showcase' para listar gêneros disponíveis.",
                        "enum": ["run", "remix", "showcase"],
                    },
                    "phrase": {
                        "type": "string",
                        "description": "Frase descrevendo o jogo (para op='run'). Ex: 'jogo de plataforma com herói'.",
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Nome do projeto (opcional, gerado da frase/seed se vazio).",
                    },
                    "seed": {
                        "type": "string",
                        "description": "Nome do seed para clone (para op='remix'). Ex: 'breakout'.",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="version_history_manage",
            description=(
                "📸 Histórico de versões jogáveis (Fatia 1.Q). "
                "Salva, lista, restaura e remove versões do jogo com screenshot e data. "
                "Navegação visual: escolher por screenshot e data, não por hash git. "
                "Quando usar: salvar marco do jogo (op=save), ver galeria de versões (op=list), "
                "voltar para versão anterior (op=restore), capturar screenshot avulso (op=screenshot). "
                "Pré-condições para screenshot: jogo precisa estar rodando em modo debug (F5 no Godot). "
                "Exemplo save: {\"op\": \"save\", \"description\": \"Antes de refatorar IA\"}. "
                "Exemplo list: {\"op\": \"list\"}. "
                "Exemplo restore: {\"op\": \"restore\", \"version_id\": \"20260721_143022\"}. "
                "Exemplo delete: {\"op\": \"delete\", \"version_id\": \"20260721_143022\"}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "op": {
                        "type": "string",
                        "description": "Operação: 'save', 'list', 'restore', 'delete' ou 'screenshot'.",
                        "enum": ["save", "list", "restore", "delete", "screenshot"],
                    },
                    "description": {
                        "type": "string",
                        "description": "Descrição da versão (para op='save'). Ex: 'Antes de refatorar IA'.",
                    },
                    "version_id": {
                        "type": "string",
                        "description": "ID da versão (para op='restore' ou op='delete'). Ex: '20260721_143022'.",
                    },
                },
                "required": [],
            },
        ),
    ]

