@tool
class_name Storage
extends Node
@export var file_path: String = "user://storage.cfg"
@export var auto_save: bool = true
@export var section: String = "data"
signal data_changed(key: String)
signal loaded()
var _config: ConfigFile
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	_config = ConfigFile.new(); load_data(); _initialized = true

func load_data() -> void:
	if _config.load(file_path) == OK: loaded.emit()

func save_data() -> void: _config.save(file_path)

func set_data(key: String, value) -> void:
	_config.set_value(section, key, value)
	data_changed.emit(key)
	if auto_save: save_data()

func get_data(key: String, default = null):
	return _config.get_value(section, key, default)

func has_key(key: String) -> bool: return _config.has_section_key(section, key)
func erase_key(key: String) -> void: _config.erase_section_key(section, key); if auto_save: save_data()
func clear_all() -> void: _config.erase_section(section); if auto_save: save_data()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if file_path.is_empty():
		w.append("file_path is empty — data will not be persisted.")
	return w
