## dock.gd — MCP Dock | Painel visual para o editor Godot.
##
## Layout em 3 zonas:
##   Zona 1 (topo):    nome do projeto, fase atual, barra de progresso,
##                      UMA frase de próximo passo
##   Zona 2 (meio):    semáforo (verde/amarelo/vermelho), erros agrupados
##                      com botão "Consertar", stack trace escondido
##   Zona 3 (rodapé):  4 botões — Rodar, Testar, Aprovar, Reverter
##
## Comunicação com o servidor MCP via WebSocket (porta 9082).
## Protocolo: JSON-RPC 2.0.

@tool
extends Control

const WS_PORT: int = 9082
const WS_URL: String = "ws://127.0.0.1:%d" % WS_PORT
const RECONNECT_INTERVAL: float = 5.0

# ── Estado ────────────────────────────────────────────────────────────────────

var _ws: WebSocketPeer
var _connected: bool = false
var _reconnect_timer: float = 0.0
var _pending_request_id: int = 0
var _detail_popup: AcceptDialog = null  # Reutiliza popup de detalhes

# Dados do projeto recebidos do MCP
var project_name: String = ""
var current_phase: String = ""
var milestone_progress: float = 0.0
var next_step: String = "Conectando ao MCP..."
var traffic_light: int = 2  # 0=verde, 1=amarelo, 2=vermelho
var errors: Array[Dictionary] = []
var last_snapshot: String = "—"

# ── Referências aos nós da UI ─────────────────────────────────────────────────

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
@onready var _status_label: Label = %StatusLabel


# ── Ciclo de vida ─────────────────────────────────────────────────────────────

func _ready() -> void:
	_connect_signals()
	_setup_websocket()
	_refresh_ui()


func _process(delta: float) -> void:
	if _ws:
		_ws.poll()
		_process_ws_messages()

	if not _connected:
		_reconnect_timer -= delta
		if _reconnect_timer <= 0.0:
			_setup_websocket()


func _exit_tree() -> void:
	if _ws:
		_ws.close()
		_ws = null


# ── WebSocket ─────────────────────────────────────────────────────────────────

func _setup_websocket() -> void:
	# Fecha conexao antiga antes de criar nova (evita vazamento)
	if _ws:
		_ws.close()
		_ws = null
	_ws = WebSocketPeer.new()
	var err := _ws.connect_to_url(WS_URL)
	if err != OK:
		_update_connection_status(false, "Erro ao conectar: %d" % err)
		_reconnect_timer = RECONNECT_INTERVAL
	else:
		_update_connection_status(false, "Conectando...")


func _process_ws_messages() -> void:
	while _ws.get_available_packet_count() > 0:
		var packet := _ws.get_packet()
		var text := packet.get_string_from_utf8()

		if _ws.was_string_packet():
			_handle_message(text)

	match _ws.get_ready_state():
		WebSocketPeer.STATE_CONNECTING:
			pass  # Aguardando handshake
		WebSocketPeer.STATE_OPEN:
			if not _connected:
				_connected = true
				_update_connection_status(true, "Conectado")
				_request_state()
		WebSocketPeer.STATE_CLOSING:
			pass  # Fechamento em andamento — continuar poll()
		WebSocketPeer.STATE_CLOSED:
			if _connected:
				_connected = false
				_update_connection_status(false, "Desconectado — reconectando...")
				_reconnect_timer = RECONNECT_INTERVAL


func _handle_message(text: String) -> void:
	var json := JSON.new()
	var err := json.parse(text)
	if err != OK:
		return

	var data: Dictionary = json.get_data()
	if not data is Dictionary:
		return

	# Rota mensagens por tipo
	match data.get("type", ""):
		"state_update":
			_apply_state(data)
		"error_update":
			_apply_errors(data)
		"pong":
			pass  # keepalive
		_:
			if data.has("result"):
				pass  # resposta a request


func _request_state() -> void:
	_pending_request_id += 1
	var msg := {
		"jsonrpc": "2.0",
		"method": "get_state",
		"id": _pending_request_id,
		"params": {}
	}
	_send(msg)


