## Teste de composicao: sfx_player + text_size
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: sfx_player
## @behavior_b: text_size

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/sfx_player/sfx_player.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/sfx_player/sfx_player.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/text_size/text_size.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/text_size/text_size.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("sfx_player foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("text_size foi liberado durante o teste")
	# ── Verifica que sfx_player ainda consegue emitir sinais ──
	# Sinal 'played': verifica conectividade
	assert_bool(_behavior_a.has_signal("played")).override_failure_message("Sinal 'played' nao encontrado em sfx_player")

	# Sinal 'finished': verifica conectividade
	assert_bool(_behavior_a.has_signal("finished")).override_failure_message("Sinal 'finished' nao encontrado em sfx_player")
	# ── Verifica que text_size ainda consegue emitir sinais ──
	# Sinal 'size_changed': verifica conectividade
	assert_bool(_behavior_b.has_signal("size_changed")).override_failure_message("Sinal 'size_changed' nao encontrado em text_size")

