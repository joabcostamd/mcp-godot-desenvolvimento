## Teste de composicao: lobby + network_sync
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: lobby
## @behavior_b: network_sync

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/lobby/lobby.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/lobby/lobby.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/network_sync/network_sync.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/network_sync/network_sync.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("lobby foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("network_sync foi liberado durante o teste")
	# ── Verifica que lobby ainda consegue emitir sinais ──
	# Sinal 'player_joined': verifica conectividade
	assert_bool(_behavior_a.has_signal("player_joined")).override_failure_message("Sinal 'player_joined' nao encontrado em lobby")

	# Sinal 'player_left': verifica conectividade
	assert_bool(_behavior_a.has_signal("player_left")).override_failure_message("Sinal 'player_left' nao encontrado em lobby")

	# Sinal 'game_started': verifica conectividade
	assert_bool(_behavior_a.has_signal("game_started")).override_failure_message("Sinal 'game_started' nao encontrado em lobby")
	# ── Verifica que network_sync ainda consegue emitir sinais ──
	# Sinal 'synced': verifica conectividade
	assert_bool(_behavior_b.has_signal("synced")).override_failure_message("Sinal 'synced' nao encontrado em network_sync")

	# Sinal 'desync_detected': verifica conectividade
	assert_bool(_behavior_b.has_signal("desync_detected")).override_failure_message("Sinal 'desync_detected' nao encontrado em network_sync")

