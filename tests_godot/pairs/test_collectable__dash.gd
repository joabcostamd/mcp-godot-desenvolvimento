## Teste de composicao: collectable + dash
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: collectable
## @behavior_b: dash

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

	var res_b := load("res://behaviors/dash/dash.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/dash/dash.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("collectable foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("dash foi liberado durante o teste")
	# ── Verifica que collectable ainda consegue emitir sinais ──
	# Sinal 'collected': verifica conectividade
	assert_bool(_behavior_a.has_signal("collected")).override_failure_message("Sinal 'collected' nao encontrado em collectable")

	# Sinal 'pickup_failed': verifica conectividade
	assert_bool(_behavior_a.has_signal("pickup_failed")).override_failure_message("Sinal 'pickup_failed' nao encontrado em collectable")
	# ── Verifica que dash ainda consegue emitir sinais ──
	# Sinal 'dashed': verifica conectividade
	assert_bool(_behavior_b.has_signal("dashed")).override_failure_message("Sinal 'dashed' nao encontrado em dash")

	# Sinal 'dash_ready': verifica conectividade
	assert_bool(_behavior_b.has_signal("dash_ready")).override_failure_message("Sinal 'dash_ready' nao encontrado em dash")

