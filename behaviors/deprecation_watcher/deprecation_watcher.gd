## Behavior deprecation_watcher para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: deprecation_watcher
﻿@tool class_name DeprecationWatcher extends Node;signal deprecation_warning(method:String);var _init:=false;func _ready()->void:if _init:return;_init=true;func warn(method:String)->void:deprecation_warning.emit(method);func _get_configuration_warnings()->PackedStringArray:return[]
