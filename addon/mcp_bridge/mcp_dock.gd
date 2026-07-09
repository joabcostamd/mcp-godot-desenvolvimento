@tool
extends VBoxContainer

# â”€â”€ MCP IA DEV â€” Painel de ConfiguraÃ§Ã£o v2 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Dock do editor Godot. Exibe status, atalhos rÃ¡pidos, configuraÃ§Ã£o
# de portas/caminhos, info do projeto e log de atividade da IA.

var _plugin: EditorPlugin

# â”€â”€ Status â”€â”€
var _status_color: ColorRect
var _status_label: Label
var _client_indicator: ColorRect
var _client_label: Label

# â”€â”€ Atalhos â”€â”€
var _btn_play: Button
var _btn_stop: Button
var _btn_screenshot: Button
var _btn_rescan: Button

# â”€â”€ ConexÃ£o â”€â”€
var _port_editor: SpinBox
var _port_game: SpinBox

# â”€â”€ Godot â”€â”€
var _godot_path: LineEdit
var _godot_console_path: LineEdit

# â”€â”€ Projeto â”€â”€
var _proj_name_label: Label
var _proj_scene_label: Label
var _proj_renderer_label: Label
var _default_project: LineEdit

# â”€â”€ Log â”€â”€
var _log_list: RichTextLabel

# â”€â”€ BotÃµes globais â”€â”€
var _btn_salvar: Button
var _btn_limpar_log: Button
var _info_label: RichTextLabel

# â”€â”€ Timer â”€â”€
var _timer: Timer
var _content: VBoxContainer

const COLORS := {
	"green": Color(0.2, 0.8, 0.3),
	"red": Color(0.9, 0.2, 0.2),
	"blue": Color(0.3, 0.6, 1.0),
	"yellow": Color(1.0, 0.8, 0.1),
	"gray": Color(0.5, 0.5, 0.5),
	"cyan": Color(0.2, 0.8, 0.8),
	"orange": Color(1.0, 0.5, 0.1),
	"purple": Color(0.7, 0.3, 0.9),
}

