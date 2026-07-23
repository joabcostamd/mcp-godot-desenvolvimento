## Teste de composicao: sfx_player + trigger_zone
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: sfx_player
## @behavior_b: trigger_zone

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/sfx_player/sfx_player.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/sfx_player/sfx_player.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/trigger_zone/trigger_zone.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/trigger_zone/trigger_zone.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("sfx_player foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("trigger_zone foi liberado durante o teste")
	# ── Verifica que sfx_player ainda consegue emitir sinais ──
	# Sinal 'played': verifica conectividade
	assert_bool(_behavior_a.has_signal("played")).override_failure_message("Sinal 'played' nao encontrado em sfx_player")

	# Sinal 'finished': verifica conectividade
	assert_bool(_behavior_a.has_signal("finished")).override_failure_message("Sinal 'finished' nao encontrado em sfx_player")
	# ── Verifica que trigger_zone ainda consegue emitir sinais ──
	# Sinal 'zone_entered': verifica conectividade
	assert_bool(_behavior_b.has_signal("zone_entered")).override_failure_message("Sinal 'zone_entered' nao encontrado em trigger_zone")

	# Sinal 'zone_exited': verifica conectividade
	assert_bool(_behavior_b.has_signal("zone_exited")).override_failure_message("Sinal 'zone_exited' nao encontrado em trigger_zone")

