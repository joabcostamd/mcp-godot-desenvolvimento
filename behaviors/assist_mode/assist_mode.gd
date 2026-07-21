@tool class_name AssistMode extends Node
@export var enabled: bool = false
signal assist_activated()
func enable() -> void: enabled=true; assist_activated.emit()
func disable() -> void: enabled=false
func _ready() -> void: pass