# TraduÃ§Ã£o de comandos tÃ©cnicos â†’ PT-BR simples
const TRANSLATE := {
	# Conexão & Status
	"ping": "Verificando conexão com a IA",
	"validate_godot_version": "Verificando versão do Godot",
	"health_check": "Verificando saúde do sistema",
	"self_test": "Executando autoteste do MCP",
	# Projeto
	"create_project": "Criando projeto novo",
	"set_active_project": "Selecionando projeto para trabalhar",
	"get_project_settings": "Lendo configurações do projeto",
	"set_project_setting": "Ajustando configuração do projeto",
	"set_main_scene": "Definindo cena principal do jogo",
	"configure_input_action": "Configurando controles (teclado/joystick)",
	"configure_autoload": "Configurando sistema global (singleton)",
	"install_mcp_addon": "Instalando ponte MCP no projeto",
	"generate_project_structure": "Criando estrutura de pastas do projeto",
	# Arquivos
	"inspect_project": "Analisando arquivos do projeto",
	"read_file": "Lendo arquivo do projeto",
	"write_file": "Criando/alterando arquivo",
	"delete_file": "Apagando arquivo",
	"move_file": "Movendo/renomeando arquivo",
	# Cenas
	"create_scene": "Criando cena nova",
	"load_scene_tree": "Carregando estrutura da cena",
	"add_node": "Adicionando elemento na cena",
	"delete_node": "Removendo elemento da cena",
	"set_node_property": "Ajustando propriedade de elemento",
	"get_node_property": "Lendo propriedade de elemento",
	"reparent_node": "Reorganizando elementos na hierarquia",
	"instance_scene_as_child": "Adicionando cena pronta dentro de outra",
	"connect_signal": "Conectando eventos entre elementos",
	"list_signals": "Listando eventos disponíveis",
	# ClassDB
	"query_classdb": "Consultando informações de classe do Godot",
	"list_valid_node_types": "Listando tipos de elementos disponíveis",
	# Scripts
	"generate_gdscript": "Gerando código do jogo",
	"attach_script": "Vinculando código a um elemento",
	"detach_script": "Desvinculando código de elemento",
	"validate_gdscript_syntax": "Verificando erros no código",
	"add_script_variable": "Adicionando variável ao código",
	"add_script_signal": "Adicionando evento ao código",
	# Física
	"add_collision_shape": "Adicionando forma de colisão",
	"set_collision_layer_mask": "Configurando camadas de colisão",
	"set_physics_material": "Configurando material físico (quique/atrito)",
	"create_joint_2d": "Criando junta física 2D",
	# Assets
	"import_texture": "Importando imagem",
	"import_sprite_sheet": "Importando sprite sheet (animação)",
	"import_audio": "Importando áudio",
	# Runtime
	"compile_test": "Compilando o jogo para verificar erros",
	"run_game": "🎮 Executando o jogo",
	"stop_game": "Parando o jogo",
	"launch_editor": "Abrindo editor Godot",
	"close_editor": "Fechando editor Godot",
	"take_screenshot": "Tirando print da tela do editor",
	"read_console_output": "Lendo mensagens do console",
	# Tilemap
	"create_tileset": "Criando conjunto de tiles (mapa)",
	"create_tilemap_layer": "Criando camada do mapa",
	"paint_tilemap_cell": "Pintando célula do mapa",
	# Animação
	"create_animation_player": "Criando reprodutor de animações",
	"create_animation": "Criando animação",
	"create_animation_tree": "Criando árvore de animações avançada",
	# UI
	"create_ui_scene": "Criando interface (botões/menus)",
	"add_control_node": "Adicionando elemento de interface",
	"create_main_menu": "Criando menu principal",
	"create_hud_template": "Criando painel de pontuação/vida",
	"create_pause_menu": "Criando menu de pausa",
	"create_health_bar": "Criando barra de vida",
	# Export
	"list_export_presets": "Listando configurações de exportação",
	"validate_export_templates_installed": "Verificando templates de exportação",
	"build_export": "Exportando jogo final (.exe)",
	"configure_export_preset": "Configurando exportação (nome/versão/ícone)",
	# Segurança
	"list_backups": "Listando backups disponíveis",
	"restore_backup": "Restaurando versão anterior (desfazendo)",
	"git_commit_checkpoint": "Salvando checkpoint no git",
	"undo_last_action": "Desfazendo última ação",
	"get_undo_history": "Listando ações que podem ser desfeitas",
	# Game Bridge
	"inject_input_event": "Simulando tecla/clique no jogo",
	"execute_gdscript_runtime": "Executando código no jogo em execução",
	"watch_signal": "Observando evento no jogo",
	# Visão
	"capture_game_screenshot": "Tirando print do jogo",
	"compare_screenshots": "Comparando screenshots (antes/depois)",
	"detect_empty_screen": "Verificando se a tela está vazia",
	"detect_offscreen_elements": "Verificando elementos fora da tela",
	"record_gameplay_gif": "Gravando gameplay em GIF",
	# Batch
	"add_nodes_batch": "Adicionando vários elementos de uma vez",
	"set_properties_batch": "Ajustando várias propriedades de uma vez",
	# Assets Procedurais
	"generate_placeholder_sprite": "Gerando sprite temporário colorido",
	"generate_placeholder_texture_atlas": "Gerando sprite sheet temporária",
	"generate_background_gradient": "Gerando fundo com degrade",
	"generate_tileset_from_colors": "Gerando tileset a partir de cores",
	"generate_audio_sfx": "Gerando efeito sonoro",
	"suggest_color_palette": "Sugerindo paleta de cores",
	# IA Agêntica
	"analyze_game_structure": "Analisando estrutura completa do jogo",
	"suggest_next_steps": "Sugerindo próximos passos",
	"find_missing_references": "Procurando referências quebradas",
	"validate_game_design": "Validando design do jogo",
	"estimate_game_scope": "Estimando tamanho do projeto",
	"search_codebase": "Buscando no código do projeto",
	"get_project_history": "Listando histórico de alterações",
	# DevSolo — Câmera
	"setup_camera_2d": "Configurando câmera 2D",
	"setup_camera_follow": "Configurando câmera para seguir personagem",
	"setup_camera_shake": "Configurando tremor de câmera",
	# DevSolo — Navegação
	"create_navigation_region_2d": "Criando região de navegação",
	"create_navigation_agent_2d": "Criando agente de pathfinding",
	"bake_navigation_polygon": "Gerando malha de navegação",
	# DevSolo — Save/Load
	"create_save_system": "Criando sistema de save/load",
	"define_save_data": "Definindo dados que serão salvos",
	# DevSolo — UI
	"setup_world_environment": "Configurando ambiente visual (luz/fog/glow)",
	"setup_screen_flash": "Configurando efeito de flash na tela",
	# Polimento Visual
	"create_parallax_background": "Criando fundo com efeito parallax",
	"add_parallax_layer": "Adicionando camada ao fundo parallax",
	"configure_particles_2d": "Configurando partículas 2D",
	"create_particles_3d": "Criando partículas 3D",
	"generate_shader_2d": "Gerando shader 2D (efeito visual)",
	"apply_shader_to_node": "Aplicando efeito visual a elemento",
	"create_path_2d": "Criando caminho/curva 2D",
	"create_patrol_route": "Criando rota de patrulha",
	"create_light_2d": "Criando iluminação 2D",
	# Gênero-Específico
	"create_dialogue_system": "Criando sistema de diálogo",
	"add_dialogue_node": "Adicionando fala ao diálogo",
	"create_dialogue_ui": "Criando interface de diálogo",
	"create_inventory_system": "Criando sistema de inventário",
	"define_inventory_item": "Definindo item do inventário",
	"create_inventory_ui": "Criando interface de inventário",
	"create_bullet_template": "Criando modelo de projétil",
	"create_gun_system": "Criando sistema de arma (tiro/munição)",
	"generate_tilemap_from_noise": "Gerando mapa procedural",
	"generate_dungeon_rooms": "Gerando masmorra procedural",
	"create_loading_screen": "Criando tela de carregamento",
	"load_scene_async": "Carregando cena com barra de progresso",
	# Tween/State Machine
	"create_tween_animation": "Criando animação suave (fade/move/scale)",
	"chain_tweens": "Encadeando animações em sequência",
	"create_state_machine": "Criando máquina de estados",
	"add_state_transition": "Adicionando transição entre estados",
	# Complementos
	"add_raycast_2d": "Adicionando sensor de linha (raycast)",
	"add_shapecast_2d": "Adicionando sensor de área (shapecast)",
	"enable_debug_collisions": "Ativando visualização de colisões",
	"enable_debug_navigation": "Ativando visualização de navegação",
	"get_performance_stats": "Verificando performance do jogo",
	"setup_localization": "Configurando tradução (múltiplos idiomas)",
	"add_translation_string": "Adicionando texto traduzido",
	"create_light_3d": "Criando iluminação 3D",
	"create_csg_shape": "Criando forma 3D de prototipagem",
	"configure_standard_material_3d": "Configurando material 3D",
	"configure_audio_bus": "Configurando canal de áudio (volume/mute)",
	"add_audio_effect": "Adicionando efeito de áudio (reverb/eco)",
	"import_3d_model": "Importando modelo 3D (.glb/.gltf)",
	# Editor Bridge
	"get_editor_state": "Lendo estado do editor",
	"run_scene": "Iniciando cena no editor",
	"stop_scene": "Parando cena no editor",
	"read_console_since": "Lendo console do editor",
	"hot_reload_script": "Recarregando script no editor",
	"rescan_filesystem": "Atualizando arquivos do projeto no editor",
}

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Setup
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

