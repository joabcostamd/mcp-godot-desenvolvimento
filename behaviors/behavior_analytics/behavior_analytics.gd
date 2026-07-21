## Behavior behavior_analytics para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: behavior_analytics
﻿@tool class_name BehaviorAnalytics extends Node;signal event_tracked(name:String);var _init:=false;func _ready()->void:if _init:return;_init=true;func track(name:String)->void:event_tracked.emit(name);func _get_configuration_warnings()->PackedStringArray:return[]
