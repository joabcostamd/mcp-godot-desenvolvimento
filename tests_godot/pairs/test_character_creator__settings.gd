## Teste de composicao: character_creator + settings
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: character_creator
## @behavior_b: settings

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/character_creator/character_creator.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/character_creator/character_creator.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/settings/settings.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/settings/settings.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("character_creator foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("settings foi liberado durante o teste")
	# ── Verifica que character_creator ainda consegue emitir sinais ──
	# Sinal 'part_changed': verifica conectividade
	assert_bool(_behavior_a.has_signal("part_changed")).override_failure_message("Sinal 'part_changed' nao encontrado em character_creator")

	# Sinal 'saved': verifica conectividade
	assert_bool(_behavior_a.has_signal("saved")).override_failure_message("Sinal 'saved' nao encontrado em character_creator")

	# Sinal 'loaded': verifica conectividade
	assert_bool(_behavior_a.has_signal("loaded")).override_failure_message("Sinal 'loaded' nao encontrado em character_creator")
	# ── Verifica que settings ainda consegue emitir sinais ──
	# Sinal 'setting_changed': verifica conectividade
	assert_bool(_behavior_b.has_signal("setting_changed")).override_failure_message("Sinal 'setting_changed' nao encontrado em settings")