func setup(plugin: EditorPlugin) -> void:
	_plugin = plugin
	_build_ui()
	_load_config()
	_refresh_status()
	_refresh_log()

	_timer = Timer.new()
	_timer.wait_time = 2.0
	_timer.autostart = true
	_timer.timeout.connect(_on_tick)
	add_child(_timer)


func _on_tick() -> void:
	_refresh_status()
	_refresh_log()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# UI Builder
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

func _build_ui() -> void:
	custom_minimum_size = Vector2(300, 0)

	# ScrollContainer para garantir acesso a todo o conteÃºdo
	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(scroll)

	_content = VBoxContainer.new()
	_content.add_theme_constant_override("separation", 2)
	scroll.add_child(_content)

	# â”€â”€ TÃ­tulo â”€â”€
	var titulo := Label.new()
	titulo.text = "ðŸ”Œ MCP IA DEV  v2.0"
	titulo.add_theme_font_size_override("font_size", 14)
	titulo.add_theme_color_override("font_color", COLORS["blue"])
	_content.add_child(titulo)

	_content.add_child(_sep())

	# â”€â”€ Status Servidor â”€â”€
	var sbox := HBoxContainer.new()
	_status_color = _dot(COLORS["red"])
	sbox.add_child(_status_color)
	_status_label = Label.new()
	_status_label.text = "Servidor: verificando..."
	_status_label.add_theme_font_size_override("font_size", 11)
	sbox.add_child(_status_label)
	_content.add_child(sbox)

	# â”€â”€ Status Cliente (IA) â”€â”€
	var cbox := HBoxContainer.new()
	_client_indicator = _dot(COLORS["gray"])
	cbox.add_child(_client_indicator)
	_client_label = Label.new()
	_client_label.text = "IA: aguardando..."
	_client_label.add_theme_font_size_override("font_size", 11)
	cbox.add_child(_client_label)
	_content.add_child(cbox)

	_content.add_child(_sep())

	# â”€â”€ O que estÃ¡ acontecendo â”€â”€
	var oq_label := Label.new()
	oq_label.text = "ðŸ’¬ O QUE ESTÃ ACONTECENDO"
	oq_label.add_theme_font_size_override("font_size", 9)
	oq_label.add_theme_color_override("font_color", COLORS["purple"])
	oq_label.tooltip_text = "Explica em linguagem simples o que a IA estÃ¡ fazendo AGORA"
	_content.add_child(oq_label)

	var oq_happening := RichTextLabel.new()
	oq_happening.name = "OQueEstaAcontecendo"
	oq_happening.bbcode_enabled = true
	oq_happening.fit_content = true
	oq_happening.custom_minimum_size = Vector2(0, 24)
	oq_happening.scroll_active = false
	oq_happening.tooltip_text = "TraduÃ§Ã£o em tempo real do que a IA estÃ¡ fazendo no seu projeto"
	_content.add_child(oq_happening)

	_content.add_child(_sep())

	# â•â•â• ATALHOS â•â•â•
	_content.add_child(_section("ATALHOS"))

	var abox := HBoxContainer.new()
	abox.add_theme_constant_override("separation", 4)

	_btn_play = _btn("â–¶ Play", COLORS["green"])
	_btn_play.pressed.connect(_on_play)
	_btn_play.tooltip_text = "Roda o jogo para testar (atalho: F5)"
	abox.add_child(_btn_play)

	_btn_stop = _btn("â¹ Stop", COLORS["red"])
	_btn_stop.pressed.connect(_on_stop)
	_btn_stop.tooltip_text = "Para o jogo que estÃ¡ rodando (atalho: F8)"
	abox.add_child(_btn_stop)

	_btn_screenshot = _btn("ðŸ“· Shot", COLORS["blue"])
	_btn_screenshot.pressed.connect(_on_screenshot)
	_btn_screenshot.tooltip_text = "Tira um print da tela do editor e abre a pasta"
	abox.add_child(_btn_screenshot)

	_btn_rescan = _btn("ðŸ”„ Rec", COLORS["yellow"])
	_btn_rescan.pressed.connect(_on_rescan)
	_btn_rescan.tooltip_text = "Atualiza a lista de arquivos (use apÃ³s a IA criar novos arquivos)"
	abox.add_child(_btn_rescan)

	_content.add_child(abox)
	_content.add_child(_sep())

	# â•â•â• CONEXÃƒO â•â•â•
	_content.add_child(_section("CONEXÃƒO"))
	_port_editor = _spin_row("Porta Editor", 9080, 1024, 65535)
	_port_game = _spin_row("Porta Jogo", 9081, 1024, 65535)

	_content.add_child(_sep())

	# â•â•â• GODOT â•â•â•
	_content.add_child(_section("GODOT"))
	_godot_path = _path_row("Editor", "C:/Godot/Godot_v4.7-stable_win64.exe")
	_godot_console_path = _path_row("Console", "C:/Godot/Godot_v4.7-stable_win64_console.exe")

	_content.add_child(_sep())

	# â•â•â• PROJETO â•â•â•
	_content.add_child(_section("PROJETO"))

	_proj_name_label = _info_line("Nome")
	_proj_scene_label = _info_line("Main Scene")
	_proj_renderer_label = _info_line("Renderer")

	_default_project = _path_row("Pasta", "")
	_content.add_child(_sep())

	# â•â•â• BOTÃ•ES â•â•â•
	var bbox := HBoxContainer.new()
	bbox.add_theme_constant_override("separation", 4)

	_btn_salvar = Button.new()
	_btn_salvar.text = "ðŸ’¾ Salvar Config"
	_btn_salvar.pressed.connect(_on_salvar)
	_btn_salvar.tooltip_text = "Salva portas e caminhos do Godot. As configs ficam no seu projeto."
	bbox.add_child(_btn_salvar)

	var btn_abrir := Button.new()
	btn_abrir.text = "ðŸ“‚ Abrir Projeto"
	btn_abrir.pressed.connect(_on_abrir_projeto)
	btn_abrir.tooltip_text = "Abre outro projeto Godot em uma nova janela"
	bbox.add_child(btn_abrir)

	var btn_instalar := Button.new()
	btn_instalar.text = "ðŸ“¦ Instalar em Todos"
	btn_instalar.pressed.connect(_on_instalar_todos)
	btn_instalar.tooltip_text = "Instala o MCP IA DEV em todos os projetos recentes do Godot. Assim vocÃª nÃ£o precisa instalar manualmente em cada um."
	bbox.add_child(btn_instalar)

	_content.add_child(bbox)
	_content.add_child(_sep())

	# â•â•â• LOG â•â•â•
	_content.add_child(_section("ATIVIDADE DA IA"))

	# Contador de aÃ§Ãµes
	var counter_label := Label.new()
	counter_label.name = "ActionCounter"
	counter_label.add_theme_color_override("font_color", COLORS["gray"])
	counter_label.add_theme_font_size_override("font_size", 9)
	counter_label.text = "0 comandos recebidos"
	counter_label.tooltip_text = "Quantas aÃ§Ãµes a IA jÃ¡ executou neste projeto"
	_content.add_child(counter_label)

	_log_list = RichTextLabel.new()
	_log_list.bbcode_enabled = true
	_log_list.fit_content = true
	_log_list.custom_minimum_size = Vector2(0, 80)
	_log_list.scroll_active = true
	_log_list.scroll_following = true
	_log_list.tooltip_text = "HistÃ³rico de comandos que a IA enviou. Passe o mouse para ver a traduÃ§Ã£o."
	_content.add_child(_log_list)

	_btn_limpar_log = Button.new()
	_btn_limpar_log.text = "ðŸ—‘ Limpar Log"
	_btn_limpar_log.pressed.connect(_on_limpar_log)
	_btn_limpar_log.tooltip_text = "Apaga o histÃ³rico de comandos da IA"
	_content.add_child(_btn_limpar_log)

	_content.add_child(_sep())

	# â”€â”€ Info â”€â”€
	_info_label = RichTextLabel.new()
	_info_label.bbcode_enabled = true
	_info_label.fit_content = true
	_info_label.custom_minimum_size = Vector2(0, 30)
	_info_label.scroll_active = false
	_content.add_child(_info_label)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# UI Helpers
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

