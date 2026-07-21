@tool class_name LavaSurface extends Node2D
@export var flow_speed: float = 0.5: set(v)=flow_speed=clampf(v,0.1,10.0)
@export var glow_intensity: float = 1.5: set(v)=glow_intensity=clampf(v,0.1,5.0)
@export var lava_color: Color = Color(1.0,0.3,0.0,1.0): set(v)=lava_color=v; _update_shader()
var _time: float = 0.0
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _update_shader(); _initialized=true
func _process(delta: float) -> void:
	_time+=delta*flow_speed
	var mat:=material as ShaderMaterial
	if mat: mat.set_shader_parameter("time",_time); mat.set_shader_parameter("intensity",glow_intensity)
func _update_shader() -> void:
	if material and material is ShaderMaterial: (material as ShaderMaterial).set_shader_parameter("color",lava_color)
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not material or not material is ShaderMaterial: w.append("Material ShaderMaterial não atribuído.")
	return w
