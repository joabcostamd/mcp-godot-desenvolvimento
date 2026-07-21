@tool class_name NoiseGenerator extends Node
@export var noise_type: String = "perlin": set(v)=noise_type=v
@export var frequency: float = 0.05: set(v)=frequency=clampf(v,0.001,1.0)
@export var amplitude: float = 1.0: set(v)=amplitude=clampf(v,0.1,10.0)
@export var octaves: int = 3: set(v)=octaves=clampi(v,1,8)
@export var seed_val: int = -1
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func get_noise_2d(x: float, y: float) -> float:
	var n:=FastNoiseLite.new(); n.seed=seed_val if seed_val>=0 else randi(); n.frequency=frequency; n.fractal_octaves=octaves
	return n.get_noise_2d(x,y)*amplitude
func generate_grid(w: int, h: int) -> Array[Array]:
	var grid:=[]; for y in h: var row:=[]; for x in w: row.append(get_noise_2d(float(x),float(y))); grid.append(row); return grid
func _get_configuration_warnings() -> PackedStringArray: return []
