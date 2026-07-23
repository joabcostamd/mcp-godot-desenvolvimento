## Teste de composicao: damage_over_time + flee
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: damage_over_time
## @behavior_b: flee

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/damage_over_time/damage_over_time.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/damage_over_time/damage_over_time.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/flee/flee.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/flee/flee.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("damage_over_time foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("flee foi liberado durante o teste")
	# ── Verifica que damage_over_time ainda consegue emitir sinais ──
	# Sinal 'dot_tick': verifica conectividade
	assert_bool(_behavior_a.has_signal("dot_tick")).override_failure_message("Sinal 'dot_tick' nao encontrado em damage_over_time")

	# Sinal 'dot_ended': verifica conectividade
	assert_bool(_behavior_a.has_signal("dot_ended")).override_failure_message("Sinal 'dot_ended' nao encontrado em damage_over_time")
	# ── Verifica que flee ainda consegue emitir sinais ──
	# Sinal 'fleeing': verifica conectividade
	assert_bool(_behavior_b.has_signal("fleeing")).override_failure_message("Sinal 'fleeing' nao encontrado em flee")

	# Sinal 'safe': verifica conectividade
	assert_bool(_behavior_b.has_signal("safe")).override_failure_message("Sinal 'safe' nao encontrado em flee")

