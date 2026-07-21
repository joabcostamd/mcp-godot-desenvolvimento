@tool class_name Leaderboard extends Node
@export var max_entries: int = 10: set(v)=max_entries=clampi(v,3,100)
signal score_submitted(player_name: String, score: int, rank: int)
var _entries: Array = []
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func submit_score(player_name: String, score: int) -> int:
	_entries.append({"name":player_name,"score":score})
	_entries.sort_custom(func(a,b): return a.score>b.score)
	if _entries.size()>max_entries: _entries.resize(max_entries)
	var rank:=1
	for i in _entries.size():
		if _entries[i].name==player_name and _entries[i].score==score: rank=i+1; break
	score_submitted.emit(player_name,score,rank)
	return rank
func get_entries() -> Array: return _entries.duplicate()
func get_top(n: int=3) -> Array: return _entries.slice(0,mini(n,_entries.size()))
func clear() -> void: _entries.clear()
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]; return w
