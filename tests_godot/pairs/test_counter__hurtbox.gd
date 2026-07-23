## Teste de composicao: counter + hurtbox
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: counter
## @behavior_b: hurtbox

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/counter/counter.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/counter/counter.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/hurtbox/hurtbox.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/hurtbox/hurtbox.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("counter foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("hurtbox foi liberado durante o teste")
	# ── Verifica que counter ainda consegue emitir sinais ──
	# Sinal 'value_changed': verifica conectividade
	assert_bool(_behavior_a.has_signal("value_changed")).override_failure_message("Sinal 'value_changed' nao encontrado em counter")

	# Sinal 'min_reached': verifica conectividade
	assert_bool(_behavior_a.has_signal("min_reached")).override_failure_message("Sinal 'min_reached' nao encontrado em counter")

	# Sinal 'max_reached': verifica conectividade
	assert_bool(_behavior_a.has_signal("max_reached")).override_failure_message("Sinal 'max_reached' nao encontrado em counter")
	# ── Verifica que hurtbox ainda consegue emitir sinais ──
	# Sinal 'hit_received': verifica conectividade
	assert_bool(_behavior_b.has_signal("hit_received")).override_failure_message("Sinal 'hit_received' nao encontrado em hurtbox")

	# Sinal 'hit_blocked': verifica conectividade
	assert_bool(_behavior_b.has_signal("hit_blocked")).override_failure_message("Sinal 'hit_blocked' nao encontrado em hurtbox")

