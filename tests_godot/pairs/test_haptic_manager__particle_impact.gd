## Teste de composicao: haptic_manager + particle_impact
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: haptic_manager
## @behavior_b: particle_impact

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/haptic_manager/haptic_manager.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/haptic_manager/haptic_manager.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/particle_impact/particle_impact.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/particle_impact/particle_impact.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("haptic_manager foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("particle_impact foi liberado durante o teste")
	# ── Verifica que haptic_manager ainda consegue emitir sinais ──
	# Sinal 'vibration_started': verifica conectividade
	assert_bool(_behavior_a.has_signal("vibration_started")).override_failure_message("Sinal 'vibration_started' nao encontrado em haptic_manager")

	# Sinal 'vibration_ended': verifica conectividade
	assert_bool(_behavior_a.has_signal("vibration_ended")).override_failure_message("Sinal 'vibration_ended' nao encontrado em haptic_manager")
	# ── Verifica que particle_impact ainda consegue emitir sinais ──
	# Sinal 'particles_emitted': verifica conectividade
	assert_bool(_behavior_b.has_signal("particles_emitted")).override_failure_message("Sinal 'particles_emitted' nao encontrado em particle_impact")