func _dot(color: Color) -> ColorRect:
	var cr := ColorRect.new()
	cr.custom_minimum_size = Vector2(10, 10)
	cr.color = color
	return cr


func _sep() -> HSeparator:
	return HSeparator.new()


func _section(title: String) -> Label:
	var lbl := Label.new()
	lbl.text = "â”€â”€ %s â”€â”€" % title
	lbl.add_theme_font_size_override("font_size", 9)
	lbl.add_theme_color_override("font_color", COLORS["gray"])
	return lbl


func _btn(text: String, color: Color) -> Button:
	var b := Button.new()
	b.text = text
	b.add_theme_color_override("font_color", color)
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return b


func _spin_row(label: String, default_val: int, min_val: int, max_val: int) -> SpinBox:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 2)
	var lbl := Label.new()
	lbl.text = label
	lbl.custom_minimum_size = Vector2(80, 0)
	lbl.add_theme_font_size_override("font_size", 10)
	row.add_child(lbl)

	var spin := SpinBox.new()
	spin.min_value = min_val
	spin.max_value = max_val
	spin.value = default_val
	spin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spin.value_changed.connect(_on_config_changed)
	row.add_child(spin)
	_content.add_child(row)
	return spin


func _path_row(label: String, default_val: String) -> LineEdit:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 2)
	var lbl := Label.new()
	lbl.text = label
	lbl.custom_minimum_size = Vector2(80, 0)
	lbl.add_theme_font_size_override("font_size", 10)
	row.add_child(lbl)

	var line := LineEdit.new()
	line.text = default_val
	line.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	line.text_changed.connect(_on_config_changed)
	row.add_child(line)

	var btn := Button.new()
	btn.text = "ðŸ“"
	btn.tooltip_text = "Selecionar..."
	btn.pressed.connect(_on_browse.bind(line))
	row.add_child(btn)

	_content.add_child(row)
	return line


