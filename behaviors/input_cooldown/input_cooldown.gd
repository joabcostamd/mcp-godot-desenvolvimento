@tool class_name InputCooldown extends Node
signal cooldown_active();signal cooldown_ready()
var _init:=false
func _ready()->void:if _init:return;_init=true
func start_cooldown()->void:cooldown_active.emit()
func end_cooldown()->void:cooldown_ready.emit()
func _get_configuration_warnings()->PackedStringArray:return[]