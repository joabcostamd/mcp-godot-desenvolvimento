## Teste de composicao: farming_plot + save_load
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: farming_plot
## @behavior_b: save_load

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/farming_plot/farming_plot.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/farming_plot/farming_plot.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/save_load/save_load.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/save_load/save_load.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("farming_plot foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("save_load foi liberado durante o teste")
	# ── Verifica que farming_plot ainda consegue emitir sinais ──
	# Sinal 'planted': verifica conectividade
	assert_bool(_behavior_a.has_signal("planted")).override_failure_message("Sinal 'planted' nao encontrado em farming_plot")

	# Sinal 'stage_changed': verifica conectividade
	assert_bool(_behavior_a.has_signal("stage_changed")).override_failure_message("Sinal 'stage_changed' nao encontrado em farming_plot")

	# Sinal 'ready': verifica conectividade
	assert_bool(_behavior_a.has_signal("ready")).override_failure_message("Sinal 'ready' nao encontrado em farming_plot")

	# Sinal 'harvested': verifica conectividade
	assert_bool(_behavior_a.has_signal("harvested")).override_failure_message("Sinal 'harvested' nao encontrado em farming_plot")
	# ── Verifica que save_load ainda consegue emitir sinais ──
	# Sinal 'saved': verifica conectividade
	assert_bool(_behavior_b.has_signal("saved")).override_failure_message("Sinal 'saved' nao encontrado em save_load")

	# Sinal 'loaded': verifica conectividade
	assert_bool(_behavior_b.has_signal("loaded")).override_failure_message("Sinal 'loaded' nao encontrado em save_load")

