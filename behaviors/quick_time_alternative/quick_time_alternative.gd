@tool class_name QuickTimeAlternative extends Node
signal qte_skipped();signal alternative_used()
var _init:=false
func _ready()->void:if _init:return;_init=true
func skip()->void:qte_skipped.emit()
func use_alternative()->void:alternative_used.emit()
func _get_configuration_warnings()->PackedStringArray:return[]