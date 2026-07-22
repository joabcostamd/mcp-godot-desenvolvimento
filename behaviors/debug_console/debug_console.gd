## Control que exibe um console de debug in-game.
## Generos: generic.
## Tags: debug, console.
## Extends: Control.
## Sinais: command_entered().
## Dependencias: nenhuma.
## @behavior: debug_console
@tool
class_name DebugConsole
extends Control
@export var max_lines: int = 200: set(v): max_lines=clampi(v,10,1000)
@export var auto_scroll: bool = true
@export var font_size: int = 12: set(v): font_size=clampi(v,8,24)
signal command_entered(command: String)
var _bg: ColorRect; var _log: RichTextLabel; var _input: LineEdit
var _commands: Dictionary = {}
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	_bg=ColorRect.new(); _bg.color=Color(0,0,0,0.7); _bg.set_anchors_preset(Control.PRESET_FULL_RECT); add_child(_bg)
	_log=RichTextLabel.new(); _log.bbcode_enabled=true; _log.set_anchors_preset(Control.PRESET_FULL_RECT)
	_log.size_flags_horizontal=Control.SIZE_FILL; _log.scroll_following=true; add_child(_log)
	_input=LineEdit.new(); _input.placeholder_text="> comando"; _input.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_input.text_submitted.connect(_on_command); add_child(_input)
	visible=false; mouse_filter=Control.MOUSE_FILTER_IGNORE; _initialized=true

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_accept") and Input.is_key_pressed(KEY_CTRL):
		visible=!visible; if visible: _input.grab_focus()

func _on_command(cmd: String) -> void:
	_input.clear(); add_line("[color=gray]> "+cmd+"[/color]")
	command_entered.emit(cmd)
	var parts=cmd.split(" ",false); var name=parts[0] if parts.size()>0 else ""
	if _commands.has(name): _commands[name].call(parts.slice(1)) if parts.size()>1 else _commands[name].call([])

func add_line(text: String) -> void:
	_log.append_text(text+"\n")
	while _log.get_line_count()>max_lines: _log.remove_line(0)

func register_command(name: String, callback: Callable) -> void: _commands[name]=callback

func clear() -> void: _log.clear()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
