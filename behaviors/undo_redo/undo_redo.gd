@tool class_name UndoRedo extends Node
signal undone();signal redone();signal history_cleared()
var _init:=false
func _ready()->void:if _init:return;_init=true
func undo()->void:undone.emit()
func redo()->void:redone.emit()
func clear_history()->void:history_cleared.emit()
func _get_configuration_warnings()->PackedStringArray:return[]