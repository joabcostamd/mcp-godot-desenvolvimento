## Teste de composicao: crafting + shop
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: crafting
## @behavior_b: shop

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

	var res_b := load("res://behaviors/shop/shop.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/shop/shop.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("crafting foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("shop foi liberado durante o teste")
	# ── Verifica que crafting ainda consegue emitir sinais ──
	# Sinal 'crafted': verifica conectividade
	assert_bool(_behavior_a.has_signal("crafted")).override_failure_message("Sinal 'crafted' nao encontrado em crafting")

	# Sinal 'missing_ingredients': verifica conectividade
	assert_bool(_behavior_a.has_signal("missing_ingredients")).override_failure_message("Sinal 'missing_ingredients' nao encontrado em crafting")

	# Sinal 'recipe_unlocked': verifica conectividade
	assert_bool(_behavior_a.has_signal("recipe_unlocked")).override_failure_message("Sinal 'recipe_unlocked' nao encontrado em crafting")
	# ── Verifica que shop ainda consegue emitir sinais ──
	# Sinal 'item_bought': verifica conectividade
	assert_bool(_behavior_b.has_signal("item_bought")).override_failure_message("Sinal 'item_bought' nao encontrado em shop")

	# Sinal 'item_sold': verifica conectividade
	assert_bool(_behavior_b.has_signal("item_sold")).override_failure_message("Sinal 'item_sold' nao encontrado em shop")

	# Sinal 'insufficient_funds': verifica conectividade
	assert_bool(_behavior_b.has_signal("insufficient_funds")).override_failure_message("Sinal 'insufficient_funds' nao encontrado em shop")

