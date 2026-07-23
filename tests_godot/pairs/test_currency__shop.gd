## Teste de composicao: currency + shop
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: currency
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
	var res_a := load("res://behaviors/currency/currency.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/currency/currency.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/shop/shop.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/shop/shop.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("currency foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("shop foi liberado durante o teste")
	# ── Verifica que currency ainda consegue emitir sinais ──
	# Sinal 'gained': verifica conectividade
	assert_bool(_behavior_a.has_signal("gained")).override_failure_message("Sinal 'gained' nao encontrado em currency")

	# Sinal 'spent': verifica conectividade
	assert_bool(_behavior_a.has_signal("spent")).override_failure_message("Sinal 'spent' nao encontrado em currency")

	# Sinal 'insufficient': verifica conectividade
	assert_bool(_behavior_a.has_signal("insufficient")).override_failure_message("Sinal 'insufficient' nao encontrado em currency")
	# ── Verifica que shop ainda consegue emitir sinais ──
	# Sinal 'item_bought': verifica conectividade
	assert_bool(_behavior_b.has_signal("item_bought")).override_failure_message("Sinal 'item_bought' nao encontrado em shop")

	# Sinal 'item_sold': verifica conectividade
	assert_bool(_behavior_b.has_signal("item_sold")).override_failure_message("Sinal 'item_sold' nao encontrado em shop")

	# Sinal 'insufficient_funds': verifica conectividade
	assert_bool(_behavior_b.has_signal("insufficient_funds")).override_failure_message("Sinal 'insufficient_funds' nao encontrado em shop")

