## Teste de composicao: dead_zone_config + tween_player
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: dead_zone_config
## @behavior_b: tween_player

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/dead_zone_config/dead_zone_config.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/dead_zone_config/dead_zone_config.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/tween_player/tween_player.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/tween_player/tween_player.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("dead_zone_config foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("tween_player foi liberado durante o teste")
	# ── Verifica que dead_zone_config ainda consegue emitir sinais ──
	# Sinal 'zone_calibrated': verifica conectividade
	assert_bool(_behavior_a.has_signal("zone_calibrated")).override_failure_message("Sinal 'zone_calibrated' nao encontrado em dead_zone_config")
	# ── Verifica que tween_player ainda consegue emitir sinais ──
	# Sinal 'tween_started': verifica conectividade
	assert_bool(_behavior_b.has_signal("tween_started")).override_failure_message("Sinal 'tween_started' nao encontrado em tween_player")

	# Sinal 'tween_finished': verifica conectividade
	assert_bool(_behavior_b.has_signal("tween_finished")).override_failure_message("Sinal 'tween_finished' nao encontrado em tween_player")