func _send(msg: Dictionary) -> void:
	if _ws and _ws.get_ready_state() == WebSocketPeer.STATE_OPEN:
		_ws.send_text(JSON.stringify(msg))


# ── Aplicar estado ────────────────────────────────────────────────────────────

func _apply_state(data: Dictionary) -> void:
	project_name = data.get("project", project_name)
	current_phase = data.get("phase", current_phase)
	milestone_progress = data.get("progress", milestone_progress)
	next_step = data.get("next_step", next_step)
	traffic_light = clampi(data.get("traffic", traffic_light), 0, 2)
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
	_revert_label.text = "Voltar: " + last_snapshot


# ── UI: Atualização ───────────────────────────────────────────────────────────

func _refresh_ui() -> void:
	if not is_inside_tree():
		return

	_project_label.text = project_name if project_name else "—"
	_phase_label.text = current_phase if current_phase else "—"
	_progress_bar.value = milestone_progress
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


func _refresh_errors() -> void:
	# Limpa erros anteriores
	for child in _error_container.get_children():
		child.queue_free()

	if errors.is_empty():
		var noerr := Label.new()
		noerr.text = "Nenhum erro."
		noerr.add_theme_color_override("font_color", Color.DIM_GRAY)
		_error_container.add_child(noerr)
		return

	# Agrupa por causa
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

		# Ícone de erro
		var icon := Label.new()
		icon.text = "✗"
		icon.add_theme_color_override("font_color", Color.RED)
		hbox.add_child(icon)

		# Causa + contagem
		var label := Label.new()
		label.text = "%s (%d)" % [cause, group.size()]
		label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		hbox.add_child(label)

		# Botão "Consertar"
		var btn := Button.new()
		btn.text = "Consertar"
		btn.pressed.connect(_on_fix_pressed.bind(cause))
		hbox.add_child(btn)

		# Botão "Detalhes"
		var detail_btn := Button.new()
		detail_btn.text = "Detalhes"
		detail_btn.pressed.connect(_on_details_pressed.bind(group))
		hbox.add_child(detail_btn)

		_error_container.add_child(hbox)


func _update_connection_status(ok: bool, msg: String) -> void:
	if is_inside_tree() and _status_label:
		_status_label.text = msg
		if ok:
			_status_label.add_theme_color_override("font_color", Color.GREEN)
		else:
			_status_label.add_theme_color_override("font_color", Color.DARK_ORANGE)


# ── Sinais dos botões ─────────────────────────────────────────────────────────

func _connect_signals() -> void:
	_btn_run.pressed.connect(_on_run_pressed)
	_btn_test.pressed.connect(_on_test_pressed)
	_btn_approve.pressed.connect(_on_approve_pressed)
	_btn_revert.pressed.connect(_on_revert_pressed)


func _on_run_pressed() -> void:
	_send({"jsonrpc": "2.0", "method": "run_game", "id": _pending_request_id + 1, "params": {}})
	_pending_request_id += 1


func _on_test_pressed() -> void:
	_send({"jsonrpc": "2.0", "method": "run_tests", "id": _pending_request_id + 1, "params": {}})
	_pending_request_id += 1


func _on_approve_pressed() -> void:
	_send({"jsonrpc": "2.0", "method": "approve_milestone", "id": _pending_request_id + 1, "params": {}})
	_pending_request_id += 1


func _on_revert_pressed() -> void:
	_send({"jsonrpc": "2.0", "method": "revert", "id": _pending_request_id + 1, "params": {}})
	_pending_request_id += 1


func _on_fix_pressed(cause: String) -> void:
	_send({
		"jsonrpc": "2.0",
		"method": "fix_error",
		"id": _pending_request_id + 1,
		"params": {"cause": cause}
	})
	_pending_request_id += 1


func _on_details_pressed(error_group: Array) -> void:
	# Fecha popup anterior se existir (evita acumulo)
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
			text += "  Sugestão: %s\n" % d["suggestion"]
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
