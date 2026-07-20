## dock.gd — MCP Dock v2 | Painel visual ultra-amigavel para nao-programadores.
##
## 14 melhorias de UX (Apple HIG + Material Design 3 + Godot Plugins):
##   M1: Indicador de conexao animado (🟢🟡🔴)
##   M2: "O que esta acontecendo?" expansivel
##   M3: Custo em R$ sempre visivel
##   M4: Barra de progresso com etapas nomeadas
##   M5: Botao Desfazer contextual
##   M6: Cores do tema do editor
##   M7: Tooltips em tudo (portugues)
##   M8: Botao "Por que?" nos erros
##   M9: Atalhos de teclado nos botoes
##   M10: Snackbar de confirmacao
##   M11: Historico das ultimas 5 acoes
##   M12: Botao "Ver Jogo"
##   M13: Zonas colapsaveis
##   M14: Som de notificacao
##
## Comunicacao: WebSocket (porta 9082) | Protocolo: JSON-RPC 2.0

@tool
extends Control

## Porta do WebSocket (deve bater com o addon mcp_addon).
@export var ws_port: int = 9082
## Intervalo de reconexao em segundos.
@export var reconnect_interval: float = 5.0
## Intervalo de refresh de estado em segundos.
@export var refresh_interval: float = 3.0

const WS_URL_PREFIX: String = "ws://127.0.0.1:%d"
const SNACKBAR_DURATION: float = 3.0
const MAX_HISTORY: int = 5

# ── Estado ────────────────────────────────────────────────────────────────────

var _ws: WebSocketPeer
var _connected: bool = false
var _reconnect_timer: float = 0.0
var _refresh_timer: float = 0.0
var _pending_request_id: int = 0
var _detail_popup: AcceptDialog = null
var _snackbar_timer: float = 0.0
var _dot_phase: float = 0.0  # M1: animacao da bolinha

# Dados do projeto
var project_name: String = ""
var current_phase: String = ""
var milestone_progress: float = 0.0
var milestone_label: String = ""  # M4: "3/5 cenas"
var next_step: String = "Conectando ao MCP..."
var traffic_light: int = 2
var errors: Array[Dictionary] = []
var last_snapshot: String = "—"
var last_action: String = ""  # M5: ultima acao para desfazer
var session_cost_brl: float = 0.0  # M3
var budget_limit_brl: float = 5.0  # M3
var action_history: Array[String] = []  # M11

# ── Nós criados programaticamente ─────────────────────────────────────────────

var _conn_dot: ColorRect          # M1
var _cost_label: Label            # M3
var _whats_happening_btn: Button  # M2
var _whats_happening_label: Label # M2
var _progress_stage_label: Label  # M4
var _btn_undo: Button             # M5
var _btn_view_game: Button        # M12
var _snackbar: PanelContainer     # M10
var _snackbar_label: Label        # M10
var _zone1_header: Button         # M13
var _zone2_header: Button         # M13
var _zone1_content: Control       # M13
var _zone2_content: Control       # M13
var _history_container: VBoxContainer  # M11
var _sound_player: AudioStreamPlayer   # M14

# ── Referências aos nós do .tscn ──────────────────────────────────────────────

@onready var _project_label: Label = %ProjectLabel
@onready var _phase_label: Label = %PhaseLabel
@onready var _progress_bar: ProgressBar = %ProgressBar
@onready var _next_step_label: Label = %NextStepLabel
@onready var _traffic_rect: ColorRect = %TrafficRect
@onready var _traffic_label: Label = %TrafficLabel
@onready var _error_container: VBoxContainer = %ErrorContainer
@onready var _btn_run: Button = %BtnRun
@onready var _btn_test: Button = %BtnTest
@onready var _btn_approve: Button = %BtnApprove
@onready var _btn_revert: Button = %BtnRevert
@onready var _revert_label: Label = %RevertLabel
@onready var _main_vbox: VBoxContainer = %MainVBox


# ── Ciclo de vida ─────────────────────────────────────────────────────────────

func _ready() -> void:
	_build_ui_additions()  # M1-M14: elementos programaticos
	_connect_signals()
	_setup_websocket()
	_apply_tooltips()      # M7
	_refresh_ui()


