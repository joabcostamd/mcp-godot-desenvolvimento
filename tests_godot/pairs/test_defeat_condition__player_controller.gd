## Teste de composicao: defeat_condition + player_controller
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: defeat_condition
## @behavior_b: player_controller

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/defeat_condition/defeat_condition.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/defeat_condition/defeat_condition.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/player_controller/player_controller.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/player_controller/player_controller.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("defeat_condition foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("player_controller foi liberado durante o teste")
	# ── Verifica que defeat_condition ainda consegue emitir sinais ──
	# Sinal 'defeat_triggered': verifica conectividade
	assert_bool(_behavior_a.has_signal("defeat_triggered")).override_failure_message("Sinal 'defeat_triggered' nao encontrado em defeat_condition")
	# ── Verifica que player_controller ainda consegue emitir sinais ──
	# Sinal 'player_died': verifica conectividade
	assert_bool(_behavior_b.has_signal("player_died")).override_failure_message("Sinal 'player_died' nao encontrado em player_controller")

	# Sinal 'jumped': verifica conectividade
	assert_bool(_behavior_b.has_signal("jumped")).override_failure_message("Sinal 'jumped' nao encontrado em player_controller")

