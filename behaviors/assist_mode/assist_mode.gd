@tool class_name AssistMode extends Node
@export var enabled: bool = false
signal assist_activated()
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func enable() -> void: enabled=true; assist_activated.emit()
func disable() -> void: enabled=false
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not enabled: w.append("AssistMode desabilitado.")
	return w
