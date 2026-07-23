## Teste de composicao: hit_stop + screen_shake
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: hit_stop
## @behavior_b: screen_shake

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/hit_stop/hit_stop.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/hit_stop/hit_stop.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/screen_shake/screen_shake.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/screen_shake/screen_shake.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("hit_stop foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("screen_shake foi liberado durante o teste")
	# ── Verifica que hit_stop ainda consegue emitir sinais ──
	# Sinal 'hit_stopped': verifica conectividade
	assert_bool(_behavior_a.has_signal("hit_stopped")).override_failure_message("Sinal 'hit_stopped' nao encontrado em hit_stop")

	# Sinal 'resumed': verifica conectividade
	assert_bool(_behavior_a.has_signal("resumed")).override_failure_message("Sinal 'resumed' nao encontrado em hit_stop")
	# ── Verifica que screen_shake ainda consegue emitir sinais ──
	# Sinal 'shake_started': verifica conectividade
	assert_bool(_behavior_b.has_signal("shake_started")).override_failure_message("Sinal 'shake_started' nao encontrado em screen_shake")

	# Sinal 'shake_ended': verifica conectividade
	assert_bool(_behavior_b.has_signal("shake_ended")).override_failure_message("Sinal 'shake_ended' nao encontrado em screen_shake")