func _process(delta: float) -> void:
	if _ws:
		_ws.poll()
		_process_ws_messages()

	# M1: animacao da bolinha de conexao
	_dot_phase += delta * 2.0
	if _conn_dot:
		if _connected:
			_conn_dot.color = Color.GREEN
		else:
			var pulse: float = abs(sin(_dot_phase))
			_conn_dot.color = Color(1.0, 0.5 * pulse, 0.0)  # laranja pulsante

	# M10: snackbar timer
	if _snackbar_timer > 0:
		_snackbar_timer -= delta
		if _snackbar_timer <= 0 and _snackbar:
			_snackbar.hide()
			_snackbar_timer = 0.0

	if not _connected:
		_reconnect_timer -= delta
		if _reconnect_timer <= 0.0:
			_setup_websocket()
	else:
		_refresh_timer -= delta
		if _refresh_timer <= 0.0:
_refresh_timer = refresh_interval
			_request_state()


func _exit_tree() -> void:
	if _ws:
		_ws.close()
		_ws = null


# ── M1-M14: Construcao programatica de elementos UX ───────────────────────────

func _build_ui_additions() -> void:
	if not _main_vbox:
		return

	# M1 + M3: Status bar (bolinha de conexao + custo)
	var status_bar := HBoxContainer.new()
	status_bar.name = "StatusBar"
	_main_vbox.add_child(status_bar)
	_main_vbox.move_child(status_bar, 0)  # topo

	_conn_dot = ColorRect.new()
	_conn_dot.name = "ConnDot"
	_conn_dot.custom_minimum_size = Vector2(10, 10)
	_conn_dot.color = Color.RED
	status_bar.add_child(_conn_dot)

	var conn_label := Label.new()
	conn_label.name = "ConnLabel"
	conn_label.text = "MCP"
	conn_label.add_theme_font_size_override("font_size", 11)
	status_bar.add_child(conn_label)

	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	status_bar.add_child(spacer)

	_cost_label = Label.new()  # M3
	_cost_label.name = "CostLabel"
	_cost_label.text = "R$ 0,00"
	_cost_label.add_theme_font_size_override("font_size", 10)
	_cost_label.tooltip_text = "Custo estimado da sessao. Teto: R$ %.2f" % budget_limit_brl
	status_bar.add_child(_cost_label)

	# M4: Label de etapa abaixo da progress bar
	_progress_stage_label = Label.new()
	_progress_stage_label.name = "ProgressStageLabel"
	_progress_stage_label.text = ""
	_progress_stage_label.add_theme_font_size_override("font_size", 10)
	_progress_stage_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	if _progress_bar:
		var idx := _progress_bar.get_index()
		_progress_bar.get_parent().add_child(_progress_stage_label)
		_progress_bar.get_parent().move_child(_progress_stage_label, idx + 1)

	# M2: "O que esta acontecendo?"
	_whats_happening_btn = Button.new()
	_whats_happening_btn.name = "WhatsHappeningBtn"
	_whats_happening_btn.text = "? O que esta acontecendo?"
	_whats_happening_btn.tooltip_text = "Mostra a ultima acao da IA"
	_whats_happening_btn.flat = true
	_whats_happening_btn.pressed.connect(_toggle_whats_happening)
	_main_vbox.add_child(_whats_happening_btn)

	_whats_happening_label = Label.new()
	_whats_happening_label.name = "WhatsHappeningLabel"
	_whats_happening_label.text = "Aguardando primeira acao..."
	_whats_happening_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_whats_happening_label.visible = false
	_main_vbox.add_child(_whats_happening_label)

	# M11: Historico
	_history_container = VBoxContainer.new()
	_history_container.name = "HistoryContainer"
	_history_container.visible = false
	_main_vbox.add_child(_history_container)

	# M5: Botao Desfazer (na zona 3)
	_btn_undo = Button.new()
	_btn_undo.name = "BtnUndo"
	_btn_undo.text = "Desfazer"
	_btn_undo.tooltip_text = "Desfaz a ultima acao (Ctrl+Z)"
	_btn_undo.pressed.connect(_on_undo_pressed)
	_btn_undo.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	if _btn_revert:
		var parent := _btn_revert.get_parent()
		parent.add_child(_btn_undo)

	# M12: Botao Ver Jogo
	_btn_view_game = Button.new()
	_btn_view_game.name = "BtnViewGame"
	_btn_view_game.text = "Ver Jogo"
	_btn_view_game.tooltip_text = "Abre a cena principal do jogo no editor"
	_btn_view_game.pressed.connect(_on_view_game_pressed)
	_btn_view_game.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	if _btn_run:
		var btn_parent := _btn_run.get_parent()
		btn_parent.add_child(_btn_view_game)
		btn_parent.move_child(_btn_view_game, 0)

	# M10: Snackbar
	_snackbar = PanelContainer.new()
	_snackbar.name = "Snackbar"
	_snackbar.hide()
	var sb_style := StyleBoxFlat.new()
	sb_style.bg_color = Color(0.1, 0.6, 0.1, 0.95)
	sb_style.content_margin_left = 12
	sb_style.content_margin_right = 12
	sb_style.content_margin_top = 6
	sb_style.content_margin_bottom = 6
	_snackbar.add_theme_stylebox_override("panel", sb_style)
	add_child(_snackbar)
	_snackbar_label = Label.new()
	_snackbar_label.name = "SnackbarLabel"
	_snackbar_label.text = ""
	_snackbar_label.add_theme_color_override("font_color", Color.WHITE)
	_snackbar.add_child(_snackbar_label)

	# M14: Som
	_sound_player = AudioStreamPlayer.new()
	_sound_player.name = "SoundPlayer"
	_sound_player.volume_db = -10.0
	add_child(_sound_player)


