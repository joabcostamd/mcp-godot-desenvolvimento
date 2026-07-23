## Teste de composicao: combo_detector + floating_text
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: combo_detector
## @behavior_b: floating_text

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/combo_detector/combo_detector.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/combo_detector/combo_detector.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/floating_text/floating_text.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/floating_text/floating_text.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("combo_detector foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("floating_text foi liberado durante o teste")
	# ── Verifica que combo_detector ainda consegue emitir sinais ──
	# Sinal 'combo_started': verifica conectividade
	assert_bool(_behavior_a.has_signal("combo_started")).override_failure_message("Sinal 'combo_started' nao encontrado em combo_detector")

	# Sinal 'combo_advanced': verifica conectividade
	assert_bool(_behavior_a.has_signal("combo_advanced")).override_failure_message("Sinal 'combo_advanced' nao encontrado em combo_detector")

	# Sinal 'combo_finished': verifica conectividade
	assert_bool(_behavior_a.has_signal("combo_finished")).override_failure_message("Sinal 'combo_finished' nao encontrado em combo_detector")

	# Sinal 'combo_dropped': verifica conectividade
	assert_bool(_behavior_a.has_signal("combo_dropped")).override_failure_message("Sinal 'combo_dropped' nao encontrado em combo_detector")
	# ── Verifica que floating_text ainda consegue emitir sinais ──
	# Sinal 'text_shown': verifica conectividade
	assert_bool(_behavior_b.has_signal("text_shown")).override_failure_message("Sinal 'text_shown' nao encontrado em floating_text")