func _info_line(label: String) -> Label:
	var lbl := Label.new()
	lbl.text = "%s: ---" % label
	lbl.add_theme_color_override("font_color", COLORS["cyan"])
	lbl.add_theme_font_size_override("font_size", 10)
	_content.add_child(lbl)
	return lbl


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# File Dialogs
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

func _on_browse(line: LineEdit) -> void:
	var fd := FileDialog.new()
	fd.access = FileDialog.ACCESS_FILESYSTEM
	fd.file_mode = FileDialog.FILE_MODE_OPEN_FILE
	fd.add_theme_font_size_override("font_size", 14)
	EditorInterface.get_base_control().add_child(fd)

	fd.file_selected.connect(func(path: String):
		line.text = path
		fd.queue_free()
		_on_config_changed("")
	)

	fd.canceled.connect(func(): fd.queue_free())
	fd.popup_centered_ratio(0.6)


func _on_abrir_projeto() -> void:
	var fd := FileDialog.new()
	fd.access = FileDialog.ACCESS_FILESYSTEM
	fd.file_mode = FileDialog.FILE_MODE_OPEN_FILE
	fd.add_filter("*.godot", "Projeto Godot (project.godot)")
	fd.add_theme_font_size_override("font_size", 14)
	EditorInterface.get_base_control().add_child(fd)

	fd.file_selected.connect(func(path: String):
		fd.queue_free()
		var godot := _godot_path.text
		if godot and FileAccess.file_exists(godot):
			var proj_dir := path.get_base_dir()
			OS.create_process(godot, ["--editor", "--path", proj_dir])
			_update_info("âœ… Abrindo: %s" % proj_dir)
		else:
			_update_info("âŒ Godot nÃ£o encontrado em: %s" % godot)
	)

	fd.canceled.connect(func(): fd.queue_free())
	fd.popup_centered_ratio(0.6)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Config (salva em user://mcp_config.json)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

func _config_path() -> String:
	if _plugin and _plugin.has_method("get_config_path"):
		return _plugin.get_config_path()
	return "user://mcp_config.json"


func _load_config() -> void:
	var cfg := _read_config()
	if cfg.is_empty():
		return

	_port_editor.value = cfg.get("addon_port", 9080)
	_port_game.value = cfg.get("game_port", 9081)
	_godot_path.text = cfg.get("godot_path", "")
	_godot_console_path.text = cfg.get("godot_console_path", "")
	_default_project.text = cfg.get("default_project", "")


func _save_config() -> void:
	var cfg := _read_config()
	if cfg.is_empty():
		cfg = {}

	cfg["addon_port"] = int(_port_editor.value)
	cfg["game_port"] = int(_port_game.value)
	cfg["godot_path"] = _godot_path.text
	cfg["godot_console_path"] = _godot_console_path.text
	cfg["default_project"] = _default_project.text

	var path := _config_path()
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(cfg, "\t"))
		file.close()
		_update_info("âœ… Config salva em: %s" % path)
	else:
		_update_info("âŒ ERRO ao salvar em: %s" % path)