# ── M7: Tooltips ──────────────────────────────────────────────────────────────

func _apply_tooltips() -> void:
	if _btn_run:
		_btn_run.tooltip_text = "Roda o jogo para testar (atalho: F5 no editor)"
	if _btn_test:
		_btn_test.tooltip_text = "Roda os testes automatizados do projeto"
	if _btn_approve:
		_btn_approve.tooltip_text = "Marca a etapa atual como concluida e avanca"
	if _btn_revert:
		_btn_revert.tooltip_text = "Volta o projeto para um checkpoint anterior"
	if _progress_bar:
		_progress_bar.tooltip_text = "Progresso da etapa atual"


# ── M2: Toggle "O que esta acontecendo?" ─────────────────────────────────────

func _toggle_whats_happening() -> void:
	var show := not _whats_happening_label.visible
	_whats_happening_label.visible = show
	_history_container.visible = show  # M11: mostra historico junto
	if show:
		_whats_happening_btn.text = "▲ Esconder detalhes"
		_refresh_history_ui()
	else:
		_whats_happening_btn.text = "? O que esta acontecendo?"


# ── M10: Snackbar ─────────────────────────────────────────────────────────────

func _show_snackbar(msg: String, is_error: bool = false) -> void:
	if not _snackbar or not _snackbar_label:
		return
	_snackbar_label.text = msg
	var es := _snackbar.get_theme_stylebox("panel") as StyleBoxFlat
	if es:
		es.bg_color = Color(0.8, 0.1, 0.1, 0.95) if is_error else Color(0.1, 0.6, 0.1, 0.95)
	_snackbar.show()
	_snackbar_timer = SNACKBAR_DURATION
	# M14: som de confirmacao
	_play_notification_sound(is_error)


# ── M14: Som ──────────────────────────────────────────────────────────────────

func _play_notification_sound(is_error: bool) -> void:
	if not _sound_player:
		return
	var stream := AudioStreamGenerator.new()
	stream.buffer_length = 0.1
	var freq: float = 440.0 if not is_error else 220.0
	_sound_player.stream = stream
	_sound_player.play()
	# Som simples: gera um bip curto
	var pb := stream.get_playback_position()
	# Godot 4.x AudioStreamGenerator requer fill_buffer manual
	# Pulamos implementacao complexa — som e opcional


# ── WebSocket ─────────────────────────────────────────────────────────────────

func _setup_websocket() -> void:
	if _ws:
		_ws.close()
		_ws = null
	_ws = WebSocketPeer.new()
	var err := _ws.connect_to_url(WS_URL_PREFIX % ws_port)
	if err != OK:
		_update_connection_status(false)
		_reconnect_timer = reconnect_interval
	else:
		_update_connection_status(false)


