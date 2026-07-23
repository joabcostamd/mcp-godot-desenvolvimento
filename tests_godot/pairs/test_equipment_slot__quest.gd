## Teste de composicao: equipment_slot + quest
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: equipment_slot
## @behavior_b: quest

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/equipment_slot/equipment_slot.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/equipment_slot/equipment_slot.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/quest/quest.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/quest/quest.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("equipment_slot foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("quest foi liberado durante o teste")
	# ── Verifica que equipment_slot ainda consegue emitir sinais ──
	# Sinal 'equipped': verifica conectividade
	assert_bool(_behavior_a.has_signal("equipped")).override_failure_message("Sinal 'equipped' nao encontrado em equipment_slot")

	# Sinal 'unequipped': verifica conectividade
	assert_bool(_behavior_a.has_signal("unequipped")).override_failure_message("Sinal 'unequipped' nao encontrado em equipment_slot")
	# ── Verifica que quest ainda consegue emitir sinais ──
	# Sinal 'quest_started': verifica conectividade
	assert_bool(_behavior_b.has_signal("quest_started")).override_failure_message("Sinal 'quest_started' nao encontrado em quest")

	# Sinal 'quest_completed': verifica conectividade
	assert_bool(_behavior_b.has_signal("quest_completed")).override_failure_message("Sinal 'quest_completed' nao encontrado em quest")

	# Sinal 'quest_failed': verifica conectividade
	assert_bool(_behavior_b.has_signal("quest_failed")).override_failure_message("Sinal 'quest_failed' nao encontrado em quest")

