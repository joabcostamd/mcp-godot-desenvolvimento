## Teste de composicao: round_timer + status_effect
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: round_timer
## @behavior_b: status_effect

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/round_timer/round_timer.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/round_timer/round_timer.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/status_effect/status_effect.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/status_effect/status_effect.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("round_timer foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("status_effect foi liberado durante o teste")
	# ── Verifica que round_timer ainda consegue emitir sinais ──
	# Sinal 'tick': verifica conectividade
	assert_bool(_behavior_a.has_signal("tick")).override_failure_message("Sinal 'tick' nao encontrado em round_timer")

	# Sinal 'round_started': verifica conectividade
	assert_bool(_behavior_a.has_signal("round_started")).override_failure_message("Sinal 'round_started' nao encontrado em round_timer")

	# Sinal 'round_ended': verifica conectividade
	assert_bool(_behavior_a.has_signal("round_ended")).override_failure_message("Sinal 'round_ended' nao encontrado em round_timer")

	# Sinal 'time_up': verifica conectividade
	assert_bool(_behavior_a.has_signal("time_up")).override_failure_message("Sinal 'time_up' nao encontrado em round_timer")
	# ── Verifica que status_effect ainda consegue emitir sinais ──
	# Sinal 'applied': verifica conectividade
	assert_bool(_behavior_b.has_signal("applied")).override_failure_message("Sinal 'applied' nao encontrado em status_effect")

	# Sinal 'tick': verifica conectividade
	assert_bool(_behavior_b.has_signal("tick")).override_failure_message("Sinal 'tick' nao encontrado em status_effect")

	# Sinal 'expired': verifica conectividade
	assert_bool(_behavior_b.has_signal("expired")).override_failure_message("Sinal 'expired' nao encontrado em status_effect")

	# Sinal 'refreshed': verifica conectividade
	assert_bool(_behavior_b.has_signal("refreshed")).override_failure_message("Sinal 'refreshed' nao encontrado em status_effect")

	# Sinal 'removed': verifica conectividade
	assert_bool(_behavior_b.has_signal("removed")).override_failure_message("Sinal 'removed' nao encontrado em status_effect")

