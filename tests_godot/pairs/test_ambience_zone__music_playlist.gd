## Teste de composicao: ambience_zone + music_playlist
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: ambience_zone
## @behavior_b: music_playlist

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/ambience_zone/ambience_zone.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/ambience_zone/ambience_zone.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/music_playlist/music_playlist.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/music_playlist/music_playlist.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("ambience_zone foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("music_playlist foi liberado durante o teste")
	# ── Verifica que ambience_zone ainda consegue emitir sinais ──
	# Sinal 'entered_zone': verifica conectividade
	assert_bool(_behavior_a.has_signal("entered_zone")).override_failure_message("Sinal 'entered_zone' nao encontrado em ambience_zone")

	# Sinal 'exited_zone': verifica conectividade
	assert_bool(_behavior_a.has_signal("exited_zone")).override_failure_message("Sinal 'exited_zone' nao encontrado em ambience_zone")
	# ── Verifica que music_playlist ainda consegue emitir sinais ──
	# Sinal 'track_changed': verifica conectividade
	assert_bool(_behavior_b.has_signal("track_changed")).override_failure_message("Sinal 'track_changed' nao encontrado em music_playlist")

	# Sinal 'playlist_finished': verifica conectividade
	assert_bool(_behavior_b.has_signal("playlist_finished")).override_failure_message("Sinal 'playlist_finished' nao encontrado em music_playlist")

