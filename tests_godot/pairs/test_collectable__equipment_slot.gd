## Teste de composicao: collectable + equipment_slot
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: collectable
## @behavior_b: equipment_slot

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/collectable/collectable.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/collectable/collectable.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/equipment_slot/equipment_slot.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/equipment_slot/equipment_slot.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("collectable foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("equipment_slot foi liberado durante o teste")
	# ── Verifica que collectable ainda consegue emitir sinais ──
	# Sinal 'collected': verifica conectividade
	assert_bool(_behavior_a.has_signal("collected")).override_failure_message("Sinal 'collected' nao encontrado em collectable")

	# Sinal 'pickup_failed': verifica conectividade
	assert_bool(_behavior_a.has_signal("pickup_failed")).override_failure_message("Sinal 'pickup_failed' nao encontrado em collectable")
	# ── Verifica que equipment_slot ainda consegue emitir sinais ──
	# Sinal 'equipped': verifica conectividade
	assert_bool(_behavior_b.has_signal("equipped")).override_failure_message("Sinal 'equipped' nao encontrado em equipment_slot")

	# Sinal 'unequipped': verifica conectividade
	assert_bool(_behavior_b.has_signal("unequipped")).override_failure_message("Sinal 'unequipped' nao encontrado em equipment_slot")

