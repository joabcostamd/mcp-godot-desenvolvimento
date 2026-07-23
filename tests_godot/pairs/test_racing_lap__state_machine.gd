## Teste de composicao: racing_lap + state_machine
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: racing_lap
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
	var res_a := load("res://behaviors/racing_lap/racing_lap.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/racing_lap/racing_lap.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/state_machine/state_machine.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/state_machine/state_machine.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("racing_lap foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("state_machine foi liberado durante o teste")
	# ── Verifica que racing_lap ainda consegue emitir sinais ──
	# Sinal 'lap_completed': verifica conectividade
	assert_bool(_behavior_a.has_signal("lap_completed")).override_failure_message("Sinal 'lap_completed' nao encontrado em racing_lap")

	# Sinal 'race_finished': verifica conectividade
	assert_bool(_behavior_a.has_signal("race_finished")).override_failure_message("Sinal 'race_finished' nao encontrado em racing_lap")

	# Sinal 'checkpoint_passed': verifica conectividade
	assert_bool(_behavior_a.has_signal("checkpoint_passed")).override_failure_message("Sinal 'checkpoint_passed' nao encontrado em racing_lap")
	# ── Verifica que state_machine ainda consegue emitir sinais ──
	# Sinal 'state_changed': verifica conectividade
	assert_bool(_behavior_b.has_signal("state_changed")).override_failure_message("Sinal 'state_changed' nao encontrado em state_machine")

	# Sinal 'state_entered': verifica conectividade
	assert_bool(_behavior_b.has_signal("state_entered")).override_failure_message("Sinal 'state_entered' nao encontrado em state_machine")

	# Sinal 'state_exited': verifica conectividade
	assert_bool(_behavior_b.has_signal("state_exited")).override_failure_message("Sinal 'state_exited' nao encontrado em state_machine")

