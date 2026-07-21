@tool class_name FarmingPlot extends Node2D
@export var growth_time: float = 30.0: set(v)=growth_time=clampf(v,1.0,600.0)
@export var stages: int = 3: set(v)=stages=clampi(v,1,5)
signal planted(); signal stage_changed(stage: int); signal ready(); signal harvested(item_id: String)
var _planted: bool = false; var _growth_elapsed: float = 0.0; var _current_stage: int = 0; var _crop_id: String = ""
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func _process(delta: float) -> void:
	if not _planted: return
	_growth_elapsed+=delta
	var new_stage:=mini(int(_growth_elapsed/(growth_time/stages)),stages)
	if new_stage!=_current_stage: _current_stage=new_stage; stage_changed.emit(_current_stage)
	if _current_stage>=stages: _planted=false; ready.emit()
func plant(crop_id: String) -> void: _crop_id=crop_id; _growth_elapsed=0.0; _current_stage=0; _planted=true; planted.emit()
func harvest() -> String:
	if _current_stage<stages: return ""
	var c:=_crop_id; _crop_id=""; _current_stage=0; harvested.emit(c); return c
func get_stage() -> int: return _current_stage
func is_planted() -> bool: return _planted or _current_stage>0
func _get_configuration_warnings() -> PackedStringArray: return []
