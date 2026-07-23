## Teste de composicao: camera_path + moving_platform
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: camera_path
## @behavior_b: moving_platform

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/camera_path/camera_path.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/camera_path/camera_path.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/moving_platform/moving_platform.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/moving_platform/moving_platform.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("camera_path foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("moving_platform foi liberado durante o teste")
	# ── Verifica que camera_path ainda consegue emitir sinais ──
	# Sinal 'waypoint_reached': verifica conectividade
	assert_bool(_behavior_a.has_signal("waypoint_reached")).override_failure_message("Sinal 'waypoint_reached' nao encontrado em camera_path")

	# Sinal 'path_completed': verifica conectividade
	assert_bool(_behavior_a.has_signal("path_completed")).override_failure_message("Sinal 'path_completed' nao encontrado em camera_path")
	# ── Verifica que moving_platform ainda consegue emitir sinais ──
	# Sinal 'waypoint_reached': verifica conectividade
	assert_bool(_behavior_b.has_signal("waypoint_reached")).override_failure_message("Sinal 'waypoint_reached' nao encontrado em moving_platform")

	# Sinal 'loop_completed': verifica conectividade
	assert_bool(_behavior_b.has_signal("loop_completed")).override_failure_message("Sinal 'loop_completed' nao encontrado em moving_platform")

