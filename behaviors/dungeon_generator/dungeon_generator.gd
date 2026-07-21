@tool class_name DungeonGenerator extends Node
@export var room_count: int = 10: set(v)=room_count=clampi(v,2,100)
@export var min_size: Vector2i = Vector2i(6,6): set(v)=min_size=Vector2i(clampi(v.x,3,20),clampi(v.y,3,20))
@export var max_size: Vector2i = Vector2i(12,12): set(v)=max_size=Vector2i(clampi(v.x,4,30),clampi(v.y,4,30))
@export var seed_val: int = -1
signal generation_started(); signal room_placed(rect: Rect2i); signal corridors_done(); signal finished()
var _rooms: Array[Rect2i] = []; var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func generate() -> Array[Rect2i]:
	if seed_val>=0: seed(seed_val); _rooms.clear(); generation_started.emit()
	for _i in room_count:
		var w:=randi_range(min_size.x,max_size.x); var h:=randi_range(min_size.y,max_size.y)
		var x:=randi_range(0,200-w); var y:=randi_range(0,200-h)
		var r:=Rect2i(x,y,w,h); var ok:=true
		for existing in _rooms:
			if r.intersects(existing.grow(1)): ok=false; break
		if ok: _rooms.append(r); room_placed.emit(r)
	corridors_done.emit(); finished.emit(); return _rooms
func get_rooms() -> Array[Rect2i]: return _rooms.duplicate()
func _get_configuration_warnings() -> PackedStringArray: return []