func _read_config() -> Dictionary:
	var path := _config_path()
	if not FileAccess.file_exists(path):
		return {}

	var file := FileAccess.open(path, FileAccess.READ)
	if not file:
		return {}

	var text := file.get_as_text()
	file.close()

	var json_conv := JSON.new()
	if json_conv.parse(text) != OK:
		return {}

	return json_conv.data


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Actions (botÃµes)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

func _on_play() -> void:
	EditorInterface.play_main_scene()
	_update_info("â–¶ Cena iniciada")


func _on_stop() -> void:
	EditorInterface.stop_playing_scene()
	_update_info("â¹ Cena parada")


func _on_screenshot() -> void:
	var viewport := EditorInterface.get_editor_viewport_2d()
	if not viewport:
		_update_info("âŒ Viewport 2D indisponÃ­vel")
		return

	var img := viewport.get_texture().get_image()
	if not img:
		_update_info("âŒ Falha ao capturar imagem")
		return

	var path := "user://mcp_shot_%d.png" % Time.get_unix_time_from_system()
	if img.save_png(path) == OK:
		var global := ProjectSettings.globalize_path(path)
		_update_info("ðŸ“· Salvo: %s" % global)
		OS.shell_show_in_file_manager(global)
	else:
		_update_info("âŒ Falha ao salvar screenshot")