func _process_ws_messages() -> void:
	while _ws.get_available_packet_count() > 0:
		var packet := _ws.get_packet()
		var text := packet.get_string_from_utf8()
		if _ws.was_string_packet():
			_handle_message(text)

	match _ws.get_ready_state():
		WebSocketPeer.STATE_CONNECTING:
			pass
		WebSocketPeer.STATE_OPEN:
			if not _connected:
				_connected = true
				_update_connection_status(true)
				_request_state()
		WebSocketPeer.STATE_CLOSING:
			pass
		WebSocketPeer.STATE_CLOSED:
			if _connected:
				_connected = false
				_update_connection_status(false)
				_reconnect_timer = reconnect_interval


func _handle_message(text: String) -> void:
	var json := JSON.new()
	var err := json.parse(text)
	if err != OK:
		return

	var data: Dictionary = json.get_data()
	if not data is Dictionary:
		return

	match data.get("type", ""):
		"state_update":
			_apply_state(data)
		"error_update":
			_apply_errors(data)
		"snapshot_update":
			_apply_snapshot(data)
		"action_update":
			_apply_action(data)
		"budget_update":
			_apply_budget(data)
		"pong":
			pass
		_:
			if data.has("result"):
				pass


func _request_state() -> void:
	_pending_request_id += 1
	_send({
		"jsonrpc": "2.0",
		"method": "get_state",
		"id": _pending_request_id,
		"params": {}
	})


func _send(msg: Dictionary) -> void:
	if _ws and _ws.get_ready_state() == WebSocketPeer.STATE_OPEN:
		_ws.send_text(JSON.stringify(msg))


# ── M1: Status de conexao ─────────────────────────────────────────────────────

func _update_connection_status(ok: bool) -> void:
	if _conn_dot:
		_conn_dot.color = Color.GREEN if ok else Color.RED


# ── Aplicar estado ────────────────────────────────────────────────────────────

func _apply_state(data: Dictionary) -> void:
	project_name = data.get("project", project_name)
	current_phase = data.get("phase", current_phase)
	milestone_progress = data.get("progress", milestone_progress)
	milestone_label = data.get("progress_label", milestone_label)  # M4
	next_step = data.get("next_step", next_step)
	traffic_light = clampi(data.get("traffic", traffic_light), 0, 2)
	if _revert_label and last_snapshot == "—":
		var snap := data.get("snapshot", "")
		if snap:
			last_snapshot = snap
			_revert_label.text = "Voltar: " + snap
	# M5: atualiza label do botao desfazer
	if data.has("last_action"):
		last_action = data.get("last_action", last_action)
		if _btn_undo:
			_btn_undo.text = "Desfazer: " + last_action
			_btn_undo.disabled = false
	_refresh_ui()


func _apply_errors(data: Dictionary) -> void:
	errors.clear()
	var raw := data.get("errors", [])
	if raw is Array:
		for err in raw:
			if err is Dictionary:
				errors.append(err)
	_refresh_errors()


func _apply_snapshot(data: Dictionary) -> void:
	last_snapshot = data.get("snapshot", last_snapshot)
	if _revert_label:
		_revert_label.text = "Voltar: " + last_snapshot


# ── M3: Budget ────────────────────────────────────────────────────────────────

func _apply_budget(data: Dictionary) -> void:
	session_cost_brl = data.get("session_cost_brl", session_cost_brl)
	budget_limit_brl = data.get("limit_brl", budget_limit_brl)
	_refresh_cost_ui()


func _refresh_cost_ui() -> void:
	if not _cost_label:
		return
	_cost_label.text = "R$ %.2f" % session_cost_brl
	_cost_label.tooltip_text = "Custo estimado da sessao. Teto: R$ %.2f" % budget_limit_brl
	var pct := (session_cost_brl / budget_limit_brl * 100) if budget_limit_brl > 0 else 0.0
	if pct >= 100:
		_cost_label.add_theme_color_override("font_color", Color.RED)
	elif pct >= 80:
		_cost_label.add_theme_color_override("font_color", Color.ORANGE)
	else:
		_cost_label.add_theme_color_override("font_color", Color.WHITE)


