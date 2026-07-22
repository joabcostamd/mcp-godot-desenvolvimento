## Behavior screenreader_support para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: screenreader_support
@tool class_name ScreenreaderSupport extends Node
signal text_spoken(text:String)
var _init:=false
func _ready()->void:if _init:return;_init=true
func speak(t:String)->void:text_spoken.emit(t)
func _get_configuration_warnings()->PackedStringArray:return[]