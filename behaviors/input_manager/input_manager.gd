## InputManager — Gerenciador de Input com Rebinding | Godot 4.7.
##
## Node que gerencia rebinding de input em runtime. Permite
## reassociar teclas/botões a ações do InputMap, detecta tipo
## de dispositivo e salva/carrega bindings via ConfigFile.
##
## @behavior: input_manager
## @genres: platformer, topdown_shooter, rpg, generic
## @tutorial: behaviors/input_manager/README.md

@tool
class_name InputManager
extends Node

## Caminho para salvar/carregar bindings.
@export var bindings_path: String = "user://input_bindings.cfg":
	set(v):
		var clean := v.strip_edges()
		bindings_path = clean if not clean.is_empty() else "user://input_bindings.cfg"

signal device_changed(device_type: String)
signal action_rebound(action_name: String, event: InputEvent)

var _device_type: String = "keyboard"
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_initialized = true


func _input(event: InputEvent) -> void:
	var new_type := _detect_device(event)
	if new_type != _device_type:
		_device_type = new_type
		device_changed.emit(_device_type)


# ---------------------------------------------------------------------------
# REBINDING
# ---------------------------------------------------------------------------

## Reassocia uma ação do InputMap a um novo evento.
## Remove bindings anteriores da ação e adiciona o novo.
## Retorna true se a ação existe no InputMap.
func rebind_action(action_name: String, event: InputEvent) -> bool:
	if not event:
		return false
	if not InputMap.has_action(action_name):
		return false

	# Remove todos os eventos existentes desta ação
	var existing := InputMap.action_get_events(action_name)
	for e in existing:
		# Só remove eventos do mesmo tipo (key para key, button para button)
		if e.get_class() == event.get_class():
			InputMap.action_erase_event(action_name, e)

	# Adiciona o novo evento
	InputMap.action_add_event(action_name, event)
	action_rebound.emit(action_name, event)
	return true


## Reseta uma ação para o estado padrão (remove todos os eventos customizados).
func reset_action(action_name: String) -> void:
	if not InputMap.has_action(action_name):
		return
	var events := InputMap.action_get_events(action_name)
	for e in events:
		InputMap.action_erase_event(action_name, e)


## Reseta todas as ações do InputMap.
func reset_all() -> void:
	var actions := InputMap.get_actions()
	for action_name in actions:
		reset_action(action_name)


## Retorna os eventos associados a uma ação.
func get_action_events(action_name: String) -> Array:
	if not InputMap.has_action(action_name):
		return []
	return InputMap.action_get_events(action_name)


# ---------------------------------------------------------------------------
# DEVICE DETECTION
# ---------------------------------------------------------------------------

## Retorna o tipo de dispositivo atual: "keyboard", "gamepad" ou "touch".
func get_device_type() -> String:
	return _device_type


func _detect_device(event: InputEvent) -> String:
	if event is InputEventKey or event is InputEventMouse:
		return "keyboard"
	if event is InputEventJoypadButton or event is InputEventJoypadMotion:
		return "gamepad"
	if event is InputEventScreenTouch or event is InputEventScreenDrag:
		return "touch"
	return _device_type


# ---------------------------------------------------------------------------
# PERSISTENCE
# ---------------------------------------------------------------------------

## Salva os bindings atuais em ConfigFile.
func save_bindings() -> bool:
	var config := ConfigFile.new()
	var actions := InputMap.get_actions()
	for action_name in actions:
		var events := InputMap.action_get_events(action_name)
		var serialized: Array = []
		for e in events:
			serialized.append(_serialize_event(e))
		config.set_value("bindings", action_name, serialized)

	var err := config.save(bindings_path)
	return err == OK


## Carrega bindings de um ConfigFile e aplica ao InputMap.
func load_bindings() -> bool:
	if not FileAccess.file_exists(bindings_path):
		return false

	var config := ConfigFile.new()
	var err := config.load(bindings_path)
	if err != OK:
		return false

	for action_name in config.get_section_keys("bindings"):
		if not InputMap.has_action(action_name):
			continue
		reset_action(action_name)
		var serialized: Array = config.get_value("bindings", action_name, [])
		for entry in serialized:
			var event := _deserialize_event(entry as Dictionary)
			if event:
				InputMap.action_add_event(action_name, event)

	return true


# ---------------------------------------------------------------------------
# SERIALIZATION HELPERS
# ---------------------------------------------------------------------------

func _serialize_event(event: InputEvent) -> Dictionary:
	var data := {"type": event.get_class()}
	if event is InputEventKey:
		var ke := event as InputEventKey
		data["keycode"] = ke.keycode
	elif event is InputEventJoypadButton:
		var jb := event as InputEventJoypadButton
		data["button_index"] = jb.button_index
	elif event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		data["button_index"] = mb.button_index
	return data


func _deserialize_event(data: Dictionary) -> InputEvent:
	var event_type: String = data.get("type", "")
	match event_type:
		"InputEventKey":
			var ke := InputEventKey.new()
			ke.keycode = data.get("keycode", KEY_NONE)
			return ke
		"InputEventJoypadButton":
			var jb := InputEventJoypadButton.new()
			jb.button_index = data.get("button_index", JOY_BUTTON_INVALID)
			return jb
		"InputEventMouseButton":
			var mb := InputEventMouseButton.new()
			mb.button_index = data.get("button_index", MOUSE_BUTTON_NONE)
			return mb
	return null


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	var actions := InputMap.get_actions()
	if actions.is_empty():
		w.append("Nenhuma ação registrada no InputMap — verifique as configurações de input do projeto.")
	return w