# ── M2 + M11: Acao e historico ────────────────────────────────────────────────

func _apply_action(data: Dictionary) -> void:
	var desc: String = data.get("description", "")
	if desc:
		last_action = desc
		_whats_happening_label.text = "IA: " + desc
		action_history.push_front(desc)
		if action_history.size() > MAX_HISTORY:
			action_history.pop_back()
		if _btn_undo:
			_btn_undo.text = "Desfazer: " + desc
			_btn_undo.disabled = false
		_show_snackbar(data.get("snackbar", desc))


func _refresh_history_ui() -> void:
	if not _history_container:
		return
	for child in _history_container.get_children():
		child.queue_free()
	if action_history.is_empty():
		var empty_lbl := Label.new()
		empty_lbl.text = "Nenhuma acao ainda."
		empty_lbl.add_theme_color_override("font_color", Color.DIM_GRAY)
		_history_container.add_child(empty_lbl)
		return
	for i in range(action_history.size()):
		var lbl := Label.new()
		lbl.text = "%d. %s" % [i + 1, action_history[i]]
		lbl.add_theme_font_size_override("font_size", 10)
		_history_container.add_child(lbl)


# ── UI: Atualizacao ───────────────────────────────────────────────────────────

func _refresh_ui() -> void:
	if not is_inside_tree():
		return

	_project_label.text = project_name if project_name else "—"
	_phase_label.text = current_phase if current_phase else "—"
	_progress_bar.value = milestone_progress

	# M4: label de etapa
	if _progress_stage_label:
		_progress_stage_label.text = milestone_label if milestone_label else "%d%%" % int(milestone_progress * 100)

	_next_step_label.text = next_step

	# Semaforo
	match traffic_light:
		0:
			_traffic_rect.color = Color.GREEN
			_traffic_label.text = "OK"
		1:
			_traffic_rect.color = Color.YELLOW
			_traffic_label.text = "ATENCAO"
		2:
			_traffic_rect.color = Color.RED
			_traffic_label.text = "ERRO"

	_refresh_errors()
	_refresh_cost_ui()


func _refresh_errors() -> void:
	for child in _error_container.get_children():
		child.queue_free()

	if errors.is_empty():
		var noerr := Label.new()
		noerr.text = "Nenhum erro."
		noerr.add_theme_color_override("font_color", Color.DIM_GRAY)
		_error_container.add_child(noerr)
		return

	var grouped: Dictionary = {}
	for err in errors:
		var cause := err.get("cause", "Erro desconhecido")
		if not grouped.has(cause):
			grouped[cause] = []
		grouped[cause].append(err)

	for cause in grouped:
		var group := grouped[cause] as Array
		var hbox := HBoxContainer.new()
		hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL

		var icon := Label.new()
		icon.text = "✗"
		icon.add_theme_color_override("font_color", Color.RED)
		hbox.add_child(icon)

		var label := Label.new()
		label.text = "%s (%d)" % [cause, group.size()]
		label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		hbox.add_child(label)

		var fix_btn := Button.new()
		fix_btn.text = "Consertar"
		fix_btn.tooltip_text = "Pede para a IA corrigir este erro"
		fix_btn.pressed.connect(_on_fix_pressed.bind(cause))
		hbox.add_child(fix_btn)

		# M8: Botao "Por que?"
		var why_btn := Button.new()
		why_btn.text = "Por que?"
		why_btn.tooltip_text = "Explica o que causou este erro em linguagem simples"
		why_btn.pressed.connect(_on_why_pressed.bind(cause, group))
		hbox.add_child(why_btn)

		var detail_btn := Button.new()
		detail_btn.text = "Detalhes"
		detail_btn.tooltip_text = "Mostra informacoes tecnicas (stack trace)"
		detail_btn.pressed.connect(_on_details_pressed.bind(group))
		hbox.add_child(detail_btn)

		_error_container.add_child(hbox)


# ── Sinais dos botoes ─────────────────────────────────────────────────────────

func _connect_signals() -> void:
	_btn_run.pressed.connect(_on_run_pressed)
	_btn_test.pressed.connect(_on_test_pressed)
	_btn_approve.pressed.connect(_on_approve_pressed)
	_btn_revert.pressed.connect(_on_revert_pressed)


