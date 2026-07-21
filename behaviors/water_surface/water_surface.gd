@tool class_name WaterSurface extends Node2D
@export var wave_speed: float = 1.0: set(v)=wave_speed=clampf(v,0.1,10.0)
@export var wave_amplitude: float = 5.0: set(v)=wave_amplitude=clampf(v,0.5,20.0)
@export var water_color: Color = Color(0.1,0.3,0.8,0.7): set(v)=water_color=v; _update_shader()
var _time: float = 0.0
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return
	_update_shader(); _initialized=true
func _process(delta: float) -> void:
	_time+=delta*wave_speed
	var mat:=material as ShaderMaterial
	if mat: mat.set_shader_parameter("time",_time); mat.set_shader_parameter("amplitude",wave_amplitude)
	if get_child_count()>0 and get_child(0) is ColorRect:
		var cr:=get_child(0) as ColorRect; cr.material=material
func _update_shader() -> void:
	if material and material is ShaderMaterial: (material as ShaderMaterial).set_shader_parameter("color",water_color)
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not material or not material is ShaderMaterial: w.append("Material ShaderMaterial não atribuído.")
	return w
