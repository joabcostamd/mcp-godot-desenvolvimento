@tool class_name ControllerRemap extends Control
@export var actions: Array = []
signal rebound(action: String)
func rebind(action: String, event: InputEvent) -> void:
	if not InputMap.has_action(action): return
	InputMap.action_add_event(action,event); rebound.emit(action)
