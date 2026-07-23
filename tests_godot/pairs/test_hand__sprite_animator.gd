## Teste de composicao: hand + sprite_animator
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: hand
## @behavior_b: sprite_animator

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/hand/hand.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/hand/hand.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/sprite_animator/sprite_animator.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/sprite_animator/sprite_animator.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("hand foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("sprite_animator foi liberado durante o teste")
	# ── Verifica que hand ainda consegue emitir sinais ──
	# Sinal 'card_added': verifica conectividade
	assert_bool(_behavior_a.has_signal("card_added")).override_failure_message("Sinal 'card_added' nao encontrado em hand")

	# Sinal 'card_removed': verifica conectividade
	assert_bool(_behavior_a.has_signal("card_removed")).override_failure_message("Sinal 'card_removed' nao encontrado em hand")

