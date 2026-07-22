## generate_icons.gd — MCP BT Editor | Gera icones coloridos por categoria.
##
## Execute no editor Godot: rode esta cena uma vez para gerar os icones
## em addons/mcp_bt_editor/icons/. Depois disso, o script pode ser removido.
##
## Uso: Abra esta cena no Godot, pressione F6 (run current scene).

@tool
extends Node

const ICON_SIZE: int = 16
const OUTPUT_DIR: String = "res://addons/mcp_bt_editor/icons"

var _category_colors: Dictionary = {
	"flow": Color(0.2, 0.5, 1.0),
	"condition": Color(0.9, 0.7, 0.1),
	"data": Color(0.3, 0.8, 0.3),
	"event": Color(0.95, 0.3, 0.1),
	"generic": Color(0.5, 0.5, 0.5),
	"vida_dano": Color(0.95, 0.2, 0.2),
	"movimento": Color(0.2, 0.5, 1.0),
	"ia": Color(0.9, 0.7, 0.1),
	"interface": Color(0.3, 0.8, 0.3),
	"audio": Color(0.8, 0.3, 0.8),
	"animacao": Color(0.95, 0.5, 0.1),
	"dados": Color(0.4, 0.4, 0.4),
}


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(OUTPUT_DIR)
	for cat_name: String in _category_colors.keys():
		_save_icon(cat_name, _category_colors[cat_name])
	print_rich("[b][BT Icons][/b] %d icones gerados em %s" % [_category_colors.size(), OUTPUT_DIR])
	get_tree().quit()


func _save_icon(name: String, color: Color) -> void:
	var img: Image = Image.create(ICON_SIZE, ICON_SIZE, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))

	var cx: float = float(ICON_SIZE) / 2.0 - 1.0
	var cy: float = float(ICON_SIZE) / 2.0 - 1.0
	var r: float = float(ICON_SIZE) / 2.0 - 3.0

	for x: int in range(ICON_SIZE):
		for y: int in range(ICON_SIZE):
			var dx: float = float(x) - cx
			var dy: float = float(y) - cy
			if dx * dx + dy * dy <= r * r:
				img.set_pixel(x, y, color)

	var path: String = OUTPUT_DIR + "/" + name + ".png"
	img.save_png(path)
