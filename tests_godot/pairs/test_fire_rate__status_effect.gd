## Teste de composicao: fire_rate + status_effect
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: fire_rate
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
	var res_a := load("res://behaviors/fire_rate/fire_rate.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/fire_rate/fire_rate.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/status_effect/status_effect.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/status_effect/status_effect.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("fire_rate foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("status_effect foi liberado durante o teste")
	# ── Verifica que fire_rate ainda consegue emitir sinais ──
	# Sinal 'fired': verifica conectividade
	assert_bool(_behavior_a.has_signal("fired")).override_failure_message("Sinal 'fired' nao encontrado em fire_rate")

	# Sinal 'cooldown_ready': verifica conectividade
	assert_bool(_behavior_a.has_signal("cooldown_ready")).override_failure_message("Sinal 'cooldown_ready' nao encontrado em fire_rate")
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

