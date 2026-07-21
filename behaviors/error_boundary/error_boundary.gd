## Behavior error_boundary para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: error_boundary
﻿@tool class_name ErrorBoundary extends Node;signal error_caught(msg:String);var _init:=false;func _ready()->void:if _init:return;_init=true;func catch(msg:String)->void:error_caught.emit(msg);func _get_configuration_warnings()->PackedStringArray:return[]