func _on_rescan() -> void:
	EditorInterface.get_resource_filesystem().scan()
	_update_info("ðŸ”„ Rescan concluÃ­do")


func _on_limpar_log() -> void:
	if _plugin and _plugin.has_method("clear_command_log"):
		_plugin.clear_command_log()
	_log_list.text = "[i](vazio)[/i]"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Signals
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

func _on_config_changed(_val = "") -> void:
	_update_info("âš™ï¸ AlteraÃ§Ãµes nÃ£o salvas")


func _on_salvar() -> void:
	_save_config()
	if _plugin and _plugin.has_method("_reload_config"):
		_plugin._reload_config()


func _on_instalar_todos() -> void:
	"""Instala o addon MCP em todos os projetos recentes."""
	var cfg_path := OS.get_user_data_dir().path_join("../../Godot/projects.cfg")
	if not FileAccess.file_exists(cfg_path):
		_update_info("âŒ projects.cfg nÃ£o encontrado")
		return

	var file := FileAccess.open(cfg_path, FileAccess.READ)
	if not file:
		return
	var content := file.get_as_text()
	file.close()

	# Extrai paths de projetos do formato [path]\nfavorite=...
	var projects: Array[String] = []
	for line in content.split("\n"):
		var stripped := line.strip_edges()
		if stripped.begins_with("[") and stripped.ends_with("]"):
			var proj_path := stripped.substr(1, stripped.length() - 2)
			if proj_path.begins_with("C:") or proj_path.begins_with("/"):
				projects.append(proj_path)

	var instalados := 0
	var erros := 0
	var source := "res://addons/mcp_bridge"

	for proj_path in projects:
		var dest := proj_path.path_join("addons/mcp_bridge")
		DirAccess.make_dir_recursive_absolute(dest)

		# Copia arquivos do addon
		var src_dir := DirAccess.open(source)
		if src_dir:
			src_dir.list_dir_begin()
			var fname := src_dir.get_next()
			while fname != "":
				if not fname.begins_with(".") and not fname.ends_with(".uid"):
					var src_file := source.path_join(fname)
					var dst_file := dest.path_join(fname)
					DirAccess.copy_absolute(src_file, dst_file)
				fname = src_dir.get_next()
				src_dir.list_dir_end()

		# Ativa plugin no project.godot
		var godot_file := proj_path.path_join("project.godot")
		if FileAccess.file_exists(godot_file):
			var f := FileAccess.open(godot_file, FileAccess.READ)
			if f:
				var proj_content := f.get_as_text()
				f.close()
				var plugin_line := 'enabled=PackedStringArray("res://addons/mcp_bridge/plugin.cfg")'
				if "[editor_plugins]" not in proj_content:
					proj_content += "\n[editor_plugins]\n" + plugin_line + "\n"
					var fw := FileAccess.open(godot_file, FileAccess.WRITE)
					if fw:
						fw.store_string(proj_content)
						fw.close()
			instalados += 1

	_update_info("ðŸ“¦ Instalado em %d projeto(s)! Reinicie o Godot para ativar." % instalados)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Status Refresh
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

