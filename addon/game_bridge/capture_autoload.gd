extends Node
## capture_autoload.gd — Autoload de captura de screenshot
##
## Script temporário injetado como autoload pelo MCP server.
## Configuração via variáveis de ambiente/project settings:
##   mcp/capture/output_path  — onde salvar o PNG (default: user://capture.png)
##   mcp/capture/wait_frames  — quantos frames esperar antes de capturar (default: 30)
##   mcp/capture/auto_quit    — se true, encerra o jogo após capturar (default: true)
##
## Uso pelo MCP:
##   1. Python copia este script para o projeto
##   2. Python adiciona autoload em project.godot
##   3. Python roda Godot com --position -9999,-9999
##   4. Este script captura screenshot após N frames e salva PNG
##   5. Se auto_quit, encerra o jogo
##   6. Python lê o PNG e retorna base64

var _frames_waited: int = 0
var _target_frames: int = 30
var _output_path: String = "user://mcp_capture.png"
var _auto_quit: bool = true
var _resolution_override: Vector2i = Vector2i(1280, 720)


func _ready() -> void:
	# ── Lê configuração de ProjectSettings ──────────────────────
	if ProjectSettings.has_setting("mcp/capture/output_path"):
		_output_path = ProjectSettings.get_setting("mcp/capture/output_path")
	if ProjectSettings.has_setting("mcp/capture/wait_frames"):
		_target_frames = ProjectSettings.get_setting("mcp/capture/wait_frames")
	if ProjectSettings.has_setting("mcp/capture/auto_quit"):
		_auto_quit = ProjectSettings.get_setting("mcp/capture/auto_quit")
	if ProjectSettings.has_setting("mcp/capture/resolution_width"):
		_resolution_override.x = ProjectSettings.get_setting("mcp/capture/resolution_width")
	if ProjectSettings.has_setting("mcp/capture/resolution_height"):
		_resolution_override.y = ProjectSettings.get_setting("mcp/capture/resolution_height")

	# ── Força resolução se configurada ──────────────────────────
	if _resolution_override.x > 0 and _resolution_override.y > 0:
		var window := get_viewport()
		if window:
			window.size = _resolution_override

	print("[MCP Capture] Aguardando ", _target_frames, " frames...")


func _process(_delta: float) -> void:
	_frames_waited += 1
	if _frames_waited >= _target_frames:
		_capture_and_quit()


func _capture_and_quit() -> void:
	# ── Captura viewport ────────────────────────────────────────
	var viewport := get_viewport()
	if not viewport:
		print("[MCP Capture] ERRO: viewport não disponível.")
		if _auto_quit:
			get_tree().quit()
		return

	var texture := viewport.get_texture()
	if not texture:
		print("[MCP Capture] ERRO: textura do viewport não disponível.")
		if _auto_quit:
			get_tree().quit()
		return

	var img := texture.get_image()
	if not img:
		print("[MCP Capture] ERRO: imagem não pôde ser capturada.")
		if _auto_quit:
			get_tree().quit()
		return

	# ── Converte para RGBA8 se necessário ───────────────────────
	if img.get_format() != Image.FORMAT_RGBA8:
		img.convert(Image.FORMAT_RGBA8)

	# ── Resolve path ────────────────────────────────────────────
	var save_path: String = _output_path
	if save_path.begins_with("user://"):
		save_path = OS.get_user_data_dir() + "/" + save_path.trim_prefix("user://")
	elif save_path.begins_with("res://"):
		save_path = ProjectSettings.globalize_path(save_path)

	# ── Garante diretório ───────────────────────────────────────
	var dir := save_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(dir):
		DirAccess.make_dir_recursive_absolute(dir)

	# ── Salva PNG ───────────────────────────────────────────────
	var err := img.save_png(save_path)
	if err != OK:
		print("[MCP Capture] ERRO ao salvar PNG: ", err)
	else:
		print("[MCP Capture] Screenshot salva: ", save_path)

	if _auto_quit:
		get_tree().quit()
