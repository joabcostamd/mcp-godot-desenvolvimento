@tool class_name DailyReward extends Node
@export var rewards: Array = []
@export var streak_bonus_multiplier: float = 1.5: set(v)=streak_bonus_multiplier=clampf(v,1.0,5.0)
signal claimed(day: int, item_id: String)
signal streak_updated(streak: int)
var _streak: int = 0
var _last_claim_date: String = ""
var _claimed_today: bool = false
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func can_claim() -> bool:
	if _claimed_today: return false
	var today:=_today_str()
	if _last_claim_date==today: return false
	return true
func claim() -> Dictionary:
	if not can_claim(): return {}
	var today:=_today_str()
	if _last_claim_date==_yesterday_str(): _streak+=1
	else: _streak=1
	_last_claim_date=today; _claimed_today=true
	var idx:=mini(_streak-1,rewards.size()-1)
	if idx<0 or idx>=rewards.size(): return {}
	var entry: Dictionary=rewards[idx] as Dictionary
	var id:=entry.get("id","") as String
	var qty:=entry.get("quantity",1) as int
	if _streak>=7: qty=int(qty*streak_bonus_multiplier)
	claimed.emit(_streak,id); streak_updated.emit(_streak)
	return {"day":_streak,"item_id":id,"quantity":qty}
func get_streak() -> int: return _streak
func reset_streak() -> void: _streak=0; streak_updated.emit(0)
func _today_str() -> String: return Time.get_date_string_from_system()
func _yesterday_str() -> String: return Time.get_date_string_from_system()
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if rewards.is_empty(): w.append("rewards vazio.")
	return w
