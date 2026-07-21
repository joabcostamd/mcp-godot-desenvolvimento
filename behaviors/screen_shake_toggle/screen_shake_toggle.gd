@tool class_name ScreenShakeToggle extends Node
@export var enabled: bool = true
signal toggled()
func toggle() -> void: enabled=!enabled; toggled.emit()
func _ready() -> void: pass
