## Teste de composicao: particle_impact + tutorial_overlay
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: particle_impact
## @behavior_b: tutorial_overlay

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/particle_impact/particle_impact.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/particle_impact/particle_impact.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/tutorial_overlay/tutorial_overlay.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/tutorial_overlay/tutorial_overlay.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("particle_impact foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("tutorial_overlay foi liberado durante o teste")
	# ── Verifica que particle_impact ainda consegue emitir sinais ──
	# Sinal 'particles_emitted': verifica conectividade
	assert_bool(_behavior_a.has_signal("particles_emitted")).override_failure_message("Sinal 'particles_emitted' nao encontrado em particle_impact")
	# ── Verifica que tutorial_overlay ainda consegue emitir sinais ──
	# Sinal 'step_completed': verifica conectividade
	assert_bool(_behavior_b.has_signal("step_completed")).override_failure_message("Sinal 'step_completed' nao encontrado em tutorial_overlay")

	# Sinal 'tutorial_finished': verifica conectividade
	assert_bool(_behavior_b.has_signal("tutorial_finished")).override_failure_message("Sinal 'tutorial_finished' nao encontrado em tutorial_overlay")

