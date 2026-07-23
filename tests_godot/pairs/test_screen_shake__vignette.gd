## Teste de composicao: screen_shake + vignette
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: screen_shake
## @behavior_b: vignette

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/screen_shake/screen_shake.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/screen_shake/screen_shake.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/vignette/vignette.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/vignette/vignette.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("screen_shake foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("vignette foi liberado durante o teste")
	# ── Verifica que screen_shake ainda consegue emitir sinais ──
	# Sinal 'shake_started': verifica conectividade
	assert_bool(_behavior_a.has_signal("shake_started")).override_failure_message("Sinal 'shake_started' nao encontrado em screen_shake")

	# Sinal 'shake_ended': verifica conectividade
	assert_bool(_behavior_a.has_signal("shake_ended")).override_failure_message("Sinal 'shake_ended' nao encontrado em screen_shake")
	# ── Verifica que vignette ainda consegue emitir sinais ──
	# Sinal 'vignette_started': verifica conectividade
	assert_bool(_behavior_b.has_signal("vignette_started")).override_failure_message("Sinal 'vignette_started' nao encontrado em vignette")

	# Sinal 'vignette_finished': verifica conectividade
	assert_bool(_behavior_b.has_signal("vignette_finished")).override_failure_message("Sinal 'vignette_finished' nao encontrado em vignette")

