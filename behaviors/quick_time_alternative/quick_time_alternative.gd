## Behavior quick_time_alternative para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: quick_time_alternative
@tool class_name QuickTimeAlternative extends Node
signal qte_skipped();signal alternative_used()
var _init:=false
func _ready()->void:if _init:return;_init=true
func skip()->void:qte_skipped.emit()
func use_alternative()->void:alternative_used.emit()
func _get_configuration_warnings()->PackedStringArray:return[]