@tool class_name RandomWalker extends Node
@export var grid_size: Vector2i = Vector2i(50,50): set(v)=grid_size=Vector2i(clampi(v.x,10,500),clampi(v.y,10,500))
@export var steps: int = 100: set(v)=steps=clampi(v,10,10000)
@export var seed_val: int = -1
signal generation_started(); signal step_placed(pos: Vector2i); signal generation_finished()
var _grid: Array[Array] = []; var _pos: Vector2i; var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func generate() -> Array[Vector2i]:
	if seed_val>=0: seed(seed_val)
	_grid.clear(); for y in grid_size.y: _grid.append([]); for _x in grid_size.x: _grid[y].append(0)
	_pos=Vector2i(grid_size.x/2,grid_size.y/2); var path: Array[Vector2i]=[_pos]; _grid[_pos.y][_pos.x]=1
	generation_started.emit()
	for _i in steps:
		var dirs:=[Vector2i(1,0),Vector2i(-1,0),Vector2i(0,1),Vector2i(0,-1)]; dirs.shuffle()
		var moved:=false
		for d in dirs:
			var n:=_pos+d
			if n.x>=0 and n.x<grid_size.x and n.y>=0 and n.y<grid_size.y and _grid[n.y][n.x]==0:
				_pos=n; _grid[n.y][n.x]=1; path.append(_pos); step_placed.emit(_pos); moved=true; break
		if not moved: break
	generation_finished.emit(); return path
func _get_configuration_warnings() -> PackedStringArray: return []
