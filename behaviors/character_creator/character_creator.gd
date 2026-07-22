## CharacterCreator — Criador de Personagem Customizável | Godot 4.7.
##
## Control que gerencia partes customizáveis (cabelo, olhos, corpo, etc.)
## com opções por parte e paleta de cores. Suporta presets salvos via
## ConfigFile. Integra com SaveLoad sibling para diretório de saves.
## Ideal para telas de criação de personagem em RPGs.
##
## @behavior: character_creator
## @genres: rpg, roguelike, generic
## @tutorial: behaviors/character_creator/README.md

@tool
class_name CharacterCreator
extends Control

## Categoria para agrupar presets (ex: "player", "npc", "enemy").
@export var preset_category: String = "default":
	set(v):
		var clean := v.strip_edges()
		if clean.is_empty():
			clean = "default"
		preset_category = clean

## Paleta de cores disponíveis para customização de partes.
@export var color_palette: PackedColorArray = [
	Color.WHITE, Color.BLACK, Color.RED, Color.BLUE,
	Color.GREEN, Color.YELLOW, Color.MAGENTA, Color.ORANGE
]:
	set(v):
		color_palette = v
		if color_palette.is_empty():
			color_palette = PackedColorArray([Color.WHITE])

signal part_changed(part_name: String)
signal saved(preset_name: String)
signal loaded(preset_name: String)

var _parts: Dictionary = {}        # part_name -> {options, current, color}
var _save_load: SaveLoad = null
var _initialized: bool = false

const _PRESET_BASE_DIR := "user://character_presets/"


func _ready() -> void:
	if _initialized:
		return
	_find_save_load()
	_initialized = true


func _find_save_load() -> void:
	var parent := get_parent()
	if not parent:
		return
	for child in parent.get_children():
		if child is SaveLoad and not _save_load:
			_save_load = child as SaveLoad
			return


# ---------------------------------------------------------------------------
# PART MANAGEMENT
# ---------------------------------------------------------------------------

## Adiciona uma parte customizável.
## @param part_name: Nome único da parte (ex: "hair", "eyes", "body").
## @param options: Lista de opções disponíveis (ex: ["hair_01", "hair_02"]).
## Retorna true se adicionada com sucesso.
func add_part(part_name: String, options: Array[String]) -> bool:
	if part_name.is_empty():
		push_warning("CharacterCreator: part_name vazio ignorado.")
		return false
	if _parts.has(part_name):
		push_warning("CharacterCreator: parte '%s' já existe, use remove_part() primeiro." % part_name)
		return false

	var opt: Array[String] = []
	opt.assign(options)

	_parts[part_name] = {
		"options": opt,
		"current": 0 if not opt.is_empty() else -1,
		"color": color_palette[0] if not color_palette.is_empty() else Color.WHITE
	}
	return true


## Remove uma parte.
func remove_part(part_name: String) -> bool:
	if not _parts.has(part_name):
		return false
	_parts.erase(part_name)
	return true


## Define a opção selecionada de uma parte (índice no array de options).
func set_part_option(part_name: String, option_index: int) -> void:
	var part: Dictionary = _get_part(part_name)
	if part.is_empty():
		return

	var options: Array = part["options"]
	if options.is_empty():
		part["current"] = -1
		return

	var clamped := clampi(option_index, 0, options.size() - 1)
	if part["current"] == clamped:
		return  # PADRÃO 10: no-op guard

	part["current"] = clamped
	part_changed.emit(part_name)


## Define a cor de uma parte.
func set_part_color(part_name: String, color: Color) -> void:
	var part: Dictionary = _get_part(part_name)
	if part.is_empty():
		return

	if part["color"] == color:
		return  # PADRÃO 10: no-op guard

	part["color"] = color
	part_changed.emit(part_name)


## Retorna o índice da opção selecionada (-1 se sem opções ou parte não existe).
func get_part_option(part_name: String) -> int:
	var part: Dictionary = _get_part(part_name)
	if part.is_empty():
		return -1
	return part["current"]


## Retorna a cor atual da parte (Color.WHITE se parte não existe).
func get_part_color(part_name: String) -> Color:
	var part: Dictionary = _get_part(part_name)
	if part.is_empty():
		return Color.WHITE
	return part["color"]


## Retorna a lista de opções disponíveis para uma parte.
func get_part_options(part_name: String) -> Array[String]:
	var part: Dictionary = _get_part(part_name)
	if part.is_empty():
		return []
	var options: Array = part["options"]
	return options.duplicate()


## Retorna os nomes de todas as partes registradas.
func get_part_names() -> Array[String]:
	var names: Array[String] = []
	for key in _parts.keys():
		names.append(key)
	return names


# ---------------------------------------------------------------------------
# CHARACTER DATA IMPORT/EXPORT
# ---------------------------------------------------------------------------

## Retorna os dados completos do personagem como Dictionary serializável.
## Formato: {part_name: {option: int, color: {r,g,b,a}}}
func get_character_data() -> Dictionary:
	var data := {}
	for part_name in _parts.keys():
		var part: Dictionary = _parts[part_name]
		var c: Color = part["color"]
		data[part_name] = {
			"option": part["current"],
			"color": {"r": c.r, "g": c.g, "b": c.b, "a": c.a}
		}
	return data


