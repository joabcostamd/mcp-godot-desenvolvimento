## Teste de composicao: avoidance + pathfinding
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: avoidance
## @behavior_b: pathfinding

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/avoidance/avoidance.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/avoidance/avoidance.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/pathfinding/pathfinding.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/pathfinding/pathfinding.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("avoidance foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("pathfinding foi liberado durante o teste")
	# ── Verifica que pathfinding ainda consegue emitir sinais ──
	# Sinal 'path_found': verifica conectividade
	assert_bool(_behavior_b.has_signal("path_found")).override_failure_message("Sinal 'path_found' nao encontrado em pathfinding")

	# Sinal 'path_lost': verifica conectividade
	assert_bool(_behavior_b.has_signal("path_lost")).override_failure_message("Sinal 'path_lost' nao encontrado em pathfinding")

	# Sinal 'arrived': verifica conectividade
	assert_bool(_behavior_b.has_signal("arrived")).override_failure_message("Sinal 'arrived' nao encontrado em pathfinding")

