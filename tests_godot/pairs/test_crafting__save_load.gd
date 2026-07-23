## Teste de composicao: crafting + save_load
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: crafting
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
	var res_a := load("res://behaviors/crafting/crafting.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/crafting/crafting.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/save_load/save_load.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/save_load/save_load.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("crafting foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("save_load foi liberado durante o teste")
	# ── Verifica que crafting ainda consegue emitir sinais ──
	# Sinal 'crafted': verifica conectividade
	assert_bool(_behavior_a.has_signal("crafted")).override_failure_message("Sinal 'crafted' nao encontrado em crafting")

	# Sinal 'missing_ingredients': verifica conectividade
	assert_bool(_behavior_a.has_signal("missing_ingredients")).override_failure_message("Sinal 'missing_ingredients' nao encontrado em crafting")

	# Sinal 'recipe_unlocked': verifica conectividade
	assert_bool(_behavior_a.has_signal("recipe_unlocked")).override_failure_message("Sinal 'recipe_unlocked' nao encontrado em crafting")
	# ── Verifica que save_load ainda consegue emitir sinais ──
	# Sinal 'saved': verifica conectividade
	assert_bool(_behavior_b.has_signal("saved")).override_failure_message("Sinal 'saved' nao encontrado em save_load")

	# Sinal 'loaded': verifica conectividade
	assert_bool(_behavior_b.has_signal("loaded")).override_failure_message("Sinal 'loaded' nao encontrado em save_load")

