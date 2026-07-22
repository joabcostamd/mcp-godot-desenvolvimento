## Control que exibe overlay de tutorial com passos destacados.
## Generos: generic.
## Tags: tutorial.
## Extends: Node.
## Sinais: step_completed(), tutorial_finished().
## Dependencias: nenhuma.
## @behavior: tutorial_overlay
@tool class_name TutorialOverlay extends Control
@export var steps: Array = []; @export var skip_enabled: bool = true
signal step_completed(index: int); signal tutorial_finished()
var _current: int = -1; var _active: bool = false
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func start() -> void: _current=0; _active=true
func next_step() -> void:
	if not _active: return
	step_completed.emit(_current); _current+=1
	if _current>=steps.size(): _active=false; tutorial_finished.emit()
func skip() -> void: if skip_enabled: _active=false; tutorial_finished.emit()
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if steps.is_empty(): w.append("steps vazio.")
	return w