## Carrega dados do personagem a partir de um Dictionary.
## Apenas partes que já existem no _parts são atualizadas.
## Retorna true se pelo menos uma parte foi atualizada.
func load_character_data(data: Dictionary) -> bool:
	if data.is_empty():
		return false

	var updated := false
	for part_name in data.keys():
		if not _parts.has(part_name):
			continue  # ignora partes desconhecidas silenciosamente

		var part_data = data[part_name]
		if not part_data is Dictionary:
			continue

		# Restaura opção
		if part_data.has("option"):
			var opt_idx: int = part_data["option"]
			var part: Dictionary = _parts[part_name]
			var options: Array = part["options"]
			if not options.is_empty():
				part["current"] = clampi(opt_idx, 0, options.size() - 1)
				updated = true

		# Restaura cor
		if part_data.has("color") and part_data["color"] is Dictionary:
			var cd: Dictionary = part_data["color"] as Dictionary
			if cd.has_all(["r", "g", "b", "a"]):
				var c: Color = Color(cd["r"], cd["g"], cd["b"], cd["a"])
				_parts[part_name]["color"] = c
				updated = true

	return updated


# ---------------------------------------------------------------------------
# PRESET MANAGEMENT
# ---------------------------------------------------------------------------

## Salva o personagem atual como preset.
func save_preset(preset_name: String) -> bool:
	if preset_name.is_empty():
		return false

	if not _ensure_preset_dir():
		push_warning("CharacterCreator: não foi possível criar diretório de presets.")
		return false

	var config := ConfigFile.new()
	var data := get_character_data()
	config.set_value("preset", "category", preset_category)
	config.set_value("preset", "parts", data)
	config.set_value("preset", "part_names", get_part_names())

	var path := _preset_path(preset_name)
	var err := config.save(path)
	if err != OK:
		push_warning("CharacterCreator: erro ao salvar preset '%s' (err=%d)." % [preset_name, err])
		return false

	saved.emit(preset_name)
	return true


## Carrega um preset, restaurando todas as partes.
## Partes que não existem no preset atual são ignoradas.
## Retorna true se carregado com sucesso.
func load_preset(preset_name: String) -> bool:
	if preset_name.is_empty():
		return false

	var path := _preset_path(preset_name)
	if not FileAccess.file_exists(path):
		return false

	var config := ConfigFile.new()
	var err := config.load(path)
	if err != OK:
		push_warning("CharacterCreator: erro ao carregar preset '%s' (err=%d)." % [preset_name, err])
		return false

	if not config.has_section_key("preset", "parts"):
		return false

	var data: Dictionary = config.get_value("preset", "parts", {})
	if not load_character_data(data):
		return false

	loaded.emit(preset_name)
	return true


## Deleta um preset.
func delete_preset(preset_name: String) -> bool:
	if preset_name.is_empty():
		return false
	var path := _preset_path(preset_name)
	if not FileAccess.file_exists(path):
		return false
	var err := DirAccess.remove_absolute(path)
	return err == OK


## Retorna a lista de nomes de presets disponíveis.
func get_preset_names() -> Array[String]:
	var names: Array[String] = []
	var dir := DirAccess.open(_preset_dir())
	if not dir:
		return names
	dir.list_dir_begin()
	var file_name := dir.get_next()
	while not file_name.is_empty():
		if file_name.ends_with(".cfg"):
			names.append(file_name.trim_suffix(".cfg"))
		file_name = dir.get_next()
	dir.list_dir_end()
	return names


# ---------------------------------------------------------------------------
# UTILITY
# ---------------------------------------------------------------------------

## Aleatoriza todas as partes (opção e cor).
func randomize_character() -> void:
	if _parts.is_empty():
		return

	for part_name in _parts.keys():
		var part: Dictionary = _parts[part_name]
		var options: Array = part["options"]
		if not options.is_empty():
			part["current"] = randi() % options.size()

		if not color_palette.is_empty():
			part["color"] = color_palette[randi() % color_palette.size()]

		part_changed.emit(part_name)


## Reseta todas as partes para a primeira opção e primeira cor da paleta.
func reset_to_defaults() -> void:
	if _parts.is_empty():
		return

	var default_color := color_palette[0] if not color_palette.is_empty() else Color.WHITE

	for part_name in _parts.keys():
		var part: Dictionary = _parts[part_name]
		var options: Array = part["options"]
		part["current"] = 0 if not options.is_empty() else -1
		part["color"] = default_color
		part_changed.emit(part_name)


# ---------------------------------------------------------------------------
# INTERNAL
# ---------------------------------------------------------------------------

func _get_part(part_name: String) -> Dictionary:
	if not _parts.has(part_name):
		return {}
	return _parts[part_name]


func _preset_dir() -> String:
	if _save_load:
		return _save_load.save_dir.path_join("character_presets").path_join(preset_category)
	return _PRESET_BASE_DIR.path_join(preset_category)


func _preset_path(preset_name: String) -> String:
	return _preset_dir().path_join(preset_name + ".cfg")


func _ensure_preset_dir() -> bool:
	var dir_path := _preset_dir()
	var dir := DirAccess.open("user://")
	if not dir:
		return false
	if not dir.dir_exists(dir_path.trim_prefix("user://")):
		var err := dir.make_dir_recursive(dir_path.trim_prefix("user://"))
		return err == OK
	return true


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if _parts.is_empty():
		w.append("Nenhuma parte configurada — use add_part() para registrar partes customizáveis.")
	if color_palette.is_empty():
		w.append("Paleta de cores vazia — as partes usarão Color.WHITE como fallback.")
	return w
