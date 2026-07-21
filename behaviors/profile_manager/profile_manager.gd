## Behavior profile_manager para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: profile_manager
@tool class_name ProfileManager extends Node
signal profile_switched(name:String);signal profile_saved(name:String)
var _init:=false
func _ready()->void:if _init:return;_init=true
func switch(n:String)->void:profile_switched.emit(n)
func save_profile(n:String)->void:profile_saved.emit(n)
func _get_configuration_warnings()->PackedStringArray:return[]