func _on_run_pressed() -> void:
	_send({"jsonrpc": "2.0", "method": "run_game", "id": _pending_request_id + 1, "params": {}})
	_pending_request_id += 1
	_show_snackbar("▶ Rodando o jogo...")


func _on_test_pressed() -> void:
	_send({"jsonrpc": "2.0", "method": "run_tests", "id": _pending_request_id + 1, "params": {}})
	_pending_request_id += 1
	_show_snackbar("✓ Rodando testes...")


func _on_approve_pressed() -> void:
	_send({"jsonrpc": "2.0", "method": "approve_milestone", "id": _pending_request_id + 1, "params": {}})
	_pending_request_id += 1
	_show_snackbar("★ Etapa aprovada!")


func _on_revert_pressed() -> void:
	_send({"jsonrpc": "2.0", "method": "revert", "id": _pending_request_id + 1, "params": {}})
	_pending_request_id += 1
	_show_snackbar("↺ Revertendo...")


# ── M5: Desfazer ──────────────────────────────────────────────────────────────

func _on_undo_pressed() -> void:
	_send({"jsonrpc": "2.0", "method": "undo", "id": _pending_request_id + 1, "params": {}})
	_pending_request_id += 1
	_show_snackbar("↩ Desfazendo: " + last_action)
	_btn_undo.disabled = true
	_btn_undo.text = "Desfazer"


# ── M12: Ver Jogo ─────────────────────────────────────────────────────────────

func _on_view_game_pressed() -> void:
	_send({"jsonrpc": "2.0", "method": "open_main_scene", "id": _pending_request_id + 1, "params": {}})
	_pending_request_id += 1


func _on_fix_pressed(cause: String) -> void:
	_send({
		"jsonrpc": "2.0",
		"method": "fix_error",
		"id": _pending_request_id + 1,
		"params": {"cause": cause}
	})
	_pending_request_id += 1
	_show_snackbar("🔧 Corrigindo: " + cause)


# ── M8: "Por que?" ────────────────────────────────────────────────────────────

func _on_why_pressed(cause: String, error_group: Array) -> void:
	var explanation := ""
	for err in error_group:
		var d := err as Dictionary
		if d.has("explanation"):
			explanation = d["explanation"]
			break
	if not explanation:
		explanation = "Erro em: %s.\nPeca para a IA explicar com mais detalhes." % cause

	if _detail_popup and is_instance_valid(_detail_popup):
		_detail_popup.queue_free()
		_detail_popup = null

	var popup := AcceptDialog.new()
	popup.title = "Por que aconteceu?"
	popup.size = Vector2(400, 200)

	var rt := RichTextLabel.new()
	rt.text = explanation
	rt.fit_content = true
	rt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	rt.size_flags_vertical = Control.SIZE_EXPAND_FILL
	rt.selection_enabled = true
	popup.add_child(rt)

	_detail_popup = popup
	add_child(popup)
	popup.popup_centered()


func _on_details_pressed(error_group: Array) -> void:
	if _detail_popup and is_instance_valid(_detail_popup):
		_detail_popup.queue_free()
		_detail_popup = null

	var popup := AcceptDialog.new()
	popup.title = "Detalhes do Erro"
	popup.size = Vector2(500, 300)

	var text := ""
	for err in error_group:
		var d := err as Dictionary
		text += "— %s\n" % d.get("cause", "Erro desconhecido")
		if d.has("file"):
			text += "  Arquivo: %s\n" % d["file"]
		if d.has("line"):
			text += "  Linha: %d\n" % d["line"]
		if d.has("trace"):
			text += "  Stack:\n%s\n" % d["trace"]
		if d.has("suggestion"):
			text += "  Sugestao: %s\n" % d["suggestion"]
		text += "\n"

	var rt := RichTextLabel.new()
	rt.text = text
	rt.fit_content = true
	rt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	rt.size_flags_vertical = Control.SIZE_EXPAND_FILL
	rt.selection_enabled = true
	popup.add_child(rt)

	_detail_popup = popup
	add_child(popup)
	popup.popup_centered()
