## Behavior world_map_generator para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: world_map_generator
@tool class_name WorldMapGenerator extends Node
@export var width: int = 100: set(v)=width=clampi(v,20,500)
@export var height: int = 100: set(v)=height=clampi(v,20,500)
@export var seed_val: int = -1
signal biome_generated(biome: String, region: Rect2i); signal map_finished()
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func generate() -> Dictionary:
	if seed_val>=0: seed(seed_val)
	var noise:=FastNoiseLite.new(); noise.seed=seed_val if seed_val>=0 else randi(); noise.frequency=0.02
	var biomes:={}; var region:=Rect2i(0,0,width/3,height/3)
	biomes["forest"]=region; biome_generated.emit("forest",region)
	region=Rect2i(width/3,0,width/3,height/3); biomes["desert"]=region; biome_generated.emit("desert",region)
	region=Rect2i(2*width/3,0,width/3,height/3); biomes["mountains"]=region; biome_generated.emit("mountains",region)
	map_finished.emit(); return biomes
func _get_configuration_warnings() -> PackedStringArray: return []
