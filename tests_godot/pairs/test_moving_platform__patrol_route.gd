## Teste de composicao: moving_platform + patrol_route
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: moving_platform
## @behavior_b: patrol_route

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/moving_platform/moving_platform.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/moving_platform/moving_platform.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/patrol_route/patrol_route.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/patrol_route/patrol_route.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("moving_platform foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("patrol_route foi liberado durante o teste")
	# ── Verifica que moving_platform ainda consegue emitir sinais ──
	# Sinal 'waypoint_reached': verifica conectividade
	assert_bool(_behavior_a.has_signal("waypoint_reached")).override_failure_message("Sinal 'waypoint_reached' nao encontrado em moving_platform")

	# Sinal 'loop_completed': verifica conectividade
	assert_bool(_behavior_a.has_signal("loop_completed")).override_failure_message("Sinal 'loop_completed' nao encontrado em moving_platform")
	# ── Verifica que patrol_route ainda consegue emitir sinais ──
	# Sinal 'waypoint_reached': verifica conectividade
	assert_bool(_behavior_b.has_signal("waypoint_reached")).override_failure_message("Sinal 'waypoint_reached' nao encontrado em patrol_route")

	# Sinal 'route_complete': verifica conectividade
	assert_bool(_behavior_b.has_signal("route_complete")).override_failure_message("Sinal 'route_complete' nao encontrado em patrol_route")

