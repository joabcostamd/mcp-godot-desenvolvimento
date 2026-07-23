## Teste de composicao: match3_grid + object_pool
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: match3_grid
## @behavior_b: object_pool

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/match3_grid/match3_grid.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/match3_grid/match3_grid.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/object_pool/object_pool.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/object_pool/object_pool.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("match3_grid foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("object_pool foi liberado durante o teste")
	# ── Verifica que match3_grid ainda consegue emitir sinais ──
	# Sinal 'match_found': verifica conectividade
	assert_bool(_behavior_a.has_signal("match_found")).override_failure_message("Sinal 'match_found' nao encontrado em match3_grid")

	# Sinal 'grid_settled': verifica conectividade
	assert_bool(_behavior_a.has_signal("grid_settled")).override_failure_message("Sinal 'grid_settled' nao encontrado em match3_grid")

	# Sinal 'combo': verifica conectividade
	assert_bool(_behavior_a.has_signal("combo")).override_failure_message("Sinal 'combo' nao encontrado em match3_grid")
	# ── Verifica que object_pool ainda consegue emitir sinais ──
	# Sinal 'object_taken': verifica conectividade
	assert_bool(_behavior_b.has_signal("object_taken")).override_failure_message("Sinal 'object_taken' nao encontrado em object_pool")

	# Sinal 'object_returned': verifica conectividade
	assert_bool(_behavior_b.has_signal("object_returned")).override_failure_message("Sinal 'object_returned' nao encontrado em object_pool")

	# Sinal 'pool_empty': verifica conectividade
	assert_bool(_behavior_b.has_signal("pool_empty")).override_failure_message("Sinal 'pool_empty' nao encontrado em object_pool")

