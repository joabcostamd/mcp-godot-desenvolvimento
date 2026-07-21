## Behavior Encrypted Save para Godot 4.
## Generos: generic.
## Tags: save.
## Extends: Node.
## Sinais: encrypted(), decrypted().
## Dependencias: nenhuma.
## @behavior: encrypted_save
@tool class_name EncryptedSave extends Node
@export var encryption_key: String = ""
signal encrypted(); signal decrypted()
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func save_encrypted(path: String, data: Dictionary) -> bool:
	var config:=ConfigFile.new()
	for k in data: config.set_value("data",k,data[k])
	if not encryption_key.is_empty(): config.save_encrypted(path,encryption_key)
	else: config.save(path)
	encrypted.emit(); return true
func load_encrypted(path: String) -> Dictionary:
	if not FileAccess.file_exists(path): return {}
	var config:=ConfigFile.new()
	if not encryption_key.is_empty(): config.load_encrypted(path,encryption_key)
	else: config.load(path)
	decrypted.emit(); return config.get_value("data","",{})
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if encryption_key.is_empty(): w.append("encryption_key vazio — salvando sem criptografia.")
	return w
