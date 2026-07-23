## Teste de composicao: interactable + inventory
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: interactable
## @behavior_b: inventory

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/interactable/interactable.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/interactable/interactable.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/inventory/inventory.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/inventory/inventory.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("interactable foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("inventory foi liberado durante o teste")
	# ── Verifica que interactable ainda consegue emitir sinais ──
	# Sinal 'focused': verifica conectividade
	assert_bool(_behavior_a.has_signal("focused")).override_failure_message("Sinal 'focused' nao encontrado em interactable")

	# Sinal 'unfocused': verifica conectividade
	assert_bool(_behavior_a.has_signal("unfocused")).override_failure_message("Sinal 'unfocused' nao encontrado em interactable")

	# Sinal 'interacted': verifica conectividade
	assert_bool(_behavior_a.has_signal("interacted")).override_failure_message("Sinal 'interacted' nao encontrado em interactable")
	# ── Verifica que inventory ainda consegue emitir sinais ──
	# Sinal 'item_added': verifica conectividade
	assert_bool(_behavior_b.has_signal("item_added")).override_failure_message("Sinal 'item_added' nao encontrado em inventory")

	# Sinal 'item_removed': verifica conectividade
	assert_bool(_behavior_b.has_signal("item_removed")).override_failure_message("Sinal 'item_removed' nao encontrado em inventory")

	# Sinal 'inventory_full': verifica conectividade
	assert_bool(_behavior_b.has_signal("inventory_full")).override_failure_message("Sinal 'inventory_full' nao encontrado em inventory")

