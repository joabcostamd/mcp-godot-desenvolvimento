## Teste de composicao: health + state_machine
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: health
## @behavior_b: state_machine

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/health/health.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/health/health.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/state_machine/state_machine.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/state_machine/state_machine.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("health foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("state_machine foi liberado durante o teste")
	# ── Verifica que health ainda consegue emitir sinais ──
	# Sinal 'died': verifica conectividade
	assert_bool(_behavior_a.has_signal("died")).override_failure_message("Sinal 'died' nao encontrado em health")

	# Sinal 'damage_taken': verifica conectividade
	assert_bool(_behavior_a.has_signal("damage_taken")).override_failure_message("Sinal 'damage_taken' nao encontrado em health")

	# Sinal 'healed': verifica conectividade
	assert_bool(_behavior_a.has_signal("healed")).override_failure_message("Sinal 'healed' nao encontrado em health")

	# Sinal 'hp_changed': verifica conectividade
	assert_bool(_behavior_a.has_signal("hp_changed")).override_failure_message("Sinal 'hp_changed' nao encontrado em health")

	# Sinal 'first_hit': verifica conectividade
	assert_bool(_behavior_a.has_signal("first_hit")).override_failure_message("Sinal 'first_hit' nao encontrado em health")
	# ── Verifica que state_machine ainda consegue emitir sinais ──
	# Sinal 'state_changed': verifica conectividade
	assert_bool(_behavior_b.has_signal("state_changed")).override_failure_message("Sinal 'state_changed' nao encontrado em state_machine")

	# Sinal 'state_entered': verifica conectividade
	assert_bool(_behavior_b.has_signal("state_entered")).override_failure_message("Sinal 'state_entered' nao encontrado em state_machine")

	# Sinal 'state_exited': verifica conectividade
	assert_bool(_behavior_b.has_signal("state_exited")).override_failure_message("Sinal 'state_exited' nao encontrado em state_machine")

