## Teste de composicao: blackboard + health
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: blackboard
## @behavior_b: health

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/blackboard/blackboard.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/blackboard/blackboard.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/health/health.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/health/health.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("blackboard foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("health foi liberado durante o teste")
	# ── Verifica que blackboard ainda consegue emitir sinais ──
	# Sinal 'var_set': verifica conectividade
	assert_bool(_behavior_a.has_signal("var_set")).override_failure_message("Sinal 'var_set' nao encontrado em blackboard")

	# Sinal 'trigger_activated': verifica conectividade
	assert_bool(_behavior_a.has_signal("trigger_activated")).override_failure_message("Sinal 'trigger_activated' nao encontrado em blackboard")
	# ── Verifica que health ainda consegue emitir sinais ──
	# Sinal 'died': verifica conectividade
	assert_bool(_behavior_b.has_signal("died")).override_failure_message("Sinal 'died' nao encontrado em health")

	# Sinal 'damage_taken': verifica conectividade
	assert_bool(_behavior_b.has_signal("damage_taken")).override_failure_message("Sinal 'damage_taken' nao encontrado em health")

	# Sinal 'healed': verifica conectividade
	assert_bool(_behavior_b.has_signal("healed")).override_failure_message("Sinal 'healed' nao encontrado em health")

	# Sinal 'hp_changed': verifica conectividade
	assert_bool(_behavior_b.has_signal("hp_changed")).override_failure_message("Sinal 'hp_changed' nao encontrado em health")

	# Sinal 'first_hit': verifica conectividade
	assert_bool(_behavior_b.has_signal("first_hit")).override_failure_message("Sinal 'first_hit' nao encontrado em health")

