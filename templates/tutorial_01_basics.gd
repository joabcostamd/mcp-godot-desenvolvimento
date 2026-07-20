## Tutorial 01 — Seu Primeiro Nó | Godot 4.7.
##
## Tutorial passo 1: criar um nó, movê-lo com input, e ver na tela.
## Para iniciantes absolutos que nunca usaram Godot.
##
## @tutorial: templates/tutorial_01_basics.gd
## @difficulty: iniciante
## @duration: 5 minutos

class_name Tutorial01Basics
extends Node2D

## Velocidade de movimento do personagem de tutorial.
@export var speed: float = 200.0

var _sprite: Sprite2D
var _label: Label
var _step: int = 0


func _ready() -> void:
	# Cria um sprite simples (quadrado colorido) para o tutorial
	_sprite = Sprite2D.new()
	_sprite.texture = _make_square_texture(Color.DODGER_BLUE, Vector2(32, 32))
	_sprite.position = Vector2(200, 150)
	add_child(_sprite)

	# Label de instrução
	_label = Label.new()
	_label.position = Vector2(20, 20)
	_label.add_theme_font_size_override("font_size", 14)
	add_child(_label)

	_show_message("Use as SETAS ← → ↑ ↓ para mover o quadrado azul!")


func _process(delta: float) -> void:
	# Movimento do sprite pelo teclado
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if direction != Vector2.ZERO:
		_sprite.position += direction * speed * delta
		if _step == 0:
			_step = 1
			_show_message("Muito bem! Você moveu o nó. Este é o conceito mais básico do Godot: todo objeto na tela é um 'nó' (Node).")


func _show_message(text: String) -> void:
	_label.text = text
	# Cria um tween para fade out apos 8 segundos
	var tween := create_tween()
	tween.tween_interval(8.0)
	tween.tween_property(_label, "modulate:a", 0.0, 2.0)


func _make_square_texture(color: Color, size: Vector2) -> Texture2D:
	var image := Image.create(size.x as int, size.y as int, false, Image.FORMAT_RGBA8)
	image.fill(color)
	return ImageTexture.create_from_image(image)
