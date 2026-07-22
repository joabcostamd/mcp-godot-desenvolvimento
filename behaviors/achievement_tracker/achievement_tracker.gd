## Node que rastreia conquistas com progresso e flags secretas.
## Generos: generic.
## Tags: achievement, social.
## Extends: Node.
## Sinais: unlocked(), progress_updated().
## Dependencias: achievement.
## @behavior: achievement_tracker
@tool class_name AchievementTracker extends Node
@export var achievements: Array = []
signal unlocked(achievement_id: String)
signal progress_updated(achievement_id: String, progress: float)
var _progress: Dictionary = {}
var _unlocked: Dictionary = {}
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func update_progress(achievement_id: String, value: float) -> void:
	var ach:=_find_achievement(achievement_id)
	if ach.is_empty(): return
	if _unlocked.get(achievement_id,false): return
	var target:=ach.get("target",1.0) as float
	var prog:=minf(value/target,1.0)
	_progress[achievement_id]=prog
	progress_updated.emit(achievement_id,prog)
	if prog>=1.0: _unlocked[achievement_id]=true; unlocked.emit(achievement_id)
func get_progress(achievement_id: String) -> float: return _progress.get(achievement_id,0.0)
func is_unlocked(achievement_id: String) -> bool: return _unlocked.get(achievement_id,false)
func _find_achievement(id: String) -> Dictionary:
	for a in achievements:
		var d:=a as Dictionary
		if d.get("id","")==id: return d
	return {}
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if achievements.is_empty(): w.append("achievements vazio.")
	return w
