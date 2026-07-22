## generate_icon.gd — MCP Addon | Gera icone 128x128 para AssetLib.
##
## Execute no editor Godot: abra esta cena, pressione F6.
## Gera addons/mcp_addon/icon.png (128x128, gradiente azul → roxo).

@tool
extends Node

const OUTPUT_PATH: String = "res://addons/mcp_addon/icon.png"
const SIZE: int = 128


func _ready() -> void:
	var img: Image = Image.create(SIZE, SIZE, false, Image.FORMAT_RGBA8)

	# Gradiente radial: azul escuro no centro → roxo nas bordas
	var cx: float = float(SIZE) / 2.0
	var cy: float = float(SIZE) / 2.0
	var max_r: float = float(SIZE) / 2.0

	var center_color: Color = Color(0.1, 0.3, 0.8)   # Azul
	var edge_color: Color = Color(0.4, 0.1, 0.7)      # Roxo

	for x: int in range(SIZE):
		for y: int in range(SIZE):
			var dx: float = float(x) - cx
			var dy: float = float(y) - cy
			var dist: float = sqrt(dx * dx + dy * dy) / max_r
			dist = clampf(dist, 0.0, 1.0)
			var pixel: Color = center_color.lerp(edge_color, dist)
			img.set_pixel(x, y, pixel)

	# Desenha "MCP" no centro (simplificado: retangulo branco)
	var text_x: int = SIZE / 2 - 30
	var text_y: int = SIZE / 2 - 20
	for x: int in range(text_x, text_x + 60):
		for y: int in range(text_y, text_y + 40):
			if x >= 0 and x < SIZE and y >= 0 and y < SIZE:
				var existing: Color = img.get_pixel(x, y)
				var white: Color = Color(1.0, 1.0, 1.0, 0.9)
				img.set_pixel(x, y, existing.lerp(white, 0.6))

	img.save_png(OUTPUT_PATH)
	print_rich("[b][MCP Icon][/b] Icone 128x128 gerado: %s" % OUTPUT_PATH)
	get_tree().quit()
