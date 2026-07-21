## Behavior migration_runner para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: migration_runner
﻿@tool class_name MigrationRunner extends Node;signal migration_started();signal migration_complete();var _init:=false;func _ready()->void:if _init:return;_init=true;func run()->void:migration_started.emit();migration_complete.emit();func _get_configuration_warnings()->PackedStringArray:return[]