func _refresh_status() -> void:
	if not is_inside_tree():
		return

	# Servidor
	if _plugin and _plugin.has_method("is_server_running") and _plugin.is_server_running():
		_status_color.color = COLORS["green"]
		_status_label.text = "Servidor ativo (porta %d)" % int(_port_editor.value)
	else:
		_status_color.color = COLORS["red"]
		_status_label.text = "Servidor parado"

	# Cliente (IA)
	if _plugin and _plugin.has_method("is_client_connected") and _plugin.is_client_connected():
		_client_indicator.color = COLORS["green"]
		_client_label.text = "IA conectada (pode criar/modificar jogos)"
		_client_label.tooltip_text = "A IA estÃ¡ linkada e pronta para criar jogos no projeto ATUAL. Suas aÃ§Ãµes aparecem no log abaixo."
	else:
		_client_indicator.color = COLORS["gray"]
		_client_label.text = "IA offline (rode o launch.py para conectar)"
		_client_label.tooltip_text = "Execute o atalho 'MCP IA DEV' na Ãrea de Trabalho para conectar a IA"

	# Atualiza contador de aÃ§Ãµes
	if _plugin and _plugin.has_method("get_command_log"):
		var log: Array = _plugin.get_command_log()
		var counter := get_node_or_null("ActionCounter") as Label
		if counter:
			counter.text = "%d comandos recebidos" % log.size()

	# Info do projeto
	if _plugin and _plugin.has_method("get_project_info"):
		var info: Dictionary = _plugin.get_project_info()
		_proj_name_label.text = "Nome: %s" % info.get("name", "?")
		_proj_scene_label.text = "Main Scene: %s" % info.get("main_scene", "---")
		_proj_renderer_label.text = "Renderer: %s" % info.get("renderer", "?")

	# Estado do jogo
	var playing := EditorInterface.get_playing_scene() != null
	if playing:
		_btn_play.disabled = true
		_btn_stop.disabled = false
		_btn_play.text = "â–¶ (rodando)"
	else:
		_btn_play.disabled = false
		_btn_stop.disabled = true
		_btn_play.text = "â–¶ Play"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Log Refresh
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

func _refresh_log() -> void:
	if not is_inside_tree():
		return
	if not _plugin or not _plugin.has_method("get_command_log"):
		return

	var log: Array = _plugin.get_command_log()

	# Atualiza contador de acoes da IA
	var counter := get_node_or_null("ActionCounter") as Label
	if counter:
		counter.text = "%d acoes da IA recebidas" % log.size()

	if log.is_empty():
		if _log_list.text == "":
			_log_list.text = "[i][color=gray](sem atividade — a IA ainda nao enviou comandos)[/color][/i]"
		var oq := get_node_or_null("OQueEstaAcontecendo") as RichTextLabel
		if oq:
			oq.text = "[i][color=gray]Aguardando comandos da IA...[/color][/i]"
		return

	var output_lines: Array[String] = []
	var max_show := 35
	var last_friendly := ""

	# Itera do mais recente para o mais antigo
	var i := log.size() - 1
	while i >= 0 and output_lines.size() < max_show:
		var entry: Dictionary = log[i]
		var time_str: String = entry.get("time", "")
		if time_str.length() > 5:
			time_str = time_str.substr(0, 5)
		var method: String = entry.get("method", "?")
		var friendly := TRANSLATE.get(method, method)
		var status: String = entry.get("status", "ok")

		if output_lines.size() == 0:
			last_friendly = friendly

		var icon := "  "
		var color := "#88cc88"
		match status:
			"error":
				icon = "X "
				color = "#ff6666"
			"working":
				icon = "..."
				color = "#ffcc66"

		var line := "[color=gray][%s][/color] [color=%s]%s[/color] %s" % [time_str, color, icon, friendly]
		output_lines.push_front(line)
		i -= 1

	_log_list.text = "\n".join(output_lines)

	var oq := get_node_or_null("OQueEstaAcontecendo") as RichTextLabel
	if oq and last_friendly != "":
		oq.text = "[color=#66ccff][b]>> %s[/b][/color]" % last_friendly

func _update_info(msg: String) -> void:
	_info_label.text = msg
	if is_inside_tree():
		var t := get_tree().create_timer(4.0)
		t.timeout.connect(func():
			if _info_label.text == msg:
				_info_label.text = ""
		)


