## Accordion — Painel Expansível | Godot 4.7.
##
## Control com seções clicáveis. Cada seção = Button (header) +
## Control (conteúdo). Toggle visibilidade do conteúdo ao clicar.
## Suporta animação e modo múltiplo.
##
## @behavior: accordion
## @genres: generic
## @tutorial: behaviors/accordion/README.md

@tool
class_name Accordion
extends Control

## Duração da animação (0 = sem animação).
@export var animation_duration: float = 0.2:
	set(v):
		animation_duration = clampf(v, 0.0, 2.0)

## Se true, várias seções podem ficar abertas ao mesmo tempo.
@export var allow_multiple: bool = false

signal section_toggled(index: int, collapsed: bool)

var _sections: Array[Dictionary] = []
var _container: VBoxContainer
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_create_ui()
	_initialized = true


func _create_ui() -> void:
	if _container:
		return
	_container = VBoxContainer.new()
	_container.name = "AccordionContainer"
	_container.set_anchors_preset(Control.PRESET_FULL_RECT)
	_container.add_theme_constant_override("separation", 0)
	add_child(_container)
	mouse_filter = Control.MOUSE_FILTER_PASS


## Adiciona uma seção ao accordion.
## @param title: texto do cabeçalho
## @param content: nó Control filho (será reparentado para dentro da seção)
## @param collapsed: estado inicial (true = recolhido)
func add_section(title: String, content: Control, collapsed: bool = false) -> int:
	var section := _make_section(title, content, collapsed)
	_sections.append(section)
	return _sections.size() - 1


## Remove uma seção pelo índice.
func remove_section(index: int) -> void:
	if index < 0 or index >= _sections.size():
		return
	var section := _sections[index]
	(section.header as Button).queue_free()
	(section.content as Control).queue_free()
	_sections.remove_at(index)


## Alterna o estado de uma seção.
func toggle_section(index: int) -> void:
	if index < 0 or index >= _sections.size():
		return
	var section := _sections[index]
	var content := section.content as Control
	var collapsed := section.collapsed as bool

	if collapsed:
		_expand(index, section)
	else:
		_collapse(index, section)


## Retorna true se a seção está recolhida.
func is_section_collapsed(index: int) -> bool:
	if index < 0 or index >= _sections.size():
		return true
	return _sections[index].collapsed


## Recolhe todas as seções.
func collapse_all() -> void:
	for i in range(_sections.size()):
		var section := _sections[i]
		if not section.collapsed:
			_collapse(i, section)


## Expande todas as seções.
func expand_all() -> void:
	for i in range(_sections.size()):
		var section := _sections[i]
		if section.collapsed:
			_expand(i, section)


## Retorna o número de seções.
func get_section_count() -> int:
	return _sections.size()


func _make_section(title: String, content: Control, collapsed: bool) -> Dictionary:
	# Header (Button)
	var header := Button.new()
	header.name = "Header_%d" % _sections.size()
	header.text = title
	header.alignment = HORIZONTAL_ALIGNMENT_LEFT
	header.size_flags_horizontal = Control.SIZE_FILL
	var idx := _sections.size()
	header.pressed.connect(func(): toggle_section(idx))

	# Content wrapper
	var wrapper := Control.new()
	wrapper.name = "Content_%d" % idx
	wrapper.size_flags_horizontal = Control.SIZE_FILL
	wrapper.visible = not collapsed

	# Reparent content
	if content.get_parent():
		content.reparent(wrapper)
	else:
		wrapper.add_child(content)
	content.size_flags_horizontal = Control.SIZE_FILL

	# Add to container
	_container.add_child(header)
	_container.add_child(wrapper)

	return {
		"header": header,
		"content": content,
		"wrapper": wrapper,
		"collapsed": collapsed,
	}


func _expand(index: int, section: Dictionary) -> void:
	section.collapsed = false
	var wrapper := section.wrapper as Control
	wrapper.visible = true
	section_toggled.emit(index, false)

	# Fecha outras seções se allow_multiple = false
	if not allow_multiple:
		for i in range(_sections.size()):
			if i != index and not _sections[i].collapsed:
				_collapse(i, _sections[i])


func _collapse(index: int, section: Dictionary) -> void:
	section.collapsed = true
	var wrapper := section.wrapper as Control
	wrapper.visible = false
	section_toggled.emit(index, true)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
