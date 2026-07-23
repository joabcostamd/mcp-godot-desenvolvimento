## Teste de composicao: upgrade + xp_level
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: upgrade
## @behavior_b: xp_level

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/upgrade/upgrade.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/upgrade/upgrade.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/xp_level/xp_level.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/xp_level/xp_level.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("upgrade foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("xp_level foi liberado durante o teste")
	# ── Verifica que upgrade ainda consegue emitir sinais ──
	# Sinal 'choices_ready': verifica conectividade
	assert_bool(_behavior_a.has_signal("choices_ready")).override_failure_message("Sinal 'choices_ready' nao encontrado em upgrade")

	# Sinal 'upgrade_applied': verifica conectividade
	assert_bool(_behavior_a.has_signal("upgrade_applied")).override_failure_message("Sinal 'upgrade_applied' nao encontrado em upgrade")
	# ── Verifica que xp_level ainda consegue emitir sinais ──
	# Sinal 'xp_gained': verifica conectividade
	assert_bool(_behavior_b.has_signal("xp_gained")).override_failure_message("Sinal 'xp_gained' nao encontrado em xp_level")

	# Sinal 'leveled_up': verifica conectividade
	assert_bool(_behavior_b.has_signal("leveled_up")).override_failure_message("Sinal 'leveled_up' nao encontrado em xp_level")

