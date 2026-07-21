@tool class_name Card extends Node
@export var face_up: bool = true: set(v): face_up=v; flipped.emit(v)
signal played(); signal drawn(); signal flipped(face_up: bool)
var card_data: Dictionary = {}
func flip() -> void: face_up=!face_up
func play() -> void: played.emit()
func draw() -> void: drawn.emit()
